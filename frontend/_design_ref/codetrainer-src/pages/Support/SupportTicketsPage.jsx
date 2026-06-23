// src/pages/Support/SupportTicketsPage.jsx
// Список «Мои обращения». Рендерится внутри SettingsLayout (вкладка «Помощь») или как /support.
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listMyTickets, SUPPORT_CATEGORIES } from "../../features/support/api/supportApi";
import CreateSupportTicketModal from "../../features/support/components/CreateSupportTicketModal";
import StatusPill from "../../features/support/components/StatusPill";
import { formatRelative } from "../../shared/lib/relativeTime";

const CAT_LABEL = Object.fromEntries(SUPPORT_CATEGORIES.map((c) => [c.id, c.label]));

export default function SupportTicketsPage() {
  const navigate = useNavigate();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);

  const load = () => {
    setLoading(true);
    listMyTickets()
      .then(setTickets)
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  return (
    <div className="max-w-3xl">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-[22px] font-extrabold tracking-tight text-ink">Помощь</h1>
          <p className="mt-1 text-[13px] text-ink-muted">
            Обращения в поддержку и к преподавателям по заданиям.
          </p>
        </div>
        <button type="button" className="btn btn-primary btn-sm" onClick={() => setCreateOpen(true)}>
          + Новое обращение
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-surface">
        {loading && <p className="px-5 py-6 text-[13px] text-ink-faint">Загрузка…</p>}

        {!loading && tickets.length === 0 && (
          <div className="flex flex-col items-center py-12 text-center">
            <div className="mb-3 grid h-14 w-14 place-items-center rounded-2xl border border-border bg-surface-2 text-ink-faint">
              🛟
            </div>
            <p className="text-[14px] font-semibold text-ink">Обращений пока нет</p>
            <p className="mt-1 max-w-xs text-[13px] text-ink-muted">
              Если что-то не работает или есть вопрос по заданию — создайте обращение.
            </p>
            <button type="button" className="btn btn-primary btn-sm mt-4" onClick={() => setCreateOpen(true)}>
              + Новое обращение
            </button>
          </div>
        )}

        {tickets.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => navigate(`/support/tickets/${t.id}`)}
            className="flex w-full items-center gap-4 border-b border-border px-5 py-4 text-left last:border-b-0 hover:bg-surface-2"
          >
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-[12px] font-semibold uppercase tracking-wide text-ink-faint">
                  {CAT_LABEL[t.category] || t.category}
                </span>
                {t.task_id && (
                  <span className="rounded bg-surface-2 px-1.5 py-0.5 font-mono text-[11px] text-ink-faint">
                    #{t.task_id}
                  </span>
                )}
              </div>
              <div className="mt-1 truncate text-[14px] font-medium text-ink">{t.subject}</div>
              <div className="mt-1 text-[12px] text-ink-faint">
                обновлено {formatRelative(t.updated_at)}
              </div>
            </div>
            <StatusPill status={t.status} />
            <span className="text-ink-faint">→</span>
          </button>
        ))}
      </div>

      <CreateSupportTicketModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={(ticket) => navigate(`/support/tickets/${ticket.id}`)}
      />
    </div>
  );
}
