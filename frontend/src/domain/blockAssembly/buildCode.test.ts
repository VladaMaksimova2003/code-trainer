import { describe, expect, it } from "vitest"
import { buildCode } from "@/domain/blockAssembly/buildCode"
import { applyDrop, resolveDropTarget } from "@/domain/blockAssembly/drop"
import { normalizeCodeColumn, snapColumnToTab } from "@/domain/blockAssembly/utils"
import type { BlockPlacement } from "@/domain/blockAssembly/types"

function placement(
  blockIndex: number,
  line: number,
  column: number,
  slot = 0,
): BlockPlacement {
  return {
    id: `p-${blockIndex}-${line}-${slot}`,
    blockIndex,
    line,
    column,
    slot,
  }
}

describe("normalizeCodeColumn", () => {
  it("keeps user-selected columns inside leading spaces", () => {
    expect(normalizeCodeColumn("    pass", 2)).toBe(2)
    expect(normalizeCodeColumn("    pass", 4)).toBe(4)
    expect(normalizeCodeColumn("", 5)).toBe(5)
    expect(normalizeCodeColumn("abc", 10)).toBe(10)
  })
})

describe("snapColumnToTab", () => {
  it("snaps columns to nearest 4-space tab stops", () => {
    expect(snapColumnToTab(1)).toBe(1)
    expect(snapColumnToTab(3)).toBe(5)
    expect(snapColumnToTab(7)).toBe(9)
    expect(snapColumnToTab(10)).toBe(9)
  })
})

describe("getInitialBaseCode", () => {
  it("uses gap spaces for slot-only template rows", async () => {
    const { getInitialBaseCode } = await import("@/domain/blockAssembly/buildCode")
    const base = getInitialBaseCode("a = 1\n{0}", ["print(a)"])
    expect(base.startsWith("a = 1\n")).toBe(true)
    expect((base.split("\n")[1] ?? "").trim().length).toBe(0)
    expect((base.split("\n")[1] ?? "").length).toBeGreaterThan(0)
  })

  it("renders gaps for placeholder-only assembly template", async () => {
    const { getInitialBaseCode } = await import("@/domain/blockAssembly/buildCode")
    const base = getInitialBaseCode("{0}\n{1}", ["begin", "end."])
    const lines = base.split("\n")
    expect(lines[0]?.length).toBeGreaterThan(0)
    expect(lines[1]?.length).toBeGreaterThan(0)
  })
})

describe("buildCode", () => {
  it("assembles slot-only template without spurious indent", () => {
    const baseCode = "a = int(input())\nb = int(input())\n"
    const code = buildCode(baseCode, [placement(0, 3, 1)], ["print(a + b)"])
    expect(code).toBe("a = int(input())\nb = int(input())\nprint(a + b)")
  })

  it("empty base + return at line 1 col 1", () => {
    const code = buildCode("", [placement(0, 1, 1)], ["return"])
    expect(code).toBe("return")
  })

  it("indented base line + block at column 5", () => {
    const baseCode = "if x:\n    "
    const code = buildCode(
      baseCode,
      [placement(0, 2, 5)],
      ["print(x)"],
    )
    expect(code).toBe("if x:\n    print(x)")
  })

  it("two blocks on one line", () => {
    const baseCode = ""
    const code = buildCode(
      baseCode,
      [
        placement(0, 1, 1, 0),
        placement(1, 1, 5, 1),
      ],
      ["a=1", "b=2"],
    )
    expect(code).toBe("a=1 b=2")
  })

  it("allows insert inside leading spaces when user drops there", () => {
    const baseCode = "    "
    const code = buildCode(
      baseCode,
      [placement(0, 1, 2)],
      ["x"],
    )
    expect(code).toBe(" x   ")
  })

  it("pads spaces when user drops beyond the current line length", () => {
    const code = buildCode("", [placement(0, 1, 5)], ["return z"])
    expect(code).toBe("    return z")
  })

  it("keeps fixed code and inserts blocks into the selected gaps", () => {
    const baseCode = "def hello():\n    \n\nhello()"
    const code = buildCode(
      baseCode,
      [placement(0, 2, 5)],
      ['print("hello")'],
    )
    expect(code).toBe('def hello():\n    print("hello")\n\nhello()')
  })

  it("assembles a full Python program from blocks with indentation", () => {
    const code = buildCode(
      "",
      [
        placement(0, 1, 1, 0),
        placement(1, 2, 5, 0),
        placement(2, 3, 5, 0),
        placement(3, 5, 1, 0),
      ],
      ['def hello():', 'print("hello")', "return", "hello()"],
    )
    expect(code).toBe('def hello():\n    print("hello")\n    return\n\nhello()')
  })

  it("replaces a multiline gap without leaving scaffold lines behind", () => {
    const baseCode = "def hello():\n                  \n          \n\nhello()"
    const code = buildCode(
      baseCode,
      [placement(0, 2, 5)],
      ['print("hello")\n    return'],
    )
    expect(code).toBe('def hello():\n    print("hello")\n    return\n\nhello()')
  })
})

describe("applyDrop", () => {
  it("does not shift neighboring placements when moving one block", () => {
    const next = applyDrop(
      [
        placement(0, 1, 1, 0),
        placement(1, 1, 5, 1),
      ],
      ["a=1", "b=2"],
      "",
      0,
      1,
      10,
    )

    const neighbor = next.find((p) => p.blockIndex === 1)
    const moved = next.find((p) => p.blockIndex === 0)

    expect(neighbor).toMatchObject({ line: 1, column: 5, slot: 1 })
    expect(moved).toMatchObject({ line: 1, column: 9 })
  })

  it("snaps drops near an inner scaffold gap to the gap start", () => {
    const target = resolveDropTarget(
      [],
      ["2 + 2"],
      "a =       ",
      1,
      8,
      0,
    )

    expect(target).toMatchObject({ line: 1, column: 5, slot: 0 })
  })

  it("keeps template slot column fixed without tab snapping", () => {
    const next = applyDrop([], ["map"], "        ", 0, 1, 12, 0)

    expect(next).toHaveLength(1)
    expect(next[0]).toMatchObject({
      blockIndex: 0,
      line: 1,
      column: 12,
      templateSlot: 0,
    })
  })
})
