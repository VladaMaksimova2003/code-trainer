import { useCallback, useLayoutEffect, useRef, useState } from "react"

export interface PopoverAnchorRect {
  left: number
  top: number
  bottom: number
  right?: number
}

interface UseDraggablePopoverOptions {
  anchorRect: PopoverAnchorRect | null | undefined
  width: number
  maxHeight?: number
  enabled?: boolean
}

const VIEWPORT_MARGIN = 12
const ANCHOR_GAP = 8
const MIN_POPOVER_HEIGHT = 120

function clampLeft(anchorLeft: number, width: number): number {
  let left = anchorLeft
  if (left + width > window.innerWidth - VIEWPORT_MARGIN) {
    left = window.innerWidth - width - VIEWPORT_MARGIN
  }
  return Math.max(VIEWPORT_MARGIN, left)
}

function resolveVerticalPlacement(
  anchorRect: PopoverAnchorRect,
  popoverHeight: number,
  maxHeight: number,
): { top: number; maxHeight: number } {
  const spaceBelow = window.innerHeight - anchorRect.bottom - VIEWPORT_MARGIN - ANCHOR_GAP
  const spaceAbove = anchorRect.top - VIEWPORT_MARGIN - ANCHOR_GAP
  const contentHeight = Math.min(Math.max(popoverHeight, MIN_POPOVER_HEIGHT), maxHeight)

  const bottomIfBelow = anchorRect.bottom + ANCHOR_GAP + contentHeight
  const overflowsBottom = bottomIfBelow > window.innerHeight - VIEWPORT_MARGIN

  const topIfAbove = anchorRect.top - ANCHOR_GAP - contentHeight
  const fitsAbove = topIfAbove >= VIEWPORT_MARGIN

  let openBelow = true
  if (overflowsBottom) {
    if (fitsAbove || spaceAbove > spaceBelow) {
      openBelow = false
    }
  }

  if (openBelow) {
    return {
      top: anchorRect.bottom + ANCHOR_GAP,
      maxHeight: Math.min(maxHeight, Math.max(MIN_POPOVER_HEIGHT, spaceBelow)),
    }
  }

  const maxH = Math.min(maxHeight, Math.max(MIN_POPOVER_HEIGHT, spaceAbove))
  const visibleHeight = Math.min(contentHeight, maxH)
  return {
    top: Math.max(VIEWPORT_MARGIN, anchorRect.top - visibleHeight - ANCHOR_GAP),
    maxHeight: maxH,
  }
}

export function useDraggablePopover({
  anchorRect,
  width,
  maxHeight = Math.min(typeof window !== "undefined" ? window.innerHeight * 0.78 : 520, 560),
  enabled = true,
}: UseDraggablePopoverOptions) {
  const [pos, setPos] = useState<{ left: number; top: number } | null>(null)
  const [resolvedMaxHeight, setResolvedMaxHeight] = useState(maxHeight)
  const [isPlacementReady, setIsPlacementReady] = useState(false)
  const popRef = useRef<HTMLDivElement | null>(null)
  const dragRef = useRef<{
    startX: number
    startY: number
    originLeft: number
    originTop: number
  } | null>(null)

  const reposition = useCallback(() => {
    if (!enabled || !anchorRect || !popRef.current) {
      return false
    }

    const left = clampLeft(anchorRect.left, width)
    const popoverHeight = popRef.current.scrollHeight
    const placement = resolveVerticalPlacement(anchorRect, popoverHeight, maxHeight)

    setPos({ left, top: placement.top })
    setResolvedMaxHeight(placement.maxHeight)
    setIsPlacementReady(true)
    return true
  }, [anchorRect, enabled, maxHeight, width])

  useLayoutEffect(() => {
    if (!enabled || !anchorRect) {
      setPos(null)
      setIsPlacementReady(false)
      return
    }

    setIsPlacementReady(false)
    const left = clampLeft(anchorRect.left, width)
    setPos({ left, top: anchorRect.bottom + ANCHOR_GAP })
    setResolvedMaxHeight(maxHeight)

    let frameId = 0
    const measure = () => {
      if (reposition()) return
      frameId = window.requestAnimationFrame(measure)
    }
    frameId = window.requestAnimationFrame(measure)

    return () => window.cancelAnimationFrame(frameId)
  }, [anchorRect, enabled, maxHeight, reposition, width])

  useLayoutEffect(() => {
    if (!enabled || !anchorRect || !popRef.current) return

    const observer = new ResizeObserver(() => {
      reposition()
    })
    observer.observe(popRef.current)
    return () => observer.disconnect()
  }, [anchorRect, enabled, reposition])

  const onDragStart = useCallback(
    (event: React.MouseEvent) => {
      if (!pos || event.button !== 0) return
      event.preventDefault()
      dragRef.current = {
        startX: event.clientX,
        startY: event.clientY,
        originLeft: pos.left,
        originTop: pos.top,
      }
      const onMove = (e: MouseEvent) => {
        const drag = dragRef.current
        if (!drag) return
        const margin = VIEWPORT_MARGIN
        setPos({
          left: Math.min(
            Math.max(margin, drag.originLeft + e.clientX - drag.startX),
            window.innerWidth - width - margin,
          ),
          top: Math.min(
            Math.max(margin, drag.originTop + e.clientY - drag.startY),
            window.innerHeight - 100 - margin,
          ),
        })
      }
      const onUp = () => {
        dragRef.current = null
        window.removeEventListener("mousemove", onMove)
        window.removeEventListener("mouseup", onUp)
      }
      window.addEventListener("mousemove", onMove)
      window.addEventListener("mouseup", onUp)
    },
    [pos, width],
  )

  return { pos, onDragStart, maxHeight: resolvedMaxHeight, popRef, isPlacementReady }
}
