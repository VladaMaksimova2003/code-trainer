import { describe, expect, it } from "vitest"

import {
  assemblyCompletionStats,
  isAssemblyComplete,
  isSlotAssemblyOrderCorrect,
  isTemplateAssemblyComplete,
} from "@/domain/blockAssembly/normalize"

describe("block assembly completion", () => {
  it("requires every template slot, not the whole block pool", () => {
    const template = "name {0} = {1}(input())\ntotal = a {2} b"
    expect(isTemplateAssemblyComplete([], template)).toBe(false)
    expect(
      isTemplateAssemblyComplete(
        [
          { id: "a", blockIndex: 2, line: 1, column: 6, slot: 0, templateSlot: 0 },
          { id: "b", blockIndex: 0, line: 1, column: 11, slot: 1, templateSlot: 1 },
        ],
        template,
      ),
    ).toBe(false)

    const complete = [
      { id: "a", blockIndex: 2, line: 1, column: 6, slot: 0, templateSlot: 0 },
      { id: "b", blockIndex: 0, line: 1, column: 11, slot: 1, templateSlot: 1 },
      { id: "c", blockIndex: 4, line: 2, column: 11, slot: 0, templateSlot: 2 },
    ]
    expect(isTemplateAssemblyComplete(complete, template)).toBe(true)
    expect(isAssemblyComplete(complete, 12, template)).toBe(true)
    expect(assemblyCompletionStats(complete, 12, template)).toEqual({
      filled: 3,
      required: 3,
    })
  })

  it("checks slot order by block label, not exact duplicate index", () => {
    const blocks = ["total", "average", "total", "load", "load", "n"]
    const template = "var {0};\n{1} := 0;\ntotal := total + {2};\nwriteln(total div {3});"
    const correctOrder = [0, 2, 4, 5]
    const placements = [
      { id: "a", blockIndex: 0, line: 1, column: 5, slot: 0, templateSlot: 0 },
      { id: "b", blockIndex: 2, line: 2, column: 1, slot: 0, templateSlot: 1 },
      { id: "c", blockIndex: 3, line: 3, column: 18, slot: 0, templateSlot: 2 },
      { id: "d", blockIndex: 5, line: 4, column: 18, slot: 0, templateSlot: 3 },
    ]
    expect(isSlotAssemblyOrderCorrect(placements, blocks, correctOrder, template)).toBe(true)
    const swappedDuplicate = [
      placements[0],
      { ...placements[1], blockIndex: 0 },
      { ...placements[2], blockIndex: 4 },
      placements[3],
    ]
    expect(isSlotAssemblyOrderCorrect(swappedDuplicate, blocks, correctOrder, template)).toBe(
      true,
    )
    const wrongPlacements = [
      placements[0],
      placements[1],
      { ...placements[2], blockIndex: 1 },
      placements[3],
    ]
    expect(isSlotAssemblyOrderCorrect(wrongPlacements, blocks, correctOrder, template)).toBe(
      false,
    )
  })

  it("accepts interchangeable duplicate begin blocks when assembly matches", () => {
    const blocks = ["var n: integer;", "begin", "readln(n);", "begin", "end;"]
    const template = "{0}\n{1}\n  {2}\n{3}\n  writeln(n);\n{4}"
    const correctOrder = [0, 1, 2, 3, 4]
    const expected = [
      { id: "a", blockIndex: 0, line: 1, column: 1, slot: 0, templateSlot: 0 },
      { id: "b", blockIndex: 1, line: 2, column: 1, slot: 0, templateSlot: 1 },
      { id: "c", blockIndex: 2, line: 3, column: 1, slot: 0, templateSlot: 2 },
      { id: "d", blockIndex: 3, line: 4, column: 1, slot: 0, templateSlot: 3 },
      { id: "e", blockIndex: 4, line: 6, column: 1, slot: 0, templateSlot: 4 },
    ]
    expect(isSlotAssemblyOrderCorrect(expected, blocks, correctOrder, template)).toBe(true)
    const swappedBegins = [
      expected[0],
      { ...expected[1], blockIndex: 3 },
      expected[2],
      { ...expected[3], blockIndex: 1 },
      expected[4],
    ]
    expect(isSlotAssemblyOrderCorrect(swappedBegins, blocks, correctOrder, template)).toBe(true)
  })
})
