import { useTaskOverview } from "@/shared/hooks/useTaskOverview"

/** @deprecated Prefer `useTaskOverview()` for list pages and `useTaskDetail()` for task pages. */
export function useTasks(filters = {}) {
  return useTaskOverview(filters)
}
