import { useQuery } from "@tanstack/react-query"
import { getTask, TASK_DETAIL_STALE_MS } from "@/shared/api/tasksClient"
import { normalizeCurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"
import type { TaskDto } from "@/shared/types/task"
import { userQueryScope } from "@/shared/providers/queryClient"

export function useTaskDetail(
  taskId: string | number | undefined | null,
  learningLanguage?: string,
  userId?: number | string | null,
  sourceLanguage?: string,
) {
  const normalizedId = taskId == null ? undefined : String(taskId)
  const normalizedLearning = normalizeCurriculumLearningLanguage(learningLanguage)
  const normalizedSource = normalizeCurriculumLearningLanguage(sourceLanguage)
  const scope = userQueryScope(userId)
  return useQuery<TaskDto>({
    queryKey: [
      "task",
      scope,
      normalizedId,
      normalizedLearning || "default",
      normalizedSource || "auto",
    ],
    queryFn: () =>
      getTask(normalizedId as string, {
        learningLanguage: normalizedLearning,
        sourceLanguage: normalizedSource,
      }),
    enabled: Boolean(normalizedId),
    staleTime: TASK_DETAIL_STALE_MS,
  })
}
