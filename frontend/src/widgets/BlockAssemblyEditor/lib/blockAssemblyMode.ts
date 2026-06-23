import { templateScaffoldIsWhitespaceOnly } from "@/domain/blockAssembly/blockScaffold"

const EXT_BY_LANG = {
  python: "py",
  javascript: "js",
  typescript: "ts",
  java: "java",
  cpp: "cpp",
  c: "c",
  csharp: "cs",
  pascal: "pas",
}

/** Template-with-gaps vs build-from-scratch (never both in one task). */
export function isTemplateAssemblyMode(baseCode, rawTemplate) {
  const template = String(rawTemplate ?? "")
  if (template && /\{\d+\}/.test(template)) {
    if (templateScaffoldIsWhitespaceOnly(template)) {
      return false
    }
    return true
  }
  return Boolean(baseCode && String(baseCode).trim().length > 0)
}

export function getAssemblyFileName(language) {
  const lang = String(language || "python").toLowerCase()
  const ext = EXT_BY_LANG[lang] || "txt"
  return `solution.${ext}`
}
