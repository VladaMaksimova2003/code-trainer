import { useCallback, useEffect, useState } from "react"
import { getStudentProfile } from "@/shared/api"
import { getStudentAnalytics } from "@/features/analytics/api/analyticsApi"
import type { UserLike } from "@/shared/types/user"

interface UseProfileOptions {
  loadAnalytics?: boolean
  enabled?: boolean
}

interface ApiErrorShape {
  response?: { data?: { detail?: string } }
  message?: string
}

function getProfileErrorMessage(err: unknown): string {
  const error = err as ApiErrorShape
  return error?.response?.data?.detail || error?.message || "Не удалось загрузить профиль"
}

export function useProfile({ loadAnalytics = false, enabled = true }: UseProfileOptions = {}) {
  const [profile, setProfile] = useState<UserLike | null>(null)
  const [analytics, setAnalytics] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [analyticsLoading, setAnalyticsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadProfile = useCallback(async () => {
    if (!enabled) {
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await getStudentProfile()
      setProfile(data as UserLike)
    } catch (err) {
      setError(getProfileErrorMessage(err))
      setProfile(null)
    } finally {
      setLoading(false)
    }
  }, [enabled])

  const reloadAnalytics = useCallback(async () => {
    if (!enabled) return
    setAnalyticsLoading(true)
    try {
      const data = await getStudentAnalytics()
      setAnalytics(data as Record<string, unknown>)
    } catch {
      setAnalytics(null)
    } finally {
      setAnalyticsLoading(false)
    }
  }, [enabled])

  useEffect(() => {
    loadProfile()
  }, [loadProfile])

  useEffect(() => {
    if (loadAnalytics) reloadAnalytics()
  }, [loadAnalytics, reloadAnalytics])

  return {
    profile,
    analytics,
    loading,
    analyticsLoading,
    error,
    reloadProfile: loadProfile,
    reloadAnalytics,
  }
}
