import { api } from "@/shared/api"

export type DebugCodesPayload = {
  task_id: number
  slot_id: string | null
  languages: string[]
  fixed_codes: Record<string, string>
  buggy_codes: Record<string, string>
}

export async function fetchDebugCodes(taskId: number | string): Promise<DebugCodesPayload> {
  const res = await api.get<DebugCodesPayload>(`/tasks/debug-codes/${taskId}`)
  return res.data
}

export async function saveDebugCodes(
  taskId: number | string,
  payload: { fixed_codes?: Record<string, string>; buggy_codes?: Record<string, string> },
): Promise<DebugCodesPayload> {
  const res = await api.put<DebugCodesPayload>(`/tasks/debug-codes/${taskId}`, payload)
  return res.data
}
