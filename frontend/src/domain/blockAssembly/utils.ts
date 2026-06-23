import type { BlockPlacement } from "@/domain/blockAssembly/types"

export const BLOCK_ASSEMBLY_TAB_SIZE = 4

/** Normalizes teacher-stored newlines (`\n`, `` `n ``) for display and assembly. */
export function decodeTemplateText(text = ""): string {
  return String(text || "")
    .replace(/\r\n/g, "\n")
    .replace(/\\n/g, "\n")
    .replace(/`n/g, "\n")
}

export function createPlacementId(): string {
  return `blk-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

/** Length of leading whitespace (spaces/tabs) on a line — Python indent region. */
export function getLineIndentLen(lineText: string): number {
  const match = lineText.match(/^(\s*)/)
  return match?.[1]?.length ?? 0
}

/**
 * 1-based code column preserving user drop position.
 * Only clamps invalid values; does not enforce indentation boundaries.
 */
export function normalizeCodeColumn(lineText: string, column: number): number {
  void lineText
  return Math.max(1, Math.floor(column))
}

/** Snap 1-based columns to editor-like tab stops: 1, 5, 9, 13... */
export function snapColumnToTab(
  column: number,
  tabSize = BLOCK_ASSEMBLY_TAB_SIZE,
): number {
  const safeColumn = Math.max(1, Math.floor(column))
  const safeTabSize = Math.max(1, Math.floor(tabSize))
  return Math.round((safeColumn - 1) / safeTabSize) * safeTabSize + 1
}

export function getBaseLine(baseCode: string, line: number): string {
  const lines = baseCode.split("\n")
  const lineNum = Math.max(1, line)
  while (lines.length < lineNum) {
    lines.push("")
  }
  return lines[lineNum - 1] ?? ""
}

/**
 * Strip scaffold padding from block text for display and assembly.
 * Trims only the outer edges of the block; inner line indentation is kept.
 * Line indent in free assembly is applied separately via editor arrows.
 */
export function trimBlockText(blockText: string): string {
  const raw = String(blockText ?? "")
  if (!raw) return ""
  if (!raw.includes("\n")) return raw.trim()

  const lines = [...raw.split("\n")]
  if (lines.length === 0) return ""

  lines[0] = lines[0].trim()
  if (lines.length > 1) {
    lines[lines.length - 1] = lines[lines.length - 1].trimEnd()
  }

  while (lines.length > 0 && lines[0].trim() === "") lines.shift()
  while (lines.length > 0 && lines[lines.length - 1].trim() === "") lines.pop()

  return lines.join("\n")
}

/** Display: stack separate statements in one chip (`a; b` → `a;\nb`). */
export function formatBlockDisplayText(blockText: string): string {
  const trimmed = trimBlockText(blockText)
  if (!trimmed || trimmed.includes("\n")) return trimmed
  if (/;\s+\S/.test(trimmed)) {
    return trimmed.replace(/;\s+/g, ";\n")
  }
  return trimmed
}

export function blockFirstLineWidth(blockText: string): number {
  const first = trimBlockText(blockText).split("\n")[0] ?? ""
  return Math.max(first.length, 1)
}

export function blockLineSpan(blockText: string): number {
  const trimmed = trimBlockText(blockText)
  if (!trimmed) return 1
  return Math.max(1, trimmed.split("\n").length)
}

export function placementsOnLine(
  placements: BlockPlacement[],
  line: number,
): BlockPlacement[] {
  return placements
    .filter((p) => p.line === line)
    .sort((a, b) => a.slot - b.slot || a.column - b.column)
}

export function padBaseCodeToLine(baseCode: string, line: number): string {
  const lines = baseCode.split("\n")
  while (lines.length < line) {
    lines.push("")
  }
  return lines.join("\n")
}

export function maxPlacementLine(
  placements: BlockPlacement[],
  blocks: string[],
): number {
  let max = 1
  for (const p of placements) {
    const span = blockLineSpan(blocks[p.blockIndex] ?? "")
    max = Math.max(max, p.line + span - 1)
  }
  return max
}
