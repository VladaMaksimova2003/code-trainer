import { describe, expect, it } from "vitest"
import {
  isCurriculumLanguageSwitch,
  taskSupportsLearningLanguageLocally,
} from "@/features/task-solving/model/curriculumMirrorNavigation"
import type { TaskDto } from "@/shared/types/task"

const unifiedTask = {
  id: 1,
  teacher_assembly_override: true,
  language_variants: {
    pascal: { template: "{0}\n{1}", blocks: ["begin", "end."] },
    java: { template: "{0}\n{1}", blocks: ["class Main", "}"] },
  },
  code_examples: {
    curriculum_showcase: {
      slot_id: "pas_001",
      target_language: "pascal",
      pedagogical_slot_id: "prc_001",
    },
  },
  curriculum: { language: "pascal", slot_id: "pas_001" },
  target_language: "pascal",
} as unknown as TaskDto

describe("taskSupportsLearningLanguageLocally", () => {
  it("returns true when teacher override is set", () => {
    expect(taskSupportsLearningLanguageLocally(unifiedTask, "java")).toBe(true)
  })

  it("returns true when language variant has assembly", () => {
    const task = {
      language_variants: {
        python: { template: "{0}", blocks: ["print(1)"] },
      },
    } as unknown as TaskDto
    expect(taskSupportsLearningLanguageLocally(task, "python")).toBe(true)
  })

  it("returns true for any track when teacher override is active", () => {
    expect(taskSupportsLearningLanguageLocally(unifiedTask, "csharp")).toBe(true)
  })
})

describe("isCurriculumLanguageSwitch", () => {
  it("never switches to another task id", () => {
    expect(isCurriculumLanguageSwitch(unifiedTask, "java", "pascal")).toBe(false)
    expect(isCurriculumLanguageSwitch(unifiedTask, "python", "pascal")).toBe(false)
  })
})
