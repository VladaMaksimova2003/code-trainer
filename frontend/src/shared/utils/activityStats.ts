import type { UserLike } from "@/shared/types/user"

const STREAK_CACHE_KEY = "code-trainer-streak-cache"

interface StreakCachePayload {
  userId?: string
  streakDays?: number
}

export function readCachedStreakDays(userId: number | string | null | undefined): number | null {
  if (userId == null) return null
  try {
    const raw = window.sessionStorage.getItem(STREAK_CACHE_KEY)
    if (!raw) return null
    const data = JSON.parse(raw) as StreakCachePayload
    if (String(data.userId) !== String(userId)) return null
    return typeof data.streakDays === "number" ? data.streakDays : null
  } catch {
    return null
  }
}

export function writeCachedStreakDays(userId: number | string | null | undefined, streakDays: number): void {
  if (userId == null || typeof streakDays !== "number") return
  try {
    window.sessionStorage.setItem(
      STREAK_CACHE_KEY,
      JSON.stringify({ userId: String(userId), streakDays }),
    )
  } catch {
    /* quota */
  }
}

export function clearCachedStreakDays(): void {
  try {
    window.sessionStorage.removeItem(STREAK_CACHE_KEY)
  } catch {
    /* ignore */
  }
}

export function formatDateKey(date: Date | string | number): string {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d.toISOString().slice(0, 10)
}

export function utcTodayStart(): Date {
  const now = new Date()
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
}

export function sumActivityInRange(byDate: Record<string, number> = {}, daysAgoStart: number, daysCount: number): number {
  let sum = 0
  const end = utcTodayStart()
  end.setUTCDate(end.getUTCDate() - daysAgoStart)
  const dayMs = 24 * 60 * 60 * 1000
  for (let i = 0; i < daysCount; i += 1) {
    const d = new Date(end.getTime() - i * dayMs)
    sum += Number(byDate[formatUtcDateKey(d)] || 0)
  }
  return sum
}

/** Ключ даты в UTC — как в activity_by_date с бэкенда. */
export function formatUtcDateKey(date: Date | string | number): string {
  const d = new Date(date)
  const y = d.getUTCFullYear()
  const m = String(d.getUTCMonth() + 1).padStart(2, "0")
  const day = String(d.getUTCDate()).padStart(2, "0")
  return `${y}-${m}-${day}`
}

export function computeStreak(byDate: Record<string, number> = {}): number {
  const now = new Date()
  let cursor = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
  const dayMs = 24 * 60 * 60 * 1000

  if (!Number(byDate[formatUtcDateKey(cursor)] || 0)) {
    cursor = new Date(cursor.getTime() - dayMs)
  }

  let streak = 0
  while (Number(byDate[formatUtcDateKey(cursor)] || 0) > 0) {
    streak += 1
    cursor = new Date(cursor.getTime() - dayMs)
  }
  return streak
}

interface AnalyticsLike {
  streak_days?: number | null
  overview?: { streak_days?: number | null }
}

/** Единый расчёт серии для сайдбара и профиля. */
export function resolveStreakDays(profile: UserLike | null | undefined, analytics: AnalyticsLike | null = null): number {
  if (typeof profile?.streak_days === "number") {
    return profile.streak_days
  }
  const fromAnalytics = analytics?.streak_days ?? analytics?.overview?.streak_days
  if (typeof fromAnalytics === "number") {
    return fromAnalytics
  }
  return computeStreak(profile?.activity_by_date ?? {})
}

export function computePeriodDeltaPercent(byDate: Record<string, number> = {}, periodDays = 30): number {
  const current = sumActivityInRange(byDate, 0, periodDays)
  const previous = sumActivityInRange(byDate, periodDays, periodDays)
  if (previous === 0) return current > 0 ? 100 : 0
  return Math.round(((current - previous) / previous) * 100)
}

export function formatDeltaBadge(
  value: number,
  { suffix = "", signed = true }: { suffix?: string; signed?: boolean } = {},
): string | null {
  if (!value) return null
  const prefix = signed && value > 0 ? "+" : ""
  return `${prefix}${value}${suffix}`
}

export interface DailyBarItem {
  key: string
  value: number
  height: number
  peak: boolean
  low: boolean
}

export function buildDailyBars(byDate: Record<string, number> = {}, days = 12): DailyBarItem[] {
  const items: Array<{ key: string; value: number }> = []
  const today = utcTodayStart()
  const dayMs = 24 * 60 * 60 * 1000
  for (let i = days - 1; i >= 0; i -= 1) {
    const d = new Date(today.getTime() - i * dayMs)
    const key = formatUtcDateKey(d)
    items.push({ key, value: Number(byDate[key] || 0) })
  }
  const max = Math.max(...items.map((x) => x.value), 1)
  return items.map((item) => ({
    ...item,
    height: Math.round((item.value / max) * 100),
    peak: item.value >= max * 0.85 && item.value > 0,
    low: item.value > 0 && item.value < max * 0.25,
  }))
}
