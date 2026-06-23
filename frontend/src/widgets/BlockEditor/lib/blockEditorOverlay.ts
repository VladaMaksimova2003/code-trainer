import {
  BLOCK_ASSEMBLY_TAB_SIZE,
  blockFirstLineWidth,
  normalizeCodeColumn,
} from "@/domain/blockAssembly"

/** Monaco line height — distance between text lines. */
export const BLOCK_EDITOR_LINE_HEIGHT = 27

export const BLOCK_OVERLAY_BOX_HEIGHT = 24
export const BLOCK_OVERLAY_PAD_X = 10
export const BLOCK_OVERLAY_GAP_X = 3
export const BLOCK_OVERLAY_ROW_GAP = 8
export const BLOCK_OVERLAY_PAD_Y = 2

function unionLineRects(lineRects) {
  if (lineRects.length === 0) return null
  if (lineRects.length === 1) return lineRects[0]

  let left = Infinity
  let top = Infinity
  let right = -Infinity
  let bottom = -Infinity

  for (const r of lineRects) {
    const h = r.height > 0 ? r.height : BLOCK_EDITOR_LINE_HEIGHT
    left = Math.min(left, r.left)
    top = Math.min(top, r.top)
    right = Math.max(right, r.left + r.width)
    bottom = Math.max(bottom, r.top + h)
  }

  return {
    left,
    top,
    width: Math.max(right - left, 2),
    height: Math.max(bottom - top, BLOCK_EDITOR_LINE_HEIGHT),
    multiline: true,
  }
}

function buildTabGuideText(column, tabSize = BLOCK_ASSEMBLY_TAB_SIZE) {
  const count = Math.max(0, column - 1)
  let text = ""
  for (let i = 1; i <= count; i += 1) {
    text += i % tabSize === 0 ? "." : " "
  }
  return text
}

export function expandRectToOverlayBox(
  rect,
  editorLineHeight = BLOCK_EDITOR_LINE_HEIGHT,
  neighbors = {},
) {
  void neighbors
  const rightPad = BLOCK_OVERLAY_PAD_X + BLOCK_OVERLAY_GAP_X

  if (rect.multiline) {
    return {
      left: rect.left,
      top: rect.top - BLOCK_OVERLAY_PAD_Y,
      width: rect.width + rightPad,
      height: rect.height + BLOCK_OVERLAY_PAD_Y * 2,
    }
  }

  const boxHeight = BLOCK_OVERLAY_BOX_HEIGHT
  const boxTop = rect.top + (editorLineHeight - boxHeight) / 2

  return {
    left: rect.left,
    top: boxTop,
    width: rect.width + rightPad,
    height: boxHeight,
  }
}

/**
 * Teacher editor: offset-based overlay rects from code in the model.
 * @param {import("monaco-editor").editor.IStandaloneCodeEditor} editor
 * @param {import("monaco-editor").editor.ITextModel} model
 * @param {{ start: number, end: number }} blockRange
 */
export function computeBlockOverlayRects(editor, model, blockRange) {
  const rangeStart = Math.max(0, blockRange.start)
  const rangeEnd = Math.min(blockRange.end, model.getValueLength())
  if (rangeStart >= rangeEnd) return []

  const lineRects = []
  const startLine = model.getPositionAt(rangeStart).lineNumber
  const endLine = model.getPositionAt(rangeEnd).lineNumber

  for (let line = startLine; line <= endLine; line += 1) {
    const lineStartOffset = model.getOffsetAt({
      lineNumber: line,
      column: 1,
    })
    const lineEndOffset = model.getOffsetAt({
      lineNumber: line,
      column: model.getLineMaxColumn(line),
    })
    const segStart = Math.max(rangeStart, lineStartOffset)
    const segEnd = Math.min(rangeEnd, lineEndOffset)
    if (segStart >= segEnd) continue

    const p1 = editor.getScrolledVisiblePosition(
      model.getPositionAt(segStart),
    )
    const p2 = editor.getScrolledVisiblePosition(
      model.getPositionAt(segEnd),
    )
    if (!p1 || !p2) continue

    lineRects.push({
      left: p1.left,
      top: p1.top,
      width: Math.max(p2.left - p1.left, 2),
      height: p1.height ?? 0,
    })
  }

  if (lineRects.length === 0) return []
  if (lineRects.length === 1) return lineRects
  return [unionLineRects(lineRects)]
}

/**
 * Line-based overlay boxes (block text shown inside frame).
 */
