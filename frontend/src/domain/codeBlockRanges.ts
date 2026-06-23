import {
  createBlockNode,
  createCodeNode,
  createDocumentNodeId,
  type DocumentNode,
  mergeAdjacentCodeNodes,
} from "@/domain/codeDocument"
import {
  hasStructuralCodeContent,
  isIgnorableRange,
  lineRangeAtOffset,
  trimRangeEdges,
} from "@/domain/codeInputNormalize"

export interface CodeBlockRange {
  id: string
  start: number
  end: number
}

export function createBlockRangeId(): string {
  return `blk-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function clampRange(
  r: CodeBlockRange,
  codeLength: number,
): CodeBlockRange {
  return {
    ...r,
    start: Math.max(0, Math.min(r.start, codeLength)),
    end: Math.max(0, Math.min(r.end, codeLength)),
  }
}

export function normalizeRanges(
  ranges: CodeBlockRange[],
  code: string,
): CodeBlockRange[] {
  return ranges
    .map((r) => clampRange(r, code.length))
    .filter((r) => r.end > r.start)
    .filter((r) => !isIgnorableRange(code, r.start, r.end))
    .sort((a, b) => a.start - b.start)
}

export function rangesOverlap(
  a: CodeBlockRange,
  b: CodeBlockRange,
): boolean {
  return a.start < b.end && b.start < a.end
}

export function addBlockRange(
  ranges: CodeBlockRange[],
  start: number,
  end: number,
  code: string,
): CodeBlockRange[] {
  const s = Math.max(0, Math.min(start, end))
  const e = Math.max(s, Math.max(start, end))
  if (s === e || isIgnorableRange(code, s, e)) {
    return normalizeRanges(ranges, code)
  }

  const candidate: CodeBlockRange = {
    id: createBlockRangeId(),
    start: s,
    end: e,
  }

  const normalized = normalizeRanges(ranges, code)
  if (normalized.some((r) => rangesOverlap(r, candidate))) {
    return normalized
  }

  return normalizeRanges([...normalized, candidate], code)
}

/** One block for the whole selection (multiline allowed; trims edge line breaks only). */
export function addBlockRangeFromSelection(
  ranges: CodeBlockRange[],
  selStart: number,
  selEnd: number,
  code: string,
): CodeBlockRange[] {
  const { start, end } = resolveBlockConversionSpan(code, ranges, selStart, selEnd)
  return addBlockRange(ranges, start, end, code)
}

export function removeBlockRange(
  ranges: CodeBlockRange[],
  id: string,
): CodeBlockRange[] {
  return ranges.filter((r) => r.id !== id)
}

export function findRangeAtOffset(
  ranges: CodeBlockRange[],
  offset: number,
): CodeBlockRange | null {
  return (
    ranges.find((r) => offset >= r.start && offset < r.end) ?? null
  )
}

export function findRangeForSelection(
  ranges: CodeBlockRange[],
  start: number,
  end: number,
): CodeBlockRange | null {
  const found = findRangesIntersectingSelection(ranges, start, end)
  return found[0] ?? null
}

/** All block ranges touched by the editor selection (or under cursor). */
export function findRangesIntersectingSelection(
  ranges: CodeBlockRange[],
  start: number,
  end: number,
): CodeBlockRange[] {
  const s = Math.min(start, end)
  const e = Math.max(start, end)

  if (s === e) {
    const at = findRangeAtOffset(ranges, s)
    return at ? [at] : []
  }

  return ranges.filter((r) => s < r.end && e > r.start)
}

/** Expand selection to fully cover every touched block range. */
export function expandSelectionToCoveringBlocks(
  ranges: CodeBlockRange[],
  start: number,
  end: number,
  code: string,
): { start: number; end: number } {
  const s = Math.min(start, end)
  const e = Math.max(start, end)
  const touched = findRangesIntersectingSelection(ranges, s, e)
  if (touched.length === 0) {
    return trimRangeEdges(code, s, e)
  }
  return {
    start: Math.min(...touched.map((range) => range.start)),
    end: Math.max(...touched.map((range) => range.end)),
  }
}

/** Resolve the text span used for «Преобразовать в блок». */
export function resolveBlockConversionSpan(
  code: string,
  ranges: CodeBlockRange[],
  selStart: number,
  selEnd: number,
): { start: number; end: number } {
  const s = Math.min(selStart, selEnd)
  const e = Math.max(selStart, selEnd)
  if (s === e) {
    const line = lineRangeAtOffset(code, s)
    return trimRangeEdges(code, line.start, line.end)
  }
  const covering = expandSelectionToCoveringBlocks(ranges, s, e, code)
  return trimRangeEdges(code, covering.start, covering.end)
}

export function removeBlockRanges(
  ranges: CodeBlockRange[],
  ids: string[],
): CodeBlockRange[] {
  if (ids.length === 0) return ranges
  const remove = new Set(ids)
  return ranges.filter((r) => !remove.has(r.id))
}

export interface ModelContentChange {
  rangeOffset: number
  rangeLength: number
  text: string
}

export function applyModelChangesToRanges(
  ranges: CodeBlockRange[],
  changes: ModelContentChange[],
  code: string,
): CodeBlockRange[] {
  let next = [...ranges]
  for (const change of changes) {
    next = applyModelChangeToRanges(next, change)
  }
  return normalizeRanges(next, code)
}

function applyModelChangeToRanges(
  ranges: CodeBlockRange[],
  change: ModelContentChange,
): CodeBlockRange[] {
  const editStart = change.rangeOffset
  const editEnd = change.rangeOffset + change.rangeLength
  const delta = change.text.length - change.rangeLength

  const next: CodeBlockRange[] = []

  for (const range of ranges) {
    if (range.end <= editStart) {
      next.push(range)
      continue
    }
    if (range.start >= editEnd) {
      next.push({
        ...range,
        start: range.start + delta,
        end: range.end + delta,
      })
      continue
    }

    let start = range.start
    let end = range.end + delta

    if (editStart <= range.start && editEnd >= range.end) {
      start = editStart
      end = editStart + change.text.length
    } else if (editStart > range.start && editEnd < range.end) {
      end = range.end + delta
    } else if (editStart <= range.start) {
      start = editStart
    } else if (editEnd >= range.end) {
      end = editEnd + change.text.length
    }

    if (end > start) {
      next.push({ ...range, start, end })
    }
  }

  return next
}

export function documentToRanges(document: DocumentNode[]): {
  code: string
  ranges: CodeBlockRange[]
} {
  let code = ""
  const ranges: CodeBlockRange[] = []

  for (const node of document) {
    const text = node.text ?? ""
    const offset = code.length
    if (node.type === "block" && hasStructuralCodeContent(text)) {
      ranges.push({
        id: node.id || createBlockRangeId(),
        start: offset,
        end: offset + text.length,
      })
    }
    code += text
  }

  return { code, ranges }
}

export function documentFromRanges(
  code: string,
  ranges: CodeBlockRange[],
): DocumentNode[] {
  const sorted = normalizeRanges(ranges, code)
  const document: DocumentNode[] = []
  let pos = 0

  for (const range of sorted) {
    if (pos < range.start) {
      document.push(createCodeNode(code.slice(pos, range.start)))
    }
    const blockText = code.slice(range.start, range.end)
    if (hasStructuralCodeContent(blockText)) {
      document.push({ ...createBlockNode(blockText), id: range.id })
    }
    pos = range.end
  }

  if (pos < code.length) {
    document.push(createCodeNode(code.slice(pos)))
  }

  if (document.length === 0) {
    return [createCodeNode(code)]
  }

  return mergeAdjacentCodeNodes(document)
}

export function rangesToLegacyBlocks(
  code: string,
  ranges: CodeBlockRange[],
): { blocks: string[]; order: number[] } {
  const document = documentFromRanges(code, ranges)
  const blocks: string[] = []
  const order: number[] = []

  for (const node of document) {
    if (node.type !== "block") continue
    const index = blocks.length
    blocks.push(node.text)
    order.push(index)
  }

  return { blocks, order }
}
