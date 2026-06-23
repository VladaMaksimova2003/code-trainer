/**
 * Structural parsing helpers for code / block editor.
 * Uses trim() for logic only — original text in the editor buffer is unchanged.
 */

/** True when text has non-whitespace content (logical line / block). */
export function hasStructuralCodeContent(text: string): boolean {
  return text.trim().length > 0
}

/** Block range that is empty or whitespace-only — must not become a block entity. */
export function isIgnorableRange(
  code: string,
  start: number,
  end: number,
): boolean {
  if (start >= end) return true
  return !hasStructuralCodeContent(code.slice(start, end))
}

export function rangeContainsNewline(
  code: string,
  start: number,
  end: number,
): boolean {
  if (start >= end) return false
  const slice = code.slice(start, end)
  return /[\n\r]/.test(slice)
}

/** Drop leading/trailing line breaks from a range (keeps code buffer unchanged). */
export function trimRangeEdges(
  code: string,
  start: number,
  end: number,
): { start: number; end: number } {
  let s = Math.min(start, end)
  let e = Math.max(start, end)
  while (s < e && (code[s] === "\n" || code[s] === "\r")) s += 1
  while (e > s && (code[e - 1] === "\n" || code[e - 1] === "\r")) e -= 1
  return { start: s, end: e }
}

/** Full line bounds for an offset (excluding trailing line break). */
export function lineRangeAtOffset(
  code: string,
  offset: number,
): { start: number; end: number } {
  const clamped = Math.max(0, Math.min(offset, code.length))
  const lineStart = code.lastIndexOf("\n", Math.max(0, clamped - 1)) + 1
  let lineEnd = code.indexOf("\n", clamped)
  if (lineEnd === -1) lineEnd = code.length
  if (lineEnd > lineStart && code[lineEnd - 1] === "\r") lineEnd -= 1
  return trimRangeEdges(code, lineStart, lineEnd)
}

function isLineBreakAt(code: string, index: number): boolean {
  return code[index] === "\n" || code[index] === "\r"
}

function lineBreakEndAt(code: string, index: number): number {
  if (code[index] === "\r" && code[index + 1] === "\n") return index + 2
  return index + 1
}

/**
 * Split [start, end) into sub-ranges that never contain \\n or \\r.
 * Newlines stay in code but are not part of any block range.
 */
export function splitRangeByNewlines(
  code: string,
  start: number,
  end: number,
): Array<{ start: number; end: number }> {
  const { start: s, end: e } = trimRangeEdges(code, start, end)
  if (s >= e) return []

  const parts: Array<{ start: number; end: number }> = []
  let partStart = s

  for (let i = s; i < e; ) {
    if (isLineBreakAt(code, i)) {
      if (i > partStart && !isIgnorableRange(code, partStart, i)) {
        parts.push({ start: partStart, end: i })
      }
      partStart = lineBreakEndAt(code, i)
      i = partStart
      continue
    }
    i += 1
  }

  if (partStart < e && !isIgnorableRange(code, partStart, e)) {
    parts.push({ start: partStart, end: e })
  }

  return parts
}

/** Segments to turn into block ranges from editor selection. */
export function segmentsFromSelection(
  code: string,
  selStart: number,
  selEnd: number,
): Array<{ start: number; end: number }> {
  return splitRangeByNewlines(code, selStart, selEnd)
}

/** Compare block texts for catalog / legacy order (indent ignored). */
export function blockTextsEqual(a: string, b: string): boolean {
  return a.trim() === b.trim()
}

/** Find block index ignoring leading/trailing whitespace differences. */
export function indexOfBlockText(blocks: string[], text: string): number {
  return blocks.findIndex((b) => blockTextsEqual(b, text))
}
