import { useMemo } from "react"
import {
  contributionLevelFromCount,
  contribLegendBackground,
  maxDailyCount,
} from "@/shared/utils/contribLevels"
import { formatUtcDateKey } from "@/shared/utils/activityStats"

const MONTH_NAMES = [
  "Янв",
  "Фев",
  "Мар",
  "Апр",
  "Май",
  "Июн",
  "Июл",
  "Авг",
  "Сен",
  "Окт",
  "Ноя",
  "Дек",
]

function buildFromActivity(byDate = {}, weeks = 26) {
  const totalDays = weeks * 7
  const now = new Date()
  const end = new Date(
    Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()),
  )
  const start = new Date(end)
  start.setUTCDate(end.getUTCDate() - (totalDays - 1))

  const counts = []
  const grid = []

  for (let w = 0; w < weeks; w += 1) {
    const days = []
    for (let d = 0; d < 7; d += 1) {
      const cell = new Date(start)
      cell.setUTCDate(start.getUTCDate() + w * 7 + d)
      const key = formatUtcDateKey(cell)
      const count = Number(byDate[key] || 0)
      days.push({ count, key })
      counts.push(count)
    }
    grid.push(days)
  }

  const maxDaily = maxDailyCount(counts)
  for (const week of grid) {
    for (const day of week) {
      day.level = contributionLevelFromCount(day.count, maxDaily)
    }
  }

  return grid
}

function formatCountTitle(count: unknown) {
  if (count <= 0) return "нет активности"
  const mod10 = count % 10
  const mod100 = count % 100
  if (mod10 === 1 && mod100 !== 11) return `${count} действие`
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return `${count} действия`
  return `${count} действий`
}

export default function ContribGraph({ byDate, weeks = 26, pp = false }) {
  const grid = useMemo(() => buildFromActivity(byDate ?? {}, weeks), [byDate, weeks])

  const totalDays = weeks * 7
  const now = new Date()
  const end = new Date(
    Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()),
  )
  const startDate = new Date(end)
  startDate.setUTCDate(end.getUTCDate() - (totalDays - 1))

  const labels = []
  let lastMonth = -1
  for (let w = 0; w < weeks; w += 1) {
    const d = new Date(startDate)
    d.setUTCDate(startDate.getUTCDate() + w * 7)
    const month = d.getUTCMonth()
    if (month !== lastMonth) {
      labels.push({ w, m: MONTH_NAMES[month] })
      lastMonth = month
    }
  }
  const monthCells = Array.from({ length: weeks }, () => "")
  labels.forEach(({ w, m }) => {
    monthCells[w] = m
  })

  return (
    <div className={`contrib-wrap${pp ? " pp" : ""}`}>
      <div
        className="contrib-months"
        style={{ gridTemplateColumns: `repeat(${weeks}, 1fr)` }}
      >
        {monthCells.map((m, i) => (
          <span key={i}>{m}</span>
        ))}
      </div>
      <div className="contrib-grid">
        <div className="contrib-days">
          {["", "Пн", "", "Ср", "", "Пт", ""].map((d, i) => (
            <span key={i}>{d}</span>
          ))}
        </div>
        <div className="contrib-weeks">
          {grid.map((week, i) => (
            <div key={i} className="contrib-week">
              {week.map(({ count, level }, j) => (
                <i
                  key={j}
                  className={level ? `l${level}` : ""}
                  title={formatCountTitle(count)}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
      <div className="contrib-legend">
        меньше
        {[1, 2, 3, 4].map((lv: unknown) => (
          <i
            key={lv}
            style={{ background: contribLegendBackground(lv, { pp }) }}
          />
        ))}
        больше
      </div>
    </div>
  )
}
