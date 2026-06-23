import { useCallback, useEffect, useRef, useState } from "react"
import BlockEditor from "@/widgets/BlockEditor/ui/BlockEditor"
import BlockTaskCodeEditor from "@/widgets/BlockTaskCodeEditor/ui/BlockTaskCodeEditor"
import CodeEditorBoard from "@/widgets/CodeEditorBoard/ui/CodeEditorBoard"
import {
  getAssignmentEditorMode,
} from "@/features/task-editor/domain/assignmentRules"
import { isEditorFixActivity } from "@/features/task-editor/domain/editorActivityTypes"
import { ensureDraftBlockEditor } from "@/features/task-editor/domain/blockEditor"
import { DifficultyLevel } from "@/features/task-editor/domain/enums"
import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { AssignmentPanelShell } from "@/features/task-editor/presentation/layout/AssignmentPanelShell"
import { useTaskDraftStore } from "@/features/task-editor/presentation/store/taskDraftStore"
import { editorSelectGhostClass, outlineMutedBtn, segmentToggleLight } from "@/features/task-editor/presentation/components/plaqueStyles"
import { resolveLanguageBlockEditorPatch } from "@/features/task-editor/domain/languageBlockEditorState"
import { useLanguages } from "@/shared/hooks/useLanguages"
import { fetchDebugCodes, saveDebugCodes } from "@/features/teacher/api/debugCodesApi"

const DIFFICULTIES = [
  { value: DifficultyLevel.EASY, label: "Сложность лёгкая" },
  { value: DifficultyLevel.MEDIUM, label: "Сложность средняя" },
  { value: DifficultyLevel.HARD, label: "Сложность сложная" },
]

type DebugCodeTab = "fixed" | "buggy"

type Props = {
  draft: TaskDraft
  onPatch: (patch: Partial<TaskDraft>) => void
}

