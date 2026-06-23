import { mergeCatalogWithDetected } from "@/features/task-editor/domain/patternCatalog"
import type { AnalysisResult, Pattern } from "@/features/task-editor/domain/entities"

/** Map analysis output to selectable pattern chips. */
export function detectPatterns(analysis: AnalysisResult | null): Pattern[] {
  if (!analysis?.patterns?.length) return []
  return mergeCatalogWithDetected(analysis.patterns)
}
