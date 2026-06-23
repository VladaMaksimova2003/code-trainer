import { useEffect, useState } from "react"
import { toast } from "@/shared/ui/toast"
import {
  createCurriculumChapter,
  updateCurriculumChapter,
  type CurriculumChapterDto,
} from "@/features/task-catalog/infrastructure/catalogApi"

type ChapterEditorMode = "create" | "edit"

type TeacherChapterEditorModalProps = {
  open: boolean
  mode: ChapterEditorMode
  initial?: CurriculumChapterDto | null
  onClose: () => void
  onSaved: () => void
}

const LANGUAGE_OPTIONS = [
  { value: "python", label: "Python" },
  { value: "pascal", label: "Pascal" },
  { value: "cpp", label: "C++" },
  { value: "java", label: "Java" },
  { value: "csharp", label: "C#" },
]

export function TeacherChapterEditorModal({
  open,
  mode,
  initial,
  onClose,
  onSaved,
}: TeacherChapterEditorModalProps) {
  const [language, setLanguage] = useState("python")
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!open) return
    setLanguage(initial?.language || "python")
    setTitle(initial?.title || "")
    setDescription(initial?.description || "")
  }, [open, initial])

  if (!open) return null

  const submit = async () => {
    const trimmedTitle = title.trim()
    if (!trimmedTitle) {
      toast.error("Ошибка", "Укажите название главы")
      return
    }
    setSaving(true)
    try {
      if (mode === "create") {
        await createCurriculumChapter({
          language,
          title: trimmedTitle,
          description: description.trim(),
        })
        toast.push({ kind: "lime", title: "Глава создана" })
      } else if (initial?.chapter_key) {
        await updateCurriculumChapter(initial.chapter_key, {
          language: initial.language || language,
          title: trimmedTitle,
          description: description.trim(),
        })
        toast.push({ kind: "lime", title: "Глава сохранена" })
      }
      onSaved()
      onClose()
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось сохранить главу"
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
        aria-labelledby="chapter-editor-title"
        onClick={(event) => event.stopPropagation()}
      >
        <h3 id="chapter-editor-title" style={{ marginTop: 0 }}>
          {mode === "create" ? "Новая глава" : "Редактировать главу"}
        </h3>
        {mode === "create" ? (
          <label className="tt-field">
            <span>Язык курса</span>
            <select
              className="input select"
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
              disabled={Boolean(initial?.language)}
            >
              {LANGUAGE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        ) : (
          <p className="muted" style={{ marginTop: 0, fontSize: 13 }}>
            Язык: {LANGUAGE_OPTIONS.find((opt) => opt.value === (initial?.language || language))?.label || initial?.language}
          </p>
        )}
        <label className="tt-field">
          <span>Название</span>
          <input
            className="input"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Например: Основы алгоритмов"
          />
        </label>
        <label className="tt-field">
          <span>Описание</span>
          <textarea
            className="input"
            rows={4}
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Кратко опишите, что студент изучит в этой главе"
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
