import type { ActionType } from "./types"

export type BadgeTone = "lime" | "purple" | "warn" | "muted"

export interface ActionMeta {
  label: string
  tone: BadgeTone
  icon: string
}

export const ACTION_META: Record<ActionType, ActionMeta> = {
  translate: { label: "Перенести", tone: "lime", icon: "⇄" },
  assemble: { label: "Собрать", tone: "purple", icon: "⧉" },
  implement: { label: "Реализовать", tone: "warn", icon: "⌨" },
  debug: { label: "Отладить", tone: "warn", icon: "⊘" },
  analyze: { label: "Разобрать", tone: "muted", icon: "◎" },
  recognize: { label: "Опознать", tone: "muted", icon: "?" },
}

export const BADGE_TONE_CLASS: Record<BadgeTone, string> = {
  lime: "border-lime/30 bg-lime/15 text-lime",
  purple: "border-purple/35 bg-purple/15 text-[#b89bff]",
  warn: "border-amber-400/35 bg-amber-400/15 text-amber-300",
  muted: "border-border-strong bg-surface-2 text-ink-muted",
}

export const DIFFICULTY_LABELS: Record<string, string> = {
  easy: "Лёгкая",
  medium: "Средняя",
  hard: "Сложная",
  Лёгкая: "Лёгкая",
  Средняя: "Средняя",
  Сложная: "Сложная",
}

export const DIFFICULTY_TONE: Record<string, BadgeTone> = {
  Лёгкая: "muted",
  Средняя: "warn",
  Сложная: "muted",
}

export function actionMetaFor(action: string | null | undefined): ActionMeta {
  if (action && action in ACTION_META) {
    return ACTION_META[action as ActionType]
  }
  return { label: action || "Задача", tone: "muted", icon: "•" }
}

export function difficultyLabel(raw: string | null | undefined): string {
  if (!raw) return "—"
  return DIFFICULTY_LABELS[raw] ?? raw
}

export function difficultyTone(raw: string | null | undefined): BadgeTone {
  return DIFFICULTY_TONE[difficultyLabel(raw)] ?? "muted"
}

export function effectiveCollectionTotal(
  progress: { total_tasks?: number | null; catalog_tasks?: number | null } | null | undefined,
): number {
  if (!progress) return 0
  const catalog = progress.catalog_tasks ?? 0
  const seeded = progress.total_tasks ?? 0
  if (seeded <= 0) return 0
  if (catalog > 0 && seeded > catalog) return catalog
  return seeded
}

/** Planned chapter/track size for UI (catalog plan), falling back to seeded tasks. */
export function displayCollectionTotal(
  progress: { total_tasks?: number | null; catalog_tasks?: number | null } | null | undefined,
): number {
  if (!progress) return 0
  const catalog = progress.catalog_tasks ?? 0
  if (catalog > 0) return catalog
  return progress.total_tasks ?? 0
}

export interface TrackProgressLike {
  progress?: { total_tasks?: number | null; catalog_tasks?: number | null } | null
  collections?: Array<{ progress?: { total_tasks?: number | null; catalog_tasks?: number | null } | null }>
}

/** Full track size for UI — sums chapter catalog plans, same as «Решено X из Y» subtitle. */
export function displayTrackTotal(row: TrackProgressLike | null | undefined): number {
  if (!row) return 0
  const fromChapters = (row.collections ?? []).reduce(
    (sum, item) => sum + displayCollectionTotal(item.progress),
    0,
  )
  if (fromChapters > 0) return fromChapters
  return displayCollectionTotal(row.progress)
}

export function progressPercent(
  progress: {
    passed_tasks?: number | null
    total_tasks?: number | null
    catalog_tasks?: number | null
    progress_percent?: number | null
  } | null | undefined,
): number {
  if (!progress) return 0
  if (typeof progress.progress_percent === "number") {
    return Math.round(progress.progress_percent)
  }
  const total = effectiveCollectionTotal(progress)
  if (!total) return 0
  return Math.round(((progress.passed_tasks ?? 0) / total) * 100)
}
