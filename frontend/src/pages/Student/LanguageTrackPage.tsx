import { useCallback, useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { getLanguageTrack, resolveCollectionNextTaskId } from "@/features/curriculum/api/curriculumApi"
import ChapterCard from "@/features/curriculum/components/ChapterCard"
import LangMini from "@/features/curriculum/components/LangMini"
import CurriculumStates from "@/features/curriculum/components/CurriculumStates"
import { progressPercent, displayCollectionTotal, displayTrackTotal } from "@/features/curriculum/actionMeta"
import {
  LANGUAGE_GLYPHS,
  LANGUAGE_LABELS,
  LANGUAGE_TRACK_DESCRIPTIONS,
  writeStoredLearningLanguage,
} from "@/features/curriculum/curriculumLanguageUi"
import { useCurriculumCollections } from "@/features/curriculum/hooks/useCurriculumCollections"
import type { Collection, CurriculumNavState, LanguageTrack } from "@/features/curriculum/types"
import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import Badge from "@/shared/ui/Badge"
import { toast } from "@/shared/ui/toast"

interface LanguageTrackPageProps {
  language: CurriculumLearningLanguage
  user?: { id?: number | string } | null
  onSignOut?: () => void
}

function trackWithoutProgress(track: LanguageTrack): LanguageTrack {
  return {
    ...track,
    progress: {
      ...track.progress,
      passed_tasks: 0,
      progress_percent: 0,
    },
    collections: track.collections.map((chapter) => ({
      ...chapter,
      completed: false,
      progress: {
        ...chapter.progress,
        passed_tasks: 0,
        progress_percent: 0,
      },
    })),
  }
}

export default function LanguageTrackPage({ language, user, onSignOut }: LanguageTrackPageProps) {
  const navigate = useNavigate()
  const hubPath = `/learn/${language}`
  const [track, setTrack] = useState<LanguageTrack | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [continueLoading, setContinueLoading] = useState(false)

  const guestMode = !user
  const { data: collectionsData } = useCurriculumCollections(undefined, {
    authenticated: !guestMode,
    userId: user?.id,
  })

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const loaded = await getLanguageTrack(language)
      setTrack(guestMode && loaded ? trackWithoutProgress(loaded) : loaded)
      writeStoredLearningLanguage(language)
    } catch {
      setError("Не удалось загрузить трек. Попробуйте обновить страницу.")
    } finally {
      setLoading(false)
    }
  }, [language, guestMode])

  useEffect(() => {
    void load()
  }, [load, user?.id])

  const openChapter = (c: Collection) => navigate(c.route_path)

  const continueChapter = async (c: Collection) => {
    setContinueLoading(true)
    try {
      const taskId = await resolveCollectionNextTaskId(language, c)
      if (!taskId) {
        toast.info("Обучение", "Нет доступных задач в этом сборнике")
        return
      }
      const state: CurriculumNavState = {
        returnTo: hubPath,
        navigationMode: "curriculum",
        collectionId: c.collection_id,
        learningLanguage: language,
      }
      navigate(`/tasks/${taskId}`, { state })
    } catch {
      toast.error("Не удалось получить следующую задачу")
    } finally {
      setContinueLoading(false)
    }
  }

  const nextChapter = guestMode
    ? null
    : track?.collections.find(
        (c) => !c.completed && displayCollectionTotal(c.progress) > 0,
      ) ?? null
  const agg = track?.progress
  const aggTotal = displayTrackTotal(track)
  const aggPassed = guestMode ? 0 : (agg?.passed_tasks ?? 0)
  const aggPercent = guestMode
    ? 0
    : progressPercent({
        ...agg,
        catalog_tasks: agg?.catalog_tasks ?? aggTotal,
      })
  const trackComplete =
    !guestMode && Boolean(agg && aggTotal > 0 && aggPassed >= aggTotal)
  const trackDescription =
    track?.track_description_ru?.trim() || LANGUAGE_TRACK_DESCRIPTIONS[language] || ""

  return (
    <LearningAppShell user={user} onSignOut={onSignOut}>
      <div className="content mx-auto max-w-[920px] px-4 py-7 sm:px-6">
        <CurriculumStates loading={loading} error={error} loadingText="Загрузка трека…" onRetry={load}>
          {track ? (
            <>
              <div className="track-hero mb-6">
                <div className="flex flex-wrap items-start gap-[18px]">
                  <div className="track-glyph">{LANGUAGE_GLYPHS[language]}</div>
                  <div className="min-w-0 flex-[1_1_280px]">
                    <div className="mb-1.5 flex flex-wrap items-center gap-2.5">
                      <Badge kind="purple">Учебный трек</Badge>
                      {trackComplete ? <Badge kind="lime">✓ Трек пройден</Badge> : null}
                      <LangMini language={language} availableLanguages={collectionsData?.languages} />
                    </div>
                    <h1 className="m-0 mb-1.5 text-[30px] font-extrabold tracking-[-0.8px] text-ink">
                      {track.language_label ?? LANGUAGE_LABELS[language]}
                    </h1>
                    <p className="m-0 max-w-[440px] text-[14.5px] text-ink-muted">
                      {trackDescription}
                    </p>
                  </div>
                  <div className="min-w-[140px] text-right">
                    <div className="text-[34px] font-extrabold tracking-[-0.5px] text-lime">{aggPercent}%</div>
                    <div className="mb-2.5 font-mono text-[12.5px] text-ink-faint">
                      {aggPassed}/{aggTotal} задач
                    </div>
                    <div className="progress">
                      <i style={{ width: `${aggPercent}%` }} />
                    </div>
                  </div>
                </div>

                {nextChapter ? (
                  <div className="mt-[22px] flex flex-wrap items-center justify-between gap-3.5 border-t border-border pt-5">
                    <div>
                      <div className="mb-0.5 text-[12px] uppercase tracking-[0.06em] text-ink-faint">
                        Продолжить с
                      </div>
                      <b className="text-[15px] text-ink">{nextChapter.title_ru}</b>
                    </div>
                    <button
                      type="button"
                      className="btn btn-primary"
                      disabled={continueLoading}
                      onClick={() => void continueChapter(nextChapter)}
                    >
                      {continueLoading ? "…" : "▸ Продолжить обучение"}
                    </button>
                  </div>
                ) : null}
              </div>

              <div className="mb-4 flex items-center justify-between">
                <h2 className="m-0 text-[18px] font-bold text-ink">Сборники</h2>
                <span className="text-[13px] text-ink-faint">{track.collections.length} глав</span>
              </div>

              <div className="roadmap">
                {track.collections.map((c, i) => (
                  <ChapterCard
                    key={c.collection_id}
                    chapter={c}
                    isCurrent={!guestMode && nextChapter?.collection_id === c.collection_id}
                    isLast={i === track.collections.length - 1}
                    onOpen={openChapter}
                    onContinue={guestMode ? undefined : continueChapter}
                  />
                ))}
              </div>
            </>
          ) : null}
        </CurriculumStates>
      </div>
    </LearningAppShell>
  )
}
