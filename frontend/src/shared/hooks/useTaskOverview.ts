import { useQuery } from "@tanstack/react-query"
import { getTaskOverview, getTaskTypes, TASK_OVERVIEW_STALE_MS } from "@/shared/api/tasksClient"
import { listAccessibleAssignmentSets } from "@/features/tasks/api/recommendationsApi"
import type { TaskOverviewFilters } from "@/shared/types/taskOverview"
import { formatApiErrorDetail } from "@/shared/utils/formatApiErrorDetail"
import { userQueryScope } from "@/shared/providers/queryClient"

interface ApiErrorShape {
  response?: { data?: { detail?: unknown } }
  message?: string
}

export function getTaskOverviewErrorMessage(err: unknown): string {
  const error = err as ApiErrorShape
  const detail = formatApiErrorDetail(error?.response?.data?.detail)
  if (detail) return detail
  if (!error?.response) {
    return "Не удалось связаться с сервером. Проверьте, что API запущен."
  }
  return error?.message || "Не удалось загрузить задачи"
}

interface UseTaskOverviewOptions {
  includeAssignmentSets?: boolean
  includeTaskTypes?: boolean
}

export function useTaskOverview(
  filters: TaskOverviewFilters = {},
  options: UseTaskOverviewOptions = {},
  userId?: number | string | null,
) {
  const includeAssignmentSets = options.includeAssignmentSets !== false
  const includeTaskTypes = options.includeTaskTypes !== false
  const scope = userQueryScope(userId)

  const overviewQuery = useQuery({
    queryKey: ["tasks", "overview", scope, filters],
    queryFn: () => getTaskOverview(filters),
    staleTime: TASK_OVERVIEW_STALE_MS,
  })

  const typesQuery = useQuery({
    queryKey: ["tasks", "types", scope],
    queryFn: getTaskTypes,
    staleTime: TASK_OVERVIEW_STALE_MS,
    enabled: includeTaskTypes,
  })

  const setsQuery = useQuery({
    queryKey: ["tasks", "assignment-sets", scope],
    queryFn: () => listAccessibleAssignmentSets(),
    staleTime: TASK_OVERVIEW_STALE_MS,
    enabled: includeAssignmentSets,
  })

  const tasks = Array.isArray(overviewQuery.data?.tasks) ? overviewQuery.data.tasks : []
  const taskTypes = Array.isArray(typesQuery.data) ? typesQuery.data : []
  const assignmentSets = Array.isArray(setsQuery.data) ? setsQuery.data : []
  const loading = overviewQuery.isLoading
  const setsLoading = setsQuery.isLoading
  const typesLoading = typesQuery.isLoading
  const error =
    overviewQuery.error
      ? getTaskOverviewErrorMessage(overviewQuery.error)
      : typesQuery.error
        ? getTaskOverviewErrorMessage(typesQuery.error)
        : includeAssignmentSets && setsQuery.error
          ? getTaskOverviewErrorMessage(setsQuery.error)
          : null

  const reload = async () => {
    await Promise.all([
      overviewQuery.refetch(),
      typesQuery.refetch(),
      ...(includeAssignmentSets ? [setsQuery.refetch()] : []),
    ])
  }

  return {
    tasks,
    total: overviewQuery.data?.total ?? tasks.length,
    taskTypes,
    assignmentSets,
    loading,
    setsLoading,
    typesLoading,
    error,
    reload,
  }
}
