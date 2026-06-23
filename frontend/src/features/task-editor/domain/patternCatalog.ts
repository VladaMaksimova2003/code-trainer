import { PatternType } from "@/features/task-editor/domain/enums"
import type { Pattern } from "@/features/task-editor/domain/entities"

export const PATTERN_CATALOG: Pattern[] = [
  { id: "cat-branching", type: PatternType.BRANCHING, label: "Branching", confidence: 1 },
  { id: "cat-loop", type: PatternType.LOOP, label: "Loop", confidence: 1 },
  { id: "cat-function", type: PatternType.FUNCTION, label: "Function", confidence: 1 },
  { id: "cat-accumulation", type: PatternType.ACCUMULATION, label: "Accumulation", confidence: 1 },
  { id: "cat-conditional", type: PatternType.CONDITIONAL, label: "Conditional", confidence: 1 },
]

export function filterPatterns(query: string, patterns: Pattern[]): Pattern[] {
  const q = query.trim().toLowerCase()
  if (!q) return patterns
  return patterns.filter(
    (p) =>
      p.label.toLowerCase().includes(q) ||
      String(p.type).toLowerCase().includes(q)
  )
}

export function mergeCatalogWithDetected(detected: Pattern[]): Pattern[] {
  const byId = new Map<string, Pattern>()
  for (const item of PATTERN_CATALOG) {
    byId.set(String(item.id), { ...item })
  }
  for (const d of detected) {
    byId.set(String(d.id), { ...d, approved: d.approved ?? true })
  }
  return Array.from(byId.values())
}
