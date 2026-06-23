import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { toAssignmentTypeId } from "@/shared/types/taskLabels"
import { buildPatternsByLanguageForSave } from "@/features/task-editor/domain/expectedConceptPatterns"
import { ensureDraftBlockEditor } from "@/features/task-editor/domain/blockEditor"
import { deriveTemplateWithSlotMarkers } from "@/domain/blockAssembly/authoring"
import { templateScaffoldIsWhitespaceOnly } from "@/domain/blockAssembly/blockScaffold"
import {
  normalizeRanges,
  rangesToLegacyBlocks,
} from "@/domain/codeBlockRanges"
import { snapshotDraftBlockEditor } from "@/features/task-editor/domain/languageBlockEditorState"

function buildLanguageVariantsFromDraft(draft: TaskDraft): Record<string, unknown> {
  const variants: Record<string, unknown> = {
    ...(draft.languageVariants ?? {}),
  }
  const snapshots = snapshotDraftBlockEditor(draft)
  for (const [language, snapshot] of Object.entries(snapshots)) {
    const code = snapshot.code
    const ranges = normalizeRanges(snapshot.blockRanges ?? [], code)
    const { blocks, order } = rangesToLegacyBlocks(code, ranges)
    const template = deriveTemplateWithSlotMarkers(code, ranges)
    const blocksOnlyScaffold = templateScaffoldIsWhitespaceOnly(template)
    const previous =
      variants[language] && typeof variants[language] === "object"
        ? (variants[language] as Record<string, unknown>)
        : {}
    variants[language] = {
      ...previous,
      original_code: code,
      template,
      blocks,
      correct_order: order,
      blocks_only_scaffold: blocksOnlyScaffold,
    }
  }
  return variants
}

export function buildBlockTaskApiFields(draft: TaskDraft) {
  const blockDraft = ensureDraftBlockEditor(draft)
  const referenceCode = blockDraft.code.code
  const ranges = normalizeRanges(blockDraft.blockRanges ?? [], referenceCode)
  const { blocks, order } = rangesToLegacyBlocks(referenceCode, ranges)
  const template = deriveTemplateWithSlotMarkers(referenceCode, ranges)
  const blocksOnlyScaffold = templateScaffoldIsWhitespaceOnly(template)
  const currentLanguage = String(
    blockDraft.code.language || blockDraft.languages[0] || "pascal",
  ).toLowerCase()
  const payload: Record<string, unknown> = {
    original_code: referenceCode,
    template,
    language: currentLanguage,
    blocks,
    correct_order: order,
    blocks_only_scaffold: blocksOnlyScaffold,
  }
  const languageVariants = buildLanguageVariantsFromDraft(blockDraft)
  if (Object.keys(languageVariants).length > 0) {
    payload.language_variants = languageVariants
  }
  const patternsByLanguage = buildPatternsByLanguageForSave(draft)
  payload.patterns_by_language = patternsByLanguage
  const primaryPatterns =
    patternsByLanguage[currentLanguage] ??
    draft.selectedPatterns.filter((pattern) => pattern.approved !== false).map((pattern) => String(pattern.id))
  payload.patterns = primaryPatterns
  payload.task_type = toAssignmentTypeId(String(draft.type || ""))
  return payload
}
