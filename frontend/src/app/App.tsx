import { useEffect, useRef, useState } from "react"
import { BrowserRouter } from "react-router-dom"
import { ToastStack } from "@/shared/ui/toast"
import {
  AUTH_SESSION_EXPIRED_EVENT,
  clearAuthTokens,
  getAccessToken,
  getRefreshToken,
  isAccessTokenExpired,
  refreshAuthTokens,
  scheduleProactiveTokenRefresh,
  stopProactiveTokenRefresh,
} from "@/shared/api/auth"
import { getMe, getStudentProfile } from "@/shared/api"
import {
  clearCachedStreakDays,
  resolveStreakDays,
  writeCachedStreakDays,
} from "@/shared/utils/activityStats"
import { logoutSession } from "@/features/settings/api/settingsApi"
import { clearUserScopedQueries } from "@/shared/providers/queryClient"
import { AppRouter } from "./router"

async function prefetchStreakCache(user) {
  if (!user?.id) return
  try {
    const profile = await getStudentProfile()
    writeCachedStreakDays(user.id, resolveStreakDays(profile))
  } catch {
    /* sidebar falls back to placeholder until hook fetch completes */
  }
}

function App() {
  const [currentUser, setCurrentUser] = useState(null)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)
  const activeUserIdRef = useRef<string | null>(null)

  const applyCurrentUser = (nextUser: { id?: number | string } | null) => {
    const nextId = nextUser?.id != null ? String(nextUser.id) : null
    if (activeUserIdRef.current !== nextId) {
      clearUserScopedQueries()
      activeUserIdRef.current = nextId
    }
    setCurrentUser(nextUser)
  }

  const clearSessionState = () => {
    if (activeUserIdRef.current !== null) {
      clearUserScopedQueries()
      activeUserIdRef.current = null
    }
    clearCachedStreakDays()
    setCurrentUser(null)
    stopProactiveTokenRefresh()
  }

  const loadCurrentUser = async ({ bootstrap = false } = {}) => {
    if (bootstrap) setIsCheckingAuth(true)

    const accessToken = getAccessToken()
    const refreshToken = getRefreshToken()

    if (!accessToken && !refreshToken) {
      clearSessionState()
      if (bootstrap) setIsCheckingAuth(false)
      return
    }

    if (!refreshToken) {
      clearAuthTokens()
      clearSessionState()
      if (bootstrap) setIsCheckingAuth(false)
      return
    }

    const finishBootstrap = () => {
      if (bootstrap) setIsCheckingAuth(false)
    }

    try {
      if (accessToken && !isAccessTokenExpired(accessToken, 0)) {
        const me = await getMe()
        applyCurrentUser(me)
        scheduleProactiveTokenRefresh()
        void prefetchStreakCache(me)
        return
      }

      await refreshAuthTokens()
      const me = await getMe()
      applyCurrentUser(me)
      scheduleProactiveTokenRefresh()
      void prefetchStreakCache(me)
    } catch (err) {
      if (import.meta.env.DEV) {
        console.warn("[auth] Не удалось проверить сессию:", err?.message || err)
      }
      clearAuthTokens()
      clearSessionState()
    } finally {
      finishBootstrap()
    }
  }

  useEffect(() => {
    loadCurrentUser({ bootstrap: true })
  }, [])

  useEffect(() => {
    if (currentUser || isCheckingAuth) return undefined
    const refreshToken = getRefreshToken()
    if (!refreshToken) return undefined

    let cancelled = false
    ;(async () => {
      setIsCheckingAuth(true)
      try {
        const accessToken = getAccessToken()
        if (!accessToken || isAccessTokenExpired(accessToken, 0)) {
          await refreshAuthTokens()
        }
        if (cancelled) return
        const me = await getMe()
        if (cancelled) return
        void prefetchStreakCache(me)
        if (cancelled) return
        applyCurrentUser(me)
        scheduleProactiveTokenRefresh()
      } catch (err) {
        if (!cancelled) {
          if (import.meta.env.DEV) {
            console.warn("[auth] Не удалось восстановить сессию:", err?.message || err)
          }
          clearAuthTokens()
          clearSessionState()
        }
      } finally {
        if (!cancelled) setIsCheckingAuth(false)
      }
    })()

    return () => {
      cancelled = true
    }
  }, [currentUser, isCheckingAuth])

  useEffect(() => {
    const onSessionExpired = () => {
      clearSessionState()
    }
    window.addEventListener(AUTH_SESSION_EXPIRED_EVENT, onSessionExpired)
    return () => window.removeEventListener(AUTH_SESSION_EXPIRED_EVENT, onSessionExpired)
  }, [])

  useEffect(() => {
    if (!currentUser) return undefined

    const refreshOnFocus = () => {
      if (document.visibilityState !== "visible") return
      const accessToken = getAccessToken()
      if (accessToken && !isAccessTokenExpired(accessToken, 60_000)) {
        return
      }
      refreshAuthTokens().catch(() => {
        // refreshAuthTokens handles auth failures
      })
    }

    window.addEventListener("focus", refreshOnFocus)
    document.addEventListener("visibilitychange", refreshOnFocus)
    return () => {
      window.removeEventListener("focus", refreshOnFocus)
      document.removeEventListener("visibilitychange", refreshOnFocus)
    }
  }, [currentUser])

  const handleSignOut = async () => {
    try {
      await logoutSession()
    } catch {
      // clear local session even if server revoke fails
    }
    clearAuthTokens()
    clearSessionState()
  }

  const handleAccountUpdated = (account) => {
    setCurrentUser((prev) =>
      prev
        ? { ...prev, name: account.name, email: account.email, about: account.about ?? null }
        : prev
    )
  }

  return (
    <BrowserRouter>
      <AppRouter
        currentUser={currentUser}
        isCheckingAuth={isCheckingAuth}
        onSignOut={handleSignOut}
        onAccountUpdated={handleAccountUpdated}
        onAuthSuccess={() => loadCurrentUser()}
      />
      <ToastStack />
    </BrowserRouter>
  )
}

export default App
