/** Copy text to clipboard; works on HTTP sites where navigator.clipboard is blocked. */
export async function copyTextToClipboard(text: string): Promise<boolean> {
  const value = String(text ?? "")
  if (!value) return false

  if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value)
      return true
    } catch {
      // fall through to execCommand
    }
  }

  if (typeof document === "undefined") return false

  try {
    const textarea = document.createElement("textarea")
    textarea.value = value
    textarea.setAttribute("readonly", "")
    textarea.style.position = "fixed"
    textarea.style.top = "0"
    textarea.style.left = "-9999px"
    document.body.appendChild(textarea)
    textarea.focus()
    textarea.select()
    const ok = document.execCommand("copy")
    document.body.removeChild(textarea)
    return ok
  } catch {
    return false
  }
}
