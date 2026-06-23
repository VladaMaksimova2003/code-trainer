import { useSearchParams } from "react-router-dom"
import { useEffect, useMemo, useState } from "react"
import TeacherToxicTasksPanel from "@/features/teacher/ui/TeacherToxicTasksPanel"
import TeacherToxicCatalogsPanel from "@/features/teacher/ui/TeacherToxicCatalogsPanel"
import TeacherToxicAnalyticsPanel from "@/features/teacher/ui/TeacherToxicAnalyticsPanel"
import TeacherToxicSolutionsPanel from "@/features/teacher/ui/TeacherToxicSolutionsPanel"
import TeacherToxicGroupsPanel from "@/features/teacher/ui/TeacherToxicGroupsPanel"
import TeacherSupportInboxPanel from "@/features/teacher/support/TeacherSupportInboxPanel"
import { TeacherPlatformCourseEditorModal } from "@/features/teacher/ui/TeacherPlatformCourseEditorModal"
import { useTeacherProfile } from "@/features/teacher-profile/hooks/useTeacherProfile"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import PageHeader from "@/features/student/layout/PageHeader"
import ConfirmDialog from "@/shared/ui/ConfirmDialog"
import AssignCatalogToGroupModal from "@/features/catalogs/ui/AssignCatalogToGroupModal"

const TABS = [
  ["tasks", "Мои задачи"],
  ["catalogs", "Каталоги"],
  ["solutions", "Решения"],
  ["support", "Обращения"],
  ["analytics", "Аналитика"],
  ["groups", "Мои группы"],
]
const TAB_IDS = TABS.map(([id]) => id)

const LEGACY_TAB_MAP = {
  "teacher-tasks": "tasks",
  tasks: "tasks",
  "teacher-solutions": "solutions",
  "teacher-groups": "groups",
}

