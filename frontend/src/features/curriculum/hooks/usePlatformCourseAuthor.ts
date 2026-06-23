import { useQuery } from "@tanstack/react-query"

import { PLATFORM_COURSE } from "@/features/curriculum/platformCourse"
import { getPlatformCourseMeta } from "@/features/task-catalog/infrastructure/catalogApi"
import { getTeacherProfile } from "@/shared/api"
import type { UserLike } from "@/shared/types/user"

export interface PlatformCourseAuthor {
  name: string
  userId: number | string | null
  profilePath: string | null
}

function authorFromMeta(meta: {
  author_name?: string | null
  author_user_id?: number | null
}): PlatformCourseAuthor | null {
  const name = meta.author_name?.trim()
  const userId = meta.author_user_id ?? null
  if (!name && userId == null) return null
  return {
    name: name || PLATFORM_COURSE.fallbackAuthor,
    userId,
    profilePath: userId != null ? `/users/${userId}` : null,
  }
}

async function fetchPlatformCourseAuthor(): Promise<PlatformCourseAuthor> {
  const envAuthorId = import.meta.env.VITE_PLATFORM_COURSE_AUTHOR_USER_ID
  if (envAuthorId) {
    try {
      const profile = await getTeacherProfile(envAuthorId)
      const name =
        profile.display_name?.trim() ||
        profile.full_name?.trim() ||
        PLATFORM_COURSE.fallbackAuthor
      return {
        name,
        userId: profile.user_id ?? envAuthorId,
        profilePath: `/users/${profile.user_id ?? envAuthorId}`,
      }
    } catch {
      /* fall through */
    }
  }

  try {
    const meta = await getPlatformCourseMeta()
    const fromMeta = authorFromMeta(meta)
    if (fromMeta) return fromMeta
  } catch {
    /* fall through */
  }

  return { name: PLATFORM_COURSE.fallbackAuthor, userId: null, profilePath: null }
}

/** Prefer author from curriculum collections payload; hook is a legacy fallback. */
export function usePlatformCourseAuthor(_user?: UserLike | null | undefined) {
  return useQuery({
    queryKey: ["platform-course-author"],
    queryFn: fetchPlatformCourseAuthor,
    staleTime: 5 * 60 * 1000,
  })
}
