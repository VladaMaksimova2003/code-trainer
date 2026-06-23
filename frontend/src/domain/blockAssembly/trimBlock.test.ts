import { describe, expect, it } from "vitest"
import { blockFirstLineWidth, formatBlockDisplayText, trimBlockText } from "@/domain/blockAssembly/utils"

describe("trimBlockText", () => {
  it("trims padding spaces around single-line blocks", () => {
    expect(trimBlockText("    for i := 1 to n do    ")).toBe("for i := 1 to n do")
  })

  it("trims outer padding on multiline blocks", () => {
    expect(trimBlockText("  begin  \n    readln(n);  \n  end;  ")).toBe(
      "begin\n    readln(n);  \n  end;",
    )
  })

  it("blockFirstLineWidth ignores padding", () => {
    expect(blockFirstLineWidth("      count := 0;     ")).toBe("count := 0;".length)
  })
})

describe("formatBlockDisplayText", () => {
  it("stacks statements separated by semicolon in one chip", () => {
    expect(formatBlockDisplayText("std::cin >> n; std::cin >> target")).toBe(
      "std::cin >> n;\nstd::cin >> target",
    )
  })

  it("leaves single-line blocks unchanged", () => {
    expect(formatBlockDisplayText("readln(n, target)")).toBe("readln(n, target)")
  })
})
