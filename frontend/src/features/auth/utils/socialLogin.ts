import { saveAuthReturnPath, buildReturnPath } from "@/features/auth/utils/authReturnPath"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? "/api" : "http://localhost:8000")

const SUPPORTED_PROVIDERS = new Set(["vk", "google", "yandex"])

/** Redirect browser to backend OAuth start endpoint. */
export function redirectToOAuth(provider: string): void {
  saveAuthReturnPath(buildReturnPath(window.location.pathname, window.location.search))
  const normalized = String(provider || "").trim().toLowerCase()
  if (!SUPPORTED_PROVIDERS.has(normalized)) {
    throw new Error(`Unsupported OAuth provider: ${provider}`)
  }
  const base = API_BASE_URL.replace(/\/$/, "")
  window.location.href = `${base}/auth/oauth/${normalized}/start`
}
