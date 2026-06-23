// Textarea + «Отправить» для teacher review. Используется и для создания, и для редактирования.
import { useState } from "react"
import type { FormEvent } from "react"
import { createComment, updateComment } from "../../analytics/api/submissionCommentsApi"
import { toast } from "@/shared/ui/toast"

const MAX = 4096

interface CommentEditing {
  id: number | string
  body?: string
}

interface TeacherCommentComposerProps {
  submissionId: number | string
  editing?: CommentEditing | null
  onCreated?: (item: unknown) => void
  onUpdated?: (item: unknown) => void
  onCancel?: () => void
}

export default function TeacherCommentComposer({
  submissionId,
  editing = null,
  onCreated,
  onUpdated,
  onCancel,
}: TeacherCommentComposerProps) {
  const [body, setBody] = useState(editing?.body || "")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const isEdit = Boolean(editing)
  const trimmed = body.trim()
  const valid = trimmed.length >= 1 && trimmed.length <= MAX

  const submit = async (e?: FormEvent) => {
    e?.preventDefault()
    if (!valid || busy) return
    setBusy(true)
    setError(null)
    try {
      if (isEdit && editing) {
        const item = await updateComment(submissionId, editing.id, trimmed)
        onUpdated?.(item)
      } else {
        const item = await createComment(submissionId, trimmed)
        onCreated?.(item)
        setBody("")
        toast.success("Комментарий отправлен", "Студент получит уведомление с ссылкой на задание.")
      }
    } catch {
      setError("Не удалось сохранить. Попробуйте ещё раз.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className={isEdit ? "rounded-lg border border-purple/40 bg-surface-2 p-2.5" : ""}>
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key === "Enter") submit(e)
        }}
        rows={isEdit ? 3 : 2}
        maxLength={MAX}
        aria-label="Текст комментария"
        placeholder="Комментарий к решению студента…"
        className="w-full resize-y rounded-md border border-border bg-bg px-3 py-2 text-[13px] text-ink
                   placeholder:text-ink-faint focus:border-purple focus:outline-none focus:ring-2 focus:ring-purple/20"
      />
      {error && <p className="mt-1 text-[12px] text-danger">{error}</p>}
      <div className="mt-2 flex items-center justify-between">
        <span className="text-[11px] text-ink-faint">
          {trimmed.length}/{MAX} · ⌘/Ctrl+Enter
        </span>
        <div className="flex gap-2">
          {isEdit && (
            <button type="button" onClick={onCancel} className="btn btn-ghost btn-sm">
              Отмена
            </button>
          )}
          <button
            type="submit"
            disabled={!valid || busy}
            className="btn btn-sm bg-purple text-white hover:bg-purple/90 disabled:opacity-50"
          >
            {busy ? "Сохранение…" : isEdit ? "Сохранить" : "Отправить"}
          </button>
        </div>
      </div>
    </form>
  )
}
