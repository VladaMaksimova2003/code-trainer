import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"

export const LANGUAGE_ROUTES: Record<CurriculumLearningLanguage, string> = {
  python: "/learn/python",
  pascal: "/learn/pascal",
  cpp: "/learn/cpp",
  csharp: "/learn/csharp",
  java: "/learn/java",
}

export const LANGUAGE_GLYPHS: Record<CurriculumLearningLanguage, string> = {
  python: "Py",
  pascal: "Pas",
  cpp: "C++",
  csharp: "C#",
  java: "Jv",
}

export const LANGUAGE_LABELS: Record<CurriculumLearningLanguage, string> = {
  python: "Python",
  pascal: "Pascal",
  cpp: "C++",
  csharp: "C#",
  java: "Java",
}

export const LANGUAGE_TRACK_DESCRIPTIONS: Record<CurriculumLearningLanguage, string> = {
  python: "Линейный путь от первой программы до алгоритмов, ООП и итогового проекта.",
  pascal: "Линейный путь от первой программы до процедур и рекурсии. Проходите сборники по порядку.",
  cpp: "Линейный путь от базового синтаксиса C++ до алгоритмов и ООП.",
  csharp: "Линейный путь от основ C# до коллекций, ООП и практических алгоритмов.",
  java: "Линейный путь от основ Java до структур данных и объектно-ориентированного программирования.",
}

export interface CurriculumLanguageOption {
  id: CurriculumLearningLanguage
  label: string
  glyph: string
  route: string
}

export const CURRICULUM_LANGUAGE_OPTIONS: CurriculumLanguageOption[] = (
  Object.keys(LANGUAGE_ROUTES) as CurriculumLearningLanguage[]
).map((id) => ({
  id,
  label: LANGUAGE_LABELS[id],
  glyph: LANGUAGE_GLYPHS[id],
  route: LANGUAGE_ROUTES[id],
}))

export const LEARNING_LANG_STORAGE_KEY = "curriculum_learning_language"
export const LEARNING_LANG_CHANGED_EVENT = "curriculum-learning-language-changed"

export function readStoredLearningLanguage(): CurriculumLearningLanguage {
  try {
    const raw = localStorage.getItem(LEARNING_LANG_STORAGE_KEY)
    if (raw && raw in LANGUAGE_ROUTES) return raw as CurriculumLearningLanguage
  } catch {
    /* ignore */
  }
  return "python"
}

export function writeStoredLearningLanguage(lang: CurriculumLearningLanguage): void {
  try {
    localStorage.setItem(LEARNING_LANG_STORAGE_KEY, lang)
    window.dispatchEvent(new CustomEvent(LEARNING_LANG_CHANGED_EVENT, { detail: lang }))
  } catch {
    /* ignore */
  }
}

export function languageRoute(lang: string): string | null {
  const key = lang as CurriculumLearningLanguage
  return LANGUAGE_ROUTES[key] ?? null
}