export function buildOverlayBoxesFromLinePlacements(
  editor,
  baseCode,
  placements,
  blocks,
  lineHeight,
  charWidth,
) {
  const model = editor.getModel()
  const monacoLineCount = model?.getLineCount() ?? 1
  const sorted = [...placements].sort(
    (a, b) => a.line - b.line || a.slot - b.slot,
  )
  const byVisualRow = new Map()
  for (const p of sorted) {
    const rowKey = Math.max(1, p.line)
    const list = byVisualRow.get(rowKey) ?? []
    list.push(p)
    byVisualRow.set(rowKey, list)
  }

  const safeCharWidth =
    Number.isFinite(charWidth) && charWidth > 0 ? charWidth : 7.87

  const boxes = []
  for (const [visualRow, lineSegs] of [...byVisualRow.entries()].sort(
    (a, b) => a[0] - b[0],
  )) {
    lineSegs.sort((a, b) => a.slot - b.slot)
    const anchorLine = Math.min(visualRow, monacoLineCount)
    const anchor = editor.getScrolledVisiblePosition({
      lineNumber: anchorLine,
      column: 1,
    })
    if (!anchor) continue

    const rowYOffset = (visualRow - anchorLine) * lineHeight

    for (let index = 0; index < lineSegs.length; index += 1) {
      const p = lineSegs[index]
      const raw = blocks[p.blockIndex] ?? ""
      const widthCols = blockFirstLineWidth(raw)
      const lineSpan = Math.max(1, raw.split("\n").length)
      const hasLeftNeighbor = index > 0
      const lineText = (baseCode.split("\n")[visualRow - 1] ?? "")
      const visualCol = normalizeCodeColumn(lineText, p.column)

      if (lineSpan > 1) {
        const lineRects = []
        for (let li = 0; li < lineSpan; li += 1) {
          const liCols = blockFirstLineWidth(raw.split("\n")[li] ?? "")
          const liWidth = Math.max(liCols * safeCharWidth, safeCharWidth)
          const liCol = li === 0 ? visualCol : 1
          lineRects.push({
            left: anchor.left + (liCol - 1) * safeCharWidth,
            top: anchor.top + rowYOffset + li * lineHeight,
            width: liWidth,
            height: anchor.height ?? lineHeight,
          })
        }
        const union = unionLineRects(lineRects)
        if (union) {
          const guideWidth = Math.max(0, (visualCol - 1) * safeCharWidth)
          boxes.push({
            key: p.id,
            blockIndex: p.blockIndex,
            guideLeft: anchor.left,
            guideTop: anchor.top + rowYOffset,
            guideText: buildTabGuideText(visualCol),
            guideWidth,
            label: raw,
            ...expandRectToOverlayBox(union, lineHeight, { hasLeftNeighbor }),
          })
        }
        continue
      }

      const widthPx = Math.max(widthCols * safeCharWidth, safeCharWidth)
      const left = anchor.left + (visualCol - 1) * safeCharWidth
      const top = anchor.top + rowYOffset
      const guideWidth = Math.max(0, (visualCol - 1) * safeCharWidth)

      boxes.push({
        key: p.id,
        blockIndex: p.blockIndex,
        guideLeft: anchor.left,
        guideTop: top,
        guideText: buildTabGuideText(visualCol),
        guideWidth,
        label: raw,
        ...expandRectToOverlayBox(
          {
            left,
            top,
            width: widthPx,
            height: anchor.height ?? lineHeight,
            multiline: false,
          },
          lineHeight,
          { hasLeftNeighbor },
        ),
      })
    }
  }

  return boxes
}

export function renderBlockOverlayLayer(layer, boxes, options = {}) {
  layer.replaceChildren()
  for (const box of boxes) {
    const el = document.createElement("div")
    el.className = "monaco-block-overlay"
    el.dataset.blockKey = box.key
    if (box.blockIndex != null) {
      el.dataset.blockIndex = String(box.blockIndex)
    }
    Object.assign(el.style, {
      position: "absolute",
      left: `${box.left}px`,
      top: `${box.top}px`,
      width: `${box.width}px`,
      height: `${box.height}px`,
    })
    if (box.guideText) {
      const guide = document.createElement("div")
      guide.className = "monaco-block-column-guide"
      guide.textContent = box.guideText
      Object.assign(guide.style, {
        position: "absolute",
        left: `${box.guideLeft}px`,
        top: `${box.guideTop}px`,
        width: `${box.guideWidth}px`,
        height: `${box.height}px`,
      })
      layer.appendChild(guide)
    }
    if (box.label) {
      const label = document.createElement("span")
      label.className = "monaco-block-overlay-label"
      label.textContent = box.label
      el.appendChild(label)
    }
    if (box.blockIndex != null) {
      if (options.onDragStart) {
        el.draggable = true
        el.addEventListener("dragstart", (event) => {
          options.onDragStart(event, box)
        })
      }
      if (options.onReturnToBank) {
        el.title = "Двойной щелчок или перетащите в банк, чтобы убрать блок"
        el.addEventListener("dblclick", (event) => {
          event.preventDefault()
          event.stopPropagation()
          options.onReturnToBank(box.blockIndex)
        })
      }
    }
    if (options.onBlockClick) {
      el.classList.add("monaco-block-overlay--interactive")
      el.title = "Клик — выделить блок целиком. Shift+клик — добавить к выделению"
      el.addEventListener("mousedown", (event) => {
        options.onBlockClick(box, event)
      })
    }
    layer.appendChild(el)
  }
}

export function ensureBlockOverlayLayer(editor) {
  const root = editor.getDomNode()
  if (!root) return null

  let layer = root.querySelector(".block-range-overlay-layer")
  if (!layer) {
    layer = document.createElement("div")
    layer.className = "block-range-overlay-layer"
    if (getComputedStyle(root).position === "static") {
      root.style.position = "relative"
    }
    root.appendChild(layer)
  }
  return layer
}
