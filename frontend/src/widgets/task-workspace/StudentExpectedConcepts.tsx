import { useMemo, useState } from "react"
import ConceptPopover from "@/widgets/task-workspace/ConceptPopover"
import { getCurriculumLearningLanguage } from "@/features/task-solving/model/studentUiUtils"
import { useExpectedConceptScan } from "@/features/task-solving/model/useExpectedConceptScan"
import type { TaskDto } from "@/shared/types/task"

interface ExpectedConcept {
  id: string
  name_ru?: string
  description_ru?: string
  transfer_hint_ru?: string
  in_proactive_scope?: boolean
  pascal_template?: string
  examples_by_language?: Record<string, Array<{ title?: string; code?: string }>>
  [key: string]: unknown
}

interface AnchorRect {
  left: number
  bottom: number
}

interface ConceptPopoverState {
  concept: ExpectedConcept
  anchorRect: AnchorRect
}

function readRecord<T>(value: unknown): Record<string, T> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null
  return value as Record<string, T>
}

interface TransferProactive {
  zone?: string | null
  text?: string | null
  concept_ids?: string[]
}

interface TransferMeta {
  pedagogy_note_ru?: string
  reference_warning_ru?: string
  hint_ru?: string
  contrast_note_ru?: string
  pitfall_id?: string | null
  debug_id?: string | null
  debug_meta?: {
    hint_ru?: string
    feedback_ru?: string
    pedagogy_note_ru?: string
  }
  algorithm_proactive?: {
    debug_id?: string
    text?: string
  }
  transfer_type?: string
  proactive?: TransferProactive
}

function readTransferMeta(task: TaskDto | null | undefined): TransferMeta | null {
  const curriculum = (task?.curriculum || {}) as Record<string, unknown>
  const rootTransfer = (task as { transfer?: unknown })?.transfer
  const curriculumTransfer = curriculum.transfer
  const asTransfer = (value: unknown): TransferMeta | null =>
    value && typeof value === "object" && !Array.isArray(value) ? (value as TransferMeta) : null

  // Root transfer is pair-resolved in finalize_student_task_payload; curriculum may be stale.
  return asTransfer(rootTransfer) ?? asTransfer(curriculumTransfer)
}

/** Language pair the backend used for hints / transfer on this payload. */
export function resolveTaskPedagogyLanguagePair(
  task: TaskDto | null | undefined,
): { source: string; target: string } | null {
  if (!task) return null
  const record = task as Record<string, unknown>
  const source = String(record.requested_source_language || record.source_language || "")
    .trim()
    .toLowerCase()
  const target = String(
    record.requested_target_language || record.target_language || record.language || "",
  )
    .trim()
    .toLowerCase()
  if (!source || !target) return null
  return { source, target }
}

export function taskPedagogyMatchesLanguagePair(
  task: TaskDto | null | undefined,
  knownLanguage: string,
  learningLanguage: string,
): boolean {
  const pair = resolveTaskPedagogyLanguagePair(task)
  if (!pair) return true
  const known = String(knownLanguage || "").trim().toLowerCase()
  const learning = String(learningLanguage || "").trim().toLowerCase()
  return pair.source === known && pair.target === learning
}

/** Proactive MPLT banner text for the student task workspace (Stage 3). */
export function pickTransferTextForTask(
  task: TaskDto | null | undefined,
): string | null {
  const transfer = readTransferMeta(task)
  if (!transfer) return null

  const transferType = String(transfer.transfer_type || "TCC").trim().toUpperCase()
  if (transferType === "TCC") return null

  const proactiveText = String(transfer.proactive?.text || "").trim()
  if (proactiveText) return proactiveText

  const reference = String(transfer.reference_warning_ru || "").trim()
  return reference || null
}

export function shouldShowTransferBanner(task: TaskDto | null | undefined): boolean {
  return Boolean(pickTransferTextForTask(task))
}

