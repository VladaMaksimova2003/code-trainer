interface TeacherToxicGroupsPanelProps {
  groups?: unknown[]
  teacherUserId?: unknown | null
  canManage?: boolean
  newGroupName: unknown
  setNewGroupName: unknown
  onCreateGroup: (...args: unknown[]) => unknown
  inviteByGroupId: unknown
  invitingGroupId: unknown
  onGenerateInvite: (...args: unknown[]) => unknown
  onCopyInvite: (...args: unknown[]) => unknown
  onDeleteGroup?: (...args: unknown[]) => unknown
  deletingGroupId?: unknown
}

import { useCallback, useEffect, useState } from "react"
import EmptyState from "@/shared/ui/EmptyState"
import Modal from "@/features/student/layout/Modal"
import { getGroupDashboard } from "@/features/groups/api/groupsApi"
import ProfileLink from "@/shared/ui/ProfileLink"
import ProfileSectionTitle from "@/shared/ui/ProfileSectionTitle"
import RoleAvatar from "@/shared/ui/RoleAvatar"
import { formatRelativeActivity } from "@/shared/utils/format"

function GroupSidebarButton({ group, active, memberCount, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        border: active ? "1px solid rgba(139, 83, 254, 0.4)" : "1px solid var(--border)",
        background: active ? "var(--purple-soft)" : "transparent",
        borderRadius: 10,
        padding: 11,
        textAlign: "left",
        cursor: "pointer",
        width: "100%",
      }}
    >
      <b style={{ fontSize: 13.5, color: active ? "#b89bff" : "var(--text)" }}>{group.name}</b>
      <div className="mut3" style={{ fontSize: 12, marginTop: 2 }}>
        {memberCount} {memberCount === 1 ? "студент" : memberCount < 5 ? "студента" : "студентов"}
      </div>
    </button>
  )
}

function AddGroupCard({ onClick }) {
  return (
    <div
      className="course-card course-card--add"
      style={{ borderStyle: "dashed" }}
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e: unknown) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onClick()
        }
      }}
    >
      <div className="catalog-add-inner">
        <div style={{ fontSize: 28, color: "var(--text-3)" }}>+</div>
        <span className="muted" style={{ fontSize: 13.5 }}>
          Новая группа
        </span>
      </div>
    </div>
  )
}

