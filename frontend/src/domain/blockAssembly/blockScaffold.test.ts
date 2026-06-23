import { describe, expect, it } from "vitest"
import {
  collectScaffoldGapRanges,
  isFullyBlockedExceptWhitespace,
  templateScaffoldIsWhitespaceOnly,
} from "@/domain/blockAssembly/blockScaffold"
import { assembleSlotTemplate } from "@/domain/blockAssembly/buildCode"
import type { CodeBlockRange } from "@/domain/codeBlockRanges"

describe("blockScaffold", () => {
  it("detects full block coverage with only spaces outside blocks", () => {
    const code = "n = int(input()) count = 0"
    const left = "n = int(input())"
    const right = "count = 0"
    const ranges: CodeBlockRange[] = [
      { id: "a", start: 0, end: left.length },
      { id: "b", start: code.indexOf(right), end: code.indexOf(right) + right.length },
    ]
    expect(isFullyBlockedExceptWhitespace(code, ranges)).toBe(true)
  })

  it("returns false when structural scaffold remains outside blocks", () => {
    const code = "if x:\n    pass"
    const passStart = code.indexOf("pass")
    const ranges: CodeBlockRange[] = [
      { id: "a", start: passStart, end: passStart + "pass".length },
    ]
    expect(isFullyBlockedExceptWhitespace(code, ranges)).toBe(false)
  })

  it("collects scaffold gaps only for structural text", () => {
    const code = "if x:\n    pass"
    const passStart = code.indexOf("pass")
    const ranges: CodeBlockRange[] = [
      { id: "a", start: passStart, end: passStart + "pass".length },
    ]
    const gaps = collectScaffoldGapRanges(code, ranges)
    expect(gaps).toHaveLength(1)
    expect(code.slice(gaps[0].start, gaps[0].end)).toBe(code.slice(0, passStart))
  })

  it("recognizes whitespace-only template scaffold", () => {
    expect(templateScaffoldIsWhitespaceOnly("{0} {1}\n{2}")).toBe(true)
    expect(templateScaffoldIsWhitespaceOnly("if x:\n{0}")).toBe(false)
  })
})

describe("assembleSlotTemplate spaces", () => {
  it("preserves spaces between blocks for python", () => {
    const template = "{0} {1}"
    const blocks = ["n = int(input())", "count = 0"]
    const placements = [
      { id: "p0", blockIndex: 0, line: 1, column: 1, slot: 0, templateSlot: 0 },
      { id: "p1", blockIndex: 1, line: 1, column: 18, slot: 1, templateSlot: 1 },
    ]
    const code = assembleSlotTemplate(template, blocks, placements)
    expect(code).toBe("n = int(input()) count = 0")
  })
})
