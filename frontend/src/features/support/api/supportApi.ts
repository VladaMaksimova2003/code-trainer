import { api } from "@/shared/api"
import { isMockApiEnabled } from "@/mocks/config"

type SupportContext = "task" | "general" | string
type TicketStatus = keyof typeof STATUS_LABELS | string

interface SupportTemplateChip {
  category: string
  label: string
  draft: string
}

interface SupportTicket {
  id: number
  subject: string
  category: string
  status: TicketStatus
  target: string
  task_id: number | null
  created_at: string
  updated_at: string
}

interface SupportMessageRow {
  id: number
  author: string
  author_name?: string
  body: string
  created_at: string
  message_type?: string
  author_id?: number | string
}

interface NormalizedSupportMessage {
  id: number
  author: string
  author_name?: string
  body: string
  created_at: string
}

interface CreateTicketPayload {
  subject?: string
  category: string
  body: string
  task_id?: number | null
  [key: string]: unknown
}

const USE_MOCK = isMockApiEnabled()
const delay = (ms = 320) => new Promise((r: unknown) => setTimeout(r, ms))

export const SUPPORT_CATEGORIES = [
  { id: "task_content", label: "Ошибка в условии" },
  { id: "autograder", label: "Автопроверка" },
  { id: "technical", label: "Техническая" },
  { id: "account", label: "Аккаунт" },
  { id: "other", label: "Другое" },
]

export const STATUS_LABELS = {
  open: "Открыто",
  in_progress: "В работе",
  resolved: "Решено",
  closed: "Закрыто",
}

let _mockTickets: SupportTicket[] = [
  {
    id: 12,
    subject: "Редактор не сохраняет код",
    category: "technical",
    status: "in_progress",
    target: "admin",
    task_id: null,
    created_at: "2026-06-04T07:00:00Z",
    updated_at: "2026-06-04T09:00:00Z",
  },
  {
    id: 9,
    subject: "Не могу войти",
    category: "account",
    status: "resolved",
    target: "admin",
    task_id: null,
    created_at: "2026-06-02T11:00:00Z",
    updated_at: "2026-06-03T08:00:00Z",
  },
  {
    id: 7,
    subject: "Ошибка в задании: Сумма чисел",
    category: "task_content",
    status: "open",
    target: "teacher",
    task_id: 12,
    created_at: "2026-06-01T10:00:00Z",
    updated_at: "2026-06-01T10:00:00Z",
  },
]

let _mockMessages: Record<number, SupportMessageRow[]> = {
  12: [
    {
      id: 1,
      author: "system",
      body: "Статус изменён: Открыто → В работе",
      created_at: "2026-06-04T08:30:00Z",
    },
    {
      id: 2,
      author: "you",
      author_name: "Вы",
      body: "Редактор не сохраняет код после обновления страницы.",
      created_at: "2026-06-04T07:00:00Z",
    },
    {
      id: 3,
      author: "support",
      author_name: "Поддержка",
      body: "Уточните, пожалуйста, браузер и ОС.",
      created_at: "2026-06-04T09:00:00Z",
    },
  ],
}

const TEMPLATES = {
  task: [
    { category: "task_content", label: "Ошибка в условии", draft: "В условии задачи неточность: " },
    { category: "task_content", label: "Неверный тест", draft: "Тест №… кажется некорректным: " },
    { category: "autograder", label: "Автопроверка", draft: "Автопроверка ведёт себя странно: " },
    { category: "other", label: "Другое", draft: "" },
  ],
  general: [
    { category: "technical", label: "Техническая проблема", draft: "Опишите проблему: " },
    { category: "account", label: "Аккаунт / доступ", draft: "Проблема с доступом: " },
    { category: "other", label: "Другое", draft: "" },
  ],
}

function flattenTemplates(payload: unknown): SupportTemplateChip[] {
  if (Array.isArray(payload)) return payload as SupportTemplateChip[]
  const categories = (payload as { categories?: Array<{ id: string; templates?: SupportTemplateChip[] }> } | null)?.categories ?? []
  const chips: SupportTemplateChip[] = []
  for (const cat of categories) {
    for (const tpl of cat.templates ?? []) {
      chips.push({
        category: cat.id,
        label: tpl.label,
        draft: tpl.draft ?? "",
      })
    }
  }
  return chips
}

