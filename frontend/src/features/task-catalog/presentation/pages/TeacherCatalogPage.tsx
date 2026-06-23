import { Navigate, useNavigate, useParams } from "react-router-dom"
import { useCallback, useEffect, useMemo, useState } from "react"

import {
  addCourseToCatalog,
  getCatalog,
  listCatalogCourses,
  listTeacherCourses,
  removeCourseFromCatalog,
  type TeacherCourseDto,
} from "@/features/task-catalog/infrastructure/catalogApi"
import AssignCatalogToGroupModal from "@/features/catalogs/ui/AssignCatalogToGroupModal"
import { listMyTeacherGroups } from "@/features/groups/api/groupsApi"
import TeacherAppShell from "@/features/teacher/layout/TeacherAppShell"
import PageHeader from "@/features/student/layout/PageHeader"
import EmptyState from "@/shared/ui/EmptyState"
import { deriveLabelGlyph } from "@/shared/utils/labelGlyph"

function pluralCourses(count: number): string {
  const mod10 = count % 10
  const mod100 = count % 100
  if (mod10 === 1 && mod100 !== 11) return "курс"
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return "курса"
  return "курсов"
}

function catalogSubtitle(catalogMeta, courseCount, groups) {
  const countPart = `${courseCount} ${pluralCourses(courseCount)}`
  if (!catalogMeta?.group_id) return countPart
  const group = groups.find((g: unknown) => g.id === catalogMeta.group_id)
  if (group?.name) return `${countPart} · группа «${group.name}»`
  return `${countPart} · назначен группе`
}

