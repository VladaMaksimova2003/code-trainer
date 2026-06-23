interface StudentSidebarProps {
  onSignOut: (...args: unknown[]) => unknown
  streakDays?: number
  streakReady?: boolean
  brandPP?: boolean
  user?: unknown | null
}

import { useLocation, useNavigate } from "react-router-dom"
import { useEffect, useState } from "react"
import { studentSidebarItems } from "./studentSidebarItems"
import BrandLogo from "@/features/auth/ui/BrandLogo"

export default function StudentSidebar({

  onSignOut,
  streakDays = 0,
  streakReady = true,
  items: itemsProp = null,
  brandPP = false,
  user = null,

}: StudentSidebarProps) {
  const navigate = useNavigate()
  const { pathname, search } = useLocation()
  const [pendingPath, setPendingPath] = useState<string | null>(null)
  const items = itemsProp ?? studentSidebarItems(user)

  useEffect(() => {
    setPendingPath(null)
  }, [pathname, search])

  return (
    <nav className="sb">
      <div className="b">
        <BrandLogo size={42} />
        <span>
          Code
          <span
            style={{
              fontFamily: "var(--serif)",
              fontStyle: "italic",
              color: "var(--purple)",
              fontWeight: 400,
            }}
          >
            {" "}
            Trainer
          </span>
        </span>
      </div>

      {items.map((item, idx) => {
        if (item.divider) {
          return (
            <div key={`d-${idx}`} className="sb-group">
              {item.divider}
            </div>
          )
        }
        const active =
          item.matches.length >= 2
            ? item.matches(pathname, search)
            : item.matches(pathname)
        const pending = pendingPath === item.to && !active
        return (
          <button
            key={item.label}
            type="button"
            className={`navlink${active ? ` active${brandPP ? " pp" : ""}` : ""}${pending ? " pending" : ""}`}
            aria-busy={pending ? "true" : undefined}
            onClick={() => {
              setPendingPath(item.to)
              if (item.query) {
                navigate({ pathname: item.to, search: `?tab=${item.query.tab}` })
              } else {
                navigate(item.to)
              }
            }}
          >
            <span className="ic" />
            {item.label}
          </button>
        )
      })}

      <div className="sb-bottom">
        {user ? (
          <>
            <div className="card-soft" style={{ padding: "12px 14px" }}>
              <div className="mono mut3" style={{ fontSize: 10.5 }}>
                Серия дней
              </div>
              <div className="row" style={{ marginTop: 4, gap: 8 }}>
                <span
                  className="stat"
                  style={{
                    fontSize: 22,
                    color: "var(--lime)",
                    minWidth: 18,
                    opacity: streakReady ? 1 : 0.35,
                  }}
                >
                  {streakReady ? streakDays : "·"}
                </span>
                <span className="muted" style={{ fontSize: 12 }}>
                  🔥 дней подряд
                </span>
              </div>
            </div>
            {onSignOut ? (
              <button
                type="button"
                className="navlink"
                style={{ marginTop: 14 }}
                onClick={onSignOut}
              >
                <span className="ic" />
                Выйти
              </button>
            ) : null}
          </>
        ) : null}
      </div>
    </nav>
  )
}
