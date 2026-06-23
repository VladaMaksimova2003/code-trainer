import { flowPayloadSignature } from "@/widgets/BlockEditor/lib/flowPayload"
import type { FlowPayload } from "@/shared/types/flow"

export function flowPayloadSignatureSafe(payload: FlowPayload | null | undefined): string {
  if (!payload) return ""
  try {
    return flowPayloadSignature(payload)
  } catch {
    return ""
  }
}
