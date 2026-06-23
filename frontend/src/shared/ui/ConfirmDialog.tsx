import Modal from "@/shared/ui/Modal"

interface ConfirmDialogProps {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: "danger" | "primary" | "secondary"
  loading?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Подтвердить",
  cancelLabel = "Отмена",
  variant = "danger",
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const confirmClass =
    variant === "danger"
      ? "btn btn-danger btn-sm"
      : variant === "primary"
        ? "btn btn-primary btn-sm"
        : "btn btn-secondary btn-sm"

  return (
    <Modal
      open={open}
      title={title}
      onClose={onCancel}
      footer={
        <>
          <button type="button" onClick={onCancel} disabled={loading} className="btn btn-ghost btn-sm">
            {cancelLabel}
          </button>
          <button type="button" onClick={onConfirm} disabled={loading} className={confirmClass}>
            {loading ? "…" : confirmLabel}
          </button>
        </>
      }
    >
      <p className="muted" style={{ fontSize: 14, margin: 0 }}>
        {message}
      </p>
    </Modal>
  )
}
