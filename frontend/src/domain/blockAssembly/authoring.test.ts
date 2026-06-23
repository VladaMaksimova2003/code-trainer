import { describe, expect, it } from "vitest"
import { deriveTemplateWithSlotMarkers } from "./authoring"

const palindrome = `s = input().strip()
normalized = s.lower()
if normalized == normalized[::-1]:
    print('Palindrome')
else:
    print('Not palindrome')`

describe("deriveTemplateWithSlotMarkers", () => {
  it("keeps line indent when selection includes leading spaces", () => {
    const printPal = palindrome.indexOf("    print('Palindrome')")
    const printNot = palindrome.indexOf("    print('Not palindrome')")
    const template = deriveTemplateWithSlotMarkers(palindrome, [
      { start: printPal, end: printPal + "    print('Palindrome')".length },
      { start: printNot, end: printNot + "    print('Not palindrome')".length },
    ])

    expect(template).toContain("    {0}")
    expect(template).toContain("    {1}")
    expect(template).not.toMatch(/^    print/m)
  })

  it("keeps line indent when selection omits leading spaces", () => {
    const printPal = palindrome.indexOf("print('Palindrome')")
    const template = deriveTemplateWithSlotMarkers(palindrome, [
      {
        start: printPal,
        end: printPal + "print('Palindrome')".length,
      },
    ])

    expect(template).toContain("    {0}")
  })
})
