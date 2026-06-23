interface StudentCatalogTasksProgressProps {
  data: unknown
  loading: unknown
  error: unknown
  manualNavigation?: boolean
}

import { useNavigate } from "react-router-dom"
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

export default function StudentCatalogTasksProgress({

  data,
  loading,
  error,
  manualNavigation = false,

}: StudentCatalogTasksProgressProps) {
  const navigate = useNavigate()

  if (loading) {
    return <p className="text-xs text-slate-500 py-2">Загрузка заданий...</p>
  }
  if (error) {
    return <p className="text-sm text-red-300 py-2">{error}</p>
  }
  if (!data?.catalogs?.length) {
    return (
      <p className="text-xs text-slate-500 py-2">
        Нет каталогов или заданий для этого студента.
      </p>
    )
  }

  return (
    <div className="mt-3 space-y-4 border-t border-slate-800 pt-3">
      {data.catalogs.map((catalog: unknown) => (
        <div key={catalog.catalog_id} className="space-y-2">
          <h4 className="text-sm font-medium text-teal-300">{catalog.catalog_title}</h4>
          {catalog.tasks.length === 0 ? (
            <p className="text-xs text-slate-500">В каталоге нет заданий</p>
          ) : (
            <ul className="space-y-1.5">
              {catalog.tasks.map((task: unknown) => {
                const meta = STATUS_META[task.status] ?? STATUS_META.not_started
                return (
                  <li
                    key={task.task_id}
                    className="flex flex-wrap items-center justify-between gap-2 rounded border border-slate-800 bg-[#030712] px-3 py-2 text-sm"
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
                            : undefined,
                        })
                      }
                      className="text-left text-slate-200 hover:text-teal-300 truncate max-w-[70%]"
                    >
                      {task.title}
                    </button>
                    <span
                      className={`text-xs rounded border px-2 py-0.5 ${meta.className}`}
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
        </div>
      ))}
    </div>
  )
}
