import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { createDefaultSegments } from "@/features/task-editor/domain/codeSegment"
import { DifficultyLevel, TaskType } from "@/features/task-editor/domain/enums"
import { IoValueKind } from "@/features/task-editor/domain/ioValue"
import { getDefaultLanguageId } from "@/shared/config/languages"

export function createEmptyAssignmentDraft(): TaskDraft {
  const segments = createDefaultSegments("")
  return {
    title: "",
    description: "",
    type: TaskType.BUILD_FROM_BLOCKS,
    difficulty: DifficultyLevel.EASY,
    languages: [getDefaultLanguageId()],
    selectedPatterns: [],
    selectedPatternsByLanguage: {},
    code: { code: "", language: getDefaultLanguageId() },
    blockRanges: [],
    segments,
    selectedSegmentId: segments[0].id,
    analysis: null,
    testCases: [],
    ioSchema: {
      inputFormat: IoValueKind.SCALAR,
      outputFormat: IoValueKind.SCALAR,
    },
    flow: { flow: [], nodes: [], edges: [] },
    flowchartExposeReferenceCode: false,
    version: 1,
    updatedAt: new Date().toISOString(),
  }
}
