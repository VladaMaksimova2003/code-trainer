import type { ICodeAnalysisService } from "@/features/task-editor/application/ports/ICodeAnalysisService"
import { AnalysisStatus } from "@/features/task-editor/domain/enums"
import type { AnalysisResult, Pattern } from "@/features/task-editor/domain/entities"
import { httpClient } from "@/features/task-editor/infrastructure/api/httpClient"

interface ApiPattern {
  id: string
  type: string
  label: string
  confidence: number
  source_construct: string
}

export class RemoteCodeAnalysisService implements ICodeAnalysisService {
  async analyze(code: string, language: string): Promise<AnalysisResult> {
    const res = await httpClient.post<{
      patterns: ApiPattern[]
      raw_constructs: string[]
    }>("/tasks/analyze-code", { code, language })

    const patterns: Pattern[] = (res.data.patterns || []).map((p) => ({
      id: p.id,
      type: p.type,
      label: p.label,
      confidence: p.confidence,
      sourceConstruct: p.source_construct,
      approved: false,
    }))

    return {
      patterns,
      rawConstructs: res.data.raw_constructs || [],
      status: AnalysisStatus.READY,
    }
  }
}
