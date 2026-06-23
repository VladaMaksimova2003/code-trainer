import { useNavigate } from "react-router-dom"
import { useEffect, useState } from "react"
import { joinGroupByCode, listJoinedGroupsOverview } from "@/features/groups/api/groupsApi"
import { openJoinedGroupLearn } from "@/features/groups/routing/joinedGroupLearnPath"
import { formatDateTime } from "@/shared/utils/format"
import { Button, Card, Field, Input, Progress } from "@/shared/ui"

export default function StudentProfileGroupsTab({ onError, onSuccess }) {
  const navigate = useNavigate()
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [inviteCode, setInviteCode] = useState("")
  const [joining, setJoining] = useState(false)

  const loadGroups = async () => {
    setLoading(true)
    onError?.(null)
    try {
      const data = await listJoinedGroupsOverview()
      setGroups(data)
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

  const handleJoinGroup = async (event: unknown) => {
    event.preventDefault()
    if (!inviteCode.trim()) return
    setJoining(true)
    onError?.(null)
    onSuccess?.(null)
    try {
      const group = await joinGroupByCode(inviteCode.trim())
      setInviteCode("")
      onSuccess?.(`Вы вступили в группу «${group.name}»`)
      await loadGroups()
      openJoinedGroupLearn(navigate, group.id)
    } catch (err) {
      onError?.(
        err?.response?.data?.detail || err?.message || "Не удалось вступить в группу"
      )
    } finally {
      setJoining(false)
    }
  }

  return (
    <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_18rem]">
      <div>
        {loading ? (
          <p className="text-sm text-ink-faint">Загрузка групп...</p>
        ) : groups.length === 0 ? (
          <p className="text-sm text-ink-muted">
            Вы пока не состоите в группах. Вступите по инвайт-коду справа.
          </p>
        ) : (
          <ul className="space-y-3">
            {groups.map((group: unknown) => {
              const progress =
                group.task_count > 0
                  ? Math.round((group.solved_count / group.task_count) * 100)
                  : 0
              return (
                <li key={group.id}>
                  <button
                    type="button"
                    onClick={() => void openJoinedGroupLearn(navigate, group.id)}
                    className="w-full rounded-lg border border-border bg-surface px-4 py-3 text-left shadow-card transition hover:-translate-y-0.5 hover:border-lime/70 hover:shadow-glow-lime"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="min-w-0">
                        <h3 className="font-semibold text-ink">{group.name}</h3>
                        <p className="mt-1 text-sm text-ink-muted">
                          Преподаватель: {group.teacher?.name || "—"}
                        </p>
                        <p className="mt-1 text-xs text-ink-faint">
                          {group.catalog_count} каталогов · {group.task_count} заданий ·
                          решено {group.solved_count}
                        </p>
                      </div>
                      <span className="shrink-0 text-lg font-bold text-lime">
                        {progress}%
                      </span>
                    </div>
                    <Progress value={progress} className="mt-3" />
                    {group.deadline_alert && (
                      <p
                        className={`text-xs mt-2 ${
                          group.deadline_alert.level === "urgent"
                            ? "text-danger"
                            : "text-warning"
                        }`}
                      >
                        Дедлайн «{group.deadline_alert.catalog_title}»:{" "}
                        {formatDateTime(group.deadline_alert.deadline_at)}
                      </p>
                    )}
                  </button>
                </li>
              )
            })}
          </ul>
        )}
      </div>

      <Card as="form" onSubmit={handleJoinGroup} className="h-fit space-y-3">
        <h2 className="text-sm font-semibold text-ink">Вступить в группу</h2>
        <Field label="Инвайт-код">
          <Input
            placeholder="ABC-123"
            value={inviteCode}
            onChange={(event: unknown) => setInviteCode(event.target.value)}
            className="font-mono"
            required
          />
        </Field>
        <Button type="submit" disabled={joining}>
          {joining ? "Вступление..." : "Вступить"}
        </Button>
      </Card>
    </section>
  )
}
