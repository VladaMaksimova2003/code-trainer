/**
 * Typed thin wrappers over `@/shared/api`.
 * No payload or response transformation — cast-only for future TS migration.
 */

import {
  checkFlow,
  getSubmission,
  getTask,
  submitSolution,
} from "@/shared/api"
import type { SubmissionResult, SubmitSolutionPayload } from "@/shared/types/execution"
import type { FlowCheckResult, FlowPayload } from "@/shared/types/flow"
import type { TaskDto } from "@/shared/types/task"

export type CheckFlowTypedPayload = FlowPayload & { task_id: number | string }

export interface SubmitSolutionTypedOptions {
  onStatus?: (submission: SubmissionResult) => void
}

export async function getTaskTyped(taskId: number | string): Promise<TaskDto> {
  return getTask(taskId) as Promise<TaskDto>
}

export async function checkFlowTyped(payload: CheckFlowTypedPayload): Promise<FlowCheckResult> {
  return checkFlow(payload) as Promise<FlowCheckResult>
}

export async function submitSolutionTyped(
  payload: SubmitSolutionPayload,
  options: SubmitSolutionTypedOptions = {},
): Promise<SubmissionResult> {
  return submitSolution(payload, options) as Promise<SubmissionResult>
}

export async function getSubmissionTyped(
  submissionId: number | string,
): Promise<SubmissionResult> {
  return getSubmission(submissionId) as Promise<SubmissionResult>
}
