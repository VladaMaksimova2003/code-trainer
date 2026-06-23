import { describe, expect, it } from "vitest"
import {
  normalizeBottomTab,
  resolveTaskHydration,
} from "@/features/task-solving/model/taskHydrationHelpers"

describe("normalizeBottomTab", () => {
  it("maps legacy lint/compiler/patterns to errors", () => {
    expect(normalizeBottomTab("lint")).toBe("errors")
    expect(normalizeBottomTab("compiler")).toBe("errors")
  })

  it("defaults unknown values to case", () => {
    expect(normalizeBottomTab(undefined)).toBe("case")
    expect(normalizeBottomTab("unknown")).toBe("case")
  })

  it("preserves comments tab", () => {
    expect(normalizeBottomTab("comments")).toBe("comments")
  })
})

describe("resolveTaskHydration", () => {
  it("restores code from matching draft", () => {
    const task = {
      id: 1,
      type: "algorithm",
      language: "python",
      template: "def solve():\n    pass",
    }
    const hydration = resolveTaskHydration(
      task,
      { code: "def solve():\n    return 1", bottomTab: "errors" },
      { defaultId: "python", languageOptions: ["python"] },
    )
    expect(hydration.code).toBe("def solve():\n    return 1")
    expect(hydration.bottomTab).toBe("errors")
  })

  it("uses initial code when draft is null", () => {
    const task = {
      id: 2,
      type: "algorithm",
      language: "python",
      template: "",
    }
    const hydration = resolveTaskHydration(task, null, {
      defaultId: "python",
      languageOptions: ["python"],
    })
    expect(typeof hydration.code).toBe("string")
    expect(hydration.activeTab).toBe("task")
    expect(hydration.bottomTab).toBe("case")
  })

  it("forces block tasks away from errors bottom tab on restore", () => {
    const task = {
      id: 3,
      type: "task_build_from_blocks",
      language: "python",
      blocks: [{ text: "print()" }],
      template: "{{0}}",
    }
    const hydration = resolveTaskHydration(
      task,
      { bottomTab: "errors", blockAssemblyCode: "{{0}}" },
      { defaultId: "python", languageOptions: ["python"] },
    )
    expect(hydration.bottomTab).toBe("case")
  })

  it("uses pascal user language for pascal curriculum tasks", () => {
    const task = {
      id: 4,
      type: "algorithm",
      language: "pascal",
      curriculum: { language: "pascal" },
    }
    const hydration = resolveTaskHydration(task, null, {
      defaultId: "python",
      languageOptions: ["python", "pascal"],
    })
    expect(hydration.userLanguage).toBe("pascal")
  })

  it("keeps preferred learning language on block tasks even when task.language is cpp", () => {
    const task = {
      id: 5,
      type: "task_build_from_blocks",
      language: "cpp",
      target_language: "cpp",
      curriculum: { language: "pascal", slot_id: "pas_002" },
      code_examples: {
        curriculum_showcase: { target_language: "cpp", slot_id: "pas_002" },
      },
      language_variants: {
        pascal: { template: "___", blocks: ["begin", "end."], correct_order: [0, 1] },
        cpp: { template: "___", blocks: ["int main(){", "}"], correct_order: [0, 1] },
      },
      blocks: ["int main(){", "}"],
      template: "___",
      correct_order: [0, 1],
    }
    const hydration = resolveTaskHydration(
      task,
      { blockLanguage: "python" },
      { preferLearningLanguage: "pascal" },
    )
    expect(hydration.blockLanguage).toBe("pascal")
    expect(hydration.userLanguage).toBe("pascal")
  })
})
