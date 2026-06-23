interface AlertBannerProps {
  variant?: "error" | "success" | "info"
  message?: string | null
  onDismiss?: () => void
}

export default function AlertBanner({ variant = "error", message, onDismiss }: AlertBannerProps) {
  if (!message) return null
  const styles: Record<string, string> = {
    error: "bg-red-900/40 border-red-800 text-red-100",
    success: "bg-emerald-900/40 border-emerald-800 text-emerald-100",
    info: "bg-sky-900/40 border-sky-800 text-sky-100",
  }
  return (
    <div
      className={`mb-4 px-4 py-3 rounded border text-sm flex justify-between gap-3 ${styles[variant] || styles.error}`}
    >
      <span>{message}</span>
      {onDismiss ? (
        <button type="button" onClick={onDismiss} className="opacity-70 hover:opacity-100">
          ×
        </button>
      ) : null}
    </div>
  )
}
