/** Student flowchart editor (React Flow) — blocks / diagram / flowchart-to-code task types. */

import type { TaskDto } from "@/shared/types/task"

export function isFlowchartTask(task: TaskDto | null | undefined): boolean {
  if (!task) return false
  const type = task.type
  return type === "blocks" || type === "diagram" || type === "task_flowchart_to_code"
}
