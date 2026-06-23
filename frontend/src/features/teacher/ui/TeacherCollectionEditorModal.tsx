import { useEffect, useState } from "react"
import { toast } from "@/shared/ui/toast"
import {
  updateCollectionMeta,
  type CollectionMetaDto,
} from "@/features/task-catalog/infrastructure/catalogApi"

type TeacherCollectionEditorModalProps = {
  open: boolean
  initial?: CollectionMetaDto | null
  onClose: () => void
  onSaved: () => void
}

export function TeacherCollectionEditorModal({
  open,
  initial,
  onClose,
  onSaved,
}: TeacherCollectionEditorModalProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!open) return
    setTitle(initial?.title || "")
    setDescription(initial?.description || "")
  }, [open, initial])

  if (!open || !initial?.language) return null

  const submit = async () => {
    const trimmedTitle = title.trim()
    if (!trimmedTitle) {
      toast.error("Ошибка", "Укажите название сборника")
      return
    }
    setSaving(true)
    try {
      await updateCollectionMeta(initial.language, {
        title: trimmedTitle,
        description: description.trim(),
      })
      toast.push({ kind: "lime", title: "Сборник сохранён" })
      onSaved()
      onClose()
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось сохранить сборник"
      toast.error("Ошибка", String(message))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="tt-modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="tt-modal card card-pad"
        role="dialog"
        aria-modal="true"
        aria-labelledby="collection-editor-title"
        onClick={(event) => event.stopPropagation()}
      >
        <h3 id="collection-editor-title" style={{ marginTop: 0 }}>
          Редактировать сборник
        </h3>
        <p className="muted" style={{ marginTop: 0, fontSize: 13 }}>
          Язык: {initial.registry_title || initial.language}
        </p>
        <label className="tt-field">
          <span>Название</span>
          <input
            className="input"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Например: Python"
          />
        </label>
        <label className="tt-field">
          <span>Описание</span>
          <textarea
            className="input"
            rows={4}
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Кратко опишите содержание трека для студентов"
          />
        </label>
        <div className="tt-modal-actions">
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose} disabled={saving}>
            Отмена
          </button>
          <button type="button" className="btn btn-primary btn-sm" onClick={() => void submit()} disabled={saving}>
            {saving ? "Сохранение…" : "Сохранить"}
          </button>
        </div>
      </div>
    </div>
  )
}
