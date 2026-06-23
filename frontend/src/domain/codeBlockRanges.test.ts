import { describe, expect, it } from "vitest"
import {
  addBlockRangeFromSelection,
  expandSelectionToCoveringBlocks,
  rangesToLegacyBlocks,
  resolveBlockConversionSpan,
} from "@/domain/codeBlockRanges"

const sample = [
  "n = int(input())\n",
  "grades = [int(input()) for _ in range(n)]\n",
  "\n",
  "best = grades[0]\n",
  "total = 0\n",
  "passed = 0\n",
].join("")

describe("resolveBlockConversionSpan", () => {
  it("expands empty caret on a line to the full line", () => {
    const lineStart = sample.indexOf("best = grades[0]")
    const caret = lineStart + 4
    const span = resolveBlockConversionSpan(sample, [], caret, caret)
    expect(sample.slice(span.start, span.end)).toBe("best = grades[0]")
  })

  it("keeps multiline drag selection as one span", () => {
    const start = sample.indexOf("best = grades[0]")
    const end = sample.indexOf("passed = 0") + "passed = 0".length
    const span = resolveBlockConversionSpan(sample, [], start, end)
    expect(sample.slice(span.start, span.end)).toBe(
      "best = grades[0]\ntotal = 0\npassed = 0",
    )
  })
})

describe("expandSelectionToCoveringBlocks", () => {
  it("expands partial selection to full multiline block", () => {
    const blockStart = sample.indexOf("best = grades[0]")
    const blockEnd = sample.indexOf("passed = 0") + "passed = 0".length
    const ranges = [{ id: "b1", start: blockStart, end: blockEnd }]
    const partial = sample.indexOf("total = 0") + 3
    const expanded = expandSelectionToCoveringBlocks(ranges, partial, partial, sample)
    expect(expanded.start).toBe(blockStart)
    expect(expanded.end).toBe(blockEnd)
  })
})

describe("rangesToLegacyBlocks", () => {
  it("keeps duplicate block text as separate indices", () => {
    const code = "begin\n  x;\nbegin\n  y;\nend."
    const secondBegin = code.indexOf("begin", 1)
    const ranges = [
      { id: "a", start: 0, end: 5 },
      { id: "b", start: secondBegin, end: secondBegin + 5 },
    ]
    const { blocks, order } = rangesToLegacyBlocks(code, ranges)
    expect(blocks).toEqual(["begin", "begin"])
    expect(order).toEqual([0, 1])
  })
})

describe("addBlockRangeFromSelection", () => {
  it("creates one block from multiline selection", () => {
    const start = sample.indexOf("best = grades[0]")
    const end = sample.indexOf("passed = 0") + "passed = 0".length
    const ranges = addBlockRangeFromSelection([], start, end, sample)
    expect(ranges).toHaveLength(1)
    expect(sample.slice(ranges[0].start, ranges[0].end)).toBe(
      "best = grades[0]\ntotal = 0\npassed = 0",
    )
  })
})
