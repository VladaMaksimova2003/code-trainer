import axios from "axios"
import type { NormalizedUserRole, UserLike } from "@/shared/types/user"
import {
  buildReturnPath,
  saveAuthReturnPath,
} from "@/features/auth/utils/authReturnPath"

const ACCESS_TOKEN_KEY = "access_token"
const REFRESH_TOKEN_KEY = "refresh_token"
const REMEMBER_ME_KEY = "auth_remember_me"
const REMEMBERED_EMAIL_KEY = "auth_remembered_email"
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? "/api" : "http://localhost:8000")

/** Refresh access token this many ms before JWT exp. */
const REFRESH_BUFFER_MS = 5 * 60 * 1000

/** Fail fast instead of waiting on TCP/DB timeouts (~20–24s). */
const REFRESH_REQUEST_TIMEOUT_MS = 5_000

export const AUTH_SESSION_EXPIRED_EVENT = "auth:session-expired"

/** Previous keys — removed on read/write/clear so storage stays consistent. */
const LEGACY_ACCESS_TOKEN_KEY = "code_trainer_access_token"
const LEGACY_REFRESH_TOKEN_KEY = "code_trainer_refresh_token"

let refreshPromise: Promise<RefreshTokenResponse> | null = null
let proactiveTimer: ReturnType<typeof window.setTimeout> | null = null

interface JwtPayload {
  exp?: number
  role?: string
  roles?: string[]
  [key: string]: unknown
}

interface RefreshTokenResponse {
  access_token?: string
  refresh_token?: string
  [key: string]: unknown
}

interface RefreshAuthError {
  response?: { status?: number }
  message?: string
}

const _migrateLegacy = (newKey: string, legacyKey: string): string | null => {
  const next = window.localStorage.getItem(newKey)
  if (next) {
    window.localStorage.removeItem(legacyKey)
    return next
  }
  const legacy = window.localStorage.getItem(legacyKey)
  if (legacy) {
    window.localStorage.setItem(newKey, legacy)
    window.localStorage.removeItem(legacyKey)
    return legacy
  }
  return null
}

const _readToken = (key: string, legacyKey: string): string | null => {
  const fromLocal = window.localStorage.getItem(key)
  if (fromLocal) {
    return fromLocal
  }
  const fromSession = window.sessionStorage.getItem(key)
  if (fromSession) {
    return fromSession
  }
  return _migrateLegacy(key, legacyKey)
}

export const getRememberMe = (): boolean => window.localStorage.getItem(REMEMBER_ME_KEY) === "1"

export const getRememberedEmail = (): string =>
  window.localStorage.getItem(REMEMBERED_EMAIL_KEY) || ""

export const setRememberMePreference = (remember: boolean, email = ""): void => {
  if (remember) {
    window.localStorage.setItem(REMEMBER_ME_KEY, "1")
    if (email) {
      window.localStorage.setItem(REMEMBERED_EMAIL_KEY, email.trim())
    }
    return
  }
  window.localStorage.removeItem(REMEMBER_ME_KEY)
  window.localStorage.removeItem(REMEMBERED_EMAIL_KEY)
}

export const getAccessToken = (): string | null => _readToken(ACCESS_TOKEN_KEY, LEGACY_ACCESS_TOKEN_KEY)

export const getRefreshToken = (): string | null => _readToken(REFRESH_TOKEN_KEY, LEGACY_REFRESH_TOKEN_KEY)

export const decodeJwtPayload = (token: string | null | undefined): JwtPayload | null => {
  if (!token || typeof token !== "string") {
    return null
  }
  try {
    const parts = token.split(".")
    if (parts.length < 2) {
      return null
    }
    let base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/")
    const pad = base64.length % 4
    if (pad) {
      base64 += "=".repeat(4 - pad)
    }
    return JSON.parse(atob(base64)) as JwtPayload
  } catch {
    return null
  }
}

export const getAccessTokenExpiresAt = (token: string | null | undefined): number | null => {
  const payload = decodeJwtPayload(token)
  if (!payload?.exp) {
    return null
  }
  return payload.exp * 1000
}

export const isAccessTokenExpired = (token: string | null | undefined, bufferMs = 0): boolean => {
  const expiresAt = getAccessTokenExpiresAt(token)
  if (!expiresAt) {
    return true
  }
  return Date.now() >= expiresAt - bufferMs
}

