import { describe, expect, it } from "vitest"
import { assembleSlotTemplate } from "@/domain/blockAssembly/buildCode"
import { buildAssemblyPreviewCode } from "@/domain/blockAssembly/scaffold"
import type { BlockPlacement } from "@/domain/blockAssembly/types"

const rawTemplate =
  "var a: array[1..5] of {0} = (5, 2, 9, 1, 7);var i, {1}: integer;begin  maximum := a[1];  for i := 1 to 5 do    if a[i] > maximum then maximum := a[i];  {2}(maximum);end."

const blocks = [
  "integer",
  "real",
  "string",
  "boolean",
  "maximum",
  "minimum",
  "result",
  "current",
  "writeln",
  "readln",
  "write",
  "print",
]

const slotPlacements: BlockPlacement[] = [
  { id: "a", blockIndex: 0, line: 1, column: 1, slot: 0, templateSlot: 0 },
  { id: "b", blockIndex: 4, line: 2, column: 1, slot: 0, templateSlot: 1 },
  { id: "c", blockIndex: 8, line: 7, column: 1, slot: 0, templateSlot: 2 },
]

describe("assembleSlotTemplate", () => {
  it("replaces numbered slots like backend build_code", () => {
    const code = assembleSlotTemplate(rawTemplate, blocks, slotPlacements)
    expect(code).toMatch(/writeln\s*\(\s*maximum\s*\)/i)
    expect(code).toMatch(/integer/i)
    expect(code).not.toMatch(/\{0\}/)
  })

  it("buildAssemblyPreviewCode uses slot assembly for concept checks", () => {
    const preview = buildAssemblyPreviewCode(rawTemplate, blocks, slotPlacements, "", "pascal")
    expect(/\b(writeln|write)\b/i.test(preview)).toBe(true)
  })

  it("prefers slot assembly over column buildCode when baseCode exists", () => {
    const template = `n, target = map(int, input().split())position = 0
for i in range(1, n + 1):
    code = int(input())
    if code == {0} and position == 0:
        position = {1}
        print(position)`
    const taskBlocks = ["target", "code", "i", "n"]
    const placements: BlockPlacement[] = [
      { id: "a", blockIndex: 0, line: 4, column: 12, slot: 0, templateSlot: 0 },
      { id: "b", blockIndex: 2, line: 5, column: 18, slot: 0, templateSlot: 1 },
    ]
    const baseCode = " ".repeat(80)
    const preview = buildAssemblyPreviewCode(template, taskBlocks, placements, baseCode, "python")
    expect(preview).toContain("if code == target")
    expect(preview).toContain("position = i")
    expect(preview).toMatch(/\bfor\b/i)
    expect(preview).not.toMatch(/\{0\}/)
  })
})
