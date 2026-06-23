import type { CodeBlockRange } from "@/domain/codeBlockRanges"
import { normalizeRanges } from "@/domain/codeBlockRanges"
import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { inferBlockRangesFromAuthorPayload } from "@/features/task-editor/domain/inferBlockRangesFromAuthor"

export type LanguageBlockEditorSnapshot = {
  code: string
  blockRanges: CodeBlockRange[]
}

export function currentDraftLanguage(draft: TaskDraft): string {
  return draft.languages[0] ?? draft.code.language
}

export function snapshotDraftBlockEditor(
  draft: TaskDraft,
  language = currentDraftLanguage(draft),
): Record<string, LanguageBlockEditorSnapshot> {
  const code = draft.code.code
  const blockRanges = normalizeRanges(draft.blockRanges ?? [], code)
  return {
    ...(draft.languageBlockEditorState ?? {}),
    [language]: { code, blockRanges },
  }
}

function defaultSnapshotForVariant(
  lang: string,
  variant: NonNullable<TaskDraft["languageVariants"]>[string] | undefined,
): LanguageBlockEditorSnapshot | null {
  if (!variant?.original_code) return null
  const code = String(variant.original_code)
  return {
    code,
    blockRanges: inferBlockRangesFromAuthorPayload({
      original_code: code,
      blocks: variant.blocks ?? [],
      correct_order: variant.correct_order ?? [],
    }),
  }
}

export function buildInitialLanguageBlockEditorState(
  primaryLanguage: string,
  author: Record<string, unknown>,
  languageVariants: TaskDraft["languageVariants"],
): Record<string, LanguageBlockEditorSnapshot> {
  const state: Record<string, LanguageBlockEditorSnapshot> = {}
  const primaryCode = String(author.original_code ?? author.source_code ?? "")
  state[primaryLanguage] = {
    code: primaryCode,
    blockRanges: inferBlockRangesFromAuthorPayload(author),
  }

  for (const [lang, variant] of Object.entries(languageVariants ?? {})) {
    if (lang === primaryLanguage) continue
    const snapshot = defaultSnapshotForVariant(lang, variant)
    if (snapshot) state[lang] = snapshot
  }

  return state
}

export function buildLanguageBlockEditorStateFromCodes(
  languageCodes: Record<string, string> | undefined,
  primaryLanguage: string,
): Record<string, LanguageBlockEditorSnapshot> {
  const state: Record<string, LanguageBlockEditorSnapshot> = {}
  for (const [lang, rawCode] of Object.entries(languageCodes ?? {})) {
    const code = String(rawCode ?? "")
    if (!code.trim()) continue
    state[lang] = { code, blockRanges: [] }
  }
  const primary = state[primaryLanguage]
  if (!primary && languageCodes?.[primaryLanguage]) {
    state[primaryLanguage] = {
      code: String(languageCodes[primaryLanguage]),
      blockRanges: [],
    }
  }
  return state
}

/** Merge active editor buffer into draft immediately before persisting to API. */
export function flushDraftBlockEditorForSave(draft: TaskDraft): TaskDraft {
  const language = currentDraftLanguage(draft)
  const languageBlockEditorState = snapshotDraftBlockEditor(draft, language)
  const active = languageBlockEditorState[language]
  if (!active) {
    return draft
  }
  return {
    ...draft,
    languageBlockEditorState,
    code: { code: active.code, language },
    blockRanges: active.blockRanges,
    languages: [language],
  }
}

export function resolveLanguageBlockEditorPatch(
  draft: TaskDraft,
  targetLanguage: string,
): Partial<TaskDraft> {
  const languageBlockEditorState = snapshotDraftBlockEditor(draft)
  const saved = languageBlockEditorState[targetLanguage]
  if (saved) {
    return {
      languageBlockEditorState,
      code: { code: saved.code, language: targetLanguage },
      languages: [targetLanguage],
      blockRanges: saved.blockRanges,
    }
  }

  const variant = draft.languageVariants?.[targetLanguage]
  const fromVariant = defaultSnapshotForVariant(targetLanguage, variant)
  if (fromVariant) {
    languageBlockEditorState[targetLanguage] = fromVariant
    return {
      languageBlockEditorState,
      code: { code: fromVariant.code, language: targetLanguage },
      languages: [targetLanguage],
      blockRanges: fromVariant.blockRanges,
    }
  }

  return {
    languageBlockEditorState,
    code: { code: "", language: targetLanguage },
    languages: [targetLanguage],
    blockRanges: [],
  }
}
