import { useCallback, useEffect, useRef, useState } from "react"

export const TASK_LEFT_RAIL_DEFAULT_WIDTH = 380
export const TASK_LEFT_RAIL_MIN_WIDTH = 300
export const TASK_LEFT_RAIL_MAX_WIDTH = 560
const STORAGE_KEY = "task_left_rail_width"

export function getTaskLeftRailMaxWidth(viewportWidth = window.innerWidth): number {
  const maxByViewport = Math.floor(viewportWidth * 0.42)
  return Math.min(TASK_LEFT_RAIL_MAX_WIDTH, Math.max(TASK_LEFT_RAIL_MIN_WIDTH, maxByViewport))
}

export function clampTaskLeftRailWidth(
  width: number,
  viewportWidth = window.innerWidth,
): number {
  const max = getTaskLeftRailMaxWidth(viewportWidth)
  return Math.max(TASK_LEFT_RAIL_MIN_WIDTH, Math.min(max, Math.round(width)))
}

function readStoredWidth(): number {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return TASK_LEFT_RAIL_DEFAULT_WIDTH
    const parsed = Number.parseInt(raw, 10)
    if (!Number.isFinite(parsed)) return TASK_LEFT_RAIL_DEFAULT_WIDTH
    return clampTaskLeftRailWidth(parsed)
  } catch {
    return TASK_LEFT_RAIL_DEFAULT_WIDTH
  }
}

export function useTaskLeftRailWidth() {
  const [width, setWidth] = useState(readStoredWidth)
  const resizeStateRef = useRef({
    dragging: false,
    startX: 0,
    startWidth: TASK_LEFT_RAIL_DEFAULT_WIDTH,
  })

  const handleResizeStart = useCallback(
    (event: React.MouseEvent) => {
      event.preventDefault()
      resizeStateRef.current = {
        dragging: true,
        startX: event.clientX,
        startWidth: width,
      }
      document.body.style.cursor = "ew-resize"
      document.body.style.userSelect = "none"
    },
    [width],
  )

  const handleResizeReset = useCallback(() => {
    setWidth(TASK_LEFT_RAIL_DEFAULT_WIDTH)
  }, [])

  useEffect(() => {
    const onMouseMove = (event: MouseEvent) => {
      if (!resizeStateRef.current.dragging) return
      const delta = event.clientX - resizeStateRef.current.startX
      setWidth(clampTaskLeftRailWidth(resizeStateRef.current.startWidth + delta))
    }

    const stopResize = () => {
      if (!resizeStateRef.current.dragging) return
      resizeStateRef.current.dragging = false
      document.body.style.cursor = ""
      document.body.style.userSelect = ""
    }

    window.addEventListener("mousemove", onMouseMove)
    window.addEventListener("mouseup", stopResize)
    return () => {
      window.removeEventListener("mousemove", onMouseMove)
      window.removeEventListener("mouseup", stopResize)
      document.body.style.cursor = ""
      document.body.style.userSelect = ""
    }
  }, [])

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, String(width))
    } catch {
      /* ignore */
    }
  }, [width])

  useEffect(() => {
    const onWindowResize = () => {
      setWidth((current) => clampTaskLeftRailWidth(current))
    }
    window.addEventListener("resize", onWindowResize)
    return () => window.removeEventListener("resize", onWindowResize)
  }, [])

  return {
    width,
    maxWidth: getTaskLeftRailMaxWidth(),
    handleResizeStart,
    handleResizeReset,
  }
}
