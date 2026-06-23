import { describe, expect, it } from "vitest"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import type { TaskDto } from "@/shared/types/task"

function task(overrides: Partial<TaskDto> = {}): TaskDto {
  return {
    id: 1,
    title: "Test",
    type: "task_translate_snippet",
    ...overrides,
  }
}

describe("isFlowchartTask", () => {
  it("returns true for blocks task type", () => {
    expect(isFlowchartTask(task({ type: "blocks" }))).toBe(true)
  })

  it("returns true for diagram task type", () => {
    expect(isFlowchartTask(task({ type: "diagram" }))).toBe(true)
  })

  it("returns true for task_flowchart_to_code task type", () => {
    expect(isFlowchartTask(task({ type: "task_flowchart_to_code" }))).toBe(true)
  })

  it("returns false for ordinary code task types", () => {
    expect(isFlowchartTask(task({ type: "task_translate_snippet" }))).toBe(false)
    expect(isFlowchartTask(task({ type: "task_build_from_blocks" }))).toBe(false)
    expect(isFlowchartTask(task({ type: "algorithm" }))).toBe(false)
  })

  it("returns false for null and undefined", () => {
    expect(isFlowchartTask(null)).toBe(false)
    expect(isFlowchartTask(undefined)).toBe(false)
  })

  it("ignores curriculum.flowchart_mode — detection is by task.type only", () => {
    expect(
      isFlowchartTask(
        task({
          type: "task_translate_snippet",
          curriculum: { flowchart_mode: "code_to_flowchart" },
        }),
      ),
    ).toBe(false)

    expect(
      isFlowchartTask(
        task({
          type: "blocks",
          curriculum: { flowchart_mode: "flowchart_to_code" },
        }),
      ),
    ).toBe(true)

    expect(
      isFlowchartTask(
        task({
          type: "diagram",
          curriculum: { flowchart_mode: "flowchart_to_blocks" },
        }),
      ),
    ).toBe(true)
  })

  it("ignores code_examples.curriculum_showcase.flowchart_mode", () => {
    expect(
      isFlowchartTask(
        task({
          type: "task_translate_full_program",
          code_examples: {
            curriculum_showcase: { flowchart_mode: "code_to_flowchart" },
          },
        }),
      ),
    ).toBe(false)
  })
})
