import ReadonlyCodeView from "@/widgets/task-workspace/ReadonlyCodeView"

interface StudentMcqPanelProps {
  prompt?: string | null
  options: string[]
  selectedCode: string
  onSelect: (code: string) => void
  disabled?: boolean
}

export default function StudentMcqPanel({
  prompt,
  options,
  selectedCode,
  onSelect,
  disabled = false,
}: StudentMcqPanelProps) {
  const normalizedSelected = selectedCode.trim()

  return (
    <div className="flex h-full min-h-0 flex-col gap-3 p-4">
      <div className="rounded-lg border border-purple/20 bg-surface-2 p-4">
        <div className="text-[13px] font-medium text-ink">Выберите верный фрагмент Pascal</div>
        {prompt ? <p className="mt-2 text-[13px] leading-relaxed text-ink-muted">{prompt}</p> : null}
      </div>

      <div className="grid min-h-0 flex-1 gap-3 overflow-y-auto md:grid-cols-2">
        {options.map((option, index) => {
          const isSelected = normalizedSelected === option.trim()
          return (
            <button
              key={`${index}-${option.slice(0, 24)}`}
              type="button"
              disabled={disabled}
              onClick={() => onSelect(option)}
              className={[
                "rounded-lg border p-3 text-left transition-colors",
                isSelected
                  ? "border-lime bg-lime-soft/20 ring-1 ring-lime/40"
                  : "border-border bg-surface hover:border-purple/40",
                disabled ? "cursor-not-allowed opacity-70" : "cursor-pointer",
              ].join(" ")}
            >
              <div className="mb-2 text-[12px] font-medium text-ink-faint">Вариант {index + 1}</div>
              <ReadonlyCodeView code={option} language="pascal" />
            </button>
          )
        })}
      </div>
    </div>
  )
}
