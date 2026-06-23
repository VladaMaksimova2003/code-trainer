import { api } from "@/shared/api/client"

export const OAUTH_PROVIDER_IDS = ["vk", "google", "yandex"] as const
export type OAuthProviderId = (typeof OAUTH_PROVIDER_IDS)[number]

const PROVIDERS_CACHE_MS = 60_000
let cachedProviders: string[] | null = null
let cacheExpiresAt = 0

export async function fetchConfiguredOAuthProviders(): Promise<string[]> {
  const now = Date.now()
  if (cachedProviders !== null && now < cacheExpiresAt) {
    return cachedProviders
  }
  try {
    const res = await api.get<{ providers: string[] }>("/auth/oauth/providers")
    const configured = Array.isArray(res.data?.providers) ? res.data.providers : []
    cachedProviders = configured.length > 0 ? configured : [...OAUTH_PROVIDER_IDS]
  } catch {
    // Show buttons even when /providers is unavailable (e.g. local dev without API).
    cachedProviders = [...OAUTH_PROVIDER_IDS]
  }
  cacheExpiresAt = now + PROVIDERS_CACHE_MS
  return cachedProviders
}

export function invalidateOAuthProvidersCache(): void {
  cachedProviders = null
  cacheExpiresAt = 0
}
