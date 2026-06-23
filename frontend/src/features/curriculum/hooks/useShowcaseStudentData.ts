import { useCallback, useEffect, useRef, useState } from "react"
import { useLocation } from "react-router-dom"

import { getShowcase, getShowcaseNext } from "@/features/curriculum/api/curriculumApi"
import type {
  CurriculumShowcaseNextDto,
  CurriculumShowcaseStudentDto,
} from "@/shared/types/curriculum"

export function useShowcaseStudentData(
  language: string,
  chapterSlug: string,
  userId?: number | string | null,
) {
  const location = useLocation()
  const [data, setData] = useState<CurriculumShowcaseStudentDto | null>(null)
  const [next, setNext] = useState<CurriculumShowcaseNextDto | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const hasDataRef = useRef(false)

  const load = useCallback(async () => {
    if (!chapterSlug) return
    if (!hasDataRef.current) setLoading(true)
    setError(null)
    try {
      const [showcase, nextData] = await Promise.all([
        getShowcase(language, chapterSlug),
        getShowcaseNext(language, chapterSlug).catch(() => null),
      ])
      setData(showcase)
      setNext(nextData)
      hasDataRef.current = true
    } catch {
      setError("Не удалось загрузить сборник. Попробуйте обновить страницу.")
    } finally {
      setLoading(false)
    }
  }, [language, chapterSlug, userId])

  useEffect(() => {
    hasDataRef.current = false
    setData(null)
    setNext(null)
    void load()
  }, [load, location.key])

  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === "visible") {
        void load()
      }
    }
    window.addEventListener("focus", onVisible)
    document.addEventListener("visibilitychange", onVisible)
    return () => {
      window.removeEventListener("focus", onVisible)
      document.removeEventListener("visibilitychange", onVisible)
    }
  }, [load])

  return { data, next, loading, error, reload: load }
}
