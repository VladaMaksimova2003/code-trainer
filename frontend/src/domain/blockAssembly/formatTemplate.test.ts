import { describe, expect, it } from "vitest"
import { formatAssemblyTemplate } from "@/domain/blockAssembly/formatTemplate"
import { isProgramEntryUsed } from "@/features/task-solving/model/conceptUsage"

describe("formatAssemblyTemplate", () => {
  it("breaks minified pascal scaffold while preserving slots", () => {
    const tpl =
      "var a: array[1..5] of {0} = (5, 2, 9, 1, 7);var i, {1}: integer;begin  maximum := a[1];  for i := 1 to 5 do    if a[i] > maximum then maximum := a[i];  {2}(maximum);end."
    const formatted = formatAssemblyTemplate(tpl, "pascal")
    expect(formatted).toContain("{0}")
    expect(formatted).toContain("{1}")
    expect(formatted).toContain("{2}")
    expect(formatted.split("\n").length).toBeGreaterThan(3)
  })

  it("preserves already formatted cpp scaffold with slots", () => {
    const tpl = `#include <iostream>
#include <vector>
int main()
{
    int {0} = 0;
    for(int {1} : loads) total += load;
    std::cout << total / {2};
}`
    const formatted = formatAssemblyTemplate(tpl, "cpp")
    expect(formatted).toContain("int {0} = 0;")
    expect(formatted).toContain("for(int {1} : loads)")
    expect(formatted.split("\n").length).toBeGreaterThan(4)
  })

  it("breaks minified python scaffold while preserving slots", () => {
    const tpl =
      "{0} = [5, 2, 9, 1, 7]{1} = numbers[0]for {2} in numbers:    if value > maximum:        maximum = valueprint(maximum)"
    const formatted = formatAssemblyTemplate(tpl, "python")
    expect(formatted).toContain("{0}")
    expect(formatted).toContain("for {2} in numbers:")
    expect(formatted.split("\n").length).toBeGreaterThan(2)
  })
})

describe("isProgramEntryUsed", () => {
  it("accepts any non-empty python fragment", () => {
    expect(isProgramEntryUsed("numbers = [1, 2]", "python")).toBe(true)
  })

  it("accepts pascal begin without program", () => {
    expect(isProgramEntryUsed("begin\n  writeln(1);\nend.", "pascal")).toBe(true)
  })

  it("accepts cpp main", () => {
    expect(isProgramEntryUsed("int main(){ return 0; }", "cpp")).toBe(true)
  })
})
