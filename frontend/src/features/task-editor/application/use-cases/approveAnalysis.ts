import {
  approveAllPatterns,
  buildApprovedAnalysis,
  rejectAllPatterns,
  togglePatternApproval,
} from "@/features/task-editor/domain/approvalRules"
import type { AnalysisResult, Pattern } from "@/features/task-editor/domain/entities"

export function approveAnalysis(
  analysis: AnalysisResult,
  patterns: Pattern[]
): { analysis: AnalysisResult; patterns: Pattern[] } {
  const approved = approveAllPatterns(patterns)
  return {
    patterns: approved,
    analysis: buildApprovedAnalysis(analysis, approved),
  }
}

export function rejectAnalysis(
  analysis: AnalysisResult,
  patterns: Pattern[]
): { analysis: AnalysisResult; patterns: Pattern[] } {
  const rejected = rejectAllPatterns(patterns)
  return { patterns: rejected, analysis: { ...analysis, patterns: rejected } }
}

export function setPatternApproval(
  patterns: Pattern[],
  patternId: string,
  approved: boolean
): Pattern[] {
  return togglePatternApproval(patterns, patternId, approved)
}
