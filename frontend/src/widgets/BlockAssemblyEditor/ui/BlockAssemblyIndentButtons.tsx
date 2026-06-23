interface BlockAssemblyIndentButtonsProps {
  indentLevel: number
  maxIndent?: number
  onDecrease: () => void
  onIncrease: () => void
  className?: string
}

function IconChevL() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
      <path d="M10 4L6 8l4 4" />
    </svg>
  )
}

function IconChevR() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
      <path d="M6 4l4 4-4 4" />
    </svg>
  )
}

function LineIconButton({ onClick, title, disabled, tone, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={title}
      disabled={disabled}
      className={[
        "inline-flex h-7 w-7 items-center justify-center rounded-md border border-[#333d4f] bg-surface-2 text-ink-muted transition",
        !disabled && "hover:border-[#3e4a60] hover:text-ink",
        !disabled && tone === "lime" && "hover:border-lime/50 hover:bg-lime-soft hover:text-lime",
        disabled && "cursor-not-allowed opacity-30",
      ].join(" ")}
    >
      {children}
    </button>
  )
}

export default function BlockAssemblyIndentButtons({
  indentLevel,
  maxIndent = 8,
  onDecrease,
  onIncrease,
  className = "",
}: BlockAssemblyIndentButtonsProps) {
  return (
    <div className={`ml-1 flex items-center gap-1 ${className}`.trim()}>
      <LineIconButton
        onClick={onDecrease}
        title="Уменьшить отступ"
        disabled={indentLevel <= 0}
        tone="lime"
      >
        <IconChevL />
      </LineIconButton>
      <LineIconButton
        onClick={onIncrease}
        title="Увеличить отступ"
        disabled={indentLevel >= maxIndent}
        tone="lime"
      >
        <IconChevR />
      </LineIconButton>
    </div>
  )
}
