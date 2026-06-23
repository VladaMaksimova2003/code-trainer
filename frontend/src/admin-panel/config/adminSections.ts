import { buildTcConceptsSubtitle } from "@/admin-panel/config/tcConceptsMeta"

export const ADMIN_SECTIONS = [
  {
    to: "/admin",
    label: "Обзор",
    end: true,
    match: (p) => p === "/admin",
    title: "Обзор платформы",
    subtitle: "Сводка по пользователям, задачам и активности",
  },
  {
    to: "/admin/users",
    label: "Пользователи",
    match: (p) => p === "/admin/users" || /^\/admin\/users\/\d+$/.test(p),
    title: "Пользователи",
    subtitle: "Поиск, роли, блокировка и удаление аккаунтов",
  },
  {
    to: "/admin/teacher-requests",
    label: "Заявки преподавателей",
    match: (p) => p.startsWith("/admin/teacher-requests"),
    title: "Заявки на роль преподавателя",
    subtitle: "Рассмотрение и модерация заявок от студентов",
  },
  {
    to: "/admin/assignments",
    label: "Задания",
    match: (p) => p.startsWith("/admin/assignments"),
    title: "Модерация заданий",
    subtitle: "Статусы, архивирование и версии заданий",
  },
  {
    to: "/admin/tc-concepts",
    label: "Концепции",
    match: (p) => p.startsWith("/admin/tc-concepts"),
    title: "Технические концепции",
    subtitle: buildTcConceptsSubtitle(),
  },
  {
    to: "/admin/create-teacher",
    label: "Создать преподавателя",
    match: (p) => p.startsWith("/admin/create-teacher"),
    title: "Создать преподавателя",
    subtitle: "Регистрация учётной записи с ролями студент и преподаватель",
  },
  {
    to: "/admin/create-admin",
    label: "Создать администратора",
    match: (p) => p.startsWith("/admin/create-admin"),
    title: "Создать администратора",
    subtitle: "Регистрация учётной записи с ролями студент и администратор",
  },
]

const USER_DETAIL_META = {
  title: "Пользователь",
  subtitle: "Просмотр и управление аккаунтом",
}

export function getAdminPageMeta(pathname) {
  if (/^\/admin\/users\/\d+$/.test(pathname)) {
    return USER_DETAIL_META
  }
  const section = ADMIN_SECTIONS.find((item) => item.match(pathname))
  if (section) {
    return { title: section.title, subtitle: section.subtitle }
  }
  return { title: "Панель управления", subtitle: "Администрирование платформы" }
}

export function getAdminCrumbLabel(pathname) {
  if (/^\/admin\/users\/\d+$/.test(pathname)) return "Пользователь"
  const section = ADMIN_SECTIONS.find((item) => item.match(pathname))
  return section?.label ?? "Админка"
}
