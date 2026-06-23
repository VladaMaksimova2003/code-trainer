import { useEffect, useState } from "react"
import { getLearningPreferences, updateLearningPreferences } from "@/features/settings/api/settingsApi"
import Chip from "@/shared/ui/Chip"
import { getErrorMessage } from "@/shared/utils/errors"
import { toast } from "@/shared/ui/toast"

const CHIP_OPTIONS = [
  { value: "beginner", label: "Лёгкая" },
  { value: "intermediate", label: "Средняя" },
  { value: "advanced", label: "Сложная" },
]

export default function LearningTab() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [difficulty, setDifficulty] = useState("intermediate")
  const [studyPlace, setStudyPlace] = useState("")
  const [studyGroup, setStudyGroup] = useState("")
  const [error, setError] = useState("")

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      try {
        const data = await getLearningPreferences()
        if (!cancelled) {
          const d = data.preferred_difficulty || "intermediate"
          setDifficulty(CHIP_OPTIONS.some((o) => o.value === d) ? d : "intermediate")
          setStudyPlace(data.study_place || "")
          setStudyGroup(data.study_group || "")
        }
      } catch (err) {
        if (!cancelled) {
          setError(getErrorMessage(err, "Не удалось загрузить предпочтения"))
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError("")
    try {
      const current = await getLearningPreferences()
      await updateLearningPreferences({
        preferred_languages: current.preferred_languages || [],
        preferred_difficulty: difficulty,
        preferred_topics: current.preferred_topics || [],
        study_place: studyPlace.trim(),
        study_group: studyGroup.trim(),
      })
      toast.push({ kind: "lime", title: "Настройки обучения сохранены" })
    } catch (err) {
      setError(getErrorMessage(err, "Не удалось сохранить предпочтения"))
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <p className="muted">Загрузка…</p>
  }

  return (
    <>
      {error ? (
        <div className="toast err" style={{ marginBottom: 16, maxWidth: "none" }}>
          <div className="tt">{error}</div>
        </div>
      ) : null}

      <form className="card card-pad" style={{ maxWidth: 640 }} onSubmit={handleSubmit}>
        <b style={{ fontSize: 14, display: "block", marginBottom: 14 }}>Обучение</b>
        <p className="muted" style={{ fontSize: 13.5, margin: "0 0 18px" }}>
          Уровень сложности задач, которые вам будут рекомендоваться по умолчанию.
        </p>
        <label className="label">Стартовая сложность</label>
        <div className="wrap" style={{ marginBottom: 24 }}>
          {CHIP_OPTIONS.map((opt) => (
            <Chip
              key={opt.value}
              active={difficulty === opt.value}
              onClick={() => setDifficulty(opt.value)}
            >
              {opt.label}
            </Chip>
          ))}
        </div>

        <p className="muted" style={{ fontSize: 13.5, margin: "0 0 14px" }}>
          Место учёбы и учебная группа — преподаватель увидит их рядом с вашим именем в списках
          решений и прогресса.
        </p>
        <label className="label" htmlFor="study-place">
          Место учёбы
        </label>
        <input
          id="study-place"
          className="input"
          style={{ marginBottom: 14 }}
          value={studyPlace}
          onChange={(event) => setStudyPlace(event.target.value)}
          placeholder="Например: ИКНТ ПГНИУ"
          maxLength={255}
        />
        <label className="label" htmlFor="study-group">
          Учебная группа
        </label>
        <input
          id="study-group"
          className="input"
          style={{ marginBottom: 20 }}
          value={studyGroup}
          onChange={(event) => setStudyGroup(event.target.value)}
          placeholder="Например: ИВТ-41"
          maxLength={128}
        />

        <div className="row" style={{ justifyContent: "flex-end", gap: 10 }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "…" : "Сохранить"}
          </button>
        </div>
      </form>
    </>
  )
}
