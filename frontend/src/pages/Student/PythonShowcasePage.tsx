import { useNavigate, useParams } from "react-router-dom"

import CurriculumProgressBar from "@/features/curriculum/components/CurriculumProgressBar"
import CurriculumStates from "@/features/curriculum/components/CurriculumStates"
import {
  resolveShowcaseStartTaskId,
  showcaseStartButtonLabel,
} from "@/features/curriculum/components/showcaseCollectionPageHelpers"
import SubtopicSection, { sectionsOf } from "@/features/curriculum/components/SubtopicSection"
import { useShowcaseStudentData } from "@/features/curriculum/hooks/useShowcaseStudentData"
import { progressPercent } from "@/features/curriculum/actionMeta"
import type { CurriculumNavState } from "@/features/curriculum/types"
import LearningAppShell from "@/features/student/layout/LearningAppShell"

const LANGUAGE = "python"
const HUB_PATH = "/learn/python"

interface PythonShowcasePageProps {
  user?: { id?: number | string } | null
  onSignOut?: () => void
}

export default function PythonShowcasePage({ user, onSignOut }: PythonShowcasePageProps) {
  const navigate = useNavigate()
  const { chapterSlug = "" } = useParams<{ chapterSlug: string }>()
  const returnTo = `${HUB_PATH}/${chapterSlug}`
  const isGuest = !user

  const { data, next, loading, error, reload: load } = useShowcaseStudentData(
    LANGUAGE,
    chapterSlug,
    user?.id,
  )

  const openTask = (taskId: number) => {
    const state: CurriculumNavState = {
      returnTo,
      navigationMode: "curriculum",
      collectionId: data?.collection_id ?? chapterSlug,
      learningLanguage: LANGUAGE,
    }
    navigate(`/tasks/${taskId}`, { state })
  }

  const continueCollection = () => {
    const taskId = resolveShowcaseStartTaskId(data, next)
    if (!taskId) return
    openTask(taskId)
  }

  const progress = data?.progress ?? null
  const hasProgress = !isGuest && !!progress
  const percent = progressPercent(progress)
  const startTaskId = resolveShowcaseStartTaskId(data, next)
  const buttonLabel = showcaseStartButtonLabel(isGuest, next)
  const sections = data ? sectionsOf(data) : []
  const title = data?.title_ru ?? "Сборник"
  const description =
    data?.description_ru ??
    (typeof data?.learning_concept === "object" && data?.learning_concept
      ? String((data.learning_concept as { description_ru?: string }).description_ru ?? "")
      : "")

  return (
    <LearningAppShell user={user} onSignOut={onSignOut}>
      <div className="mx-auto max-w-[960px] px-4 py-7 sm:px-6">
        <CurriculumStates
          loading={loading}
          error={error}
          empty={!loading && !error && !data}
          loadingText="Загрузка сборника…"
          onRetry={load}
        >
          {data && (
            <>
              <button type="button" className="btn btn-ghost btn-sm mb-3.5" onClick={() => navigate(HUB_PATH)}>
                ← Все сборники
              </button>

              <div className="mb-1 flex flex-wrap items-end justify-between gap-4">
                <div className="min-w-0">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <span className="text-[13px] text-ink-faint">{data.total_tasks} задач</span>
                  </div>
                  <h1 className="m-0 mb-1 text-[26px] font-extrabold tracking-[-0.6px] text-ink">
                    <span className="text-[18px] font-semibold text-ink-faint">Python / </span>
                    {title}
                  </h1>
                  {description ? <p className="m-0 text-[14px] text-ink-muted">{description}</p> : null}
                </div>
                <div className="flex flex-wrap gap-2.5">
                  <button
                    type="button"
                    className="btn btn-primary btn-sm"
                    disabled={!startTaskId}
                    onClick={continueCollection}
                  >
                    ▸ {buttonLabel}
                  </button>
                </div>
              </div>

              {hasProgress ? (
                <div className="my-6 rounded-2xl border border-border bg-surface p-5">
                  <div className="mb-3 flex flex-wrap items-center justify-between gap-2.5">
                    <b className="text-[14px] text-ink">Прогресс сборника</b>
                    <span className="font-mono text-[13px] text-ink-faint">
                      {progress!.passed_tasks}/{progress!.total_tasks} · {percent}%
                    </span>
                  </div>
                  <CurriculumProgressBar percent={percent} />
                </div>
              ) : null}

              <div className="grid gap-[30px]">
                {sections.map((section, i) => (
                  <SubtopicSection
                    key={section.id ?? section.name_ru ?? i}
                    section={section}
                    index={i + 1}
                    isGuest={isGuest}
                    onOpenTask={openTask}
                  />
                ))}
              </div>
            </>
          )}
        </CurriculumStates>
      </div>
    </LearningAppShell>
  )
}
