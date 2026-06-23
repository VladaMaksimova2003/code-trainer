import { useEffect, useMemo, useState } from "react"

import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"

import { useQuery } from "@tanstack/react-query"

import { useTaskDraftStore } from "@/features/task-editor/presentation/store/taskDraftStore"

import { useTaskEditorController } from "@/features/task-editor/presentation/hooks/useTaskEditorController"

import { AssignmentConfigPanel } from "@/features/task-editor/presentation/components/AssignmentConfigPanel"

import { AssignmentExecutionPanel } from "@/features/task-editor/presentation/components/AssignmentExecutionPanel"

import { loadPatternCatalog } from "@/features/task-editor/application/use-cases/loadPatternCatalog"

import { loadTaskTypes } from "@/features/task-editor/application/use-cases/loadTaskTypes"

import { loadAssignmentForEdit } from "@/features/task-editor/application/use-cases/loadAssignmentForEdit"

import {
  getPatternCatalogRepository,
  getTaskTypeRepository,
} from "@/features/task-editor/infrastructure/container"

import { teacherProfileLinkClass } from "@/features/task-editor/presentation/components/plaqueStyles"
import {
  assignTaskToChapter,
  getCatalogTask,
  listCurriculumChapters,
  type CurriculumChapterDto,
} from "@/features/task-catalog/infrastructure/catalogApi"
import { CURRICULUM_LANGUAGE_OPTIONS } from "@/features/curriculum/curriculumLanguageUi"
import { toast } from "@/shared/ui/toast"
import { getErrorMessage } from "@/shared/utils/errors"
import { useLanguages } from "@/shared/hooks/useLanguages"
import {
  clearEditDraftAutosave,
  isMeaningfulEditDraft,
  isPageReload,
  loadEditDraftAutosave,
  useTaskEditorDraftPersistence,
} from "@/features/task-editor/presentation/hooks/useTaskEditorDraftPersistence"

