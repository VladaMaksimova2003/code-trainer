/** Включить mock API: в .env.local задайте VITE_USE_MOCK_API=true */
export function isMockApiEnabled() {
  return String(import.meta.env.VITE_USE_MOCK_API || "").toLowerCase() === "true"
}

export const MOCK_DELAY_MS = Number(import.meta.env.VITE_MOCK_DELAY_MS || 450)
