import BlockAssemblyEditor from "@/widgets/BlockAssemblyEditor/ui/BlockAssemblyEditor"
import CodeEditorBoard from "@/widgets/CodeEditorBoard/ui/CodeEditorBoard"
import { useMemo } from "react"
import { prepareBlockAssemblyScaffold } from "@/domain/blockAssembly"
import { getDefaultLanguageId } from "@/shared/config/languages"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import StudentCodeSplit from "@/widgets/task-workspace/StudentCodeSplit"
import StudentFlowchartSplit from "@/widgets/task-workspace/StudentFlowchartSplit"
import StudentReferenceSplit from "@/widgets/task-workspace/StudentReferenceSplit"
import StudentModeBar from "@/widgets/task-workspace/StudentModeBar"
import BlockEditor from "@/widgets/BlockEditor/ui/BlockEditor"
import {
  StudentFlowchartModeBar,
  StudentLearningLanguageBar,
  StudentParallelLanguageBar,
} from "@/widgets/task-workspace/StudentLanguageBar"
import {
  canSwapFlowchartSolutionModes,
  getBlockVariantForLanguage,
  getReferenceCode,
  getStudentReferenceLanguages,
  hasParallelExamples,
  hasTeacherFlowchartReference,
  isDualCodeTask,
  isMcqTask,
  getMcqOptions,
  isAnalyzeTask,
  isReferenceSplitTask,
  isFlowchartBlockAssemblyTask,
  isCodeToFlowchartTask,
  isPythonCurriculumTask,
  langDisplay,
  resolveKnownLanguageBarOptions,
  resolveLearningLanguageBarOptions,
  getLearningLanguages,
  getTaskPrimaryAction,
  shouldShowKnownLanguageSelector,
  shouldShowKnownReferenceCode,
  shouldShowParallelLanguageBar,
  shouldShowCppLearningBar,
  shouldShowPascalLearningBar,
  shouldShowPythonLearningBar,
} from "@/features/task-solving/model/studentUiUtils"
import ReadonlyCodeView from "@/widgets/task-workspace/ReadonlyCodeView"
import StudentAnalyzePredict from "@/widgets/task-workspace/StudentAnalyzePredict"
import StudentMcqPanel from "@/widgets/task-workspace/StudentMcqPanel"
import type { BlockPlacement } from "@/domain/blockAssembly"
import type { FlowPayload } from "@/shared/types/flow"
import type { PanelError } from "@/shared/types/execution"
import type { TaskDto } from "@/shared/types/task"

type EditorMode = "code" | "blocks" | "flow" | string
type FlowchartSolutionMode = "code" | "flow" | string

interface StudentEditorMainProps {
  task: TaskDto | null | undefined
  editorMode: EditorMode
  setEditorMode: (mode: EditorMode) => void
  isAlgorithmTask?: boolean
  isBlockAssemblyTask: boolean
  code: string
  setCode: (code: string) => void
  userLanguage: string
  setUserLanguage: (language: string) => void
  onKnownLanguageChange?: (language: string) => void
  selectedExampleLanguage: string
  languages: string[]
  swapLanguages?: () => void
  flow: FlowPayload
  setFlow: (flow: FlowPayload) => void
  resetFlowDraft: () => void
  registerGetFlowPayload: (getter: (() => FlowPayload) | null) => void
  flowchartSolutionMode: FlowchartSolutionMode
  swapFlowchartSolutionMode?: () => void
  blockAssemblyCode: string
  blockPlacements: BlockPlacement[]
  onBlockAssemblyChange: (payload: { placements: BlockPlacement[] }) => void
  blockLanguage: string
  onBlockLanguageChange?: (language: string) => void
  compilerErrors?: PanelError[]
  linterErrors?: PanelError[]
  highlightLine?: number | null
  isTeacherReview: boolean
  onAnalyzeSubmit?: () => void | Promise<void>
}

