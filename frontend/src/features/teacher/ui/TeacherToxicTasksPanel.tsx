import { Link } from "react-router-dom"
import { useEffect, useMemo, useRef, useState, type DragEvent } from "react"
import Badge from "@/shared/ui/Badge"
import DiffBadge from "@/shared/ui/DiffBadge"
import EmptyState from "@/shared/ui/EmptyState"
import { formatTaskTypeLabel } from "@/shared/types/taskLabels"
import { getLanguageLabel } from "@/shared/config/languages"
import { CURRICULUM_LANGUAGE_OPTIONS, LANGUAGE_TRACK_DESCRIPTIONS } from "@/features/curriculum/curriculumLanguageUi"
import { PLATFORM_COURSE } from "@/features/curriculum/platformCourse"
import { deriveLabelGlyph } from "@/shared/utils/labelGlyph"
import { teacherTaskEditPath } from "@/features/teacher/routing/teacherTaskEditPath"
import { teacherTaskCreatePath } from "@/features/teacher/routing/teacherTaskCreatePath"
import {
  updateChapterTaskOrder,
  updateCollectionChapterOrder,
  deleteCatalogTask,
  deleteCurriculumChapter,
  type CollectionMetaDto,
  type CurriculumChapterDto,
  type PlatformCourseMetaDto,
  type TeacherCourseDto,
} from "@/features/task-catalog/infrastructure/catalogApi"
import { TeacherChapterEditorModal } from "@/features/teacher/ui/TeacherChapterEditorModal"
import { TeacherCollectionEditorModal } from "@/features/teacher/ui/TeacherCollectionEditorModal"
import { TeacherPlatformCourseEditorModal } from "@/features/teacher/ui/TeacherPlatformCourseEditorModal"
import ConfirmDialog from "@/shared/ui/ConfirmDialog"
import { toast } from "@/shared/ui/toast"
import { formatStackedDateTime } from "@/shared/utils/format"
import "./teacher-tasks-panel.css"

interface TeacherToxicTasksPanelProps {
  tasks?: unknown[]
  visibleTasks?: unknown[]
  catalogNameById: unknown
  catalogs?: unknown[]
  groups?: unknown[]
  canManageCatalogs?: boolean
  onAssignCatalog?: (catalog: unknown) => void
  canEdit: unknown
  search: unknown
  onSearchChange: (...args: unknown[]) => unknown
  onTasksRefresh?: () => Promise<void> | void
  onMetaRefresh?: () => Promise<void> | void
  loading?: boolean
  metaLoading?: boolean
  chapters?: CurriculumChapterDto[]
  collectionMeta?: CollectionMetaDto[]
  courses?: TeacherCourseDto[]
  platformCourseMeta?: PlatformCourseMetaDto | null
  teacherProfile?: { display_name?: string | null; full_name?: string | null; user_id?: number | string | null } | null
}

type TaskRow = {
  id: number
  title: string
  type_id?: string
  type?: string
  difficulty?: string
  diff?: string
  catalog_ids?: number[]
  languages?: string[]
  language?: string | null
  source_language?: string | null
  lang?: string | null
  chapter_key?: string | null
  chapter_title?: string | null
  chapter_order?: number | null
  display_order?: number | null
  activity_label?: string | null
  primary_action?: string | null
  is_debug_task?: boolean
  action_sort_order?: number
  created_at?: string | null
  updated_at?: string | null
}

type CatalogFilter = "all" | "assigned" | "unassigned"

type ChapterGroup = {
  key: string
  title: string
  order: number
  tasks: TaskRow[]
  language?: string
  description?: string
  isCustom?: boolean
  updated_at?: string | null
}

type TrackGroup = {
  id: string
  label: string
  chapters: ChapterGroup[]
}

type DragPayload =
  | { kind: "task"; taskId: number; chapterKey: string }
  | { kind: "chapter"; chapterKey: string; trackId: string }

type CatalogRow = {
  id: number
  title: string
  group_id?: number | null
}

function normalizeCatalogName(value: string): string {
  return value.trim().toLowerCase()
}

function findCatalogForChapter(
  chapterTitle: string,
  chapterTasks: TaskRow[],
  catalogs: CatalogRow[],
): CatalogRow | null {
  if (!catalogs.length) return null
  const chapterName = normalizeCatalogName(chapterTitle)
  const byTitle = catalogs.find((catalog) => normalizeCatalogName(catalog.title) === chapterName)
  if (byTitle) return byTitle

  const byPartial = catalogs.find((catalog) => {
    const catalogName = normalizeCatalogName(catalog.title)
    return catalogName.includes(chapterName) || chapterName.includes(catalogName)
  })
  if (byPartial) return byPartial

  const counts = new Map<number, number>()
  for (const task of chapterTasks) {
    for (const catalogId of task.catalog_ids || []) {
      counts.set(catalogId, (counts.get(catalogId) || 0) + 1)
    }
  }
  let bestId: number | null = null
  let bestCount = 0
  for (const [catalogId, count] of counts) {
    if (count > bestCount) {
      bestCount = count
      bestId = catalogId
    }
  }
  if (bestId != null) {
    return catalogs.find((catalog) => catalog.id === bestId) || null
  }
  return null
}

type LayoutOverrides = {
  taskOrderByChapter: Record<string, number[]>
  chapterOrder: string[] | null
}

function reorderIds(ids: number[], taskId: number, index: number): number[] {
  const oldIndex = ids.indexOf(taskId)
  if (oldIndex < 0) return ids
  const next = ids.filter((id) => id !== taskId)
  let targetIndex = index
  if (oldIndex < index) targetIndex = index - 1
  targetIndex = Math.max(0, Math.min(targetIndex, next.length))
  next.splice(targetIndex, 0, taskId)
  return next
}

function reorderKeys(keys: string[], chapterKey: string, index: number): string[] {
  const oldIndex = keys.indexOf(chapterKey)
  if (oldIndex < 0) return keys
  const next = keys.filter((key) => key !== chapterKey)
  let targetIndex = index
  if (oldIndex < index) targetIndex = index - 1
  targetIndex = Math.max(0, Math.min(targetIndex, next.length))
  next.splice(targetIndex, 0, chapterKey)
  return next
}

