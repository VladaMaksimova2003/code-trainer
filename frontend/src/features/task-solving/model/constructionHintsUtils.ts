import type { PanelError, TestCaseResult } from "@/shared/types/execution"

type PatternCheck = (code: string) => boolean

const PATTERN_USAGE_CHECKS: Record<string, PatternCheck> = {
  function_definition: (code) =>
    /\bdef\s+\w+/.test(code) ||
    /\bfunction\s+\w+/.test(code) ||
    /\b(int|void|double|float|char|bool|auto)\s+\w+\s*\([^)]*\)/.test(code),
  for_loop: (code) => /\bfor\b/.test(code),
  while_loop: (code) => /\bwhile\b/.test(code),
  if_statement: (code) => /\bif\b/.test(code) || /\?\s*[^:]+\s*:/.test(code),
  return_statement: (code) => /\breturn\b/.test(code),
  binary_expression: (code) => /[+\-*/%]/.test(code),
  nested_loops: (code) => {
    const loops = code.match(/\b(for|while)\b/g)
    return (loops?.length ?? 0) >= 2
  },
  io: (code) =>
    /\b(print|console\.log|cout|fmt\.Print|Println|printf|input|prompt|cin|Scan)\b/.test(code),
  arith: (code) => /[+\-*/%]/.test(code) || /\/\//.test(code) || /Math\.floor/.test(code),
  assign: (code) => /[=:]=?/.test(code),
  cond: (code) => /\bif\b/.test(code),
  loop: (code) => /\b(while|for)\b/.test(code),
}

export function isPatternUsedInCode(pattern: string, code = ""): boolean {
  const source = String(code)
  const check = PATTERN_USAGE_CHECKS[pattern]
  if (check) return check(source)
  return false
}

export function buildPatternUsageMap(
  patterns: string[] = [],
  code = "",
): Record<string, boolean> {
  const map: Record<string, boolean> = {}
  for (const pattern of patterns) {
    map[pattern] = isPatternUsedInCode(pattern, code)
  }
  return map
}

export interface ConstructHint {
  title?: string
  examples?: Record<string, string>
  variants?: Record<string, Array<{ name?: string; code?: string }>>
}

export interface ConstructVariant {
  name: string
  code: string
}

/**
 * Variants for construct popover — supports future `variants` array in API.
 */
export function getConstructVariants(
  hint: ConstructHint | null | undefined,
  learningLang: string,
  fallbackTitle = "Пример",
): ConstructVariant[] {
  if (!hint) return []

  const variantsByLang = hint.variants?.[learningLang]
  if (Array.isArray(variantsByLang) && variantsByLang.length > 0) {
    return variantsByLang.map((item, index) => ({
      name: item.name || `${fallbackTitle} ${index + 1}`,
      code: item.code || "",
    }))
  }

  const langKey = String(learningLang || "").toLowerCase()
  const examples = hint.examples || {}
  const example =
    examples[langKey] ??
    examples[learningLang] ??
    Object.entries(examples).find(([key]) => key.toLowerCase() === langKey)?.[1]
  if (typeof example === "string" && example.trim()) {
    return [{ name: fallbackTitle, code: example }]
  }

  const firstExample = Object.values(hint.examples || {}).find(
    (value) => typeof value === "string" && value.trim(),
  )
  if (typeof firstExample === "string" && firstExample) {
    return [{ name: fallbackTitle, code: firstExample }]
  }

  return []
}

interface ErrorWithLine {
  line?: number
  text?: string
  message?: string
}

export function pickEditorHighlightLine({
  compilerErrors = [],
  linterErrors = [],
  results = [],
}: {
  compilerErrors?: PanelError[]
  linterErrors?: PanelError[]
  results?: TestCaseResult[]
}): number | null {
  const pickLine = (errors: ErrorWithLine[]) => {
    for (const error of errors) {
      if (error?.line != null && Number.isFinite(Number(error.line))) {
        return Number(error.line)
      }
      const text = String(error?.text || error?.message || "")
      const match = text.match(/Line\s+(\d+)/i) || text.match(/строка\s+(\d+)/i)
      if (match) return Number(match[1])
    }
    return null
  }

  return pickLine(compilerErrors) ?? pickLine(linterErrors) ?? pickLine(results) ?? null
}
