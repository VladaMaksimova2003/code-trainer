interface StudentTeacherProgressPanelProps {
  catalogs?: unknown[]
  canManageAsTeacher?: boolean
}

import { useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import ProfileSectionTitle from "@/shared/ui/ProfileSectionTitle"
import StudentProgressTaskTable from "@/features/users/ui/StudentProgressTaskTable"

export default function StudentTeacherProgressPanel({

  catalogs = [],
  canManageAsTeacher = false,

}: StudentTeacherProgressPanelProps) {
  const navigate = useNavigate()
  const [catalogId, setCatalogId] = useState("")

  const catalogOptions = useMemo(
    () =>
      catalogs.map((cat: unknown) => ({
        id: String(cat.catalog_id),
        title: cat.catalog_title,
      })),
    [catalogs]
  )

  const taskRows = useMemo(() => {
    const rows = []
    for (const catalog of catalogs) {
      if (catalogId && String(catalog.catalog_id) !== catalogId) {
        continue
      }
      for (const task of catalog.tasks || []) {
        rows.push({
          id: task.task_id,
          title: task.title,
          type: task.type || task.task_type,
          task_type: task.task_type,
          difficulty: task.difficulty,
          language: task.language,
          solved: task.status === "solved",
          attempted: task.status === "in_progress",
          attempts: task.attempts ?? 0,
          last_activity_at: task.last_activity_at,
          catalog_id: catalog.catalog_id,
          catalog_title: catalog.catalog_title,
        })
      }
    }
    return rows
  }, [catalogs, catalogId])

  if (taskRows.length === 0 && catalogOptions.length === 0) {
    return null
  }

  const handleTaskClick = (taskId: unknown) => {
    if (canManageAsTeacher) {
      navigate(`/tasks/${taskId}`)
    }
  }

  return (
    <section>
      <ProfileSectionTitle>Прогресс по заданиям</ProfileSectionTitle>

      {catalogOptions.length > 0 ? (
        <div className="wrap" style={{ marginBottom: 14, gap: 8 }}>
          <span
            className={`chip${catalogId === "" ? " on pp" : ""}`}
            role="button"
            tabIndex={0}
            onClick={() => setCatalogId("")}
            onKeyDown={(e: unknown) => e.key === "Enter" && setCatalogId("")}
          >
            Все каталоги
          </span>
          {catalogOptions.map((cat: unknown) => (
            <span
              key={cat.id}
              className={`chip${catalogId === cat.id ? " on pp" : ""}`}
              role="button"
              tabIndex={0}
              onClick={() => setCatalogId(cat.id)}
              onKeyDown={(e: unknown) => e.key === "Enter" && setCatalogId(cat.id)}
            >
              {cat.title}
            </span>
          ))}
        </div>
      ) : null}

      <StudentProgressTaskTable
        tasks={taskRows}
        onTaskClick={canManageAsTeacher ? handleTaskClick : undefined}
        emptyText={
          catalogId
            ? "В этом каталоге нет назначенных задач."
            : "Пока нет задач в каталогах преподавателя."
        }
      />
    </section>
  )
}