function buildChapterGroups(tasks: TaskRow[]): ChapterGroup[] {
  const byKey = new Map<string, ChapterGroup>()
  for (const task of tasks) {
    const key = task.chapter_key || "__none__"
    const title = task.chapter_title || (task.chapter_key ? task.chapter_key : "Без главы")
    const order = task.chapter_key ? (task.chapter_order ?? 999) : 9999
    const existing = byKey.get(key)
    if (existing) {
      existing.tasks.push(task)
    } else {
      byKey.set(key, { key, title, order, tasks: [task] })
    }
  }
  return [...byKey.values()]
    .map((group) => ({
      ...group,
      tasks: [...group.tasks].sort((a, b) => compareTasks(a, b)),
    }))
    .sort((a, b) => {
      if (a.order !== b.order) return a.order - b.order
      return a.title.localeCompare(b.title, "ru")
    })
}

function taskBelongsToTrack(task: TaskRow, trackLanguage: string): boolean {
  const langs = (task.languages?.length ? task.languages : [task.language, task.source_language, task.lang])
    .map((lang) => String(lang || "").toLowerCase())
    .filter(Boolean)
  if (!langs.length) return true
  return langs.includes(trackLanguage)
}

function mergeChapterCatalog(
  groups: ChapterGroup[],
  chapters: CurriculumChapterDto[],
): ChapterGroup[] {
  const byKey = new Map(groups.map((group) => [group.key, { ...group }]))
  for (const chapter of chapters) {
    const existing = byKey.get(chapter.chapter_key)
    if (existing) {
      const taskDerivedOrder =
        existing.tasks.length > 0 && existing.order < 9000 ? existing.order : null
      byKey.set(chapter.chapter_key, {
        ...existing,
        title: chapter.title,
        order: taskDerivedOrder ?? chapter.sort_order ?? existing.order,
        language: chapter.language,
        description: chapter.description,
        isCustom: chapter.is_custom,
        updated_at: chapter.updated_at ?? existing.updated_at,
      })
      continue
    }
    byKey.set(chapter.chapter_key, {
      key: chapter.chapter_key,
      title: chapter.title,
      order: chapter.sort_order,
      tasks: [],
      language: chapter.language,
      description: chapter.description,
      isCustom: chapter.is_custom,
      updated_at: chapter.updated_at ?? null,
    })
  }
  return [...byKey.values()].sort((a, b) => {
    if (a.order !== b.order) return a.order - b.order
    return a.title.localeCompare(b.title, "ru")
  })
}

function buildTrackGroups(
  tasks: TaskRow[],
  chapters: CurriculumChapterDto[],
): TrackGroup[] {
  return CURRICULUM_LANGUAGE_OPTIONS.map((track) => {
    const trackChapters = chapters.filter((chapter) => chapter.language === track.id)
    const trackTasks = tasks.filter((task) => taskBelongsToTrack(task, track.id))
    const chapterGroups = mergeChapterCatalog(buildChapterGroups(trackTasks), trackChapters).filter(
      (group) => group.key !== "__none__",
    )
    return {
      id: track.id,
      label: track.label,
      chapters: chapterGroups,
    }
  })
}

function applyLayoutOverrides(
  groups: ChapterGroup[],
  overrides: LayoutOverrides,
): ChapterGroup[] {
  let next = groups.map((group) => {
    const overrideIds = overrides.taskOrderByChapter[group.key]
    if (!overrideIds?.length) return group
    const byId = new Map(group.tasks.map((task) => [task.id, task]))
    const tasks = overrideIds.map((id) => byId.get(id)).filter(Boolean) as TaskRow[]
    for (const task of group.tasks) {
      if (!overrideIds.includes(task.id)) tasks.push(task)
    }
    return { ...group, tasks }
  })

  if (overrides.chapterOrder?.length) {
    const byKey = new Map(next.map((group) => [group.key, group]))
    const ordered = overrides.chapterOrder
      .map((key) => byKey.get(key))
      .filter(Boolean) as ChapterGroup[]
    for (const group of next) {
      if (!overrides.chapterOrder.includes(group.key)) ordered.push(group)
    }
    next = ordered
  }

  return next
}

function plural(n: number, one: string, few: string, many: string): string {
  const m10 = n % 10
  const m100 = n % 100
  if (m10 === 1 && m100 !== 11) return one
  if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return few
  return many
}

function formatTaskLanguages(task: TaskRow) {
  const langs = Array.isArray(task.languages) ? task.languages.filter(Boolean) : []
  if (langs.length > 0) {
    return langs.map((lang) => getLanguageLabel(String(lang)) || String(lang))
  }
  const fallback = task.language || task.source_language || task.lang
  if (!fallback) return []
  return [getLanguageLabel(String(fallback)) || String(fallback)]
}

function formatActivityType(task: TaskRow) {
  if (task.activity_label) return task.activity_label
  return formatTaskTypeLabel(task.type_id || task.type)
}

function isCapstoneTitle(title: string): boolean {
  return /итоговая/i.test(String(title || ""))
}

function emptyStateText(
  totalTasks: number,
  catalogFilter: CatalogFilter,
  hasSearch: boolean,
): { title: string; text: string; icon: string } {
  if (totalTasks === 0) {
    return {
      icon: "📝",
      title: "Задач пока нет",
      text: "Создайте первую задачу — она появится в списке и её можно будет добавить в каталог.",
    }
  }
  if (hasSearch) {
    return {
      icon: "⌕",
      title: "Ничего не найдено",
      text: "Попробуйте изменить фильтры или поисковый запрос.",
    }
  }
  if (catalogFilter === "assigned") {
    return {
      icon: "📂",
      title: "Нет задач в каталогах",
      text: "Ни одна задача не добавлена в каталог. Выберите «Все задачи» или «Без каталога».",
    }
  }
  if (catalogFilter === "unassigned") {
    return {
      icon: "📂",
      title: "Все задачи в каталогах",
      text: "Нет задач без каталога. Выберите «Все задачи» или «В каталогах».",
    }
  }
  return {
    icon: "⌕",
    title: "Ничего не найдено",
    text: "Попробуйте изменить фильтры или поисковый запрос.",
  }
}

