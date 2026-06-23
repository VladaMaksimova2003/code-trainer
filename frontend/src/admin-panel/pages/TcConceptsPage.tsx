import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useOutletContext } from "react-router-dom"
import {
  fetchAdminTcConcept,
  fetchAdminTcConcepts,
  patchAdminTcConcept,
} from "@/admin-panel/api/admin"
import { buildTcConceptsSubtitle } from "@/admin-panel/config/tcConceptsMeta"
import { useAsyncResource } from "@/admin-panel/hooks/useAsyncResource"
import { ApSpinner, ApAlert, ApEmptyState } from "@/admin-panel/components/ui/ApFeedback"
import { toast } from "@/shared/ui/toast"

const LANGUAGES = ["pascal", "python", "cpp", "csharp", "java"]
const LANG_LABELS = {
  pascal: "Pascal",
  python: "Python",
  cpp: "C++",
  csharp: "C#",
  java: "Java",
}

function makeEditState(concept) {
  const examples = {}
  for (const lang of LANGUAGES) {
    examples[lang] = (concept.examples_by_language?.[lang] ?? []).map((item) => ({
      title: item.title ?? "",
      code: item.code ?? "",
    }))
  }
  return {
    name_ru: concept.name_ru ?? "",
    description_ru: concept.description_ru ?? "",
    examples_by_language: examples,
  }
}

function isDraftDirty(concept, draft) {
  if (!concept || !draft) return false
  return JSON.stringify(makeEditState(concept)) !== JSON.stringify(draft)
}

