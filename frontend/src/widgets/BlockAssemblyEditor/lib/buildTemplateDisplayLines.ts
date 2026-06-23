import { normalizePlacements } from "@/domain/blockAssembly/normalize"

function gapDropColumn(lineText, gapStart0) {
  const before = lineText[gapStart0 - 1] ?? ""
  return /\S/.test(before) ? gapStart0 + 2 : gapStart0 + 1
}

function blockGapWidth(blockText) {
  const firstLine = String(blockText ?? "").split("\n")[0] ?? ""
  return Math.max(1, firstLine.length)
}

function leadingIndentFromBlock(blockText) {
  const firstLine = String(blockText ?? "").split("\n")[0] ?? ""
  return (firstLine.match(/^(\s*)/) ?? ["", ""])[1]
}

function parseMarkerLine(templateLine, baseLine, placements, lineNum, blocks) {
  const indentMatch = templateLine.match(/^(\s*)/)
  let indentStr = indentMatch?.[1] ?? ""
  const content = templateLine.slice(indentStr.length)
  const tokens = []
  const re = /\{(\d+)\}/g
  let lastIndex = 0
  let match

  while ((match = re.exec(content)) !== null) {
    if (match.index > lastIndex) {
      tokens.push({ kind: "fixed", text: content.slice(lastIndex, match.index) })
    }

    const templateSlot = Number(match[1])
    if (!indentStr) {
      indentStr = leadingIndentFromBlock(blocks[templateSlot])
    }

    const baseLeading = baseLine.match(/^(\s*)/)?.[1]?.length ?? 0
    const gapStart =
      baseLine.length > 0
        ? baseLeading + match.index
        : indentStr.length + match.index

    const slotOnlyLine = /^\s*\{\d+\}\s*$/.test(templateLine)
    const defaultDropColumn = slotOnlyLine
      ? 1
      : gapDropColumn(baseLine || indentStr + "        ", gapStart)

    const placement =
      placements.find((p) => p.templateSlot === templateSlot) ??
      placements.find(
        (p) =>
          p.line === lineNum &&
          Math.abs((p.column ?? 0) - defaultDropColumn) <= 2,
      ) ??
      null

    tokens.push({
      kind: "slot",
      templateSlot,
      dropColumn: defaultDropColumn,
      placement,
    })
    lastIndex = match.index + match[0].length
  }

  if (lastIndex < content.length) {
    tokens.push({ kind: "fixed", text: content.slice(lastIndex) })
  }

  return { indentStr, tokens }
}

function parseFixedLine(line) {
  const indentMatch = line.match(/^(\s*)/)
  const indentStr = indentMatch?.[1] ?? ""
  const content = line.slice(indentStr.length)
  if (!content) {
    return { indentStr, tokens: [] }
  }
  return { indentStr, tokens: [{ kind: "fixed", text: content }] }
}

/** Legacy scaffold: one gap per block, in file order, sized to block width. */
function findOrderedBlockGaps(baseCode, blocks) {
  const gaps = []
  let searchFrom = 0

  for (let blockIndex = 0; blockIndex < blocks.length; blockIndex += 1) {
    const width = blockGapWidth(blocks[blockIndex])
    const slice = baseCode.slice(searchFrom)
    const match = slice.match(new RegExp(`[ \\t]{${width},}`))
    if (!match || match.index == null) break

    const absoluteStart = searchFrom + match.index
    const before = baseCode.slice(0, absoluteStart)
    const lineNum = before.split("\n").length
    const lineStart = before.lastIndexOf("\n") + 1
    const localStart = absoluteStart - lineStart

    gaps.push({
      blockIndex,
      lineNum,
      gapStart: localStart,
      width: match[0].length,
    })
    searchFrom = absoluteStart + match[0].length
  }

  return gaps
}