function compareTasks(a: TaskRow, b: TaskRow): number {
  const ao = a.chapter_order ?? 999
  const bo = b.chapter_order ?? 999
  if (ao !== bo) return ao - bo
  const ac = isCapstoneTitle(a.title) ? 1 : 0
  const bc = isCapstoneTitle(b.title) ? 1 : 0
  if (ac !== bc) return ac - bc
  const at = a.action_sort_order ?? 99
  const bt = b.action_sort_order ?? 99
  if (at !== bt) return at - bt
  const ad = a.display_order ?? 999_999
  const bd = b.display_order ?? 999_999
  if (ad !== bd) return ad - bd
  return String(a.title).localeCompare(String(b.title), "ru")
}
function halfDropIndex(event: DragEvent, base: number): number {
  const rect = event.currentTarget.getBoundingClientRect()
  return event.clientY < rect.top + rect.height / 2 ? base : base + 1
}

function TaskRowView({
  task,
  index,
  catalogNameById,
  canEdit,
  canDrag,
  isDragging,
  dragOverTop,
  dragOverBottom,
  onDragStart,
  onDragEnd,
  onRowDragOver,
  onRowDrop,
  onDelete,
}: {
  task: TaskRow
  index: number
  catalogNameById: Map<number, string>
  canEdit: boolean
  canDrag: boolean
  isDragging: boolean
  dragOverTop: boolean
  dragOverBottom: boolean
  onDragStart: (event: DragEvent) => void
  onDragEnd: () => void
  onRowDragOver: (event: DragEvent) => void
  onRowDrop: (event: DragEvent) => void
  onDelete?: () => void
}) {
  const catalogLabel =
    task.catalog_ids
      ?.map((id) => catalogNameById.get(id))
      .filter(Boolean)
      .join(", ") || null
  const langs = formatTaskLanguages(task)
  const updatedStamp = formatStackedDateTime(task.updated_at || task.created_at)

  return (
    <div
      className={`tt-row${isDragging ? " is-dragging" : ""}`}
      onDragOver={canDrag ? onRowDragOver : undefined}
      onDrop={canDrag ? onRowDrop : undefined}
    >
      {dragOverTop ? <span className="drop-line top" /> : null}
      {dragOverBottom ? <span className="drop-line bottom" /> : null}
      <div className="ti-title">
        {canDrag ? (
          <span
            className="tt-grip sm"
            draggable
            title="Перетащить задачу"
            onDragStart={onDragStart}
            onDragEnd={onDragEnd}
          >
            ⠿
          </span>
        ) : null}
        <span className="tt-tnum">{index + 1}</span>
        <span className="ti-title-text">{task.title}</span>
        {catalogLabel ? <span className="ti-title-sub muted">{catalogLabel}</span> : null}
      </div>
      <div className="ti-type muted">
        <Badge kind="muted">{formatActivityType(task)}</Badge>
      </div>
      <div className="ti-langs">
        {langs.length ? (
          langs.map((lang) => (
            <span key={lang} className="tt-langtag">
              {lang}
            </span>
          ))
        ) : (
          <span className="muted">—</span>
        )}
      </div>
      <div className="ti-diff">
        <DiffBadge diff={task.difficulty || task.diff} />
      </div>
      <div className="ti-updated" title="Время последнего изменения">
        {updatedStamp ? (
          <>
            <span className="ti-updated-time">{updatedStamp.time}</span>
            <span className="ti-updated-date">{updatedStamp.date}</span>
          </>
        ) : (
          <span className="muted">—</span>
        )}
      </div>
      <div className="ti-actions">
        <Link to={`/tasks/${task.id}`} className="btn btn-ghost btn-sm">
          Открыть
        </Link>
        {canEdit ? (
          <>
            <Link to={teacherTaskEditPath(task.id)} className="btn btn-secondary btn-sm">
              Редактировать
            </Link>
            {onDelete ? (
              <button type="button" className="btn btn-danger btn-sm" onClick={onDelete}>
                Удалить
              </button>
            ) : null}
          </>
        ) : null}
      </div>
    </div>
  )
}

