const LABELS = {
  syntax: "Синтаксис",
  logic: "Логика",
  runtime: "Runtime",
}

interface ErrorBreakdown {
  percent?: Record<string, number>
  counts?: Record<string, number>
  total_failed?: number
}

interface ErrorBreakdownChartProps {
  breakdown?: ErrorBreakdown | null
  title?: string
}

export default function ErrorBreakdownChart({
  breakdown,
  title = "Частые ошибки",
}: ErrorBreakdownChartProps) {
  const percent = breakdown?.percent ?? {}
  const counts = breakdown?.counts ?? {}
  const total = breakdown?.total_failed ?? 0

  if (!total) {
    return (
      <div className="rounded-xl border border-slate-800 bg-[#0c1224] p-4">
        <h3 className="text-sm font-medium text-slate-200 mb-2">{title}</h3>
        <p className="text-sm text-slate-500">Недостаточно неуспешных попыток для анализа.</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0c1224] p-4 space-y-3">
      <h3 className="text-sm font-medium text-slate-200">{title}</h3>
      <p className="text-xs text-slate-500">На основе {total} неуспешных отправок</p>
      <ul className="space-y-2">
        {Object.entries(LABELS).map(([key, label]) => (
          <li key={key} className="flex items-center justify-between gap-3 text-sm">
            <span className="text-slate-300">{label}</span>
            <span className="text-slate-400">
              {percent[key] ?? 0}% ({counts[key] ?? 0})
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
