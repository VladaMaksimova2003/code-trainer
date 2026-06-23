import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { hasFlowchartDiagram } from "@/features/task-editor/application/use-cases/buildFlowchartApiFields"
import { validateFlowchartStructure } from "@/features/task-editor/domain/validateFlowchartStructure"

/** Flowchart tasks: need a teacher diagram and/or student-visible reference code. */
export function validateFlowchartAssignment(draft: TaskDraft): string[] {
  const errors: string[] = []
  const hasDiagram = hasFlowchartDiagram(draft)
  const referenceCode = draft.code.code?.trim() ?? ""
  const exposesCode = Boolean(draft.flowchartExposeReferenceCode && referenceCode)

  if (!hasDiagram && !exposesCode) {
    errors.push(
      "Добавьте эталонную блок-схему и/или эталонный код (с опцией показа студенту).",
    )
    return errors
  }

  if (hasDiagram) {
    errors.push(...validateFlowchartStructure(draft.flow))
  }

  if (draft.flowchartExposeReferenceCode && !referenceCode) {
    errors.push("Введите эталонный код или отключите показ кода студенту.")
  }

  return errors
}
