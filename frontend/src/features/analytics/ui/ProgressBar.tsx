interface ProgressBarProps {
  label: string
  hint?: string
  percent?: number
  detail?: string
  accent?: "lime" | "purple" | "violet" | string
}

export default function ProgressBar({
  label,
  hint,
  percent = 0,
  detail,
  accent = "lime",
}: ProgressBarProps) {
  const width = Math.min(100, Math.max(0, Number(percent) || 0))
  const barClass =
    accent === "purple" || accent === "violet"
      ? "bg-gradient-to-r from-purple to-[#a877ff]"
      : "bg-gradient-to-r from-lime to-lime-600"

  return (
    <div className="space-y-1.5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="text-sm font-medium text-ink">{label}</span>
        <span className="text-sm text-ink-muted">{width}%</span>
      </div>
      {hint && <p className="text-xs text-ink-faint">{hint}</p>}
      <div className="h-2 overflow-hidden rounded-full bg-surface-3">
        <div
          className={`h-full rounded-full transition-all ${barClass}`}
          style={{ width: `${width}%` }}
        />
      </div>
      {detail && <p className="text-xs text-ink-faint">{detail}</p>}
    </div>
  )
}
