export default function BlockAssemblyModeHint({ isTemplate, variant = "student" }) {
  const isTeacher = variant === "teacher"
  const label = isTeacher
    ? "Редактор блоков"
    : isTemplate
      ? "Шаблон с пропусками"
      : "Свободная сборка"
  const hint = isTeacher
    ? "Напишите код, выделите фрагмент и преобразуйте его в блок."
    : isTemplate
      ? "Заполни пропуски нужными блоками."
      : "Перетаскивай блоки в строки, как нужно."

  return (
    <div className="flex shrink-0 items-center gap-2 border-b border-border bg-surface/40 px-4 py-2.5">
      <span className="mr-1 text-[11px] font-semibold uppercase tracking-[0.1em] text-ink-faint">
        Режим
      </span>
      <span className="inline-flex h-7 items-center rounded-md border border-[rgba(142,255,1,.4)] bg-lime-soft px-3 text-[12.5px] font-medium text-lime">
        {label}
      </span>
      <div className="flex-1" />
      <p className="text-[11.5px] text-ink-faint">{hint}</p>
    </div>
  )
}
