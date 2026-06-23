import { useNavigate, useSearchParams } from "react-router-dom"
import { useEffect, useMemo, useState } from "react"
import RoleAvatar from "@/shared/ui/RoleAvatar"
import { listJoinedGroupsOverview } from "@/features/groups/api/groupsApi"
import { userHasRole } from "@/shared/api/auth"
import { getMyTeacherProfile } from "@/shared/api"
import ContribGraph from "@/features/student/ui/ContribGraph"
import StudentToxicGroupsTab from "@/features/student/ui/StudentToxicGroupsTab"
import StudentToxicSolutionsPanel from "@/features/student/ui/StudentToxicSolutionsPanel"
import StudentProfileProgressPanel from "@/features/student/ui/StudentProfileProgressPanel"
import { useProfile } from "@/shared/hooks/useProfile"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import PageHeader from "@/features/student/layout/PageHeader"
import Badge from "@/shared/ui/Badge"
import LoadingBlock from "@/shared/ui/LoadingBlock"
import {
  computePeriodDeltaPercent,
  formatDeltaBadge,
  resolveStreakDays,
} from "@/shared/utils/activityStats"

const TABS = [
  ["progress", "Прогресс"],
  ["solutions", "Мои решения"],
  ["groups", "Группы"],
]

const TAB_IDS = TABS.map(([id]) => id)

const CABINET_TAB_REDIRECT = {
  "teacher-tasks": "tasks",
  tasks: "tasks",
  analytics: "analytics",
  catalogs: "catalogs",
  "teacher-solutions": "solutions",
  "teacher-groups": "groups",
}

function normalizeTab(raw) {
  if (!raw) return "progress"
  return TAB_IDS.includes(raw) ? raw : "progress"
}

function statRow(label, value) {
  return (
    <div className="between" style={{ padding: "11px 0", borderTop: "1px solid var(--border)" }}>
      <span className="muted" style={{ fontSize: 13 }}>
        {label}
      </span>
      {typeof value === "string" ? <b>{value}</b> : value}
    </div>
  )
}

