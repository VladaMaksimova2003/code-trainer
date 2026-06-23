interface TeacherToxicCatalogsPanelProps {
  catalogs?: unknown[]
  canManage?: boolean
  groups?: unknown[]
  loading?: boolean
  newCatalogTitle: unknown
  setNewCatalogTitle: unknown
  newCatalogDescription: unknown
  setNewCatalogDescription: unknown
  newCatalogPrivate: unknown
  setNewCatalogPrivate: unknown
  newCatalogGroupId: unknown
  setNewCatalogGroupId: unknown
  onCreateCatalog: (...args: unknown[]) => unknown
  onAssign: (...args: unknown[]) => unknown
  onDelete: (...args: unknown[]) => unknown
  /** На вкладке «Мои задачи» — только создание каталога, без карточек */
  embedded?: boolean
}

import { useNavigate } from "react-router-dom"
import { useState } from "react"
import Modal from "@/features/student/layout/Modal"

function catalogInitials(title: unknown) {
  const parts = String(title || "")
    .trim()
    .split(/[\s·]+/)
    .filter(Boolean)
  if (parts.length >= 2) {
    return parts
      .slice(0, 2)
      .map((p: unknown) => p[0])
      .join("")
      .slice(0, 2)
      .toUpperCase()
  }
  return (parts[0] || "?").slice(0, 2).toUpperCase()
}

function taskCountLabel(count: unknown) {
  const n = Number(count) || 0
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod100 >= 11 && mod100 <= 14) return `${n} задач`
  if (mod10 === 1) return `${n} задача`
  if (mod10 >= 2 && mod10 <= 4) return `${n} задачи`
  return `${n} задач`
}

function groupAssignmentLabel(catalog, groups) {
  if (catalog.group_id == null) return "Не назначен ни одной группе"
  const group = groups.find((g: unknown) => g.id === catalog.group_id)
  if (group?.name) return `Назначен группе «${group.name}»`
  return "Назначен 1 группе(ам)"
}

export default function TeacherToxicCatalogsPanel({

  catalogs = [],
  canManage = false,
  groups = [],
  loading = false,
  newCatalogTitle,
  setNewCatalogTitle,
  newCatalogDescription,
  setNewCatalogDescription,
  newCatalogPrivate,
  setNewCatalogPrivate,
  newCatalogGroupId,
  setNewCatalogGroupId,
  onCreateCatalog,
  onAssign,
  onDelete,
  embedded = false,

}: TeacherToxicCatalogsPanelProps) {
  const navigate = useNavigate()
  const [createOpen, setCreateOpen] = useState(false)

  const openCreate = () => setCreateOpen(true)
  const closeCreate = () => {
    setCreateOpen(false)
    setNewCatalogTitle("")
    setNewCatalogDescription("")
    setNewCatalogPrivate(false)
    setNewCatalogGroupId("")
  }

  const handleCreate = async (event: unknown) => {
    await onCreateCatalog?.(event)
    closeCreate()
  }

  const stop = (event: unknown) => event.stopPropagation()
  if (!embedded && !canManage && !loading && catalogs.length === 0) {
    return null
  }
  if (embedded && !canManage) {
    return null
  }

  const createCard = canManage ? (
    <div
      className="course-card course-card--add"
      style={{ borderStyle: "dashed" }}
      role="button"
      tabIndex={0}
      onClick={openCreate}
      onKeyDown={(e: unknown) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          openCreate()
        }
      }}
    >
      <div className="catalog-add-inner">
        <div style={{ fontSize: 28, color: "var(--text-3)" }}>+</div>
        <span className="muted" style={{ fontSize: 13.5 }}>
          Новый каталог
        </span>
      </div>
    </div>
  ) : null

  return (
    <div className={`teacher-catalogs-panel${embedded ? " teacher-catalogs-panel--embedded" : ""}`}>
      {loading && !embedded ? (
        <p className="muted">Загрузка каталогов…</p>
      ) : embedded ? (
        createCard ? <div className="tt-catalog-create-row">{createCard}</div> : null
      ) : (
        <div className="cards3 cards3--catalogs">
          {catalogs.map((catalog: unknown) => (
            <div key={catalog.id} className="course-card pp course-card--actions course-card--catalog">
              <div className="between">
                <div className="ico">{catalogInitials(catalog.title)}</div>
                <span className="badge badge-purple">{taskCountLabel(catalog.task_count)}</span>
              </div>
              <b className="catalog-card-title">{catalog.title}</b>
              <p className="muted catalog-card-meta">{groupAssignmentLabel(catalog, groups)}</p>
              <div className="catalog-card-actions">
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => navigate(`/teacher/catalogs/${catalog.id}`)}
                >
                  Открыть
                </button>
                {canManage ? (
                  <>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={(e: unknown) => {
                        stop(e)
                        onAssign?.(catalog)
                      }}
                    >
                      Назначить группе
                    </button>
                    <button
                      type="button"
                      className="btn btn-danger btn-sm btn-icon"
                      aria-label="Удалить каталог"
                      onClick={(e: unknown) => {
                        stop(e)
                        onDelete?.(catalog)
                      }}
                    >
                      ✕
                    </button>
                  </>
                ) : null}
              </div>
            </div>
          ))}
          {createCard}
        </div>
      )}

      <Modal
        open={createOpen}
        onClose={closeCreate}
        title="Новый каталог"
        footer={
          <>
            <button type="button" className="btn btn-ghost btn-sm" onClick={closeCreate}>
              Отмена
            </button>
            <button type="submit" form="create-catalog-form" className="btn btn-primary btn-sm">
              Создать каталог
            </button>
          </>
        }
      >
        <form id="create-catalog-form" className="grid" style={{ gap: 12 }} onSubmit={handleCreate}>
          <input
            className="input"
            placeholder="Название"
            value={newCatalogTitle}
            onChange={(e: unknown) => setNewCatalogTitle(e.target.value)}
            required
          />
          <textarea
            className="textarea"
            placeholder="Описание (опционально)"
            value={newCatalogDescription}
            onChange={(e: unknown) => setNewCatalogDescription(e.target.value)}
            rows={3}
            style={{ minHeight: 76, resize: "vertical", fontFamily: "var(--font)" }}
          />
          <label className="row" style={{ gap: 8, fontSize: 13.5, cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={newCatalogPrivate}
              onChange={(e: unknown) => setNewCatalogPrivate(e.target.checked)}
            />
            Сделать каталог приватным
          </label>
          {newCatalogPrivate ? (
            <>
              <select
                className="select"
                value={newCatalogGroupId}
                onChange={(e: unknown) => setNewCatalogGroupId(e.target.value)}
              >
                <option value="">Только для меня</option>
                {groups.map((g: unknown) => (
                  <option key={g.id} value={g.id}>
                    {g.name}
                  </option>
                ))}
              </select>
              <p className="mut3" style={{ fontSize: 12 }}>
                Если выбрать группу, задачи из каталога будут видны студентам, которые вступили в неё по
                инвайт-коду.
              </p>
            </>
          ) : null}
        </form>
      </Modal>
    </div>
  )
}
