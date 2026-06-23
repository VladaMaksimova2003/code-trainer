import { displayTrackTotal, effectiveCollectionTotal } from "@/features/curriculum/actionMeta"
import {
  LANGUAGE_LABELS,
  readStoredLearningLanguage,
} from "@/features/curriculum/curriculumLanguageUi"
import {
  isCurriculumLearningLanguage,
  type CurriculumLearningLanguage,
} from "@/shared/config/curriculumLanguages"
import type { TaskOverviewItem } from "@/shared/types/taskOverview"

export interface UnifiedTaskStats {
  solved: number
  total: number
}

export interface TrackTaskStats extends UnifiedTaskStats {
  language: CurriculumLearningLanguage
  languageLabel: string
}

interface CollectionProgressRow {
  progress?: {
    total_tasks?: number | null
    passed_tasks?: number | null
    catalog_tasks?: number | null
  } | null
}

interface CurriculumLanguageProgress {
  language?: string
  language_label?: string
  progress?: CollectionProgressRow["progress"]
  collections?: CollectionProgressRow[]
}

const PHRASE_NOT_STARTED = "трек ещё не начат"
const PHRASE_EARLY_PROGRESS = "пройдены первые темы"
const PHRASE_TRACK_START = "начинаете работу с этим треком"
const PHRASE_RECENT_HARD = "в последних разделах преобладают сложные задачи"
const PHRASE_RECENT_MEDIUM =
  "сейчас основная часть задач находится на среднем уровне сложности"
const PHRASE_DEFAULT = "сложность постепенно растёт по мере прохождения трека"

function difficultyWeight(raw: string | null | undefined): number {
  const value = String(raw ?? "").toLowerCase()
  if (value.includes("hard") || value === "сложная") return 3
  if (value.includes("medium") || value === "средняя") return 2
  return 1
}

function average(values: number[]): number {
  if (!values.length) return 0
  return values.reduce((sum, value) => sum + value, 0) / values.length
}

function pedagogicalDedupeKey(task: TaskOverviewItem): string {
  const ped = String(task.pedagogical_slot_id || "").trim()
  if (ped) return ped
  const slot = String(task.slot_id || "").trim()
  if (slot) return slot
  return String(task.id)
}

function trackDisplayTotal(row: CurriculumLanguageProgress | undefined): number {
  return displayTrackTotal(row)
}

function curriculumUnifiedTotal(curriculumLanguages: CurriculumLanguageProgress[]): number {
  if (!curriculumLanguages.length) return 0
  return Math.max(...curriculumLanguages.map((lang) => trackDisplayTotal(lang)), 0)
}

function resolveUnifiedTotal(
  curriculumTotal: number,
  dedupedTotal: number,
  rawTotal: number,
  tasksComplete: boolean,
): number {
  if (curriculumTotal > 0) return curriculumTotal
  if (tasksComplete && dedupedTotal > 0 && rawTotal > dedupedTotal) return dedupedTotal
  return rawTotal || dedupedTotal
}

function countUniquePedagogicalTasks(tasks: TaskOverviewItem[]): number {
  return new Set(tasks.map(pedagogicalDedupeKey)).size
}

function countSolvedOnTrack(tasks: TaskOverviewItem[], track: CurriculumLearningLanguage): number {
  const solvedByKey = new Map<string, boolean>()
  for (const task of tasks) {
    const state = task.language_track_states?.[track]
    const solved =
      state === "solved" || (state === undefined && Boolean(task.solved) && trackMatchesTask(task, track))
    if (!solved) continue
    solvedByKey.set(pedagogicalDedupeKey(task), true)
  }
  return solvedByKey.size
}

function trackMatchesTask(task: TaskOverviewItem, track: CurriculumLearningLanguage): boolean {
  const tracks = task.available_language_tracks
  if (Array.isArray(tracks) && tracks.length > 0) {
    return tracks.map((item) => String(item).toLowerCase()).includes(track)
  }
  const single = String(task.target_language || task.language || "").toLowerCase()
  return !single || single === track
}

/** Active curriculum track: last used language from storage, with sensible fallbacks. */
export function resolveActiveLearningTrack(
  curriculumLanguages: CurriculumLanguageProgress[] = [],
): CurriculumLearningLanguage {
  const stored = readStoredLearningLanguage()
  if (curriculumLanguages.some((row) => row.language === stored)) {
    return stored
  }
  const withProgress = curriculumLanguages.find((row) => (row.progress?.passed_tasks ?? 0) > 0)
  const candidate = withProgress?.language
  if (candidate && isCurriculumLearningLanguage(candidate)) {
    return candidate
  }
  return stored
}