export default function TeacherToxicGroupsPanel({

  groups = [],
  teacherUserId = null,
  canManage = false,
  newGroupName,
  setNewGroupName,
  onCreateGroup,
  inviteByGroupId,
  invitingGroupId,
  onGenerateInvite,
  onCopyInvite,
  onDeleteGroup,
  deletingGroupId = null,

}: TeacherToxicGroupsPanelProps) {
  const [activeGroupId, setActiveGroupId] = useState(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [catalogId, setCatalogId] = useState("")
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (groups.length === 0) {
      setActiveGroupId(null)
      return
    }
    if (!activeGroupId || !groups.some((g: unknown) => g.id === activeGroupId)) {
      setActiveGroupId(groups[0].id)
    }
  }, [groups, activeGroupId])

  const activeGroup = groups.find((g: unknown) => g.id === activeGroupId) ?? null
  const activeInvite = activeGroup ? inviteByGroupId[activeGroup.id] : null

  const loadDashboard = useCallback(async () => {
    if (!activeGroupId) {
      setDashboard(null)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const params = catalogId ? { catalog_id: Number(catalogId) } : {}
      const data = await getGroupDashboard(activeGroupId, params)
      setDashboard(data)
    } catch (err) {
      setDashboard(null)
      setError(err?.response?.data?.detail || err?.message || "Не удалось загрузить группу")
    } finally {
      setLoading(false)
    }
  }, [activeGroupId, catalogId])

  useEffect(() => {
    setCatalogId("")
  }, [activeGroupId])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

  useEffect(() => {
    if (!canManage || !activeGroup || activeInvite || invitingGroupId === activeGroup.id) return
    onGenerateInvite?.(activeGroup, { silent: true })
  }, [activeGroup, activeInvite, canManage, invitingGroupId, onGenerateInvite])

  const openCreate = () => setCreateOpen(true)
  const closeCreate = () => {
    setCreateOpen(false)
    setNewGroupName("")
  }

  const handleCreate = async (event: unknown) => {
    await onCreateGroup?.(event)
    closeCreate()
  }

  const createModal = (
    <Modal
      open={createOpen}
      onClose={closeCreate}
      title="Новая группа"
      footer={
        <>
          <button type="button" className="btn btn-ghost btn-sm" onClick={closeCreate}>
            Отмена
          </button>
          <button type="submit" form="create-group-form" className="btn btn-primary btn-sm">
            Создать группу
          </button>
        </>
      }
    >
      <form id="create-group-form" className="grid" style={{ gap: 12 }} onSubmit={handleCreate}>
        <input
          className="input"
          placeholder="Название группы"
          value={newGroupName}
          onChange={(e: unknown) => setNewGroupName(e.target.value)}
          required
        />
      </form>
    </Modal>
  )

  if (groups.length === 0 && !canManage) {
    return (
      <div className="card card-pad">
        <EmptyState
          icon="👥"
          title="Групп пока нет"
          text="Создайте группу, чтобы назначать каталоги и приглашать студентов."
        />
      </div>
    )
  }

  if (groups.length === 0 && canManage) {
    return (
      <>
        <div className="teacher-catalogs-panel">
          <div className="cards3 cards3--catalogs">
            <AddGroupCard onClick={openCreate} />
          </div>
        </div>
        {createModal}
      </>
    )
  }

  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "230px 1fr", gap: 18, alignItems: "start" }}>
        <aside>
          <div className="grid" style={{ gap: 8 }}>
            {groups.map((group: unknown) => (
              <GroupSidebarButton
                key={group.id}
                group={group}
                active={group.id === activeGroupId}
                memberCount={group.member_count ?? 0}
                onClick={() => setActiveGroupId(group.id)}
              />
            ))}
            {canManage ? <AddGroupCard onClick={openCreate} /> : null}
          </div>
        </aside>

        <div>
          {loading && !dashboard ? (
            <p className="muted">Загрузка группы…</p>
          ) : error && !dashboard ? (
            <p className="muted">{error}</p>
          ) : activeGroup ? (
            <>
              <div className="card card-pad" style={{ marginBottom: 16 }}>
                <div className="between">
                  <div>
                    <b style={{ fontSize: 16 }}>{activeGroup.name}</b>
                    {activeInvite ? (
                      <p className="mut3" style={{ fontSize: 12.5, margin: "4px 0 0" }}>
                        Инвайт-код:{" "}
                        <span className="mono" style={{ color: "var(--lime)" }}>
                          {activeInvite.code}
                        </span>
                      </p>
                    ) : canManage ? (
                      <p className="mut3" style={{ fontSize: 12.5, margin: "4px 0 0" }}>
                        {invitingGroupId === activeGroup.id
                          ? "Создание инвайт-кода…"
                          : "Инвайт-код не создан"}
                      </p>
                    ) : null}
                  </div>
                  <div className="row" style={{ gap: 8 }}>
                    {activeInvite ? (
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => onCopyInvite?.(activeInvite.code, activeGroup.name)}
                      >
                        ⧉ Копировать код
                      </button>
                    ) : canManage ? (
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        disabled={invitingGroupId === activeGroup.id}
                        onClick={() => onGenerateInvite?.(activeGroup)}
                      >
                        Инвайт-код
                      </button>
                    ) : null}
                    {canManage ? (
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        style={{ color: "var(--danger)" }}
                        disabled={deletingGroupId === activeGroup.id}
                        onClick={() => onDeleteGroup?.(activeGroup)}
                      >
                        {deletingGroupId === activeGroup.id ? "Удаление…" : "Удалить"}
                      </button>
                    ) : null}
                  </div>
                </div>
              </div>

              {(dashboard?.catalogs?.length ?? 0) > 0 ? (
                <div className="wrap" style={{ marginBottom: 14, gap: 8 }}>
                  <span
                    className={`chip${catalogId === "" ? " on pp" : ""}`}
                    role="button"
                    tabIndex={0}
                    onClick={() => setCatalogId("")}
                    onKeyDown={(e: unknown) => e.key === "Enter" && setCatalogId("")}
                  >
                    Все каталоги
                  </span>
                  {dashboard.catalogs.map((cat: unknown) => (
                    <span
                      key={cat.id}
                      className={`chip${String(catalogId) === String(cat.id) ? " on pp" : ""}`}
                      role="button"
                      tabIndex={0}
                      onClick={() => setCatalogId(String(cat.id))}
                      onKeyDown={(e: unknown) => e.key === "Enter" && setCatalogId(String(cat.id))}
                    >
                      {cat.title}
                    </span>
                  ))}
                </div>
              ) : null}

              {(dashboard?.student_summaries?.length ?? 0) > 0 ? (
                <ProfileSectionTitle>Прогресс студентов</ProfileSectionTitle>
              ) : null}

              <div className="card card-pad">
                {(dashboard?.student_summaries?.length ?? 0) === 0 ? (
                  <EmptyState
                    icon="👥"
                    title="Студентов пока нет"
                    text="Поделитесь инвайт-кодом группы — студенты появятся в списке прогресса."
                  />
                ) : (
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Студент</th>
                        <th>Решено</th>
                        <th>Прогресс</th>
                        <th>Активность</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dashboard.student_summaries.map((row: unknown) => (
                        <tr key={row.student_id} className="no-hover">
                          <td>
                            <div className="row" style={{ gap: 9 }}>
                              <RoleAvatar
                                user={{ id: row.student_id }}
                                name={row.student_name}
                                role="student"
                                size="sm"
                                style={{ width: 28, height: 28, fontSize: 12 }}
                              />
                              <ProfileLink
                                userId={row.student_id}
                                teacherId={teacherUserId ?? dashboard?.group?.teacher_id}
                              >
                                {row.student_name}
                              </ProfileLink>
                            </div>
                          </td>
                          <td className="mono">
                            {row.solved_count} / {row.total_tasks}
                          </td>
                          <td style={{ minWidth: 140 }}>
                            <div className="progress pp">
                              <i style={{ width: `${row.progress_percent || 0}%` }} />
                            </div>
                          </td>
                          <td className="muted">{formatRelativeActivity(row.last_activity_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </>
          ) : null}
        </div>
      </div>
      {createModal}
    </>
  )
}
