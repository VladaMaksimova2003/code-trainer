import {
  canAccessAdminWorkspace,
  canAccessTeacherWorkspace,
} from "@/shared/api/auth"
import type { UserLike } from "@/shared/types/user"

export interface SidebarDividerItem {
  divider: string
}

export interface SidebarLinkItem {
  to: string
  label: string
  matches: (path: string) => boolean
}

export type SidebarItem = SidebarDividerItem | SidebarLinkItem

export function isSidebarDivider(item: SidebarItem): item is SidebarDividerItem {
  return "divider" in item
}

/** Shared sidebar: learning, workspace (teacher + admin), account. */
export function learningSidebarItems(user: UserLike | null = null): SidebarItem[] {
  if (!user) {
    return [
      { to: "/", label: "Список задач", matches: (p: unknown) => p === "/" },
      {
        to: "/learn",
        label: "Курсы",
        matches: (p: unknown) => String(p).startsWith("/learn"),
      },
    ]
  }

  const items: SidebarItem[] = [
    { divider: "Обучение" },
    { to: "/", label: "Список задач", matches: (p: unknown) => p === "/" },
    {
      to: "/learn",
      label: "Курсы",
      matches: (p: unknown) => String(p).startsWith("/learn"),
    },
  ]

  items.push({
    to: "/student/profile",
    label: "Профиль",
    matches: (p: unknown) => p === "/student/profile" || String(p).startsWith("/student/groups"),
  })

  const workspace: SidebarLinkItem[] = []
  if (canAccessTeacherWorkspace(user)) {
    workspace.push({
      to: "/teacher/cabinet",
      label: "Кабинет преподавателя",
      matches: (p: unknown) => p.startsWith("/teacher/cabinet"),
    })
  }
  if (canAccessAdminWorkspace(user)) {
    workspace.push({
      to: "/admin",
      label: "Панель управления",
      matches: (p: unknown) => p.startsWith("/admin"),
    })
  }
  if (workspace.length > 0) {
    items.push({ divider: "Рабочее пространство" }, ...workspace)
  }

  if (user) {
    items.push(
      { divider: "Аккаунт" },
      {
        to: "/settings/profile",
        label: "Настройки",
        matches: (p: unknown) => String(p).startsWith("/settings"),
      },
    )
  }

  return items
}
