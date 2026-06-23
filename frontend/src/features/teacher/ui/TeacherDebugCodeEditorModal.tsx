import { useEffect, useMemo, useState } from "react"
import Modal from "@/shared/ui/Modal"
import { fetchDebugCodes, saveDebugCodes } from "@/features/teacher/api/debugCodesApi"
import { getLanguageLabel } from "@/shared/config/languages"
import { toast } from "@/shared/ui/toast"

type Mode = "fixed" | "buggy"

type Props = {
  taskId: number | null
  mode: Mode | null
  onClose: () => void
}

export default function TeacherDebugCodeEditorModal({ taskId, mode, onClose }: Props) {
  const [languages, setLanguages] = useState<string[]>([])
  const [activeLanguage, setActiveLanguage] = useState("python")
  const [fixedCodes, setFixedCodes] = useState<Record<string, string>>({})
  const [buggyCodes, setBuggyCodes] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!taskId || !mode) return
    let cancelled = false
    setLoading(true)
    setError(null)
    fetchDebugCodes(taskId)
      .then((payload) => {
        if (cancelled) return
        const langs = payload.languages?.length ? payload.languages : ["python"]
        setLanguages(langs)
        setActiveLanguage(langs[0] ?? "python")
        setFixedCodes(payload.fixed_codes ?? {})
        setBuggyCodes(payload.buggy_codes ?? {})
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(
          (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            (err as Error)?.message ||
            "Не удалось загрузить код",
        )
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [taskId, mode])

  const title = mode === "fixed" ? "Правильный код (эталон)" : "Неправильный код (для ученика)"
  const codes = mode === "fixed" ? fixedCodes : buggyCodes
  const setCodes = mode === "fixed" ? setFixedCodes : setBuggyCodes

  const currentCode = useMemo(() => codes[activeLanguage] ?? "", [codes, activeLanguage])

  const handleSave = async () => {
    if (!taskId || !mode) return
    setSaving(true)
    setError(null)
    try {
      await saveDebugCodes(
        taskId,
        mode === "fixed" ? { fixed_codes: fixedCodes } : { buggy_codes: buggyCodes },
      )
      toast.success("Сохранено", title)
      onClose()
    } catch (err: unknown) {
      setError(
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          (err as Error)?.message ||
          "Не удалось сохранить",
      )
    } finally {
      setSaving(false)
    }
  }

  if (!taskId || !mode) return null

  return (
    <Modal open={Boolean(taskId && mode)} onClose={onClose} title={title}>
      {loading ? <p className="muted">Загрузка…</p> : null}
      {error ? (
        <p className="text-sm text-red-400" role="alert">
          {error}
        </p>
      ) : null}

      {!loading ? (
        <>
          <div className="mb-3 flex flex-wrap gap-1.5">
            {languages.map((lang) => (
              <button
                key={lang}
                type="button"
                className={`btn btn-sm ${activeLanguage === lang ? "btn-primary" : "btn-ghost"}`}
                onClick={() => setActiveLanguage(lang)}
              >
                {getLanguageLabel(lang) || lang}
              </button>
            ))}
          </div>

          <textarea
            className="input font-mono text-[13px] leading-relaxed"
            style={{ minHeight: 320, width: "100%", resize: "vertical" }}
            value={currentCode}
            onChange={(event) =>
              setCodes((prev) => ({ ...prev, [activeLanguage]: event.target.value }))
            }
            spellCheck={false}
          />

          <div className="mt-4 flex justify-end gap-2">
            <button type="button" className="btn btn-ghost btn-sm" onClick={onClose} disabled={saving}>
              Отмена
            </button>
            <button type="button" className="btn btn-primary btn-sm" onClick={() => void handleSave()} disabled={saving}>
              {saving ? "Сохранение…" : "Сохранить"}
            </button>
          </div>
        </>
      ) : null}
    </Modal>
  )
}
