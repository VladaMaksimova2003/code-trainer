import { useEffect, useMemo, useState } from "react"
import { pickEditorHighlightLine } from "@/features/task-solving/model/constructionHintsUtils"
import { countTestStats, buildTestRows } from "@/features/task-solving/model/testPanelUtils"
import { testInputDisplayContextFromTask } from "@/features/task-solving/model/testInputDisplay"
import StudentBottomPanel from "@/widgets/test-panel/StudentBottomPanel"
import StudentLeftRail from "@/widgets/task-workspace/StudentLeftRail"
import StudentEditorMain from "@/widgets/task-workspace/StudentEditorMain"
import StudentTaskHeader from "@/widgets/task-header/StudentTaskHeader"
import { buildAssemblyPreviewCode } from "@/domain/blockAssembly"
import {
  getBlockVariantForLanguage,
  hasParallelExamples,
  isAnalyzeTask,
  resolveEditorMode,
} from "@/features/task-solving/model/studentUiUtils"
import { buildTaskIssueContext } from "@/features/support/buildTaskIssueContext"
import type { UseTaskSolverReturn } from "@/features/task-solving/hooks/useTaskSolver"

interface StudentTaskWorkspaceProps extends UseTaskSolverReturn {
  user?: unknown | null
}

export default function StudentTaskWorkspace({
  id,
  task,
  user = null,
  isAlgorithmTask,
  isBlockAssemblyTask,
  teacherReview,
  isTeacherReview,
  activeSubmissionId,
  reviewSubmission,
  reviewLoading,
  navigationMode,
  collectionId,
  manualTaskIds,
  fetchedCollectionNav,
  adaptiveLoading,
  handleAdaptiveNext,
  code,
  setCode,
  flow,
  setFlow,
  resetFlowDraft,
  registerGetFlowPayload,
  flowchartSolutionMode,
  swapFlowchartSolutionMode,
  blockAssemblyCode,
  blockPlacements,
  setBlockPlacements,
  blockLanguage,
  userLanguage,
  languageOptions,
  handleTaskLanguageChange,
  handleUserLanguageChange,
  swapLanguages,
  runCode,
  isSubmitting,
  results,
  compilerErrors,
  linterErrors,
  patternErrors,
  flowCheckDebug,
  bottomTab,
  setBottomTab,
  selectedExampleLanguage,
  isPedagogyRefreshing,
}: StudentTaskWorkspaceProps) {
  const exampleLanguages = task?.code_examples ? Object.keys(task.code_examples) : []
  const [editorMode, setEditorMode] = useState(() =>
    resolveEditorMode(task, isBlockAssemblyTask),
  )

  const parallel = hasParallelExamples(task, isBlockAssemblyTask)
  const isAnalyze = isAnalyzeTask(task)
  const showLanguageBar = false

  useEffect(() => {
    setEditorMode(resolveEditorMode(task, isBlockAssemblyTask))
  }, [task?.id, task?.type, isBlockAssemblyTask])

  const learnedCode = useMemo(() => {
    if (!isBlockAssemblyTask || !task) return code
    const lang = blockLanguage || userLanguage
    const variant = getBlockVariantForLanguage(task, lang)
    const blocks = variant?.blocks ?? task.blocks ?? []
    const rawTemplate = variant?.template ?? task?.template ?? ""
    return buildAssemblyPreviewCode(
      rawTemplate,
      blocks,
      blockPlacements,
      blockAssemblyCode,
      lang,
    )
  }, [
    isBlockAssemblyTask,
    task,
    code,
    blockAssemblyCode,
    blockPlacements,
    blockLanguage,
    userLanguage,
  ])

  const testInputDisplay = useMemo(
    () => testInputDisplayContextFromTask(task, userLanguage),
    [task, userLanguage],
  )
  const testRows = useMemo(
    () => buildTestRows(task?.test_cases, results, testInputDisplay),
    [task?.test_cases, results, testInputDisplay],
  )
  const testStats = useMemo(() => countTestStats(testRows), [testRows])
  const highlightLine = useMemo(
    () =>
      pickEditorHighlightLine({
        compilerErrors,
        linterErrors,
        results,
      }),
    [compilerErrors, linterErrors, results],
  )
  const hasFailedTests = testStats.failed > 0

  const issueContext = useMemo(
    () =>
      buildTaskIssueContext({
        taskId: id,
        language: userLanguage,
        activeSubmissionId,
        results,
        compilerErrors,
        linterErrors,
        patternErrors,
        testStats,
      }),
    [
      id,
      userLanguage,
      activeSubmissionId,
      results,
      compilerErrors,
      linterErrors,
      patternErrors,
      testStats,
    ],
  )

  const handleAnalyzeSubmit = async () => {
    // Analyze tasks validate locally in StudentAnalyzePredict — no compiler runner.
  }

  const teacherReviewRecord = teacherReview as { studentName?: string } | null | undefined
  const reviewSubmissionRecord = reviewSubmission as {
    student_name?: string
    success?: boolean
    status?: string
  } | null

  return (
    <div className="flex h-screen min-h-0 flex-col overflow-hidden bg-bg text-ink">
      <StudentTaskHeader
        user={user}
        task={task}
        id={id}
        taskId={id}
        activeSubmissionId={activeSubmissionId}
        isTeacherReview={isTeacherReview}
        navigationMode={navigationMode}
        collectionId={collectionId}
        manualTaskIds={manualTaskIds}
        fetchedCollectionNav={fetchedCollectionNav}
        onAdaptiveNext={handleAdaptiveNext}
        adaptiveLoading={adaptiveLoading}
        knownLanguage={selectedExampleLanguage}
        learningLanguage={userLanguage}
        exampleLanguages={exampleLanguages}
        learningLanguages={languageOptions}
        onKnownLanguageChange={handleTaskLanguageChange}
        onLearningLanguageChange={handleUserLanguageChange}
        onSwap={swapLanguages}
        showLanguageBar={showLanguageBar}
        issueContext={issueContext}
      />

      {isTeacherReview && (
        <div className="shrink-0 border-b border-[rgba(139,83,254,.3)] bg-purple-soft px-5 py-2.5 text-sm text-[#d4bcff]">
          Просмотр · {teacherReviewRecord?.studentName || reviewSubmissionRecord?.student_name || "студент"}
          {" · "}
          {reviewLoading
            ? "Загрузка решения…"
            : reviewSubmissionRecord?.success === true
              ? "Решение успешно"
              : reviewSubmissionRecord?.success === false
                ? "Решение с ошибкой"
                : reviewSubmissionRecord
                  ? `Статус: ${reviewSubmissionRecord.status}`
                  : "Текст решения недоступен"}
        </div>
      )}

      <div className="task-workspace-main flex flex-1 min-h-0 flex-col lg:flex-row">
        <StudentLeftRail
          task={task}
          userLanguage={userLanguage}
          knownLanguage={selectedExampleLanguage}
          learnedCode={learnedCode}
          isAlgorithmTask={isAlgorithmTask}
          isPedagogyRefreshing={isPedagogyRefreshing}
        />

        <StudentEditorMain
          task={task}
          editorMode={editorMode}
          setEditorMode={setEditorMode}
          isAlgorithmTask={isAlgorithmTask}
          isBlockAssemblyTask={isBlockAssemblyTask}
          code={code}
          setCode={setCode}
          userLanguage={userLanguage}
          setUserLanguage={handleUserLanguageChange}
          onKnownLanguageChange={handleTaskLanguageChange}
          selectedExampleLanguage={selectedExampleLanguage}
          languages={languageOptions}
          swapLanguages={swapLanguages}
          flow={flow}
          setFlow={setFlow}
          resetFlowDraft={resetFlowDraft}
          registerGetFlowPayload={registerGetFlowPayload}
          flowchartSolutionMode={flowchartSolutionMode}
          swapFlowchartSolutionMode={swapFlowchartSolutionMode}
          blockAssemblyCode={blockAssemblyCode}
          blockPlacements={blockPlacements}
          onBlockAssemblyChange={({ placements }) => setBlockPlacements(placements)}
          blockLanguage={blockLanguage}
          onBlockLanguageChange={handleUserLanguageChange}
          compilerErrors={compilerErrors}
          linterErrors={linterErrors}
          highlightLine={hasFailedTests ? highlightLine : null}
          isTeacherReview={isTeacherReview}
          onAnalyzeSubmit={handleAnalyzeSubmit}
        />
      </div>

      {!isAnalyze && (
      <StudentBottomPanel
        bottomTab={bottomTab}
        setBottomTab={setBottomTab}
        task={task}
        results={results}
        compilerErrors={compilerErrors}
        linterErrors={linterErrors}
        patternErrors={patternErrors}
        flowCheckDebug={flowCheckDebug}
        onRun={(task?.test_cases?.length ?? 0) > 0 ? runCode : undefined}
        isSubmitting={isSubmitting}
        isTeacherReview={isTeacherReview}
        activeSubmissionId={activeSubmissionId}
        currentUser={user}
        learningLanguage={userLanguage}
      />
      )}
    </div>
  )
}
