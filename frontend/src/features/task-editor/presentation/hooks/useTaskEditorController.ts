import { useCallback } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { saveAssignment } from "@/features/task-editor/application/use-cases/saveAssignment"
import { getTaskRepository } from "@/features/task-editor/infrastructure/container"
import { useTaskDraftStore } from "@/features/task-editor/presentation/store/taskDraftStore"

export function useTaskEditorController() {
  const queryClient = useQueryClient()
  const draft = useTaskDraftStore((s) => s.draft)
  const patchDraft = useTaskDraftStore((s) => s.patchDraft)
  const setTestCases = useTaskDraftStore((s) => s.setTestCases)
  const setSelectedPatterns = useTaskDraftStore((s) => s.setSelectedPatterns)
  const reset = useTaskDraftStore((s) => s.reset)

  const saveMutation = useMutation({
    mutationFn: async () => {
      const currentDraft = useTaskDraftStore.getState().draft
      return saveAssignment(getTaskRepository(), currentDraft)
    },
    onSuccess: (result) => {
      if ("taskId" in result) {
        const taskId = String(result.taskId)
        queryClient.invalidateQueries({ queryKey: ["task", taskId] })
        queryClient.invalidateQueries({ queryKey: ["assignment-edit", taskId] })
        window.dispatchEvent(new CustomEvent("teacher-tasks-changed"))
      }
    },
  })

  const clearAll = useCallback(() => {
    reset()
  }, [reset])

  return {
    draft,
    patchDraft,
    setSelectedPatterns,
    setTestCases,
    saveMutation,
    clearAll,
  }
}
