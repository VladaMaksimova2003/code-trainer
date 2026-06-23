import type { CodeBlockRange } from "@/domain/codeBlockRanges"
import { normalizeRanges } from "@/domain/codeBlockRanges"
import { hasStructuralCodeContent } from "@/domain/codeInputNormalize"

/** True when text is empty or whitespace-only (spaces, tabs, newlines). */
export function isWhitespaceOnlyText(text: string): boolean {
  if (!text) return true
  return !hasStructuralCodeContent(text)
}

/** Every non-block region in code is whitespace-only — only spaces may sit outside blocks. */
export function isFullyBlockedExceptWhitespace(
  code: string,
  ranges: CodeBlockRange[],
): boolean {
  const normalized = normalizeRanges(ranges, code)
  if (normalized.length === 0) return false

  let pos = 0
  for (const range of normalized) {
    if (pos < range.start && hasStructuralCodeContent(code.slice(pos, range.start))) {
      return false
    }
    pos = Math.max(pos, range.end)
  }
  return !hasStructuralCodeContent(code.slice(pos))
}

/** Template fixed scaffold (text except `{n}` markers) is whitespace-only. */
export function templateScaffoldIsWhitespaceOnly(template: string): boolean {
  const withoutSlots = String(template ?? "").replace(/\{\d+\}/g, "")
  return isWhitespaceOnlyText(withoutSlots)
}

/** Gaps between `{n}` markers in template — used to size student scaffold gaps. */
export function slotGapWidthsFromTemplate(template: string, blocks: string[] = []): number[] {
  const text = String(template ?? "")
  const widths: number[] = []
  const re = /\{(\d+)\}/g
  let match: RegExpExecArray | null
  let prevEnd = 0

  while ((match = re.exec(text)) !== null) {
    const slot = Number(match[1])
    const between = text.slice(prevEnd, match.index)
    if (prevEnd > 0 || match.index > 0) {
      widths[slot] = Math.max(widths[slot] ?? 0, between.length)
    }
    prevEnd = match.index + match[0].length
  }

  for (let i = 0; i < blocks.length; i += 1) {
    const blockWidth = Math.max(1, String(blocks[i] ?? "").split("\n")[0]?.length ?? 0)
    widths[i] = Math.max(widths[i] ?? 0, blockWidth, 1)
  }

  return widths
}

export function collectScaffoldGapRanges(
  code: string,
  ranges: CodeBlockRange[],
): Array<{ start: number; end: number }> {
  const normalized = normalizeRanges(ranges, code)
  const gaps: Array<{ start: number; end: number }> = []
  let pos = 0

  for (const range of normalized) {
    if (pos < range.start) {
      const start = pos
      const end = range.start
      if (hasStructuralCodeContent(code.slice(start, end))) {
        gaps.push({ start, end })
      }
    }
    pos = Math.max(pos, range.end)
  }

  if (pos < code.length && hasStructuralCodeContent(code.slice(pos))) {
    gaps.push({ start: pos, end: code.length })
  }

  return gaps
}
