import { api } from "@/shared/api"
import { isMockApiEnabled } from "@/mocks/config"

const USE_MOCK = isMockApiEnabled()
const delay = (ms = 250) => new Promise((r: unknown) => setTimeout(r, ms))

const INBOX_KINDS = new Set(["comment", "ticket_reply"])

type NotificationKind = "comment" | "ticket_reply" | string

interface MockNotificationRow {
  id: number
  kind: NotificationKind
  title: string
  body: string
  is_read: boolean
  ticket_id: number | null
  task_id?: number
  submission_id?: number
  created_at: string
  read?: boolean
  meta?: NotificationMeta
}

interface NotificationMeta {
  ticket_id?: number | null
  task_id?: number | null
  submission_id?: number | null
}

export interface NormalizedNotification {
  id: number
  kind: NotificationKind
  title: string
  body: string
  read: boolean
  created_at: string
  meta: NotificationMeta
  task_id?: number
  ticket_id?: number | null
}

let _mockNotifications: MockNotificationRow[] = [
  {
    id: 101,
    kind: "ticket_reply",
    title: "Ответ в обращении #12",
    body: "Администратор: Проверили логи — перезапустите проверку решения, должно заработать.",
    is_read: false,
    ticket_id: 12,
    created_at: "2026-06-04T09:05:00Z",
  },
  {
    id: 100,
    kind: "comment",
    title: "Иванов · Сумма чисел",
    body: "Проверь граничный случай n=0 — цикл не обрабатывает пустой ввод.",
    is_read: false,
    ticket_id: null,
    task_id: 12,
    submission_id: 42,
    created_at: "2026-06-04T08:40:00Z",
  },
]

function filterInbox(items: MockNotificationRow[]): MockNotificationRow[] {
  return items.filter((n: unknown) => INBOX_KINDS.has(n.kind))
}

function normalizeNotification(row: MockNotificationRow): NormalizedNotification {
  return {
    id: row.id,
    kind: row.kind,
    title: row.title,
    body: row.body,
    read: row.is_read ?? row.read ?? false,
    created_at: row.created_at,
    meta: row.meta ?? {
      ticket_id: row.ticket_id,
      task_id: row.task_id,
      submission_id: row.submission_id,
    },
    task_id: row.task_id,
    ticket_id: row.ticket_id,
  }
}

export async function listNotifications(unreadOnly = false): Promise<NormalizedNotification[]> {
  if (USE_MOCK) {
    await delay()
    const items = filterInbox(_mockNotifications).map(normalizeNotification)
    return unreadOnly ? items.filter((n: unknown) => !n.read) : items
  }
  const { data } = await api.get("/notifications", { params: { unread_only: unreadOnly } })
  const items = (data as { items?: MockNotificationRow[] }).items ?? []
  return filterInbox(items).map(normalizeNotification)
}

export async function getUnreadCount(): Promise<{ count: number }> {
  if (USE_MOCK) {
    await delay(120)
    return { count: filterInbox(_mockNotifications).filter((n: unknown) => !n.is_read).length }
  }
  const { data } = await api.get("/notifications/unread-count")
  return { count: (data as { unread_count?: number }).unread_count ?? 0 }
}

export async function markRead(id: number): Promise<{ ok: boolean }> {
  if (USE_MOCK) {
    await delay(120)
    _mockNotifications = _mockNotifications.map((n: unknown) =>
      n.id === id ? { ...n, is_read: true } : n,
    )
    return { ok: true }
  }
  await api.patch(`/notifications/${id}/read`)
  return { ok: true }
}

export async function markAllRead(): Promise<{ ok: boolean }> {
  if (USE_MOCK) {
    await delay(150)
    _mockNotifications = _mockNotifications.map((n: unknown) => ({ ...n, is_read: true }))
    return { ok: true }
  }
  await api.post("/notifications/read-all")
  return { ok: true }
}

export function notificationHref(n: NormalizedNotification): string {
  switch (n.kind) {
    case "comment": {
      const taskId = n.meta?.task_id ?? n.task_id
      const submissionId = n.meta?.submission_id ?? n.submission_id
      const params = new URLSearchParams({ tab: "comments" })
      if (submissionId != null) params.set("submission", String(submissionId))
      return `/tasks/${taskId}?${params.toString()}`
    }
    case "ticket_reply":
      return `/support/tickets/${n.meta?.ticket_id ?? n.ticket_id}`
    default:
      return "/support"
  }
}
