import { CompositeCodeAnalysisService } from "@/features/task-editor/infrastructure/services/CompositeCodeAnalysisService"
import { PatternCatalogRepository } from "@/features/task-editor/infrastructure/repositories/PatternCatalogRepository"
import { TaskRepository } from "@/features/task-editor/infrastructure/repositories/TaskRepository"
import { TaskTypeRepository } from "@/features/task-editor/infrastructure/repositories/TaskTypeRepository"
import type { ICodeAnalysisService } from "@/features/task-editor/application/ports/ICodeAnalysisService"
import type { IPatternCatalogRepository } from "@/features/task-editor/application/ports/IPatternCatalogRepository"
import type { ITaskRepository } from "@/features/task-editor/application/ports/ITaskRepository"
import type { ITaskTypeRepository } from "@/features/task-editor/application/ports/ITaskTypeRepository"

let analysisService: ICodeAnalysisService | null = null
let taskRepository: ITaskRepository | null = null
let patternCatalogRepository: IPatternCatalogRepository | null = null
let taskTypeRepository: ITaskTypeRepository | null = null

export function getCodeAnalysisService(): ICodeAnalysisService {
  if (!analysisService) {
    analysisService = new CompositeCodeAnalysisService()
  }
  return analysisService
}

export function getTaskRepository(): ITaskRepository {
  if (!taskRepository) {
    taskRepository = new TaskRepository()
  }
  return taskRepository
}

export function getPatternCatalogRepository(): IPatternCatalogRepository {
  if (!patternCatalogRepository) {
    patternCatalogRepository = new PatternCatalogRepository()
  }
  return patternCatalogRepository
}

export function getTaskTypeRepository(): ITaskTypeRepository {
  if (!taskTypeRepository) {
    taskTypeRepository = new TaskTypeRepository()
  }
  return taskTypeRepository
}
