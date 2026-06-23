import { useEffect, useRef, useState } from "react"
import { isMockApiEnabled } from "@/mocks/config"
import { MOCK_NOTIFICATIONS } from "@/mocks/data/notifications"

function formatWhen(iso: unknown) {
  if (!iso) return ""
  try {
    return new Date(iso).toLocaleString("ru-RU", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    })
  } catch {
    return ""
  }
}

export default function StudentNotificationsButton() {
  const [open, setOpen] = useState(false)
  const [items, setItems] = useState([])
  const rootRef = useRef(null)

  useEffect(() => {
    if (isMockApiEnabled()) {
      setItems(MOCK_NOTIFICATIONS)
    }
  }, [])

  useEffect(() => {
    if (!open) return undefined
    const onDoc = (event: unknown) => {
      if (!rootRef.current?.contains(event.target)) setOpen(false)
    }
    const onEsc = (event: unknown) => {
      if (event.key === "Escape") setOpen(false)
    }
    document.addEventListener("mousedown", onDoc)
    document.addEventListener("keydown", onEsc)
    return () => {
      document.removeEventListener("mousedown", onDoc)
      document.removeEventListener("keydown", onEsc)
    }
  }, [open])

  const unread = items.filter((item: unknown) => !item.read).length

  return (
    <div className="relative" ref={rootRef}>
      <button
        type="button"
        className="icon-btn relative"
        title="Уведомления"
        aria-expanded={open}
        onClick={() => setOpen((value: unknown) => !value)}
      >
        🔔
        {unread > 0 ? (
          <span
            className="absolute -right-1 -top-1 flex h-[18px] min-w-[18px] items-center justify-center rounded-full border border-[rgba(255,80,80,.6)] bg-[#ff3131] px-1 text-[10px] font-bold text-white shadow-[0_0_8px_rgba(255,49,49,.55)]"
            aria-label={`Непрочитанных: ${unread}`}
          >
            {unread > 9 ? "9+" : unread}
          </span>
        ) : null}
      </button>

      {open ? (
        <div
          className="absolute right-0 z-50 mt-2 w-[min(320px,calc(100vw-24px))] overflow-hidden rounded-xl border border-border-2 bg-surface shadow-[0_20px_50px_-20px_rgba(0,0,0,.8)]"
          role="dialog"
          aria-label="Уведомления"
        >
          <div className="border-b border-border px-4 py-3">
            <b style={{ fontSize: 14 }}>Уведомления</b>
          </div>
          <ul className="max-h-[280px] overflow-y-auto py-1">
            {items.length === 0 ? (
              <li className="px-4 py-6 text-center text-[13px] text-ink-faint">Пока нет уведомлений</li>
            ) : (
              items.map((item: unknown) => (
                <li
                  key={item.id}
                  className={`border-b border-border/60 px-4 py-3 last:border-0 ${
                    item.read ? "opacity-70" : "bg-lime-soft/20"
                  }`}
                >
                  <div className="text-[13px] font-medium text-ink">{item.title}</div>
                  <div className="mt-1 text-[12px] leading-snug text-ink-muted">{item.body}</div>
                  <div className="mut3 mt-1.5 text-[11px]">{formatWhen(item.created_at)}</div>
                </li>
              ))
            )}
          </ul>
        </div>
      ) : null}
    </div>
  )
}