export default function TeacherCatalogPage({ user = null, onSignOut = null }) {
  const navigate = useNavigate()
  const { catalogId } = useParams()
  const isDetail = Boolean(catalogId)
  const [catalogMeta, setCatalogMeta] = useState(null)
  const [catalogCourses, setCatalogCourses] = useState<TeacherCourseDto[]>([])
  const [availableCourses, setAvailableCourses] = useState<TeacherCourseDto[]>([])
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedCourseIds, setSelectedCourseIds] = useState<number[]>([])
  const [candidateSearch, setCandidateSearch] = useState("")
  const [assignOpen, setAssignOpen] = useState(false)

  const loadDetail = useCallback(async () => {
    if (!catalogId) return
    setLoading(true)
    setError(null)
    try {
      const [meta, inCatalog, allCourses, teacherGroups] = await Promise.all([
        getCatalog(Number(catalogId)),
        listCatalogCourses(Number(catalogId)),
        listTeacherCourses(),
        listMyTeacherGroups().catch(() => []),
      ])
      const inCatalogIds = new Set(inCatalog.map((course) => course.id))
      setCatalogMeta(meta)
      setCatalogCourses(inCatalog)
      setAvailableCourses(allCourses.filter((course) => !inCatalogIds.has(course.id)))
      setGroups(Array.isArray(teacherGroups) ? teacherGroups : [])
      setSelectedCourseIds([])
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Ошибка загрузки")
    } finally {
      setLoading(false)
    }
  }, [catalogId])

  useEffect(() => {
    if (isDetail) {
      loadDetail()
    }
  }, [isDetail, loadDetail])

  const handleAddExisting = async () => {
    if (selectedCourseIds.length === 0 || !catalogId) return
    try {
      await Promise.all(
        selectedCourseIds.map((courseId) => addCourseToCatalog(Number(catalogId), courseId)),
      )
      setSelectedCourseIds([])
      await loadDetail()
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Не удалось добавить курсы")
    }
  }

  const toggleSelectedCourse = (courseId: number) => {
    setSelectedCourseIds((current) =>
      current.includes(courseId)
        ? current.filter((id) => id !== courseId)
        : [...current, courseId],
    )
  }

  const handleRemove = async (courseId: number) => {
    try {
      await removeCourseFromCatalog(Number(catalogId), courseId)
      await loadDetail()
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Не удалось убрать курс")
    }
  }

  const catalogTitle = catalogMeta?.title || `Каталог #${catalogId}`
  const normalizedCandidateSearch = candidateSearch.trim().toLowerCase()
  const visibleCandidateCourses = useMemo(() => {
    if (!normalizedCandidateSearch) return availableCourses
    return availableCourses.filter((course) =>
      [course.title, course.description]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(normalizedCandidateSearch)),
    )
  }, [availableCourses, normalizedCandidateSearch])

  if (!isDetail) {
    return <Navigate to="/teacher/cabinet?tab=catalogs" replace />
  }

  return (
    <TeacherAppShell user={user} onSignOut={onSignOut}>
      <button
        type="button"
        className="btn btn-ghost btn-sm"
        style={{ marginBottom: 14 }}
        onClick={() => navigate("/teacher/cabinet?tab=catalogs")}
      >
        ← К каталогам
      </button>

      <PageHeader
        title={catalogTitle}
        subtitle={catalogSubtitle(catalogMeta, catalogCourses.length, groups)}
        right={[
          <button
            key="assign"
            type="button"
            className={`btn btn-sm ${catalogMeta?.group_id ? "btn-secondary" : "btn-primary"}`}
            onClick={() => setAssignOpen(true)}
            disabled={!catalogMeta}
          >
            {catalogMeta?.group_id ? "Переназначить группе" : "Назначить группе"}
          </button>,
        ]}
      />

      {error ? (
        <div className="note err" style={{ marginBottom: 16 }}>
          {error}
        </div>
      ) : null}

      {!loading && catalogMeta && !catalogMeta.group_id && catalogCourses.length > 0 ? (
        <div className="note warn" style={{ marginBottom: 16, lineHeight: 1.5 }}>
          <b>Студенты пока не видят этот каталог.</b> Курсы добавлены, но каталог нужно назначить группе —
          иначе на «Курсы» у учеников будет пусто.{" "}
          <button
            type="button"
            className="btn btn-primary btn-xs"
            style={{ marginLeft: 8 }}
            onClick={() => setAssignOpen(true)}
          >
            Назначить группе
          </button>
        </div>
      ) : null}

      {loading ? (
        <div className="card card-pad" style={{ textAlign: "center" }}>
          <div className="spinner" style={{ marginBottom: 12 }} />
          <p className="muted" style={{ margin: 0 }}>
            Загрузка каталога…
          </p>
        </div>
      ) : (
        <div className="catalog-detail-grid">
          <div className="card card-pad">
            {catalogCourses.length === 0 ? (
              <EmptyState
                icon="📚"
                title="В каталоге пока нет курсов"
                text="Выберите курсы справа и нажмите «Добавить выбранные» — задачи основного курса попадут в каталог автоматически."
              />
            ) : (
              <div className="tt-rows">
                {catalogCourses.map((course) => (
                  <div key={course.id} className="candidate-tile" style={{ cursor: "default" }}>
                    <span style={{ fontSize: 18 }}>{deriveLabelGlyph(course.title)}</span>
                    <span style={{ flex: 1, minWidth: 0 }}>
                      <span style={{ display: "block", fontSize: 14, fontWeight: 600 }}>{course.title}</span>
                      {course.description ? (
                        <span className="muted" style={{ display: "block", fontSize: 12.5, marginTop: 4 }}>
                          {course.description}
                        </span>
                      ) : null}
                      <span className="mono mut3" style={{ fontSize: 11, display: "block", marginTop: 6 }}>
                        {course.task_count}{" "}
                        {course.task_count === 1 ? "задача" : course.task_count >= 2 && course.task_count <= 4 ? "задачи" : "задач"}
                        {course.is_default ? " · основной курс" : ""}
                      </span>
                    </span>
                    <button
                      type="button"
                      className="btn btn-danger btn-sm"
                      onClick={() => void handleRemove(course.id)}
                    >
                      Убрать
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <aside className="card card-pad">
            <div className="between" style={{ marginBottom: 4 }}>
              <b style={{ fontSize: 14 }}>Добавить существующие курсы</b>
              {selectedCourseIds.length > 0 ? (
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={() => void handleAddExisting()}
                >
                  Добавить выбранные ({selectedCourseIds.length})
                </button>
              ) : null}
            </div>
            <p className="mut3" style={{ fontSize: 12, margin: "0 0 12px" }}>
              Можно выбрать сразу несколько курсов.
            </p>
            <input
              type="search"
              className="input"
              style={{ height: 36, marginBottom: 10 }}
              placeholder="Поиск курсов…"
              value={candidateSearch}
              onChange={(event) => setCandidateSearch(event.target.value)}
            />
            {visibleCandidateCourses.length === 0 ? (
              <EmptyState
                icon="🔍"
                title="Нет курсов для добавления"
                text={
                  availableCourses.length === 0
                    ? "Все ваши курсы уже в этом каталоге."
                    : "По запросу ничего не найдено."
                }
              />
            ) : (
              <div className="catalog-detail-candidates">
                {visibleCandidateCourses.map((course) => {
                  const picked = selectedCourseIds.includes(course.id)
                  return (
                    <label
                      key={course.id}
                      className={`candidate-tile${picked ? " on" : ""}`}
                      onClick={(event) => {
                        event.preventDefault()
                        toggleSelectedCourse(course.id)
                      }}
                    >
                      <span className={`checkbox${picked ? " on" : ""}`} aria-hidden />
                      <span style={{ flex: 1, minWidth: 0 }}>
                        <span style={{ display: "block", fontSize: 13.5, fontWeight: 500 }}>{course.title}</span>
                        <span className="mono mut3" style={{ fontSize: 11 }}>
                          {course.task_count}{" "}
                          {course.task_count === 1 ? "задача" : course.task_count >= 2 && course.task_count <= 4 ? "задачи" : "задач"}
                        </span>
                      </span>
                    </label>
                  )
                })}
              </div>
            )}
          </aside>
        </div>
      )}

      <AssignCatalogToGroupModal
        catalog={assignOpen ? catalogMeta : null}
        groups={groups}
        onClose={() => setAssignOpen(false)}
        onAssigned={loadDetail}
      />
    </TeacherAppShell>
  )
}
