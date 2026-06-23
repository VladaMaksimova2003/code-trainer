/** Short badge label from a title (course name, etc.). */
export function deriveLabelGlyph(title: string, maxLen = 2): string {
  const text = String(title || "").trim()
  if (!text) return "?"

  const compact = text.replace(/\s+/g, "")
  if (compact.length <= maxLen + 1 && /[+/#]/.test(compact)) {
    return compact.slice(0, Math.min(compact.length, maxLen + 1))
  }

  const letters = [...compact.replace(/[^\p{L}\p{N}+#]/gu, "")]
  if (!letters.length) return "?"
  return letters.slice(0, maxLen).join("").toUpperCase()
}
