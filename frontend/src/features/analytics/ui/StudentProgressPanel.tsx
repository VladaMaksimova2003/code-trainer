interface StudentProgressPanelProps {
  analytics: unknown
}

import { Link } from "react-router-dom"
import ProgressBar from "@/features/analytics/ui/ProgressBar"
import ErrorBreakdownChart from "@/features/analytics/ui/ErrorBreakdownChart"
import { formatTaskTypeLabel } from "@/shared/types/taskLabels"
import { Card } from "@/shared/ui"

function formatDate(iso: unknown) {
  if (!iso) return ""
  try {
    return new Date(iso).toLocaleString("ru-RU", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    })
  } catch {
    return iso
  }
}

export default function StudentProgressPanel({
 analytics 
}: StudentProgressPanelProps) {
  if (!analytics) return null

  const { overview, by_language, by_structure, recent_activity, per_task, by_task_type, error_breakdown, recommendations } =
    analytics

  return (
    <div className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Общий прогресс"
          value={`${overview.completion_percent}%`}
          sub={`${overview.solved_count} / ${overview.total_tasks} задач`}
        />
        <StatCard label="Уровень" value={overview.level} sub="по доле решённых" />
        <StatCard
          label="Успешность"
          value={`${overview.success_rate}%`}
          sub={`${overview.total_submissions} попыток`}
        />
        <StatCard
          label="Решено"
          value={String(overview.solved_count)}
          sub="уникальных задач"
        />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card className="space-y-4">
          <h3 className="text-sm font-semibold text-ink">По языкам</h3>
          {by_language?.length ? (
            by_language.map((row: unknown) => (
              <ProgressBar
                key={row.language}
                label={row.language}
                percent={row.percent}
                detail={`${row.solved} / ${row.total} задач`}
                accent="lime"
              />
            ))
          ) : (
            <p className="text-sm text-ink-faint">Нет данных по языкам.</p>
          )}
        </Card>

        <Card className="space-y-4">
          <h3 className="text-sm font-semibold text-ink">Навыки</h3>
          {by_structure?.map((row: unknown) => (
            <ProgressBar
              key={row.id}
              label={row.label}
              hint={row.hint}
              percent={row.percent}
              detail={
                row.attempted > 0
                  ? `Решено ${row.solved} из ${row.attempted} затронутых задач`
                  : "Пока нет попыток по этой теме"
              }
            />
          ))}
        </Card>
      </section>

      <Card as="section">
        <h3 className="mb-3 text-sm font-semibold text-ink">Недавняя активность</h3>
        {!recent_activity?.length ? (
          <p className="text-sm text-ink-faint">Активности пока нет.</p>
        ) : (
          <ul className="divide-y divide-border">
            {recent_activity.map((item: unknown) => (
              <li
                key={item.submission_id}
                className="flex flex-wrap items-center justify-between gap-2 py-2 text-sm"
              >
                <div>
                  <Link
                    to={`/tasks/${item.task_id}`}
                    className="font-medium text-lime hover:text-lime-600"
                  >
                    {item.task_title}
                  </Link>
                  <span className="ml-2 text-ink-faint">{item.language}</span>
                  <div className="mt-0.5 text-xs text-ink-faint">
                    {formatDate(item.created_at)}
                  </div>
                </div>
                <span
                  className={
                    item.success === true
                      ? "text-lime"
                      : item.success === false
                        ? "text-danger"
                        : "text-ink-muted"
                  }
                >
                  {item.success === true
                    ? "Успех"
                    : item.success === false
                      ? "Ошибка"
                      : "В обработке"}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-ink">По задачам</h3>
          <div className="max-h-64 overflow-auto scrollbar-dark">
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase text-ink-faint">
                <tr>
                  <th className="pb-2">Задача</th>
                  <th className="pb-2">Попытки</th>
                  <th className="pb-2">Успех %</th>
                </tr>
              </thead>
              <tbody>
                {per_task?.map((row: unknown) => (
                  <tr key={row.task_id} className="border-t border-border">
                    <td className="max-w-[12rem] truncate py-2 pr-2 text-ink">
                      {row.title}
                    </td>
                    <td className="py-2 text-ink-muted">{row.attempts}</td>
                    <td className="py-2">
                      <span className={row.solved ? "text-lime" : "text-ink-muted"}>
                        {row.success_rate}%
                        {row.solved ? " ✓" : ""}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <div className="space-y-4">
          <Card>
            <h3 className="mb-3 text-sm font-semibold text-ink">По типу задания</h3>
            <ul className="space-y-2 text-sm">
              {by_task_type?.map((row: unknown) => (
                <li key={row.task_type} className="flex justify-between gap-2">
                  <span className="text-ink-muted">
                    {formatTaskTypeLabel(row.task_type)}
                  </span>
                  <span className="text-ink-muted">{row.success_rate}%</span>
                </li>
              ))}
            </ul>
          </Card>
          <ErrorBreakdownChart breakdown={error_breakdown} />
        </div>
      </section>

      {recommendations?.length > 0 && (
        <Card as="section" className="border-lime/40 bg-lime/10">
          <h3 className="mb-2 text-sm font-semibold text-lime">Рекомендации</h3>
          <ul className="space-y-2 text-sm text-ink-muted">
            {recommendations.map((rec, index) => (
              <li key={`${rec.kind}-${index}`}>
                <span className="font-medium text-ink">{rec.text}</span>
                {rec.detail && (
                  <span className="mt-0.5 block text-xs text-ink-faint">{rec.detail}</span>
                )}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  )
}

function StatCard({ label, value, sub }) {
  return (
    <Card>
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-faint">{label}</p>
      <p className="mt-1 text-2xl font-bold text-ink">{value}</p>
      {sub && <p className="mt-1 text-xs text-ink-faint">{sub}</p>}
    </Card>
  )
}
