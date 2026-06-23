import type { Pattern } from "@/features/task-editor/domain/entities"
import type { IPatternCatalogRepository } from "@/features/task-editor/application/ports/IPatternCatalogRepository"

export async function loadPatternCatalog(
  repository: IPatternCatalogRepository
): Promise<Pattern[]> {
  return repository.fetchCatalog()
}
