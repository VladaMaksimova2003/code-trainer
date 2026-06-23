import type { TaskDraft } from "@/features/task-editor/domain/entities"
import {
  getAssignmentEditorMode,
  isTranslationAssignmentType,
} from "@/features/task-editor/domain/assignmentRules"
import { resolveEditorActivityKind } from "@/features/task-editor/domain/editorActivityTypes"
import { buildPatternsByLanguageForSave } from "@/features/task-editor/domain/expectedConceptPatterns"
import { buildAssignmentApiPayload } from "@/features/task-editor/application/use-cases/buildCreatePayload"
import { validateAssignmentDraft } from "@/features/task-editor/application/use-cases/validateAssignmentDraft"
import { buildBlockTaskApiFields } from "@/features/task-editor/application/use-cases/buildBlockTaskPayload"
import { buildFlowchartApiFields } from "@/features/task-editor/application/use-cases/buildFlowchartApiFields"
import { buildTranslationApiFields } from "@/features/task-editor/application/use-cases/buildTranslationApiFields"
import type { CreatedTask, ITaskRepository } from "@/features/task-editor/application/ports/ITaskRepository"
import { AssignmentEditorRepository } from "@/features/task-editor/infrastructure/repositories/AssignmentEditorRepository"
import { serializeIoValueForTestCase } from "@/features/task-editor/domain/ioValue"
import { flushDraftBlockEditorForSave } from "@/features/task-editor/domain/languageBlockEditorState"

const editorRepo = new AssignmentEditorRepository()

export async function saveAssignment(
  taskRepository: ITaskRepository,
  draft: TaskDraft
): Promise<CreatedTask | { taskId: number; updated: true }> {
  const preparedDraft = flushDraftBlockEditorForSave(draft)
  const validation = validateAssignmentDraft(preparedDraft)
  if (!validation.valid) {
    throw new Error(validation.errors[0] ?? "Validation failed")
  }

  if (preparedDraft.id) {
    const taskId = Number(preparedDraft.id)
    const activityKind = resolveEditorActivityKind(preparedDraft)
    const patternsByLanguage = buildPatternsByLanguageForSave(preparedDraft)
    const patternIds = preparedDraft.selectedPatterns
      .filter((pattern) => pattern.approved !== false)
      .map((pattern) => String(pattern.id))
    const testCasesPayload = preparedDraft.testCases.map((tc, index) => ({
      name: tc.name || `Тест ${index + 1}`,
      inputs: serializeIoValueForTestCase(tc.input),
      output: serializeIoValueForTestCase(tc.expectedOutput),
      description: tc.description,
    }))

    if (activityKind === "assemble") {
      await editorRepo.updateBlockTask(taskId, {
        title: preparedDraft.title,
        description: preparedDraft.description,
        difficulty: preparedDraft.difficulty,
        test_cases: testCasesPayload,
        patterns: patternIds,
        patterns_by_language: patternsByLanguage,
        ...buildBlockTaskApiFields(preparedDraft),
      })
      if (typeof window !== "undefined") {
        window.localStorage.removeItem(`task-draft:${taskId}`)
      }
      return { taskId, updated: true }
    }

    const editorMode = getAssignmentEditorMode(preparedDraft.type)

    if (editorMode === "flowchart") {
      await editorRepo.updateFlowchartTask(taskId, {
        title: preparedDraft.title,
        description: preparedDraft.description,
        difficulty: preparedDraft.difficulty,
        test_cases: testCasesPayload,
        patterns: patternIds,
        ...buildFlowchartApiFields(preparedDraft),
      })
      if (typeof window !== "undefined") {
        window.localStorage.removeItem(`task-draft:${taskId}`)
      }
      return { taskId, updated: true }
    }

    if (isTranslationAssignmentType(preparedDraft.type)) {
      await editorRepo.updateTranslationTask(taskId, {
        title: preparedDraft.title,
        description: preparedDraft.description,
        difficulty: preparedDraft.difficulty,
        test_cases: testCasesPayload,
        patterns: patternIds,
        patterns_by_language: patternsByLanguage,
        ...buildTranslationApiFields(preparedDraft),
      })
      if (typeof window !== "undefined") {
        window.localStorage.removeItem(`task-draft:${taskId}`)
      }
      return { taskId, updated: true }
    }

    throw new Error("Редактирование этого типа задачи пока не поддерживается")
  }

  return taskRepository.createTask(buildAssignmentApiPayload(preparedDraft))
}
