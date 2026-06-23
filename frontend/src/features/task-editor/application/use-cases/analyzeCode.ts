import type { ICodeAnalysisService } from "@/features/task-editor/application/ports/ICodeAnalysisService"
import { AnalysisStatus } from "@/features/task-editor/domain/enums"
import type { AnalysisResult } from "@/features/task-editor/domain/entities"

export async function analyzeCode(
  service: ICodeAnalysisService,
  code: string,
  language: string
): Promise<AnalysisResult> {
  if (!code.trim()) {
    return { patterns: [], rawConstructs: [], status: AnalysisStatus.IDLE }
  }
  try {
    const result = await service.analyze(code, language)
    return { ...result, status: AnalysisStatus.READY }
  } catch (err) {
    const message = err instanceof Error ? err.message : "Analysis failed"
    return {
      patterns: [],
      rawConstructs: [],
      status: AnalysisStatus.ERROR,
      error: message,
    }
  }
}
