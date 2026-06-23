import { describe, expect, it } from "vitest"
import type { TaskDto } from "@/shared/types/task"
import {
  getKnownLanguages,
  getReferenceCode,
  resolveKnownLanguageWithReference,
} from "@/features/task-solving/model/studentUiUtils"

function makeTask(overrides: Partial<TaskDto> = {}): TaskDto {
  return {
    id: 2,
    title: "Linear search",
    type: "task_translate_full_program",
    language: "pascal",
    target_language: "pascal",
    curriculum: {
      language: "pascal",
      group: "pascal_curriculum_v311",
      slot_id: "pas_002",
    },
    code_examples: {
      pascal:
        "var n, i, code, target, position: integer;\nbegin\n  readln(n, target);\nend.",
      python:
        "n, target = map(int, input().split())\nposition = 0\nfor i in range(1, n + 1):\n    code = int(input())\n",
      cpp: "#include <iostream>\nint main() { return 0; }",
      curriculum_showcase: {
        slot_id: "pas_002",
        target_language: "pascal",
      },
    },
    ...overrides,
  } as TaskDto
}

describe("getKnownLanguages", () => {
  it("keeps pascal available in «Я знаю» for pascal curriculum tasks", () => {
    const task = makeTask()
    expect(getKnownLanguages(task)).toContain("pascal")
    expect(getKnownLanguages(task)).toContain("python")
  })

  it("resolveKnownLanguageWithReference prefers language with matching snippet", () => {
    const task = makeTask()
    const python = getReferenceCode(task, "python") || ""
    const resolved = resolveKnownLanguageWithReference(task, "python")
    expect(resolved).toBe("python")
    expect(getReferenceCode(task, resolved)).toBe(python)
    expect(getReferenceCode(task, resolved)).not.toContain("readln(")
  })
})
