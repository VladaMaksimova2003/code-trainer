import type { CodeBlockRange } from "@/domain/codeBlockRanges"

export function inferBlockRangesFromAuthorPayload(
  author: Record<string, unknown>,
): CodeBlockRange[] {
  const code = String(author.original_code ?? "")
  const blocks = Array.isArray(author.blocks) ? author.blocks.map(String) : []
  const order = Array.isArray(author.correct_order)
    ? author.correct_order.map(Number)
    : blocks.map((_, index) => index)
  const ranges: CodeBlockRange[] = []
  let cursor = 0

  order.forEach((blockIndex, sequenceIndex) => {
    const block = blocks[blockIndex]
    if (!block) return

    let start = code.indexOf(block, cursor)
    let end = start >= 0 ? start + block.length : -1

    if (start < 0) {
      const trimmed = block.trim()
      const trimmedStart = trimmed ? code.indexOf(trimmed, cursor) : -1
      if (trimmedStart >= 0) {
        start = trimmedStart
        end = trimmedStart + trimmed.length
      }
    }

    if (start < 0 || end <= start) return
    ranges.push({
      id: `loaded-block-${sequenceIndex}-${start}`,
      start,
      end,
    })
    cursor = end
  })

  return ranges
}
