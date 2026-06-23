import { create } from "zustand"
import { AnalysisStatus } from "@/features/task-editor/domain/enums"
import type { AnalysisResult, Pattern, TaskDraft, TestCase } from "@/features/task-editor/domain/entities"
import { ensureDraftBlockEditor } from "@/features/task-editor/domain/blockEditor"
import {
  currentDraftLanguage,
  snapshotDraftBlockEditor,
} from "@/features/task-editor/domain/languageBlockEditorState"
import type { CodeBlockRange } from "@/features/task-editor/domain/blockEditor"
import { normalizeRanges } from "@/domain/codeBlockRanges"
import { updateTaskDraft } from "@/features/task-editor/application/use-cases/updateTaskDraft"
import { createEmptyAssignmentDraft } from "@/features/task-editor/application/use-cases/clearAssignmentDraft"
import { normalizeIoValue, IoValueKind } from "@/features/task-editor/domain/ioValue"
import { flowsEqual } from "@/features/task-editor/domain/flowSnapshot"

const STORAGE_KEY = "task-editor-draft-v2"

function migrateDraft(parsed: Partial<TaskDraft>): TaskDraft {
  const base = { ...createEmptyAssignmentDraft(), ...parsed }
  base.testCases = (parsed.testCases ?? []).map((tc) => ({
    ...tc,
    input: normalizeIoValue(
      (tc as TestCase & { input?: unknown }).input ?? ""
    ),
    expectedOutput: normalizeIoValue(
      (tc as TestCase & { expectedOutput?: unknown }).expectedOutput ?? ""
    ),
  }))
  if (parsed.ioSchema) {
    base.ioSchema = parsed.ioSchema
  } else {
    base.ioSchema = {
      inputFormat: IoValueKind.SCALAR,
      outputFormat: IoValueKind.SCALAR,
    }
  }
  return ensureDraftBlockEditor(base)
}

interface TaskDraftState {
  draft: TaskDraft
  isSaving: boolean
  saveError: string | null
  patchDraft: (patch: Partial<TaskDraft>) => void
  setDraft: (draft: TaskDraft) => void
  setAnalysis: (analysis: AnalysisResult | null) => void
  setSelectedPatterns: (patterns: Pattern[]) => void
  setTestCases: (cases: TestCase[]) => void
  setBlockTaskEditor: (payload: {
    code: string
    blockRanges: CodeBlockRange[]
  }) => void
  setSaving: (v: boolean) => void
  setSaveError: (msg: string | null) => void
  loadAutosave: () => void
  autosave: () => void
  reset: () => void
}

export const useTaskDraftStore = create<TaskDraftState>((set, get) => ({
  draft: ensureDraftBlockEditor(createEmptyAssignmentDraft()),
  isSaving: false,
  saveError: null,

  patchDraft: (patch) =>
    set((s) => {
      if (patch.flow !== undefined && flowsEqual(s.draft.flow, patch.flow)) {
        return s
      }
      const next = updateTaskDraft(s.draft, patch)
      return { draft: ensureDraftBlockEditor(next) }
    }),

  setDraft: (draft) => set({ draft: ensureDraftBlockEditor(draft) }),

  setAnalysis: (analysis) =>
    set((s) => ({
      draft: updateTaskDraft(s.draft, {
        analysis,
        selectedPatterns: analysis?.patterns?.length
          ? analysis.patterns.map((p) => ({ ...p, approved: true }))
          : s.draft.selectedPatterns,
      }),
    })),

  setSelectedPatterns: (selectedPatterns) =>
    set((s) => ({ draft: updateTaskDraft(s.draft, { selectedPatterns }) })),

  setTestCases: (testCases) =>
    set((s) => ({ draft: updateTaskDraft(s.draft, { testCases }) })),

  setBlockTaskEditor: ({ code, blockRanges }) =>
    set((s) => {
      const draft = ensureDraftBlockEditor(s.draft)
      const lang = currentDraftLanguage(draft)
      const normalizedRanges = normalizeRanges(blockRanges, code)
      return {
        draft: ensureDraftBlockEditor(
          updateTaskDraft(draft, {
            code: { ...draft.code, code },
            blockRanges: normalizedRanges,
            languageBlockEditorState: {
              ...snapshotDraftBlockEditor(draft, lang),
              [lang]: { code, blockRanges: normalizedRanges },
            },
          }),
        ),
      }
    }),

  setSaving: (isSaving) => set({ isSaving }),
  setSaveError: (saveError) => set({ saveError }),

  loadAutosave: () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return
      const parsed = JSON.parse(raw) as Partial<TaskDraft>
      set({ draft: migrateDraft(parsed) })
    } catch {
      /* ignore */
    }
  },

  autosave: () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(get().draft))
    } catch {
      /* ignore */
    }
  },

  reset: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({
      draft: ensureDraftBlockEditor(createEmptyAssignmentDraft()),
      saveError: null,
    })
  },
}))

export function isAnalyzing(draft: TaskDraft): boolean {
  return draft.analysis?.status === AnalysisStatus.ANALYZING
}
