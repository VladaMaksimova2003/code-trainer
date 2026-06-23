import { useMemo, useState } from "react"
import Badge from "@/shared/ui/Badge"
import { buildDailyBars, formatDeltaBadge } from "@/shared/utils/activityStats"

function legendDot(color, label) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 7 }}>
      <i
        style={{
          width: 11,
          height: 11,
          borderRadius: 3,
          background: color,
          display: "inline-block",
        }}
      />
      {label}
    </span>
  )
}

export default function TeacherToxicAnalyticsPanel({ analytics, activity, catalogCount = 0 }) {
  const [rangeDays, setRangeDays] = useState(30)

  const summary = useMemo(() => {
    const s = analytics?.summary
    if (s) {
      return {
        students: s.student_count ?? 0,
        activeTasks: s.active_tasks ?? 0,
        avgSuccess: s.avg_success_rate ?? 0,
        studentsWeeklyDelta: s.students_weekly_delta ?? 0,
        successDeltaMonth: s.avg_success_rate_delta_month ?? 0,
      }
    }
    if (!analytics) {
      return {
        students: 0,
        activeTasks: 0,
        avgSuccess: 0,
        studentsWeeklyDelta: 0,
        successDeltaMonth: 0,
      }
    }
    const rates = (analytics.per_assignment || []).map((r: unknown) => r.success_percent)
    return {
      students: analytics.students?.length ?? 0,
      activeTasks: analytics.per_assignment?.length ?? 0,
      avgSuccess:
        rates.length > 0
          ? Math.round(rates.reduce((a, b) => a + b, 0) / rates.length)
          : 0,
      studentsWeeklyDelta: 0,
      successDeltaMonth: 0,
    }
  }, [analytics])

  const activityByDate = analytics?.submissions_by_date ?? activity?.by_date ?? {}

  const bars = useMemo(
    () => buildDailyBars(activityByDate, rangeDays === 7 ? 7 : 30),
    [activityByDate, rangeDays]
  )

  const topTasks = useMemo(() => {
    return [...(analytics?.per_assignment || [])]
      .sort((a, b) => (b.total_submissions || 0) - (a.total_submissions || 0))
      .slice(0, 4)
  }, [analytics])

  const weakTasks = useMemo(() => {
    return [...(analytics?.per_assignment || [])]
      .filter((r: unknown) => r.total_submissions > 0)
      .sort((a, b) => a.success_percent - b.success_percent)
      .slice(0, 3)
  }, [analytics])

  if (!analytics) {
    return <p className="muted">Нет данных аналитики.</p>
  }

  const studentsDeltaLabel = formatDeltaBadge(summary.studentsWeeklyDelta, { suffix: " за неделю" })
  const successDeltaLabel = formatDeltaBadge(summary.successDeltaMonth, {
    suffix: "% к месяцу",
  })

  return (
    <div>
      <div className="cards3" style={{ marginBottom: 18 }}>
        <div className="card card-pad">
          <div className="mut3" style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Студентов
          </div>
          <div className="stat" style={{ marginTop: 6 }}>
            {summary.students}
          </div>
          {studentsDeltaLabel ? (
            <Badge
              kind={summary.studentsWeeklyDelta >= 0 ? "lime" : "warn"}
              style={{ marginTop: 8, display: "inline-flex" }}
            >
              {studentsDeltaLabel}
            </Badge>
          ) : null}
        </div>
        <div className="card card-pad">
          <div className="mut3" style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Активных задач
          </div>
          <div className="stat" style={{ marginTop: 6 }}>
            {summary.activeTasks}
          </div>
          <Badge kind="purple" style={{ marginTop: 8, display: "inline-flex" }}>
            в {catalogCount} каталогах
          </Badge>
        </div>
        <div className="card card-pad">
          <div className="mut3" style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Средняя сдача
          </div>
          <div className="stat" style={{ marginTop: 6 }}>
            {summary.avgSuccess}%
          </div>
          {successDeltaLabel ? (
            <Badge
              kind={summary.successDeltaMonth >= 0 ? "lime" : "warn"}
              style={{ marginTop: 8, display: "inline-flex" }}
            >
              {successDeltaLabel}
            </Badge>
          ) : null}
        </div>
      </div>

      <div className="card card-pad">
        <div className="between" style={{ marginBottom: 16 }}>
          <b style={{ fontSize: 15 }}>Решения по дням</b>
          <select
            className="select"
            style={{ width: 140, height: 34, padding: "6px 12px", fontSize: 13 }}
            value={rangeDays}
            onChange={(e: unknown) => setRangeDays(Number(e.target.value))}
          >
            <option value={30}>30 дней</option>
            <option value={7}>7 дней</option>
          </select>
        </div>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 5, height: 140 }}>
          {bars.map((bar: unknown) => (
            <div
              key={bar.key}
              style={{
                flex: 1,
                background: bar.peak ? "var(--lime)" : "var(--purple)",
                height: `${Math.max(bar.height, bar.value ? 8 : 4)}%`,
                borderRadius: 4,
                opacity: bar.low ? 0.35 : 1,
              }}
              title={`${bar.key}: ${bar.value}`}
            />
          ))}
        </div>
        <div className="wrap" style={{ marginTop: 14, gap: 18, fontSize: 12.5, color: "var(--text-2)" }}>
          {legendDot("var(--purple)", "Принятые решения")}
          {legendDot("var(--lime)", "Пики активности")}
        </div>
      </div>

      <div className="cards2" style={{ marginTop: 16 }}>
        <div className="card card-pad">
          <b style={{ fontSize: 14 }}>Топ задач по решениям</b>
          <div className="grid" style={{ gap: 10, marginTop: 14 }}>
            {topTasks.length === 0 ? (
              <p className="muted" style={{ fontSize: 13.5 }}>
                Пока нет отправок.
              </p>
            ) : (
              topTasks.map((row, i) => (
                <div
                  key={row.task_id}
                  className="between"
                  style={{
                    fontSize: 13.5,
                    padding: "8px 0",
                    borderTop: i ? "1px solid var(--border)" : "none",
                  }}
                >
                  <span>{row.title}</span>
                  <b className="mono" style={{ color: "var(--lime)" }}>
                    {row.total_submissions}
                  </b>
                </div>
              ))
            )}
          </div>
        </div>
        <div className="card card-pad">
          <b style={{ fontSize: 14 }}>Проблемные задачи</b>
          <div className="grid" style={{ gap: 10, marginTop: 14 }}>
            {weakTasks.length === 0 ? (
              <p className="muted" style={{ fontSize: 13.5 }}>
                Недостаточно данных.
              </p>
            ) : (
              weakTasks.map((row, i) => (
                <div
                  key={row.task_id}
                  className="between"
                  style={{
                    fontSize: 13.5,
                    padding: "8px 0",
                    borderTop: i ? "1px solid var(--border)" : "none",
                  }}
                >
                  <span>{row.title}</span>
                  <Badge kind="warn">{Math.round(row.success_percent)}% сдают</Badge>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
