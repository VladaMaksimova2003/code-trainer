import axios, { type InternalAxiosRequestConfig } from "axios"
import {
  getAccessToken,
  isAccessTokenExpired,
  refreshAuthTokens,
} from "@/shared/api/auth"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? "/api" : "http://localhost:8000")

interface RetryableAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 30_000,
})

/** Attach Bearer only when access token is still valid — never block on refresh here. */
export const attachAccessTokenIfValid = (config: InternalAxiosRequestConfig): void => {
  const token = getAccessToken()
  if (token && !isAccessTokenExpired(token, 0)) {
    config.headers.Authorization = `Bearer ${token}`
  }
}

api.interceptors.request.use((config) => {
  const url = config.url || ""
  if (url.includes("/auth/login") || url.includes("/auth/refresh")) {
    return config
  }
  attachAccessTokenIfValid(config)
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as RetryableAxiosRequestConfig | undefined
    const status = error?.response?.status
    const url = originalRequest?.url || ""

    if (
      originalRequest &&
      !originalRequest._retry &&
      status === 401 &&
      !url.includes("/auth/login") &&
      !url.includes("/auth/refresh")
    ) {
      originalRequest._retry = true
      try {
        await refreshAuthTokens()
        const token = getAccessToken()
        if (token) {
          originalRequest.headers = originalRequest.headers || {}
          originalRequest.headers.Authorization = `Bearer ${token}`
        }
        return api(originalRequest)
      } catch {
        // refreshAuthTokens clears tokens and emits auth:session-expired
      }
    }

    return Promise.reject(error)
  },
)
