import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { getMyGroupWorkspace } from "@/features/groups/api/groupsApi"
import StudentGroupCatalogsToxic from "@/features/student/ui/StudentGroupCatalogsToxic"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import PageHeader from "@/features/student/layout/PageHeader"
import Badge from "@/shared/ui/Badge"
import ProfileLink from "@/shared/ui/ProfileLink"
import RoleAvatar from "@/shared/ui/RoleAvatar"

export default function GroupDetailPage({ user = null, onSignOut = null }) {
  const { groupId } = useParams()
  const navigate = useNavigate()
  const [workspace, setWorkspace] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError("")
    getMyGroupWorkspace(Number(groupId))
      .then((data) => {
        if (!cancelled) setWorkspace(data)
      })
      .catch((err) => {
        if (!cancelled) {
          setWorkspace(null)
          setError(
            err?.response?.data?.detail ||
              err?.message ||
              "Не удалось загрузить группу"
          )
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [groupId])

  const group = workspace?.group
  const solved =
    workspace?.catalogs?.reduce((acc, cat) => {
      return acc + (cat.tasks?.filter((t) => t.status === "solved").length ?? 0)
    }, 0) ?? 0
  const total =
    workspace?.catalogs?.reduce((acc, cat) => acc + (cat.tasks?.length ?? 0), 0) ?? 0

  return (
    <LearningAppShell
      user={user}
      onSignOut={onSignOut}
    >
      <button
        type="button"
        className="btn btn-ghost btn-sm"
        style={{ marginBottom: 14 }}
        onClick={() => navigate("/student/profile?tab=groups")}
      >
        ← Все группы
      </button>

      {loading ? <p className="muted">Загрузка…</p> : null}
      {!loading && error ? (
        <div className="toast err" style={{ maxWidth: "none" }}>
          {error}
        </div>
      ) : null}

      {!loading && workspace && group ? (
        <>
          <PageHeader
            title={group.name}
            subtitle={
              workspace.teacher?.name
                ? `Преподаватель: ${workspace.teacher.name}`
                : "Группа преподавателя"
            }
            right={[<Badge key="p" kind="lime">{`Решено ${solved} / ${total}`}</Badge>]}
          />

          <div className="card card-pad" style={{ marginBottom: 18 }}>
            <div className="between">
              <div className="row">
                <RoleAvatar
                  user={{ id: workspace.teacher?.id }}
                  name={workspace.teacher?.name}
                  role="teacher"
                  size="lg"
                  style={{ width: 48, height: 48, fontSize: 18, borderRadius: 14 }}
                />
                <div>
                  <ProfileLink userId={workspace.teacher?.id}>
                    <b>{workspace.teacher?.name || "Преподаватель"}</b>
                  </ProfileLink>
                  <p className="mut3" style={{ margin: "2px 0 0", fontSize: 12.5 }}>
                    Преподаватель группы
                  </p>
                </div>
              </div>
            </div>
          </div>

          <StudentGroupCatalogsToxic catalogs={workspace.catalogs} groupId={groupId} />
        </>
      ) : null}
    </LearningAppShell>
  )
}
