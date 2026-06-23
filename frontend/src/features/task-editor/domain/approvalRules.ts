import type { AnalysisResult, Pattern } from "@/features/task-editor/domain/entities"
import { AnalysisStatus } from "@/features/task-editor/domain/enums"

export function approveAllPatterns(patterns: Pattern[]): Pattern[] {
  return patterns.map((p) => ({ ...p, approved: true }))
}

export function rejectAllPatterns(patterns: Pattern[]): Pattern[] {
  return patterns.map((p) => ({ ...p, approved: false }))
}

export function togglePatternApproval(
  patterns: Pattern[],
  patternId: string,
  approved: boolean
): Pattern[] {
  return patterns.map((p) =>
    p.id === patternId ? { ...p, approved } : p
  )
}

export function buildApprovedAnalysis(
  analysis: AnalysisResult,
  patterns: Pattern[]
): AnalysisResult {
  return {
    ...analysis,
    patterns,
    status: AnalysisStatus.APPROVED,
  }
}
