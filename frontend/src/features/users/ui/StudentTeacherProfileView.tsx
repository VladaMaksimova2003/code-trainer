interface StudentTeacherProfileViewProps {
  data: unknown
  viewerUser: unknown
  viewerIsTeacher: unknown
}

import { Link } from "react-router-dom"
import Badge from "@/shared/ui/Badge"
import SkillsProgressCard from "@/features/users/ui/SkillsProgressCard"
import StudentTeacherProgressPanel from "@/features/users/ui/StudentTeacherProgressPanel"
import RoleAvatar from "@/shared/ui/RoleAvatar"
import { formatRelativeActivity } from "@/shared/utils/format"

function SidebarStat({ label, value, valueStyle }) {
  return (
    <div className="profile-sidebar-stat between">
      <span className="muted" style={{ fontSize: 13 }}>
        {label}
      </span>
      {typeof value === "string" || typeof value === "number" ? (
        <b style={valueStyle}>{value}</b>
      ) : (
        value
      )}
    </div>
  )
}

const LEVEL_CAPITALIZE = {
  начальный: "Junior",
  средний: "Middle",
  продвинутый: "Senior",
}

export default function StudentTeacherProfileView({

  data,
  viewerUser,
  viewerIsTeacher,

}: StudentTeacherProfileViewProps) {
  const summary = data.summary || {}
  const teacherId = data.teacher?.id
  const canManageAsTeacher =
    viewerIsTeacher && teacherId != null && viewerUser?.id === teacherId

  const levelRaw = data.level || "начальный"
  const levelBadge = `Уровень · ${LEVEL_CAPITALIZE[levelRaw] || levelRaw}`

  return (
    <div className="profile-page">
      <div
        className="profile-student-layout"
        style={{
          gridTemplateColumns: canManageAsTeacher
            ? "minmax(0, 1fr)"
            : "260px minmax(0, 1fr)",
        }}
      >
        {!canManageAsTeacher ? (
          <aside className="card card-pad glow-card profile-student-sidebar">
            <RoleAvatar
              user={{ id: data.user_id }}
              name={data.display_name}
              role="student"
              size="lg"
              style={{
                margin: "0 auto 12px",
                width: 72,
                height: 72,
                borderRadius: 16,
                fontSize: 24,
              }}
            />
            <b style={{ fontSize: 17, display: "block", textAlign: "center" }}>
              {data.display_name}
            </b>
            <p className="mut3" style={{ fontSize: 13, margin: "4px 0 10px", textAlign: "center" }}>
              {data.handle || "@student"}
              {" · "}Студент
            </p>
            <Badge kind="lime" style={{ marginBottom: 16, display: "inline-flex" }}>
              {levelBadge}
            </Badge>

            <div className="profile-sidebar-stats">
              <SidebarStat label="Решено задач" value={summary.solved_count ?? 0} />
              <SidebarStat
                label="Серия дней"
                value={
                  <b style={{ color: "var(--lime)" }}>
                    {summary.streak_days ?? 0}
                    {(summary.streak_days ?? 0) > 0 ? " 🔥" : ""}
                  </b>
                }
              />
              <SidebarStat
                label="Точность"
                value={`${summary.success_rate ?? 0}%`}
              />
              <SidebarStat
                label="Группа"
                value={data.primary_group || "—"}
                valueStyle={{ color: "#b89bff" }}
              />
              <SidebarStat
                label="Был(а) недавно"
                value={
                  summary.last_activity_at
                    ? formatRelativeActivity(summary.last_activity_at)
                    : "—"
                }
              />
            </div>

            {data.teacher ? (
              <p className="muted" style={{ fontSize: 12.5, marginTop: 14, textAlign: "center" }}>
                Преподаватель:{" "}
                <Link to={`/users/${data.teacher.id}`} className="t-name">
                  {data.teacher.name}
                </Link>
              </p>
            ) : null}
          </aside>
        ) : (
          <div className="card card-pad profile-teacher-student-header">
            <div className="row" style={{ gap: 14, alignItems: "flex-start" }}>
              <RoleAvatar
                user={{ id: data.user_id }}
                name={data.display_name}
                role="student"
                size="lg"
                style={{ width: 56, height: 56, borderRadius: 14 }}
              />
              <div style={{ flex: 1 }}>
                <h1 style={{ fontSize: 20, margin: "0 0 6px" }}>{data.display_name}</h1>
                <p className="mut3" style={{ fontSize: 13 }}>
                  {data.handle} · Студент · {levelBadge}
                </p>
                {data.primary_group ? (
                  <p className="muted" style={{ fontSize: 13, marginTop: 8 }}>
                    Группа: <b style={{ color: "#b89bff" }}>{data.primary_group}</b>
                  </p>
                ) : null}
              </div>
              <div className="profile-stat-row profile-stat-row--compact">
                <div>
                  <div className="profile-stat-value" style={{ fontSize: 20 }}>
                    {summary.solved_count ?? 0}
                  </div>
                  <div className="profile-stat-label">Решено</div>
                </div>
                <div>
                  <div className="profile-stat-value" style={{ fontSize: 20 }}>
                    {summary.success_rate ?? 0}%
                  </div>
                  <div className="profile-stat-label">Точность</div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="profile-student-main grid" style={{ gap: 18 }}>
          <SkillsProgressCard skills={data.skills ?? []} />
          {canManageAsTeacher ? (
            <StudentTeacherProgressPanel
              catalogs={data.catalogs}
              canManageAsTeacher={canManageAsTeacher}
            />
          ) : null}
        </div>
      </div>
    </div>
  )
}
