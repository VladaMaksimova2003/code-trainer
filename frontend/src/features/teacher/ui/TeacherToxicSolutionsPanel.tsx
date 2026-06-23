interface TeacherToxicSolutionsPanelProps {
  groups?: unknown[]
  catalogs?: unknown[]
  teacherUserId?: unknown | null
  onItemsCount: (...args: unknown[]) => unknown
}

import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { getTeacherSubmissions } from "@/features/analytics/api/analyticsApi"
import { teacherReviewNavigation } from "@/features/task-solving/routing/teacherReviewNavigation"
import { submissionUiStatus } from "@/features/student/utils/taskView"
import StatusBadge from "@/shared/ui/StatusBadge"
import ProfileLink from "@/shared/ui/ProfileLink"
import ProfileSectionTitle from "@/shared/ui/ProfileSectionTitle"
import RoleAvatar from "@/shared/ui/RoleAvatar"
import EmptyState from "@/shared/ui/EmptyState"
import { formatShortDateTime, shortDisplayName } from "@/shared/utils/format"
import { getLanguageLabel } from "@/shared/config/languages"

const STATUS_FILTERS = [
  ["all", "Все"],
  ["accepted", "Принятые"],
  ["failed", "С ошибкой"],
]

export default function TeacherToxicSolutionsPanel({

  groups = [],
  catalogs = [],
  teacherUserId = null,
  onItemsCount,

}: TeacherToxicSolutionsPanelProps) {
  const navigate = useNavigate()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusFilter, setStatusFilter] = useState("all")
  const [groupId, setGroupId] = useState("")
  const [catalogId, setCatalogId] = useState("")

  const groupCatalogs = useMemo(() => {
    if (!groupId) return catalogs
    return catalogs.filter((c: unknown) => String(c.group_id) === String(groupId))
  }, [catalogs, groupId])

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const params = { limit: 200 }
        if (groupId) params.group_id = Number(groupId)
        if (catalogId) params.catalog_id = Number(catalogId)
        const data = await getTeacherSubmissions(params)
        if (!cancelled) setItems(data.items ?? [])
      } catch (err) {
        if (!cancelled) {
          setItems([])
          setError(err?.response?.data?.detail || err?.message || "Не удалось загрузить решения")
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [groupId, catalogId])

  const filtered = useMemo(() => {
    if (statusFilter === "all") return items
    return items.filter((row: unknown) => submissionUiStatus(row) === statusFilter)
  }, [items, statusFilter])

  useEffect(() => {
    if (!loading) onItemsCount?.(items.length)
  }, [items.length, loading, onItemsCount])

  const showFilters = items.length > 0 || groupId || catalogId
  const isFullyEmpty = !loading && items.length === 0 && !groupId && !catalogId

  const openTaskReview = (row: { id: number | string; task_id: number | string; student_name?: string; success?: boolean | null }) => {
    const target = teacherReviewNavigation(row)
    navigate(target)
  }

  return (
    <section>
      {!loading && !isFullyEmpty ? (
        <ProfileSectionTitle>Решения студентов</ProfileSectionTitle>
      ) : null}

      {showFilters ? (
        <>
          <div className="wrap" style={{ marginBottom: 14, gap: 8 }}>
            {groups.length > 0 ? (
              <select
                className="select"
                style={{ width: 180, height: 34, padding: "6px 12px", fontSize: 13 }}
                value={groupId}
                onChange={(e: unknown) => {
                  setGroupId(e.target.value)
                  setCatalogId("")
                }}
              >
                <option value="">Все группы</option>
                {groups.map((g: unknown) => (
                  <option key={g.id} value={g.id}>
                    {g.name}
                  </option>
                ))}
              </select>
            ) : null}
            {groupCatalogs.length > 0 ? (
              <select
                className="select"
                style={{ width: 200, height: 34, padding: "6px 12px", fontSize: 13 }}
                value={catalogId}
                onChange={(e: unknown) => setCatalogId(e.target.value)}
              >
                <option value="">Все каталоги</option>
                {groupCatalogs.map((c: unknown) => (
                  <option key={c.id} value={c.id}>
                    {c.title}
                  </option>
                ))}
              </select>
            ) : null}
          </div>

          <div className="wrap" style={{ marginBottom: 14 }}>
            {STATUS_FILTERS.map(([id, label]) => (
              <span
                key={id}
                className={`chip${statusFilter === id ? " on pp" : ""}`}
                role="button"
                tabIndex={0}
                onClick={() => setStatusFilter(id)}
                onKeyDown={(e: unknown) => e.key === "Enter" && setStatusFilter(id)}
              >
                {label}
              </span>
            ))}
          </div>
        </>
      ) : null}

      {error ? (
        <div className="toast err" style={{ marginBottom: 14, maxWidth: "none" }}>
          <div className="tt">{error}</div>
        </div>
      ) : null}

      {loading ? (
        <p className="muted">Загрузка решений…</p>
      ) : isFullyEmpty ? (
        <div className="card card-pad">
          <EmptyState
            icon="📋"
            title="Решений пока нет"
            text="Когда студенты начнут отправлять решения по вашим задачам, они появятся в этом списке."
          />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card card-pad">
          <EmptyState
            icon="⌕"
            title="Ничего не найдено"
            text="Попробуйте изменить фильтры или сбросить статус."
          />
        </div>
      ) : (
        <div className="card card-pad">
          <table className="table">
            <thead>
              <tr>
                <th>Студент</th>
                <th>Задача</th>
                <th>Язык</th>
                <th>Статус</th>
                <th>Дата</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filtered.map((row: unknown) => {
                const lang = getLanguageLabel(row.language) || row.language || "—"
                return (
                  <tr key={row.id} className="no-hover">
                    <td>
                      <div className="row" style={{ gap: 9 }}>
                        <RoleAvatar
                          user={{ id: row.student_id }}
                          name={row.student_name}
                          role="student"
                          size="sm"
                        />
                        <ProfileLink userId={row.student_id} teacherId={teacherUserId}>
                          <span>{shortDisplayName(row.student_name)}</span>
                          {row.study_identity ? (
                            <span className="mut3" style={{ display: "block", fontSize: 11.5 }}>
                              {row.study_identity}
                            </span>
                          ) : null}
                        </ProfileLink>
                      </div>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        style={{ padding: "2px 0", minHeight: 0, fontWeight: 500 }}
                        onClick={() => openTaskReview(row)}
                      >
                        {row.task_title}
                      </button>
                    </td>
                    <td className="muted">{lang}</td>
                    <td>
                      <StatusBadge status={submissionUiStatus(row)} />
                    </td>
                    <td
                      className="muted"
                      style={row.is_late ? { color: "var(--warn, #ffb347)" } : undefined}
                      title={row.is_late ? "Сдано после дедлайна" : undefined}
                    >
                      {formatShortDateTime(row.created_at)}
                    </td>
                    <td className="right">
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => openTaskReview(row)}
                      >
                        Открыть
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
