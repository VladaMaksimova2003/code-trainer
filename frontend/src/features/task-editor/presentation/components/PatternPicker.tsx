import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { ChevronDownIcon, XMarkIcon } from "@heroicons/react/24/outline"
import type { Pattern, TaskDraft } from "@/features/task-editor/domain/entities"
import { detectExpectedConcepts } from "@/features/task-editor/application/use-cases/detectExpectedConcepts"
import {
  collectLanguageCodeSamples,
  conceptCardFromCatalog,
  getSelectedConceptIdsForLanguage,
  listConceptEditorLanguages,
  mapConceptIdsToPatterns,
  mergeConceptIdsForLanguage,
  patternLabel,
  setSelectedConceptIdsForLanguage,
} from "@/features/task-editor/domain/expectedConceptPatterns"
import ConceptPopover from "@/widgets/task-workspace/ConceptPopover"
import {
  editorInputClass,
  editorLabelClass,
  patternChipClass,
  patternChipLabelClass,
  patternChipListClass,
  patternChipRemoveBtnClass,
  patternDropdownDoneBtn,
  patternDropdownPanelClass,
  outlineMutedBtn,
  segmentToggleLight,
} from "@/features/task-editor/presentation/components/plaqueStyles"

type Props = {
  catalog: Pattern[]
  draft: TaskDraft
  onPatch: (patch: Partial<TaskDraft>) => void
  isLoading?: boolean
  getLanguageLabel: (languageId: string) => string
}