export default function TcConceptsPage() {
  const { setAdminPageSubtitle } = useOutletContext() || {}
  const [search, setSearch] = useState("")
  const [selId, setSelId] = useState(null)
  const [draft, setDraft] = useState(null)
  const [activeLang, setActiveLang] = useState("pascal")
  const [saving, setSaving] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailsById, setDetailsById] = useState({})
  const loadRequestRef = useRef(0)

  const { data, loading, error, setData } = useAsyncResource(
    () => fetchAdminTcConcepts(),
    [],
  )

  useEffect(() => {
    if (!setAdminPageSubtitle) return undefined
    if (data?.length) {
      setAdminPageSubtitle(buildTcConceptsSubtitle(data.length))
    } else {
      setAdminPageSubtitle(null)
    }
    return () => setAdminPageSubtitle(null)
  }, [data?.length, setAdminPageSubtitle])

  const selectedSummary = useMemo(
    () => (data ?? []).find((concept) => concept.id === selId) ?? null,
    [data, selId],
  )

  const selectedDetail = selId ? detailsById[selId] ?? null : null

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return (data ?? []).filter((concept) => {
      if (!q) return true
      return (
        (concept.name_ru ?? "").toLowerCase().includes(q) ||
        concept.id.toLowerCase().includes(q) ||
        (concept.description_ru ?? "").toLowerCase().includes(q)
      )
    })
  }, [data, search])

  const dirty = isDraftDirty(selectedDetail, draft)
  const activeExamples = draft?.examples_by_language?.[activeLang] ?? []

  const loadConceptDetail = useCallback(async (conceptId, { force = false } = {}) => {
    if (!conceptId) return null
    if (!force && detailsById[conceptId]) {
      return detailsById[conceptId]
    }

    const requestId = ++loadRequestRef.current
    setDetailLoading(true)
    try {
      const full = await fetchAdminTcConcept(conceptId)
      if (requestId !== loadRequestRef.current) return full
      setDetailsById((prev) => ({ ...prev, [conceptId]: full }))
      return full
    } finally {
      if (requestId === loadRequestRef.current) {
        setDetailLoading(false)
      }
    }
  }, [detailsById])

  const openConcept = useCallback(
    async (concept) => {
      setSelId(concept.id)
      setActiveLang("pascal")
      const cached = detailsById[concept.id]
      if (cached) {
        setDraft(makeEditState(cached))
        return
      }
      setDraft(null)
      try {
        const full = await loadConceptDetail(concept.id)
        if (full) setDraft(makeEditState(full))
      } catch (err) {
        toast.error(
          "Ошибка",
          err?.response?.data?.detail || err?.message || "Не удалось загрузить концепцию",
        )
      }
    },
    [detailsById, loadConceptDetail],
  )

  useEffect(() => {
    if (!data?.length || selId != null) return
    void openConcept(data[0])
  }, [data, selId, openConcept])

  const setField = (field, value) =>
    setDraft((prev) => (prev ? { ...prev, [field]: value } : prev))

  const setExampleField = (lang, index, field, value) => {
    setDraft((prev) => {
      if (!prev) return prev
      const nextExamples = [...(prev.examples_by_language[lang] ?? [])]
      nextExamples[index] = { ...nextExamples[index], [field]: value }
      return {
        ...prev,
        examples_by_language: {
          ...prev.examples_by_language,
          [lang]: nextExamples,
        },
      }
    })
  }

  const handleCancel = () => {
    if (selectedDetail) setDraft(makeEditState(selectedDetail))
  }

  const handleSave = async () => {
    if (!selectedDetail || !draft || !dirty || !selId) return
    setSaving(true)
    try {
      const saved = await patchAdminTcConcept(selId, {
        name_ru: draft.name_ru,
        description_ru: draft.description_ru,
        examples_by_language: draft.examples_by_language,
      })
      setDetailsById((prev) => ({ ...prev, [selId]: saved }))
      setData((prev) =>
        (prev ?? []).map((item) =>
          item.id === selId
            ? {
                ...item,
                name_ru: saved.name_ru,
                description_ru: saved.description_ru,
                has_overrides: true,
              }
            : item,
        ),
      )
      toast.success("Концепция сохранена", draft.name_ru)
    } catch (err) {
      toast.error("Ошибка", err?.response?.data?.detail || err?.message || "Не удалось сохранить")
    } finally {
      setSaving(false)
    }
  }

  const listReady = Boolean(data?.length)

  return (
    <>
      <ApAlert message={error} />

      <div className="tc-toolbar">
        <input
          className="ap-input"
          style={{ maxWidth: 340, height: 38 }}
          placeholder="Поиск концепции…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading && !listReady ? (
        <ApSpinner />
      ) : !listReady ? (
        <ApEmptyState
          icon="📘"
          title="Концепции не найдены"
          text="Проверьте tc_display_registry.json и доступ к API /admin/tc-concepts."
        />
      ) : (
        <div className="ap-split">
          <div className="tc-list">
            {filtered.length === 0 ? (
              <p className="ap-muted" style={{ fontSize: 13, padding: "20px 4px" }}>
                Ничего не найдено
              </p>
            ) : (
              filtered.map((concept) => (
                <button
                  key={concept.id}
                  type="button"
                  className={`tc-item${concept.id === selId ? " on" : ""}`}
                  onClick={() => void openConcept(concept)}
                >
                  <span
                    className={`tc-item-dot${concept.has_overrides ? " changed" : ""}`}
                  />
                  <span className="tc-item-nm">{concept.name_ru}</span>
                  <span className="tc-item-id ap-mono">{concept.id}</span>
                </button>
              ))
            )}
          </div>

          <div className="ap-editor" style={{ paddingTop: 2 }}>
            {!selId || !selectedSummary ? (
              <ApEmptyState
                icon="📘"
                title="Выберите концепцию"
                text="Слева — список конструкций."
              />
            ) : detailLoading && !draft ? (
              <div style={{ padding: "24px 0" }}>
                <ApSpinner />
                <p className="ap-muted" style={{ fontSize: 13, marginTop: 12 }}>
                  Загрузка примеров…
                </p>
              </div>
            ) : !draft ? (
              <ApEmptyState
                icon="📘"
                title="Не удалось открыть концепцию"
                text="Попробуйте выбрать другую или обновите страницу."
              />
            ) : (
              <>
                <div className="ap-row" style={{ gap: 10, marginBottom: 18 }}>
                  <b style={{ fontSize: 18 }}>{draft.name_ru || selectedSummary.name_ru}</b>
                  <span className="ap-mono ap-muted" style={{ fontSize: 12 }}>
                    {selectedSummary.id}
                  </span>
                  {selectedSummary.has_overrides && (
                    <span style={{ fontSize: 12, color: "var(--warning)" }}>· изменена</span>
                  )}
                </div>

                <div className="ap-field">
                  <label className="ap-label">Название</label>
                  <input
                    className="ap-input"
                    value={draft.name_ru}
                    onChange={(e) => setField("name_ru", e.target.value)}
                  />
                </div>

                <div className="ap-field">
                  <label className="ap-label">Описание</label>
                  <textarea
                    className="ap-input"
                    rows={4}
                    style={{ resize: "vertical", minHeight: 84 }}
                    value={draft.description_ru}
                    onChange={(e) => setField("description_ru", e.target.value)}
                  />
                </div>

                <div className="eyebrow" style={{ marginTop: 6 }}>
                  Примеры по языкам
                </div>
                <div className="tabbar" style={{ marginBottom: 16 }}>
                  {LANGUAGES.map((lang) => (
                    <button
                      key={lang}
                      type="button"
                      className={activeLang === lang ? "on pp" : ""}
                      onClick={() => setActiveLang(lang)}
                    >
                      {LANG_LABELS[lang]}
                    </button>
                  ))}
                </div>

                {activeExamples.length === 0 ? (
                  <p className="ap-muted" style={{ fontSize: 13, margin: 0 }}>
                    Для языка {LANG_LABELS[activeLang]} примеров пока нет.
                  </p>
                ) : (
                  activeExamples.map((example, index) => (
                    <div key={`${activeLang}-${index}`} style={{ marginBottom: 18 }}>
                      <input
                        className="ap-input"
                        style={{ marginBottom: 8, fontSize: 13 }}
                        value={example.title}
                        onChange={(e) =>
                          setExampleField(activeLang, index, "title", e.target.value)
                        }
                        placeholder="Заголовок примера"
                      />
                      <div className="ap-code">
                        <textarea
                          spellCheck={false}
                          value={example.code}
                          onChange={(e) =>
                            setExampleField(activeLang, index, "code", e.target.value)
                          }
                        />
                      </div>
                    </div>
                  ))
                )}

                <div className="ap-editor-foot">
                  {dirty ? (
                    <span className="ap-dirty">
                      <span className="d" />
                      Несохранённые изменения
                    </span>
                  ) : (
                    <span />
                  )}
                  <div className="ap-row" style={{ gap: 10 }}>
                    <button
                      type="button"
                      className="ap-btn ap-btn-ghost"
                      onClick={handleCancel}
                      disabled={!dirty || saving}
                    >
                      Отмена
                    </button>
                    <button
                      type="button"
                      className="ap-btn ap-btn-primary"
                      onClick={handleSave}
                      disabled={!dirty || saving}
                    >
                      {saving ? "Сохранение…" : "Сохранить"}
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  )
}
