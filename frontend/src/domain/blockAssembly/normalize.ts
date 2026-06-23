import { createPlacementId, getBaseLine, normalizeCodeColumn } from "@/domain/blockAssembly/utils"
import type { BlockPlacement } from "@/domain/blockAssembly/types"
import { blockTextsEqual } from "@/domain/codeInputNormalize"

function normalizeAssemblyText(code: string): string {
  return String(code ?? "")
    .trim()
    .replace(/\r\n/g, "\n")
    .replace(/\s+/g, " ")
}

function slotPlacementsFromCorrectOrder(
  correctOrder: number[],
  template: string,
): BlockPlacement[] {
  return requiredTemplateSlotIds(template).map((templateSlot) => ({
    id: `expected-${templateSlot}`,
    blockIndex: correctOrder[templateSlot] ?? templateSlot,
    line: 1,
    column: 1,
    slot: 0,
    templateSlot,
  }))
}

function replaceTemplateSlots(
  template: string,
  blocks: string[],
  slotToBlockIndex: Map<number, number>,
): string {
  let result = String(template ?? "")
  for (const slot of requiredTemplateSlotIds(template)) {
    const blockIndex = slotToBlockIndex.get(slot)
    if (blockIndex === undefined) continue
    const token = `{${slot}}`
    const blockText = blocks[blockIndex] ?? ""
    if (!blockText || !result.includes(token)) continue
    result = result.replace(token, blockText)
  }
  return result
}

export function normalizePlacements(
  placements: BlockPlacement[],
  baseCode = "",
): BlockPlacement[] {
  return placements
    .filter((p) => p && typeof p.blockIndex === "number" && p.blockIndex >= 0)
    .map((p) => {
      const line = Math.max(1, Math.floor(p.line))
      const baseLine = baseCode ? getBaseLine(baseCode, line) : ""
      const column = baseCode
        ? normalizeCodeColumn(baseLine, p.column)
        : Math.max(1, Math.floor(p.column))
      return {
        id: p.id || createPlacementId(),
        blockIndex: p.blockIndex,
        line,
        column,
        slot: Math.max(0, Math.floor(p.slot)),
        ...(typeof p.templateSlot === "number" && p.templateSlot >= 0
          ? { templateSlot: p.templateSlot }
          : {}),
      }
    })
    .sort((a, b) => a.line - b.line || a.slot - b.slot || a.column - b.column)
}

export function requiredTemplateSlotIds(template: string): number[] {
  const slots = new Set<number>()
  for (const match of String(template ?? "").matchAll(/\{(\d+)\}/g)) {
    slots.add(Number(match[1]))
  }
  return [...slots].sort((a, b) => a - b)
}

export function countFilledTemplateSlots(placements: BlockPlacement[]): number {
  return new Set(
    normalizePlacements(placements)
      .filter((p) => typeof p.templateSlot === "number")
      .map((p) => p.templateSlot as number),
  ).size
}

export function isTemplateAssemblyComplete(
  placements: BlockPlacement[],
  template: string,
): boolean {
  const required = requiredTemplateSlotIds(template)
  if (required.length === 0) return false
  const normalized = normalizePlacements(placements)
  const filled = new Set(
    normalized
      .filter((p) => typeof p.templateSlot === "number")
      .map((p) => p.templateSlot as number),
  )
  return required.every((slot) => filled.has(slot))
}

export function assemblyCompletionStats(
  placements: BlockPlacement[],
  blockCount: number,
  template?: string | null,
): { filled: number; required: number } {
  if (template && /\{\d+\}/.test(template)) {
    const required = requiredTemplateSlotIds(template)
    return {
      filled: countFilledTemplateSlots(placements),
      required: required.length,
    }
  }
  const used = new Set(normalizePlacements(placements).map((p) => p.blockIndex))
  return { filled: used.size, required: blockCount }
}

export function isAssemblyComplete(
  placements: BlockPlacement[],
  blockCount: number,
  template?: string | null,
): boolean {
  if (template && /\{\d+\}/.test(template)) {
    return isTemplateAssemblyComplete(placements, template)
  }
  if (blockCount <= 0) return false
  const used = new Set(
    normalizePlacements(placements).map((p) => p.blockIndex),
  )
  return used.size === blockCount
}

export const BLOCK_ORDER_ERROR_MESSAGE =
  "Неверный порядок или неверные блоки. Проверьте, что в каждом пропуске стоит нужный фрагмент."

/** True when every template slot contains the expected block label (duplicate-safe). */
export function isSlotAssemblyOrderCorrect(
  placements: BlockPlacement[],
  blocks: string[],
  correctOrder: number[] | undefined,
  template: string,
): boolean {
  if (!template || !/\{\d+\}/.test(template)) return true
  if (!Array.isArray(correctOrder) || correctOrder.length === 0) return true

  const slotIds = requiredTemplateSlotIds(template)
  if (slotIds.length === 0) return true

  const normalized = normalizePlacements(placements)
  const bySlot = new Map<number, number>()
  for (const placement of normalized) {
    if (typeof placement.templateSlot === "number" && placement.templateSlot >= 0) {
      bySlot.set(placement.templateSlot, placement.blockIndex)
    }
  }

  if (bySlot.size >= slotIds.length && slotIds.every((slot) => bySlot.has(slot))) {
    const expectedCode = normalizeAssemblyText(
      replaceTemplateSlots(
        template,
        blocks,
        new Map(
          slotPlacementsFromCorrectOrder(correctOrder, template).map((placement) => [
            placement.templateSlot as number,
            placement.blockIndex,
          ]),
        ),
      ),
    )
    const actualCode = normalizeAssemblyText(
      replaceTemplateSlots(template, blocks, bySlot),
    )
    if (expectedCode && actualCode && expectedCode === actualCode) {
      return true
    }
  }

  for (const slot of slotIds) {
    if (slot >= correctOrder.length) return false
    const placedIndex = bySlot.get(slot)
    if (placedIndex === undefined) return false
    const expectedIndex = correctOrder[slot]
    if (!blockTextsEqual(blocks[placedIndex] ?? "", blocks[expectedIndex] ?? "")) {
      return false
    }
  }

  return true
}