/** AlgorithmDebug proactive hint — separate from MPLT transfer banner (Stage 3/4). */
export function pickAlgorithmDebugHint(task: TaskDto | null | undefined): string | null {
  const transfer = readTransferMeta(task)
  if (!transfer?.debug_id) return null

  const explicit = String(transfer.algorithm_proactive?.text || "").trim()
  if (explicit) return explicit

  const fromMeta = String(transfer.debug_meta?.hint_ru || "").trim()
  return fromMeta || null
}

export function shouldShowAlgorithmDebugHint(task: TaskDto | null | undefined): boolean {
  return Boolean(pickAlgorithmDebugHint(task))
}

function normalizeConceptCard(item: unknown): ExpectedConcept | null {
  if (!item) return null
  if (typeof item === "string") {
    const id = item.trim()
    return id ? { id, name_ru: id } : null
  }
  if (typeof item !== "object" || Array.isArray(item)) return null
  const concept = item as ExpectedConcept
  const id = String(concept.id || "").trim()
  if (!id) return null
  const name = String(concept.name_ru || "").trim()
  return {
    ...concept,
    id,
    name_ru: name && name !== id ? name : id,
  }
}

function normalizeConceptCards(items: unknown[]): ExpectedConcept[] {
  return items
    .map((item) => normalizeConceptCard(item))
    .filter((item): item is ExpectedConcept => item !== null)
}

function collectConceptCardPool(
  task: TaskDto | null | undefined,
  curriculum: Record<string, unknown>,
): Map<string, ExpectedConcept> {
  const pool = new Map<string, ExpectedConcept>()

  const addCards = (items: unknown) => {
    if (!Array.isArray(items)) return
    for (const card of normalizeConceptCards(items)) {
      pool.set(card.id, card)
    }
  }

  const byLanguageCards =
    readRecord<ExpectedConcept[]>(curriculum.expected_concepts_by_language) ??
    readRecord<ExpectedConcept[]>(
      (task as { expected_concepts_by_language?: unknown })?.expected_concepts_by_language,
    )
  if (byLanguageCards) {
    for (const cards of Object.values(byLanguageCards)) {
      addCards(cards)
    }
  }

  addCards(task?.expected_concepts)
  addCards(curriculum.expected_concepts)

  const conceptsByLang = readRecord<string[] | ExpectedConcept[]>(curriculum.expected_concepts)
  if (conceptsByLang && !Array.isArray(conceptsByLang)) {
    for (const entry of Object.values(conceptsByLang)) {
      if (Array.isArray(entry) && entry.length > 0 && typeof entry[0] === "object") {
        addCards(entry)
      }
    }
  }

  return pool
}

function resolvePerLanguageConceptIds(
  task: TaskDto | null | undefined,
  curriculum: Record<string, unknown>,
  lang: string,
): string[] {
  const byLanguageIds =
    readRecord<string[]>(curriculum.expected_concept_ids_by_language) ??
    readRecord<string[]>(
      (task as { expected_concept_ids_by_language?: unknown })?.expected_concept_ids_by_language,
    )
  const fromByLanguage = byLanguageIds?.[lang]
  if (Array.isArray(fromByLanguage) && fromByLanguage.length > 0) {
    return fromByLanguage.map(String).filter(Boolean)
  }

  const conceptsByLang = readRecord<string[] | ExpectedConcept[]>(curriculum.expected_concepts)
  if (conceptsByLang && !Array.isArray(conceptsByLang)) {
    const forLang = conceptsByLang[lang]
    if (Array.isArray(forLang) && forLang.length > 0 && typeof forLang[0] === "string") {
      return forLang.map(String).filter(Boolean)
    }
  }

  return []
}