function normalizeTab(raw) {
  if (!raw) return "tasks"
  const mapped = LEGACY_TAB_MAP[raw] || raw
  return TAB_IDS.includes(mapped) ? mapped : "tasks"
}
export default function TeacherCabinetPage({ user = null, onSignOut = null }) {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialTab = normalizeTab(searchParams.get("tab"))
  const [tab, setTab] = useState(initialTab)
  const [courseCreateOpen, setCourseCreateOpen] = useState(false)

  const viewTeacherIdRaw = searchParams.get("teacherId")
  const viewTeacherId = viewTeacherIdRaw ? Number(viewTeacherIdRaw) : null
  const viewOnly = Boolean(viewTeacherId && viewTeacherId !== user?.id)

  const teacher = useTeacherProfile({
    enabled: true,
    activeTab: tab,
    viewTeacherId: viewTeacherId || null,
    viewOnly,
  })

  const effectiveTeacherUserId = viewTeacherId || user?.id

  const wideTab = ["analytics", "tasks", "groups", "catalogs"].includes(tab)

  const tabBusy =
    (tab === "tasks" && (teacher.tasksLoading || teacher.metaLoading)) ||
    (tab === "catalogs" && teacher.catalogsLoading) ||
    (tab === "analytics" && teacher.analyticsLoading)
  const pageTitle = useMemo(() => {
    if (viewOnly && teacher.profile?.display_name) {
      return `Кабинет: ${teacher.profile.display_name}`
    }
    return "Кабинет преподавателя"
  }, [viewOnly, teacher.profile?.display_name])

  useEffect(() => {
    const q = normalizeTab(searchParams.get("tab"))
    if (q !== tab) setTab(q)
  }, [searchParams, tab])

  const handleTabChange = (id) => {
    setTab(id)
    const next = { tab: id }
    if (viewTeacherId) next.teacherId = String(viewTeacherId)
    setSearchParams(next, { replace: true })
  }

  return (
    <LearningAppShell user={user} onSignOut={onSignOut}>
      <PageHeader
        title={pageTitle}
        subtitle={
          viewOnly
            ? "Просмотр задач, каталогов и групп преподавателя."
            : "Задачи, решения студентов, аналитика и управление группами."
        }
        right={
          !viewOnly && teacher.canEditTasks
            ? [
                <button
                  key="add-course"
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={() => setCourseCreateOpen(true)}
                >
                  + Добавить курс
                </button>,
              ]
            : []
        }
      />
      {teacher.error ? (
        <div className="toast err" style={{ marginBottom: 16, maxWidth: "none" }}>
          <div className="tt">{teacher.error}</div>
        </div>
      ) : null}

      <div className={wideTab ? "teacher-profile-wide" : undefined}>
        <div className="tabbar-row">
          <div className="tabbar">
            {TABS.map(([id, label]) => (
              <button
                key={id}
                type="button"
                className={`${tab === id ? "on pp" : ""}${tab === id && tabBusy ? " pending" : ""}`}
                aria-busy={tab === id && tabBusy ? "true" : undefined}
                onClick={() => handleTabChange(id)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {teacher.loading && !teacher.profile ? (
          <p className="muted">Загрузка…</p>
        ) : (
          <>
            {tabBusy ? (
              <p className="tab-loading-hint muted" aria-live="polite">
                Загрузка раздела…
              </p>
            ) : null}
            {tab === "tasks" && (
              <TeacherToxicTasksPanel
                  tasks={teacher.tasks}
                  visibleTasks={teacher.visibleTasks}
                  catalogNameById={teacher.catalogNameById}
                  catalogs={teacher.catalogs}
                  groups={teacher.groups}
                  canManageCatalogs={teacher.canManageCatalogs}
                  onAssignCatalog={teacher.setCatalogToAssign}
                  canEdit={teacher.canEditTasks}
                  search={teacher.search}
                  onSearchChange={teacher.setSearch}
                  onTasksRefresh={teacher.refreshTasks}
                  onMetaRefresh={teacher.refreshTasksMeta}
                  loading={teacher.tasksLoading}
                  metaLoading={teacher.metaLoading}
                  chapters={teacher.chapters}
                  collectionMeta={teacher.collectionMeta}
                  courses={teacher.courses}
                  platformCourseMeta={teacher.platformCourseMeta}
                  teacherProfile={teacher.profile}
                />
            )}
            {tab === "catalogs" && (
              <TeacherToxicCatalogsPanel
                catalogs={teacher.catalogs}
                canManage={teacher.canManageCatalogs}
                groups={teacher.groups}
                loading={teacher.catalogsLoading}
                newCatalogTitle={teacher.newCatalogTitle}
                setNewCatalogTitle={teacher.setNewCatalogTitle}
                newCatalogDescription={teacher.newCatalogDescription}
                setNewCatalogDescription={teacher.setNewCatalogDescription}
                newCatalogPrivate={teacher.newCatalogPrivate}
                setNewCatalogPrivate={teacher.setNewCatalogPrivate}
                newCatalogGroupId={teacher.newCatalogGroupId}
                setNewCatalogGroupId={teacher.setNewCatalogGroupId}
                onCreateCatalog={teacher.handleCreateCatalog}
                onAssign={teacher.setCatalogToAssign}
                onDelete={teacher.setCatalogToDelete}
              />
            )}
            {tab === "solutions" && (              <TeacherToxicSolutionsPanel
                groups={teacher.groups}
                catalogs={teacher.catalogs}
                teacherUserId={effectiveTeacherUserId}
              />
            )}
            {tab === "support" && !viewOnly && <TeacherSupportInboxPanel />}
            {tab === "analytics" && (
              <>
                {teacher.analyticsLoading && <p className="muted">Загрузка аналитики…</p>}
                {!teacher.analyticsLoading && (
                  <TeacherToxicAnalyticsPanel
                    analytics={teacher.analytics}
                    activity={teacher.activity}
                    catalogCount={teacher.catalogs.length}
                  />
                )}
              </>
            )}
            {tab === "groups" && (
              <TeacherToxicGroupsPanel
                groups={teacher.groups}
                teacherUserId={effectiveTeacherUserId}
                canManage={teacher.canManageGroups}
                newGroupName={teacher.newGroupName}
                setNewGroupName={teacher.setNewGroupName}
                onCreateGroup={teacher.handleCreateGroup}
                inviteByGroupId={teacher.inviteByGroupId}
                invitingGroupId={teacher.invitingGroupId}
                onGenerateInvite={teacher.handleGenerateInvite}
                onCopyInvite={teacher.copyInviteCode}
                onDeleteGroup={teacher.handleDeleteGroup}
                deletingGroupId={teacher.deletingGroupId}
              />
            )}
          </>
        )}
      </div>

      {!viewOnly ? (
        <>
          <TeacherPlatformCourseEditorModal
            open={courseCreateOpen}
            mode="create"
            onClose={() => setCourseCreateOpen(false)}
            onSaved={() => void teacher.refreshCourses()}
          />
          <AssignCatalogToGroupModal
            catalog={teacher.catalogToAssign}
            groups={teacher.groups}
            onClose={() => teacher.setCatalogToAssign(null)}
            onAssigned={teacher.refreshCatalogs}
          />
          <ConfirmDialog
            open={Boolean(teacher.catalogToDelete)}
            title="Удалить каталог?"
            message={
              teacher.catalogToDelete
                ? `Каталог «${teacher.catalogToDelete.title}» будет удалён. Задачи останутся в вашем списке.`
                : ""
            }
            confirmLabel="Удалить"
            cancelLabel="Отмена"
            loading={teacher.deletingCatalog}
            onConfirm={teacher.handleDeleteCatalog}
            onCancel={() => teacher.setCatalogToDelete(null)}
          />
        </>
      ) : null}
    </LearningAppShell>
  )
}