function normalizeMessage(
  msg: SupportMessageRow,
  currentUserId: number | string | null = null,
): NormalizedSupportMessage {
  if (msg.message_type === "system" || msg.author === "system") {
    return {
      id: msg.id,
      author: "system",
      body: msg.body,
      created_at: msg.created_at,
    }
  }
  const mine =
    msg.author === "you" ||
    (currentUserId != null && msg.author_id === currentUserId)
  return {
    id: msg.id,
    author: mine ? "you" : "support",
    author_name: msg.author_name || (mine ? "Вы" : "Поддержка"),
    body: msg.body,
    created_at: msg.created_at,
  }
}

export async function getTemplates(context: SupportContext = "general"): Promise<SupportTemplateChip[]> {
  if (USE_MOCK) {
    await delay(150)
    return TEMPLATES[context] || TEMPLATES.general
  }
  const { data } = await api.get("/support/templates", { params: { context } })
  return flattenTemplates(data)
}

export async function createTicket(payload: CreateTicketPayload): Promise<SupportTicket | unknown> {
  if (USE_MOCK) {
    await delay()
    const id = Math.max(0, ..._mockTickets.map((t: unknown) => t.id)) + 1
    const target = ["task_content", "autograder"].includes(payload.category) ? "teacher" : "admin"
    const ticket = {
      id,
      subject:
        payload.subject ||
        SUPPORT_CATEGORIES.find((c: unknown) => c.id === payload.category)?.label ||
        "Обращение",
      category: payload.category,
      status: "open",
      target,
      task_id: payload.task_id || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    _mockTickets = [ticket, ..._mockTickets]
    _mockMessages[id] = [
      {
        id: 1,
        author: "you",
        author_name: "Вы",
        body: payload.body,
        created_at: ticket.created_at,
      },
    ]
    return ticket
  }
  const { data } = await api.post("/support/tickets", payload)
  return data
}

export async function listMyTickets(): Promise<SupportTicket[]> {
  if (USE_MOCK) {
    await delay()
    return [..._mockTickets].sort((a, b) => b.updated_at.localeCompare(a.updated_at))
  }
  const { data } = await api.get("/support/tickets/mine")
  return data.items ?? []
}

export async function listTeacherInbox(): Promise<SupportTicket[]> {
  if (USE_MOCK) {
    await delay()
    return _mockTickets.filter((t: unknown) => t.target === "teacher")
  }
  const { data } = await api.get("/support/tickets/inbox")
  return data.items ?? []
}

export async function listAdminInbox(): Promise<SupportTicket[]> {
  if (USE_MOCK) {
    await delay()
    return _mockTickets.filter((t: unknown) => t.target === "admin")
  }
  const { data } = await api.get("/support/tickets/admin/inbox")
  return data.items ?? []
}

export async function getTicket(
  id: number | string,
  currentUserId: number | string | null = null,
): Promise<Record<string, unknown>> {
  if (USE_MOCK) {
    await delay()
    const ticket = _mockTickets.find((t: unknown) => t.id === Number(id))
    return {
      ...ticket,
      messages: (_mockMessages[id] || []).map((m: unknown) => normalizeMessage(m, currentUserId)),
    }
  }
  const { data } = await api.get(`/support/tickets/${id}`)
  const messages = (data.messages ?? []).map((m: unknown) => normalizeMessage(m, currentUserId))
  return { ...data, messages }
}

export async function postMessage(
  id: number | string,
  body: string,
  currentUserId: number | string | null = null,
): Promise<NormalizedSupportMessage> {
  if (USE_MOCK) {
    await delay()
    const list = _mockMessages[id] || (_mockMessages[id] = [])
    const msg = {
      id: list.length + 1,
      author: "you",
      author_name: "Вы",
      body,
      created_at: new Date().toISOString(),
    }
    list.push(msg)
    _mockTickets = _mockTickets.map((t: unknown) =>
      t.id === Number(id) ? { ...t, updated_at: msg.created_at } : t,
    )
    return msg
  }
  const { data } = await api.post(`/support/tickets/${id}/messages`, { body })
  return normalizeMessage(data, currentUserId)
}

export async function patchTicket(
  id: number | string,
  patch: Record<string, unknown>,
): Promise<SupportTicket | undefined | unknown> {
  if (USE_MOCK) {
    await delay()
    _mockTickets = _mockTickets.map((t: unknown) =>
      t.id === Number(id) ? { ...t, ...patch, updated_at: new Date().toISOString() } : t,
    )
    return _mockTickets.find((t: unknown) => t.id === Number(id))
  }
  const { data } = await api.patch(`/support/tickets/${id}`, patch)
  return data
}
