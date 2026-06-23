import { useState } from "react"
import Modal from "@/features/student/layout/Modal"

interface TeacherCreateCatalogButtonProps {
  groups?: { id: number; name?: string }[]
  newCatalogTitle: string
  setNewCatalogTitle: (value: string) => void
  newCatalogDescription: string
  setNewCatalogDescription: (value: string) => void
  newCatalogPrivate: boolean
  setNewCatalogPrivate: (value: boolean) => void
  newCatalogGroupId: string
  setNewCatalogGroupId: (value: string) => void
  onCreateCatalog: (event: React.FormEvent) => Promise<void> | void
  className?: string
}

export default function TeacherCreateCatalogButton({
  groups = [],
  newCatalogTitle,
  setNewCatalogTitle,
  newCatalogDescription,
  setNewCatalogDescription,
  newCatalogPrivate,
  setNewCatalogPrivate,
  newCatalogGroupId,
  setNewCatalogGroupId,
  onCreateCatalog,
  className = "",
}: TeacherCreateCatalogButtonProps) {
  const [createOpen, setCreateOpen] = useState(false)

  const closeCreate = () => {
    setCreateOpen(false)
    setNewCatalogTitle("")
    setNewCatalogDescription("")
    setNewCatalogPrivate(false)
    setNewCatalogGroupId("")
  }

  const handleCreate = async (event: React.FormEvent) => {
    await onCreateCatalog?.(event)
    closeCreate()
  }

  return (
    <>
      <button
        type="button"
        className={`btn btn-secondary btn-sm ${className}`.trim()}
        onClick={() => setCreateOpen(true)}
      >
        + Новый каталог
      </button>

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
            onChange={(e) => setNewCatalogTitle(e.target.value)}
            required
          />
          <textarea
            className="textarea"
            placeholder="Описание (опционально)"
            value={newCatalogDescription}
            onChange={(e) => setNewCatalogDescription(e.target.value)}
            rows={3}
            style={{ minHeight: 76, resize: "vertical", fontFamily: "var(--font)" }}
          />
          <label className="row" style={{ gap: 8, fontSize: 13.5, cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={newCatalogPrivate}
              onChange={(e) => setNewCatalogPrivate(e.target.checked)}
            />
            Сделать каталог приватным
          </label>
          {newCatalogPrivate ? (
            <>
              <select
                className="select"
                value={newCatalogGroupId}
                onChange={(e) => setNewCatalogGroupId(e.target.value)}
              >
                <option value="">Только для меня</option>
                {groups.map((g) => (
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
    </>
  )
}
