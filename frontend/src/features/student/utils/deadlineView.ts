import type { CSSProperties } from "react"

/** Short label + urgency color for assignment set deadlines. */
export function formatSetDeadline(value: string | null | undefined): string | null {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null
  const label = date.toLocaleString("ru-RU", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  })
  return `до ${label}`
}

export function deadlineUrgencyStyle(value: string | null | undefined): CSSProperties | null {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null

  const msLeft = date.getTime() - Date.now()
  if (msLeft < 0) {
    return { color: "var(--danger)", fontWeight: 600 }
  }

  const daysLeft = msLeft / (24 * 60 * 60 * 1000)
  if (daysLeft <= 1) {
    return { color: "var(--warning)", fontWeight: 600 }
  }
  if (daysLeft <= 3) {
    return { color: "#ff9f43", fontWeight: 600 }
  }
  if (daysLeft <= 7) {
    return { color: "#ffb86b" }
  }
  return { color: "var(--text-2)" }
}