export const notifySessionExpired = (): void => {
  if (typeof window !== "undefined") {
    saveAuthReturnPath(
      buildReturnPath(window.location.pathname, window.location.search),
    )
  }
  window.dispatchEvent(new CustomEvent(AUTH_SESSION_EXPIRED_EVENT))
}

const _clearTokenStorage = (): void => {
  ;[window.localStorage, window.sessionStorage].forEach((storage) => {
    storage.removeItem(ACCESS_TOKEN_KEY)
    storage.removeItem(REFRESH_TOKEN_KEY)
  })
  window.localStorage.removeItem(LEGACY_ACCESS_TOKEN_KEY)
  window.localStorage.removeItem(LEGACY_REFRESH_TOKEN_KEY)
}

export const setAuthTokens = ({
  accessToken,
  refreshToken,
  persist = true,
}: {
  accessToken?: string | null
  refreshToken?: string | null
  persist?: boolean
}): void => {
  _clearTokenStorage()
  const storage = persist ? window.localStorage : window.sessionStorage
  if (accessToken) {
    storage.setItem(ACCESS_TOKEN_KEY, accessToken)
  }
  if (refreshToken) {
    storage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  }
  scheduleProactiveTokenRefresh()
}

export const clearAuthTokens = (): void => {
  _clearTokenStorage()
  stopProactiveTokenRefresh()
}

const _isMockAuthToken = (): boolean => {
  const access = getAccessToken()
  if (String(import.meta.env.VITE_USE_MOCK_API || "").toLowerCase() !== "true") {
    return false
  }
  if (typeof access !== "string") return false
  return access.endsWith(".mock-signature") || access.startsWith("mock.")
}

const _tokenPersistPreference = (): boolean =>
  getRememberMe() || window.localStorage.getItem(REFRESH_TOKEN_KEY) != null

const _isRefreshAuthFailure = (error: unknown): boolean => {
  const err = error as RefreshAuthError
  const status = err?.response?.status
  if (status === 401 || status === 403) {
    return true
  }
  const message = String(err?.message || "")
  const code = (err as { code?: string }).code
  return (
    message === "Refresh token is missing" ||
    message === "Refresh response is incomplete" ||
    code === "ECONNABORTED"
  )
}

const _refreshAuthTokensInternal = async (): Promise<RefreshTokenResponse> => {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    throw new Error("Refresh token is missing")
  }

  if (_isMockAuthToken()) {
    return {
      access_token: getAccessToken() ?? undefined,
      refresh_token: refreshToken,
    }
  }

  const response = await axios.post(
    `${API_BASE_URL}/auth/refresh`,
    { refresh_token: refreshToken },
    { withCredentials: true, timeout: REFRESH_REQUEST_TIMEOUT_MS },
  )
  const nextAccess = response.data?.access_token
  const nextRefresh = response.data?.refresh_token

  if (!nextAccess || !nextRefresh) {
    throw new Error("Refresh response is incomplete")
  }

  setAuthTokens({
    accessToken: nextAccess,
    refreshToken: nextRefresh,
    persist: _tokenPersistPreference(),
  })

  return response.data as RefreshTokenResponse
}

/**
 * Single-flight refresh: parallel callers share one in-flight request.
 * Clears auth state and notifies listeners if refresh fails.
 */
export const refreshAuthTokens = async (): Promise<RefreshTokenResponse> => {
  if (refreshPromise) {
    return refreshPromise
  }

  refreshPromise = (async () => {
    try {
      return await _refreshAuthTokensInternal()
    } catch (error) {
      if (_isRefreshAuthFailure(error)) {
        clearAuthTokens()
        notifySessionExpired()
      }
      throw error
    } finally {
      refreshPromise = null
    }
  })()

  return refreshPromise
}

/**
 * Ensure a valid access token exists (refresh if missing or expiring soon).
 */
export const ensureValidAccessToken = async (): Promise<string> => {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    throw new Error("Refresh token is missing")
  }

  if (_isMockAuthToken()) {
    return getAccessToken() || refreshToken
  }

  const accessToken = getAccessToken()
  if (accessToken && !isAccessTokenExpired(accessToken, REFRESH_BUFFER_MS)) {
    return accessToken
  }

  await refreshAuthTokens()
  const nextAccess = getAccessToken()
  if (!nextAccess) {
    throw new Error("Access token is missing after refresh")
  }
  return nextAccess
}

