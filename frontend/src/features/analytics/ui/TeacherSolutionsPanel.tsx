import { Link, useNavigate } from "react-router-dom"
import { useEffect, useMemo, useState } from "react"
import { getTeacherSubmissions } from "@/features/analytics/api/analyticsApi"
import { formatTaskTypeLabel } from "@/shared/types/taskLabels"
import { teacherReviewNavigation } from "@/features/task-solving/routing/teacherReviewNavigation"

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

export default function TeacherSolutionsPanel({ tasks = [], groups = [] }) {
  const navigate = useNavigate()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [taskId, setTaskId] = useState("")
  const [studentId, setStudentId] = useState("")
  const [groupId, setGroupId] = useState("")

  const studentOptions = useMemo(() => {
    const map = new Map()
    items.forEach((row: unknown) => {
      if (row.student_id) {
        map.set(row.student_id, row.student_name)
      }
    })
    return Array.from(map.entries()).map(([id, name]) => ({ id, name }))
  }, [items])

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const params = { limit: 150 }
        if (taskId) params.task_id = Number(taskId)
        if (studentId) params.student_id = Number(studentId)
        if (groupId) params.group_id = Number(groupId)
        const data = await getTeacherSubmissions(params)
        if (!cancelled) setItems(data.items ?? [])
      } catch (err) {
        if (!cancelled) {
          setError(
            err?.response?.data?.detail ||
              err?.message ||
              "Не удалось загрузить решения"
          )
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [taskId, studentId, groupId])

  return (
    <section className="space-y-4">
      <p className="text-xs text-slate-500">
        Показаны решения только студентов из ваших групп.
      </p>
      <div className="flex flex-wrap gap-3">
        <select
          value={taskId}
          onChange={(e: unknown) => setTaskId(e.target.value)}
          className="rounded-lg border border-slate-700 bg-[#0c1224] px-3 py-2 text-sm text-slate-200"
        >
          <option value="">Все задачи</option>
          {tasks.map((t: unknown) => (
            <option key={t.id} value={t.id}>
              {t.title}
            </option>
          ))}
        </select>
        <select
          value={groupId}
          onChange={(e: unknown) => setGroupId(e.target.value)}
          className="rounded-lg border border-slate-700 bg-[#0c1224] px-3 py-2 text-sm text-slate-200"
        >
          <option value="">Все группы</option>
          {groups.map((g: unknown) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </select>
        <select
          value={studentId}
          onChange={(e: unknown) => setStudentId(e.target.value)}
          className="rounded-lg border border-slate-700 bg-[#0c1224] px-3 py-2 text-sm text-slate-200"
        >
          <option value="">Все студенты</option>
          {studentOptions.map((s: unknown) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <p className="text-sm text-red-300">{typeof error === "string" ? error : "Ошибка"}</p>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">Загрузка решений...</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-slate-500">Решений по выбранным фильтрам нет.</p>
      ) : (
        <ul className="divide-y divide-slate-800 border border-slate-800 rounded-lg overflow-hidden bg-[#0c1224]">
          {items.map((row: unknown) => (
            <li
              key={row.id}
              className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 hover:bg-slate-900/80 text-sm"
            >
              <div className="min-w-0">
                <span className="font-medium text-white block truncate">
                  {row.student_name}
                </span>
                <Link
                  to={`/tasks/${row.task_id}`}
                  className="text-teal-300 hover:text-teal-200"
                >
                  {row.task_title}
                </Link>
                <div className="text-xs text-slate-500 mt-1">
                  {formatTaskTypeLabel(row.task_type)} · {row.language} ·{" "}
                  {formatDate(row.created_at)}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={
                    row.success === true
                      ? "text-emerald-400"
                      : row.success === false
                        ? "text-rose-400"
                        : "text-slate-400"
                  }
                >
                  {row.success === true
                    ? "Успех"
                    : row.success === false
                      ? "Ошибка"
                      : row.status}
                </span>
                <button
                  type="button"
                  onClick={() => navigate(teacherReviewNavigation(row))}
                  className="text-xs rounded border border-slate-600 px-2 py-1 text-teal-300 hover:bg-slate-800"
                >
                  К заданию
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
