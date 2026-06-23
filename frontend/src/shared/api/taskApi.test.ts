import { beforeEach, describe, expect, it, vi } from "vitest"
import type { FlowCheckResult, FlowPayload } from "@/shared/types/flow"
import type { SubmissionResult, SubmitSolutionPayload } from "@/shared/types/execution"
import type { TaskDto } from "@/shared/types/task"

const { getTask, checkFlow, submitSolution, getSubmission } = vi.hoisted(() => ({
  getTask: vi.fn(),
  checkFlow: vi.fn(),
  submitSolution: vi.fn(),
  getSubmission: vi.fn(),
}))

vi.mock("@/shared/api", () => ({
  getTask,
  checkFlow,
  submitSolution,
  getSubmission,
}))

import {
  checkFlowTyped,
  getSubmissionTyped,
  getTaskTyped,
  submitSolutionTyped,
} from "@/shared/api/taskApi"

describe("taskApi typed wrappers", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("getTaskTyped delegates to getTask with same id and returns same object", async () => {
    const task: TaskDto = { id: 13, type: "blocks", title: "Flow task" }
    getTask.mockResolvedValue(task)

    const result = await getTaskTyped(13)

    expect(getTask).toHaveBeenCalledTimes(1)
    expect(getTask).toHaveBeenCalledWith(13)
    expect(result).toBe(task)
  })

  it("checkFlowTyped delegates to checkFlow without changing payload or response", async () => {
    const payload: FlowPayload & { task_id: number } = {
      task_id: 25,
      flow: [{ type: "start" }, { type: "end" }],
      nodes: [{ id: "n1", type: "start" }],
      edges: [],
    }
    const response: FlowCheckResult = {
      success: true,
      errors: [],
      debug: { node_count: 2 },
    }
    checkFlow.mockResolvedValue(response)

    const result = await checkFlowTyped(payload)

    expect(checkFlow).toHaveBeenCalledTimes(1)
    expect(checkFlow).toHaveBeenCalledWith(payload)
    expect(result).toBe(response)
  })

  it("submitSolutionTyped delegates to submitSolution with same payload and options", async () => {
    const payload: SubmitSolutionPayload = {
      task_id: 8,
      language: "python",
      code: "print(1)",
    }
    const onStatus = vi.fn()
    const response: SubmissionResult = {
      task_id: 8,
      success: true,
      test_results: [{ case: 1, status: "PASSED" }],
    }
    submitSolution.mockResolvedValue(response)

    const result = await submitSolutionTyped(payload, { onStatus })

    expect(submitSolution).toHaveBeenCalledTimes(1)
    expect(submitSolution).toHaveBeenCalledWith(payload, { onStatus })
    expect(result).toBe(response)
  })

  it("getSubmissionTyped delegates to getSubmission with same id and returns same object", async () => {
    const response: SubmissionResult = {
      submission_id: 99,
      status: "done",
      success: true,
    }
    getSubmission.mockResolvedValue(response)

    const result = await getSubmissionTyped(99)

    expect(getSubmission).toHaveBeenCalledTimes(1)
    expect(getSubmission).toHaveBeenCalledWith(99)
    expect(result).toBe(response)
  })
})