function matchConceptCardsByIds(
  pool: Map<string, ExpectedConcept>,
  ids: string[],
): ExpectedConcept[] {
  const matched: ExpectedConcept[] = []
  const seen = new Set<string>()
  for (const rawId of ids) {
    const id = String(rawId || "").trim()
    if (!id || seen.has(id)) continue
    seen.add(id)
    const direct = pool.get(id)
    if (direct) {
      matched.push(direct)
      continue
    }
    for (const card of pool.values()) {
      if (String(card.display_id || "") === id) {
        matched.push(card)
        break
      }
      const techIds = card.technical_concept_ids
      if (Array.isArray(techIds) && techIds.some((techId) => String(techId) === id)) {
        matched.push(card)
        break
      }
    }
  }
  return matched
}

/** Expected concept cards for the active learning language (not the whole task). */
export function pickExpectedConceptsForLanguage(
  task: TaskDto | null | undefined,
  learningLanguage: string,
): ExpectedConcept[] {
  const lang = String(learningLanguage || "").trim().toLowerCase() || "pascal"
  const curriculum = (task?.curriculum || {}) as Record<string, unknown>
  const cardPool = collectConceptCardPool(task, curriculum)
  const perLanguageIds = resolvePerLanguageConceptIds(task, curriculum, lang)

  const byLanguageCards =
    readRecord<ExpectedConcept[]>(curriculum.expected_concepts_by_language) ??
    readRecord<ExpectedConcept[]>(
      (task as { expected_concepts_by_language?: unknown })?.expected_concepts_by_language,
    )
  if (byLanguageCards) {
    const forLang = byLanguageCards[lang]
    if (Array.isArray(forLang) && forLang.length > 0) {
      const cards = normalizeConceptCards(forLang)
      if (!perLanguageIds.length || cards.length >= perLanguageIds.length) {
        return cards
      }
      const matched = matchConceptCardsByIds(cardPool, perLanguageIds)
      if (matched.length >= perLanguageIds.length) return matched
      if (matched.length > cards.length) return matched
      return cards
    }
  }

  if (perLanguageIds.length > 0) {
    const matched = matchConceptCardsByIds(cardPool, perLanguageIds)
    if (matched.length >= perLanguageIds.length) return matched
    if (matched.length > 0) {
      const matchedIds = new Set(matched.map((card) => card.id))
      const filled = [...matched]
      for (const id of perLanguageIds) {
        if (!matchedIds.has(id)) {
          filled.push({ id, name_ru: id })
        }
      }
      return filled
    }
    return perLanguageIds.map((id) => ({ id, name_ru: id }))
  }

  const targetLang = String(
    task?.target_language || curriculum.target_language || task?.language || curriculum.language || "",
  )
    .trim()
    .toLowerCase()
  const topLevelCards = Array.isArray(task?.expected_concepts)
    ? task.expected_concepts
    : Array.isArray(curriculum.expected_concepts)
      ? (curriculum.expected_concepts as ExpectedConcept[])
      : []
  if (topLevelCards.length > 0 && (!targetLang || targetLang === lang)) {
    return normalizeConceptCards(topLevelCards)
  }

  const conceptsByLang = readRecord<string[] | ExpectedConcept[]>(curriculum.expected_concepts)
  if (conceptsByLang && !Array.isArray(conceptsByLang)) {
    const forLang = conceptsByLang[lang]
    if (Array.isArray(forLang) && forLang.length > 0 && typeof forLang[0] === "object") {
      return normalizeConceptCards(forLang as ExpectedConcept[])
    }
  }

  const ids = [
    ...(Array.isArray(curriculum.expected_concept_ids)
      ? (curriculum.expected_concept_ids as string[])
      : []),
    ...(Array.isArray(task?.expected_concept_ids) ? task.expected_concept_ids : []),
  ]
    .map(String)
    .filter(Boolean)

  const uniqueIds = [...new Set(ids)]
  if (uniqueIds.length === 0) return []

  const matched = matchConceptCardsByIds(cardPool, uniqueIds)
  if (matched.length > 0) return matched

  return uniqueIds.map((id) => ({
    id,
    name_ru: id,
  }))
}

export function taskHasExpectedConceptsForLanguage(
  task: TaskDto | null | undefined,
  learningLanguage: string,
): boolean {
  return pickExpectedConceptsForLanguage(task, learningLanguage).length > 0
}

