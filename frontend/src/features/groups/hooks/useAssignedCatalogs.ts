import { useQuery } from "@tanstack/react-query"

import { listAssignedCatalogs } from "@/features/groups/api/groupsApi"
import { userQueryScope } from "@/shared/providers/queryClient"

export const ASSIGNED_CATALOGS_STALE_MS = 60 * 1000

export function useAssignedCatalogs(userId?: number | string | null, enabled = true) {
  const scope = userQueryScope(userId)
  return useQuery({
    queryKey: ["groups", "joined", "assigned-catalogs", scope],
    queryFn: listAssignedCatalogs,
    staleTime: ASSIGNED_CATALOGS_STALE_MS,
    enabled: enabled && userId != null,
    retry: 2,
  })
}
