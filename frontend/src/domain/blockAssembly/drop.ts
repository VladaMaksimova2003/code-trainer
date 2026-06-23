import {
  createPlacementId,
  blockFirstLineWidth,
  getBaseLine,
  normalizeCodeColumn,
  placementsOnLine,
  snapColumnToTab,
} from "@/domain/blockAssembly/utils"
import { normalizePlacements } from "@/domain/blockAssembly/normalize"
import type { BlockPlacement } from "@/domain/blockAssembly/types"

export type DropTarget = {
  line: number
  column: number
  slot: number
}

function snapColumnToCodeGap(lineText: string, column: number): number | null {
  const normalizedColumn = normalizeCodeColumn(lineText, column)
  const gapRegex = /[ \t]{2,}/g
  let match: RegExpExecArray | null
  let best: { anchor: number; distance: number } | null = null

  while ((match = gapRegex.exec(lineText)) != null) {
    const start = match.index + 1
    const end = start + match[0].length

    // Leading indentation is controlled by tab snapping; inner gaps are task slots.
    if (start === 1) continue
    const anchor = /\S/.test(lineText[start - 2] ?? "") ? start + 1 : start

    if (normalizedColumn >= anchor - 6 && normalizedColumn <= end + 6) {
      const distance = Math.abs(normalizedColumn - anchor)
      if (!best || distance < best.distance) {
        best = { anchor, distance }
      }
    }
  }

  return best?.anchor ?? null
}

function snapDropColumn(lineText: string, column: number): number {
  const normalized = normalizeCodeColumn(lineText, column)
  if (!String(lineText ?? "").trim()) {
    return snapColumnToTab(normalized)
  }
  return snapColumnToCodeGap(lineText, column) ??
    snapColumnToTab(normalized)
}

export function resolveDropTarget(
  placements: BlockPlacement[],
  blocks: string[],
  baseCode: string,
  dropLine: number,
  dropColumn: number,
  movingBlockIndex: number,
): DropTarget {
  const line = Math.max(1, dropLine)
  const baseLine = getBaseLine(baseCode, line)
  const column = snapDropColumn(baseLine, dropColumn)

  const peers = normalizePlacements(
    placements.filter((p) => p.blockIndex !== movingBlockIndex),
    baseCode,
  )
  const onLine = placementsOnLine(peers, line)

  if (onLine.length === 0) {
    return { line, column, slot: 0 }
  }

  const movingText = blocks[movingBlockIndex] ?? ""
  if (movingText.includes("\n")) {
    return { line, column, slot: 0 }
  }

  for (let slot = 0; slot < onLine.length; slot += 1) {
    const peer = onLine[slot]
    const startCol = peer.column
    const endCol = startCol + blockFirstLineWidth(blocks[peer.blockIndex] ?? "")
    if (column >= startCol && column < endCol) {
      return { line, column: endCol, slot: slot + 1 }
    }
    if (column < startCol) {
      return { line, column, slot }
    }
  }

  return { line, column, slot: onLine.length }
}

export function addPlacement(
  placements: BlockPlacement[],
  blockIndex: number,
  target: DropTarget,
  baseCode: string,
  existingId?: string,
  templateSlot?: number,
): BlockPlacement[] {
  const without = placements.filter((p) => {
    if (p.blockIndex === blockIndex) return false
    if (
      typeof templateSlot === "number" &&
      typeof p.templateSlot === "number" &&
      p.templateSlot === templateSlot
    ) {
      return false
    }
    return true
  })

  const placement: BlockPlacement = {
    id: existingId ?? createPlacementId(),
    blockIndex,
    line: target.line,
    column: target.column,
    slot: target.slot,
    ...(typeof templateSlot === "number" ? { templateSlot } : {}),
  }

  return normalizePlacements([...without, placement], baseCode)
}

export function removePlacement(
  placements: BlockPlacement[],
  blockIndex: number,
  placementId?: string,
): BlockPlacement[] {
  return normalizePlacements(
    placements.filter((p) => {
      if (placementId) return p.id !== placementId
      return p.blockIndex !== blockIndex
    }),
  )
}

export function removePlacementsByIds(
  placements: BlockPlacement[],
  ids: string[],
): BlockPlacement[] {
  const idSet = new Set(ids)
  return normalizePlacements(placements.filter((p) => !idSet.has(p.id)))
}

export function applyDrop(
  placements: BlockPlacement[],
  blocks: string[],
  baseCode: string,
  blockIndex: number,
  dropLine: number,
  dropColumn: number,
  templateSlot?: number,
): BlockPlacement[] {
  const normalized = normalizePlacements(placements, baseCode)
  const existing = normalized.find((p) => p.blockIndex === blockIndex)

  // Template `{n}` slots are fixed in the scaffold — no column snap or peer shift.
  if (typeof templateSlot === "number") {
    const target: DropTarget = {
      line: Math.max(1, dropLine),
      column: Math.max(1, Math.floor(dropColumn)),
      slot: templateSlot,
    }
    return addPlacement(
      normalized,
      blockIndex,
      target,
      baseCode,
      existing?.id,
      templateSlot,
    )
  }

  const target = resolveDropTarget(
    normalized,
    blocks,
    baseCode,
    dropLine,
    dropColumn,
    blockIndex,
  )
  return addPlacement(
    normalized,
    blockIndex,
    target,
    baseCode,
    existing?.id,
    templateSlot,
  )
}

/** Shift a placed block left/right by tab stops (Python indent). */
export function shiftPlacementColumn(
  placements: BlockPlacement[],
  placementId: string,
  deltaTabs: number,
  baseCode: string,
  tabSize = 4,
): BlockPlacement[] {
  if (!deltaTabs) return normalizePlacements(placements, baseCode)
  const deltaColumns = deltaTabs * Math.max(1, tabSize)
  return normalizePlacements(
    placements.map((p) =>
      p.id === placementId
        ? { ...p, column: Math.max(1, Math.floor(p.column) + deltaColumns) }
        : p,
    ),
    baseCode,
  )
}
