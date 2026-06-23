import { normalizePlacements, prepareBlockAssemblyScaffold } from "@/domain/blockAssembly"
import type { BlockPlacement } from "@/domain/blockAssembly"
import {
  getStudentFlowStarterPayload,
  isFlowEmpty,
  resolveStudentFlowFromDraft,
} from "@/widgets/BlockEditor/lib/flowInitialState"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import {
  canSwapFlowchartSolutionModes,
  getBlockVariantForLanguage,
  getCurriculumLearningLanguage,
  getDefaultFlowchartSolutionMode,
  getInitialStudentCode,
  getLearningLanguages,
  getParallelLanguages,
  getTaskPrimaryAction,
  isCppCurriculumTask,
  isCsharpCurriculumTask,
  isCurriculumMirrorTask,
  isJavaCurriculumTask,
  isPascalCurriculumTask,
  isPythonCurriculumTask,
  resolveParallelLanguagePair,
} from "@/features/task-solving/model/studentUiUtils"
import type { TaskDraftRecord } from "@/features/task-solving/model/taskDraftHelpers"
import type { FlowPayload } from "@/shared/types/flow"
import type { TaskDto, TaskType } from "@/shared/types/task"
import { normalizeCurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"

type FlowchartSolutionMode = "code" | "flow"

export interface TaskHydrationSnapshot {
  activeTab: string
  bottomTab: string
  code: string
  flow: FlowPayload
  blockAssemblyCode: string
  blockPlacements: BlockPlacement[]
  blockLanguage: string
  selectedExampleLanguage: string
  userLanguage: string
  flowchartSolutionMode: FlowchartSolutionMode
}

export interface TaskHydrationOptions {
  defaultId?: string
  languageOptions?: string[]
  preferLearningLanguage?: string
}

export function normalizeBottomTab(value: string | null | undefined): string {
  if (value === "comments") return "comments"
  if (value === "lint" || value === "compiler" || value === "patterns") return "errors"
  if (value === "result") return "case"
  if (value === "case" || value === "errors") return value
  return "case"
}

function isBlockAssemblyTaskType(type: TaskType | undefined): boolean {
  return (
    type === "block_reorder" ||
    type === "code_assembly" ||
    type === "task_build_from_blocks"
  )
}

function hasTeacherAssemblyOverride(task: TaskDto | null | undefined): boolean {
  if (!task) return false
  const codeExamples = task.code_examples as Record<string, unknown> | undefined
  return Boolean(task.teacher_assembly_override || codeExamples?.teacher_assembly_override)
}

function shouldRestoreDraftCode(task: TaskDto | null | undefined): boolean {
  if (!task) return true
  if (getTaskPrimaryAction(task) === "debug" && hasTeacherAssemblyOverride(task)) {
    return false
  }
  if (isCurriculumMirrorTask(task)) {
    return getTaskPrimaryAction(task) === "debug"
  }
  return true
}

/**
 * Pure hydration snapshot after getTask + draft resolution (matches useTaskSolver load handler).
 */
export function resolveTaskHydration(
  task: TaskDto | null | undefined,
  draft: TaskDraftRecord | null | undefined,
  { defaultId = "", languageOptions = [], preferLearningLanguage }: TaskHydrationOptions = {},
): TaskHydrationSnapshot {
  const isBlockTask = isBlockAssemblyTaskType(task?.type)

  const activeTab = draft?.activeTab || "task"

  const draftBottomTab = normalizeBottomTab(draft?.bottomTab)
  const bottomTab = isBlockTask && draftBottomTab === "errors" ? "case" : draftBottomTab

  let resolvedKnownLanguage = ""
  let resolvedLearningLanguage = defaultId || languageOptions[0] || ""
  if (isFlowchartTask(task)) {
    const flowLangs = getParallelLanguages(task)
    resolvedLearningLanguage =
      (typeof draft?.userLanguage === "string" && draft.userLanguage) ||
      (defaultId && flowLangs.includes(defaultId) ? defaultId : "") ||
      flowLangs[0] ||
      languageOptions[0] ||
      ""
  } else {
    const pair = resolveParallelLanguagePair(task, { defaultId, languageOptions }, draft)
    resolvedKnownLanguage = pair.knownLanguage
    resolvedLearningLanguage = pair.learningLanguage
  }

  const code =
    shouldRestoreDraftCode(task) &&
    typeof draft?.code === "string" &&
    draft.code.trim()
      ? draft.code
      : getInitialStudentCode(task, resolvedLearningLanguage)

  const draftFlow = draft?.flow && typeof draft.flow === "object" ? draft.flow : null
  const defaultFlow = isFlowchartTask(task)
    ? (getStudentFlowStarterPayload(task) as FlowPayload)
    : { flow: [], nodes: [], edges: [] }
  const flow = isFlowchartTask(task)
    ? (resolveStudentFlowFromDraft(task, draftFlow, draft) as FlowPayload)
    : draftFlow && !isFlowEmpty(draftFlow)
      ? draftFlow
      : defaultFlow

  const taskPrimaryLanguage = String(task?.language || "").toLowerCase()
  const curriculumLearningLanguage =
    getCurriculumLearningLanguage(task) ||
    normalizeCurriculumLearningLanguage(String(task?.target_language || ""))
  const preferredLearningLanguage = normalizeCurriculumLearningLanguage(preferLearningLanguage)
  const learningAvailable = getLearningLanguages(task).map((lang) => String(lang).toLowerCase())
  const pickLearningLanguage = (lang: string | null | undefined): string => {
    const normalized = String(lang || "").toLowerCase()
    if (normalized && learningAvailable.includes(normalized)) return normalized
    return ""
  }

  const draftBlockLanguage =
    typeof draft?.blockLanguage === "string" ? draft.blockLanguage.toLowerCase() : ""
  const blockAssemblyLanguage = (() => {
    if (!isBlockTask) {
      return resolvedLearningLanguage
    }
    return (
      pickLearningLanguage(preferredLearningLanguage) ||
      pickLearningLanguage(draftBlockLanguage) ||
      pickLearningLanguage(curriculumLearningLanguage) ||
      pickLearningLanguage(taskPrimaryLanguage) ||
      resolvedLearningLanguage
    )
  })()

  const learningVariant = getBlockVariantForLanguage(task, blockAssemblyLanguage)
  const assemblyBlocks = learningVariant?.blocks ?? task?.blocks ?? []
  const assemblyLang = blockAssemblyLanguage
  const rawAssemblyTemplate = learningVariant?.template ?? task?.template ?? null
  const preparedScaffold = rawAssemblyTemplate
    ? prepareBlockAssemblyScaffold(rawAssemblyTemplate, assemblyBlocks, assemblyLang)
    : { template: "", baseCode: "" }
  const blockAssemblyCode = preparedScaffold.baseCode
  const draftPlacements = Array.isArray(draft?.blockPlacements)
    ? draft.blockPlacements.filter(
        (p) => p && typeof p.blockIndex === "number" && typeof p.line === "number",
      )
    : []
  const blockPlacements = normalizePlacements(draftPlacements, blockAssemblyCode)
  const blockLanguage = assemblyLang
  const selectedExampleLanguage = resolvedKnownLanguage
  let userLanguage = isBlockTask
    ? blockLanguage
    : isPascalCurriculumTask(task)
      ? "pascal"
      : isPythonCurriculumTask(task)
        ? "python"
        : isCppCurriculumTask(task)
          ? "cpp"
          : resolvedLearningLanguage

  const preferred = preferredLearningLanguage
  if (preferred) {
    const picked = pickLearningLanguage(preferred)
    if (picked) {
      userLanguage = picked
    } else if (!isBlockTask) {
      if (
        (preferred === "pascal" && isPascalCurriculumTask(task)) ||
        (preferred === "python" && isPythonCurriculumTask(task)) ||
        (preferred === "cpp" && isCppCurriculumTask(task)) ||
        (preferred === "csharp" && isCsharpCurriculumTask(task)) ||
        (preferred === "java" && isJavaCurriculumTask(task))
      ) {
        userLanguage = preferred
      }
    }
  }

  let flowchartSolutionMode: FlowchartSolutionMode = "code"
  if (isFlowchartTask(task)) {
    const defaultMode = getDefaultFlowchartSolutionMode(task) as FlowchartSolutionMode
    const draftMode = draft?.flowchartSolutionMode
    const canSwap = canSwapFlowchartSolutionModes(task)
    flowchartSolutionMode =
      draftMode === "flow" || draftMode === "code"
        ? canSwap
          ? (draftMode as FlowchartSolutionMode)
          : defaultMode
        : defaultMode
  }

  return {
    activeTab,
    bottomTab,
    code,
    flow,
    blockAssemblyCode,
    blockPlacements,
    blockLanguage,
    selectedExampleLanguage,
    userLanguage,
    flowchartSolutionMode,
  }
}
