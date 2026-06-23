/**
 * Runtime language helpers — populated from GET /languages via useLanguages().
 * Do NOT add static language lists here.
 */

import type { LanguageItem } from "@/shared/types/language"

const HIDDEN_LANGUAGE_IDS = new Set(["javascript"])

let _languages: LanguageItem[] = []

export function setLanguagesCache(languages: unknown): void {
  _languages = Array.isArray(languages)
    ? languages.filter((item) => !HIDDEN_LANGUAGE_IDS.has(String((item as LanguageItem)?.id || "").toLowerCase())) as LanguageItem[]
    : []
}

export function getLanguagesCache(): LanguageItem[] {
  return _languages
}

function visibleLanguages(): LanguageItem[] {
  return _languages
}

export function getLanguageLabel(id: string | null | undefined): string {
  const item = visibleLanguages().find((l) => l.id === id)
  return item?.label ?? id ?? ""
}

const MONACO_LANGUAGE_FALLBACK: Record<string, string> = {
  python: "python",
  typescript: "typescript",
  java: "java",
  cpp: "cpp",
  c: "c",
  go: "go",
  csharp: "csharp",
  pascal: "pascal",
}

export function getMonacoLanguage(id: string | null | undefined): string {
  const key = String(id || "").toLowerCase()
  const item = visibleLanguages().find((l) => l.id === key)
  if (item?.monaco_language) {
    return item.monaco_language
  }
  return MONACO_LANGUAGE_FALLBACK[key] || key || "plaintext"
}

/** Languages that can run automated tests (student submit + teacher reference run). */
export function getExecutableLanguageIds(): string[] {
  return visibleLanguages()
    .filter((l) => (l.supported_features || []).includes("test"))
    .map((l) => l.id)
}

/** Languages available when creating/editing assignments (includes Java, C#, Pascal). */
export function getTaskAuthoringLanguageIds(): string[] {
  return getExecutableLanguageIds()
}

export function getDefaultLanguageId(): string {
  const langs = visibleLanguages()
  if (langs.some((l) => l.id === "python")) {
    return "python"
  }
  return langs[0]?.id ?? "python"
}

export function getAllLanguageIds(): string[] {
  return visibleLanguages().map((l) => l.id)
}
