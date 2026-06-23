import { useEffect, useRef } from "react"
import { createPortal } from "react-dom"
import type { ReactNode } from "react"

interface ModalProps {
  open: boolean
  onClose?: () => void
  title?: ReactNode
  children?: ReactNode
  footer?: ReactNode
  labelledById?: string
}

export default function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  labelledById = "modal-title",
}: ModalProps) {
  const ref = useRef<HTMLDivElement>(null)
  const prevFocus = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (!open) return undefined
    prevFocus.current = document.activeElement as HTMLElement | null
    const node = ref.current

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose?.()
        return
      }
      if (e.key === "Tab" && node) {
        const focusables = node.querySelectorAll<HTMLElement>(
          'a[href],button:not([disabled]),textarea,input,select,[tabindex]:not([tabindex="-1"])',
        )
        if (!focusables.length) return
        const first = focusables[0]
        const last = focusables[focusables.length - 1]
        if (e.shiftKey && document.activeElement === first) {
          last.focus()
          e.preventDefault()
        } else if (!e.shiftKey && document.activeElement === last) {
          first.focus()
          e.preventDefault()
        }
      }
    }

    document.addEventListener("keydown", onKey)
    const t = window.setTimeout(() => {
      const f = node?.querySelector<HTMLElement>(
        'textarea,input,button:not([disabled]),[tabindex]:not([tabindex="-1"])',
      )
      f?.focus()
    }, 30)

    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = "hidden"

    return () => {
      document.removeEventListener("keydown", onKey)
      clearTimeout(t)
      document.body.style.overflow = prevOverflow
      prevFocus.current?.focus?.()
    }
  }, [open, onClose])

  if (!open) return null

  return createPortal(
    <div
      className="fixed inset-0 z-[320] flex items-center justify-center bg-black/65 backdrop-blur-md p-4 sm:p-6"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose?.()
      }}
    >
      <div
        ref={ref}
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledById}
        className="w-full sm:w-[min(520px,calc(100vw-24px))] max-h-[min(92vh,calc(100vh-48px))] flex flex-col bg-surface border border-border rounded-xl shadow-[0_40px_90px_-30px_rgba(0,0,0,0.8)]"
      >
        {title ? (
          <div className="flex items-center justify-between px-5 py-4 border-b border-border">
            <h2 id={labelledById} className="text-[15px] font-semibold text-ink">
              {title}
            </h2>
            <button
              type="button"
              aria-label="Закрыть"
              onClick={onClose}
              className="icon-btn h-8 w-8 text-ink-faint hover:text-ink"
            >
              ✕
            </button>
          </div>
        ) : null}
        <div className="px-5 py-4 overflow-y-auto">{children}</div>
        {footer ? (
          <div className="flex justify-end gap-2.5 px-5 py-4 border-t border-border">{footer}</div>
        ) : null}
      </div>
    </div>,
    document.body,
  )
}
