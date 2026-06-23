import { describe, expect, it } from "vitest"
import { createEmptyAssignmentDraft } from "@/features/task-editor/application/use-cases/clearAssignmentDraft"
import {
  collectLanguageCodeSamples,
  getSelectedConceptIdsForLanguage,
  listConceptEditorLanguages,
  mapConceptIdsToPatterns,
  mergeConceptIdsForLanguage,
  setSelectedConceptIdsForLanguage,
} from "@/features/task-editor/domain/expectedConceptPatterns"

describe("expectedConceptPatterns", () => {
  it("collects code from block editor state and variants", () => {
    const draft = {
      ...createEmptyAssignmentDraft(),
      code: { code: "print(1)", language: "python" },
      languages: ["python"],
      languageBlockEditorState: {
        pascal: { code: "writeln(1);", blockRanges: [] },
      },
      languageVariants: {
        cpp: { original_code: "cout << 1;" },
      },
    }
    const samples = collectLanguageCodeSamples(draft)
    expect(samples.map((item) => item.language).sort()).toEqual(["cpp", "pascal", "python"])
  })

  it("maps catalog labels onto concept ids", () => {
    const catalog = [{ id: "stdin_read", type: "stdin_read", label: "Ввод", confidence: 1 }]
    const patterns = mapConceptIdsToPatterns(catalog, ["stdin_read"])
    expect(patterns[0]?.label).toBe("Ввод")
  })

  it("stores concepts per language independently", () => {
    const draft = createEmptyAssignmentDraft()
    const byLang = setSelectedConceptIdsForLanguage(draft, "python", ["a", "b"])
    const updated = { ...draft, selectedPatternsByLanguage: byLang }
    expect(getSelectedConceptIdsForLanguage(updated, "python")).toEqual(["a", "b"])
    expect(getSelectedConceptIdsForLanguage(updated, "pascal")).toEqual([])
  })

  it("merges detected ids without dropping existing", () => {
    expect(mergeConceptIdsForLanguage(["a"], ["b", "a"])).toEqual(["a", "b"])
  })

  it("lists editor languages from draft snapshots", () => {
    const draft = {
      ...createEmptyAssignmentDraft(),
      languageBlockEditorState: { java: { code: "class Main {}", blockRanges: [] } },
    }
    expect(listConceptEditorLanguages(draft)).toContain("java")
  })
})
