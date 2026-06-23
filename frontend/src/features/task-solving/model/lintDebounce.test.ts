import { describe, expect, it } from "vitest"
import { lintDebounceMs } from "@/features/task-solving/model/lintDebounce"

describe("lintDebounceMs", () => {
  it("uses shorter delay for ruff/javac languages", () => {
    expect(lintDebounceMs("python")).toBe(450)
    expect(lintDebounceMs("java")).toBe(500)
  })

  it("uses moderate delay for pascal fpc", () => {
    expect(lintDebounceMs("pascal")).toBe(650)
  })

  it("uses javac-like delay for cpp and csharp dotnet build", () => {
    expect(lintDebounceMs("cpp")).toBe(500)
    expect(lintDebounceMs("csharp")).toBe(500)
  })
})
