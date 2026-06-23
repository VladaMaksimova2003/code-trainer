const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

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
