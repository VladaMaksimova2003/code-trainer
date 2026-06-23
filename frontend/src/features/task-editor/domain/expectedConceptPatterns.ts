import type { Pattern, TaskDraft } from "@/features/task-editor/domain/entities"

const AUTHORING_LANGS = ["pascal", "python", "cpp", "csharp", "java"]

export function patternLabel(catalog: Pattern[], pattern: Pattern): string {
  return catalog.find((item) => String(item.id) === String(pattern.id))?.label ?? pattern.label
}

export function conceptCardFromCatalog(catalog: Pattern[], conceptId: string) {
  return catalog.find((item) => String(item.id) === conceptId)?.card ?? null
}

export function mapConceptIdsToPatterns(catalog: Pattern[], ids: string[]): Pattern[] {
  const byId = new Map(catalog.map((item) => [String(item.id), item]))
  return ids.map((id) => {
    const fromCatalog = byId.get(id)
    if (fromCatalog) {
      return { ...fromCatalog, approved: true as const }
    }
    return {
      id,
      type: id,
      label: id,
      confidence: 1,
      approved: true as const,
    }
  })
}

export function listConceptEditorLanguages(draft: TaskDraft): string[] {
  const langs = new Set<string>()
  const add = (language: string) => {
    const lang = String(language || "").trim().toLowerCase()
    if (lang) langs.add(lang)
  }
  add(draft.code.language)
  add(draft.languages[0] ?? "")
  for (const lang of Object.keys(draft.languageBlockEditorState ?? {})) add(lang)
  for (const lang of Object.keys(draft.languageVariants ?? {})) add(lang)
  for (const lang of Object.keys(draft.selectedPatternsByLanguage ?? {})) add(lang)
  return [...langs].sort((a, b) => {
    const ai = AUTHORING_LANGS.indexOf(a)
    const bi = AUTHORING_LANGS.indexOf(b)
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })
}

export function getSelectedConceptIdsForLanguage(
  draft: TaskDraft,
  language: string,
): string[] {
  const lang = String(language || "").trim().toLowerCase()
  const fromMap = draft.selectedPatternsByLanguage?.[lang]
  if (Array.isArray(fromMap)) return [...fromMap]
  if (lang === String(draft.code.language || draft.languages[0] || "").toLowerCase()) {
    return draft.selectedPatterns
      .filter((item) => item.approved !== false)
      .map((item) => String(item.id))
  }
  return []
}

export function setSelectedConceptIdsForLanguage(
  draft: TaskDraft,
  language: string,
  ids: string[],
): Record<string, string[]> {
  const lang = String(language || "").trim().toLowerCase()
  return {
    ...(draft.selectedPatternsByLanguage ?? {}),
    [lang]: [...new Set(ids.map(String))],
  }
}

export function collectLanguageCodeSamples(draft: TaskDraft): Array<{ language: string; code: string }> {
  const samples = new Map<string, string>()

  const add = (language: string, code: string) => {
    const lang = String(language || "").trim().toLowerCase()
    const text = String(code || "").trim()
    if (!lang || !text) return
    samples.set(lang, text)
  }

  add(draft.code?.language ?? "", draft.code?.code ?? "")
  add(draft.languages[0] ?? "", draft.code?.code ?? "")

  for (const [language, snapshot] of Object.entries(draft.languageBlockEditorState ?? {})) {
    add(language, snapshot.code)
  }

  for (const [language, variant] of Object.entries(draft.languageVariants ?? {})) {
    if (variant?.original_code) {
      add(language, variant.original_code)
    }
  }

  const activeLanguage = String(draft.code?.language || draft.languages[0] || "")
    .trim()
    .toLowerCase()
  if (activeLanguage && draft.code?.code) {
    samples.set(activeLanguage, String(draft.code.code))
  }

  return [...samples.entries()].map(([language, code]) => ({ language, code }))
}

export function mergeConceptIdsForLanguage(
  currentIds: string[],
  idsToMerge: string[],
): string[] {
  const seen = new Set(currentIds.map(String))
  const next = [...currentIds.map(String)]
  for (const id of idsToMerge) {
    if (seen.has(id)) continue
    seen.add(id)
    next.push(id)
  }
  return next
}

export function buildPatternsByLanguageForSave(draft: TaskDraft): Record<string, string[]> {
  const byLanguage: Record<string, string[]> = {}

  for (const lang of listConceptEditorLanguages(draft)) {
    const ids = getSelectedConceptIdsForLanguage(draft, lang)
    if (ids.length > 0) {
      byLanguage[lang] = [...new Set(ids.map(String))]
    }
  }

  return byLanguage
}
