interface TeacherAnalyticsPanelProps {
  analytics: unknown
}

import ErrorBreakdownChart from "@/features/analytics/ui/ErrorBreakdownChart"
import { formatTaskTypeLabel } from "@/shared/types/taskLabels"

const DIFFICULTY_LABELS = {
  easy: "Лёгкая",
  medium: "Средняя",
  hard: "Сложная",
}

export default function TeacherAnalyticsPanel({
 analytics 
}: TeacherAnalyticsPanelProps) {
  if (!analytics) return null

  const {
    per_assignment,
    task_type_success,
    groups,
    students,
    error_breakdown_overall,
  } = analytics

  return (
    <div className="space-y-6">
      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-[#0c1224] p-4">
          <h3 className="text-sm font-medium text-slate-200 mb-3">По заданиям</h3>
          {!per_assignment?.length ? (
            <p className="text-sm text-slate-500">Нет отправок по вашим задачам.</p>
          ) : (
            <div className="max-h-80 overflow-auto scrollbar-dark">
              <table className="w-full text-sm text-left">
                <thead className="text-xs uppercase text-slate-500 sticky top-0 bg-[#0c1224]">
                  <tr>
                    <th className="pb-2 pr-2">Задача</th>
                    <th className="pb-2">Успех</th>
                    <th className="pb-2">Ср. попытки</th>
                    <th className="pb-2">Студенты</th>
                  </tr>
                </thead>
                <tbody>
                  {per_assignment.map((row: unknown) => (
                    <tr key={row.task_id} className="border-t border-slate-800">
                      <td className="py-2 pr-2">
                        <span className="text-slate-200 block truncate max-w-[10rem]">
                          {row.title}
                        </span>
                        <span className="text-xs text-slate-500">
                          {DIFFICULTY_LABELS[row.difficulty] || row.difficulty}
                        </span>
                      </td>
                      <td className="py-2 text-emerald-300">{row.success_percent}%</td>
                      <td className="py-2 text-slate-400">{row.avg_attempts}</td>
                      <td className="py-2 text-slate-400">{row.student_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <ErrorBreakdownChart
          breakdown={error_breakdown_overall}
          title="Типичные ошибки (все задания)"
        />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-[#0c1224] p-4">
          <h3 className="text-sm font-medium text-slate-200 mb-3">По группам</h3>
          {!groups?.length ? (
            <p className="text-sm text-slate-500">Групп пока нет.</p>
          ) : (
            <ul className="space-y-3 text-sm">
              {groups.map((g: unknown) => (
                <li
                  key={g.group_id}
                  className="border-b border-slate-800 pb-3 last:border-0"
                >
                  <div className="flex justify-between gap-2">
                    <span className="font-medium text-white">{g.name}</span>
                    <span className="text-slate-400">{g.member_count} чел.</span>
                  </div>
                  <p className="text-slate-400 mt-1">
                    Средний прогресс: {g.avg_progress_percent}%
                  </p>
                  {g.weak_topics?.length > 0 && (
                    <p className="text-xs text-rose-300/90 mt-1">
                      Слабые темы: {g.weak_topics.join(", ")}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="rounded-xl border border-slate-800 bg-[#0c1224] p-4">
          <h3 className="text-sm font-medium text-slate-200 mb-3">По типу задания</h3>
          <ul className="space-y-2 text-sm">
            {task_type_success?.map((row: unknown) => (
              <li key={row.task_type} className="flex justify-between gap-2">
                <span className="text-slate-300">
                  {formatTaskTypeLabel(row.task_type)}
                </span>
                <span className="text-slate-400">
                  {row.success_rate}% ({row.submissions} отпр.)
                </span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="rounded-xl border border-slate-800 bg-[#0c1224] p-4">
        <h3 className="text-sm font-medium text-slate-200 mb-3">Студенты групп</h3>
        {!students?.length ? (
          <p className="text-sm text-slate-500">
            Нет студентов в группах или нет активности.
          </p>
        ) : (
          <div className="max-h-72 overflow-auto scrollbar-dark">
            <table className="w-full text-sm text-left">
              <thead className="text-xs uppercase text-slate-500">
                <tr>
                  <th className="pb-2">Студент</th>
                  <th className="pb-2">Прогресс</th>
                  <th className="pb-2">Слабые темы</th>
                  <th className="pb-2">Активность</th>
                </tr>
              </thead>
              <tbody>
                {students.map((row: unknown) => (
                  <tr key={row.student_id} className="border-t border-slate-800">
                    <td className="py-2 text-slate-200">{row.name}</td>
                    <td className="py-2 text-teal-300">{row.progress_percent}%</td>
                    <td className="py-2 text-xs text-slate-400">
                      {row.weak_topics?.join(", ") || "—"}
                    </td>
                    <td className="py-2 text-xs text-slate-500">
                      {row.last_activity_at
                        ? new Date(row.last_activity_at).toLocaleDateString("ru-RU")
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {per_assignment?.some((a: unknown) => a.error_breakdown?.total_failed > 0) && (
        <section className="rounded-xl border border-slate-800 bg-[#0c1224] p-4">
          <h3 className="text-sm font-medium text-slate-200 mb-3">
            Ошибки по заданиям (выборка)
          </h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {per_assignment
              .filter((a: unknown) => a.error_breakdown?.total_failed > 0)
              .slice(0, 6)
              .map((row: unknown) => (
                <ErrorBreakdownChart
                  key={row.task_id}
                  breakdown={row.error_breakdown}
                  title={row.title}
                />
              ))}
          </div>
        </section>
      )}
    </div>
  )
}
