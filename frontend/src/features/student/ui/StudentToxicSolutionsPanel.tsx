interface StudentToxicSolutionsPanelProps {
  submissions?: unknown[]
}

import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { formatDateTime } from "@/shared/utils/format"
import { getLanguageLabel } from "@/shared/config/languages"
import { submissionUiStatus } from "@/features/student/utils/taskView"
import { usePagination } from "@/shared/hooks/usePagination"
import StatusBadge from "@/shared/ui/StatusBadge"
import EmptyState from "@/shared/ui/EmptyState"
import Pagination from "@/shared/ui/Pagination"

const PAGE_SIZE = 15

export default function StudentToxicSolutionsPanel({
  submissions = [],
}: StudentToxicSolutionsPanelProps) {
  const navigate = useNavigate()
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [sort, setSort] = useState("new")

  const filtered = useMemo(() => {
    let rows = [...submissions]
    if (search.trim()) {
      const q = search.toLowerCase()
      rows = rows.filter(
        (s: unknown) =>
          (s.task_title || "").toLowerCase().includes(q) ||
          String(s.task_id || "").includes(q),
      )
    }
    if (statusFilter !== "all") {
      rows = rows.filter((s: unknown) => submissionUiStatus(s) === statusFilter)
    }
    rows.sort((a, b) => {
      const da = new Date(a.created_at || 0)
      const db = new Date(b.created_at || 0)
      return sort === "old" ? da - db : db - da
    })
    return rows
  }, [submissions, search, statusFilter, sort])

  const { page, setPage, totalPages, pageItems } = usePagination(filtered, PAGE_SIZE)

  useEffect(() => {
    setPage(1)
  }, [search, statusFilter, sort, submissions.length, setPage])

  return (
    <div>
      <div className="between" style={{ marginBottom: 16, flexWrap: "wrap", gap: 10 }}>
        <input
          className="input"
          style={{ width: 280, height: 38 }}
          placeholder="Поиск по решениям…"
          value={search}
          onChange={(e: unknown) => setSearch(e.target.value)}
        />
        <div className="wrap">
          <select
            className="select"
            style={{ width: 150, height: 38, padding: "8px 12px", fontSize: 13 }}
            value={statusFilter}
            onChange={(e: unknown) => setStatusFilter(e.target.value)}
          >
            <option value="all">Все статусы</option>
            <option value="accepted">Решено</option>
            <option value="failed">Ошибка тестов</option>
            <option value="reviewing">На проверке</option>
          </select>
          <select
            className="select"
            style={{ width: 170, height: 38, padding: "8px 12px", fontSize: 13 }}
            value={sort}
            onChange={(e: unknown) => setSort(e.target.value)}
          >
            <option value="new">Сначала новые</option>
            <option value="old">Сначала старые</option>
          </select>
        </div>
      </div>

      <div className="card card-pad">
        {filtered.length === 0 ? (
          <EmptyState
            icon="📋"
            title={submissions.length === 0 ? "Решений пока нет" : "Ничего не найдено"}
            text={
              submissions.length === 0
                ? "Решите свою первую задачу — попытки появятся здесь."
                : "Попробуйте изменить фильтры или поисковый запрос."
            }
            action={
              submissions.length === 0 ? (
                <button type="button" className="btn btn-primary" onClick={() => navigate("/")}>
                  К списку задач
                </button>
              ) : null
            }
          />
        ) : (
          <>
            <table className="table">
              <thead>
                <tr>
                  <th>Задача</th>
                  <th>Язык</th>
                  <th>Попытка</th>
                  <th>Статус</th>
                  <th>Дата</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((s: unknown) => (
                  <tr key={s.id} onClick={() => navigate(`/tasks/${s.task_id}`)}>
                    <td className="t-name">{s.task_title || `Задача #${s.task_id}`}</td>
                    <td className="muted">{getLanguageLabel(s.language) || s.language || "—"}</td>
                    <td className="mono mut3">#{s.id}</td>
                    <td>
                      <StatusBadge status={submissionUiStatus(s)} />
                    </td>
                    <td className="muted">{formatDateTime(s.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {totalPages > 1 ? (
              <div className="between" style={{ marginTop: 16, flexWrap: "wrap", gap: 10 }}>
                <span className="mut3" style={{ fontSize: 13 }}>
                  {filtered.length} решений · страница {page} из {totalPages}
                </span>
                <Pagination page={page} pageCount={totalPages} onChange={setPage} />
              </div>
            ) : null}
          </>
        )}
      </div>
    </div>
  )
}
