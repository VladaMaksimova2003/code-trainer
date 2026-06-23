import { describe, expect, it } from "vitest"
import {
  buildTcConceptsSubtitle,
  formatRussianConstructionCount,
} from "@/admin-panel/config/tcConceptsMeta"

describe("tcConceptsMeta", () => {
  it("formats 29 constructions", () => {
    expect(formatRussianConstructionCount(29)).toBe("29 конструкций")
    expect(buildTcConceptsSubtitle(29)).toBe("29 конструкций · примеры на 5 языках")
  })

  it("handles singular and paucal forms", () => {
    expect(formatRussianConstructionCount(1)).toBe("1 конструкция")
    expect(formatRussianConstructionCount(3)).toBe("3 конструкции")
    expect(formatRussianConstructionCount(11)).toBe("11 конструкций")
  })
})