function pickPrimaryTc(task: TaskDto | null | undefined): string {
  const curriculum = (task?.curriculum || {}) as Record<string, unknown>
  return String(
    curriculum.technical_concept_id ??
      curriculum.primary_technical_concept_id ??
      task?.primary_technical_concept_id ??
      "",
  )
}

function buildConceptGroups(concepts: ExpectedConcept[], primaryTc: string) {
  if (primaryTc === "inheritance_hierarchy") {
    return [{ label: "Наследование", concepts }]
  }
  return [{ label: null as string | null, concepts }]
}

function chipClassName(active: boolean, used: boolean) {
  if (used) {
    return [
      "inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[13px] font-medium transition",
      "border border-[rgba(142,255,1,.32)] bg-[rgba(142,255,1,.12)] text-lime",
      active ? "ring-1 ring-lime/12" : "",
    ]
      .filter(Boolean)
      .join(" ")
  }
  return [
    "inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[13px] font-medium transition",
    "border border-border bg-surface-2 text-ink-faint",
    active ? "ring-1 ring-border text-ink-muted" : "hover:border-border-2 hover:text-ink-muted",
  ].join(" ")
}

interface StudentExpectedConceptsProps {
  task: TaskDto | null | undefined
  knownLanguage?: string
  learnedCode?: string
  learningLanguage?: string
  className?: string
}

export default function StudentExpectedConcepts({
  task,
  knownLanguage = "python",
  learnedCode = "",
  learningLanguage: learningLanguageProp,
  className = "",
}: StudentExpectedConceptsProps) {
  const learningLanguage =
    learningLanguageProp || getCurriculumLearningLanguage(task) || "pascal"

  const concepts = useMemo(
    () => pickExpectedConceptsForLanguage(task, learningLanguage),
    [task, learningLanguage],
  )
  const primaryTc = pickPrimaryTc(task)
  const groups = useMemo(
    () => buildConceptGroups(concepts, primaryTc),
    [concepts, primaryTc],
  )

  const { usedMap, reasons, loading } = useExpectedConceptScan(
    learnedCode,
    learningLanguage,
    concepts,
  )

  const [popover, setPopover] = useState<ConceptPopoverState | null>(null)

  if (concepts.length === 0) {
    return null
  }

  const onChipClick = (concept: ExpectedConcept, element: HTMLElement) => {
    const rect = element.getBoundingClientRect()
    setPopover((current) =>
      current?.concept?.id === concept.id ? null : { concept, anchorRect: rect },
    )
  }

  const activeConcept = popover?.concept ?? null

  return (
    <>
      <section className={className}>
        <div className="mb-3 flex items-center justify-between gap-2">
          <h3 className="text-[11px] font-semibold uppercase tracking-[0.1em] text-ink-faint">
            Ожидаемые конструкции
          </h3>
          {loading ? (
            <span className="text-[11px] text-ink-faint">Проверка…</span>
          ) : null}
        </div>

        <div className="space-y-3">
          {groups.map((group) => (
            <div key={group.label || "default"}>
              {group.label ? (
                <div className="mb-1.5 text-[12px] font-medium text-ink-muted">{group.label}</div>
              ) : null}
              <div className="flex flex-wrap gap-1.5">
                {group.concepts.map((concept) => (
                  <button
                    key={concept.id}
                    type="button"
                    data-concept-id={concept.id}
                    onClick={(event) => onChipClick(concept, event.currentTarget)}
                    title={reasons[concept.id] || undefined}
                    className={chipClassName(
                      activeConcept?.id === concept.id,
                      usedMap[concept.id] ?? false,
                    )}
                  >
                    {concept.name_ru}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

      </section>

      <ConceptPopover
        concept={popover?.concept}
        anchorRect={popover?.anchorRect}
        learningLanguage={learningLanguage}
        knownLanguage={knownLanguage}
        onClose={() => setPopover(null)}
      />
    </>
  )
}
