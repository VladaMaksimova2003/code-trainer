import type { CodeBlockRange } from "@/domain/codeBlockRanges"
import { normalizeRanges } from "@/domain/codeBlockRanges"

function lineBoundsAtOffset(code: string, offset: number) {
  const lineStart = code.lastIndexOf("\n", Math.max(0, offset - 1)) + 1
  const lineBreak = code.indexOf("\n", offset)
  const lineEnd = lineBreak === -1 ? code.length : lineBreak
  return { lineStart, lineEnd }
}

function lineIndent(code: string, lineStart: number, lineEnd: number) {
  const lineText = code.slice(lineStart, lineEnd)
  return (lineText.match(/^(\s*)/) ?? ["", ""])[1]
}

/**
 * Teacher template with `{0}`, `{1}` … — keeps Python/JS line indent before placeholders.
 */
export function deriveTemplateWithSlotMarkers(
  referenceCode: string,
  ranges: CodeBlockRange[],
): string {
  const ascending = [...normalizeRanges(ranges, referenceCode)].sort(
    (a, b) => a.start - b.start,
  )
  let result = referenceCode

  for (let blockIndex = ascending.length - 1; blockIndex >= 0; blockIndex -= 1) {
    const range = ascending[blockIndex]
    const { lineStart, lineEnd } = lineBoundsAtOffset(referenceCode, range.start)
    const indent = lineIndent(referenceCode, lineStart, lineEnd)

    let insertStart = range.start
    const insertEnd = range.end

    if (indent.length > 0 && range.start <= lineStart + indent.length) {
      insertStart = lineStart + indent.length
    }

    result =
      result.slice(0, insertStart) +
      `{${blockIndex}}` +
      result.slice(insertEnd)
  }

  return result
}

/**
 * Student scaffold: reference code with block regions replaced by spaces (same width).
 */
export function deriveBaseCodeFromReference(
  referenceCode: string,
  ranges: CodeBlockRange[],
): string {
  const normalized = [...normalizeRanges(ranges, referenceCode)].sort(
    (a, b) => b.start - a.start,
  )
  let result = referenceCode
  for (const range of normalized) {
    const width = Math.max(0, range.end - range.start)
    result =
      result.slice(0, range.start) + " ".repeat(width) + result.slice(range.end)
  }
  return result
}

export function extractBlocksFromRanges(
  referenceCode: string,
  ranges: CodeBlockRange[],
): string[] {
  return normalizeRanges(ranges, referenceCode).map((r) =>
    referenceCode.slice(r.start, r.end),
  )
}
