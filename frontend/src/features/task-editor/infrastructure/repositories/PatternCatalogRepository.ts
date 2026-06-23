import type { Pattern } from "@/features/task-editor/domain/entities"
import type { IPatternCatalogRepository } from "@/features/task-editor/application/ports/IPatternCatalogRepository"
import { httpClient } from "@/features/task-editor/infrastructure/api/httpClient"

export class PatternCatalogRepository implements IPatternCatalogRepository {
  async fetchCatalog(): Promise<Pattern[]> {
    const res = await httpClient.get<{
      patterns: Array<{
        id: string
        type: string
        label: string
        description?: string
        card?: Pattern["card"]
      }>
      source?: string
      total?: number
    }>("/tasks/patterns")
    return (res.data.patterns ?? []).map((p) => ({
      id: p.id,
      type: p.type,
      label: p.label,
      confidence: 1,
      approved: false,
      card: p.card,
    }))
  }
}
