import { useState } from "react"
import ApStatCard from "@/admin-panel/components/ui/ApStatCard"
import { ApSpinner, ApAlert } from "@/admin-panel/components/ui/ApFeedback"
import { ApProgressBar, ApAvatar } from "@/admin-panel/components/ui/ApPrimitives"
import { fetchAdminStatistics, fetchTeacherRoleRequests } from "@/admin-panel/api/admin"
import { useAsyncResource } from "@/admin-panel/hooks/useAsyncResource"
import { formatNumber, roleLabel, workflowStatusLabel } from "@/shared/utils/format"
import { Link } from "react-router-dom"

const REGISTRATION_PERIODS = [
  { id: "week", label: "Неделя", title: "Регистрация пользователей за неделю" },
  { id: "month", label: "Месяц", title: "Регистрация пользователей за месяц" },
]

const ROLE_ORDER = ["student", "teacher", "admin"]

function roleProgressVariant(role) {
  if (role === "admin") return "orange"
  if (role === "student") return "lime"
  if (role === "teacher") return "purple"
  return "purple"
}

function monthBadge(count) {
  return count > 0 ? `+${formatNumber(count)} за месяц` : "0 за месяц"
}

function monthBadgeKind(role, count) {
  if (count <= 0) return "muted"
  if (role === "student") return "lime"
  if (role === "teacher") return "purple"
  if (role === "admin") return "warn"
  return count > 0 ? "lime" : "muted"
}

function registrationBarHeight(value, max) {
  if (max <= 0) return 4
  return Math.max(4, Math.round((value / max) * 100))
}

function bucketTotal(bucket) {
  return (bucket?.student ?? 0) + (bucket?.teacher ?? 0) + (bucket?.admin ?? 0)
}

function formatBucketTitle(bucket) {
  const parts = []
  if (bucket.admin > 0) parts.push(`админ: ${bucket.admin}`)
  if (bucket.teacher > 0) parts.push(`препод.: ${bucket.teacher}`)
  if (bucket.student > 0) parts.push(`студ.: ${bucket.student}`)
  const total = bucketTotal(bucket)
  if (total === 0) return "нет регистраций"
  return `${total} рег. (${parts.join(", ")})`
}

