interface StudentGroupCatalogsViewProps {
  catalogs?: unknown[]
  loading?: boolean
  error?: string
  manualNavigation?: boolean
  emptyMessage?: string
}

import { useNavigate } from "react-router-dom"
import { formatDateTime } from "@/shared/utils/format"

const STATUS_META = {
  solved: { label: "Решено", className: "text-emerald-400 bg-emerald-950/40 border-emerald-800" },
  in_progress: {
    label: "В процессе",
    className: "text-amber-300 bg-amber-950/40 border-amber-800",
  },
  not_started: {
    label: "Не начато",
    className: "text-slate-400 bg-slate-900 border-slate-700",
  },
}

export default function StudentGroupCatalogsView({

  catalogs = [],
  loading = false,
  error = "",
  manualNavigation = true,
  emptyMessage = "Преподаватель пока не назначил каталоги для этой группы.",

}: StudentGroupCatalogsViewProps) {
  const navigate = useNavigate()

  if (loading) {
    return <p className="text-sm text-gray-500 py-6">Загрузка заданий...</p>
  }
  if (error) {
    return <p className="text-sm text-red-300 py-6">{error}</p>
  }
  if (!catalogs.length) {
    return <p className="text-sm text-gray-500 py-6">{emptyMessage}</p>
  }

  return (
    <div className="space-y-6">
      {catalogs.map((catalog: unknown) => (
        <section
          key={catalog.catalog_id}
          className="rounded-xl border border-gray-800 bg-gray-900/50 overflow-hidden"
        >
          <div className="border-b border-gray-800 px-5 py-4">
            <h2 className="text-lg font-semibold text-teal-300">
              {catalog.catalog_title}
            </h2>
            {catalog.catalog_description && (
              <p className="text-sm text-gray-400 mt-1">{catalog.catalog_description}</p>
            )}
            {catalog.deadline_at && (
              <p className="text-xs text-amber-300 mt-2">
                Срок сдачи: {formatDateTime(catalog.deadline_at)}
              </p>
            )}
          </div>

          {catalog.tasks.length === 0 ? (
            <p className="px-5 py-4 text-sm text-gray-500">В каталоге пока нет заданий.</p>
          ) : (
            <ul className="divide-y divide-gray-800">
              {catalog.tasks.map((task: unknown) => {
                const meta = STATUS_META[task.status] ?? STATUS_META.not_started
                return (
                  <li
                    key={task.task_id}
                    className="flex flex-wrap items-center justify-between gap-3 px-5 py-4 hover:bg-gray-900/80"
                  >
                    <button
                      type="button"
                      onClick={() =>
                        navigate(`/tasks/${task.task_id}`, {
                          state: manualNavigation
                            ? {
                                navigationMode: "manual",
                                collectionId: catalog.catalog_id,
                              }
                            : { navigationMode: "adaptive", collectionId: null },
                        })
                      }
                      className="text-left text-white hover:text-teal-300 font-medium"
                    >
                      {task.title}
                    </button>
                    <span
                      className={`text-xs rounded border px-2.5 py-1 ${meta.className}`}
                    >
                      {meta.label}
                      {task.attempts > 0 && task.status !== "not_started"
                        ? ` · ${task.attempts} попыт.`
                        : ""}
                    </span>
                  </li>
                )
              })}
            </ul>
          )}
        </section>
      ))}
    </div>
  )
}
