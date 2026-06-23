import { describe, expect, it } from "vitest"
import { getPostSolveExplanation, getTaskHints } from "@/features/task-solving/model/studentUiUtils"
import type { TaskDto } from "@/shared/types/task"

describe("debug task pedagogy helpers", () => {
  it("reads hints from top-level payload first", () => {
    const task = {
      hints: ["a", "b"],
      code_examples: { hints: ["legacy"] },
    } as unknown as TaskDto
    expect(getTaskHints(task)).toEqual(["a", "b"])
  })

  it("falls back to code_examples hints", () => {
    const task = {
      code_examples: { hints: ["from code_examples"] },
    } as unknown as TaskDto
    expect(getTaskHints(task)).toEqual(["from code_examples"])
  })

  it("reads post_solve from top-level payload", () => {
    const task = {
      post_solve_explanation: "Разбор",
      code_examples: { post_solve_explanation: "legacy" },
    } as unknown as TaskDto
    expect(getPostSolveExplanation(task)).toBe("Разбор")
  })
})
