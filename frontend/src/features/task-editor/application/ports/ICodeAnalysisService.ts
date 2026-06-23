import type { AnalysisResult } from "@/features/task-editor/domain/entities"

export interface ICodeAnalysisService {
  analyze(code: string, language: string): Promise<AnalysisResult>
}
