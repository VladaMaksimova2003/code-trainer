/**
 * Единый блок активности по дням для ученика и преподавателя.
 * Данные до 2026 года не показываются.
 */
export const MIN_ACTIVITY_YEAR = 2026

const MONTHS_SHORT = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
const CELL_SIZE = 10
const CELL_GAP = 3
const GRAPH_HEIGHT = 7 * CELL_SIZE + 6 * CELL_GAP

function filterActivityFromMinYear(byDate, minYear = MIN_ACTIVITY_YEAR) {
  const prefix = `${minYear}-`
  const out = {}
  for (const [k, v] of Object.entries(byDate ?? {})) {
    if (k >= prefix && typeof v === "number") out[k] = v
  }
  return out
}

function countEventsInYear(byDate, year) {
  let n = 0
  const prefix = `${year}-`
  for (const [k, v] of Object.entries(byDate ?? {})) {
    if (k.startsWith(prefix) && typeof v === "number") n += v
  }
  return n
}

function formatDayTitle(isoDate, countInYear, inYear) {
  if (!inYear || countInYear < 0) return ""
  const [ys, ms, ds] = isoDate.split("-")
  const m = parseInt(ms, 10)
  const d = parseInt(ds, 10)
  const monthLabel = MONTHS_SHORT[m - 1] ?? ms
  if (countInYear === 0) return `${d} ${monthLabel} ${ys}: без активности`
  if (countInYear === 1) return `${d} ${monthLabel} ${ys}: 1 активность`
  if (countInYear >= 2 && countInYear <= 4) {
    return `${d} ${monthLabel} ${ys}: ${countInYear} активности`
  }
  return `${d} ${monthLabel} ${ys}: ${countInYear} активностей`
}

function buildColumnsForYear(byDate, year) {
  const jan1 = new Date(Date.UTC(year, 0, 1))
  const dec31 = new Date(Date.UTC(year, 11, 31))

  let gridStart = new Date(jan1)
  const back = (jan1.getUTCDay() + 6) % 7
  gridStart.setUTCDate(gridStart.getUTCDate() - back)

  let gridEnd = new Date(dec31)
  const monIdx = (dec31.getUTCDay() + 6) % 7
  gridEnd.setUTCDate(gridEnd.getUTCDate() + (6 - monIdx))

  const columns = []
  for (let weekStart = new Date(gridStart); weekStart <= gridEnd; ) {
    const cells = []
    for (let r = 0; r < 7; r += 1) {
      const cell = new Date(weekStart)
      cell.setUTCDate(weekStart.getUTCDate() + r)
      const key = cell.toISOString().slice(0, 10)
      const inYear = cell >= jan1 && cell <= dec31
      const countRaw = typeof byDate[key] === "number" ? byDate[key] : 0
      const count = inYear ? countRaw : -1
      cells.push({
        date: key,
        count,
        inYear,
      })
    }
    columns.push({ weekStartUtc: weekStart.toISOString().slice(0, 10), cells })
    weekStart.setUTCDate(weekStart.getUTCDate() + 7)
  }
  return columns
}

function monthLabelForWeek(cells) {
  for (const c of cells) {
    if (!c.inYear) continue
    const m = Number(c.date.slice(5, 7))
    const d = Number(c.date.slice(8, 10))
    if (d === 1) return MONTHS_SHORT[m - 1] ?? ""
  }
  return ""
}

function levelClass(cell) {
  if (!cell.inYear || cell.count < 0) {
    return "bg-gray-800 border border-gray-700"
  }
  const n = cell.count
  if (n <= 0) return "bg-gray-800 border border-gray-700"
  if (n === 1) return "bg-emerald-900"
  if (n === 2) return "bg-emerald-700"
  if (n <= 4) return "bg-emerald-600"
  return "bg-emerald-400"
}

export default function GithubContributionGraph({
  byDate = {},
  year,
  title = "Активность",
  subtitle = "",
  summaryText,
}) {
  const filtered = filterActivityFromMinYear(byDate, MIN_ACTIVITY_YEAR)
  const currentYear = Math.max(MIN_ACTIVITY_YEAR, year ?? new Date().getUTCFullYear())
  const columns = buildColumnsForYear(filtered, currentYear)
  const totalEvents = countEventsInYear(filtered, currentYear)

  return (
    <section className="rounded-lg border border-gray-800 bg-gray-900 p-4 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">
          {title}
        </h2>
        <span className="text-xs text-gray-500">
          {summaryText || `Событий за ${currentYear}: ${totalEvents}`}
        </span>
      </div>

      {subtitle ? (
        <p className="text-xs text-gray-500 mb-3">{subtitle}</p>
      ) : null}

      <div className="flex-1 min-w-0 overflow-x-auto pb-2 scrollbar-activity">
        <div className="flex gap-3 mb-1">
          <div className="w-9 shrink-0 pr-1" aria-hidden />
          <div className="flex min-w-0" style={{ gap: CELL_GAP }}>
            {columns.map((col, i) => {
              const lbl = monthLabelForWeek(col.cells)
              return (
                <div
                  key={`m-${col.weekStartUtc}-${i}`}
                  className="shrink-0 text-[11px] text-gray-500 leading-none"
                  style={{ width: CELL_SIZE }}
                >
                  {lbl ? <span className="block truncate text-left">{lbl}</span> : null}
                </div>
              )
            })}
          </div>
        </div>

        <div className="flex gap-3">
          <div
            className="flex flex-col justify-between shrink-0 w-9 text-[11px] text-gray-500 pr-1"
            style={{ height: GRAPH_HEIGHT }}
          >
            <span>пн</span>
            <span />
            <span>ср</span>
            <span />
            <span>пт</span>
            <span />
            <span />
          </div>

          <div className="flex" style={{ gap: CELL_GAP }}>
            {columns.map((col, ci) => (
              <div
                key={`c-${ci}-${col.weekStartUtc}`}
                className="flex flex-col shrink-0"
                style={{ gap: CELL_GAP }}
              >
                {col.cells.map((cell, ri) => (
                  <div
                    key={ri}
                    title={formatDayTitle(cell.date, cell.count, cell.inYear)}
                    className={`rounded-sm shrink-0 transition-opacity hover:opacity-90 ${levelClass(cell)}`}
                    style={{ width: CELL_SIZE, height: CELL_SIZE }}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 mt-4 text-[10px] text-gray-500">
        <span>Меньше</span>
        <div className="flex gap-0.5">
          <div className="w-3 h-3 rounded-sm bg-gray-800 border border-gray-700" />
          <div className="w-3 h-3 rounded-sm bg-emerald-900" />
          <div className="w-3 h-3 rounded-sm bg-emerald-700" />
          <div className="w-3 h-3 rounded-sm bg-emerald-600" />
          <div className="w-3 h-3 rounded-sm bg-emerald-400" />
        </div>
        <span>Больше</span>
      </div>
    </section>
  )
}
