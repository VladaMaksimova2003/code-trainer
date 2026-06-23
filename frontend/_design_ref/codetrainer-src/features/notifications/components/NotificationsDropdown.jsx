// src/features/notifications/components/NotificationsDropdown.jsx
// Улучшенный dropdown колокольчика. Самодостаточный: кнопка + поповер + бейдж.
// Подключается к notificationsApi. Подходит и для student topbar, и для teacher topbar.
import { useEffect, useRef, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  listNotifications,
  getUnreadCount,
  markRead,
  markAllRead,
  notificationHref,
} from "../api/notificationsApi";
import { formatRelative } from "../../../shared/lib/relativeTime";

const ICONS = {
  comment: "💬",
  ticket_reply: "↩",
  ticket_created: "🆕",
  ticket_status: "●",
};

export default function NotificationsDropdown() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(false);
  const ref = useRef(null);

  const refreshCount = useCallback(() => {
    getUnreadCount().then((r) => setUnread(r.count || 0)).catch(() => {});
  }, []);

  useEffect(() => {
    refreshCount();
    const t = setInterval(refreshCount, 60000);
    return () => clearInterval(t);
  }, [refreshCount]);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    listNotifications(false)
      .then(setItems)
      .finally(() => setLoading(false));
    const onDoc = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const openItem = async (n) => {
    if (!n.read) {
      await markRead(n.id);
      setItems((prev) => prev.map((x) => (x.id === n.id ? { ...x, read: true } : x)));
      setUnread((c) => Math.max(0, c - 1));
    }
    setOpen(false);
    navigate(notificationHref(n));
  };

  const onMarkAll = async () => {
    await markAllRead();
    setItems((prev) => prev.map((x) => ({ ...x, read: true })));
    setUnread(0);
  };

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        aria-label={`Уведомления${unread ? `, непрочитанных: ${unread}` : ""}`}
        className="icon-btn relative"
        onClick={() => setOpen((o) => !o)}
      >
        🔔
        {unread > 0 && (
          <span className="absolute -right-1 -top-1 grid h-4 min-w-4 place-items-center rounded-full bg-lime px-1 text-[10px] font-bold text-bg">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 top-11 z-50 w-[min(360px,calc(100vw-24px))] overflow-hidden rounded-xl border border-border bg-surface shadow-[0_30px_60px_-20px_rgba(0,0,0,0.8)]"
        >
          <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
            <span className="text-[13px] font-semibold text-ink">Уведомления</span>
            <button
              type="button"
              onClick={onMarkAll}
              disabled={unread === 0}
              className="text-[12px] font-medium text-lime hover:underline disabled:text-ink-faint disabled:no-underline"
            >
              Прочитать все
            </button>
          </div>

          <div className="max-h-[60vh] overflow-y-auto">
            {loading && <p className="px-4 py-5 text-[13px] text-ink-faint">Загрузка…</p>}

            {!loading && items.length === 0 && (
              <p className="px-4 py-8 text-center text-[13px] text-ink-muted">Уведомлений нет</p>
            )}

            {items.map((n) => (
              <button
                key={n.id}
                type="button"
                role="menuitem"
                onClick={() => openItem(n)}
                className={
                  "flex w-full items-start gap-3 border-b border-border px-4 py-3 text-left last:border-b-0 hover:bg-surface-2 " +
                  (!n.read ? "bg-lime-soft/20" : "")
                }
              >
                <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg border border-border bg-surface-2 text-[13px]">
                  {ICONS[n.kind] || "•"}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block text-[13px] font-medium text-ink">{n.title}</span>
                  {n.body && (
                    <span className="mt-0.5 block truncate text-[12px] text-ink-muted">{n.body}</span>
                  )}
                  <span className="mt-1 block text-[11px] text-ink-faint">
                    {formatRelative(n.created_at)}
                  </span>
                </span>
                {!n.read && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-lime" />}
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={() => {
              setOpen(false);
              navigate("/support");
            }}
            className="block w-full border-t border-border px-4 py-2.5 text-center text-[12px] font-medium text-ink-muted hover:bg-surface-2 hover:text-ink"
          >
            Все обращения →
          </button>
        </div>
      )}
    </div>
  );
}
