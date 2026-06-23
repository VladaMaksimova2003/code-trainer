import { useEffect, useMemo } from "react"

import { langDisplay } from "@/features/task-solving/model/studentUiUtils"

import CodeBlockView from "@/widgets/task-workspace/CodeBlockView"

import {
  useDraggablePopover,
  type PopoverAnchorRect,
} from "@/widgets/task-workspace/useDraggablePopover"

interface ConceptExample {
  title?: string
  code?: string
}

interface ExpectedConcept {
  id: string
  name_ru?: string
  description_ru?: string
  transfer_hint_ru?: string
  in_proactive_scope?: boolean
  descriptions_by_language?: Record<string, string>
  pascal_template?: string
  examples_by_language?: Record<string, ConceptExample[]>
  [key: string]: unknown
}

/** Chip-level MPLT hint — only when backend marked the concept in proactive scope. */
export function pickConceptTransferHint(
  concept: ExpectedConcept | null | undefined,
): string | null {
  if (!concept || concept.in_proactive_scope !== true) return null
  const hint = String(concept.transfer_hint_ru || "").trim()
  return hint || null
}

function isDivisionTransferHint(hint: string): boolean {
  const text = hint.toLowerCase()
  return (
    text.includes("div") ||
    text.includes("//") ||
    text.includes("делен") ||
    text.includes("частн")
  )
}

function pickRelevantExamples(
  rows: ConceptExample[],
  divisionPair: boolean,
): ConceptExample[] {
  if (!rows.length) return []
  if (!divisionPair) return rows.slice(0, 2)
  const divisionRows = rows.filter((row) => {
    const code = String(row.code || "").toLowerCase()
    const title = String(row.title || "").toLowerCase()
    return (
      code.includes("//") ||
      code.includes("div") ||
      title.includes("div") ||
      title.includes("цел") ||
      title.includes("//")
    )
  })
  return (divisionRows.length ? divisionRows : rows).slice(0, 1)
}

function languageForExampleTitle(title: string, fallback: string): string {
  const match = title.match(/^([^·]+)·/)
  return match ? match[1].trim().toLowerCase() : fallback
}

/** Popover examples: target language; for MPLT pairs also source when proactive. */
export function pickExamplesForConcept(
  concept: ExpectedConcept | null | undefined,
  learningLanguage: string,
  knownLanguage = "",
): ConceptExample[] {
  if (!concept) return []
  const targetLang = String(learningLanguage || "pascal").toLowerCase()
  const sourceLang = String(knownLanguage || "").toLowerCase()
  const fromApi = concept.examples_by_language
  if (!fromApi || typeof fromApi !== "object") {
    const fallback = String(concept.pascal_template || "").trim()
    if (fallback && targetLang === "pascal") {
      return [{ title: "Пример", code: fallback }]
    }
    return []
  }

  const transferHint = pickConceptTransferHint(concept) || ""
  const divisionPair = Boolean(transferHint) && isDivisionTransferHint(transferHint)
  const proactivePair =
    concept.in_proactive_scope === true &&
    Boolean(sourceLang) &&
    sourceLang !== targetLang

  if (proactivePair) {
    const merged: ConceptExample[] = []
    const sourceRows = Array.isArray(fromApi[sourceLang]) ? fromApi[sourceLang] : []
    const targetRows = Array.isArray(fromApi[targetLang]) ? fromApi[targetLang] : []
    for (const row of pickRelevantExamples(sourceRows, divisionPair)) {
      merged.push({
        ...row,
        title: `${langDisplay(sourceLang)} · ${row.title || "Пример"}`,
      })
    }
    for (const row of pickRelevantExamples(targetRows, divisionPair)) {
      merged.push({
        ...row,
        title: `${langDisplay(targetLang)} · ${row.title || "Пример"}`,
      })
    }
    if (merged.length) return merged
  }

  const preferred = fromApi[targetLang]
  if (Array.isArray(preferred) && preferred.length > 0) {
    return preferred
  }
  return []
}

interface ConceptPopoverProps {
  concept?: ExpectedConcept | null
  anchorRect?: PopoverAnchorRect | null
  learningLanguage?: string
  knownLanguage?: string
  onClose?: () => void
}

