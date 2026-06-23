import { describe, expect, it } from "vitest"
import { buildCode } from "@/domain/blockAssembly/buildCode"
import { shiftPlacementColumn } from "@/domain/blockAssembly/drop"
import { isTemplateAssemblyMode } from "@/widgets/BlockAssemblyEditor/lib/blockAssemblyMode"

describe("isTemplateAssemblyMode whitespace scaffold", () => {
  it("uses free assembly when template is whitespace-only", () => {
    const template = "{0}\n{1}\n    {2}\n        {3}"
    expect(isTemplateAssemblyMode("        \n            ", template)).toBe(false)
  })

  it("uses template assembly when scaffold has fixed code", () => {
    expect(isTemplateAssemblyMode("if x:\n    ", "if x:\n{0}")).toBe(true)
  })
})

describe("shiftPlacementColumn", () => {
  it("shifts block column for python indent", () => {
    const placements = [
      { id: "p1", blockIndex: 2, line: 3, column: 5, slot: 0, templateSlot: 2 },
    ]
    const next = shiftPlacementColumn(placements, "p1", 1, "    \n        ")
    expect(next[0].column).toBe(9)
    const code = buildCode("    \n        \n            ", next, [
      "n = int(input())",
      "count = 0",
      "for _ in range(n):",
      "    amount = int(input())",
      "        count += 1",
    ])
    expect(code).toContain("    for _ in range(n):")
  })
})

describe("buildCode priority over slot template", () => {
  it("respects column indent on whitespace scaffold lines", () => {
    const base = "        \n            "
    const blocks = ["for _ in range(n):", "    count += 1"]
    const placements = [
      { id: "a", blockIndex: 0, line: 1, column: 5, slot: 0, templateSlot: 0 },
      { id: "b", blockIndex: 1, line: 2, column: 5, slot: 0, templateSlot: 1 },
    ]
    const code = buildCode(base, placements, blocks)
    expect(code).toContain("for _ in range(n):")
    expect(code).toContain("count += 1")
    expect(code.indexOf("count")).toBeGreaterThan(code.indexOf("for"))
  })
})