export function AssignmentExecutionPanel({ draft, onPatch }: Props) {
  const { authoringIds: languageOptions, getLabel } = useLanguages()
  const editorMode = getAssignmentEditorMode(draft.type)
  const language = draft.languages[0] ?? draft.code.language
  const onPatchRef = useRef(onPatch)
  onPatchRef.current = onPatch

  const setBlockTaskEditor = useTaskDraftStore((s) => s.setBlockTaskEditor)
  const blockDraft = ensureDraftBlockEditor(draft)
  const blockRanges = blockDraft.blockRanges ?? []

  const isBlockTask = editorMode === "blocks"
  const isCodeTask = editorMode === "code"
  const isFlowchartTask = editorMode === "flowchart"
  const [flowchartTab, setFlowchartTab] = useState<"diagram" | "code">("diagram")
  const [debugCodeTab, setDebugCodeTab] = useState<DebugCodeTab>("buggy")
  const [fixedCodes, setFixedCodes] = useState<Record<string, string>>({})
  const [buggyCodes, setBuggyCodes] = useState<Record<string, string>>({})
  const [debugCodesLoading, setDebugCodesLoading] = useState(false)
  const [debugCodesError, setDebugCodesError] = useState<string | null>(null)
  const debugSaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const taskId = draft.id ? Number(draft.id) : null
  const isFixActivity = isEditorFixActivity(draft)
  const showDebugCodeActions = Boolean(isFixActivity && isCodeTask && taskId)

  const convertActionsRef = useRef({
    convertToBlock: () => {},
    convertToCode: () => {},
  })
  const [canConvertToBlock, setCanConvertToBlock] = useState(false)
  const [canConvertToCode, setCanConvertToCode] = useState(false)

  const handleConvertStateChange = useCallback(
    (state: {
      canConvertToBlock: boolean
      canConvertToCode: boolean
      convertToBlock: () => void
      convertToCode: () => void
    }) => {
      convertActionsRef.current = {
        convertToBlock: state.convertToBlock,
        convertToCode: state.convertToCode,
      }
      setCanConvertToBlock(state.canConvertToBlock)
      setCanConvertToCode(state.canConvertToCode)
    },
    [],
  )

  const handleBlockEditorChange = useCallback(
    (payload: { code: string; blockRanges: typeof blockRanges }) => {
      setBlockTaskEditor(payload)
    },
    [setBlockTaskEditor],
  )

  const handleFlowChange = useCallback(
    (next: NonNullable<TaskDraft["flow"]>) => {
      onPatchRef.current({ flow: next })
    },
    [],
  )

  const setLanguage = (lang: string) => {
    onPatch(resolveLanguageBlockEditorPatch(draft, lang))
  }

  const setReferenceCode = (code: string) => {
    onPatch({ code: { ...draft.code, code } })
  }

  useEffect(() => {
    if (!taskId || !isFixActivity) return
    let cancelled = false
    setDebugCodesLoading(true)
    setDebugCodesError(null)
    fetchDebugCodes(taskId)
      .then((payload) => {
        if (cancelled) return
        setFixedCodes(payload.fixed_codes ?? {})
        setBuggyCodes(payload.buggy_codes ?? {})
      })
      .catch((err: unknown) => {
        if (cancelled) return
        const fallbackCode = draft.code.code ?? ""
        if (fallbackCode.trim()) {
          setFixedCodes((prev) => ({ ...prev, [language]: prev[language] ?? fallbackCode }))
          setBuggyCodes((prev) => ({ ...prev, [language]: prev[language] ?? fallbackCode }))
        }
        const detail =
          (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          (err as Error)?.message ||
          "Не удалось загрузить код"
        if (!fallbackCode.trim()) {
          setDebugCodesError(detail)
        }
      })
      .finally(() => {
        if (!cancelled) setDebugCodesLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [taskId, isFixActivity])

  useEffect(() => {
    return () => {
      if (debugSaveTimerRef.current) clearTimeout(debugSaveTimerRef.current)
    }
  }, [])

  const scheduleDebugCodesSave = useCallback(
    (payload: { fixed_codes?: Record<string, string>; buggy_codes?: Record<string, string> }) => {
      if (!taskId) return
      if (debugSaveTimerRef.current) clearTimeout(debugSaveTimerRef.current)
      debugSaveTimerRef.current = setTimeout(() => {
        void saveDebugCodes(taskId, payload).catch((err: unknown) => {
          setDebugCodesError(
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
              (err as Error)?.message ||
              "Не удалось сохранить код",
          )
        })
      }, 800)
    },
    [taskId],
  )

  const activeDebugCode =
    debugCodeTab === "fixed" ? (fixedCodes[language] ?? "") : (buggyCodes[language] ?? "")

  const handleDebugCodeChange = useCallback(
    (code: string) => {
      if (debugCodeTab === "fixed") {
        const next = { ...fixedCodes, [language]: code }
        setFixedCodes(next)
        scheduleDebugCodesSave({ fixed_codes: next })
        return
      }
      const next = { ...buggyCodes, [language]: code }
      setBuggyCodes(next)
      scheduleDebugCodesSave({ buggy_codes: next })
    },
    [buggyCodes, debugCodeTab, fixedCodes, language, scheduleDebugCodesSave],
  )

  const flow = draft.flow ?? { flow: [], nodes: [], edges: [] }

  const header = (
    <div className="border-b border-border pb-4 pt-2">
      <div className="flex w-full flex-wrap items-center gap-4">
        <select
          id="exec-language"
          className={editorSelectGhostClass}
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          aria-label="Язык программирования"
        >
          {languageOptions.map((lang) => (
            <option key={lang} value={lang} className="bg-surface text-ink">
              {getLabel(lang)}
            </option>
          ))}
        </select>
        <select
          id="exec-difficulty"
          className={editorSelectGhostClass}
          value={draft.difficulty}
          onChange={(e) =>
            onPatch({ difficulty: e.target.value as DifficultyLevel })
          }
          aria-label="Сложность задания"
        >
          {DIFFICULTIES.map((d) => (
            <option key={d.value} value={d.value} className="bg-surface text-ink">
              {d.label}
            </option>
          ))}
        </select>
        {showDebugCodeActions ? (
          <div className="flex items-center gap-1 rounded-lg border border-border bg-surface-2 p-1">
            <button
              type="button"
              className={segmentToggleLight(debugCodeTab === "fixed")}
              onClick={() => setDebugCodeTab("fixed")}
            >
              Правильный код
            </button>
            <button
              type="button"
              className={segmentToggleLight(debugCodeTab === "buggy")}
              onClick={() => setDebugCodeTab("buggy")}
            >
              Неправильный код
            </button>
          </div>
        ) : null}
        {isBlockTask && (
          <>
            <button
              type="button"
              className={outlineMutedBtn()}
              disabled={!canConvertToBlock}
              onClick={() => convertActionsRef.current.convertToBlock()}
            >
              Преобразовать в блок
            </button>
            <button
              type="button"
              className={outlineMutedBtn()}
              disabled={!canConvertToCode}
              onClick={() => convertActionsRef.current.convertToCode()}
            >
              Преобразовать в код
            </button>
            <span className="text-xs text-ink-muted">
              Клик по рамке — блок целиком; тяните мышью — несколько строк в один блок
            </span>
          </>
        )}
        {isFlowchartTask && (
          <>
            <div className="flex items-center gap-1 rounded-lg border border-border bg-surface-2 p-1">
              <button
                type="button"
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  flowchartTab === "diagram"
                    ? "bg-lime/15 text-lime"
                    : "text-ink-muted hover:text-ink"
                }`}
                onClick={() => setFlowchartTab("diagram")}
              >
                Блок-схема
              </button>
              <button
                type="button"
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  flowchartTab === "code"
                    ? "bg-lime/15 text-lime"
                    : "text-ink-muted hover:text-ink"
                }`}
                onClick={() => setFlowchartTab("code")}
              >
                Эталонный код
              </button>
            </div>
            {flowchartTab === "code" && (
              <label className="flex cursor-pointer items-center gap-2 text-xs text-ink-muted">
                <input
                  type="checkbox"
                  className="accent-lime"
                  checked={Boolean(draft.flowchartExposeReferenceCode)}
                  onChange={(e) =>
                    onPatch({ flowchartExposeReferenceCode: e.target.checked })
                  }
                />
                Показать студенту
              </label>
            )}
          </>
        )}
      </div>
    </div>
  )

  return (
    <>
      <AssignmentPanelShell variant="execution" header={header}>
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
        {isFlowchartTask && flowchartTab === "diagram" && (
          <BlockEditor
            taskId={draft.id ? Number(draft.id) : 0}
            flow={flow}
            setFlow={handleFlowChange}
            showModeHint={false}
          />
        )}
        {isFlowchartTask && flowchartTab === "code" && (
          <div className="flex min-h-[360px] flex-1 flex-col overflow-hidden">
            <CodeEditorBoard
              code={draft.code.code}
              setCode={setReferenceCode}
              userLanguage={language}
              setUserLanguage={setLanguage}
              selectedExampleLanguage=""
              languages={languageOptions}
              compilerErrors={[]}
              linterErrors={[]}
              hideLanguageSelect
            />
          </div>
        )}
        {isCodeTask && (
          showDebugCodeActions ? (
            debugCodesLoading ? (
              <div className="flex flex-1 items-center justify-center p-6 text-sm text-ink-faint">
                Загрузка кода…
              </div>
            ) : (
              <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
                {debugCodesError ? (
                  <p className="border-b border-border px-4 py-2 text-sm text-red-400" role="alert">
                    {debugCodesError}
                  </p>
                ) : null}
                <CodeEditorBoard
                  key={`${debugCodeTab}-${language}`}
                  code={activeDebugCode}
                  setCode={handleDebugCodeChange}
                  userLanguage={language}
                  setUserLanguage={setLanguage}
                  selectedExampleLanguage=""
                  languages={languageOptions}
                  compilerErrors={[]}
                  linterErrors={[]}
                  hideLanguageSelect
                />
              </div>
            )
          ) : (
            <CodeEditorBoard
              code={draft.code.code}
              setCode={setReferenceCode}
              userLanguage={language}
              setUserLanguage={setLanguage}
              selectedExampleLanguage=""
              languages={languageOptions}
              compilerErrors={[]}
              linterErrors={[]}
              hideLanguageSelect
            />
          )
        )}
        {isBlockTask && (
          <div className="flex h-full min-h-[360px] flex-col bg-bg-2">
            <p className="border-b border-border px-4 py-2 text-[13px] text-ink-muted">
              Между блоками можно вставлять пробелы и переводы строк — они задают отступы в Python при сборке.
            </p>
            <BlockTaskCodeEditor
              key={language}
              code={blockDraft.code.code}
              blockRanges={blockRanges}
              language={language}
              onChange={handleBlockEditorChange}
              onConvertStateChange={handleConvertStateChange}
              className="min-h-0 flex-1"
            />
          </div>
        )}
        </div>
      </AssignmentPanelShell>
    </>
  )
}
