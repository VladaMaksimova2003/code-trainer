import { useEffect } from "react"
import { buildDraftPayload, writeDraft } from "@/features/task-solving/model/taskDraftHelpers"
import type { BlockPlacement } from "@/domain/blockAssembly"
import type { FlowPayload } from "@/shared/types/flow"
import type { TaskDto } from "@/shared/types/task"

type FlowchartSolutionMode = "code" | "flow"

interface UseDraftStateOptions {
  taskId: string | undefined
  task: TaskDto | null
  loadedTaskId: string | null
  isTaskLoading: boolean
  code: string
  flow: FlowPayload
  blockAssemblyCode: string
  blockPlacements: BlockPlacement[]
  blockLanguage: string
  selectedExampleLanguage: string
  userLanguage: string
  activeTab: string
  bottomTab: string
  flowchartSolutionMode: FlowchartSolutionMode
}

/**
 * Persists solver workspace fields to localStorage (FE-ARCH-6.2).
 * Key: task-draft:{taskId} — unchanged from pre-extraction behavior.
 */
export function useDraftState({
  taskId,
  task,
  loadedTaskId,
  isTaskLoading,
  code,
  flow,
  blockAssemblyCode,
  blockPlacements,
  blockLanguage,
  selectedExampleLanguage,
  userLanguage,
  activeTab,
  bottomTab,
  flowchartSolutionMode,
}: UseDraftStateOptions) {
  useEffect(() => {
    if (!taskId || !task || loadedTaskId !== String(taskId) || isTaskLoading) return
    writeDraft(
      taskId,
      buildDraftPayload(task, {
        code,
        flow,
        blockAssemblyCode,
        blockPlacements,
        blockLanguage,
        selectedExampleLanguage,
        userLanguage,
        activeTab,
        bottomTab,
        flowchartSolutionMode,
      }),
    )
  }, [
    taskId,
    task,
    loadedTaskId,
    isTaskLoading,
    code,
    flow,
    blockAssemblyCode,
    blockPlacements,
    blockLanguage,
    selectedExampleLanguage,
    userLanguage,
    activeTab,
    bottomTab,
    flowchartSolutionMode,
  ])
}
