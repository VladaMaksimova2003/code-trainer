import type { IoSchema, Pattern, TaskDraft } from "@/features/task-editor/domain/entities"
import {
  EDITOR_ACTIVITY_OPTIONS,
  patchDraftForEditorActivity,
  resolveEditorActivityKind,
  type EditorActivityKind,
} from "@/features/task-editor/domain/editorActivityTypes"
import type { TaskTypeOption } from "@/features/task-editor/application/ports/ITaskTypeRepository"
import { AssignmentPanelShell } from "@/features/task-editor/presentation/layout/AssignmentPanelShell"
import { PatternPicker } from "@/features/task-editor/presentation/components/PatternPicker"
import { TestCasesSection } from "@/features/task-editor/presentation/components/TestCasesSection"
import type { CurriculumChapterDto } from "@/features/task-catalog/infrastructure/catalogApi"
import {
  editorFieldBlockClass,
  editorInputClass,
  editorLabelClass,
  editorSectionDividerClass,
  footerActionButton,
} from "@/features/task-editor/presentation/components/plaqueStyles"

type CollectionOption = {
  id: string
  label: string
}

type Props = {
  draft: TaskDraft
  taskTypes: TaskTypeOption[]
  typesLoading: boolean
  patternCatalog: Pattern[]
  patternsLoading: boolean
  isSubmitting: boolean
  isEditMode: boolean
  onPatch: (patch: Partial<TaskDraft>) => void
  onPatternsChange: (patterns: Pattern[]) => void
  onIoSchemaChange: (schema: IoSchema) => void
  onTestCasesChange: (cases: TaskDraft["testCases"]) => void
  onClearAll: () => void
  onSubmit: () => void
  collectionOptions: CollectionOption[]
  selectedCollectionLanguage: string
  chapters: CurriculumChapterDto[]
  selectedChapterKey: string
  currentChapterTitle?: string | null
  placementSaving: boolean
  placementMessage: string | null
  placementError: string | null
  onCollectionLanguageChange: (language: string) => void
  onChapterChange: (chapterKey: string) => void
  onAddToChapter: () => void
  getLanguageLabel: (languageId: string) => string
}

export function AssignmentConfigPanel({
  draft,
  typesLoading: _typesLoading,
  taskTypes: _taskTypes,
  patternCatalog,
  patternsLoading,
  isSubmitting,
  isEditMode,
  onPatch,
  onPatternsChange,
  onIoSchemaChange,
  onTestCasesChange,
  onClearAll,
  onSubmit,
  collectionOptions,
  selectedCollectionLanguage,
  chapters,
  selectedChapterKey,
  currentChapterTitle,
  placementSaving,
  placementMessage,
  placementError,
  onCollectionLanguageChange,
  onChapterChange,
  onAddToChapter,
  getLanguageLabel,
}: Props) {
  const selectedActivity = resolveEditorActivityKind(draft)

  return (
    <AssignmentPanelShell variant="config">
      <div className="flex flex-col gap-6 pb-4 pt-6">
        <div className={editorFieldBlockClass}>
          <label className={editorLabelClass} htmlFor="editor-task-type">
            Тип задания
          </label>
          <select
            id="editor-task-type"
            className={editorInputClass}
            value={selectedActivity}
            onChange={(e) =>
              onPatch(patchDraftForEditorActivity(e.target.value as EditorActivityKind))
            }
          >
            {EDITOR_ACTIVITY_OPTIONS.map((option) => (
              <option key={option.kind} value={option.kind}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <label className={`${editorFieldBlockClass} ${editorSectionDividerClass}`}>
          <span className={editorLabelClass}>Название</span>
          <input
            className={editorInputClass}
            value={draft.title}
            onChange={(e) => onPatch({ title: e.target.value })}
          />
        </label>

        <label className={`${editorFieldBlockClass} ${editorSectionDividerClass}`}>
          <span className={editorLabelClass}>Описание</span>
          <textarea
            className={`${editorInputClass} min-h-[100px] resize-y`}
            value={draft.description}
            onChange={(e) => onPatch({ description: e.target.value })}
          />
        </label>

        <div className={editorSectionDividerClass}>
          <PatternPicker
            catalog={patternCatalog}
            draft={draft}
            onPatch={onPatch}
            isLoading={patternsLoading}
            getLanguageLabel={getLanguageLabel}
          />
        </div>

        <TestCasesSection
          testCases={draft.testCases}
          ioSchema={draft.ioSchema}
          onIoSchemaChange={onIoSchemaChange}
          onChange={onTestCasesChange}
        />

        <div className={editorSectionDividerClass}>
          <div className="te-test-card flex flex-col gap-4">
            <div>
              <h3 className="text-sm font-semibold tracking-wide text-ink">
                Размещение в сборнике
              </h3>
              <p className="mt-1 text-sm text-ink-faint">
                Выберите сборник по языку и главу. Перед добавлением эталонное решение
                прогоняется через все тестовые случаи.
              </p>
              {currentChapterTitle ? (
                <p className="mt-2 text-sm text-lime">
                  Сейчас: {currentChapterTitle}
                </p>
              ) : null}
            </div>
            <label className={editorFieldBlockClass}>
              <span className={editorLabelClass}>Сборник</span>
              <select
                className={editorInputClass}
                value={selectedCollectionLanguage}
                onChange={(event) => onCollectionLanguageChange(event.target.value)}
              >
                {collectionOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label className={editorFieldBlockClass}>
              <span className={editorLabelClass}>Глава</span>
              <select
                className={editorInputClass}
                value={selectedChapterKey}
                onChange={(event) => onChapterChange(event.target.value)}
              >
                <option value="">Выберите главу</option>
                {chapters.map((chapter) => (
                  <option key={chapter.chapter_key} value={chapter.chapter_key}>
                    {chapter.title}
                  </option>
                ))}
              </select>
            </label>
            {isEditMode && (
              <button
                type="button"
                disabled={!selectedChapterKey || placementSaving}
                onClick={onAddToChapter}
                className="btn btn-primary btn-full disabled:opacity-50"
              >
                {placementSaving ? "Проверка и добавление..." : "Добавить в главу"}
              </button>
            )}
            {placementMessage && <p className="text-sm text-lime">{placementMessage}</p>}
            {placementError && <p className="te-error">{placementError}</p>}
          </div>
        </div>

        <div className={`te-footer -mx-6 mt-2 ${editorSectionDividerClass}`}>
          {!isEditMode && (
            <button
              type="button"
              onClick={onClearAll}
              className={footerActionButton("clear")}
            >
              Очистить всё
            </button>
          )}
          <button
            type="button"
            disabled={isSubmitting}
            onClick={onSubmit}
            className={footerActionButton("submit", !isEditMode ? "" : "flex-1")}
          >
            {isSubmitting
              ? "Сохранение…"
              : isEditMode
                ? "Сохранить"
                : "Отправить задание"}
          </button>
        </div>
      </div>
    </AssignmentPanelShell>
  )
}
