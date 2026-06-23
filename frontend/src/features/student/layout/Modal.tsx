import { useEffect } from "react"

export default function Modal({ open, onClose, title, footer, children, width }) {
  useEffect(() => {
    if (!open) return undefined
    const onKey = (e: unknown) => {
      if (e.key === "Escape") onClose?.()
    }
    document.addEventListener("keydown", onKey)
    return () => document.removeEventListener("keydown", onKey)
  }, [open, onClose])

  if (!open) return null

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e: unknown) => {
        if (e.target === e.currentTarget) onClose?.()
      }}
    >
      <div className="modal" style={width ? { maxWidth: width } : undefined} role="dialog">
        {title ? (
          <div className="mh">
            <b style={{ fontSize: 16 }}>{title}</b>
            <button type="button" className="icon-btn" onClick={onClose} aria-label="Закрыть">
              ✕
            </button>
          </div>
        ) : null}
        <div className="mb">{children}</div>
        {footer ? <div className="mf">{footer}</div> : null}
      </div>
    </div>
  )
}
