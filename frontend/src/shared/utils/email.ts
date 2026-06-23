const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

/** Служебный адрес при входе через VK/Google/Yandex без email в ответе провайдера. */
export const OAUTH_PLACEHOLDER_EMAIL_DOMAIN = "@oauth.code-trainer.local"

export function isOAuthPlaceholderEmail(value: unknown): boolean {
  return String(value || "")
    .trim()
    .toLowerCase()
    .endsWith(OAUTH_PLACEHOLDER_EMAIL_DOMAIN)
}

/** Email для отображения в UI; служебные OAuth-адреса скрываются. */
export function displayContactEmail(value: unknown): string {
  const trimmed = String(value || "").trim()
  if (!trimmed || isOAuthPlaceholderEmail(trimmed)) return ""
  return trimmed
}

export function isValidEmail(value: unknown): boolean {
  const trimmed = String(value || "").trim()
  if (!trimmed) return false
  return EMAIL_RE.test(trimmed)
}

export function emailValidationMessage(value: unknown): string | null {
  const trimmed = String(value || "").trim()
  if (!trimmed) return "Укажите email"
  if (!isValidEmail(trimmed)) return "Укажите корректный email"
  return null
}
