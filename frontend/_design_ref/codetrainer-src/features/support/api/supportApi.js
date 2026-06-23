// src/features/support/api/supportApi.js
import client from "../../../shared/api/client";

const USE_MOCK = import.meta.env.VITE_USE_MOCK_API === "true";
const delay = (ms = 320) => new Promise((r) => setTimeout(r, ms));

export const SUPPORT_CATEGORIES = [
  { id: "task_content", label: "Ошибка в условии" },
  { id: "autograder", label: "Автопроверка" },
  { id: "technical", label: "Техническая" },
  { id: "account", label: "Аккаунт" },
  { id: "other", label: "Другое" },
];

export const STATUS_LABELS = {
  open: "Открыто",
  in_progress: "В работе",
  resolved: "Решено",
  closed: "Закрыто",
};

// ---- mock store ----
let _mockTickets = [
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
];
let _mockMessages = {
  12: [
    { id: 1, author: "system", body: "Статус изменён: Открыто → В работе", created_at: "2026-06-04T08:30:00Z" },
    { id: 2, author: "you", author_name: "Вы", body: "Редактор не сохраняет код после обновления страницы.", created_at: "2026-06-04T07:00:00Z" },
    { id: 3, author: "support", author_name: "Поддержка", body: "Уточните, пожалуйста, браузер и ОС.", created_at: "2026-06-04T09:00:00Z" },
  ],
};
const TEMPLATES = {
  task: [
    { category: "task_content", label: "Ошибка в условии", draft: "В условии задачи неточность: " },
    { category: "task_content", label: "Неверный тест", draft: "Тест №… кажется некорректным: ожидается …, но …" },
    { category: "autograder", label: "Автопроверка", draft: "Автопроверка ведёт себя странно: " },
    { category: "other", label: "Другое", draft: "" },
  ],
  general: [
    { category: "technical", label: "Техническая проблема", draft: "Опишите проблему: что произошло и как воспроизвести. " },
    { category: "account", label: "Аккаунт / доступ", draft: "Проблема с доступом: " },
    { category: "other", label: "Другое", draft: "" },
  ],
};

export async function getTemplates(context = "general") {
  if (USE_MOCK) {
    await delay(150);
    return TEMPLATES[context] || TEMPLATES.general;
  }
  const { data } = await client.get(`/support/templates`, { params: { context } });
  return data;
}

export async function createTicket(payload) {
  if (USE_MOCK) {
    await delay();
    const id = Math.max(0, ..._mockTickets.map((t) => t.id)) + 1;
    const target = ["task_content", "autograder"].includes(payload.category) ? "teacher" : "admin";
    const ticket = {
      id,
      subject: payload.subject || SUPPORT_CATEGORIES.find((c) => c.id === payload.category)?.label || "Обращение",
      category: payload.category,
      status: "open",
      target,
      task_id: payload.task_id || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    _mockTickets = [ticket, ..._mockTickets];
    _mockMessages[id] = [
      { id: 1, author: "you", author_name: "Вы", body: payload.body, created_at: ticket.created_at },
    ];
    return ticket;
  }
  const { data } = await client.post(`/support/tickets`, payload);
  return data;
}

export async function listMyTickets() {
  if (USE_MOCK) {
    await delay();
    return [..._mockTickets].sort((a, b) => b.updated_at.localeCompare(a.updated_at));
  }
  const { data } = await client.get(`/support/tickets/mine`);
  return data;
}

export async function listTeacherInbox() {
  if (USE_MOCK) {
    await delay();
    return _mockTickets.filter((t) => t.target === "teacher");
  }
  const { data } = await client.get(`/support/tickets/inbox`);
  return data;
}

export async function listAdminInbox() {
  if (USE_MOCK) {
    await delay();
    return _mockTickets.filter((t) => t.target === "admin");
  }
  const { data } = await client.get(`/support/tickets/admin/inbox`);
  return data;
}

export async function getTicket(id) {
  if (USE_MOCK) {
    await delay();
    const ticket = _mockTickets.find((t) => t.id === Number(id));
    return { ...ticket, messages: _mockMessages[id] || [] };
  }
  const { data } = await client.get(`/support/tickets/${id}`);
  return data;
}

export async function postMessage(id, body) {
  if (USE_MOCK) {
    await delay();
    const list = _mockMessages[id] || (_mockMessages[id] = []);
    const msg = {
      id: list.length + 1,
      author: "you",
      author_name: "Вы",
      body,
      created_at: new Date().toISOString(),
    };
    list.push(msg);
    _mockTickets = _mockTickets.map((t) =>
      t.id === Number(id) ? { ...t, updated_at: msg.created_at } : t
    );
    return msg;
  }
  const { data } = await client.post(`/support/tickets/${id}/messages`, { body });
  return data;
}

export async function patchTicket(id, patch) {
  if (USE_MOCK) {
    await delay();
    _mockTickets = _mockTickets.map((t) =>
      t.id === Number(id) ? { ...t, ...patch, updated_at: new Date().toISOString() } : t
    );
    return _mockTickets.find((t) => t.id === Number(id));
  }
  const { data } = await client.patch(`/support/tickets/${id}`, patch);
  return data;
}
