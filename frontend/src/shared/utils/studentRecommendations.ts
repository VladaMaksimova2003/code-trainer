import type { TaskDto } from "@/shared/types/task"

const PROGRESS_WEAK_MAX = 50
const PROGRESS_SOLID_MAX = 80
const ERROR_SHARE_THRESHOLD = 0.35
const MIN_ERRORS_FOR_HINT = 2

export interface SkillProgressRow {
  label: string
  percent?: number
  total?: number
}

export interface WeakTopic {
  name: string
  progress: number
  recommendation: string
}

export interface RecentResultRow {
  success?: boolean
  message?: string
}

export interface StudentRecommendations {
  streak: { days: number; message: string }
  weak_topics: WeakTopic[]
  errors: string[]
  next_steps: string[]
}

export interface LegacyRecommendationItem {
  kind: "success" | "hint"
  message: string
  detail?: string
  id: string
}

function progressRecommendation(label: string, percent: number): string {
  if (percent < PROGRESS_WEAK_MAX) {
    return `Рекомендуется решить 2–3 задания по теме «${label}»`
  }
  if (percent <= PROGRESS_SOLID_MAX) {
    return `Рекомендуется закрепить тему «${label}»`
  }
  return `Можно переходить к более сложным задачам по теме «${label}»`
}

export function analyzeProgress(skillProgress: SkillProgressRow[] = []): {
  weakTopics: WeakTopic[]
  nextSteps: string[]
} {
  const weakTopics: WeakTopic[] = []
  const nextSteps: string[] = []
  const ranked = skillProgress
    .filter((row) => (row.total ?? 0) > 0)
    .sort((a, b) => (a.percent ?? 0) - (b.percent ?? 0))

  for (const row of ranked) {
    const percent = Number(row.percent ?? 0)
    if (percent < PROGRESS_WEAK_MAX) {
      weakTopics.push({
        name: row.label,
        progress: Math.round(percent * 10) / 10,
        recommendation: progressRecommendation(row.label, percent),
      })
    }
  }

  if (ranked.length > 0) {
    const weakest = ranked[0]
    nextSteps.push(`Рекомендуется перейти к теме: ${weakest.label}`)
    const strong = ranked.filter((row) => Number(row.percent ?? 0) > PROGRESS_SOLID_MAX)
    if (strong.length > 0) {
      const best = strong.reduce((a, b) => ((a.percent ?? 0) > (b.percent ?? 0) ? a : b))
      nextSteps.push(progressRecommendation(best.label, best.percent ?? 0))
    }
  }

  return { weakTopics, nextSteps }
}

export function analyzeErrorsFromSubmissions(recentResults: RecentResultRow[] = []): string[] {
  const failed = recentResults.filter((row) => !row.success).slice(0, 20)
  if (failed.length < MIN_ERRORS_FOR_HINT) return []
  const hints: string[] = []
  const threshold = Math.max(MIN_ERRORS_FOR_HINT, failed.length * ERROR_SHARE_THRESHOLD)
  const messages = failed.map((row) => String(row.message || "").toLowerCase()).join(" ")
  if (messages.includes("компил") || messages.includes("syntax") || messages.includes("синтакс")) {
    if (failed.length >= threshold) hints.push("Обратите внимание на синтаксис выбранного языка")
  }
  if (messages.includes("runtime") || messages.includes("выполнен")) {
    if (failed.length >= threshold) {
      hints.push("Частые ошибки выполнения — обратите внимание на обработку граничных условий")
    }
  }
  if (failed.length >= threshold) {
    hints.push("Рекомендуется внимательнее проверять логику решения")
  }
  return [...new Set(hints)]
}

export function analyzeBehavior({
  streakDays = 0,
  tasks = [],
}: {
  streakDays?: number
  tasks?: TaskDto[]
}): { streak: { days: number; message: string }; nextSteps: string[] } {
  let message: string
  if (streakDays >= 3) {
    message = `Вы занимаетесь ${streakDays} дней подряд — отличная регулярность`
  } else if (streakDays > 0) {
    message = `Продолжайте заниматься, чтобы сохранить серию (${streakDays} дн.)`
  } else {
    message = "Решите любую задачу сегодня — так начнётся серия дней"
  }

  const nextSteps: string[] = []
  const difficulties = new Set(
    tasks.map((t) => String(t.difficulty || "").toLowerCase()).filter(Boolean),
  )
  const onlyEasy =
    difficulties.size > 0 &&
    [...difficulties].every((d) => d === "easy" || d === "лёгкая" || d === "легкая")
  if (onlyEasy && tasks.length >= 3) {
    nextSteps.push("Попробуйте задания среднего уровня")
  }

  return { streak: { days: streakDays, message }, nextSteps }
}

export function buildStudentRecommendations({
  skillProgress = [],
  streakDays = 0,
  recentResults = [],
  tasks = [],
}: {
  skillProgress?: SkillProgressRow[]
  streakDays?: number
  recentResults?: RecentResultRow[]
  tasks?: TaskDto[]
}): StudentRecommendations {
  const { weakTopics, nextSteps: progressSteps } = analyzeProgress(skillProgress)
  const errors = analyzeErrorsFromSubmissions(recentResults)
  const { streak, nextSteps: behaviorSteps } = analyzeBehavior({ streakDays, tasks })

  const nextSteps: string[] = []
  const seen = new Set<string>()
  for (const step of [...progressSteps, ...behaviorSteps]) {
    if (!seen.has(step)) {
      seen.add(step)
      nextSteps.push(step)
    }
  }

  return { streak, weak_topics: weakTopics, errors, next_steps: nextSteps }
}

export function recommendationsToLegacyList(structured: StudentRecommendations | null | undefined): LegacyRecommendationItem[] {
  if (!structured) return []
  const items: LegacyRecommendationItem[] = []
  for (const [index, topic] of (structured.weak_topics || []).entries()) {
    items.push({
      kind: "hint",
      message: topic.recommendation || topic.name,
      detail: topic.name,
      id: `weak-${index}`,
    })
  }
  for (const [index, text] of (structured.errors || []).entries()) {
    items.push({ kind: "hint", message: text, id: `error-${index}` })
  }
  for (const [index, text] of (structured.next_steps || []).entries()) {
    items.push({ kind: "hint", message: text, id: `step-${index}` })
  }
  return items
}
