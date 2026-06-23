interface StudentToxicGroupsTabProps {
  onError: (...args: unknown[]) => unknown
  showTeacherRequest?: boolean
}

import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "@/shared/ui/toast"
import { joinGroupByCode, listJoinedGroupsOverview } from "@/features/groups/api/groupsApi"
import { openJoinedGroupLearn } from "@/features/groups/routing/joinedGroupLearnPath"
import { requestTeacherRole } from "@/shared/api"
import Badge from "@/shared/ui/Badge"
import EmptyState from "@/shared/ui/EmptyState"
import ProfileLink from "@/shared/ui/ProfileLink"

export default function StudentToxicGroupsTab({

  onError,
  showTeacherRequest = true,

}: StudentToxicGroupsTabProps) {
  const navigate = useNavigate()
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [code, setCode] = useState("")
  const [joining, setJoining] = useState(false)

  const loadGroups = async () => {
    setLoading(true)
    onError?.(null)
    try {
      const data = await listJoinedGroupsOverview()
      setGroups(Array.isArray(data) ? data : [])
    } catch (err) {
      setGroups([])
      onError?.(
        err?.response?.data?.detail || err?.message || "Не удалось загрузить группы"
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadGroups()
  }, [])

  const handleJoin = async () => {
    const trimmed = code.trim()
    if (!trimmed) return
    setJoining(true)
    onError?.(null)
    try {
      const group = await joinGroupByCode(trimmed)
      setCode("")
      toast.push({ kind: "lime", title: "Вы вступили в группу", body: group.name })
      await loadGroups()
      openJoinedGroupLearn(navigate, group.id)
    } catch (err) {
      const message =
        err?.response?.data?.detail || err?.message || "Код не найден. Проверьте написание."
      onError?.(message)
      toast.error("Не удалось вступить в группу", message)
    } finally {
      setJoining(false)
    }
  }

  const handleTeacherRequest = async () => {
    try {
      await requestTeacherRole()
      toast.push({
        kind: "lime",
        title: "Заявка отправлена",
        body: "Ожидайте ответа администратора",
      })
    } catch (err) {
      const message =
        err?.response?.data?.detail || err?.message || "Не удалось отправить заявку"
      onError?.(message)
      toast.error("Не удалось отправить заявку", message)
    }
  }

  const filteredGroups = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return groups
    return groups.filter(
      (g: unknown) =>
        g.name?.toLowerCase().includes(q) ||
        g.teacher?.name?.toLowerCase().includes(q)
    )
  }, [groups, search])

  const joinControls = (
    <div className="row">
      <input
        className="input mono"
        style={{ width: 160, height: 38 }}
        placeholder="GRP-XXXX"
        value={code}
        onChange={(e: unknown) => setCode(e.target.value.toUpperCase())}
      />
      <button
        type="button"
        className="btn btn-primary btn-sm"
        onClick={handleJoin}
        disabled={joining}
      >
        {joining ? "…" : "Вступить по коду"}
      </button>
    </div>
  )

  return (
    <div>
      <div className="between" style={{ marginBottom: 16, flexWrap: "wrap", gap: 12 }}>
        <input
          className="input"
          style={{ width: 280, height: 38 }}
          placeholder="Поиск по группам…"
          value={search}
          onChange={(e: unknown) => setSearch(e.target.value)}
        />
        {joinControls}
      </div>

      {loading ? (
        <p className="muted">Загрузка групп…</p>
      ) : groups.length === 0 ? (
        <div className="card card-pad">
          <EmptyState
            icon="👥"
            title="Групп пока нет"
            text="Вступите в группу по инвайт-коду преподавателя — курсы и задания появятся здесь."
          />
        </div>
      ) : filteredGroups.length === 0 ? (
        <div className="card card-pad">
          <EmptyState
            icon="⌕"
            title="Ничего не найдено"
            text="Попробуйте изменить поисковый запрос."
          />
        </div>
      ) : (
        <div className="cards2">
          {filteredGroups.map((g, i) => {
            const progress =
              g.task_count > 0
                ? Math.round((g.solved_count / g.task_count) * 100)
                : g.avg_progress ?? 0
            const pp = i % 2 === 1
            return (
              <div
                key={g.id}
                className={`course-card${pp ? " pp" : ""}`}
                onClick={() => void openJoinedGroupLearn(navigate, g.id)}
                onKeyDown={(e: unknown) =>
                  e.key === "Enter" && void openJoinedGroupLearn(navigate, g.id)
                }
                role="button"
                tabIndex={0}
              >
                <div className="between">
                  <b style={{ fontSize: 15 }}>{g.name}</b>
                  <Badge kind={pp ? "purple" : "lime"}>Активна</Badge>
                </div>
                <p className="muted" style={{ fontSize: 13, margin: "8px 0 14px" }}>
                  Преподаватель:{" "}
                  {g.teacher?.id ? (
                    <ProfileLink
                      userId={g.teacher.id}
                      className="t-name"
                      onClick={(e: unknown) => e.stopPropagation()}
                    >
                      {g.teacher.name || "—"}
                    </ProfileLink>
                  ) : (
                    "—"
                  )}{" "}
                  · {g.students ?? g.student_count ?? "—"} студентов
                </p>
                <div className={`progress ${pp ? "pp" : ""}`}>
                  <i style={{ width: `${progress}%` }} />
                </div>
                <p className="mut3" style={{ fontSize: 12, margin: "8px 0 0" }}>
                  Решено {progress}% задач курса
                </p>
              </div>
            )
          })}
        </div>
      )}

      {showTeacherRequest ? (
        <div className="note" style={{ marginTop: 18 }}>
          <b>Хотите стать преподавателем? </b>
          Подайте заявку — администратор рассмотрит её в течение 1–2 дней.{" "}
          <button
            type="button"
            className="btn btn-secondary btn-xs"
            style={{ marginLeft: 8 }}
            onClick={handleTeacherRequest}
          >
            Подать заявку
          </button>
        </div>
      ) : null}
    </div>
  )
}
