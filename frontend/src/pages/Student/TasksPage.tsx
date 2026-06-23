import { useEffect, useMemo, useState, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import { useLanguages } from "@/shared/hooks/useLanguages"
import { useTaskOverview } from "@/shared/hooks/useTaskOverview"
import { useCurriculumCollections } from "@/features/curriculum/hooks/useCurriculumCollections"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import PageHeader from "@/features/student/layout/PageHeader"
import Filters from "@/features/student/ui/Filters"
import TaskTable from "@/features/student/ui/TaskTable"
import Badge from "@/shared/ui/Badge"
import AssignedCatalogSidebarCard from "@/features/student/ui/AssignedCatalogSidebarCard"
import JoinedGroupSidebarCard from "@/features/student/ui/JoinedGroupSidebarCard"
import StudentGroupInviteCard from "@/features/student/ui/StudentGroupInviteCard"
import { CardSkeleton } from "@/shared/ui/LoadingBlock"
import {
  buildTaskListSubtitle,
  computeTrackTaskStats,
} from "@/features/student/utils/taskListSummary"
import { useActiveLearningTrack } from "@/features/student/hooks/useActiveLearningTrack"
import CurriculumTrackBanner from "@/features/curriculum/components/CurriculumTrackBanner"
import { buildTaskTypeOptions } from "@/features/student/utils/taskView"
import { canAccessTeacherWorkspace } from "@/shared/api/auth"
import { useAssignedCatalogs } from "@/features/groups/hooks/useAssignedCatalogs"
import { useJoinedGroupsOverview } from "@/features/groups/hooks/useJoinedGroupsOverview"
import { openJoinedGroupLearn } from "@/features/groups/routing/joinedGroupLearnPath"
import { userQueryScope } from "@/shared/providers/queryClient"
import type { GroupDto, StudentJoinedGroupOverviewDto } from "@/shared/types/groups"
import type { LanguageItem } from "@/shared/types/language"

function resolveLanguageFilter(langFrom: string, languages: LanguageItem[]): string | undefined {
  if (langFrom === "all") return undefined
  const match = languages.find((item) => item.label === langFrom)
  return match?.id || langFrom.toLowerCase()
}
const PAGE_SIZE = 20
const DIFFICULTIES = ["easy", "medium", "hard"]

export default function TasksPage({
  user = null,
  onSignOut = null,
  taskPathPrefix = "/tasks",
}) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const guestMode = !user
  const { languages } = useLanguages()
  const [search, setSearch] = useState("")
  const [debouncedSearch, setDebouncedSearch] = useState("")
  const [type, setType] = useState("all")
  const [status, setStatus] = useState("all")
  const [diff, setDiff] = useState("all")
  const [langFrom, setLangFrom] = useState("all")
  const [langTo, setLangTo] = useState("all")
  const [patternSel, setPatternSel] = useState("")
  const [matchMode, setMatchMode] = useState("all")
  const [filterOpen, setFilterOpen] = useState(false)
  const [page, setPage] = useState(1)
  const [loadCurriculum, setLoadCurriculum] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search.trim()), 300)
    return () => window.clearTimeout(timer)
  }, [search])

  useEffect(() => {
    setLoadCurriculum(true)
  }, [])

  const overviewFilters = useMemo(
    () => ({
      page,
      pageSize: PAGE_SIZE,
      search: debouncedSearch || undefined,
      type: type !== "all" ? type : undefined,
      status: !guestMode && status !== "all" ? status : undefined,
      difficulty: diff !== "all" ? diff : undefined,
      pattern: patternSel || undefined,
      language: resolveLanguageFilter(langFrom, languages),
      matchMode: matchMode === "any" ? "any" : "all",
    }),
    [page, debouncedSearch, type, status, diff, patternSel, langFrom, languages, matchMode, guestMode],
  )

  const { tasks, total: overviewTotal, taskTypes, loading, error } = useTaskOverview(
    overviewFilters,
    {
      includeAssignmentSets: false,
      includeTaskTypes: filterOpen || type !== "all",
    },
    user?.id,
  )

  const curriculumQuery = useCurriculumCollections(undefined, {
    enabled: loadCurriculum,
    authenticated: !guestMode,
    userId: user?.id,
  })
  const assignedQuery = useAssignedCatalogs(user?.id, !guestMode)
  const joinedGroupsQuery = useJoinedGroupsOverview(user?.id, !guestMode)
  const assignedCatalogs = Array.isArray(assignedQuery.data) ? assignedQuery.data : []
  const assignedCatalogCount = assignedCatalogs.length
  const joinedGroups = Array.isArray(joinedGroupsQuery.data) ? joinedGroupsQuery.data : []
  const joinedGroupCatalogCount = joinedGroups.reduce(
    (sum, group) => sum + (group.catalog_count ?? 0),
    0,
  )
  const pendingJoinedGroups = joinedGroups.filter((group) => (group.catalog_count ?? 0) === 0)
  const sidebarItemCount = assignedCatalogCount || joinedGroups.length
  const hasStudentAssignments =
    assignedCatalogCount > 0 || joinedGroupCatalogCount > 0 || joinedGroups.length > 0
  const showStudentSidebar = !guestMode
  const showStudentLearningChrome =
    guestMode || !canAccessTeacherWorkspace(user) || hasStudentAssignments
  const curriculumLanguages = Array.isArray(curriculumQuery.data?.languages)
    ? curriculumQuery.data.languages
    : []
  const languageOptions = useMemo(
    () =>
      (Array.isArray(languages) ? languages : [])
        .map((l) => l.label)
        .filter(Boolean),
    [languages],
  )

  const taskTypeOptions = useMemo(() => buildTaskTypeOptions(taskTypes), [taskTypes])

  const patternOptions = useMemo(() => {
    const patterns = new Set<string>()
    tasks.forEach((t) => (t.constructions || []).forEach((p) => patterns.add(p)))
    return Array.from(patterns)
  }, [tasks])

  const pageCount = Math.max(1, Math.ceil((overviewTotal || 0) / PAGE_SIZE))

  useEffect(() => {
    if (page > pageCount) setPage(1)
  }, [pageCount, page])

  useEffect(() => {
    setPage(1)
  }, [debouncedSearch, type, status, diff, patternSel, langFrom, matchMode])

  const activeTrack = useActiveLearningTrack()

  const stats = useMemo(
    () =>
      computeTrackTaskStats(curriculumLanguages, activeTrack, tasks, overviewTotal, {
        ignoreCurriculumProgress: guestMode,
      }),
    [curriculumLanguages, activeTrack, tasks, overviewTotal, guestMode],
  )

  const taskListSubtitle = useMemo(() => {
    if (loading || (loadCurriculum && curriculumQuery.isLoading)) {
      return "Загрузка прогресса…"
    }
    return buildTaskListSubtitle(stats, tasks)
  }, [loading, loadCurriculum, curriculumQuery.isLoading, stats, tasks])

  const filterCount =
    (type !== "all" ? 1 : 0) +
    (status !== "all" ? 1 : 0) +
    (diff !== "all" ? 1 : 0) +
    (patternSel ? 1 : 0)

  const handleGroupJoined = useCallback(
    async (group?: GroupDto) => {
      const scope = userQueryScope(user?.id)
      if (group) {
        queryClient.setQueryData<StudentJoinedGroupOverviewDto[]>(
          ["groups", "joined", "overview", scope],
          (old) => {
            const existing = old ?? []
            if (existing.some((item) => item.id === group.id)) return existing
            return [
              ...existing,
              {
                id: group.id,
                name: group.name,
                teacher: { id: group.teacher_id, name: `Преподаватель #${group.teacher_id}` },
                catalog_count: 0,
                task_count: 0,
                solved_count: 0,
                deadline_alert: null,
              },
            ]
          },
        )
      }
      await queryClient.invalidateQueries({ queryKey: ["groups", "joined"] })
    },
    [queryClient, user?.id],
  )

  const resetFilters = () => {
    setType("all")
    setStatus("all")
    setDiff("all")
    setLangFrom("all")
    setLangTo("all")
    setPatternSel("")
    setMatchMode("all")
    setSearch("")
    setPage(1)
  }

  const content = (
    <>
      {error ? (
        <div className="toast err" style={{ marginBottom: 16, maxWidth: "none" }}>
          {error}
        </div>
      ) : null}

      <PageHeader title="Список задач" subtitle={taskListSubtitle} />

      {showStudentLearningChrome ? (
        <CurriculumTrackBanner
          languages={curriculumLanguages}
          loading={curriculumQuery.isLoading}
          error={
            curriculumQuery.isError
              ? String(
                  (curriculumQuery.error as { message?: string })?.message ||
                    "Не удалось загрузить учебный трек",
                )
              : null
          }
          taskPathPrefix={taskPathPrefix}
          guestMode={guestMode}
        />
      ) : null}

      <Filters
        search={search}
        onSearchChange={(v) => {
          setSearch(v)
          setPage(1)
        }}
        langFrom={langFrom}
        langTo={langTo}
        languageOptions={languageOptions}
        onLangFromChange={(v) => {
          setLangFrom(v)
          setPage(1)
        }}
        onLangToChange={(v) => {
          setLangTo(v)
          setPage(1)
        }}
        onSwapLangs={() => {
          const a = langFrom
          setLangFrom(langTo)
          setLangTo(a)
          setPage(1)
        }}
        filterOpen={filterOpen}
        onFilterOpenChange={setFilterOpen}
        filterCount={filterCount}
        matchMode={matchMode}
        onMatchModeChange={setMatchMode}
        status={status}
        onStatusChange={(v) => {
          setStatus(v)
          setPage(1)
        }}
        diff={diff}
        onDiffChange={(v) => {
          setDiff(v)
          setPage(1)
        }}
        type={type}
        onTypeChange={(v) => {
          setType(v)
          setPage(1)
        }}
        patternSel={patternSel}
        onPatternSelChange={(v) => {
          setPatternSel(v)
          setPage(1)
        }}
        difficulties={DIFFICULTIES}
        taskTypeOptions={taskTypeOptions}
        patternOptions={patternOptions}
        onReset={resetFilters}
        hideStatusFilter={guestMode}
      />

      {loading ? (
        <CardSkeleton rows={5} />
      ) : (
        <div
          className={
            showStudentSidebar
              ? "tasks-page-layout tasks-page-layout--with-sidebar"
              : "tasks-page-layout"
          }
        >
          <TaskTable
            tasks={tasks}
            page={page}
            pageSize={PAGE_SIZE}
            pageCount={pageCount}
            totalFiltered={overviewTotal || tasks.length}
            onPageChange={setPage}
            onResetFilters={resetFilters}
            taskPathPrefix={taskPathPrefix}
          />
          {showStudentSidebar ? (
            <aside className="card card-pad">
              <div className="between" style={{ marginBottom: 8 }}>
                <b style={{ fontSize: 15 }}>Назначения</b>
                <Badge kind="purple">{sidebarItemCount || "0"}</Badge>
              </div>
              <p className="muted" style={{ fontSize: 12.5, margin: "0 0 14px", lineHeight: 1.4 }}>
                {joinedGroups.length > 0 && assignedCatalogCount === 0
                  ? "Вы в группе — каталоги появятся, когда преподаватель их назначит."
                  : "Каталоги групп, к которым вы подключены."}
              </p>
              <div className="grid" style={{ gap: 10 }}>
                {assignedQuery.isLoading ||
                (joinedGroupsQuery.isLoading && joinedGroups.length === 0 && assignedCatalogCount === 0) ? (
                  <CardSkeleton rows={2} />
                ) : assignedQuery.isError && assignedCatalogCount === 0 && joinedGroups.length === 0 ? (
                  <div className="toast err" style={{ margin: 0, maxWidth: "none" }}>
                    Не удалось загрузить назначения.
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      style={{ marginTop: 8 }}
                      onClick={() => void assignedQuery.refetch()}
                    >
                      Повторить
                    </button>
                  </div>
                ) : (
                  <>
                    {assignedCatalogs.map((catalog) => (
                      <AssignedCatalogSidebarCard
                        key={`${catalog.group_id}-${catalog.catalog_id}`}
                        catalog={catalog}
                        onOpen={() =>
                          navigate(`/learn/assigned/${catalog.catalog_id}?group=${catalog.group_id}`)
                        }
                      />
                    ))}
                    {pendingJoinedGroups.map((group) => (
                      <JoinedGroupSidebarCard
                        key={`group-${group.id}`}
                        group={group}
                        onOpen={() => void openJoinedGroupLearn(navigate, group.id)}
                      />
                    ))}
                  </>
                )}
                <StudentGroupInviteCard onJoined={handleGroupJoined} />
                {hasStudentAssignments ? (
                  <button
                    type="button"
                    onClick={() => navigate("/learn")}
                    style={{
                      border: "1px dashed var(--border-2)",
                      background: "transparent",
                      borderRadius: 12,
                      padding: 13,
                      cursor: "pointer",
                      color: "var(--text-2)",
                      fontSize: 13,
                    }}
                  >
                    Все назначения →
                  </button>
                ) : null}
              </div>
            </aside>
          ) : null}
        </div>
      )}
    </>
  )

  return (
    <LearningAppShell user={user} onSignOut={guestMode ? null : onSignOut}>
      {content}
    </LearningAppShell>
  )
}