function RegistrationsChart({ buckets = [] }) {
  const maxTotal = Math.max(...buckets.map(bucketTotal), 1)

  return (
    <div className="ap-bar-chart">
      {buckets.map((bucket, i) => {
        const total = bucketTotal(bucket)
        const height = registrationBarHeight(total, maxTotal)
        return (
          <div key={i} className="ap-bar-col" title={formatBucketTitle(bucket)}>
            <div className="ap-bar-stack" style={{ height: `${height}%` }}>
              {bucket.admin > 0 ? (
                <i className="role-admin" style={{ height: `${(bucket.admin / total) * 100}%` }} />
              ) : null}
              {bucket.teacher > 0 ? (
                <i className="role-teacher" style={{ height: `${(bucket.teacher / total) * 100}%` }} />
              ) : null}
              {bucket.student > 0 ? (
                <i className="role-student" style={{ height: `${(bucket.student / total) * 100}%` }} />
              ) : null}
              {total === 0 ? <i className="role-student" style={{ height: "100%", opacity: 0.2 }} /> : null}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default function DashboardPage() {
  const [regPeriod, setRegPeriod] = useState("month")
  const statsQuery = useAsyncResource(() => fetchAdminStatistics(), [])
  const pendingQuery = useAsyncResource(() => fetchTeacherRoleRequests("pending"), [])

  const stats = statsQuery.data
  const pending = pendingQuery.data || []

  if (statsQuery.loading && !stats) return <ApSpinner />

  const students = stats?.users_by_role?.student ?? 0
  const teachers = stats?.users_by_role?.teacher ?? 0
  const admins = stats?.users_by_role?.admin ?? 0
  const newByRole = stats?.users_new_last_month_by_role ?? {}
  const registrations = stats?.registrations_by_period?.[regPeriod] ?? []
  const periodMeta = REGISTRATION_PERIODS.find((p) => p.id === regPeriod) ?? REGISTRATION_PERIODS[1]

  const sortedRoles = Object.entries(stats?.users_by_role || {}).sort(([a], [b]) => {
    const ai = ROLE_ORDER.indexOf(a)
    const bi = ROLE_ORDER.indexOf(b)
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })

  const tasksTotal = Math.max(
    stats?.assignments_total ?? 0,
    stats?.curriculum_catalog_tasks ?? 0,
  )

  return (
    <>
      <ApAlert message={statsQuery.error} />
      <ApAlert message={pendingQuery.error} kind="info" />

      {stats ? (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 16 }}>
            <ApStatCard
              label="Всего пользователей"
              value={formatNumber(stats.users_total)}
              badge={monthBadge(stats.users_new_last_month ?? 0)}
              badgeKind={monthBadgeKind(null, stats.users_new_last_month ?? 0)}
            />
            <ApStatCard
              label="Студентов"
              value={formatNumber(students)}
              badge={monthBadge(newByRole.student ?? 0)}
              badgeKind={monthBadgeKind("student", newByRole.student ?? 0)}
            />
            <ApStatCard
              label="Преподавателей"
              value={formatNumber(teachers)}
              badge={monthBadge(newByRole.teacher ?? 0)}
              badgeKind={monthBadgeKind("teacher", newByRole.teacher ?? 0)}
            />
            <ApStatCard
              label="Администраторов"
              value={formatNumber(admins)}
              badge={monthBadge(newByRole.admin ?? 0)}
              badgeKind={monthBadgeKind("admin", newByRole.admin ?? 0)}
            />
          </div>

          <div style={{ marginBottom: 16, maxWidth: 320 }}>
            <ApStatCard
              label="Всего задач"
              value={formatNumber(tasksTotal)}
              badge={
                stats.tasks_new_last_30_days > 0
                  ? `+${formatNumber(stats.tasks_new_last_30_days)} за месяц`
                  : "0 за месяц"
              }
              badgeKind={stats.tasks_new_last_30_days > 0 ? "lime" : "muted"}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 16, alignItems: "start" }}>
            <div className="ap-card ap-card-pad">
              <div className="between" style={{ marginBottom: 16 }}>
                <b style={{ fontSize: 15 }}>{periodMeta.title}</b>
                <select
                  className="select"
                  style={{ width: 140, height: 34, padding: "6px 12px", fontSize: 13 }}
                  value={regPeriod}
                  onChange={(e) => setRegPeriod(e.target.value)}
                >
                  {REGISTRATION_PERIODS.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>
              <RegistrationsChart buckets={registrations} />
            </div>

            <div className="ap-card ap-card-pad">
              <div className="ap-between" style={{ marginBottom: 14 }}>
                <b style={{ fontSize: 15 }}>Заявки преподавателей</b>
                <Link to="/admin/teacher-requests" style={{ fontSize: 12.5, color: "var(--lime)" }}>
                  Все →
                </Link>
              </div>
              {pending.length === 0 ? (
                <p className="ap-muted" style={{ fontSize: 13, margin: 0 }}>
                  Новых заявок нет.
                </p>
              ) : (
                <div className="ap-grid" style={{ gap: 10 }}>
                  {pending.slice(0, 3).map((r) => (
                    <div key={r.id} className="ap-between">
                      <div className="ap-row" style={{ gap: 10 }}>
                            <ApAvatar name={r.user_name} role="teacher" />
                        <div>
                          <div style={{ fontSize: 13.5, fontWeight: 600 }}>{r.user_name || "—"}</div>
                          <div className="ap-mut3" style={{ fontSize: 12 }}>
                            {r.user_email || "—"}
                          </div>
                        </div>
                      </div>
                      <Link to="/admin/teacher-requests" className="ap-btn ap-btn-primary ap-btn-sm">
                        →
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="ap-cards2" style={{ marginTop: 16, marginBottom: 16 }}>
            <div className="ap-card ap-card-pad">
              <b style={{ fontSize: 14, display: "block", marginBottom: 14 }}>Пользователи по ролям</b>
              <div className="ap-grid" style={{ gap: 12 }}>
                {sortedRoles.map(([role, count]) => (
                  <div key={role}>
                    <div className="ap-between" style={{ fontSize: 13, marginBottom: 6 }}>
                      <span className="ap-muted">{roleLabel(role)}</span>
                      <b className="ap-mono">{formatNumber(count)}</b>
                    </div>
                    <ApProgressBar
                      value={count}
                      max={stats.users_total || 1}
                      variant={roleProgressVariant(role)}
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className="ap-card ap-card-pad">
              <b style={{ fontSize: 14, display: "block", marginBottom: 14 }}>Задания по статусу</b>
              <div className="ap-grid" style={{ gap: 12 }}>
                {Object.entries(stats.assignments_by_status || {}).map(([status, count], i) => (
                  <div key={status}>
                    <div className="ap-between" style={{ fontSize: 13, marginBottom: 6 }}>
                      <span className="ap-muted">{workflowStatusLabel(status)}</span>
                      <b className="ap-mono">{formatNumber(count)}</b>
                    </div>
                    <ApProgressBar
                      value={count}
                      max={tasksTotal || 1}
                      variant={i % 2 ? "purple" : "lime"}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      ) : null}
    </>
  )
}
