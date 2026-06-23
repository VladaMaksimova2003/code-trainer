import { useCallback, useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import ProgressBar from "@/features/analytics/ui/ProgressBar"
import { getGroupDashboard, getStudentGroupTasksProgress } from "@/features/groups/api/groupsApi"
import { getTeacherSubmissions } from "@/features/analytics/api/analyticsApi"
import StudentCatalogTasksProgress from "@/features/groups/ui/StudentCatalogTasksProgress"
import { teacherReviewNavigation } from "@/features/task-solving/routing/teacherReviewNavigation"

const DEADLINE_LABELS = {
  on_time: { text: "В срок", className: "text-emerald-400" },
  late: { text: "Просрочено", className: "text-rose-400" },
  pending: { text: "В процессе", className: "text-amber-300" },
  no_deadline: { text: "Без дедлайна", className: "text-slate-500" },
}

function formatDeadline(iso: unknown) {
  if (!iso) return "—"
  try {
    return new Date(iso).toLocaleString("ru-RU", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  } catch {
    return iso
  }
}

export default function TeacherGroupDetailPanel({ group, onBack }) {
  const navigate = useNavigate()
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [recentSolutions, setRecentSolutions] = useState([])
  const [expandedStudentId, setExpandedStudentId] = useState(null)
  const [taskProgress, setTaskProgress] = useState(null)
  const [taskProgressLoading, setTaskProgressLoading] = useState(false)
  const [taskProgressError, setTaskProgressError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [dash, subs] = await Promise.all([
        getGroupDashboard(group.id),
        getTeacherSubmissions({ group_id: group.id, limit: 30 }),
      ])
      setDashboard(dash)
      setRecentSolutions(subs.items ?? [])
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Не удалось загрузить данные группы"
      )
    } finally {
      setLoading(false)
    }
  }, [group.id])

  useEffect(() => {
    load()
  }, [load])

  const progressByStudent = useMemo(() => {
    const map = new Map()
    for (const row of dashboard?.student_catalog_progress ?? []) {
      if (!map.has(row.student_id)) {
        map.set(row.student_id, {
          student_id: row.student_id,
          student_name: row.student_name,
          study_identity: row.study_identity,
          catalogs: [],
        })
      }
      map.get(row.student_id).catalogs.push(row)
    }
    return Array.from(map.values())
  }, [dashboard])

  const toggleStudent = async (studentId: unknown) => {
    if (expandedStudentId === studentId) {
      setExpandedStudentId(null)
      setTaskProgress(null)
      return
    }
    setExpandedStudentId(studentId)
    setTaskProgress(null)
    setTaskProgressError(null)
    setTaskProgressLoading(true)
    try {
      const data = await getStudentGroupTasksProgress(group.id, studentId)
      setTaskProgress(data)
    } catch (err) {
      setTaskProgressError(
        err?.response?.data?.detail ||
          err?.message ||
          "Не удалось загрузить прогресс по заданиям"
      )
    } finally {
      setTaskProgressLoading(false)
    }
  }

  const openTaskReview = (row: unknown) => {
    navigate(teacherReviewNavigation(row))
  }

  if (loading) {
    return <p className="text-sm text-slate-500">Загрузка группы...</p>
  }

  if (error && !dashboard) {
    return (
      <div className="space-y-3">
        <button
          type="button"
          onClick={onBack}
          className="text-sm text-teal-400 hover:text-teal-300"
        >
          ← К списку групп
        </button>
        <p className="text-sm text-red-300">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <button
            type="button"
            onClick={onBack}
            className="text-sm text-teal-400 hover:text-teal-300 mb-2"
          >
            ← К списку групп
          </button>
          <h2 className="text-lg font-semibold text-white">{group.name}</h2>
          <p className="text-sm text-slate-500">
            {dashboard?.members?.length ?? 0} студентов ·{" "}
            {dashboard?.catalogs?.length ?? 0} каталогов
          </p>
        </div>
      </div>

      {error && <p className="text-sm text-red-300">{error}</p>}

      {dashboard?.catalogs?.length > 0 && (
        <section className="space-y-3">
          <h3 className="text-sm font-medium text-slate-300">Каталоги группы</h3>
          <ul className="grid gap-2 sm:grid-cols-2">
            {dashboard.catalogs.map((cat: unknown) => (
              <li
                key={cat.id}
                className="rounded-lg border border-slate-800 bg-[#0c1224] px-4 py-3 text-sm"
              >
                <span className="font-medium text-white">{cat.title}</span>
                <div className="text-xs text-slate-500 mt-1">
                  {cat.task_count} задач · дедлайн: {formatDeadline(cat.deadline_at)}
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="space-y-4">
        <h3 className="text-sm font-medium text-slate-300">
          Прогресс студентов по каталогам
        </h3>
        <p className="text-xs text-slate-500">
          Нажмите на имя студента, чтобы увидеть статус каждого задания.
        </p>
        {progressByStudent.length === 0 ? (
          <p className="text-sm text-slate-500">
            Нет студентов или каталогов для отображения прогресса.
          </p>
        ) : (
          progressByStudent.map((student: unknown) => {
            const isOpen = expandedStudentId === student.student_id
            return (
              <div
                key={student.student_id}
                className="rounded-lg border border-slate-800 bg-[#0c1224] overflow-hidden"
              >
                <button
                  type="button"
                  onClick={() => toggleStudent(student.student_id)}
                  className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left hover:bg-slate-900/80 transition-colors"
                >
                  <div className="min-w-0">
                    <span className="font-medium text-white">{student.student_name}</span>
                    {student.study_identity ? (
                      <span className="text-xs text-slate-500 block">{student.study_identity}</span>
                    ) : null}
                  </div>
                  <span className="text-xs text-slate-500 shrink-0">
                    {isOpen ? "Свернуть ▲" : "Подробнее ▼"}
                  </span>
                </button>
                {!isOpen && student.catalogs.length > 0 && (
                  <div className="px-4 pb-4 space-y-3">
                    {student.catalogs.map((row: unknown) => {
                      const dl =
                        DEADLINE_LABELS[row.deadline_status] ?? DEADLINE_LABELS.pending
                      return (
                        <div
                          key={`${student.student_id}-${row.catalog_id}`}
                          className="space-y-1"
                        >
                          <div className="flex flex-wrap justify-between gap-2 text-sm">
                            <span className="text-slate-300">{row.catalog_title}</span>
                            <span className={dl.className}>{dl.text}</span>
                          </div>
                          <ProgressBar
                            percent={row.progress_percent}
                            label={row.catalog_title}
                            detail={`${row.solved_count} / ${row.total_tasks} задач`}
                          />
                        </div>
                      )
                    })}
                  </div>
                )}
                {isOpen && (
                  <div className="px-4 pb-4 space-y-3">
                    {student.catalogs.length > 0 && (
                      <div className="space-y-3 border-b border-slate-800 pb-3">
                        {student.catalogs.map((row: unknown) => {
                          const dl =
                            DEADLINE_LABELS[row.deadline_status] ?? DEADLINE_LABELS.pending
                          return (
                            <div
                              key={`sum-${student.student_id}-${row.catalog_id}`}
                              className="space-y-1"
                            >
                              <div className="flex flex-wrap justify-between gap-2 text-sm">
                                <span className="text-slate-300">{row.catalog_title}</span>
                                <span className={dl.className}>{dl.text}</span>
                              </div>
                              <ProgressBar
                                percent={row.progress_percent}
                                label={row.catalog_title}
                                detail={`${row.solved_count} / ${row.total_tasks} задач`}
                              />
                            </div>
                          )
                        })}
                      </div>
                    )}
                    <StudentCatalogTasksProgress
                      data={taskProgress}
                      loading={taskProgressLoading}
                      error={taskProgressError}
                    />
                  </div>
                )}
              </div>
            )
          })
        )}
      </section>

      <section className="space-y-3">
        <h3 className="text-sm font-medium text-slate-300">
          Последние решения студентов группы
        </h3>
        {recentSolutions.length === 0 ? (
          <p className="text-sm text-slate-500">Решений пока нет.</p>
        ) : (
          <ul className="divide-y divide-slate-800 border border-slate-800 rounded-lg overflow-hidden bg-[#0c1224]">
            {recentSolutions.map((row: unknown) => (
              <li
                key={row.id}
                className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-slate-900/80"
              >
                <div>
                  <span className="text-white font-medium">{row.student_name}</span>
                  {row.study_identity ? (
                    <span className="text-slate-500 block text-xs">{row.study_identity}</span>
                  ) : null}
                  <span className="text-slate-400 block">{row.task_title}</span>
                </div>
                <button
                  type="button"
                  onClick={() => openTaskReview(row)}
                  className="text-xs rounded border border-slate-600 px-2 py-1 text-teal-300 hover:bg-slate-800"
                >
                  К заданию
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
