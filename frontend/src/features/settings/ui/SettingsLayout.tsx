import { Outlet, useLocation, useNavigate } from "react-router-dom"
import { userHasRole } from "@/shared/api/auth"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import PageHeader from "@/features/student/layout/PageHeader"

export const inputClass = "input"

function settingsTabsFor() {
  return [
    { to: "/settings/profile", label: "Профиль" },
    { to: "/settings/security", label: "Безопасность" },
    { to: "/settings/learning", label: "Обучение" },
    { to: "/settings/help", label: "Помощь" },
  ]
}

export default function SettingsLayout({ user, onSignOut }) {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const tabs = settingsTabsFor()
  return (
    <LearningAppShell user={user} onSignOut={onSignOut}>
      <PageHeader
        title="Настройки"
        subtitle="Управляйте профилем, безопасностью и предпочтениями обучения."
      />
      <div className="tabbar">
        {tabs.map((t: unknown) => (
          <button
            key={t.to}
            type="button"
            className={`${pathname === t.to || pathname.startsWith(`${t.to}/`) ? "on" : ""}${userHasRole(user, "TEACHER") ? " pp" : ""}`}
            onClick={() => navigate(t.to)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <Outlet context={{ user }} />
    </LearningAppShell>
  )
}
