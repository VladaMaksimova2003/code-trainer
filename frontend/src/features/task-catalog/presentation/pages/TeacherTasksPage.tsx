import { Link } from "react-router-dom"
import { useCallback, useEffect, useMemo, useState } from "react"

import {
  assignTaskToCatalog,
  deleteCatalogTask,
  listCatalogTasks,
  listMyCatalogs,
} from "@/features/task-catalog/infrastructure/catalogApi"
import CreateTaskModal from "@/features/task-catalog/presentation/components/CreateTaskModal"
import TeacherAppShell from "@/features/teacher/layout/TeacherAppShell"
import { teacherTaskEditPath } from "@/features/teacher/routing/teacherTaskEditPath"
import PageHeader from "@/features/student/layout/PageHeader"
import { Button, Card, Chip, Select } from "@/shared/ui"
import { toast } from "@/shared/ui/toast"

export default function TeacherTasksPage({ user = null, onSignOut = null }) {
  const [tasks, setTasks] = useState([])
  const [catalogs, setCatalogs] = useState([])
  const [filter, setFilter] = useState("all")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [assignTaskId, setAssignTaskId] = useState(null)
  const [assignCatalogId, setAssignCatalogId] = useState("")

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params =
        filter === "assigned"
          ? { assigned: true }
          : filter === "unassigned"
            ? { assigned: false }
            : {}
      const [taskList, catalogList] = await Promise.all([
        listCatalogTasks(params),
        listMyCatalogs(),
      ])
      setTasks(taskList)
      setCatalogs(catalogList)
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Ошибка загрузки")
    } finally {
      setLoading(false)
    }
  }, [filter])

  useEffect(() => {
    load()
  }, [load])

  const catalogNameById = useMemo(() => {
    const map = new Map()
    catalogs.forEach((c: unknown) => map.set(c.id, c.title))
    return map
  }, [catalogs])

  const handleDelete = async (taskId: unknown, title = "") => {
    if (!window.confirm(`Удалить задание «${title || taskId}»?`)) return
    try {
      const result = await deleteCatalogTask(taskId)
      if (result.action === "archived") {
        toast.push({ kind: "info", title: "Задание скрыто", body: title || String(taskId) })
      } else {
        toast.push({ kind: "lime", title: "Задание удалено", body: title || String(taskId) })
      }
      load()
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось удалить задание"
      toast.error("Ошибка", String(message))
    }
  }

  const handleAssign = async () => {
    if (!assignTaskId || !assignCatalogId) return
    await assignTaskToCatalog(Number(assignCatalogId), assignTaskId)
    setAssignTaskId(null)
    setAssignCatalogId("")
    load()
  }

  return (
    <TeacherAppShell user={user} onSignOut={onSignOut}>
      <PageHeader
        title="Мои задачи"
        subtitle="Создавайте, редактируйте и распределяйте задачи по каталогам."
        right={[
          <Link key="cabinet" to="/teacher/cabinet?tab=tasks" className="btn btn-ghost btn-sm">
            ← В кабинет
          </Link>,
          <Button key="create" type="button" onClick={() => setModalOpen(true)}>
            + Создать задачу
          </Button>,
        ]}
      />

      <div className="wrap" style={{ marginBottom: 14 }}>
        {[
          ["all", "Все"],
          ["assigned", "В каталогах"],
          ["unassigned", "Без каталога"],
        ].map(([value, label]) => (
          <Chip
            key={value}
            onClick={() => setFilter(value)}
            active={filter === value}
            tone="purple"
          >
            {label}
          </Chip>
        ))}
      </div>

      {error && (
        <div className="note err" style={{ marginBottom: 14, padding: "10px 12px" }}>
          {error}
        </div>
      )}

      {loading ? (
        <p className="muted">Загрузка…</p>
      ) : (
        <div className="grid" style={{ gap: 12 }}>
          {tasks.length === 0 && (
            <p className="text-sm text-ink-faint">Задач пока нет.</p>
          )}
          {tasks.map((task: unknown) => (
            <Card
              as="article"
              key={task.id}
              className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between"
            >
              <div>
                <h2 className="font-semibold text-ink">{task.title}</h2>
                <p className="line-clamp-2 text-sm text-ink-muted">{task.content}</p>
                <p className="mt-1 text-xs text-ink-faint">
                  Тип: {task.type_id}
                  {task.is_assigned && task.catalog_ids?.length > 0 && (
                    <>
                      {" · "}
                      Каталоги:{" "}
                      {task.catalog_ids
                        .map((id: unknown) => catalogNameById.get(id) || `#${id}`)
                        .join(", ")}
                    </>
                  )}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {!task.is_assigned && (
                  <Button
                    type="button"
                    onClick={() => setAssignTaskId(task.id)}
                    variant="ghost"
                    size="sm"
                  >
                    В каталог
                  </Button>
                )}
                <Button
                  as={Link}
                  to={teacherTaskEditPath(task.id)}
                  variant="ghost"
                  size="sm"
                >
                  Редактор
                </Button>
                <Button
                  type="button"
                  onClick={() => handleDelete(task.id, task.title)}
                  variant="danger"
                  size="sm"
                >
                  Удалить
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {assignTaskId != null && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-xl border border-border-strong bg-surface p-6 shadow-glow-purple">
            <h3 className="mb-3 text-lg font-semibold text-ink">Добавить в каталог</h3>
            <Select
              className="mb-4"
              value={assignCatalogId}
              onChange={(e: unknown) => setAssignCatalogId(e.target.value)}
            >
              <option value="">Выберите каталог</option>
              {catalogs.map((c: unknown) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </Select>
            <div className="flex justify-end gap-2">
              <Button type="button" onClick={() => setAssignTaskId(null)} variant="ghost" size="sm">
                Отмена
              </Button>
              <Button type="button" onClick={handleAssign} size="sm">
                Добавить
              </Button>
            </div>
          </div>
        </div>
      )}

      <CreateTaskModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreated={() => load()}
      />
    </TeacherAppShell>
  )
}
