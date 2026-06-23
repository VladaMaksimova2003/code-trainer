import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"

import {
  CURRICULUM_LANGUAGE_OPTIONS,
  readStoredLearningLanguage,
} from "@/features/curriculum/curriculumLanguageUi"
import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"
import type { TcTaskRecommendation } from "@/shared/types/analytics"
import type {
  LegacyRecommendationItem,
  StudentRecommendations,
} from "@/shared/utils/studentRecommendations"

interface SkillRow {
  id: string
  label: string
  total: number
  solved: number
  percent: number
}

interface TcSkillLanguageOption {
  code: string
  label: string
}

interface StudentProfileProgressPanelProps {
  analytics: {
    overview?: { solved_count?: number }
    tc_skills?: SkillRow[]
    tc_skills_by_language?: Record<string, SkillRow[]>
    tc_skill_groups?: SkillRow[]
    tc_skill_groups_by_language?: Record<string, SkillRow[]>
    tc_skill_languages?: TcSkillLanguageOption[]
    tc_skills_default_language?: string
    tc_task_recommendations?: TcTaskRecommendation[]
    tc_task_recommendations_by_language?: Record<string, TcTaskRecommendation[]>
    by_structure?: (SkillRow & { hint?: string })[]
    student_recommendations?: StudentRecommendations
    recommendations?: LegacyRecommendationItem[]
    streak_days?: number
  } | null
}

const MAX_TASK_RECOMMENDATIONS = 3
const MAX_TIP_LINES = 3

function normalizeLangCode(raw: string | null | undefined): string {
  return String(raw || "")
    .trim()
    .toLowerCase()
    .replace("c++", "cpp")
}

function formatPercent(value: number): string {
  const pct = Math.max(0, Math.min(100, value))
  if (pct > 0 && pct < 1) return `${pct.toFixed(1)}%`
  return `${pct % 1 === 0 ? pct.toFixed(0) : pct.toFixed(1)}%`
}

function SkillProgressRow({ row }: { row: SkillRow }) {
  const pct = Number(row.percent) || 0
  const done = Number(row.solved) > 0

  return (
    <div>
      <div className="between" style={{ fontSize: 13.5, marginBottom: 6 }}>
        <span>{row.label}</span>
        <span
          className="mono"
          style={{ color: done ? "var(--lime)" : "var(--text-3)", fontSize: 12.5 }}
        >
          {formatPercent(pct)}
        </span>
      </div>
      <div className="progress">
        <i style={{ width: `${Math.max(pct, done ? 2 : 0)}%` }} />
      </div>
      {row.total > 0 ? (
        <div className="mut3" style={{ fontSize: 11.5, marginTop: 5 }}>
          Решено {row.solved ?? 0} из {row.total ?? 0}
        </div>
      ) : (
        <div className="mut3" style={{ fontSize: 11.5, marginTop: 5 }}>
          Задания появятся в следующих главах курса
        </div>
      )}
    </div>
  )
}

