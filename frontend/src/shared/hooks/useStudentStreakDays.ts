import { useEffect, useState } from "react"
import { getStudentProfile } from "@/shared/api"
import { isMockApiEnabled } from "@/mocks/config"
import { DEMO_STREAK_DAYS } from "@/mocks/data/profileDemo"
import {
  readCachedStreakDays,
  resolveStreakDays,
  writeCachedStreakDays,
} from "@/shared/utils/activityStats"

/** Серия дней для сайдбара и шапки (профиль / mock / календарь активности). */
export function useStudentStreakDays(enabled = true, userId: number | string | null = null) {
  const [streakDays, setStreakDays] = useState<number | null>(() => {
    if (isMockApiEnabled()) return DEMO_STREAK_DAYS
    return readCachedStreakDays(userId)
  })
  const [ready, setReady] = useState(() =>
    isMockApiEnabled() || readCachedStreakDays(userId) != null,
  )

  useEffect(() => {
    if (!enabled) {
      setStreakDays(null)
      setReady(true)
      return undefined
    }

    const cached = readCachedStreakDays(userId)
    if (cached != null) {
      setStreakDays(cached)
      setReady(true)
      return undefined
    }

    if (!isMockApiEnabled()) {
      setReady(false)
    }

    let cancelled = false
    getStudentProfile()
      .then((profile: { user_id?: number | string; id?: number | string; streak_days?: number; activity_by_date?: Record<string, number> }) => {
        if (cancelled) return
        const next = resolveStreakDays(profile)
        const cacheUserId = userId ?? profile?.user_id ?? profile?.id
        writeCachedStreakDays(cacheUserId ?? null, next)
        setStreakDays(next)
        setReady(true)
      })
      .catch(() => {
        if (cancelled) return
        if (isMockApiEnabled()) {
          setStreakDays(DEMO_STREAK_DAYS)
        }
        setReady(true)
      })

    return () => {
      cancelled = true
    }
  }, [enabled, userId])

  return { streakDays: streakDays ?? 0, ready }
}
