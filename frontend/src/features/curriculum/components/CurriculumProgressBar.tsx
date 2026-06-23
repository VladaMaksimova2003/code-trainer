interface CurriculumProgressBarProps {
  /** 0..100 */
  percent: number
  /** purple-вариант (для текущего сборника) */
  purple?: boolean
  className?: string
  /** @deprecated optional label row — kept for CurriculumLanguagesBlock compat */
  label?: string
}

export default function CurriculumProgressBar({
  percent,
  purple = false,
  className = "",
  label,
}: CurriculumProgressBarProps) {
  const value = Math.max(0, Math.min(100, percent ?? 0))
  const bar = (
    <div className={`h-2 overflow-hidden rounded-full bg-surface-3 ${className}`}>
      <div
        className={
          "h-full rounded-full transition-[width] duration-500 " +
          (purple
            ? "bg-gradient-to-r from-purple to-[#a877ff]"
            : "bg-gradient-to-r from-lime to-lime-600")
        }
        style={{ width: `${value}%` }}
      />
    </div>
  )

  if (!label) return bar

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-ink-muted">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      {bar}
    </div>
  )
}

/** @deprecated use CurriculumProgressBar */
export const ProgressBar = CurriculumProgressBar
