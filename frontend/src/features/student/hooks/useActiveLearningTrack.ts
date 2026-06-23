import { useEffect, useState } from "react"
import {
  LEARNING_LANG_CHANGED_EVENT,
  readStoredLearningLanguage,
} from "@/features/curriculum/curriculumLanguageUi"
import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"

/** Keeps TasksPage subtitle in sync with the last active curriculum track. */
export function useActiveLearningTrack(): CurriculumLearningLanguage {
  const [track, setTrack] = useState<CurriculumLearningLanguage>(() => readStoredLearningLanguage())

  useEffect(() => {
    const sync = () => setTrack(readStoredLearningLanguage())
    window.addEventListener(LEARNING_LANG_CHANGED_EVENT, sync)
    window.addEventListener("storage", sync)
    return () => {
      window.removeEventListener(LEARNING_LANG_CHANGED_EVENT, sync)
      window.removeEventListener("storage", sync)
    }
  }, [])

  return track
}
