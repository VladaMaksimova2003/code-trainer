import { useLocation, useNavigate } from "react-router-dom"
import type { UserLike } from "@/shared/types/user"

interface NavItem {
  to: string
  label: string
  match: (pathname: string) => boolean
}

function studentNavItems(user: UserLike | null): NavItem[] {
  const items: NavItem[] = [
    { to: "/", label: "Задачи", match: (p) => p === "/" },
    { to: "/learn", label: "Курсы", match: (p) => p.startsWith("/learn") },
  ]
  if (!user) return items

  items.push(
    {
      to: "/student/profile",
      label: "Профиль",
      match: (p) => p === "/student/profile" || p.startsWith("/student/groups"),
    },
    {
      to: "/settings/profile",
      label: "Настройки",
      match: (p) => p.startsWith("/settings"),
    },
  )
  return items
}

interface StudentMobileNavProps {
  user?: UserLike | null
}

export default function StudentMobileNav({ user = null }: StudentMobileNavProps) {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const items = studentNavItems(user)

  return (
    <nav className="student-mobile-nav" aria-label="Основная навигация">
      {items.map((item) => {
        const active = item.match(pathname)
        return (
          <button
            key={item.to}
            type="button"
            className={`student-mobile-nav__item${active ? " is-active" : ""}`}
            aria-current={active ? "page" : undefined}
            onClick={() => navigate(item.to)}
          >
            {item.label}
          </button>
        )
      })}
    </nav>
  )
}