export default function TaskEditorPage() {
  const { id: editTaskId } = useParams()
  const [searchParams] = useSearchParams()
  const { getLabel: getLanguageLabel } = useLanguages()

  const navigate = useNavigate()

  const isEditMode = Boolean(editTaskId)
  const [chapters, setChapters] = useState<CurriculumChapterDto[]>([])
  const [selectedCollectionLanguage, setSelectedCollectionLanguage] = useState("python")
  const [selectedChapterKey, setSelectedChapterKey] = useState("")
  const [currentChapterTitle, setCurrentChapterTitle] = useState<string | null>(null)
  const [placementMessage, setPlacementMessage] = useState<string | null>(null)
  const [placementError, setPlacementError] = useState<string | null>(null)
  const [placementSaving, setPlacementSaving] = useState(false)

  const loadAutosave = useTaskDraftStore((s) => s.loadAutosave)
  const autosave = useTaskDraftStore((s) => s.autosave)
  const setDraft = useTaskDraftStore((s) => s.setDraft)
  const isSaving = useTaskDraftStore((s) => s.isSaving)
  const setSaving = useTaskDraftStore((s) => s.setSaving)
  const saveError = useTaskDraftStore((s) => s.saveError)
  const setSaveError = useTaskDraftStore((s) => s.setSaveError)

  const {
    draft,
    patchDraft,
    setSelectedPatterns,
    setTestCases,
    saveMutation,
    clearAll,
  } = useTaskEditorController()

  const patternsQuery = useQuery({
    queryKey: ["assignment-pattern-catalog"],
    queryFn: () => loadPatternCatalog(getPatternCatalogRepository()),
    staleTime: 5 * 60 * 1000,
  })

  const typesQuery = useQuery({
    queryKey: ["assignment-task-types"],
    queryFn: () => loadTaskTypes(getTaskTypeRepository()),
    staleTime: 5 * 60 * 1000,
  })

  const editQuery = useQuery({
    queryKey: ["assignment-edit", editTaskId],
    queryFn: () => loadAssignmentForEdit(Number(editTaskId)),
    enabled: isEditMode && Boolean(editTaskId),
  })

  const { isDraftHydrated } = useTaskEditorDraftPersistence({
    isEditMode,
    taskId: editTaskId,
    serverDraft: editQuery.data,
    draft,
    setDraft,
    autosaveCreateDraft: autosave,
    loadCreateDraft: loadAutosave,
  })

  useEffect(() => {
    listCurriculumChapters()
      .then((items) => setChapters(items))
      .catch(() => setChapters([]))
  }, [])

  useEffect(() => {
    if (isEditMode) return
    const chapterKey = searchParams.get("chapter")
    const language = searchParams.get("language")
    if (language) setSelectedCollectionLanguage(language)
    if (!chapterKey || !chapters.length) return
    const chapter = chapters.find((item) => item.chapter_key === chapterKey)
    if (chapter?.language) setSelectedCollectionLanguage(chapter.language)
    setSelectedChapterKey(chapterKey)
    setCurrentChapterTitle(chapter?.title || chapterKey)
  }, [isEditMode, searchParams, chapters])

  useEffect(() => {
    if (!isEditMode || !editTaskId) return
    getCatalogTask(Number(editTaskId))
      .then((task) => {
        if (task.chapter_key) {
          setSelectedChapterKey(task.chapter_key)
          setCurrentChapterTitle(task.chapter_title || task.chapter_key)
          const chapter = chapters.find((item) => item.chapter_key === task.chapter_key)
          if (chapter?.language) {
            setSelectedCollectionLanguage(chapter.language)
          } else if (task.language) {
            setSelectedCollectionLanguage(task.language)
          }
        }
      })
      .catch(() => {})
  }, [isEditMode, editTaskId, chapters])

  const chaptersForCollection = useMemo(
    () =>
      chapters
        .filter((chapter) => chapter.language === selectedCollectionLanguage)
        .sort((a, b) => a.sort_order - b.sort_order || a.title.localeCompare(b.title, "ru")),
    [chapters, selectedCollectionLanguage],
  )

  const handleAddToChapter = async () => {
    if (!editTaskId || !selectedChapterKey) return
    setPlacementSaving(true)
    setPlacementError(null)
    setPlacementMessage(null)
    try {
      const result = await assignTaskToChapter(Number(editTaskId), {
        language: selectedCollectionLanguage,
        chapter_key: selectedChapterKey,
      })
      setCurrentChapterTitle(result.chapter_title)
      setPlacementMessage(`Задание добавлено в «${result.chapter_title}»`)
      toast.push({
        kind: "lime",
        title: "Задание добавлено в главу",
        body: result.chapter_title,
      })
      window.dispatchEvent(new CustomEvent("teacher-tasks-changed"))
    } catch (err) {
      const message =
        err &&
        typeof err === "object" &&
        "response" in err &&
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      const errorText =
        typeof message === "string" ? message : "Не удалось добавить задачу в главу"
      setPlacementError(errorText)
      toast.push({
        kind: "danger",
        title: "Не удалось добавить в главу",
        body: errorText,
      })
    } finally {
      setPlacementSaving(false)
    }
  }

  const handleCollectionLanguageChange = (language: string) => {
    setSelectedCollectionLanguage(language)
    setSelectedChapterKey("")
    setPlacementMessage(null)
    setPlacementError(null)
  }

  const handleChapterChange = (chapterKey: string) => {
    setSelectedChapterKey(chapterKey)
    setPlacementMessage(null)
    setPlacementError(null)
  }

  const handleSubmit = async () => {
    if (isEditMode && editTaskId) {
      if (!isDraftHydrated) {
        setSaveError("Задача ещё загружается — подождите секунду и сохраните снова")
        return
      }
      if (String(draft.id ?? "") !== String(editTaskId)) {
        setSaveError("Черновик не совпадает с задачей — обновите страницу")
        return
      }
    }

    setSaveError(null)
    setSaving(true)

    try {
      await saveMutation.mutateAsync()

      if (isEditMode && editTaskId) {
        clearEditDraftAutosave(editTaskId)
      } else if (!isEditMode) {
        useTaskDraftStore.getState().reset()
      }

      toast.push({
        kind: "lime",
        title: isEditMode ? "Задача сохранена" : "Задача создана",
        body: draft.title?.trim() || "Без названия",
      })

      navigate("/teacher/cabinet?tab=tasks")
    } catch (err) {
      setSaveError(getErrorMessage(err, "Ошибка сохранения"))
    } finally {
      setSaving(false)
    }
  }

  const handleClearAll = () => {
    if (window.confirm("Очистить все поля?")) {
      clearAll()
    }
  }

  const pageTitle = isEditMode ? "Редактирование задачи" : "Создание задачи"

  const hasReloadDraft =
    isEditMode &&
    editTaskId &&
    isPageReload() &&
    isMeaningfulEditDraft(loadEditDraftAutosave(editTaskId))

  if (isEditMode && editQuery.isLoading && !hasReloadDraft) {
    return (
      <div className="tp-page flex h-screen items-center justify-center text-sm text-ink-faint">
        Загрузка задачи…
      </div>
    )
  }

  if (isEditMode && editQuery.isError) {
    return (
      <div className="tp-page h-screen p-6">
        <Link to="/teacher/cabinet?tab=tasks" className={teacherProfileLinkClass}>
          ← Профиль
        </Link>
        <p className="mt-4 text-danger">
          {editQuery.error instanceof Error
            ? editQuery.error.message
            : "Не удалось загрузить задачу"}
        </p>
      </div>
    )
  }

  return (
    <div className="tp-page flex h-screen flex-col overflow-hidden">
      <header className="flex flex-shrink-0 items-center justify-between border-b border-border bg-surface/70 px-6 py-3 backdrop-blur">
        <div>
          <Link to="/teacher/cabinet?tab=tasks" className={teacherProfileLinkClass}>
            ← Профиль преподавателя
          </Link>
          <h1 className="mt-1 text-2xl font-extrabold tracking-[-0.4px] text-ink">{pageTitle}</h1>
        </div>
      </header>

      {saveError && (
        <div className="mx-6 mt-4 rounded-md border border-danger/40 bg-danger/15 px-4 py-3 text-sm text-[#ffb0bf]">
          {saveError}
        </div>
      )}

      <div className="relative flex min-h-0 flex-1 flex-col gap-4 p-4 lg:flex-row">
        <AssignmentConfigPanel
          draft={draft}
          taskTypes={typesQuery.data ?? []}
          typesLoading={typesQuery.isLoading}
          patternCatalog={patternsQuery.data ?? []}
          patternsLoading={patternsQuery.isLoading}
          isSubmitting={isSaving || saveMutation.isPending || (isEditMode && !isDraftHydrated)}
          isEditMode={isEditMode}
          onPatch={patchDraft}
          onPatternsChange={setSelectedPatterns}
          onIoSchemaChange={(ioSchema) => patchDraft({ ioSchema })}
          onTestCasesChange={setTestCases}
          onClearAll={handleClearAll}
          onSubmit={handleSubmit}
          collectionOptions={CURRICULUM_LANGUAGE_OPTIONS.map((option) => ({
            id: option.id,
            label: option.label,
          }))}
          selectedCollectionLanguage={selectedCollectionLanguage}
          chapters={chaptersForCollection}
          selectedChapterKey={selectedChapterKey}
          currentChapterTitle={currentChapterTitle}
          placementSaving={placementSaving}
          placementMessage={placementMessage}
          placementError={placementError}
          onCollectionLanguageChange={handleCollectionLanguageChange}
          onChapterChange={handleChapterChange}
          onAddToChapter={handleAddToChapter}
          getLanguageLabel={getLanguageLabel}
        />

        <AssignmentExecutionPanel draft={draft} onPatch={patchDraft} />
      </div>
    </div>
  )
}
