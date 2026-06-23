import { createPlacementId, blockFirstLineWidth } from "@/domain/blockAssembly/utils"
import { normalizePlacements } from "@/domain/blockAssembly/normalize"

const TAB_SIZE = 4

export function linesFromPlacements(placements, baseCode) {
  const normalized = normalizePlacements(placements, baseCode)
  if (normalized.length === 0) {
    return [{ id: "1", indent: 0, blockIndices: [] }]
  }

  const maxLine = Math.max(...normalized.map((p) => p.line))
  const lines = []

  for (let lineNum = 1; lineNum <= maxLine; lineNum += 1) {
    const onLine = normalized
      .filter((p) => p.line === lineNum)
      .sort((a, b) => a.slot - b.slot || a.column - b.column)
    const indent =
      onLine.length > 0 ? Math.max(0, Math.floor((onLine[0].column - 1) / TAB_SIZE)) : 0
    lines.push({
      id: String(lineNum),
      indent,
      blockIndices: onLine.map((p) => p.blockIndex),
    })
  }

  const last = lines[lines.length - 1]
  if (!last || last.blockIndices.length > 0) {
    lines.push({ id: String(maxLine + 1), indent: 0, blockIndices: [] })
  }

  return lines
}

export function placementsFromLines(lines, blocks) {
  const placements = []

  lines.forEach((line, index) => {
    const lineNum = index + 1
    let column = 1 + line.indent * TAB_SIZE

    line.blockIndices.forEach((blockIndex, slot) => {
      placements.push({
        id: createPlacementId(),
        blockIndex,
        line: lineNum,
        column,
        slot,
      })
      const text = blocks[blockIndex] ?? ""
      column += blockFirstLineWidth(text) + 1
    })
  })

  return normalizePlacements(placements, "")
}