export default function ProfilePage({ user = null, onSignOut }) {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const isTeacher = userHasRole(user, "TEACHER")
  const initialTab = normalizeTab(searchParams.get("tab"))
  const [tab, setTab] = useState(initialTab)
  const [tabError, setTabError] = useState(null)
  const [groupsCount, setGroupsCount] = useState(0)
  const [teacherStats, setTeacherStats] = useState({ createdTasks: 0, createdGroups: 0 })

  const { profile, analytics, loading, analyticsLoading, error, reloadAnalytics } = useProfile({
    loadAnalytics: true,
  })

  const displayName = profile?.display_name || user?.name || "Пользователь"
  const profileRole = isTeacher ? "teacher" : "student"
  const contactEmail = profile?.email || user?.email || ""

  useEffect(() => {
    const raw = searchParams.get("tab")
    if (raw && CABINET_TAB_REDIRECT[raw] && isTeacher) {
      navigate(`/teacher/cabinet?tab=${CABINET_TAB_REDIRECT[raw]}`, { replace: true })
      return
    }
    const q = normalizeTab(raw)
    if (q !== tab) setTab(q)
  }, [searchParams, isTeacher, navigate, tab])

  useEffect(() => {
    if (tab === "progress") reloadAnalytics()
  }, [tab, reloadAnalytics])

  useEffect(() => {
    listJoinedGroupsOverview()
      .then((data) => setGroupsCount(Array.isArray(data) ? data.length : 0))
      .catch(() => setGroupsCount(0))
  }, [])

  useEffect(() => {
    if (!isTeacher) return
    getMyTeacherProfile()
      .then((data) => {
        setTeacherStats({
          createdTasks: data?.total_tasks ?? 0,
          createdGroups: Array.isArray(data?.groups) ? data.groups.length : 0,
        })
      })
      .catch(() => setTeacherStats({ createdTasks: 0, createdGroups: 0 }))
  }, [isTeacher])

  const handleTabChange = (id) => {
    setTab(id)
    setSearchParams({ tab: id }, { replace: true })
  }

  const levelLabel = analytics?.overview?.level ?? "—"
  const activityByDate = profile?.activity_by_date ?? {}
  const streakDays = useMemo(
    () => resolveStreakDays(profile, analytics),
    [profile, analytics],
  )
  const activityDelta = useMemo(
    () => computePeriodDeltaPercent(activityByDate, 30),
    [activityByDate]
  )
  const activityDeltaLabel = formatDeltaBadge(activityDelta, {
    suffix: "% к прошлому месяцу",
  })
  const aboutText = profile?.about ?? user?.about ?? ""
  const studyIdentity =
    profile?.study_identity ||
    [profile?.study_place, profile?.study_group].filter(Boolean).join(" · ") ||
    ""
  const mySubmissions = profile?.recent_submissions ?? []
  const profileReady = Boolean(profile)
  const toastError = profileReady ? tabError : error || tabError

  return (
    <LearningAppShell user={user} onSignOut={onSignOut}>
      <PageHeader
        title="Мой профиль"
        subtitle="Прогресс обучения, ваши решения и группы, в которых вы состоите."
      />

      {toastError ? (
        <div className="toast err" style={{ marginBottom: 16, maxWidth: "none" }}>
          <div className="tt">{typeof toastError === "string" ? toastError : "Ошибка"}</div>
        </div>
      ) : null}

      {loading ? (
        <LoadingBlock text="Загрузка профиля…" minHeight={200} />
      ) : profileReady ? (
        <div className="profile-page-layout">
          <aside className="card card-pad glow-card" style={{ textAlign: "center" }}>
            <RoleAvatar
              user={user}
              name={displayName}
              role={profileRole}
              size="lg"
              style={{ margin: "0 auto 12px" }}
            />
            <b style={{ fontSize: 17 }}>{displayName}</b>
            <p className="mut3" style={{ fontSize: 13, margin: "4px 0 10px" }}>
              {contactEmail}
            </p>
            {studyIdentity ? (
              <p
                className="muted"
                style={{
                  fontSize: 12.5,
                  margin: "0 0 12px",
                  lineHeight: 1.45,
                }}
              >
                {studyIdentity}
              </p>
            ) : null}
            {aboutText ? (
              <p
                className="muted"
                style={{
                  fontSize: 13,
                  lineHeight: 1.5,
                  margin: "0 0 14px",
                  textAlign: "left",
                  whiteSpace: "pre-wrap",
                }}
              >
                {aboutText}
              </p>
            ) : (
              <p className="mut3" style={{ fontSize: 12.5, margin: "0 0 14px", fontStyle: "italic" }}>
                Расскажите о себе в настройках профиля
              </p>
            )}
            {isTeacher ? (
              <Badge kind="purple" style={{ marginBottom: 6, display: "inline-flex" }}>
                Преподаватель
              </Badge>
            ) : null}
            <Badge kind="lime" style={{ marginBottom: 18 }}>
              Уровень · {levelLabel}
            </Badge>
            <div className="grid" style={{ gap: 0, textAlign: "left", marginTop: 8 }}>
              {statRow("Решено задач", String(profile.solved_tasks_count ?? 0))}
              {statRow(
                "Серия дней",
                <b style={{ color: "var(--lime)" }}>
                  {streakDays}
                  {streakDays > 0 ? " 🔥" : ""}
                </b>
              )}
              {statRow("Точность", `${profile.success_rate ?? 0}%`)}
              {statRow("Группы", String(groupsCount))}
              {isTeacher ? (
                <>
                  {statRow("Создано задач", String(teacherStats.createdTasks))}
                  {statRow("Создано групп", String(teacherStats.createdGroups))}
                </>
              ) : null}
            </div>
            <button
              type="button"
              className="btn btn-ghost btn-sm btn-full"
              style={{ marginTop: 14 }}
              onClick={() => navigate("/settings/profile")}
            >
              Редактировать профиль
            </button>
          </aside>

          <div>
            <div className="card card-pad" style={{ marginBottom: 18 }}>
              <div className="between" style={{ marginBottom: 16 }}>
                <b style={{ fontSize: 15 }}>Активность за 26 недель</b>
                {activityDeltaLabel ? (
                  <Badge kind={activityDelta >= 0 ? "purple" : "warn"}>{activityDeltaLabel}</Badge>
                ) : null}
              </div>
              <ContribGraph byDate={profile.activity_by_date} weeks={26} />
            </div>

            <div className="tabbar">
              {TABS.map(([id, label]) => (
                <button
                  key={id}
                  type="button"
                  className={tab === id ? "on" : ""}
                  onClick={() => handleTabChange(id)}
                >
                  {label}
                </button>
              ))}
            </div>

            {tab === "progress" && (
              analyticsLoading && !analytics ? (
                <LoadingBlock text="Загрузка статистики…" minHeight={160} />
              ) : (
                <StudentProfileProgressPanel analytics={analytics} />
              )
            )}
            {tab === "solutions" && (
              <StudentToxicSolutionsPanel submissions={mySubmissions} />
            )}
            {tab === "groups" && (
              <StudentToxicGroupsTab onError={setTabError} showTeacherRequest={!isTeacher} />
            )}
          </div>
        </div>
      ) : null}
    </LearningAppShell>
  )
}
