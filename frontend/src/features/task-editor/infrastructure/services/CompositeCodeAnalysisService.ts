import type { ICodeAnalysisService } from "@/features/task-editor/application/ports/ICodeAnalysisService"
import type { AnalysisResult } from "@/features/task-editor/domain/entities"
import { RuleBasedCodeAnalysisService } from "@/features/task-editor/infrastructure/services/RuleBasedCodeAnalysisService"
import { RemoteCodeAnalysisService } from "@/features/task-editor/infrastructure/services/RemoteCodeAnalysisService"

/** Tries API first; falls back to local rules (AI-ready swap point). */
export class CompositeCodeAnalysisService implements ICodeAnalysisService {
  constructor(
    private readonly remote: ICodeAnalysisService = new RemoteCodeAnalysisService(),
    private readonly local: ICodeAnalysisService = new RuleBasedCodeAnalysisService()
  ) {}

  async analyze(code: string, language: string): Promise<AnalysisResult> {
    try {
      return await this.remote.analyze(code, language)
    } catch {
      return this.local.analyze(code, language)
    }
  }
}
