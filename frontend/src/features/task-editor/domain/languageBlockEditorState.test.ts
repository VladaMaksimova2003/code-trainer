import { describe, expect, it } from "vitest"
import type { TaskDraft } from "@/features/task-editor/domain/entities"
import {
  resolveLanguageBlockEditorPatch,
  snapshotDraftBlockEditor,
} from "@/features/task-editor/domain/languageBlockEditorState"

const baseDraft = (): TaskDraft => ({
  title: "t",
  description: "d",
  type: "block_reorder",
  difficulty: "easy",
  languages: ["python"],
  selectedPatterns: [],
  code: { code: "a = 1\nprint(a)", language: "python" },
  blockRanges: [{ id: "r1", start: 0, end: 5 }],
  analysis: null,
  testCases: [],
  ioSchema: { inputFormat: "scalar", outputFormat: "scalar" },
  languageVariants: {
    pascal: { original_code: "begin\n  writeln(1);\nend." },
  },
  version: 1,
  updatedAt: "",
})

describe("languageBlockEditorState", () => {
  it("preserves python markings when switching away and back", () => {
    const draft = baseDraft()
    const toPascal = resolveLanguageBlockEditorPatch(draft, "pascal")
    const pascalDraft = { ...draft, ...toPascal } as TaskDraft

    const backToPython = resolveLanguageBlockEditorPatch(pascalDraft, "python")
    expect(backToPython.code?.code).toBe("a = 1\nprint(a)")
    expect(backToPython.blockRanges).toEqual([{ id: "r1", start: 0, end: 5 }])
  })

  it("snapshotDraftBlockEditor stores current language slice", () => {
    const draft = baseDraft()
    const state = snapshotDraftBlockEditor(draft)
    expect(state.python?.blockRanges).toHaveLength(1)
    expect(state.python?.code).toContain("print")
  })
})