function LanguageBadgeSelect({
  value,
  options,
  onChange,
}: {
  value: string
  options: TcSkillLanguageOption[]
  onChange: (code: CurriculumLearningLanguage) => void
}) {
  return (
    <label className="profile-skills-lang">
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as CurriculumLearningLanguage)}
        aria-label="Язык курса"
      >
        {options.map((option) => (
          <option key={option.code} value={option.code}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  )
}

function TaskRecommendationCard({
  rec,
  onOpen,
}: {
  rec: TcTaskRecommendation
  onOpen: () => void
}) {
  const title = String(rec.title || "").trim() || `Задача #${rec.task_id}`
  const topics = (rec.weak_tc_labels || [])
    .slice(0, 2)
    .filter(Boolean)
    .join(" · ")

  return (
    <div className="rec-card">
      <div style={{ minWidth: 0, flex: "1 1 auto" }}>
        <div className="rec-title">{title}</div>
        {topics ? (
          <div className="rec-topics">
            Темы: {topics}
          </div>
        ) : rec.reason ? (
          <div className="rec-topics">{rec.reason}</div>
        ) : null}
      </div>
      <button
        type="button"
        className="btn btn-primary btn-sm"
        style={{ flex: "none" }}
        onClick={onOpen}
      >
        Решать →
      </button>
    </div>
  )
}

function TipRow({ text }: { text: string }) {
  return (
    <div className="rec-tip">
      <span className="rec-tip-ico">💡</span>
      <span style={{ fontSize: 13 }}>{text}</span>
    </div>
  )
}

function resolveLanguageOptions(
  analytics: NonNullable<StudentProfileProgressPanelProps["analytics"]>,
): TcSkillLanguageOption[] {
  const fromApi = analytics.tc_skill_languages || []
  if (fromApi.length > 0) {
    return fromApi
  }
  const byLang = analytics.tc_skills_by_language || {}
  return Object.keys(byLang).map((code) => {
    const meta = CURRICULUM_LANGUAGE_OPTIONS.find((opt) => opt.id === code)
    return { code, label: meta?.label || code }
  })
}

function pickInitialLanguage(
  analytics: NonNullable<StudentProfileProgressPanelProps["analytics"]>,
  options: TcSkillLanguageOption[],
): CurriculumLearningLanguage {
  const codes = new Set(options.map((row) => row.code))
  const stored = readStoredLearningLanguage()
  if (codes.has(stored)) return stored

  const fromApi = String(analytics.tc_skills_default_language || "").trim()
  if (fromApi && codes.has(fromApi)) return fromApi as CurriculumLearningLanguage

  const first = options[0]?.code
  if (first && CURRICULUM_LANGUAGE_OPTIONS.some((opt) => opt.id === first)) {
    return first as CurriculumLearningLanguage
  }
  return stored
}

function pickSkillRows(
  analytics: NonNullable<StudentProfileProgressPanelProps["analytics"]>,
  language: string,
): {
  rows: SkillRow[]
  usingStructureFallback: boolean
} {
  const groupScoped =
    analytics.tc_skill_groups_by_language?.[language] ||
    (analytics.tc_skills_default_language === language ? analytics.tc_skill_groups : undefined)

  if (groupScoped && groupScoped.length > 0) {
    return { rows: groupScoped, usingStructureFallback: false }
  }

  const scoped =
    analytics.tc_skills_by_language?.[language] ||
    (analytics.tc_skills_default_language === language ? analytics.tc_skills : undefined)

  const tcRows = (scoped || []).filter((row) => Number(row?.total || 0) > 0)
  if (tcRows.length > 0) {
    return { rows: displaySkillRows(tcRows), usingStructureFallback: false }
  }

  const structureRows = (analytics.by_structure || []).filter((row) => Number(row?.total || 0) > 0)
  if (structureRows.length > 0) {
    return { rows: displaySkillRows(structureRows), usingStructureFallback: true }
  }

  return { rows: [], usingStructureFallback: false }
}

function displaySkillRows(rows: SkillRow[]): SkillRow[] {
  return rows
    .filter((row) => Number(row.total) > 0)
    .slice()
    .sort((a, b) => {
      const byPercent = Number(a.percent) - Number(b.percent)
      if (byPercent !== 0) return byPercent
      return Number(b.total) - Number(a.total)
    })
}

function taskMatchesLanguage(rec: TcTaskRecommendation, language: string): boolean {
  const taskLang = normalizeLangCode(rec.language)
  const selected = normalizeLangCode(language)
  if (!taskLang || !selected) return true
  return taskLang === selected
}

function buildTips(
  analytics: NonNullable<StudentProfileProgressPanelProps["analytics"]>,
): string[] {
  const tips: string[] = []
  const seen = new Set<string>()
  const push = (text: string) => {
    const line = String(text || "").trim()
    if (!line || seen.has(line)) return
    seen.add(line)
    tips.push(line)
  }

  const structured = analytics.student_recommendations
  push(String(structured?.streak?.message || ""))

  for (const topic of structured?.weak_topics || []) {
    if (tips.length >= MAX_TIP_LINES) break
    push(topic.recommendation || `Подтяните тему «${topic.name}»`)
  }

  for (const text of structured?.errors || []) {
    if (tips.length >= MAX_TIP_LINES) break
    push(text)
  }

  for (const text of structured?.next_steps || []) {
    if (tips.length >= MAX_TIP_LINES) break
    push(text)
  }

  if (tips.length === 0) {
    for (const rec of analytics.recommendations || []) {
      if (tips.length >= MAX_TIP_LINES) break
      push(rec.message)
    }
  }

  return tips.slice(0, MAX_TIP_LINES)
}

function buildTaskRecommendations(
  analytics: NonNullable<StudentProfileProgressPanelProps["analytics"]>,
  language: string,
): TcTaskRecommendation[] {
  const byLang = analytics.tc_task_recommendations_by_language?.[language]
  const source = byLang?.length
    ? byLang
    : (analytics.tc_task_recommendations || []).filter((rec) => taskMatchesLanguage(rec, language))
  return source
    .filter((rec) => Number(rec?.task_id || 0) > 0)
    .slice(0, MAX_TASK_RECOMMENDATIONS)
}

export default function StudentProfileProgressPanel({
  analytics,
}: StudentProfileProgressPanelProps) {
  const navigate = useNavigate()
  const languageOptions = useMemo(
    () => (analytics ? resolveLanguageOptions(analytics) : []),
    [analytics],
  )
  const [skillLanguage, setSkillLanguage] = useState<CurriculumLearningLanguage>(() =>
    analytics ? pickInitialLanguage(analytics, languageOptions) : readStoredLearningLanguage(),
  )

  useEffect(() => {
    if (!analytics) return
    const options = resolveLanguageOptions(analytics)
    setSkillLanguage((current) => {
      if (options.some((row) => row.code === current)) return current
      return pickInitialLanguage(analytics, options)
    })
  }, [analytics])

  const selectorOptions =
    languageOptions.length > 0
      ? languageOptions
      : CURRICULUM_LANGUAGE_OPTIONS.map((opt) => ({ code: opt.id, label: opt.label }))

  if (!analytics) {
    return (
      <div className="cards2">
        <div className="card card-pad">
          <b style={{ fontSize: 15 }}>Навыки</b>
          <p className="mut3" style={{ fontSize: 12.5, margin: "14px 0 0" }}>
            Статистика появится после решения задач.
          </p>
        </div>
        <div className="card card-pad">
          <b style={{ fontSize: 15 }}>Рекомендации</b>
          <p className="mut3" style={{ fontSize: 12.5, margin: "14px 0 0" }}>
            Персональные подсказки появятся после первых попыток.
          </p>
        </div>
      </div>
    )
  }

  const { rows: skillRows, usingStructureFallback } = pickSkillRows(analytics, skillLanguage)
  const taskRecommendations = buildTaskRecommendations(analytics, skillLanguage)
  const tips = buildTips(analytics)
  const solvedCount = Number(analytics.overview?.solved_count || 0)
  const activeLanguageLabel =
    selectorOptions.find((row) => row.code === skillLanguage)?.label || skillLanguage

  return (
    <div className="cards2">
      <div className="card card-pad">
        <div className="between" style={{ marginBottom: 4 }}>
          <b style={{ fontSize: 15 }}>Навыки</b>
          <LanguageBadgeSelect
            value={skillLanguage}
            options={selectorOptions}
            onChange={setSkillLanguage}
          />
        </div>
        <p className="mut3" style={{ fontSize: 12.5, margin: "4px 0 16px" }}>
          {usingStructureFallback
            ? "Доля решённых заданий по группам конструкций."
            : "Доля решённых заданий по группам тем курса."}
        </p>
        {skillRows.length > 0 ? (
          <div className="grid" style={{ gap: 14 }}>
            {skillRows.map((row, index) => (
              <SkillProgressRow key={row.id || index} row={row} />
            ))}
          </div>
        ) : (
          <p className="mut3" style={{ fontSize: 12.5, lineHeight: 1.45 }}>
            {solvedCount > 0
              ? `Для ${activeLanguageLabel} пока нет прогресса. Решайте задачи из «Курсы».`
              : `Начните курс на ${activeLanguageLabel} — здесь появятся навыки.`}
          </p>
        )}
      </div>

      <div className="card card-pad">
        <b style={{ fontSize: 15 }}>Рекомендации</b>
        <p className="mut3" style={{ fontSize: 12.5, margin: "4px 0 16px" }}>
          С чего продолжить, чтобы подтянуть слабые темы.
        </p>
        {taskRecommendations.length > 0 || tips.length > 0 ? (
          <>
            {taskRecommendations.length > 0 ? (
              <div className="grid" style={{ gap: 10 }}>
                {taskRecommendations.map((rec) => (
                  <TaskRecommendationCard
                    key={rec.task_id}
                    rec={rec}
                    onOpen={() => navigate(`/tasks/${rec.task_id}`)}
                  />
                ))}
              </div>
            ) : null}
            {taskRecommendations.length > 0 && tips.length > 0 ? (
              <div className="divider" style={{ margin: "16px 0" }} />
            ) : null}
            {tips.length > 0 ? (
              <div className="grid" style={{ gap: 10 }}>
                {tips.map((text, index) => (
                  <TipRow key={`${index}-${text.slice(0, 24)}`} text={text} />
                ))}
              </div>
            ) : null}
          </>
        ) : (
          <p className="mut3" style={{ fontSize: 12.5, lineHeight: 1.45 }}>
            {solvedCount > 0
              ? "Продолжайте курс — подскажем задачи по слабым темам."
              : "Решите первую задачу — мы предложим, с чего продолжить."}
          </p>
        )}
      </div>
    </div>
  )
}