export default function StudentEditorMain({
  task,
  editorMode,
  setEditorMode,
  isBlockAssemblyTask,
  code,
  setCode,
  userLanguage,
  setUserLanguage,
  onKnownLanguageChange,
  selectedExampleLanguage,
  languages,
  swapLanguages,
  flow,
  setFlow,
  resetFlowDraft,
  registerGetFlowPayload,
  flowchartSolutionMode,
  swapFlowchartSolutionMode,
  blockAssemblyCode,
  blockPlacements,
  onBlockAssemblyChange,
  blockLanguage,
  onBlockLanguageChange,
  compilerErrors,
  linterErrors,
  highlightLine = null,
  isTeacherReview,
  onAnalyzeSubmit,
}: StudentEditorMainProps) {
  const isFlowchart = isFlowchartTask(task)
  const isMcq = isMcqTask(task)
  const mcqOptions = useMemo(() => getMcqOptions(task), [task])
  const isFlowchartBlockAssembly = isFlowchartBlockAssemblyTask(task, isBlockAssemblyTask)
  const isAnalyze = isAnalyzeTask(task)
  const isDualCode = isDualCodeTask(task, isBlockAssemblyTask)
  const isReferenceSplit = isReferenceSplitTask(task, isBlockAssemblyTask)
  const hasExamples = hasParallelExamples(task, isBlockAssemblyTask)
  const showParallelLanguageBar = shouldShowParallelLanguageBar(task, isBlockAssemblyTask)
  const showKnownSelector = shouldShowKnownLanguageSelector(task)
  const showKnownReferenceCode = shouldShowKnownReferenceCode(task, isBlockAssemblyTask)
  const showPascalLearningBar = shouldShowPascalLearningBar(task, isBlockAssemblyTask)
  const showPythonLearningBar = shouldShowPythonLearningBar(task, isBlockAssemblyTask)
  const showCppLearningBar = shouldShowCppLearningBar(task, isBlockAssemblyTask)
  const showFixedLearningBar = showPascalLearningBar || showPythonLearningBar || showCppLearningBar
  const defaultLearningLanguage = showPythonLearningBar
    ? "python"
    : showCppLearningBar
      ? "cpp"
      : "pascal"

  const knownBarLanguages = useMemo(
    () => resolveKnownLanguageBarOptions(task),
    [task],
  )
  const learningBarLanguages = useMemo(
    () => resolveLearningLanguageBarOptions(task, languages),
    [task, languages],
  )
  const blockLearningLanguages = useMemo(
    () => getLearningLanguages(task),
    [task],
  )

  const knownCode = getReferenceCode(task, selectedExampleLanguage)
  const knownCodeMissing = knownCode == null || knownCode === ""
  const learningVariant = isBlockAssemblyTask
    ? getBlockVariantForLanguage(task, blockLanguage || userLanguage)
    : null
  const assemblyBlocks = learningVariant?.blocks ?? task?.blocks ?? []
  const assemblyLang = blockLanguage || userLanguage
  const assemblyTemplate = useMemo(() => {
    if (!isBlockAssemblyTask) return learningVariant?.template ?? task?.template
    const raw = learningVariant?.template ?? task?.template ?? ""
    return prepareBlockAssemblyScaffold(raw, assemblyBlocks, assemblyLang).template
  }, [
    isBlockAssemblyTask,
    learningVariant?.template,
    task?.template,
    assemblyBlocks,
    assemblyLang,
  ])

  const languageBar = showParallelLanguageBar && !isFlowchart ? (
    <StudentParallelLanguageBar
      task={task}
      knownLanguage={selectedExampleLanguage}
      learningLanguage={userLanguage}
      knownLanguages={knownBarLanguages}
      learningLanguages={learningBarLanguages}
      showKnownSelector={showKnownSelector}
      onKnownLanguageChange={onKnownLanguageChange}
      onLearningLanguageChange={setUserLanguage}
      onSwap={swapLanguages}
    />
  ) : null

  const flowchartReferenceLanguages = useMemo(
    () => getStudentReferenceLanguages(task),
    [task],
  )
  const flowchartReferenceLanguage =
    flowchartReferenceLanguages.find((lang) => lang === selectedExampleLanguage) ||
    flowchartReferenceLanguages[0] ||
    selectedExampleLanguage
  const flowchartReferenceCode = getReferenceCode(task, flowchartReferenceLanguage)

  const flowchartSwapEnabled = canSwapFlowchartSolutionModes(task)
  const flowchartModeBar =
    isFlowchart && flowchartSwapEnabled ? (
    <StudentFlowchartModeBar
      solutionMode={flowchartSolutionMode}
      swapEnabled={flowchartSwapEnabled}
      swapDisabledReason={
        hasTeacherFlowchartReference(task) && !flowchartSwapEnabled ? "no_code" : "no_code"
      }
      onSwap={swapFlowchartSolutionMode}
      learningLanguage={userLanguage}
      languages={learningBarLanguages}
      onLearningLanguageChange={setUserLanguage}
      showLanguageSelect={flowchartSolutionMode === "code"}
    />
  ) : null

  const showModeBar =
    !isDualCode && !isReferenceSplit && !isFlowchart && !isBlockAssemblyTask && !isAnalyze && !isMcq

  const codeExamples = task?.code_examples as Record<string, string> | undefined
  const analyzeReferenceCode =
    (isPythonCurriculumTask(task) ? getReferenceCode(task, "python") : null) ||
    getReferenceCode(task, "pascal") ||
    getReferenceCode(task, selectedExampleLanguage) ||
    codeExamples?.python ||
    codeExamples?.pascal ||
    ""

  const blockAssemblyEditor = (
    <BlockAssemblyEditor
      blocks={assemblyBlocks}
      baseCode={blockAssemblyCode}
      rawTemplate={assemblyTemplate}
      correctOrder={learningVariant?.correct_order ?? task?.correct_order}
      placements={blockPlacements}
      onChange={onBlockAssemblyChange}
      language={blockLanguage}
      primaryLanguage={task?.language || getDefaultLanguageId()}
      languageVariants={task?.language_variants || null}
      onLanguageChange={onBlockLanguageChange}
      shuffleKey={String(task?.id ?? task?.title ?? "")}
      hideLanguageSelect
    />
  )

  return (
    <main className="task-workspace-editor flex min-w-0 flex-1 flex-col bg-bg-2">
      {showModeBar && (
        <StudentModeBar
          mode={editorMode}
          setMode={setEditorMode}
          knownLanguage={selectedExampleLanguage}
          learningLanguage={userLanguage}
          showBlocks={isBlockAssemblyTask}
          showFlow={false}
          hasParallel={showParallelLanguageBar}
        />
      )}

      {isDualCode && (
        <StudentCodeSplit
          knownLanguage={selectedExampleLanguage}
          knownCode={knownCode ?? ""}
          learningLanguage={userLanguage}
          learnedCode={code}
          setLearnedCode={setCode}
          knownLanguages={knownBarLanguages}
          learningLanguages={learningBarLanguages}
          onKnownLanguageChange={onKnownLanguageChange}
          onLearningLanguageChange={setUserLanguage}
          onSwap={swapLanguages}
          compilerErrors={compilerErrors}
          linterErrors={linterErrors}
          highlightLine={highlightLine}
        />
      )}

      {isBlockAssemblyTask && (
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
          {isFlowchartBlockAssembly ? (
            <StudentFlowchartSplit
              taskId={task?.id}
              referenceFlow={task?.diagram}
              workspacePanel={blockAssemblyEditor}
            />
          ) : (
            <>
              {showParallelLanguageBar ? (
                <StudentParallelLanguageBar
                  task={task}
                  knownLanguage={selectedExampleLanguage}
                  learningLanguage={blockLanguage || userLanguage}
                  knownLanguages={knownBarLanguages}
                  learningLanguages={blockLearningLanguages.length > 0 ? blockLearningLanguages : learningBarLanguages}
                  showKnownSelector={showKnownSelector}
                  onKnownLanguageChange={onKnownLanguageChange}
                  onLearningLanguageChange={onBlockLanguageChange}
                  onSwap={swapLanguages}
                />
              ) : (
                <StudentLearningLanguageBar
                  learningLanguage={blockLanguage || userLanguage}
                  languages={
                    blockLearningLanguages.length > 0 ? blockLearningLanguages : learningBarLanguages
                  }
                  onLearningLanguageChange={onBlockLanguageChange}
                />
              )}
              {showKnownReferenceCode ? (
                <StudentReferenceSplit
                  referenceLanguage={selectedExampleLanguage}
                  referenceCode={knownCode}
                  referenceMissing={knownCodeMissing}
                  referenceMissingLabel="Выберите язык в «Я знаю», чтобы увидеть исходный фрагмент."
                  header={null}
                >
                  {blockAssemblyEditor}
                </StudentReferenceSplit>
              ) : (
                blockAssemblyEditor
              )}
            </>
          )}
        </div>
      )}

      {isAnalyze && !isBlockAssemblyTask && !isFlowchart && (
        <StudentAnalyzePredict
          task={task}
          referenceLanguage="pascal"
          referenceCode={analyzeReferenceCode}
          onSubmitAnswer={onAnalyzeSubmit}
        />
      )}

      {isFlowchart && task && (
        <StudentFlowchartSplit
          taskId={task.id}
          referenceFlow={
            task?.diagram?.nodes?.length
              ? task.diagram
              : task?.flow_spec?.nodes?.length
                ? task.flow_spec
                : null
          }
          referencePanel={
            flowchartSolutionMode === "flow" ? (
              flowchartReferenceCode ? (
                <ReadonlyCodeView
                  code={flowchartReferenceCode}
                  language={flowchartReferenceLanguage}
                />
              ) : (
                <div className="flex h-full items-center justify-center p-6 text-center text-sm text-ink-muted">
                  Эталонный код для составления схемы не задан.
                </div>
              )
            ) : null
          }
          modeBar={flowchartModeBar}
          workspacePanel={
            flowchartSolutionMode === "flow" ? (
              <BlockEditor
                key={`flow-editor-${task.id}`}
                taskId={task.id}
                flow={flow}
                setFlow={setFlow}
                readOnly={isTeacherReview}
                minimalScaffold={isCodeToFlowchartTask(task)}
                registerGetPayload={isCodeToFlowchartTask(task) ? registerGetFlowPayload : null}
              />
            ) : (
              <CodeEditorBoard
                code={code}
                setCode={setCode}
                userLanguage={userLanguage}
                setUserLanguage={setUserLanguage}
                selectedExampleLanguage={selectedExampleLanguage}
                languages={languages}
                compilerErrors={compilerErrors}
                linterErrors={linterErrors}
                highlightLine={highlightLine}
                hideLanguageSelect
                variant="student"
                readOnly={isTeacherReview}
              />
            )
          }
        />
      )}

      {isReferenceSplit && !isBlockAssemblyTask && !isFlowchartTask(task) && !isAnalyze && (
        <StudentReferenceSplit
          referenceLanguage={selectedExampleLanguage}
          referenceCode={knownCode}
          referenceMissing={knownCodeMissing}
          referenceMissingLabel={
            knownCodeMissing
              ? `Эталонный код для ${langDisplay(selectedExampleLanguage)} не задан.`
              : null
          }
          header={languageBar}
        >
          {isMcq ? (
            <StudentMcqPanel
              prompt={task?.description}
              options={mcqOptions}
              selectedCode={code}
              onSelect={setCode}
              disabled={isTeacherReview}
            />
          ) : (
            <CodeEditorBoard
              code={code}
              setCode={setCode}
              userLanguage={userLanguage}
              setUserLanguage={setUserLanguage}
              selectedExampleLanguage={selectedExampleLanguage}
              languages={languages}
              compilerErrors={compilerErrors}
              linterErrors={linterErrors}
              highlightLine={highlightLine}
              hideLanguageSelect
              variant="student"
              readOnly={isTeacherReview}
            />
          )}
        </StudentReferenceSplit>
      )}

      {isMcq && !isReferenceSplit && (
        <div className="flex min-h-0 flex-1 flex-col">
          {languageBar}
          <StudentMcqPanel
            prompt={task?.description}
            options={mcqOptions}
            selectedCode={code}
            onSelect={setCode}
            disabled={isTeacherReview}
          />
        </div>
      )}

      {!isReferenceSplit &&
        !isDualCode &&
        !isBlockAssemblyTask &&
        !isFlowchart &&
        !isAnalyze &&
        !isMcq &&
        showParallelLanguageBar && (
          <div className="flex min-h-0 flex-1 flex-col">
            {languageBar}
            {getTaskPrimaryAction(task) !== "recognize" ? (
              <CodeEditorBoard
                code={code}
                setCode={setCode}
                userLanguage={userLanguage}
                setUserLanguage={setUserLanguage}
                selectedExampleLanguage={selectedExampleLanguage}
                languages={languages}
                compilerErrors={compilerErrors}
                linterErrors={linterErrors}
                highlightLine={highlightLine}
                hideLanguageSelect
                variant="student"
                readOnly={isTeacherReview}
              />
            ) : null}
          </div>
        )}

      {!showParallelLanguageBar &&
        !hasExamples &&
        !isFlowchart &&
        !isAnalyze &&
        !isMcq &&
        editorMode === "code" && (
        <div className="flex min-h-0 flex-1 flex-col">
          {showFixedLearningBar && (
            <StudentLearningLanguageBar
              learningLanguage={userLanguage || defaultLearningLanguage}
              languages={learningBarLanguages}
              onLearningLanguageChange={setUserLanguage}
            />
          )}
          <CodeEditorBoard
            code={code}
            setCode={setCode}
            userLanguage={userLanguage}
            setUserLanguage={setUserLanguage}
            selectedExampleLanguage={selectedExampleLanguage}
            languages={languages}
            compilerErrors={compilerErrors}
            linterErrors={linterErrors}
            highlightLine={highlightLine}
            hideLanguageSelect
            variant="student"
            readOnly={isTeacherReview}
          />
        </div>
      )}
    </main>
  )
}
