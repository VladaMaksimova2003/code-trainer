// src/features/notifications/api/notificationsApi.js
import client from "../../../shared/api/client";

const USE_MOCK = import.meta.env.VITE_USE_MOCK_API === "true";
const delay = (ms = 250) => new Promise((r) => setTimeout(r, ms));

let _mockNotifications = [
  {
    id: 101,
    kind: "ticket_reply",
    title: "Ответ в обращении #12",
    body: "Поддержка ответила на ваше обращение.",
    read: false,
    created_at: "2026-06-04T09:05:00Z",
    meta: { ticket_id: 12 },
  },
  {
    id: 100,
    kind: "comment",
    title: "Комментарий преподавателя",
    body: "Преподаватель оставил комментарий к задаче «Сумма чисел».",
    read: false,
    created_at: "2026-06-04T08:40:00Z",
    meta: { task_id: 12, submission_id: 42 },
  },
  {
    id: 98,
    kind: "ticket_status",
    title: "Статус обращения изменён",
    body: "Обращение #9 отмечено как решённое.",
    read: true,
    created_at: "2026-06-03T08:00:00Z",
    meta: { ticket_id: 9 },
  },
];

export async function listNotifications(unreadOnly = false) {
  if (USE_MOCK) {
    await delay();
    return unreadOnly ? _mockNotifications.filter((n) => !n.read) : _mockNotifications;
  }
  const { data } = await client.get(`/notifications`, { params: { unread_only: unreadOnly } });
  return data;
}

export async function getUnreadCount() {
  if (USE_MOCK) {
    await delay(120);
    return { count: _mockNotifications.filter((n) => !n.read).length };
  }
  const { data } = await client.get(`/notifications/unread-count`);
  return data;
}

export async function markRead(id) {
  if (USE_MOCK) {
    await delay(120);
    _mockNotifications = _mockNotifications.map((n) => (n.id === id ? { ...n, read: true } : n));
    return { ok: true };
  }
  await client.patch(`/notifications/${id}/read`);
  return { ok: true };
}

export async function markAllRead() {
  if (USE_MOCK) {
    await delay(150);
    _mockNotifications = _mockNotifications.map((n) => ({ ...n, read: true }));
    return { ok: true };
  }
  await client.post(`/notifications/read-all`);
  return { ok: true };
}

// Карта «kind → маршрут» (используется в NotificationsDropdown)
export function notificationHref(n) {
  switch (n.kind) {
    case "comment":
      return `/tasks/${n.meta?.task_id}?tab=comments`;
    case "ticket_reply":
    case "ticket_status":
      return `/support/tickets/${n.meta?.ticket_id}`;
    case "ticket_created":
      return `/teacher?tab=support`;
    default:
      return "/";
  }
}
