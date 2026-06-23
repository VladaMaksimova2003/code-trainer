import { useEffect, useState } from "react"
import { toast } from "@/shared/ui/toast"
import {
  createTeacherCourse,
  updateTeacherCourse,
} from "@/features/task-catalog/infrastructure/catalogApi"

type TeacherPlatformCourseEditorModalProps = {
  open: boolean
  mode?: "create" | "edit"
  courseId?: number | null
  initial?: { title?: string; description?: string } | null
  onClose: () => void
  onSaved: () => void
}

export function TeacherPlatformCourseEditorModal({
  open,
  mode = "edit",
  courseId = null,
  initial,
  onClose,
  onSaved,
}: TeacherPlatformCourseEditorModalProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!open) return
    setTitle(initial?.title || "")
    setDescription(initial?.description || "")
  }, [open, initial])

  if (!open) return null

  const submit = async () => {
    const trimmedTitle = title.trim()
    if (!trimmedTitle) {
      toast.error("Ошибка", "Укажите название курса")
      return
    }
    setSaving(true)
    try {
      if (mode === "create") {
        await createTeacherCourse({
          title: trimmedTitle,
          description: description.trim(),
        })
        toast.push({ kind: "lime", title: "Курс создан" })
      } else if (courseId) {
        await updateTeacherCourse(courseId, {
          title: trimmedTitle,
          description: description.trim(),
        })
        toast.push({ kind: "lime", title: "Курс сохранён" })
      } else {
        toast.error("Ошибка", "Курс не выбран")
        return
      }
      onSaved()
      onClose()
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось сохранить курс"
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
        aria-labelledby="platform-course-editor-title"
        onClick={(event) => event.stopPropagation()}
      >
        <h3 id="platform-course-editor-title" style={{ marginTop: 0 }}>
          {mode === "create" ? "Новый курс" : "Настроить курс"}
        </h3>
        <p className="muted" style={{ marginTop: 0, fontSize: 13 }}>
          {mode === "create"
            ? "Задайте название и описание нового курса."
            : "Название и описание отображаются в кабинете и в разделе «Курсы»."}
        </p>
        <label className="tt-field">
          <span>Название</span>
          <input
            className="input"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Например: Базовый синтаксис через алгоритмы"
          />
        </label>
        <label className="tt-field">
          <span>Описание</span>
          <textarea
            className="input"
            rows={4}
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Кратко опишите курс для студентов"
          />
        </label>
        <div className="tt-modal-actions">
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose} disabled={saving}>
            Отмена
          </button>
          <button type="button" className="btn btn-primary btn-sm" onClick={() => void submit()} disabled={saving}>
            {saving ? "Сохранение…" : mode === "create" ? "Создать" : "Сохранить"}
          </button>
        </div>
      </div>
    </div>
  )
}
