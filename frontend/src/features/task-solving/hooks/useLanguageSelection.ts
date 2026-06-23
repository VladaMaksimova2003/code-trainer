import { useCallback, useEffect, useState } from "react"
import { prepareBlockAssemblyScaffold } from "@/domain/blockAssembly"
import type { BlockPlacement } from "@/domain/blockAssembly"
import {
  canSwapFlowchartSolutionModes,
  canSwapParallelLanguages,
  getBlockVariantForLanguage,
  getDefaultFlowchartSolutionMode,
  getInitialStudentCode,
  getKnownLanguages,
  getLearningLanguages,
  getMirrorSiblingLanguage,
  getTaskPrimaryAction,
  isCurriculumMirrorTask,
  resolveKnownLanguageWithReference,
} from "@/features/task-solving/model/studentUiUtils"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import type { TaskDto } from "@/shared/types/task"
import type { TaskHydrationSnapshot } from "@/features/task-solving/hooks/useTaskLoader"

type FlowchartSolutionMode = "code" | "flow"

function pickFallbackKnownLanguage(task: TaskDto | null, exclude: string): string {
  const known = getKnownLanguages(task).filter((lang) => lang !== exclude)
  if (isCurriculumMirrorTask(task)) {
    const sibling = getMirrorSiblingLanguage(task)
    if (sibling && sibling !== exclude && known.includes(sibling)) {
      return resolveKnownLanguageWithReference(task, sibling)
    }
  }
  for (const pref of ["python", "pascal", "cpp", "csharp", "java"]) {
    if (pref !== exclude && known.includes(pref)) {
      return resolveKnownLanguageWithReference(task, pref)
    }
  }
  return resolveKnownLanguageWithReference(task, known[0] || "")
}

interface UseLanguageSelectionOptions {
  task: TaskDto | null
  isBlockAssemblyTask: boolean
  defaultId: string
  setBlockAssemblyCode: (code: string) => void
  setBlockPlacements: (placements: BlockPlacement[]) => void
  setCode?: (code: string) => void
}

/**
 * Parallel / block / flowchart language selection (FE-ARCH-6.3).
 */
export function useLanguageSelection({
  task,
  isBlockAssemblyTask,
  defaultId,
  setBlockAssemblyCode,
  setBlockPlacements,
  setCode,
}: UseLanguageSelectionOptions) {
  const [selectedExampleLanguage, setSelectedExampleLanguage] = useState(defaultId)
  const [userLanguage, setUserLanguage] = useState(defaultId)
  const [blockLanguage, setBlockLanguage] = useState(defaultId)
  const [flowchartSolutionMode, setFlowchartSolutionMode] = useState<FlowchartSolutionMode>("code")

  const applyLearningLanguageVariant = useCallback(
    (nextLanguage: string) => {
      if (!task || !isBlockAssemblyTask) return
      const variant = getBlockVariantForLanguage(task, nextLanguage)
      if (!variant) return
      setBlockLanguage(nextLanguage)
      const { baseCode } = prepareBlockAssemblyScaffold(
        variant.template,
        variant.blocks ?? [],
        nextLanguage,
      )
      setBlockAssemblyCode(baseCode)
      setBlockPlacements([])
    },
    [task, isBlockAssemblyTask, setBlockAssemblyCode, setBlockPlacements],
  )

  const applyLanguageHydration = useCallback((hydration: TaskHydrationSnapshot) => {
    setSelectedExampleLanguage(hydration.selectedExampleLanguage)
    setUserLanguage(hydration.userLanguage)
    setBlockLanguage(hydration.blockLanguage)
    setFlowchartSolutionMode(hydration.flowchartSolutionMode)
  }, [])

  useEffect(() => {
    if (!task || isFlowchartTask(task)) return
    const known = getKnownLanguages(task)
    if (!known.length) return
    const resolved = resolveKnownLanguageWithReference(task, selectedExampleLanguage)
    if (resolved && resolved !== selectedExampleLanguage) {
      setSelectedExampleLanguage(resolved)
    }
  }, [task, selectedExampleLanguage])

  useEffect(() => {
    if (!task || !isFlowchartTask(task)) return
    if (canSwapFlowchartSolutionModes(task)) return
    const defaultMode = getDefaultFlowchartSolutionMode(task) as FlowchartSolutionMode
    setFlowchartSolutionMode((mode) => (mode === defaultMode ? mode : defaultMode))
  }, [task])

  const handleTaskLanguageChange = useCallback(
    (nextLanguage: string) => {
      const resolved = task
        ? resolveKnownLanguageWithReference(task, nextLanguage)
        : nextLanguage
      setSelectedExampleLanguage(resolved)
      if (resolved && resolved === userLanguage) {
        const fallback = pickFallbackKnownLanguage(task, resolved)
        setUserLanguage(fallback)
        applyLearningLanguageVariant(fallback)
      }
    },
    [task, userLanguage, applyLearningLanguageVariant],
  )

  const reloadDebugStudentCode = useCallback(
    (learningLanguage: string) => {
      if (!task || !setCode || getTaskPrimaryAction(task) !== "debug") return
      setCode(getInitialStudentCode(task, learningLanguage))
    },
    [task, setCode],
  )

  const handleUserLanguageChange = useCallback(
    (nextLanguage: string) => {
      setUserLanguage(nextLanguage)
      applyLearningLanguageVariant(nextLanguage)
      reloadDebugStudentCode(nextLanguage)
      if (nextLanguage && nextLanguage === selectedExampleLanguage) {
        setSelectedExampleLanguage(pickFallbackKnownLanguage(task, nextLanguage))
      }
    },
    [task, selectedExampleLanguage, applyLearningLanguageVariant, reloadDebugStudentCode],
  )

  const swapLanguages = useCallback(() => {
    if (!task) return
    const knownAvailable = getKnownLanguages(task)
    const learningAvailable = getLearningLanguages(task)
    if (
      !canSwapParallelLanguages(
        selectedExampleLanguage,
        userLanguage,
        knownAvailable,
        learningAvailable,
        task,
      )
    ) {
      return
    }
    const nextKnown = userLanguage
    const nextLearning = selectedExampleLanguage
    setSelectedExampleLanguage(nextKnown)
    setUserLanguage(nextLearning)
    applyLearningLanguageVariant(nextLearning)
    reloadDebugStudentCode(nextLearning)
  }, [task, selectedExampleLanguage, userLanguage, applyLearningLanguageVariant, reloadDebugStudentCode])

  const swapFlowchartSolutionMode = useCallback(() => {
    if (!canSwapFlowchartSolutionModes(task)) return
    setFlowchartSolutionMode((mode) => (mode === "code" ? "flow" : "code"))
  }, [task])

  return {
    selectedExampleLanguage,
    setSelectedExampleLanguage,
    userLanguage,
    setUserLanguage,
    blockLanguage,
    setBlockLanguage,
    flowchartSolutionMode,
    setFlowchartSolutionMode,
    applyLanguageHydration,
    handleTaskLanguageChange,
    handleUserLanguageChange,
    swapLanguages,
    swapFlowchartSolutionMode,
  }
}
