import { useMemo, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import PageHeader from "@/features/student/layout/PageHeader"
import LearnCourseCard from "@/features/curriculum/components/LearnCourseCard"
import AssignedCatalogCard from "@/features/curriculum/components/AssignedCatalogCard"
import CurriculumStates from "@/features/curriculum/components/CurriculumStates"
import { buildLearnCourses, filterLearnCourses } from "@/features/curriculum/learnTracksUi"
import {
  getCurriculumCollectionsErrorMessage,
  useCurriculumCollections,
} from "@/features/curriculum/hooks/useCurriculumCollections"
import { getMyGroupWorkspace } from "@/features/groups/api/groupsApi"
import { useAssignedCatalogs } from "@/features/groups/hooks/useAssignedCatalogs"
import { mapGroupWorkspaceCatalogs } from "@/features/groups/utils/mapGroupWorkspaceCatalogs"
import { userQueryScope } from "@/shared/providers/queryClient"

interface LearnHubPageProps {
  user?: { id?: number | string } | null
  onSignOut?: (() => void) | null
}

export default function LearnHubPage({ user = null, onSignOut = null }: LearnHubPageProps) {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const groupFilter = searchParams.get("group")
  const [search, setSearch] = useState("")
  const guestMode = !user

  const assignedQuery = useAssignedCatalogs(user?.id, !guestMode)
  const groupWorkspaceQuery = useQuery({
    queryKey: ["groups", "workspace", userQueryScope(user?.id), groupFilter],
    queryFn: () => getMyGroupWorkspace(groupFilter!),
    enabled: Boolean(user && groupFilter),
  })

  const curriculumQuery = useCurriculumCollections(undefined, {
    enabled: true,
    authenticated: !guestMode,
    userId: user?.id,
  })

  const assignedCatalogs = Array.isArray(assignedQuery.data) ? assignedQuery.data : []
  const groupCatalogs = useMemo(
    () => (groupFilter ? mapGroupWorkspaceCatalogs(groupWorkspaceQuery.data, groupFilter) : []),
    [groupFilter, groupWorkspaceQuery.data],
  )

  const visibleAssigned = useMemo(() => {
    if (groupFilter) return groupCatalogs
    return assignedCatalogs
  }, [groupFilter, groupCatalogs, assignedCatalogs])

  const showAssigned = !guestMode && (Boolean(groupFilter) || assignedCatalogs.length > 0)

  const filteredAssigned = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return visibleAssigned
    return visibleAssigned.filter(
      (catalog) =>
        catalog.catalog_title.toLowerCase().includes(q) ||
        catalog.group_name.toLowerCase().includes(q) ||
        (catalog.teacher_name || "").toLowerCase().includes(q),
    )
  }, [visibleAssigned, search])

  const loading = groupFilter
    ? groupWorkspaceQuery.isLoading
    : showAssigned
      ? assignedQuery.isLoading
      : curriculumQuery.isLoading

  const error = groupFilter
    ? groupWorkspaceQuery.error
      ? "Не удалось загрузить назначения группы."
      : null
    : showAssigned
      ? assignedQuery.error
        ? "Не удалось загрузить назначения преподавателя."
        : null
      : curriculumQuery.error
        ? getCurriculumCollectionsErrorMessage(curriculumQuery.error)
        : null

  const courses = useMemo(
    () => buildLearnCourses(curriculumQuery.data, { guestMode }),
    [curriculumQuery.data, guestMode],
  )
  const filteredCourses = useMemo(() => filterLearnCourses(courses, search), [courses, search])

  const groupName =
    groupWorkspaceQuery.data?.group?.name ||
    visibleAssigned[0]?.group_name ||
    null

  const pageTitle = groupFilter || showAssigned ? "Назначения" : "Курсы"
  const pageSubtitle = groupFilter
    ? groupName
      ? `Каталоги группы «${groupName}», назначенные преподавателем.`
      : "Каталоги этой группы, назначенные преподавателем."
    : showAssigned
      ? "Каталоги и задания, назначенные преподавателем."
      : "Общие курсы платформы и персональные задания от преподавателя."

  const assignedEmptyMessage = groupFilter
    ? "Преподаватель пока не назначил каталоги этой группе. Попросите его нажать «Назначить группе» в кабинете преподавателя."
    : "Измените запрос — поиск идёт по каталогу, группе и преподавателю."

  const showAssignedEmpty = showAssigned && !loading && !error && filteredAssigned.length === 0

  return (
    <LearningAppShell user={user} onSignOut={guestMode ? null : onSignOut}>
      <PageHeader title={pageTitle} subtitle={pageSubtitle} />

      <div className="relative mb-[22px] max-w-[520px]">
        <input
          className="input h-11 pl-10"
          placeholder={
            showAssigned ? "Поиск по каталогу, группе или преподавателю…" : "Поиск по названию, языку или автору…"
          }
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label={showAssigned ? "Поиск назначений" : "Поиск курсов"}
        />
        <span
          className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[15px] text-ink-faint"
          aria-hidden
        >
          ⌕
        </span>
      </div>

      <CurriculumStates
        loading={loading}
        error={error}
        empty={!showAssigned && !loading && !error && filteredCourses.length === 0}
        loadingText={showAssigned ? "Загрузка назначений…" : "Загрузка курсов…"}
        onRetry={() => {
          if (groupFilter) void groupWorkspaceQuery.refetch()
          else if (showAssigned) void assignedQuery.refetch()
          else void curriculumQuery.refetch()
        }}
      >
        {showAssigned ? (
          showAssignedEmpty ? (
            <div className="card card-pad">
              <div className="py-8 text-center">
                <p className="mb-1 text-[16px] font-semibold text-ink">Назначений пока нет</p>
                <p className="mx-auto max-w-sm text-[13.5px] text-ink-muted">{assignedEmptyMessage}</p>
              </div>
            </div>
          ) : (
            <div className="track-grid">
              {filteredAssigned.map((catalog) => (
                <AssignedCatalogCard
                  key={`${catalog.group_id}-${catalog.catalog_id}`}
                  catalog={catalog}
                  onOpen={() =>
                    navigate(`/learn/assigned/${catalog.catalog_id}?group=${catalog.group_id}`)
                  }
                />
              ))}
            </div>
          )
        ) : filteredCourses.length === 0 ? (
          <div className="card card-pad">
            <div className="py-8 text-center">
              <div className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-2xl border border-border bg-surface-2 text-2xl text-ink-faint">
                🔍
              </div>
              <p className="mb-1 text-[16px] font-semibold text-ink">Курсы не найдены</p>
              <p className="mx-auto max-w-sm text-[13.5px] text-ink-muted">
                Измените запрос — поиск идёт по названию, языку и автору.
              </p>
            </div>
          </div>
        ) : (
          <div className="track-grid">
            {filteredCourses.map((course) => (
              <LearnCourseCard key={course.id} course={course} />
            ))}
          </div>
        )}
      </CurriculumStates>
    </LearningAppShell>
  )
}
