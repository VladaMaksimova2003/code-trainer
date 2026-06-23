export const DEFAULT_EDITOR_LINE_HEIGHT = 27

function lineFromRelativeY(relY: number, lineHeight: number): number {
  if (!Number.isFinite(relY) || lineHeight <= 0) return 1
  return Math.max(1, Math.floor(relY / lineHeight) + 1)
}

function finiteMaxLine(...candidates: number[]): number {
  let best = 1
  for (const value of candidates) {
    if (Number.isFinite(value) && value >= 1) {
      best = Math.max(best, Math.floor(value))
    }
  }
  return best
}

export type DropPositionResult = {
  lineNumber: number
  column: number
}

/**
 * Resolve drop line (Y) and column (X) from pointer in Monaco editor.
 */
export function resolveDropPosition(
  editor: {
    getModel(): { getLineCount(): number; getLineMaxColumn(line: number): number } | null
    getDomNode(): HTMLElement | null
    getLayoutInfo(): { contentLeft?: number; contentTop?: number }
    getScrollLeft?(): number
    getScrollTop(): number
    getOption(option: unknown): unknown
    getScrolledVisiblePosition?(pos: {
      lineNumber: number
      column: number
    }): { lineNumber: number; column: number } | null
    getTargetAtClientPoint?(
      x: number,
      y: number,
    ): { position?: { lineNumber: number; column: number } } | null
  },
  monaco: { editor: { EditorOption: { fontInfo: unknown; lineHeight: unknown } } },
  clientX: number,
  clientY: number,
): DropPositionResult {
  const model = editor.getModel()
  const fromTarget = editor.getTargetAtClientPoint?.(clientX, clientY)?.position
  const targetLine = Math.max(1, fromTarget?.lineNumber ?? 1)
  const targetColumn = Math.max(1, fromTarget?.column ?? 1)

  if (!model) {
    return { lineNumber: targetLine, column: targetColumn }
  }

  const domNode = editor.getDomNode()
  if (!domNode) {
    return { lineNumber: targetLine, column: targetColumn }
  }

  const rect = domNode.getBoundingClientRect()
  const layout = editor.getLayoutInfo()
  const contentTop = Number(layout?.contentTop)
  const safeContentTop = Number.isFinite(contentTop) ? contentTop : 0
  const contentLeft = Number(layout?.contentLeft)
  const safeContentLeft = Number.isFinite(contentLeft) ? contentLeft : 0

  const rawLineHeight = editor.getOption(monaco.editor.EditorOption.lineHeight)
  const lineHeight =
    typeof rawLineHeight === "number" &&
    Number.isFinite(rawLineHeight) &&
    rawLineHeight > 0
      ? rawLineHeight
      : DEFAULT_EDITOR_LINE_HEIGHT

  const scrollTop = Number(editor.getScrollTop())
  const safeScrollTop = Number.isFinite(scrollTop) ? scrollTop : 0
  const scrollLeft = Number(editor.getScrollLeft?.() ?? 0)
  const safeScrollLeft = Number.isFinite(scrollLeft) ? scrollLeft : 0

  const relYContent = clientY - rect.top - safeContentTop + safeScrollTop
  const relYViewport = clientY - rect.top
  const lineFromY = finiteMaxLine(
    lineFromRelativeY(relYContent, lineHeight),
    lineFromRelativeY(relYViewport, lineHeight),
  )

  const lineNumber = fromTarget?.lineNumber
    ? targetLine
    : finiteMaxLine(lineFromY)
  const rawFontInfo = editor.getOption(monaco.editor.EditorOption.fontInfo)
  const fontInfo =
    rawFontInfo && typeof rawFontInfo === "object"
      ? (rawFontInfo as {
          typicalFullwidthCharacterWidth?: number
          typicalHalfwidthCharacterWidth?: number
        })
      : null
  const charWidth =
    fontInfo?.typicalHalfwidthCharacterWidth ??
    fontInfo?.typicalFullwidthCharacterWidth ??
    7.87
  const relXContent = clientX - rect.left - safeContentLeft + safeScrollLeft
  const columnFromX =
    Number.isFinite(relXContent) && Number.isFinite(charWidth) && charWidth > 0
      ? Math.max(1, Math.floor(relXContent / charWidth) + 1)
      : targetColumn
  const column = Number.isFinite(columnFromX) ? columnFromX : targetColumn

  return { lineNumber, column }
}
