import { useMemo, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { formatTaskActivityLabel } from "@/shared/types/taskLabels"
import { langDisplay } from "@/features/task-solving/model/studentUiUtils"
import StudentHeaderActions from "@/features/student/layout/StudentHeaderActions"
import ReportTaskIssueModal from "@/features/support/components/ReportTaskIssueModal"
import { fetchCurriculumNext } from "@/features/curriculum/api/curriculumApi"
import type { TaskDto } from "@/shared/types/task"
import {
  resolveBackLabel,
  resolveBackTarget,
  resolveHasNext,
  resolveHasPrev,
  resolveNextTaskAction,
  resolvePrevTaskAction,
  findTaskIndex,
  resolveOrderedTaskIds,
  isCollectionNavigation,
} from "@/features/task-solving/model/taskNavigationHelpers"

interface CurriculumNavigation {
  task_ids?: number[]
  prev_task_id?: number | null
  prev_collection_id?: string | number | null
  next_task_id?: number | null
  next_collection_id?: string | number | null
  course_completed?: boolean
  collection_id?: string | number | null
  collection_title_ru?: string
  task_index?: number
  total_tasks?: number
}

interface StudentTaskHeaderProps {
  user?: unknown | null
  task: TaskDto | null | undefined
  id?: string | number
  navigationMode?: string
  collectionId?: string | number | null
  manualTaskIds?: number[]
  fetchedCollectionNav?: CurriculumNavigation | null
  onAdaptiveNext?: () => void | Promise<void>
  adaptiveLoading?: boolean
  knownLanguage?: string
  learningLanguage?: string
  exampleLanguages?: string[]
  learningLanguages?: string[]
  onKnownLanguageChange?: (language: string) => void
  onLearningLanguageChange?: (language: string) => void
  onSwap?: () => void
  showLanguageBar?: boolean
  taskId?: string | number
  activeSubmissionId?: number | string | null
  issueContext?: unknown | null
  isTeacherReview?: boolean
}

export default function StudentTaskHeader({
  user = null,
  task,
  id,
  navigationMode,
  collectionId,
  manualTaskIds,
  fetchedCollectionNav = null,
  onAdaptiveNext,
  adaptiveLoading,
  knownLanguage,
  learningLanguage,
  onKnownLanguageChange,
  onLearningLanguageChange,
  onSwap,
  showLanguageBar,
  taskId,
  activeSubmissionId = null,
  issueContext = null,
  isTeacherReview = false,
}: StudentTaskHeaderProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const locationState = location.state as {
    returnTo?: string
    learningLanguage?: string
    navigationMode?: string
    collectionId?: string | number | null
  } | null
  const returnTo =
    locationState?.returnTo ||
    (task?.curriculum as { navigation?: { return_path?: string } } | undefined)?.navigation?.return_path
  const [reportOpen, setReportOpen] = useState(false)
  const [reportNotice, setReportNotice] = useState("")

  const collectionNav =
    (task?.curriculum as { navigation?: CurriculumNavigation } | undefined)?.navigation ||
    fetchedCollectionNav ||
    undefined

  const orderedTaskIds = resolveOrderedTaskIds(collectionNav?.task_ids, manualTaskIds ?? [])
  const isCollectionNav = isCollectionNavigation(
    navigationMode || "",
    orderedTaskIds,
    Boolean(collectionNav?.task_ids?.length),
  )

  const index = findTaskIndex(orderedTaskIds, id ?? taskId ?? "")
  const hasPrev = resolveHasPrev(isCollectionNav, collectionNav, index)
  const hasNext =
    collectionNav?.next_task_id != null ||
    resolveHasNext(isCollectionNav, collectionNav, index, orderedTaskIds.length)
  const taskIndex =
    collectionNav?.task_index ?? (index >= 0 ? index + 1 : Number(id))
  const totalTasks =
    collectionNav?.total_tasks ?? (orderedTaskIds.length > 0 ? orderedTaskIds.length : "—")

  const taskTypeLabel = useMemo(() => formatTaskActivityLabel(task), [task])
  const difficultyLabel = useMemo(() => {
    const d = String(task?.difficulty || "").toLowerCase()
    if (!d) return null
    if (d === "easy") return "Лёгкая"
    if (d === "medium") return "Средняя"
    if (d === "hard") return "Сложная"
    return task?.difficulty
  }, [task?.difficulty])

  const backLabel = resolveBackLabel(returnTo)

  const goTask = (nextTaskId: number | string, nextCollectionId: string | number | null = null) => {
    navigate(`/tasks/${nextTaskId}`, {
      state: {
        navigationMode: navigationMode === "manual" ? "manual" : "curriculum",
        collectionId:
          nextCollectionId || collectionId || collectionNav?.collection_id || null,
        returnTo,
        learningLanguage: learningLanguage || locationState?.learningLanguage,
      },
    })
  }

  const goPrev = () => {
    const action = resolvePrevTaskAction(collectionNav, index, orderedTaskIds)
    if (action?.kind === "task") {
      goTask(action.taskId, action.collectionId)
    }
  }

  const goNext = async () => {
    const action = resolveNextTaskAction({
      collectionNav,
      index,
      orderedTaskIds,
      hasAdaptiveNext: Boolean(onAdaptiveNext),
    })
    if (action?.kind === "task") {
      goTask(action.taskId, action.collectionId)
      return
    }
    if (action?.kind === "returnTo") {
      navigate(returnTo || "/")
      return
    }
    if (action?.kind === "adaptive") {
      await onAdaptiveNext?.()
      return
    }
    if (action?.kind === "curriculumNext") {
      try {
        const payload = await fetchCurriculumNext()
        if (payload?.completed) {
          navigate(returnTo || "/")
          return
        }
        if (payload?.next_task?.task_id) {
          goTask(payload.next_task.task_id, payload?.collection?.collection_id)
        }
      } catch {
        /* navigation fallback failed */
      }
    }
  }

  const goBack = () => {
    navigate(resolveBackTarget(returnTo))
  }

  return (
    <header className="topbar task-page-header shrink-0" style={{ padding: "12px 20px" }}>
      <div className="flex w-full flex-col gap-2">
        <div className="row flex flex-wrap items-center gap-2">
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={goBack}
            title={backLabel}
          >
            ← {backLabel}
          </button>
          <div className="crumb">
            {taskTypeLabel}
            {task?.title ? (
              <>
                {" "}
                / <b>{task.title}</b>
              </>
            ) : null}
          </div>
          {difficultyLabel && <span className="badge badge-muted">{difficultyLabel}</span>}
          {showLanguageBar && knownLanguage && (
            <span className="badge badge-purple">{langDisplay(knownLanguage)}</span>
          )}
          {!isTeacherReview && task?.title ? (
            <button
              type="button"
              className="btn btn-ghost btn-sm text-ink-faint"
              onClick={() => setReportOpen(true)}
            >
              Сообщить об ошибке
            </button>
          ) : null}
          <div className="flex-1" />
          <StudentHeaderActions user={user} />
        </div>

        <div className="row flex flex-wrap items-center gap-2">
          <span className="muted" style={{ fontSize: 13 }}>
            {collectionNav?.collection_title_ru
              ? `«${collectionNav.collection_title_ru}» · `
              : ""}
            Задача {taskIndex} из {totalTasks}
          </span>
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            disabled={!hasPrev}
            onClick={goPrev}
            title="Предыдущая"
          >
            ← Предыдущая
          </button>
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            disabled={isCollectionNav ? !hasNext : adaptiveLoading}
            onClick={goNext}
            title="Следующая"
          >
            Следующая →
          </button>
        </div>
      </div>

      {reportNotice ? (
        <div className="border-b border-lime/30 bg-lime-soft/30 px-5 py-2 text-[13px] text-ink">
          {reportNotice}{" "}
          <button type="button" className="text-lime underline" onClick={() => navigate("/support")}>
            Мои обращения
          </button>
        </div>
      ) : null}

      <ReportTaskIssueModal
        open={reportOpen}
        onClose={() => setReportOpen(false)}
        taskId={taskId ?? task?.id}
        taskTitle={task?.title}
        submissionId={activeSubmissionId}
        issueContext={issueContext}
        onSuccess={(ticket: { id?: number | string; target?: string }) => {
          const target =
            ticket?.target === "teacher" ? "преподавателю" : "в поддержку"
          setReportNotice(`Обращение #${ticket.id} отправлено ${target}.`)
        }}
      />
    </header>
  )
}
