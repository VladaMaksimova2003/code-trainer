/** Client-side block assembly (mirrors backend block_reorder_task.build_code). */

export type TemplatePart =
  | { kind: "text"; value: string }
  | { kind: "slot"; slot: number }

export function parseTemplateParts(template: string): TemplatePart[] {
  const parts: TemplatePart[] = []
  const regex = /\{(\d+)\}/g
  let last = 0
  let match = regex.exec(template)
  while (match) {
    if (match.index > last) {
      parts.push({ kind: "text", value: template.slice(last, match.index) })
    }
    parts.push({ kind: "slot", slot: Number(match[1]) })
    last = regex.lastIndex
    match = regex.exec(template)
  }
  if (last < template.length) {
    parts.push({ kind: "text", value: template.slice(last) })
  }
  return parts
}

export function getUniqueSlotIds(template: string | null): number[] {
  if (!template) return []
  const ids: number[] = []
  const matches = template.matchAll(/\{(\d+)\}/g)
  for (const match of matches) {
    ids.push(Number(match[1]))
  }
  return [...new Set(ids)].sort((a, b) => a - b)
}

export function getSlotCount(template: string | null, blockCount: number): number {
  const slotIds = getUniqueSlotIds(template)
  return slotIds.length > 0 ? slotIds.length : blockCount
}

export function createEmptyOrder(template: string | null, blockCount: number): number[] {
  return Array(getSlotCount(template, blockCount)).fill(-1)
}

export function slotIdToPosition(slotId: number, template: string | null): number {
  const ids = getUniqueSlotIds(template)
  const index = ids.indexOf(slotId)
  return index === -1 ? slotId : index
}

export function getTemplateSlotIndent(template: string, slotIndex: number): string {
  const slotToken = `{${slotIndex}}`
  const pos = template.indexOf(slotToken)
  if (pos === -1) return ""
  const lineStart = template.lastIndexOf("\n", 0, pos) + 1
  let indent = ""
  for (const ch of template.slice(lineStart, pos)) {
    if (ch === " " || ch === "\t") indent += ch
    else break
  }
  return indent
}

function applyIndentToBlock(block: string, indent: string): string {
  if (!indent || !block.includes("\n")) return block
  const lines = block.split("\n")
  return lines[0] + ("\n" + indent).join(lines.slice(1))
}

function applyManualIndentLevel(block: string, level: number): string {
  if (level <= 0) return block
  const prefix = " ".repeat(level)
  return block
    .split("\n")
    .map((line) => (line ? prefix + line : line))
    .join("\n")
}

export function buildAssembledCode(
  blocks: string[],
  order: number[],
  template: string | null,
  indents: number[] = [],
): string {
  const selected = order
    .filter((index) => typeof index === "number" && index >= 0)
    .map((index) => blocks[index] ?? "")

  if (!template) {
    if (indents.length > 0) {
      return selected
        .map((block, idx) =>
          applyManualIndentLevel(block, Number(indents[idx] ?? 0)),
        )
        .join("\n")
    }
    return selected.join("\n")
  }

  let result = template
  for (let i = 0; i < order.length; i += 1) {
    const blockIndex = order[i]
    if (blockIndex < 0) continue
    const blockText = blocks[blockIndex] ?? ""
    const slotToken = `{${i}}`
    const indent = getTemplateSlotIndent(result, i)
    const indented = applyIndentToBlock(blockText, indent)
    result = result.replace(slotToken, indented)
  }
  return result
}

export function shuffleBlockIndices(
  blockCount: number,
  seed = "",
): number[] {
  const indices = Array.from({ length: blockCount }, (_, i) => i)
  let hash = 0
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) | 0
  }
  const random = () => {
    hash = (hash * 1664525 + 1013904223) | 0
    return (hash >>> 0) / 4294967296
  }
  for (let i = indices.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1))
    ;[indices[i], indices[j]] = [indices[j], indices[i]]
  }
  return indices
}
