import { useEffect } from "react"

export default function ApModal({ open, title, children, footer, onClose, width }) {
  useEffect(() => {
    if (!open) return undefined
    const onKey = (e) => {
      if (e.key === "Escape") onClose?.()
    }
    document.addEventListener("keydown", onKey)
    return () => document.removeEventListener("keydown", onKey)
  }, [open, onClose])

  if (!open) return null

  return (
    <div
      className="ap-modal-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose?.()
      }}
    >
      <div className="ap-modal" style={width ? { maxWidth: width } : undefined}>
        {title ? (
          <div className="ap-modal-head">
            <b style={{ fontSize: 16 }}>{title}</b>
            <button type="button" className="ap-btn ap-btn-ghost ap-btn-sm" onClick={onClose}>
              ✕
            </button>
          </div>
        ) : null}
        <div className="ap-modal-body">{children}</div>
        {footer ? <div className="ap-modal-foot">{footer}</div> : null}
      </div>
    </div>
  )
}

export function ApConfirmDialog({
  open,
  title,
  body,
  confirmLabel = "Подтвердить",
  cancelLabel = "Отмена",
  danger = false,
  loading = false,
  onConfirm,
  onClose,
}) {
  return (
    <ApModal
      open={open}
      title={title}
      onClose={onClose}
      footer={
        <>
          <button type="button" className="ap-btn ap-btn-ghost ap-btn-sm" onClick={onClose} disabled={loading}>
            {cancelLabel}
          </button>
          <button
            type="button"
            className={`ap-btn ap-btn-sm ${danger ? "ap-btn-danger" : "ap-btn-primary"}`}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "…" : confirmLabel}
          </button>
        </>
      }
    >
      <p className="ap-muted" style={{ margin: 0, fontSize: 14 }}>
        {body}
      </p>
    </ApModal>
  )
}
