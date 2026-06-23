import type { Pattern } from "@/features/task-editor/domain/entities"

export interface IPatternCatalogRepository {
  fetchCatalog(): Promise<Pattern[]>
}
