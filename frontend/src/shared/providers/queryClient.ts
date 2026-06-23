import { QueryClient } from "@tanstack/react-query"

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false, staleTime: 60_000 },
  },
})

export function userQueryScope(userId: number | string | null | undefined): string {
  if (userId == null || userId === "") return "guest"
  return String(userId)
}

/** Drop cached API data that embeds per-user progress (tasks, curriculum, groups). */
export function clearUserScopedQueries(): void {
  queryClient.removeQueries({ queryKey: ["tasks"] })
  queryClient.removeQueries({ queryKey: ["curriculum"] })
  queryClient.removeQueries({ queryKey: ["groups"] })
  queryClient.removeQueries({ queryKey: ["task"] })
  queryClient.removeQueries({ queryKey: ["platform-course-author"] })
  queryClient.removeQueries({ queryKey: ["student"] })
}
