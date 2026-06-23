import { normalizePlacements } from "@/domain/blockAssembly/normalize"
import {
  slotGapWidthsFromTemplate,
  templateScaffoldIsWhitespaceOnly,
} from "@/domain/blockAssembly/blockScaffold"
import {
  blockLineSpan,
  decodeTemplateText,
  normalizeCodeColumn,
  trimBlockText,
} from "@/domain/blockAssembly/utils"
import type { BlockPlacement } from "@/domain/blockAssembly/types"

type OccupiedRange = { start: number; end: number }

function resolveInsertIndex(
  lineText: string,
  column: number,
  occupied: OccupiedRange[],
): number {
  const codeColumn = normalizeCodeColumn(lineText, column)
  let index = Math.max(0, codeColumn - 1)

  for (const range of occupied) {
    if (index >= range.start && index < range.end) {
      index = range.end
    }
  }

  return Math.max(0, index)
}

function resolveReplacementEnd(
  lineText: string,
  insertAt: number,
  insertedText: string,
): number {
  const prefix = lineText.slice(0, insertAt)
  const isCodeGap = /\S/.test(prefix) || insertAt % 4 === 0
  if (!isCodeGap) {
    return insertAt
  }

  let end = insertAt
  const maxReplace = insertedText.length

  while (
    end < lineText.length &&
    end - insertAt < maxReplace &&
    /\s/.test(lineText[end] ?? "")
  ) {
    end += 1
  }

  return end
}

function assembleLine(
  baseLine: string,
  row: BlockPlacement[],
  blocks: string[],
): { lines: string[]; consumedBaseLines: number } {
  const sorted = [...row].sort((a, b) => a.slot - b.slot || a.column - b.column)
  let lineText = baseLine
  const occupied: OccupiedRange[] = []
  const trailingLines: string[] = []
  let consumedBaseLines = 1

  for (const placement of sorted) {
    const blockText = trimBlockText(blocks[placement.blockIndex] ?? "")
    const parts = blockText.split("\n")
    consumedBaseLines = Math.max(consumedBaseLines, parts.length)
    const firstLine = parts[0] ?? ""
    const insertAt = resolveInsertIndex(lineText, placement.column, occupied)
    const safeInsertAt = insertAt
    if (safeInsertAt > lineText.length) {
      lineText = lineText.padEnd(safeInsertAt, " ")
    }
    const replaceEnd = resolveReplacementEnd(lineText, safeInsertAt, firstLine)

    lineText =
      lineText.slice(0, safeInsertAt) +
      firstLine +
      lineText.slice(replaceEnd)
    occupied.push({
      start: safeInsertAt,
      end: safeInsertAt + firstLine.length,
    })
    occupied.sort((a, b) => a.start - b.start)

    if (parts.length > 1) {
      trailingLines.push(...parts.slice(1))
    }
  }

  return { lines: [lineText, ...trailingLines], consumedBaseLines }
}

/**
 * Assemble final code from immutable baseCode and line-based placements.
 */
export function buildCode(
  baseCode: string,
  placements: BlockPlacement[],
  blocks: string[],
): string {
  const normalized = normalizePlacements(placements, baseCode)
  if (normalized.length === 0) {
    return baseCode
  }

  let maxLine = Math.max(1, baseCode.split("\n").length)
  for (const p of normalized) {
    maxLine = Math.max(maxLine, p.line + blockLineSpan(blocks[p.blockIndex] ?? "") - 1)
  }

  const baseLines = baseCode.split("\n")
  while (baseLines.length < maxLine) {
    baseLines.push("")
  }

  const byLine = new Map<number, BlockPlacement[]>()
  for (const p of normalized) {
    const list = byLine.get(p.line) ?? []
    list.push(p)
    byLine.set(p.line, list)
  }

  const output: string[] = []
  for (let lineNum = 1; lineNum <= maxLine; lineNum += 1) {
    const baseLine = baseLines[lineNum - 1] ?? ""
    const row = byLine.get(lineNum)
    if (!row || row.length === 0) {
      output.push(baseLine)
      continue
    }
    const assembled = assembleLine(baseLine, row, blocks)
    output.push(...assembled.lines)
    lineNum += assembled.consumedBaseLines - 1
  }

  return output.join("\n")
}

/** Replace `{0}`…`{n}` markers using templateSlot placements (matches backend build_code). */
export function assembleSlotTemplate(
  template: string,
  blocks: string[],
  placements: BlockPlacement[],
): string {
  const text = String(template ?? "")
  if (!/\{\d+\}/.test(text)) return ""

  const slotPlacements = normalizePlacements(placements, text)
    .filter((p) => typeof p.templateSlot === "number")
    .sort((a, b) => (a.templateSlot as number) - (b.templateSlot as number))

  if (slotPlacements.length === 0) return ""

  let result = text
  for (const placement of slotPlacements) {
    const slot = placement.templateSlot as number
    const token = `{${slot}}`
    const blockText = trimBlockText(blocks[placement.blockIndex] ?? "")
    if (!blockText || !result.includes(token)) continue
    result = result.replace(token, blockText)
  }
  return result
}

/** Legacy API bridge — prefer buildCode + assembled_code submit. */
export function deriveSubmitPayload(
  placements: BlockPlacement[],
  baseCode: string,
): {
  order: number[]
  indents: number[]
} {
  const sorted = normalizePlacements(placements, baseCode)
  const ordered = [...sorted].sort((a, b) => {
    const aSlot = a.templateSlot
    const bSlot = b.templateSlot
    if (typeof aSlot === "number" && typeof bSlot === "number" && aSlot !== bSlot) {
      return aSlot - bSlot
    }
    return a.line - b.line || a.slot - b.slot || a.column - b.column
  })
  const order = ordered.map((p) => p.blockIndex)
  const indents = ordered.map((p, index, arr) => {
    const prev = arr[index - 1]
    const isFirstOnLine = !prev || prev.line !== p.line
    if (!isFirstOnLine) return 0
    return Math.max(0, p.column - 1)
  })
  return { order, indents }
}

const DEFAULT_SLOT_GAP_WIDTH = 8

export function getInitialBaseCode(
  template: string | null | undefined,
  blocks: string[] = [],
): string {
  if (template == null) return ""
  const text = decodeTemplateText(template)
  if (!text.trim()) return ""
  if (!/\{\d+\}/.test(text)) return ""

  const whitespaceScaffold = templateScaffoldIsWhitespaceOnly(text)
  const slotWidths = whitespaceScaffold ? slotGapWidthsFromTemplate(text, blocks) : []

  return text.replace(/\{(\d+)\}/g, (match, rawIndex, offset) => {
    const slot = Number(rawIndex)
    const block = blocks[slot] ?? ""
    const width = whitespaceScaffold
      ? Math.max(slotWidths[slot] ?? 1, blockGapWidth(block), match.length)
      : Math.max(
          DEFAULT_SLOT_GAP_WIDTH,
          blockGapWidth(block),
          match.length,
        )
    const lineStart = text.lastIndexOf("\n", Math.max(0, offset - 1)) + 1
    const lineEnd = text.indexOf("\n", offset)
    const line = text.slice(lineStart, lineEnd === -1 ? text.length : lineEnd)
    const withoutSlot = line.replace(match, "").trim()
    if (!withoutSlot) {
      return " ".repeat(width)
    }

    return " ".repeat(width)
  })
}

function blockGapWidth(blockText: string): number {
  const firstLine = String(blockText ?? "").split("\n")[0] ?? ""
  return Math.max(1, firstLine.length)
}
