import { useCallback } from "react"
import type { NavigateFunction } from "react-router-dom"
import { taskSupportsLearningLanguageLocally } from "@/features/task-solving/model/curriculumMirrorNavigation"
import { normalizeCurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"
import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"
import type { TaskDto } from "@/shared/types/task"

interface UseCurriculumMirrorLanguageOptions {
  task: TaskDto | null
  userLanguage: string
  navigate: NavigateFunction
  onLearningLanguageChange: (language: string) => void
  onKnownLanguageChange?: (language: string) => void
  onStayOnTaskLanguageChange?: (language: CurriculumLearningLanguage) => void
}

export function useCurriculumMirrorLanguage({
  task,
  onLearningLanguageChange,
  onKnownLanguageChange,
  onStayOnTaskLanguageChange,
}: UseCurriculumMirrorLanguageOptions) {
  const handleUserLanguageChange = useCallback(
    (nextLanguage: string) => {
      if (task && taskSupportsLearningLanguageLocally(task, nextLanguage)) {
        const normalized = normalizeCurriculumLearningLanguage(nextLanguage)
        if (normalized) {
          onStayOnTaskLanguageChange?.(normalized)
        }
      }
      onLearningLanguageChange(nextLanguage)
    },
    [task, onLearningLanguageChange, onStayOnTaskLanguageChange],
  )

  const handleKnownLanguageChange = useCallback(
    (nextLanguage: string) => {
      if (!onKnownLanguageChange) return
      onKnownLanguageChange(nextLanguage)
    },
    [onKnownLanguageChange],
  )

  return {
    handleUserLanguageChange,
    handleKnownLanguageChange,
  }
}