export default function TeacherToxicTasksPanel({
  tasks = [],
  visibleTasks = [],
  catalogNameById,
  catalogs = [],
  groups = [],
  canManageCatalogs = false,
  onAssignCatalog,
  canEdit,
  search,
  onSearchChange,
  onTasksRefresh,
  loading = false,
  metaLoading = false,
  chapters = [],
  collectionMeta = [],
  courses = [],
  platformCourseMeta = null,
  onMetaRefresh,
  teacherProfile = null,
}: TeacherToxicTasksPanelProps) {
  const [catalogFilter, setCatalogFilter] = useState<CatalogFilter>("all")
  const [savingOrder, setSavingOrder] = useState(false)
  const [expandedChapters, setExpandedChapters] = useState<Record<string, boolean>>({})
  const [expandedTracks, setExpandedTracks] = useState<Record<string, boolean>>({})
  const [layoutOverrides, setLayoutOverrides] = useState<LayoutOverrides>({
    taskOrderByChapter: {},
    chapterOrder: null,
  })
  const dragRef = useRef<DragPayload | null>(null)
  const [dragTaskId, setDragTaskId] = useState<number | null>(null)
  const [dragChapterKey, setDragChapterKey] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [over, setOver] = useState<string | null>(null)
  const [chapterEditorOpen, setChapterEditorOpen] = useState(false)
  const [chapterEditorMode, setChapterEditorMode] = useState<"create" | "edit">("create")
  const [chapterEditorInitial, setChapterEditorInitial] = useState<CurriculumChapterDto | null>(null)
  const [collectionEditorOpen, setCollectionEditorOpen] = useState(false)
  const [collectionEditorInitial, setCollectionEditorInitial] = useState<CollectionMetaDto | null>(null)
  const [platformCourseEditorOpen, setPlatformCourseEditorOpen] = useState(false)
  const [editingCourse, setEditingCourse] = useState<TeacherCourseDto | null>(null)
  const [taskToDelete, setTaskToDelete] = useState<TaskRow | null>(null)
  const [chapterToDelete, setChapterToDelete] = useState<ChapterGroup | null>(null)
  const [deletingTask, setDeletingTask] = useState(false)
  const [deletingChapter, setDeletingChapter] = useState(false)

  const baseTasks = (visibleTasks.length ? visibleTasks : tasks) as TaskRow[]
  const sourceTasks = (tasks as TaskRow[]) || []
  const catalogMap = catalogNameById as Map<number, string>
  const catalogRows = catalogs as CatalogRow[]
  const editable = Boolean(canEdit)

  const reloadChapters = async () => {
    await onMetaRefresh?.()
  }

  const reloadCollectionMeta = async () => {
    await onMetaRefresh?.()
  }

  const reloadPlatformCourseMeta = async () => {
    await onMetaRefresh?.()
  }

  const orderFingerprint = useMemo(
    () =>
      baseTasks
        .map((task) => `${task.id}:${task.chapter_order ?? ""}:${task.display_order ?? ""}`)
        .join("|"),
    [baseTasks],
  )

  const collectionMetaByLang = useMemo(
    () => new Map(collectionMeta.map((row) => [row.language, row])),
    [collectionMeta],
  )

  const canDrag =
    editable &&
    !String(search || "").trim() &&
    !savingOrder

  useEffect(() => {
    setLayoutOverrides({ taskOrderByChapter: {}, chapterOrder: null })
  }, [orderFingerprint])

  const filtered = useMemo(() => {
    let rows = baseTasks
    if (catalogFilter === "assigned") {
      rows = rows.filter((t) => (t.catalog_ids?.length ?? 0) > 0)
    } else if (catalogFilter === "unassigned") {
      rows = rows.filter((t) => !(t.catalog_ids?.length ?? 0))
    }
    return rows
  }, [baseTasks, catalogFilter])

  const trackGroups = useMemo((): TrackGroup[] => {
    return buildTrackGroups(filtered, chapters)
  }, [filtered, chapters])

  const displayTrackGroups = useMemo((): TrackGroup[] => {
    return trackGroups
      .map((track) => ({
        ...track,
        chapters: applyLayoutOverrides(track.chapters, layoutOverrides).filter(
          (group) =>
            group.key !== "__none__" && (group.tasks.length > 0 || Boolean(group.isCustom)),
        ),
      }))
      .filter((track) => track.chapters.length > 0)
  }, [trackGroups, layoutOverrides])

  const resolvedCourses = useMemo((): TeacherCourseDto[] => {
    if (courses.length > 0) return courses
    return [
      {
        id: 0,
        title: platformCourseMeta?.title?.trim() || PLATFORM_COURSE.title,
        description: platformCourseMeta?.description?.trim() || PLATFORM_COURSE.description,
        is_default: true,
        task_count: sourceTasks.length,
        created_at: "",
        updated_at: platformCourseMeta?.updated_at ?? null,
      },
    ]
  }, [courses, platformCourseMeta, sourceTasks.length])

  const openCreateChapter = (language?: string) => {
    setChapterEditorMode("create")
    setChapterEditorInitial(
      language
        ? {
            language,
            chapter_key: "",
            title: "",
            description: "",
            sort_order: 0,
            is_custom: true,
            task_count: 0,
          }
        : null,
    )
    setChapterEditorOpen(true)
  }

  const openEditChapter = (group: ChapterGroup, trackLanguage: string) => {
    setChapterEditorMode("edit")
    setChapterEditorInitial({
      language: group.language || trackLanguage,
      chapter_key: group.key,
      title: group.title,
      description: group.description || "",
      sort_order: group.order,
      is_custom: group.isCustom ?? false,
      task_count: group.tasks.length,
    })
    setChapterEditorOpen(true)
  }

  const openEditCollection = (trackLanguage: string) => {
    const meta = collectionMetaByLang.get(trackLanguage)
    const trackMeta = CURRICULUM_LANGUAGE_OPTIONS.find((opt) => opt.id === trackLanguage)
    const defaultDescription =
      LANGUAGE_TRACK_DESCRIPTIONS[trackLanguage as keyof typeof LANGUAGE_TRACK_DESCRIPTIONS] || ""
    setCollectionEditorInitial(
      meta
        ? {
            ...meta,
            description: meta.description?.trim() || defaultDescription,
          }
        : {
            language: trackLanguage,
            title: trackMeta?.label || trackLanguage,
            description: defaultDescription,
            registry_title: trackMeta?.label || trackLanguage,
          },
    )
    setCollectionEditorOpen(true)
  }

  const handleChapterSaved = async () => {
    await reloadChapters()
    await onTasksRefresh?.()
  }

  const handleCollectionSaved = async () => {
    await reloadCollectionMeta()
  }

  const handlePlatformCourseSaved = async () => {
    setEditingCourse(null)
    await reloadPlatformCourseMeta()
  }

  const openEditCourse = (course: TeacherCourseDto) => {
    setEditingCourse(course)
    setPlatformCourseEditorOpen(true)
  }

  const openAssignChapter = (
    chapter: ChapterGroup,
    chapterTasks: TaskRow[],
    trackTitle: string,
  ) => {
    if (!canManageCatalogs || !onAssignCatalog) return
    const matchedCatalog = findCatalogForChapter(chapter.title, chapterTasks, catalogRows)
    if (matchedCatalog) {
      onAssignCatalog(matchedCatalog)
      return
    }
    toast.error(
      "Каталог не найден",
      `Создайте каталог «${chapter.title || trackTitle}» на вкладке «Каталоги» и добавьте в него курс.`,
    )
  }

  const chapterExpandKey = (trackId: string, chapterKey: string) => `${trackId}:${chapterKey}`

  const setOverIf = (key: string) => setOver((current) => (current === key ? current : key))

  const endDrag = () => {
    dragRef.current = null
    setDragTaskId(null)
    setDragChapterKey(null)
    setIsDragging(false)
    setOver(null)
  }

  const getTaskIdsForChapter = (chapterKey: string) => {
    const override = layoutOverrides.taskOrderByChapter[chapterKey]
    if (override?.length) return override
    for (const track of trackGroups) {
      const group = track.chapters.find((item) => item.key === chapterKey)
      if (group) return group.tasks.map((task) => task.id)
    }
    return []
  }

  const getChapterKeysOrdered = (groups: ChapterGroup[]) => {
    const override = layoutOverrides.chapterOrder
    if (override?.length) {
      const ordered = override
        .map((key) => groups.find((group) => group.key === key))
        .filter(Boolean) as ChapterGroup[]
      for (const group of groups) {
        if (!override.includes(group.key)) ordered.push(group)
      }
      return ordered.map((group) => group.key)
    }
    return groups.map((group) => group.key)
  }

  const startTaskDrag = (event: DragEvent, task: TaskRow, chapterKey: string) => {
    if (!canDrag || !chapterKey || chapterKey === "__none__") return
    event.stopPropagation()
    try {
      event.dataTransfer.setData("text/plain", String(task.id))
      event.dataTransfer.effectAllowed = "move"
    } catch {
      /* noop */
    }
    dragRef.current = { kind: "task", taskId: task.id, chapterKey }
    setDragTaskId(task.id)
    setIsDragging(true)
  }

  const startChapterDrag = (event: DragEvent, chapterKey: string, trackId: string) => {
    if (!canDrag || chapterKey === "__none__") return
    event.stopPropagation()
    try {
      event.dataTransfer.setData("text/plain", chapterKey)
      event.dataTransfer.effectAllowed = "move"
    } catch {
      /* noop */
    }
    dragRef.current = { kind: "chapter", chapterKey, trackId }
    setDragChapterKey(chapterKey)
    setIsDragging(true)
  }

  const persistTaskOrder = async (chapterKey: string, orderedIds: number[]) => {
    const previousOverride = layoutOverrides.taskOrderByChapter[chapterKey]
    setLayoutOverrides((current) => ({
      ...current,
      taskOrderByChapter: { ...current.taskOrderByChapter, [chapterKey]: orderedIds },
    }))
    setSavingOrder(true)
    try {
      await updateChapterTaskOrder(chapterKey, orderedIds)
      await onTasksRefresh?.()
      toast.push({ kind: "lime", title: "Порядок задач сохранён" })
    } catch (err: unknown) {
      setLayoutOverrides((current) => {
        const next = { ...current.taskOrderByChapter }
        if (previousOverride) next[chapterKey] = previousOverride
        else delete next[chapterKey]
        return { ...current, taskOrderByChapter: next }
      })
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось сохранить порядок задач"
      toast.error("Ошибка", message)
    } finally {
      setSavingOrder(false)
    }
  }

  const persistChapterOrder = async (orderedKeys: string[]) => {
    const curriculumKeys = orderedKeys.filter((key) => key !== "__none__")
    if (curriculumKeys.length === 0) return
    const previousOverride = layoutOverrides.chapterOrder
    setLayoutOverrides((current) => ({
      ...current,
      chapterOrder: orderedKeys,
    }))
    setSavingOrder(true)
    try {
      await updateCollectionChapterOrder(curriculumKeys)
      await onTasksRefresh?.()
      toast.push({ kind: "lime", title: "Порядок глав сохранён" })
    } catch (err: unknown) {
      setLayoutOverrides((current) => ({
        ...current,
        chapterOrder: previousOverride,
      }))
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось сохранить порядок глав"
      toast.error("Ошибка", message)
    } finally {
      setSavingOrder(false)
    }
  }

  const moveTaskInChapter = (chapterKey: string, taskId: number, index: number) => {
    const currentIds = getTaskIdsForChapter(chapterKey)
    const nextIds = reorderIds(currentIds, taskId, index)
    if (nextIds.join(",") === currentIds.join(",")) return
    void persistTaskOrder(chapterKey, nextIds)
  }

  const moveChapter = (
    trackId: string,
    chapterKey: string,
    index: number,
    groups: ChapterGroup[],
  ) => {
    const currentKeys = getChapterKeysOrdered(groups)
    const nextKeys = reorderKeys(currentKeys, chapterKey, index)
    if (nextKeys.join(",") === currentKeys.join(",")) return
    void persistChapterOrder(nextKeys)
  }

  const toggleChapter = (trackId: string, chapterKey: string) => {
    const key = chapterExpandKey(trackId, chapterKey)
    setExpandedChapters((cur) => ({ ...cur, [key]: !cur[key] }))
  }

  const isChapterOpen = (trackId: string, chapterKey: string) =>
    Boolean(expandedChapters[chapterExpandKey(trackId, chapterKey)])

  const toggleTrack = (trackId: string) => {
    setExpandedTracks((cur) => ({ ...cur, [trackId]: !cur[trackId] }))
  }

  const isTrackOpen = (trackId: string) => Boolean(expandedTracks[trackId])

  const confirmDeleteTask = async () => {
    if (!taskToDelete) return
    setDeletingTask(true)
    try {
      const result = await deleteCatalogTask(taskToDelete.id)
      if (result.action === "archived") {
        toast.push({
          kind: "info",
          title: "Задание скрыто",
          body: taskToDelete.title,
        })
      } else {
        toast.push({
          kind: "lime",
          title: "Задание удалено",
          body: taskToDelete.title,
        })
      }
      setTaskToDelete(null)
      await onTasksRefresh?.()
      window.dispatchEvent(new Event("teacher-tasks-changed"))
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось удалить задание"
      toast.error("Ошибка", String(message))
    } finally {
      setDeletingTask(false)
    }
  }

  const confirmDeleteChapter = async () => {
    if (!chapterToDelete) return
    setDeletingChapter(true)
    try {
      await deleteCurriculumChapter(chapterToDelete.key, chapterToDelete.language)
      toast.push({
        kind: "lime",
        title: "Глава удалена",
        body: chapterToDelete.title,
      })
      setChapterToDelete(null)
      await reloadChapters()
      await onTasksRefresh?.()
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось удалить главу"
      toast.error("Ошибка", String(message))
    } finally {
      setDeletingChapter(false)
    }
  }

  const totalCount = filtered.length
  const hasSearch = Boolean(String(search || "").trim())
  const emptyState = emptyStateText(sourceTasks.length, catalogFilter, hasSearch)
  const courseTitle = platformCourseMeta?.title?.trim() || PLATFORM_COURSE.title
  const courseDescription = platformCourseMeta?.description?.trim() || PLATFORM_COURSE.description
  const courseGlyph = deriveLabelGlyph(courseTitle)
  const nTracks = displayTrackGroups.length
  const isLoadingTasks = loading && sourceTasks.length === 0
  const isLoadingLayout = metaLoading && sourceTasks.length > 0 && displayTrackGroups.length === 0
  const showLoading = isLoadingTasks || isLoadingLayout
  const showEmpty = !loading && !metaLoading && sourceTasks.length === 0 && courses.length === 0

  return (
    <div className="teacher-tasks-panel">
      <div className="card card-pad" style={{ padding: 12, marginBottom: 14 }}>
        <div className="tt-toolbar">
          <input
            className="input tt-toolbar-search"
            placeholder="Поиск среди ваших задач…"
            value={search as string}
            onChange={(e: unknown) =>
              onSearchChange((e as { target: { value: string } }).target.value)
            }
          />
          <select
            className="select tt-toolbar-select"
            value={catalogFilter}
            onChange={(e) => setCatalogFilter(e.target.value as CatalogFilter)}
            aria-label="Фильтр по каталогу"
          >
            <option value="all">Все задачи</option>
            <option value="assigned">В каталогах</option>
            <option value="unassigned">Без каталога</option>
          </select>
          {editable ? (
            <Link to={teacherTaskCreatePath()} className="btn btn-primary btn-sm">
              + Создать задачу
            </Link>
          ) : null}
        </div>
      </div>

      <div
          className="mut3"
          style={{ fontSize: 12.5, margin: "0 0 14px", display: "flex", alignItems: "center", gap: 7 }}
        >
          <span style={{ fontSize: 14 }}>⠿</span>
          {showLoading
            ? "Загрузка задач и структуры курса…"
            : displayTrackGroups.length === 0
              ? "Ваши задачи. Общие курсы платформы доступны в разделе «Курсы»."
              : canDrag
                ? "Перетаскивайте задачи между главами, а главы — между языковыми сборниками. Это один курс на пяти языках."
                : String(search || "").trim()
                  ? "Очистите поиск, чтобы менять порядок перетаскиванием."
                  : PLATFORM_COURSE.teacherHint}
      </div>

      {showLoading ? (
        <div className="card card-pad tt-loading-card">
          <p className="muted" style={{ margin: 0, textAlign: "center", padding: "28px 0" }}>
            Загрузка задач…
          </p>
        </div>
      ) : showEmpty ? (
        <div className="card card-pad">
          <EmptyState icon={emptyState.icon} title={emptyState.title} text={emptyState.text} />
          {editable ? (
            <div style={{ marginTop: 16, display: "flex", gap: 8, flexWrap: "wrap" }}>
              <Link to={teacherTaskCreatePath()} className="btn btn-primary btn-sm">
                + Создать задачу
              </Link>
            </div>
          ) : null}
        </div>
      ) : totalCount === 0 ? (
        <div className="card card-pad">
          <EmptyState icon={emptyState.icon} title={emptyState.title} text={emptyState.text} />
        </div>
      ) : displayTrackGroups.length === 0 && !resolvedCourses.some((course) => course.is_default) ? (
        <div className="card card-pad">
          <div className="tt-rows">
            {filtered.map((task, taskIndex) => (
              <TaskRowView
                key={task.id}
                task={task}
                index={taskIndex}
                catalogNameById={catalogMap}
                canEdit={editable}
                canDrag={false}
                isDragging={false}
                dragOverTop={false}
                dragOverBottom={false}
                onDragStart={() => undefined}
                onDragEnd={() => undefined}
                onRowDragOver={() => undefined}
                onRowDrop={() => undefined}
                onDelete={editable ? () => setTaskToDelete(task) : undefined}
              />
            ))}
          </div>
        </div>
      ) : (
        <>
          <div className="tt-collections">
            {resolvedCourses.map((course) => {
              const sectionTitle = course.title?.trim() || PLATFORM_COURSE.title
              const sectionDescription = course.description?.trim() || ""
              const sectionGlyph = deriveLabelGlyph(sectionTitle)
              return (
            <div key={course.id} className="tt-collection">
              <div className="tt-coll-head">
                <span className="tt-coll-ico">{sectionGlyph}</span>
                <div className="tt-coll-title-wrap">
                  <span className="tt-coll-name">{sectionTitle}</span>
                  {sectionDescription ? (
                    <p className="tt-coll-desc muted">{sectionDescription}</p>
                  ) : null}
                </div>
                {editable && course.id > 0 ? (
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm tt-meta-edit"
                    onClick={() => openEditCourse(course)}
                  >
                    Изменить курс
                  </button>
                ) : null}
                {course.is_default ? (
                  <span className="gcount">
                    {nTracks} {plural(nTracks, "трек", "трека", "треков")}
                  </span>
                ) : (
                  <span className="gcount">{course.task_count} задач</span>
                )}
              </div>
              {course.is_default ? (
              <div className="tt-coll-body">
                {displayTrackGroups.map((track) => {
                  const trackMeta = CURRICULUM_LANGUAGE_OPTIONS.find((opt) => opt.id === track.id)
                  const collectionRow = collectionMetaByLang.get(track.id)
                  const trackTitle = collectionRow?.title || track.label
                  const trackDescription =
                    collectionRow?.description?.trim() ||
                    LANGUAGE_TRACK_DESCRIPTIONS[track.id as keyof typeof LANGUAGE_TRACK_DESCRIPTIONS] ||
                    ""
                  const nCh = track.chapters.length
                  const trackOpen = isTrackOpen(track.id)
                  const chapterDrag = canDrag && isDragging && dragRef.current?.kind === "chapter"
                  return (
                    <div key={track.id} className={`tt-group${trackOpen ? " open" : ""}`}>
                      <div className="tt-ghead tt-ghead-track">
                        <button
                          type="button"
                          className="tt-ghead-btn"
                          onClick={() => toggleTrack(track.id)}
                        >
                          <span className="caret">▶</span>
                          <span className="tt-track-glyph">{trackMeta?.glyph ?? "📚"}</span>
                          <span className="tt-glabel">Трек</span>
                          <span className="gtitle">{trackTitle}</span>
                        </button>
                        {trackDescription ? (
                          <span className="tt-track-desc muted">{trackDescription}</span>
                        ) : null}
                        {editable ? (
                          <>
                            <button
                              type="button"
                              className="btn btn-ghost btn-sm tt-meta-edit"
                              onClick={() => openEditCollection(track.id)}
                            >
                              Изменить
                            </button>
                            <button
                              type="button"
                              className="btn btn-add-chapter btn-sm"
                              onClick={() => openCreateChapter(track.id)}
                            >
                              + Добавить главу
                            </button>
                          </>
                        ) : null}
                        <span className="gcount">
                          {nCh} {plural(nCh, "глава", "главы", "глав")}
                        </span>
                      </div>
                      {trackOpen ? (
                        <div
                          className="tt-track-body"
                          onDragOver={
                            chapterDrag
                              ? (event) => {
                                  const drag = dragRef.current
                                  if (!drag || drag.kind !== "chapter" || drag.trackId !== track.id) return
                                  event.preventDefault()
                                  event.dataTransfer.dropEffect = "move"
                                  setOverIf(`c:${track.id}:${nCh}`)
                                }
                              : undefined
                          }
                          onDrop={
                            chapterDrag
                              ? (event) => {
                                  const drag = dragRef.current
                                  if (!drag || drag.kind !== "chapter" || drag.trackId !== track.id) return
                                  event.preventDefault()
                                  moveChapter(track.id, drag.chapterKey, nCh, track.chapters)
                                  endDrag()
                                }
                              : undefined
                          }
                        >
                          {nCh === 0 ? (
                            <div className="tt-coll-empty">Глав пока нет</div>
                          ) : (
                            track.chapters.map((group, groupIndex) => {
                              const open = isChapterOpen(track.id, group.key)
                              const chapterKey = group.key
                              const canDragChapter = Boolean(canDrag && chapterKey)
                              const items = group.tasks
                              const taskDrag = canDrag && isDragging && dragRef.current?.kind === "task"
                              const before =
                                chapterDrag &&
                                over === `c:${track.id}:${groupIndex}`
                              const after =
                                chapterDrag &&
                                groupIndex === nCh - 1 &&
                                over === `c:${track.id}:${nCh}`
                              const rowsEndOn = taskDrag && over === `t:${chapterKey}:${items.length}`
                              const draggingThisCh =
                                isDragging &&
                                dragRef.current?.kind === "chapter" &&
                                dragChapterKey === group.key

                              return (
                                <div
                                  key={`${track.id}:${group.key}`}
                                  className={`tt-group${open ? " open" : ""}${draggingThisCh ? " is-dragging" : ""}`}
                                  onDragOver={
                                    canDragChapter
                                      ? (event) => {
                                          const drag = dragRef.current
                                          if (!drag) return
                                          if (drag.kind === "chapter") {
                                            if (drag.trackId !== track.id) return
                                            event.preventDefault()
                                            event.stopPropagation()
                                            event.dataTransfer.dropEffect = "move"
                                            setOverIf(
                                              `c:${track.id}:${halfDropIndex(event, groupIndex)}`,
                                            )
                                            return
                                          }
                                          if (drag.kind !== "task" || drag.chapterKey !== chapterKey) return
                                          event.preventDefault()
                                          event.dataTransfer.dropEffect = "move"
                                          setOverIf(`t:${chapterKey}:${items.length}`)
                                        }
                                      : undefined
                                  }
                                  onDrop={
                                    canDragChapter
                                      ? (event) => {
                                          const drag = dragRef.current
                                          if (!drag) return
                                          event.preventDefault()
                                          if (drag.kind === "chapter") {
                                            if (drag.trackId !== track.id) return
                                            moveChapter(
                                              track.id,
                                              drag.chapterKey,
                                              halfDropIndex(event, groupIndex),
                                              track.chapters,
                                            )
                                            endDrag()
                                            return
                                          }
                                          if (drag.kind !== "task" || drag.chapterKey !== chapterKey) return
                                          moveTaskInChapter(chapterKey, drag.taskId, items.length)
                                          endDrag()
                                        }
                                      : undefined
                                  }
                                >
                                  {before ? <span className="drop-line top" /> : null}
                                  {after ? <span className="drop-line bottom" /> : null}
                                  <div className="tt-ghead">
                                    {canDragChapter ? (
                                      <span
                                        className="tt-grip"
                                        draggable
                                        title="Перетащить главу"
                                        onDragStart={(event) =>
                                          startChapterDrag(event, chapterKey, track.id)
                                        }
                                        onDragEnd={endDrag}
                                      >
                                        ⠿
                                      </span>
                                    ) : null}
                                    <button
                                      type="button"
                                      className="tt-ghead-btn"
                                      onClick={() => toggleChapter(track.id, group.key)}
                                    >
                                      <span className="caret">▶</span>
                                      <span className="tt-gnum">{groupIndex + 1}</span>
                                      <span className="tt-glabel">Глава</span>
                                      <span className="gtitle">{group.title}</span>
                                    </button>
                                    {editable ? (
                                      <button
                                        type="button"
                                        className="btn btn-ghost btn-sm tt-meta-edit"
                                        onClick={(event) => {
                                          event.stopPropagation()
                                          openEditChapter(group, track.id)
                                        }}
                                      >
                                        Изменить
                                      </button>
                                    ) : null}
                                    {canManageCatalogs && onAssignCatalog ? (
                                      <button
                                        type="button"
                                        className="btn btn-secondary btn-sm"
                                        onClick={(event) => {
                                          event.stopPropagation()
                                          openAssignChapter(group, items, trackTitle)
                                        }}
                                      >
                                        Назначить группе
                                      </button>
                                    ) : null}
                                    {editable && group.isCustom && items.length === 0 ? (
                                      <button
                                        type="button"
                                        className="btn btn-danger btn-sm"
                                        onClick={(event) => {
                                          event.stopPropagation()
                                          setChapterToDelete(group)
                                        }}
                                      >
                                        Удалить
                                      </button>
                                    ) : null}
                                    <span className="gcount">
                                      {items.length}{" "}
                                      {plural(items.length, "задача", "задачи", "задач")}
                                    </span>
                                  </div>
                                  {open ? (
                                    <div
                                      className="tt-rows"
                                      onDragOver={
                                        taskDrag
                                          ? (event) => {
                                              event.preventDefault()
                                              event.dataTransfer.dropEffect = "move"
                                              setOverIf(`t:${chapterKey}:${items.length}`)
                                            }
                                          : undefined
                                      }
                                      onDrop={
                                        taskDrag
                                          ? (event) => {
                                              const drag = dragRef.current
                                              if (!drag || drag.kind !== "task") return
                                              event.preventDefault()
                                              moveTaskInChapter(chapterKey, drag.taskId, items.length)
                                              endDrag()
                                            }
                                          : undefined
                                      }
                                    >
                                      {group.description?.trim() ? (
                                        <p className="tt-chapter-desc muted">{group.description}</p>
                                      ) : null}
                                      {items.length === 0 ? (
                                        <div
                                          className={`tt-coll-empty${over === `t:${chapterKey}:0` ? " on" : ""}`}
                                          style={{ margin: 0 }}
                                        >
                                          В этой главе пока нет задач
                                        </div>
                                      ) : (
                                        items.map((task, taskIndex) => {
                                          const dropKey = `t:${chapterKey}:${taskIndex}`
                                          const dropAfterKey = `t:${chapterKey}:${taskIndex + 1}`
                                          const draggingThis =
                                            dragTaskId === task.id &&
                                            isDragging &&
                                            dragRef.current?.kind === "task"
                                          return (
                                            <TaskRowView
                                              key={task.id}
                                              task={task}
                                              index={taskIndex}
                                              catalogNameById={catalogMap}
                                              canEdit={editable}
                                              canDrag={Boolean(canDrag && chapterKey)}
                                              isDragging={draggingThis}
                                              dragOverTop={taskDrag && over === dropKey}
                                              dragOverBottom={
                                                taskDrag &&
                                                (over === dropAfterKey ||
                                                  (taskIndex === items.length - 1 && rowsEndOn))
                                              }
                                              onDragStart={(event) => {
                                                startTaskDrag(event, task, chapterKey)
                                              }}
                                              onDragEnd={endDrag}
                                              onRowDragOver={(event) => {
                                                const drag = dragRef.current
                                                if (!canDrag || !chapterKey || !drag || drag.kind !== "task")
                                                  return
                                                if (drag.chapterKey !== chapterKey) return
                                                event.preventDefault()
                                                event.stopPropagation()
                                                event.dataTransfer.dropEffect = "move"
                                                setOverIf(
                                                  `t:${chapterKey}:${halfDropIndex(event, taskIndex)}`,
                                                )
                                              }}
                                              onRowDrop={(event) => {
                                                const drag = dragRef.current
                                                if (!canDrag || !chapterKey || !drag || drag.kind !== "task")
                                                  return
                                                if (drag.chapterKey !== chapterKey) return
                                                event.preventDefault()
                                                event.stopPropagation()
                                                moveTaskInChapter(
                                                  chapterKey,
                                                  drag.taskId,
                                                  halfDropIndex(event, taskIndex),
                                                )
                                                endDrag()
                                              }}
                                              onDelete={
                                                editable
                                                  ? () => setTaskToDelete(task)
                                                  : undefined
                                              }
                                            />
                                          )
                                        })
                                      )}
                                    </div>
                                  ) : null}
                                </div>
                              )
                            })
                          )}
                        </div>
                      ) : null}
                    </div>
                  )
                })}
              </div>
              ) : (
                <div className="tt-coll-body" style={{ padding: "16px 12px" }}>
                  <p className="muted" style={{ margin: 0 }}>
                    Дополнительный курс. Его можно добавить в каталог на вкладке «Каталоги».
                  </p>
                </div>
              )}
            </div>
              )
            })}
          </div>
        </>
      )}
      <TeacherChapterEditorModal
        open={chapterEditorOpen}
        mode={chapterEditorMode}
        initial={chapterEditorInitial}
        onClose={() => setChapterEditorOpen(false)}
        onSaved={() => void handleChapterSaved()}
      />
      <TeacherCollectionEditorModal
        open={collectionEditorOpen}
        initial={collectionEditorInitial}
        onClose={() => setCollectionEditorOpen(false)}
        onSaved={() => void handleCollectionSaved()}
      />
      <TeacherPlatformCourseEditorModal
        open={platformCourseEditorOpen}
        mode="edit"
        courseId={editingCourse?.id ?? null}
        initial={{
          title: editingCourse?.title || courseTitle,
          description: editingCourse?.description || courseDescription,
        }}
        onClose={() => {
          setPlatformCourseEditorOpen(false)
          setEditingCourse(null)
        }}
        onSaved={() => void handlePlatformCourseSaved()}
      />
      <ConfirmDialog
        open={Boolean(taskToDelete)}
        title="Удалить задание?"
        message={
          taskToDelete
            ? `Задание «${taskToDelete.title}» будет удалено из кабинета.`
            : ""
        }
        confirmLabel="Удалить"
        cancelLabel="Отмена"
        loading={deletingTask}
        onConfirm={() => void confirmDeleteTask()}
        onCancel={() => setTaskToDelete(null)}
      />
      <ConfirmDialog
        open={Boolean(chapterToDelete)}
        title="Удалить главу?"
        message={
          chapterToDelete
            ? `Глава «${chapterToDelete.title}» будет удалена без возможности восстановления.`
            : ""
        }
        confirmLabel="Удалить"
        cancelLabel="Отмена"
        loading={deletingChapter}
        onConfirm={() => void confirmDeleteChapter()}
        onCancel={() => setChapterToDelete(null)}
      />
    </div>
  )
}
