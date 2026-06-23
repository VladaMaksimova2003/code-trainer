import { useEffect, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"
import { getUserProfile } from "@/features/users/api/userProfileApi"
import TeacherPublicProfileView from "@/features/users/ui/TeacherPublicProfileView"
import StudentTeacherProfileView from "@/features/users/ui/StudentTeacherProfileView"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import { userHasRole } from "@/shared/api/auth"

export default function UserProfilePage({ user = null, onSignOut = null }) {
  const { userId } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const teacherIdParam = searchParams.get("teacherId")
  const teacherId = teacherIdParam ? Number(teacherIdParam) : null
  const viewerIsTeacher = userHasRole(user, "TEACHER")

  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const isSelf = Number(userId) === user?.id && !teacherId

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError("")
    getUserProfile(Number(userId), { teacherId })
      .then((data) => {
        if (!cancelled) setProfile(data)
      })
      .catch((err) => {
        if (!cancelled) {
          setProfile(null)
          setError(
            err?.response?.data?.detail ||
              err?.message ||
              "Не удалось загрузить профиль"
          )
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [userId, teacherId])

  const title =
    profile?.display_name || profile?.full_name || (loading ? "Профиль" : "Пользователь")

  return (
    <LearningAppShell user={user} onSignOut={onSignOut}>
      <button
        type="button"
        className="btn btn-ghost btn-sm"
        style={{ marginBottom: 14 }}
        onClick={() => navigate(-1)}
      >
        ← Назад
      </button>

      {loading ? <p className="muted">Загрузка…</p> : null}
      {!loading && error ? (
        <div className="toast err" style={{ maxWidth: "none" }}>
          {error}
        </div>
      ) : null}

      {!loading && profile?.kind === "teacher" ? (
        <TeacherPublicProfileView
          data={profile}
          viewerIsOwner={profile.is_own_profile || Number(userId) === user?.id}
        />
      ) : null}

      {!loading && profile?.kind === "student" ? (
        <StudentTeacherProfileView
          data={profile}
          viewerUser={user}
          viewerIsTeacher={viewerIsTeacher}
        />
      ) : null}

      {isSelf ? (
        <p className="muted" style={{ fontSize: 13, marginTop: 16 }}>
          Это ваш профиль.{" "}
          <Link to="/settings/profile">Редактировать в настройках</Link>
        </p>
      ) : null}
    </LearningAppShell>
  )
}
