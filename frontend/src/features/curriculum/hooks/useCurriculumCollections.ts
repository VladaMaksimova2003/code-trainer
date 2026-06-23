import { useQuery } from "@tanstack/react-query"
import { fetchCurriculumCollections } from "@/features/curriculum/api/curriculumApi"
import { userQueryScope } from "@/shared/providers/queryClient"

export const CURRICULUM_COLLECTIONS_STALE_MS = 5 * 60 * 1000

export function useCurriculumCollections(
  language?: string,
  options?: {
    enabled?: boolean
    authenticated?: boolean
    userId?: number | string | null
  },
) {
  const authenticated = options?.authenticated ?? true
  const scope = userQueryScope(options?.userId)
  return useQuery({
    queryKey: ["curriculum", "collections", scope, language ?? "all", { light: true, authenticated }],
    queryFn: () => fetchCurriculumCollections(language, { light: true }),
    staleTime: CURRICULUM_COLLECTIONS_STALE_MS,
    enabled: options?.enabled ?? true,
  })
}

export function getCurriculumCollectionsErrorMessage(err: unknown): string {
  const error = err as { response?: { data?: { detail?: string } }; message?: string }
  return error?.response?.data?.detail || error?.message || "Не удалось загрузить языки"
}
