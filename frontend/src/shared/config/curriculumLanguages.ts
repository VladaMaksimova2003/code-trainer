/** Languages with curriculum tracks (showcase / unified tasks). */
export const CURRICULUM_LEARNING_LANGUAGES = ["pascal", "python", "cpp", "csharp", "java"] as const

export type CurriculumLearningLanguage = (typeof CURRICULUM_LEARNING_LANGUAGES)[number]

export function isCurriculumLearningLanguage(
  value: string | null | undefined,
): value is CurriculumLearningLanguage {
  const lang = String(value || "").toLowerCase()
  return (CURRICULUM_LEARNING_LANGUAGES as readonly string[]).includes(lang)
}

export function normalizeCurriculumLearningLanguage(
  value: string | null | undefined,
): CurriculumLearningLanguage | undefined {
  const lang = String(value || "").toLowerCase()
  return isCurriculumLearningLanguage(lang) ? lang : undefined
}

export function resolveLearningLanguageFromNav(
  state: { learningLanguage?: string; collectionId?: string | number | null } | null | undefined,
): CurriculumLearningLanguage | undefined {
  const fromState = normalizeCurriculumLearningLanguage(state?.learningLanguage)
  if (fromState) return fromState
  const collectionId = String(state?.collectionId || "").toLowerCase()
  for (const lang of CURRICULUM_LEARNING_LANGUAGES) {
    if (collectionId.includes(lang)) return lang
  }
  return undefined
}