function buildFromMarkers(templateText, baseLines, placements, blocks) {
  const templateLines = templateText.split("\n")
  const lineCount = Math.max(templateLines.length, baseLines.length)
  const result = []

  for (let index = 0; index < lineCount; index += 1) {
    const lineNum = index + 1
    const templateLine = templateLines[index] ?? ""
    const baseLine = baseLines[index] ?? ""

    const parsed = /\{\d+\}/.test(templateLine)
      ? parseMarkerLine(templateLine, baseLine, placements, lineNum, blocks)
      : parseFixedLine(templateLine || baseLine)

    result.push({
      lineNum,
      indentStr: parsed.indentStr,
      tokens: parsed.tokens,
    })
  }

  return result
}

function injectLegacySlotsIntoLine(lineNum, baseLine, gapsOnLine, placements) {
  if (gapsOnLine.length === 0) {
    return parseFixedLine(baseLine)
  }

  const tokens = []
  let pos = 0
  const sorted = [...gapsOnLine].sort((a, b) => a.gapStart - b.gapStart)

  for (const gap of sorted) {
    const localStart = Math.max(0, gap.gapStart)
    if (localStart > pos) {
      tokens.push({ kind: "fixed", text: baseLine.slice(pos, localStart) })
    }

    const placement =
      placements.find(
        (p) => p.blockIndex === gap.blockIndex && p.line === lineNum,
      ) ??
      placements.find((p) => p.blockIndex === gap.blockIndex) ??
      null

    tokens.push({
      kind: "slot",
      templateSlot: gap.blockIndex,
      dropColumn: gapDropColumn(baseLine, localStart),
      placement,
    })
    pos = localStart + gap.width
  }

  if (pos < baseLine.length) {
    tokens.push({ kind: "fixed", text: baseLine.slice(pos) })
  }

  const indentMatch = baseLine.match(/^(\s*)/)
  return { indentStr: indentMatch?.[1] ?? "", tokens }
}

function buildLegacyScaffold(baseCode, placements, blocks) {
  const baseLines = baseCode.split("\n")
  const gaps = findOrderedBlockGaps(baseCode, blocks)
  const gapsByLine = new Map()

  for (const gap of gaps) {
    const list = gapsByLine.get(gap.lineNum) ?? []
    list.push(gap)
    gapsByLine.set(gap.lineNum, list)
  }

  return baseLines.map((baseLine, index) => {
    const lineNum = index + 1
    const gapsOnLine = gapsByLine.get(lineNum) ?? []
    const parsed =
      gapsOnLine.length > 0
        ? injectLegacySlotsIntoLine(lineNum, baseLine, gapsOnLine, placements)
        : parseFixedLine(baseLine)
    return { lineNum, indentStr: parsed.indentStr, tokens: parsed.tokens }
  })
}

/**
 * Display lines for template assembly: exactly one slot per `{n}` placeholder.
 * @returns {{ lineNum: number, indentStr: string, tokens: Array }[]}
 */
export function buildTemplateDisplayLines(
  baseCode,
  rawTemplate,
  placements,
  blocks = [],
) {
  const baseLines = String(baseCode ?? "").split("\n")
  const templateText = String(rawTemplate ?? "")
  const normalized = normalizePlacements(placements, baseCode)

  if (/\{\d+\}/.test(templateText)) {
    return buildFromMarkers(templateText, baseLines, normalized, blocks)
  }

  if (blocks.length > 0 && baseCode.trim()) {
    return buildLegacyScaffold(baseCode, normalized, blocks)
  }

  return baseLines.map((baseLine, index) => {
    const parsed = parseFixedLine(baseLine)
    return { lineNum: index + 1, indentStr: parsed.indentStr, tokens: parsed.tokens }
  })
}

export function slotCountFromDisplayLines(displayLines) {
  return displayLines.reduce(
    (sum, line) => sum + line.tokens.filter((token) => token.kind === "slot").length,
    0,
  )
}

export function getSlotDropTarget(displayLines, lineNum, slotIndexOnLine) {
  const line = displayLines.find((row) => row.lineNum === lineNum)
  if (!line) return null
  const slots = line.tokens.filter((token) => token.kind === "slot")
  const slot = slots[slotIndexOnLine]
  if (!slot?.dropColumn) return null
  return { line: lineNum, column: slot.dropColumn }
}
