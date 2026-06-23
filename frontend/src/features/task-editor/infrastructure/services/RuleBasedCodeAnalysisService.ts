import type { ICodeAnalysisService } from "@/features/task-editor/application/ports/ICodeAnalysisService"
import { AnalysisStatus } from "@/features/task-editor/domain/enums"
import type { AnalysisResult, Pattern } from "@/features/task-editor/domain/entities"
import { detectPatternsWithRegex } from "@/features/task-editor/infrastructure/services/strategies/regexPatternStrategy"

export class RuleBasedCodeAnalysisService implements ICodeAnalysisService {
  async analyze(code: string, _language: string): Promise<AnalysisResult> {
    const patterns: Pattern[] = detectPatternsWithRegex(code)
    return {
      patterns,
      rawConstructs: patterns.map((p) => String(p.type)),
      status: AnalysisStatus.READY,
    }
  }
}
