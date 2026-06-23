import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import Badge from "@/shared/ui/Badge"
import LoadingBlock from "@/shared/ui/LoadingBlock"
import {
  LANGUAGE_GLYPHS,
  LANGUAGE_LABELS,
  readStoredLearningLanguage,
  writeStoredLearningLanguage,
  languageRoute,
} from "@/features/curriculum/curriculumLanguageUi"
import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"
import { displayTrackTotal, progressPercent } from "@/features/curriculum/actionMeta"
import { resolveCollectionNextTaskId } from "@/features/curriculum/api/curriculumApi"
import { writeNavigationContext } from "@/features/task-solving/model/navigationContext"
import { toast } from "@/shared/ui/toast"

interface CurriculumLanguageRow {
  language: string
  language_label?: string
  available?: boolean
  progress?: {
    total_tasks?: number
    passed_tasks?: number
    progress_percent?: number
    catalog_tasks?: number
  }
  collections?: Array<{
    collection_id?: string
    title_ru?: string
    order?: number
    completed?: boolean
    route_path?: string
    next_task?: { task_id?: number; title?: string } | null
    progress?: {
      total_tasks?: number
      catalog_tasks?: number
      passed_tasks?: number
    }
  }>
}

interface CurriculumTrackBannerProps {
  languages?: CurriculumLanguageRow[]
  loading?: boolean
  error?: string | null
  taskPathPrefix?: string
  /** Demo / unauthenticated — no saved progress, hide continue banner. */
  guestMode?: boolean
}

function firstIncompleteCollection(lang: CurriculumLanguageRow | undefined) {
  return lang?.collections?.find((c) => !c.completed) ?? null
}

export default function CurriculumTrackBanner({
  languages = [],
  loading = false,
  error = null,
  taskPathPrefix = "/tasks",
  guestMode = false,
}: CurriculumTrackBannerProps) {
  const navigate = useNavigate()
  const [selectedLang, setSelectedLang] = useState<CurriculumLearningLanguage>(() =>
    readStoredLearningLanguage(),
  )
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    writeStoredLearningLanguage(selectedLang)
  }, [selectedLang])

  const selected = useMemo(
    () => languages.find((l) => l.language === selectedLang) ?? languages.find((l) => l.available !== false),
    [languages, selectedLang],
  )

  useEffect(() => {
    if (!selected?.language) return
    const lang = selected.language as CurriculumLearningLanguage
    if (lang !== selectedLang) setSelectedLang(lang)
  }, [selected?.language, selectedLang])

  const progress = selected?.progress
  const total = displayTrackTotal(selected)
  const passed = progress?.passed_tasks ?? 0
  const percent = progressPercent({
    passed_tasks: passed,
    total_tasks: progress?.total_tasks,
    catalog_tasks: progress?.catalog_tasks ?? total,
    progress_percent: progress?.progress_percent,
  })
  const nextCollection = firstIncompleteCollection(selected)
  const langKey = (selected?.language ?? selectedLang) as CurriculumLearningLanguage
  const glyph = LANGUAGE_GLYPHS[langKey] ?? "?"
  const langLabel = selected?.language_label ?? LANGUAGE_LABELS[langKey] ?? langKey
  const hubRoute = languageRoute(langKey) ?? "/learn"

  const continueLabel = nextCollection?.next_task?.title
    ? `${nextCollection.order ?? ""}. ${nextCollection.title_ru ?? ""} · ${nextCollection.next_task.title}`
    : nextCollection
      ? `${nextCollection.order ?? ""}. ${nextCollection.title_ru ?? ""}`
      : null

  const continueLearning = async () => {
    if (!selected || selected.available === false) {
      navigate(hubRoute)
      return
    }
    setBusy(true)
    try {
      const chapter = nextCollection
      if (!chapter) {
        navigate(hubRoute)
        return
      }
      const taskId =
        chapter.next_task?.task_id ??
        (await resolveCollectionNextTaskId(langKey, chapter))
      if (!taskId) {
        toast.info("Обучение", "Нет доступных задач")
        navigate(chapter.route_path || hubRoute)
        return
      }
      writeNavigationContext({
        mode: "curriculum",
        collectionId: chapter.collection_id || null,
      })
      navigate(`${taskPathPrefix}/${taskId}`, {
        state: {
          navigationMode: "curriculum",
          collectionId: chapter.collection_id || null,
          learningLanguage: langKey,
          returnTo: hubRoute,
        },
      })
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data
          ?.detail ||
        (err as Error)?.message ||
        ""
      toast.error("Не удалось получить следующую задачу", message)
    } finally {
      setBusy(false)
    }
  }

  if (guestMode) return null

  if (loading) {
    return (
      <div className="track-entry mb-[18px] cursor-default">
        <LoadingBlock text="Загрузка трека…" minHeight={72} className="border-0 bg-transparent p-0" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="track-entry mb-[18px] cursor-default">
        <p className="m-0 text-sm text-red-400" role="alert">
          {error}
        </p>
      </div>
    )
  }

  if (!languages.length || !selected) return null

  return (
    <button
      type="button"
      className="track-entry"
      disabled={busy}
      onClick={() => void continueLearning()}
    >
      <div className="te-glyph">{glyph}</div>
      <div className="min-w-0 flex-[1_1_auto]">
        <div className="mb-0.5 flex flex-wrap items-center gap-2">
          <b className="text-[15px] text-ink">Учебный трек</b>
          <Badge kind="purple">{langLabel}</Badge>
          <span className="font-mono text-xs text-ink-faint">
            {passed}/{total} · {percent}%
          </span>
        </div>
        {continueLabel ? (
          <div className="flex min-w-0 items-center gap-1.5 text-[13px] text-ink-faint">
            <span className="text-ink-muted">Продолжаете:</span>
            <span className="truncate font-medium text-ink">{continueLabel}</span>
          </div>
        ) : null}
      </div>
      <span className="btn btn-primary btn-sm flex-none pointer-events-none">
        {busy ? "…" : "Продолжить обучение"}
      </span>
    </button>
  )
}