export const scheduleProactiveTokenRefresh = (): void => {
  stopProactiveTokenRefresh()

  const accessToken = getAccessToken()
  const refreshToken = getRefreshToken()
  if (!accessToken || !refreshToken) {
    return
  }

  const expiresAt = getAccessTokenExpiresAt(accessToken)
  if (!expiresAt) {
    return
  }

  const refreshAt = expiresAt - REFRESH_BUFFER_MS
  const delay = Math.max(refreshAt - Date.now(), 0)

  proactiveTimer = window.setTimeout(async () => {
    proactiveTimer = null
    try {
      await refreshAuthTokens()
    } catch {
      // refreshAuthTokens already cleared tokens and emitted the event
    }
  }, delay)
}

export const stopProactiveTokenRefresh = (): void => {
  if (proactiveTimer != null) {
    window.clearTimeout(proactiveTimer)
    proactiveTimer = null
  }
}

/**
 * Single source of truth for role strings from JWT / API / enum repr.
 */
export const normalizeUserRole = (raw: unknown): NormalizedUserRole => {
  if (raw == null || raw === "") {
    return "STUDENT"
  }
  const s = String(raw).trim()
  if (s === "UserType.ADMIN") {
    return "ADMIN"
  }
  if (s === "UserType.TEACHER") {
    return "TEACHER"
  }
  if (s === "UserType.STUDENT") {
    return "STUDENT"
  }
  const lower = s.toLowerCase()
  if (lower === "admin" || lower === "administrator") {
    return "ADMIN"
  }
  if (lower === "teacher") {
    return "TEACHER"
  }
  if (lower === "student") {
    return "STUDENT"
  }
  const u = s.toUpperCase()
  if (u === "ADMIN" || u === "TEACHER" || u === "STUDENT") {
    return u
  }
  if (u.includes("USERTYPE.ADMIN") || u.endsWith(".ADMIN")) {
    return "ADMIN"
  }
  if (u.includes("USERTYPE.TEACHER") || u.endsWith(".TEACHER")) {
    return "TEACHER"
  }
  return "STUDENT"
}

/** Roles from /auth/me (preferred) or legacy single role field. */
export const getUserRoles = (user: UserLike | null | undefined): NormalizedUserRole[] => {
  if (!user) return []
  if (Array.isArray(user.roles) && user.roles.length > 0) {
    return user.roles.map((r) => normalizeUserRole(r))
  }
  if (user.role != null && user.role !== "") {
    return [normalizeUserRole(user.role)]
  }
  return []
}

export const userHasRole = (user: UserLike | null | undefined, roleKey: unknown): boolean => {
  const key = normalizeUserRole(roleKey)
  return getUserRoles(user).includes(key)
}

export const userHasAnyRole = (user: UserLike | null | undefined, roleKeys: unknown[]): boolean => {
  const allowed = new Set(roleKeys.map((r) => normalizeUserRole(r)))
  return getUserRoles(user).some((r) => allowed.has(r))
}

/** Teacher cabinet and teacher APIs (TEACHER or ADMIN). */
export const canAccessTeacherWorkspace = (user: UserLike | null | undefined): boolean =>
  userHasAnyRole(user, ["TEACHER", "ADMIN"])

/** Admin panel. */
export const canAccessAdminWorkspace = (user: UserLike | null | undefined): boolean => userHasRole(user, "ADMIN")

/** Student profile, groups, task list as learner. */
export const canAccessStudentLearning = (user: UserLike | null | undefined): boolean =>
  userHasAnyRole(user, ["STUDENT", "TEACHER", "ADMIN"])

export const getRoleFromAccessToken = (accessToken: string | null | undefined): NormalizedUserRole | null => {
  const payload = decodeJwtPayload(accessToken)
  if (!payload) return null
  if (Array.isArray(payload.roles) && payload.roles.length > 0) {
    return normalizeUserRole(payload.roles[0])
  }
  const raw = payload?.role
  if (raw == null || raw === "") {
    return null
  }
  return normalizeUserRole(raw)
}
