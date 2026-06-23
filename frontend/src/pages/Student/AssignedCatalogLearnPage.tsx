import { useMemo, useState } from "react"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"

import LearnCourseCard from "@/features/curriculum/components/LearnCourseCard"
import CurriculumStates from "@/features/curriculum/components/CurriculumStates"
import { buildLearnCourses, filterLearnCourses } from "@/features/curriculum/learnTracksUi"
import {
  getCurriculumCollectionsErrorMessage,
  useCurriculumCollections,
} from "@/features/curriculum/hooks/useCurriculumCollections"
import { getMyGroupWorkspace } from "@/features/groups/api/groupsApi"
import { userQueryScope } from "@/shared/providers/queryClient"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import PageHeader from "@/features/student/layout/PageHeader"
import {
  deadlineUrgencyStyle,
  formatSetDeadline,
} from "@/features/student/utils/deadlineView"

interface AssignedCatalogLearnPageProps {
  user?: { id?: number | string } | null
  onSignOut?: (() => void) | null
}

export default function AssignedCatalogLearnPage({
  user = null,
  onSignOut = null,
}: AssignedCatalogLearnPageProps) {
  const navigate = useNavigate()
  const { catalogId } = useParams()
  const [searchParams] = useSearchParams()
  const groupId = searchParams.get("group")
  const [search, setSearch] = useState("")
  const guestMode = !user

  const curriculumQuery = useCurriculumCollections(undefined, {
    enabled: true,
    authenticated: !guestMode,
    userId: user?.id,
  })

  const workspaceQuery = useQuery({
    queryKey: ["groups", "workspace", userQueryScope(user?.id), groupId],
    queryFn: () => getMyGroupWorkspace(groupId!),
    enabled: Boolean(user && groupId),
  })

  const catalog = useMemo(() => {
    const catalogs = workspaceQuery.data?.catalogs
    if (!Array.isArray(catalogs)) return null
    const id = Number(catalogId)
    return catalogs.find((row) => Number(row.catalog_id) === id) ?? null
  }, [workspaceQuery.data, catalogId])

  const loading = curriculumQuery.isLoading || workspaceQuery.isLoading
  const error = curriculumQuery.error
    ? getCurriculumCollectionsErrorMessage(curriculumQuery.error)
    : workspaceQuery.error
      ? String(
          (workspaceQuery.error as { message?: string })?.message ||
            "Не удалось загрузить назначение",
        )
      : !workspaceQuery.isLoading && groupId && !catalog
        ? "Каталог не найден или недоступен."
        : !groupId
          ? "Не указана группа для этого каталога."
          : null

  const courses = useMemo(
    () => buildLearnCourses(curriculumQuery.data, { guestMode }),
    [curriculumQuery.data, guestMode],
  )

  const filteredCourses = useMemo(() => filterLearnCourses(courses, search), [courses, search])

  const deadlineLabel = formatSetDeadline(catalog?.deadline_at)
  const deadlineStyle = deadlineUrgencyStyle(catalog?.deadline_at)
  const subtitleParts = [
    workspaceQuery.data?.group?.name,
    workspaceQuery.data?.teacher?.name,
    deadlineLabel,
  ].filter(Boolean)

  return (
    <LearningAppShell user={user} onSignOut={guestMode ? null : onSignOut}>
      <PageHeader
        title={catalog?.catalog_title || "Курсы"}
        subtitle={
          subtitleParts.length > 0
            ? subtitleParts.join(" · ")
            : "Общие курсы платформы и персональные задания от преподавателя."
        }
      />

      {deadlineLabel ? (
        <p className="mono mb-4 max-w-[520px]" style={{ fontSize: 13, ...deadlineStyle }}>
          {deadlineLabel}
        </p>
      ) : null}

      <div className="relative mb-[22px] max-w-[520px]">
        <input
          className="input h-11 pl-10"
          placeholder="Поиск по названию, языку или автору…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Поиск курсов"
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
        empty={!loading && !error && courses.length === 0}
        loadingText="Загрузка курсов…"
        onRetry={() => {
          void curriculumQuery.refetch()
          void workspaceQuery.refetch()
        }}
      >
        {filteredCourses.length === 0 ? (
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

      <div className="mt-6">
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => navigate("/learn")}>
          ← К курсам платформы
        </button>
      </div>
    </LearningAppShell>
  )
}
