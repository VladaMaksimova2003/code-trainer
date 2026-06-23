import { describe, expect, it } from "vitest"
import { isInfrastructureError } from "@/features/task-solving/model/executionResultHelpers"

describe("isInfrastructureError", () => {
  it("detects docker and timeout errors", () => {
    expect(isInfrastructureError([{ type: "TIMEOUT", text: "x" }])).toBe(true)
    expect(isInfrastructureError([{ type: "EXECUTION", text: "Docker is required" }])).toBe(true)
    expect(isInfrastructureError([{ type: "LINT", text: "unused variable" }])).toBe(false)
  })
})
