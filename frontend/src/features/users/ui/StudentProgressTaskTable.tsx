interface StudentProgressTaskTableProps {
  tasks?: unknown[]
  onTaskClick: (...args: unknown[]) => unknown
  emptyText?: string
}

import { formatTaskTypeLabel } from "@/shared/types/taskLabels"
import TaskStatusDot from "@/shared/ui/TaskStatusDot"
import DiffBadge from "@/shared/ui/DiffBadge"
import StatusBadge from "@/shared/ui/StatusBadge"
import EmptyState from "@/shared/ui/EmptyState"
import { taskLanguageLabel, taskStudentStatus } from "@/features/student/utils/taskView"
import { formatShortDateTime } from "@/shared/utils/format"

export default function StudentProgressTaskTable({

  tasks = [],
  onTaskClick,
  emptyText = "Нет задач.",

}: StudentProgressTaskTableProps) {
  if (tasks.length === 0) {
    return (
      <div className="card card-pad">
        <EmptyState icon="⌕" title="Ничего не найдено" text={emptyText} />
      </div>
    )
  }

  return (
    <div className="card card-pad">
      <table className="table">
        <thead>
          <tr>
            <th style={{ width: 38 }} />
            <th>Задача</th>
            <th>Тип</th>
            <th>Язык</th>
            <th>Сложность</th>
            <th>Статус</th>
            <th>Попытки</th>
            <th>Дата</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((t: unknown) => {
            const status = taskStudentStatus(t)
            const clickable = Boolean(onTaskClick)
            return (
              <tr
                key={`${t.catalog_id ?? "c"}-${t.id}`}
                onClick={clickable ? () => onTaskClick(t.id) : undefined}
                className={clickable ? undefined : "no-hover"}
                style={clickable ? { cursor: "pointer" } : undefined}
              >
                <td>
                  <TaskStatusDot status={status} />
                </td>
                <td className="t-name">{t.title}</td>
                <td className="muted">{formatTaskTypeLabel(t.type || t.task_type)}</td>
                <td className="muted">{taskLanguageLabel(t)}</td>
                <td>
                  <DiffBadge diff={t.difficulty || t.diff} />
                </td>
                <td>
                  <StatusBadge status={status} />
                </td>
                <td className="mono">{t.attempts ?? 0}</td>
                <td className="muted">
                  {t.last_activity_at ? formatShortDateTime(t.last_activity_at) : "—"}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
