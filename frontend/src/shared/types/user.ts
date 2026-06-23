/** Auth and profile user shapes used across shared modules. */

import type { TaskDto } from "./task"

export type NormalizedUserRole = "STUDENT" | "TEACHER" | "ADMIN"

export interface UserLike {
  email?: string | null
  role?: string | null
  roles?: string[] | null
  name?: string | null
  display_name?: string | null
  full_name?: string | null
  role_label?: string | null
  avatar?: { initial?: string } | null
  user_id?: number | string | null
  id?: number | string | null
  streak_days?: number | null
  activity_by_date?: Record<string, number> | null
  [key: string]: unknown
}

export interface UserProfileStats {
  tasks_count?: number
  catalogs_count?: number
  groups_count?: number
  students_count?: number
  [key: string]: unknown
}

export interface UserPublicCatalog {
  id?: number | string
  title?: string
  name?: string
  tasks?: TaskDto[]
  [key: string]: unknown
}

/** GET /users/:id (teacher or student public profile). */
export interface UserProfileDto {
  kind?: "teacher" | "student" | string
  user_id?: number | string
  display_name?: string
  full_name?: string
  is_own_profile?: boolean
  can_browse_catalogs?: boolean
  level?: string
  public_catalogs?: UserPublicCatalog[]
  stats?: UserProfileStats
  summary?: Record<string, unknown>
  teacher?: { id?: number | string; name?: string; [key: string]: unknown }
  [key: string]: unknown
}
