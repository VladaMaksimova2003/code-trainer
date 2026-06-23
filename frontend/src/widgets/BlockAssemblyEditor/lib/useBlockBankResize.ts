import { useCallback, useEffect, useRef, useState, type MouseEvent as ReactMouseEvent, type RefObject } from "react"

const STORAGE_KEY = "block-assembly-bank-height"
export const DEFAULT_BANK_HEIGHT = 220
export const MIN_BANK_HEIGHT = 72
export const MAX_BANK_HEIGHT = 480

function clampBankHeight(value: number, max = MAX_BANK_HEIGHT) {
  return Math.min(max, Math.max(MIN_BANK_HEIGHT, Math.round(value)))
}

function readStoredBankHeight() {
  if (typeof window === "undefined") return DEFAULT_BANK_HEIGHT
  const raw = window.sessionStorage.getItem(STORAGE_KEY)
  const parsed = raw ? Number(raw) : NaN
  return Number.isFinite(parsed) ? clampBankHeight(parsed) : DEFAULT_BANK_HEIGHT
}

export function useBlockBankResize(containerRef: RefObject<HTMLElement | null>) {
  const [bankHeight, setBankHeight] = useState(readStoredBankHeight)
  const resizeStateRef = useRef({ dragging: false, startY: 0, startHeight: DEFAULT_BANK_HEIGHT })

  const getMaxHeight = useCallback(() => {
    const containerHeight = containerRef.current?.clientHeight ?? 0
    if (containerHeight > 0) {
      const reservedForSolution = 120
      const maxByContainer = Math.max(MIN_BANK_HEIGHT, containerHeight - reservedForSolution)
      return clampBankHeight(Math.min(containerHeight * 0.72, maxByContainer), maxByContainer)
    }
    return MAX_BANK_HEIGHT
  }, [containerRef])

  const handleResizeStart = useCallback(
    (event: ReactMouseEvent<HTMLDivElement>) => {
      event.preventDefault()
      resizeStateRef.current = {
        dragging: true,
        startY: event.clientY,
        startHeight: bankHeight,
      }
      document.body.style.cursor = "ns-resize"
      document.body.style.userSelect = "none"
    },
    [bankHeight],
  )

  const handleResizeReset = useCallback(() => {
    setBankHeight(DEFAULT_BANK_HEIGHT)
  }, [])

  useEffect(() => {
    const onMouseMove = (event: MouseEvent) => {
      if (!resizeStateRef.current.dragging) return
      const delta = resizeStateRef.current.startY - event.clientY
      setBankHeight(
        clampBankHeight(resizeStateRef.current.startHeight + delta, getMaxHeight()),
      )
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
  }, [getMaxHeight])

  useEffect(() => {
    window.sessionStorage.setItem(STORAGE_KEY, String(bankHeight))
  }, [bankHeight])

  useEffect(() => {
    const onWindowResize = () => {
      setBankHeight((current) => clampBankHeight(current, getMaxHeight()))
    }
    window.addEventListener("resize", onWindowResize)
    return () => window.removeEventListener("resize", onWindowResize)
  }, [getMaxHeight])

  return {
    bankHeight,
    handleResizeStart,
    handleResizeReset,
    getMaxHeight,
  }
}
