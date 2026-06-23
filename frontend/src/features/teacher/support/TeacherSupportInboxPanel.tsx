// Вкладка «Обращения по заданиям» в кабинете преподавателя.
import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import EmptyState from "@/shared/ui/EmptyState"
import { listTeacherInbox, SUPPORT_CATEGORIES } from "../../support/api/supportApi"
import StatusPill from "../../support/components/StatusPill"
import { formatRelative } from "../../../shared/lib/relativeTime"

const CAT_LABEL = Object.fromEntries(SUPPORT_CATEGORIES.map((c: unknown) => [c.id, c.label]))

export default function TeacherSupportInboxPanel() {
  const navigate = useNavigate()
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState("all")

  useEffect(() => {
    setLoading(true)
    listTeacherInbox()
      .then(setTickets)
      .finally(() => setLoading(false))
  }, [])

  const filtered = tickets.filter((t: unknown) => filter === "all" || t.status === filter)
  const openCount = tickets.filter((t: unknown) => t.status === "open").length
  const isFullyEmpty = !loading && tickets.length === 0

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-2">
        {[
          ["all", "Все"],
          ["open", `Открытые${openCount ? ` · ${openCount}` : ""}`],
          ["in_progress", "В работе"],
          ["resolved", "Решённые"],
        ].map(([id, label]) => (
          <button
            key={id}
            type="button"
            onClick={() => setFilter(id)}
            className={
              "rounded-full border px-3 h-8 text-[13px] transition " +
              (filter === id
                ? "border-purple/45 bg-purple-soft text-purple"
                : "border-border bg-surface-2 text-ink-muted hover:text-ink")
            }
          >
            {label}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="muted">Загрузка обращений…</p>
      ) : isFullyEmpty ? (
        <div className="card card-pad">
          <EmptyState
            icon="📋"
            title="Обращений пока нет"
            text="Когда студенты начнут отправлять вопросы по вашим заданиям, они появятся в этом списке."
          />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card card-pad">
          <EmptyState
            icon="⌕"
            title="Ничего не найдено"
            text="Попробуйте выбрать другой фильтр статуса."
          />
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-border bg-surface">
          {filtered.map((t: unknown) => (
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
                      задача #{t.task_id}
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
      )}
    </div>
  )
}
