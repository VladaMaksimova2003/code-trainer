import { useMemo } from "react"
import {
  canSwapCurriculumMirrorTrack,
  canSwapParallelLanguages,
  isKnownLanguageOptionDisabled,
  isLearningLanguageOptionDisabled,
  langDisplay,
} from "@/features/task-solving/model/studentUiUtils"
import type { TaskDto } from "@/shared/types/task"

function SwapIcon() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M3 5h9M9 2l3 3-3 3" />
      <path d="M13 11H4M7 14l-3-3 3-3" />
    </svg>
  )
}

function useLanguageOptions(languages: string[] | undefined) {
  return useMemo(() => {
    if (!Array.isArray(languages)) return []
    return languages.map((id) => String(id).toLowerCase()).filter(Boolean)
  }, [languages])
}

interface StudentParallelLanguageBarProps {
  task?: TaskDto | null
  knownLanguage: string
  learningLanguage: string
  knownLanguages?: string[]
  learningLanguages?: string[]
  languages?: string[]
  showKnownSelector?: boolean
  onKnownLanguageChange?: (language: string) => void
  onLearningLanguageChange?: (language: string) => void
  onSwap?: () => void
}

export function StudentParallelLanguageBar({
  task = null,
  knownLanguage,
  learningLanguage,
  knownLanguages = [],
  learningLanguages = [],
  languages = [],
  showKnownSelector = true,
  onKnownLanguageChange,
  onLearningLanguageChange,
  onSwap,
}: StudentParallelLanguageBarProps) {
  const knownOptions = useLanguageOptions(knownLanguages)
  const learningOptions = useLanguageOptions(
    learningLanguages.length ? learningLanguages : languages,
  )
  const mirrorSwap = canSwapCurriculumMirrorTrack(task, knownLanguage, learningLanguage)
  const swapEnabled = canSwapParallelLanguages(
    knownLanguage,
    learningLanguage,
    knownOptions,
    learningOptions,
    task,
  )
  const swapTitle = swapEnabled
    ? mirrorSwap
      ? "Переключить сборник: Pascal ↔ Python"
      : "Поменять языки местами"
    : "Нельзя поменять: языки совпадают или доступен только один вариант"

  return (
    <div className="flex shrink-0 justify-center border-b border-border bg-surface/40">
      <div className="flex flex-nowrap items-center justify-center gap-2 px-4 py-2.5">
        {showKnownSelector ? (
          <>
            <span className="mut3 shrink-0 text-[12px]">Я знаю</span>
            <select
              value={knownLanguage || ""}
              onChange={(e) => onKnownLanguageChange?.(e.target.value)}
              className="select-inline h-[34px] shrink-0 py-1 px-2 text-[13px]"
            >
              {knownOptions.map((lang) => (
                <option
                  key={lang}
                  value={lang}
                  disabled={isKnownLanguageOptionDisabled(lang, learningLanguage, task)}
                >
                  {langDisplay(lang)}
                </option>
              ))}
            </select>
          </>
        ) : null}

        <button
          type="button"
          onClick={onSwap}
          disabled={!swapEnabled}
          className="btn btn-ghost btn-sm btn-icon shrink-0"
          title={swapTitle}
        >
          <SwapIcon />
        </button>

        <span className="mut3 shrink-0 text-[12px]">Учу</span>
        <select
          value={learningLanguage || ""}
          onChange={(e) => onLearningLanguageChange?.(e.target.value)}
          className="select-inline h-[34px] shrink-0 py-1 px-2 text-[13px]"
        >
          {learningOptions.map((lang) => (
            <option
              key={lang}
              value={lang}
              disabled={isLearningLanguageOptionDisabled(lang, knownLanguage, task)}
            >
              {langDisplay(lang)}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}

interface StudentLearningLanguageBarProps {
  learningLanguage: string
  languages?: string[]
  onLearningLanguageChange?: (language: string) => void
}

export function StudentLearningLanguageBar({
  learningLanguage,
  languages = [],
  onLearningLanguageChange,
}: StudentLearningLanguageBarProps) {
  const options = useLanguageOptions(languages)

  return (
    <div className="flex shrink-0 justify-center border-b border-border bg-surface/40">
      <div className="flex flex-nowrap items-center justify-center gap-2 px-4 py-2.5">
        <span className="mut3 shrink-0 text-[12px]">Язык решения</span>
        <select
          value={learningLanguage || ""}
          onChange={(e) => onLearningLanguageChange?.(e.target.value)}
          className="select-inline h-[34px] shrink-0 py-1 px-2 text-[13px]"
        >
          {options.map((lang) => (
            <option key={lang} value={lang}>
              {langDisplay(lang)}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}

interface StudentFlowchartModeBarProps {
  solutionMode?: "code" | "flow" | string
  swapEnabled?: boolean
  swapDisabledReason?: string
  onSwap?: () => void
  learningLanguage?: string
  languages?: string[]
  onLearningLanguageChange?: (language: string) => void
  showLanguageSelect?: boolean
}

export function StudentFlowchartModeBar({
  solutionMode = "code",
  swapEnabled = false,
  swapDisabledReason = "no_code",
  onSwap,
  learningLanguage,
  languages = [],
  onLearningLanguageChange,
  showLanguageSelect = true,
}: StudentFlowchartModeBarProps) {
  const options = useLanguageOptions(languages)
  const isFlowMode = solutionMode === "flow"
  const swapTitle = swapEnabled
    ? "Поменять режим: блок-схема ↔ код"
    : swapDisabledReason === "diagram_given"
      ? "Составление схемы недоступно: нет эталонного кода от преподавателя"
      : "Составление схемы недоступно: преподаватель не дал эталонный код"

  return (
    <div className="flex flex-nowrap items-center justify-center gap-2 px-4">
      <span
        className={`shrink-0 text-[12px] ${
          isFlowMode ? "text-ink font-medium" : "mut3"
        }`}
      >
        Блок-схема
      </span>

      <button
        type="button"
        onClick={swapEnabled ? onSwap : undefined}
        disabled={!swapEnabled}
        aria-disabled={!swapEnabled}
        className="btn btn-ghost btn-sm btn-icon shrink-0"
        title={swapTitle}
      >
        <SwapIcon />
      </button>

      {showLanguageSelect && !isFlowMode && options.length > 0 && (
        <select
          value={learningLanguage || ""}
          onChange={(e) => onLearningLanguageChange?.(e.target.value)}
          className="select-inline h-[34px] shrink-0 py-1 px-2 text-[13px]"
          aria-label="Язык решения"
        >
          {options.map((lang) => (
            <option key={lang} value={lang}>
              {langDisplay(lang)}
            </option>
          ))}
        </select>
      )}
    </div>
  )
}