function descriptionForConcept(concept: ExpectedConcept, learningLanguage: string): string {
  const lang = String(learningLanguage || "pascal").toLowerCase()
  const byLang = concept.descriptions_by_language
  if (byLang && typeof byLang === "object") {
    const localized = byLang[lang]
    if (typeof localized === "string" && localized.trim()) return localized.trim()
  }
  return String(concept.description_ru || "").trim()
}

export default function ConceptPopover({
  concept,
  anchorRect,
  learningLanguage = "pascal",
  knownLanguage = "",
  onClose,
}: ConceptPopoverProps) {
  const activeLanguage = String(learningLanguage || "pascal").toLowerCase()

  const popW = 440
  const { pos, onDragStart, maxHeight, popRef, isPlacementReady } = useDraggablePopover({
    anchorRect,
    width: popW,
    enabled: Boolean(concept && anchorRect),
  })

  const variants = useMemo(
    () => (concept ? pickExamplesForConcept(concept, activeLanguage, knownLanguage) : []),
    [concept, activeLanguage, knownLanguage],
  )

  const conceptTransferHint = useMemo(() => pickConceptTransferHint(concept), [concept])

  const description = useMemo(
    () => (concept ? descriptionForConcept(concept, activeLanguage) : ""),
    [concept, activeLanguage],
  )

  useEffect(() => {
    if (!concept) return undefined
    const onDoc = (event: MouseEvent) => {
      const target = event.target
      if (!(target instanceof Element)) return
      if (!target.closest("[data-concept-popover]") && !target.closest("[data-concept-id]")) {
        onClose?.()
      }
    }
    const onEsc = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose?.()
    }
    document.addEventListener("mousedown", onDoc)
    document.addEventListener("keydown", onEsc)
    return () => {
      document.removeEventListener("mousedown", onDoc)
      document.removeEventListener("keydown", onEsc)
    }
  }, [concept, onClose])

  if (!concept || !anchorRect || !pos) return null

  return (
    <div
      ref={popRef}
      data-concept-popover
      className="fixed z-50 pop-in"
      style={{
        left: pos.left,
        top: pos.top,
        width: popW,
        maxHeight,
        opacity: isPlacementReady ? 1 : 0,
        pointerEvents: isPlacementReady ? "auto" : "none",
      }}
    >
      <div className="flex max-h-[inherit] flex-col overflow-hidden rounded-xl border border-border bg-surface shadow-[0_30px_60px_-20px_rgba(0,0,0,0.8)]">
        <div
          className="flex shrink-0 cursor-grab select-none items-center gap-2 border-b border-border px-4 py-3 active:cursor-grabbing"
          onMouseDown={onDragStart}
          title="Перетащите, чтобы переместить"
        >
          <div className="text-[15px] font-semibold text-ink">{concept.name_ru}</div>
          <span className="text-ink-faint text-[12px]">·</span>
          <span className="text-[12px] text-lime font-medium">{langDisplay(activeLanguage)}</span>
          <div className="flex-1" />
          <button
            type="button"
            onClick={onClose}
            className="h-6 w-6 ml-1 rounded-md text-ink-faint hover:text-ink hover:bg-surface-2 flex items-center justify-center transition cursor-pointer"
            aria-label="Закрыть"
            onMouseDown={(event) => event.stopPropagation()}
          >
            ×
          </button>
        </div>

        {description ? (
          <div className="shrink-0 px-4 pt-3.5 pb-1">
            <p className="text-[13px] text-ink-muted leading-relaxed">{description}</p>
          </div>
        ) : null}

        <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 pb-4 pt-2">
          {variants.length === 0 ? (
            <p className="text-[13px] text-ink-muted">Примеры для этого языка пока недоступны.</p>
          ) : (
            variants.map((variant, index) => {
              const blockLang = languageForExampleTitle(
                String(variant.title || ""),
                activeLanguage,
              )
              return (
                <div key={`${blockLang}-${index}`}>
                  {variant.title ? (
                    <div className="text-[12px] font-medium text-ink-muted mb-1.5">{variant.title}</div>
                  ) : null}
                  <div className="overflow-x-auto rounded-lg border border-border bg-bg-2">
                    <CodeBlockView code={variant.code ?? ""} language={blockLang} />
                  </div>
                </div>
              )
            })
          )}

          {conceptTransferHint ? (
            <p className="text-[12px] text-ink-faint leading-relaxed border-t border-border pt-3">
              {conceptTransferHint}
            </p>
          ) : null}
        </div>
      </div>
    </div>
  )
}
