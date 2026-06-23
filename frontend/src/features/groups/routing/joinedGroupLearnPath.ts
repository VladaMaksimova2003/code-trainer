import type { NavigateFunction } from "react-router-dom"

/** Open /learn filtered to teacher-assigned catalogs for this group. */
export function openJoinedGroupLearn(
  navigate: NavigateFunction,
  groupId: number | string,
): void {
  navigate(`/learn?group=${groupId}`)
}