function trackLabel(
  track: CurriculumLearningLanguage,
  curriculumLanguages: CurriculumLanguageProgress[],
): string {
  const row = curriculumLanguages.find((item) => item.language === track)
  if (row?.language_label) return row.language_label
  return LANGUAGE_LABELS[track] ?? track
}

interface ComputeTrackTaskStatsOptions {
  /** Guest/demo session — ignore curriculum passed_tasks from API. */
  ignoreCurriculumProgress?: boolean
}

/** Progress for the current active language track (not summed across languages). */
export function computeTrackTaskStats(
  curriculumLanguages: CurriculumLanguageProgress[],
  activeTrack: CurriculumLearningLanguage,
  tasks: TaskOverviewItem[] = [],
  overviewTotal = 0,
  options?: ComputeTrackTaskStatsOptions,
): TrackTaskStats {
  const row = curriculumLanguages.find((item) => item.language === activeTrack)
  const curriculumTotal = curriculumUnifiedTotal(curriculumLanguages)
  const dedupedTotal = countUniquePedagogicalTasks(tasks)
  const rawTotal = overviewTotal > 0 ? overviewTotal : tasks.length
  const tasksComplete = overviewTotal > 0 && tasks.length >= overviewTotal
  const total =
    trackDisplayTotal(row) ||
    resolveUnifiedTotal(curriculumTotal, dedupedTotal, rawTotal, tasksComplete)

  const solvedFromCurriculum = row?.progress?.passed_tasks
  const solved = options?.ignoreCurriculumProgress
    ? countSolvedOnTrack(tasks, activeTrack)
    : typeof solvedFromCurriculum === "number"
      ? solvedFromCurriculum
      : countSolvedOnTrack(tasks, activeTrack)

  return {
    language: activeTrack,
    languageLabel: trackLabel(activeTrack, curriculumLanguages),
    solved,
    total,
  }
}

function tasksSolvedOnTrack(
  tasks: TaskOverviewItem[],
  track: CurriculumLearningLanguage,
): TaskOverviewItem[] {
  return tasks.filter((task) => {
    const state = task.language_track_states?.[track]
    if (state === "solved") return true
    if (state === "attempted" || state === "todo") return false
    return Boolean(task.solved) && trackMatchesTask(task, track)
  })
}

function detectDifficultyTrendForTrack(
  tasks: TaskOverviewItem[],
  track: CurriculumLearningLanguage,
): string | null {
  const solved = tasksSolvedOnTrack(tasks, track)
  if (solved.length < 4) return null

  const recent = [...solved].sort((a, b) => b.id - a.id).slice(0, 5)
  const weights = recent.map((task) => difficultyWeight(task.difficulty))
  const avgRecent = average(weights)
  const hardCount = weights.filter((weight) => weight >= 3).length
  const mediumCount = weights.filter((weight) => weight === 2).length

  if (avgRecent >= 2.4 || hardCount >= 3) {
    return PHRASE_RECENT_HARD
  }
  if (avgRecent >= 1.75 && mediumCount >= 3) {
    return PHRASE_RECENT_MEDIUM
  }
  return null
}

function trackInsightPhrase(stats: TrackTaskStats, tasks: TaskOverviewItem[]): string {
  if (stats.solved === 0) return PHRASE_NOT_STARTED
  if (stats.solved <= 4) return PHRASE_EARLY_PROGRESS
  const trend = detectDifficultyTrendForTrack(tasks, stats.language)
  if (trend) return trend
  if (stats.solved <= 12) return PHRASE_TRACK_START
  return PHRASE_DEFAULT
}

/**
 * Subtitle under «Список задач» for the active language track.
 * Example: «Решено 4 из 128 · Python · пройдены первые темы»
 */
export function buildTaskListSubtitle(stats: TrackTaskStats, tasks: TaskOverviewItem[]): string {
  const base = `Решено ${stats.solved} из ${stats.total}`
  const insight = trackInsightPhrase(stats, tasks)
  return `${base} · ${stats.languageLabel} · ${insight}`
}

/** @deprecated Use computeTrackTaskStats for per-track progress. */
export function computeUnifiedTaskStats(
  tasks: TaskOverviewItem[],
  overviewTotal: number,
  curriculumLanguages: CurriculumLanguageProgress[] = [],
): UnifiedTaskStats {
  const track = resolveActiveLearningTrack(curriculumLanguages)
  const stats = computeTrackTaskStats(curriculumLanguages, track, tasks, overviewTotal)
  return { solved: stats.solved, total: stats.total }
}
