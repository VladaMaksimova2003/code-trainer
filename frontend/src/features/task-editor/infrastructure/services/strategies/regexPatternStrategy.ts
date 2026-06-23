import { PatternType } from "@/features/task-editor/domain/enums"
import type { Pattern } from "@/features/task-editor/domain/entities"

/** Rule-based strategy — replaceable without touching UI. */
export function detectPatternsWithRegex(code: string): Pattern[] {
  const found: Pattern[] = []
  const rules: Array<{ type: PatternType; re: RegExp; confidence: number; label: string }> = [
    { type: PatternType.BRANCHING, re: /\bif\b|\belse\b|\belif\b/, confidence: 0.88, label: "Branching" },
    { type: PatternType.LOOP, re: /\bfor\b|\bwhile\b/, confidence: 0.9, label: "Loop" },
    { type: PatternType.FUNCTION, re: /\bdef\b|\bfunction\b|\w+\s*\(/, confidence: 0.75, label: "Function" },
    { type: PatternType.ACCUMULATION, re: /\+=|-=|\*=|\/=/, confidence: 0.8, label: "Accumulation" },
    { type: PatternType.CONDITIONAL, re: /[<>!=]=?|&&|\|\|/, confidence: 0.7, label: "Conditional" },
  ]
  for (const rule of rules) {
    if (rule.re.test(code)) {
      found.push({
        id: `local-${rule.type}`,
        type: rule.type,
        label: rule.label,
        confidence: rule.confidence,
        sourceConstruct: "regex",
        approved: false,
      })
    }
  }
  return found
}
