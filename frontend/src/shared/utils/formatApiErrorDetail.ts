export function formatApiErrorDetail(detail: unknown): string | null {
  if (typeof detail === "string" && detail.trim()) return detail
  if (Array.isArray(detail)) {
    const text = detail
      .map((item: unknown) => {
        if (typeof item === "string") return item
        if (item && typeof item === "object") {
          const row = item as { msg?: string; message?: string }
          return row.msg || row.message || JSON.stringify(item)
        }
        return String(item)
      })
      .join(". ")
    if (text.trim()) return text
  }
  if (detail && typeof detail === "object") {
    const row = detail as { msg?: string; message?: string }
    if (row.msg || row.message) return row.msg || row.message || null
  }
  return null
}
