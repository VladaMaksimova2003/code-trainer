import type { PanelError } from "@/shared/types/execution"

/** Returns true when lint/execution errors indicate infra failure (skip surfacing as linter noise). */
export function isInfrastructureError(errors: PanelError[] = []): boolean {
  return errors.some((error) => {
    const type = String(error?.type || "").toUpperCase()
    const text = String(error?.text || "")
    return (
      type === "INTERNAL_ERROR" ||
      type === "TIMEOUT" ||
      text.includes("Docker is required") ||
      text.includes("Docker is not available") ||
      text.includes("Submission is still processing") ||
      text.includes("Сервер проверки не отвечает")
    )
  })
}