export function PatternPicker({
  catalog,
  draft,
  onPatch,
  isLoading,
  getLanguageLabel,
}: Props) {
  const languages = useMemo(() => listConceptEditorLanguages(draft), [draft])
  const [activeLanguage, setActiveLanguage] = useState(
    () => languages[0] ?? draft.languages[0] ?? draft.code.language ?? "pascal",
  )

  useEffect(() => {
    if (!languages.includes(activeLanguage) && languages[0]) {
      setActiveLanguage(languages[0])
    }
  }, [languages, activeLanguage])

  const selectedIds = getSelectedConceptIdsForLanguage(draft, activeLanguage)
  const selectedPatterns = mapConceptIdsToPatterns(catalog, selectedIds)

  const patchLanguageIds = useCallback(
    (ids: string[]) => {
      const byLanguage = setSelectedConceptIdsForLanguage(draft, activeLanguage, ids)
      onPatch({
        selectedPatternsByLanguage: byLanguage,
        selectedPatterns: mapConceptIdsToPatterns(
          catalog,
          byLanguage[activeLanguage] ?? ids,
        ),
      })
    },
    [activeLanguage, catalog, draft, onPatch],
  )

  const togglePattern = (p: Pattern) => {
    const id = String(p.id)
    if (selectedIds.includes(id)) {
      patchLanguageIds(selectedIds.filter((x) => x !== id))
    } else {
      patchLanguageIds([...selectedIds, id])
    }
  }

  const removePattern = (id: string) => {
    patchLanguageIds(selectedIds.filter((x) => x !== id))
  }

  const removePatternForLanguage = (language: string, id: string) => {
    const lang = language.toLowerCase()
    const current = getSelectedConceptIdsForLanguage(draft, lang)
    const byLanguageNext = setSelectedConceptIdsForLanguage(
      draft,
      lang,
      current.filter((item) => item !== id),
    )
    onPatch({
      selectedPatternsByLanguage: byLanguageNext,
      selectedPatterns:
        lang === activeLanguage
          ? mapConceptIdsToPatterns(catalog, byLanguageNext[lang] ?? [])
          : draft.selectedPatterns,
    })
  }

  const addPatternForLanguage = (language: string, id: string) => {
    const lang = language.toLowerCase()
    const current = getSelectedConceptIdsForLanguage(draft, lang)
    const byLanguageNext = setSelectedConceptIdsForLanguage(
      draft,
      lang,
      mergeConceptIdsForLanguage(current, [id]),
    )
    onPatch({
      selectedPatternsByLanguage: byLanguageNext,
      selectedPatterns:
        lang === activeLanguage
          ? mapConceptIdsToPatterns(catalog, byLanguageNext[lang] ?? [])
          : draft.selectedPatterns,
    })
  }

  const [open, setOpen] = useState(false)
  const [analysisOpen, setAnalysisOpen] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [analyzeError, setAnalyzeError] = useState<string | null>(null)
  const [byLanguage, setByLanguage] = useState<
    Record<string, Array<{ id: string; label: string }>>
  >({})
  const [popoverConceptId, setPopoverConceptId] = useState<string | null>(null)
  const [popoverLanguage, setPopoverLanguage] = useState<string>(activeLanguage)
  const [popoverAnchor, setPopoverAnchor] = useState<DOMRect | null>(null)
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const onDoc = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", onDoc)
    return () => document.removeEventListener("mousedown", onDoc)
  }, [open])

  const handleAnalyze = async () => {
    const samples = collectLanguageCodeSamples(draft)
    if (samples.length === 0) {
      setAnalyzeError("Добавьте эталонный код хотя бы для одного языка")
      setAnalysisOpen(true)
      return
    }

    setAnalyzing(true)
    setAnalyzeError(null)
    setAnalysisOpen(true)
    try {
      const result = await detectExpectedConcepts(samples)
      setByLanguage(result.byLanguage)
      if (Object.keys(result.byLanguage).length === 0) {
        setAnalyzeError("Концепции в коде не найдены")
      }
    } catch (err) {
      setAnalyzeError(err instanceof Error ? err.message : "Не удалось проанализировать код")
      setByLanguage({})
    } finally {
      setAnalyzing(false)
    }
  }

  const applyDetectedForLanguage = (language: string) => {
    const detected = byLanguage[language]?.map((item) => item.id) ?? []
    if (detected.length === 0) return
    const lang = language.toLowerCase()
    const current = getSelectedConceptIdsForLanguage(draft, lang)
    const byLanguageNext = setSelectedConceptIdsForLanguage(
      draft,
      lang,
      mergeConceptIdsForLanguage(current, detected),
    )
    onPatch({
      selectedPatternsByLanguage: byLanguageNext,
      selectedPatterns:
        lang === activeLanguage
          ? mapConceptIdsToPatterns(catalog, byLanguageNext[lang] ?? [])
          : draft.selectedPatterns,
    })
  }

  const openConceptHint = (
    conceptId: string,
    element: HTMLElement,
    language: string = activeLanguage,
  ) => {
    const lang = String(language || activeLanguage).toLowerCase()
    if (popoverConceptId === conceptId && popoverLanguage === lang) {
      setPopoverConceptId(null)
      setPopoverAnchor(null)
      return
    }
    setPopoverConceptId(conceptId)
    setPopoverLanguage(lang)
    setPopoverAnchor(element.getBoundingClientRect())
  }

  const renderSelectedConceptChip = (concept: { id: string; label: string }) => (
    <span key={concept.id} className={patternChipClass}>
      <button
        type="button"
        className={patternChipLabelClass}
        onClick={(event) => openConceptHint(concept.id, event.currentTarget, activeLanguage)}
      >
        {concept.label}
      </button>
      <button
        type="button"
        onClick={() => removePattern(concept.id)}
        className={patternChipRemoveBtnClass}
        aria-label={`Убрать ${concept.label}`}
      >
        <XMarkIcon className="h-4 w-4" strokeWidth={2} />
      </button>
    </span>
  )

  const popoverCard = popoverConceptId
    ? conceptCardFromCatalog(catalog, popoverConceptId)
    : null

  if (isLoading) {
    return <p className="text-xs text-ink-faint">Загрузка концепций…</p>
  }

  if (catalog.length === 0) {
    return <p className="text-xs text-ink-faint">Концепции недоступны</p>
  }

  const triggerLabel =
    selectedIds.length === 0
      ? "Концепции"
      : `Концепции · ${selectedIds.length} (${getLanguageLabel(activeLanguage)})`

  return (
    <div ref={rootRef} className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className={editorLabelClass}>Обязательные концепции</span>
        <button
          type="button"
          className={outlineMutedBtn()}
          disabled={analyzing}
          onClick={() => void handleAnalyze()}
        >
          {analyzing ? "Анализ…" : "Проанализировать код"}
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {languages.map((lang) => (
          <button
            key={lang}
            type="button"
            className={segmentToggleLight(activeLanguage === lang)}
            onClick={() => setActiveLanguage(lang)}
          >
            {getLanguageLabel(lang)}
            {(draft.selectedPatternsByLanguage?.[lang]?.length ?? 0) > 0
              ? ` · ${draft.selectedPatternsByLanguage?.[lang]?.length}`
              : ""}
          </button>
        ))}
      </div>

      <div className="relative">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className={`${editorInputClass} flex items-center justify-between gap-2 text-left font-medium`}
          aria-expanded={open}
        >
          <span>{triggerLabel}</span>
          <ChevronDownIcon
            className={`h-4 w-4 shrink-0 text-ink-faint transition-transform ${open ? "rotate-180" : ""}`}
          />
        </button>

        {open && (
          <div className={patternDropdownPanelClass}>
            <ul className="max-h-56 overflow-y-auto overscroll-contain py-1 scrollbar-dark">
              {catalog.map((p) => {
                const id = String(p.id)
                const checked = selectedIds.includes(id)
                return (
                  <li key={p.id}>
                    <label className="flex cursor-pointer items-start gap-3 px-3 py-2 transition-colors hover:bg-surface-2">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => togglePattern(p)}
                        className="mt-0.5 h-4 w-4 shrink-0 rounded border-border-strong bg-bg-2 accent-lime focus:ring-lime/20"
                      />
                      <button
                        type="button"
                        className="text-left text-sm leading-snug hover:text-lime"
                        onClick={(event) => {
                          event.preventDefault()
                          openConceptHint(id, event.currentTarget, activeLanguage)
                        }}
                      >
                        {p.label}
                      </button>
                    </label>
                  </li>
                )
              })}
            </ul>
            <div className="border-t border-border px-3 py-2">
              <button
                type="button"
                className={patternDropdownDoneBtn()}
                onClick={() => setOpen(false)}
              >
                Готово
              </button>
            </div>
          </div>
        )}
      </div>

      {analysisOpen && (
        <div className="rounded-lg border border-border bg-surface-2/80 p-3">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm font-medium text-ink">Найденные концепции по языкам</p>
            <button
              type="button"
              className="text-xs text-ink-faint hover:text-ink"
              onClick={() => setAnalysisOpen(false)}
            >
              Скрыть
            </button>
          </div>

          {analyzeError && <p className="mb-2 text-xs text-danger">{analyzeError}</p>}

          {Object.entries(byLanguage).map(([language, concepts]) => (
            <div key={language} className="mb-3 last:mb-0">
              <div className="mb-1.5 flex flex-wrap items-center justify-between gap-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-ink-faint">
                  {getLanguageLabel(language)}
                </p>
                <button
                  type="button"
                  className={outlineMutedBtn()}
                  disabled={concepts.length === 0}
                  onClick={() => applyDetectedForLanguage(language)}
                >
                  Добавить для {getLanguageLabel(language)}
                </button>
              </div>
              {concepts.length === 0 ? (
                <p className="text-xs text-ink-faint">Ничего не найдено</p>
              ) : (
                <div className="flex flex-wrap gap-1.5">
                  {concepts.map((concept) => {
                    const active = getSelectedConceptIdsForLanguage(draft, language).includes(
                      concept.id,
                    )
                    if (active) {
                      return (
                        <span key={`${language}-${concept.id}`} className={patternChipClass}>
                          <button
                            type="button"
                            className={patternChipLabelClass}
                            onClick={(event) =>
                              openConceptHint(concept.id, event.currentTarget, language)
                            }
                          >
                            {concept.label}
                          </button>
                          <button
                            type="button"
                            onClick={() => removePatternForLanguage(language, concept.id)}
                            className={patternChipRemoveBtnClass}
                            aria-label={`Убрать ${concept.label}`}
                          >
                            <XMarkIcon className="h-3.5 w-3.5" strokeWidth={2} />
                          </button>
                        </span>
                      )
                    }
                    return (
                      <span
                        key={`${language}-${concept.id}`}
                        className="inline-flex items-center rounded-full border border-border bg-bg-2"
                      >
                        <button
                          type="button"
                          onClick={(event) =>
                            openConceptHint(concept.id, event.currentTarget, language)
                          }
                          className="rounded-l-full px-3 py-1 text-xs text-ink-muted transition hover:text-ink"
                        >
                          {concept.label}
                        </button>
                        <button
                          type="button"
                          onClick={() => addPatternForLanguage(language, concept.id)}
                          className="rounded-r-full border-l border-border px-2 py-1 text-xs text-lime transition hover:bg-lime/10"
                          aria-label={`Добавить ${concept.label}`}
                          title="Добавить"
                        >
                          +
                        </button>
                      </span>
                    )
                  })}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedPatterns.length > 0 && (
        <div className={patternChipListClass}>
          {selectedPatterns.map((p) =>
            renderSelectedConceptChip({
              id: String(p.id),
              label: patternLabel(catalog, p),
            }),
          )}
        </div>
      )}

      <ConceptPopover
        concept={
          popoverCard
            ? {
                id: popoverCard.id,
                name_ru: popoverCard.name_ru ?? popoverCard.id,
                description_ru: popoverCard.description_ru,
                descriptions_by_language: popoverCard.descriptions_by_language,
                examples_by_language: popoverCard.examples_by_language,
                pascal_template: popoverCard.pascal_template,
              }
            : null
        }
        anchorRect={popoverAnchor}
        learningLanguage={popoverLanguage}
        knownLanguage={popoverLanguage}
        transferText={null}
        onClose={() => {
          setPopoverConceptId(null)
          setPopoverAnchor(null)
          setPopoverLanguage(activeLanguage)
        }}
      />
    </div>
  )
}
