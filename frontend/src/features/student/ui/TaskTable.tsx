interface TaskTableProps {
  tasks: unknown
  page: unknown
  pageSize: unknown
  pageCount: unknown
  totalFiltered: unknown
  onPageChange: (...args: unknown[]) => unknown
  onResetFilters: (...args: unknown[]) => unknown
  taskPathPrefix?: string
}

import { useNavigate } from "react-router-dom"
import { formatTaskTypeLabel } from "@/shared/types/taskLabels"
import TaskStatusDot from "@/shared/ui/TaskStatusDot"
import DiffBadge from "@/shared/ui/DiffBadge"
import LangPills from "@/features/student/ui/LangPills"
import LangStatus from "@/features/student/ui/LangStatus"
import Pagination from "@/shared/ui/Pagination"
import EmptyState from "@/shared/ui/EmptyState"
import { taskStudentStatus } from "@/features/student/utils/taskView"

export default function TaskTable({

  tasks,
  page,
  pageSize,
  pageCount,
  totalFiltered,
  onPageChange,
  onResetFilters,
  taskPathPrefix = "/tasks",

}: TaskTableProps) {
  const navigate = useNavigate()

  if (tasks.length === 0) {
    return (
      <div className="card card-pad">
        <EmptyState
          icon="⌕"
          title="Ничего не найдено"
          text="Попробуйте сбросить фильтры или поискать что-то другое."
          action={
            <button type="button" className="btn btn-primary btn-sm" onClick={onResetFilters}>
              Сбросить фильтры
            </button>
          }
        />
      </div>
    )
  }

  const from = (page - 1) * pageSize + 1
  const to = Math.min(page * pageSize, totalFiltered)

  return (
    <div className="card card-pad task-table-card">
      <div className="table-scroll">
        <table className="table task-table">
          <thead>
            <tr>
              <th className="task-table__dot" />
              <th>Задача</th>
              <th>Тип</th>
              <th>Язык</th>
              <th>Сложность</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((t: unknown) => {
              const status = taskStudentStatus(t)
              return (
                <tr key={t.id} onClick={() => navigate(`${taskPathPrefix}/${t.id}`)}>
                  <td>
                    <TaskStatusDot status={status} />
                  </td>
                  <td className="t-name">{t.title}</td>
                  <td className="muted">{formatTaskTypeLabel(t.type)}</td>
                  <td>
                    <LangPills task={t} />
                  </td>
                  <td>
                    <DiffBadge diff={t.difficulty || t.diff} />
                  </td>
                  <td>
                    <LangStatus task={t} />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div className="between" style={{ marginTop: 16 }}>
        <span className="mut3" style={{ fontSize: 13 }}>
          {from}–{to} из {totalFiltered}
        </span>
        <Pagination page={page} pageCount={pageCount} onChange={onPageChange} />
      </div>
    </div>
  )
}
