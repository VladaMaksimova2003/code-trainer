import { fetchAdminStatistics } from "@/admin-panel/api/admin"

import { useAsyncResource } from "@/admin-panel/hooks/useAsyncResource"

import ApPageHeader from "@/admin-panel/components/ui/ApPageHeader"

import ApStatCard from "@/admin-panel/components/ui/ApStatCard"

import { ApSpinner, ApAlert } from "@/admin-panel/components/ui/ApFeedback"

import { ApProgressBar } from "@/admin-panel/components/ui/ApPrimitives"

import { formatNumber, roleLabel, workflowStatusLabel } from "@/shared/utils/format"



export default function AnalyticsPage() {

  const { data: stats, loading, error } = useAsyncResource(() => fetchAdminStatistics(), [])



  if (loading && !stats) return <ApSpinner />



  const students = stats?.users_by_role?.student ?? 0

  const teachers = stats?.users_by_role?.teacher ?? 0

  const admins = stats?.users_by_role?.admin ?? 0



  return (

    <>

      <ApPageHeader title="Статистика системы" subtitle="Агрегированные метрики платформы" />



      <ApAlert message={error} />



      {stats ? (

        <>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 16 }}>

            <ApStatCard label="Всего пользователей" value={formatNumber(stats.users_total)} badgeKind="muted" />

            <ApStatCard label="Студентов" value={formatNumber(students)} badgeKind="lime" />

            <ApStatCard label="Преподавателей" value={formatNumber(teachers)} badgeKind="purple" />

            <ApStatCard label="Администраторов" value={formatNumber(admins)} badgeKind="purple" />

          </div>



          <div className="ap-cards2" style={{ marginBottom: 16 }}>

            <div className="ap-card ap-card-pad">

              <b style={{ fontSize: 14, display: "block", marginBottom: 14 }}>Пользователи по ролям</b>

              <div className="ap-grid" style={{ gap: 12 }}>

                {Object.entries(stats.users_by_role || {}).map(([role, count], i) => (

                  <div key={role}>

                    <div className="ap-between" style={{ fontSize: 13, marginBottom: 6 }}>

                      <span className="ap-muted">{roleLabel(role)}</span>

                      <b className="ap-mono">{formatNumber(count)}</b>

                    </div>

                    <ApProgressBar value={count} max={stats.users_total || 1} variant={i % 2 ? "lime" : "purple"} />

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

                      max={stats.assignments_total || 1}

                      variant={i % 2 ? "purple" : "lime"}

                    />

                  </div>

                ))}

              </div>

            </div>

          </div>



          <div className="ap-cards2">

            <ApStatCard

              label="Всего заданий"

              value={formatNumber(stats.assignments_total)}

              badgeKind="muted"

            />

            <ApStatCard

              label="Заявок преподавателей"

              value={formatNumber(stats.teacher_requests_pending)}

              badge="Ожидают рассмотрения"

              badgeKind="warn"

            />

          </div>

        </>

      ) : null}

    </>

  )

}


