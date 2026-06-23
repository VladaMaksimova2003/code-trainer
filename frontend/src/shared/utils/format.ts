export function formatRelativeActivity(value: unknown): string {
  if (!value) return "—"
  const date = new Date(String(value))
  if (Number.isNaN(date.getTime())) return "—"
  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const startOfDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const dayDiff = Math.round((startOfToday.getTime() - startOfDate.getTime()) / 86400000)
  if (dayDiff === 0) return "сегодня"
  if (dayDiff === 1) return "вчера"
  if (dayDiff < 7) return `${dayDiff} дней назад`
  return date.toLocaleDateString("ru-RU", { day: "numeric", month: "short" })
}

export function formatShortDateTime(value: unknown): string {
  if (!value) return "—"
  const date = new Date(String(value))
  if (Number.isNaN(date.getTime())) return "—"
  return date.toLocaleString("ru-RU", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  })
}

/** Time on first line (19:30), date on second (16.06.2026) — teacher cabinet stamps. */
export function formatStackedDateTime(value: unknown): { time: string; date: string } | null {
  if (!value) return null
  const date = new Date(String(value))
  if (Number.isNaN(date.getTime())) return null
  return {
    time: date.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }),
    date: date.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }),
  }
}

export function shortDisplayName(name: unknown): string {
  const parts = String(name || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean)
  if (parts.length < 2) return parts[0] || "—"
  return `${parts[0]} ${parts[1][0]}.`
}

export function formatRegistrationDate(value: unknown): string {
  if (!value) return "—"
  const date = new Date(String(value))
  if (Number.isNaN(date.getTime())) return "—"
  return date.toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  })
}

export function formatLastLogin(value: unknown): string {
  if (!value) return "—"
  const date = new Date(String(value))
  if (Number.isNaN(date.getTime())) return "—"
  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const startOfDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const dayDiff = Math.round((startOfToday.getTime() - startOfDate.getTime()) / 86400000)
  const time = date.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })
  if (dayDiff === 0) return `сегодня, ${time}`
  if (dayDiff === 1) return `вчера, ${time}`
  return formatShortDateTime(value)
}

export function formatDateTime(value: unknown): string {
  if (!value) return "—"
  const date = new Date(String(value))
  if (Number.isNaN(date.getTime())) return "—"
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export function formatNumber(value: unknown): string {
  if (value == null || Number.isNaN(Number(value))) return "0"
  return new Intl.NumberFormat("ru-RU").format(Number(value))
}

export function workflowStatusLabel(status: unknown): string {
  const map: Record<string, string> = {
    active: "Активно",
    under_review: "На проверке",
    archived: "В архиве",
  }
  return map[String(status || "").toLowerCase()] || String(status || "—")
}

export function requestStatusLabel(status: unknown): string {
  const map: Record<string, string> = {
    pending: "Ожидает",
    approved: "Одобрена",
    rejected: "Отклонена",
  }
  return map[String(status || "").toLowerCase()] || String(status || "—")
}

export { getLanguageLabel as languageLabel } from "@/shared/config/languages"

export function submissionStatusLabel(status: unknown): string {
  const map: Record<string, string> = {
    done: "Проверено",
    queued: "В очереди",
    running: "Выполняется",
    failed: "Ошибка",
  }
  return map[String(status || "").toLowerCase()] || "Неизвестно"
}

export function submissionResultLabel(success: boolean | null | undefined): string {
  if (success === true) return "Успешно"
  if (success === false) return "Не пройдено"
  return "В обработке"
}

export function submissionResultClass(success: boolean | null | undefined): string {
  if (success === true) return "text-emerald-400 bg-emerald-950/40 border-emerald-800"
  if (success === false) return "text-red-400 bg-red-950/40 border-red-800"
  return "text-amber-300 bg-amber-950/40 border-amber-800"
}

export function roleLabel(role: unknown): string {
  const map: Record<string, string> = {
    student: "Студент",
    teacher: "Преподаватель",
    admin: "Администратор",
    STUDENT: "Студент",
    TEACHER: "Преподаватель",
    ADMIN: "Администратор",
  }
  return map[String(role)] || String(role ?? "")
}
