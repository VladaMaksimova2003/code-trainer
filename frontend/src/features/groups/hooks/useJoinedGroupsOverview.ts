import { useQuery } from "@tanstack/react-query"

import { listJoinedGroupsOverview } from "@/features/groups/api/groupsApi"
import { userQueryScope } from "@/shared/providers/queryClient"

export const JOINED_GROUPS_OVERVIEW_STALE_MS = 60 * 1000

export function useJoinedGroupsOverview(userId?: number | string | null, enabled = true) {
  const scope = userQueryScope(userId)
  return useQuery({
    queryKey: ["groups", "joined", "overview", scope],
    queryFn: listJoinedGroupsOverview,
    staleTime: JOINED_GROUPS_OVERVIEW_STALE_MS,
    enabled: enabled && userId != null,
  })
}
