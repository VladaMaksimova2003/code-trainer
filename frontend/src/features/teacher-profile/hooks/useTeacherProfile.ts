import { useEffect, useState } from "react"
import {
  getMyTeacherProfile,
  getTeacherActivity,
  getTeacherProfile,
  getTeacherTasksList,
} from "@/shared/api"
import { createTeacherGroup, deleteTeacherGroup, generateGroupInvitation, listMyTeacherGroups } from "@/features/groups/api/groupsApi"
import {
  createCatalog,
  deleteCatalog,
  getPlatformCourseMeta,
  listCatalogTasks,
  listCollectionMeta,
  listCurriculumChapters,
  listMyCatalogs,
  listTeacherCourses,
  type TeacherCourseDto,
  updateChapterTaskOrder,
} from "@/features/task-catalog/infrastructure/catalogApi"
import { getTeacherAnalytics } from "@/features/analytics/api/analyticsApi"
import { toast } from "@/shared/ui/toast"
import { copyTextToClipboard } from "@/shared/utils/copyToClipboard"

function readError(err, fallback) {
  return err?.response?.data?.detail || err?.message || fallback
}

export function useTeacherProfile({ enabled = true, activeTab = null, viewTeacherId = null, viewOnly = false } = {}) {
  const [profile, setProfile] = useState(null)
  const [tasks, setTasks] = useState([])
  const [catalogs, setCatalogs] = useState([])
  const [groups, setGroups] = useState([])
  const [activity, setActivity] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(() => Boolean(enabled))
  const [tasksLoading, setTasksLoading] = useState(() => Boolean(enabled))
  const [metaLoading, setMetaLoading] = useState(false)
  const [catalogsLoading, setCatalogsLoading] = useState(false)
  const [chapters, setChapters] = useState([])
  const [collectionMeta, setCollectionMeta] = useState([])
  const [platformCourseMeta, setPlatformCourseMeta] = useState(null)
  const [courses, setCourses] = useState<TeacherCourseDto[]>([])

  const [search, setSearch] = useState("")
  const [newCatalogTitle, setNewCatalogTitle] = useState("")
  const [newCatalogDescription, setNewCatalogDescription] = useState("")
  const [newCatalogPrivate, setNewCatalogPrivate] = useState(false)
  const [newCatalogGroupId, setNewCatalogGroupId] = useState("")

  const [newGroupName, setNewGroupName] = useState("")
  const [inviteByGroupId, setInviteByGroupId] = useState({})
  const [invitingGroupId, setInvitingGroupId] = useState(null)
  const [deletingGroupId, setDeletingGroupId] = useState(null)

  const [catalogToDelete, setCatalogToDelete] = useState(null)
  const [deletingCatalog, setDeletingCatalog] = useState(false)
  const [catalogToAssign, setCatalogToAssign] = useState(null)

  const [selectedGroup, setSelectedGroup] = useState(null)

  const [analytics, setAnalytics] = useState(null)
  const [analyticsLoading, setAnalyticsLoading] = useState(false)

  useEffect(() => {
    if (!enabled) return undefined
    let cancelled = false
    async function loadProfile() {
      setLoading(true)
      setError(null)
      try {
        const prof = viewTeacherId
          ? await getTeacherProfile(viewTeacherId)
          : await getMyTeacherProfile()
        if (cancelled) return
        setProfile(prof)
        if (viewTeacherId) {
          setGroups(Array.isArray(prof.groups) ? prof.groups : [])
          setCatalogs(
            (prof.collections || []).map((c: { id?: number; name?: string; title?: string }) => ({
              id: c.id,
              title: c.name || c.title,
            })),
          )
        }
      } catch (err) {
        if (!cancelled) {
          setError(readError(err, "Не удалось загрузить профиль преподавателя"))
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadProfile()
    return () => {
      cancelled = true
    }
  }, [enabled, viewTeacherId])

  useEffect(() => {
    if (!enabled || viewTeacherId) return undefined
    let cancelled = false
    setCatalogsLoading(true)
    Promise.allSettled([listMyCatalogs(), listMyTeacherGroups()])
      .then(([catalogResult, groupResult]) => {
        if (cancelled) return
        if (catalogResult.status === "fulfilled") setCatalogs(catalogResult.value)
        if (groupResult.status === "fulfilled") setGroups(groupResult.value)
      })
      .finally(() => {
        if (!cancelled) setCatalogsLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [enabled, viewTeacherId])

  useEffect(() => {
    if (!enabled || activeTab !== "catalogs" || viewTeacherId) return undefined
    if (catalogs.length > 0) return undefined
    let cancelled = false
    setCatalogsLoading(true)
    Promise.allSettled([listMyCatalogs(), listMyTeacherGroups()])
      .then(([catalogResult, groupResult]) => {
        if (cancelled) return
        if (catalogResult.status === "fulfilled") setCatalogs(catalogResult.value)
        if (groupResult.status === "fulfilled") setGroups(groupResult.value)
      })
      .finally(() => {
        if (!cancelled) setCatalogsLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [enabled, activeTab, viewTeacherId, catalogs.length])

  useEffect(() => {
    if (!enabled || activeTab !== "tasks") return undefined
    let cancelled = false
    async function loadTasksTab() {
      setTasksLoading(true)
      setMetaLoading(!viewTeacherId)
      try {
        if (viewTeacherId) {
          const taskList = await getTeacherTasksList(viewTeacherId)
          if (!cancelled) setTasks(taskList || [])
          return
        }
        const [taskResult, catalogResult, groupResult, chaptersResult, collectionsResult, courseResult, coursesResult] =
          await Promise.allSettled([
            listCatalogTasks(),
            listMyCatalogs(),
            listMyTeacherGroups(),
            listCurriculumChapters(),
            listCollectionMeta(),
            getPlatformCourseMeta(),
            listTeacherCourses(),
          ])
        if (cancelled) return
        if (taskResult.status === "fulfilled") {
          setTasks(taskResult.value)
        } else {
          setTasks([])
          const message = readError(taskResult.reason, "Не удалось загрузить список задач")
          setError(message)
          toast.error("Не удалось загрузить задачи", message)
        }
        if (catalogResult.status === "fulfilled") {
          setCatalogs(catalogResult.value)
        }
        if (groupResult.status === "fulfilled") {
          setGroups(groupResult.value)
        }
        if (chaptersResult.status === "fulfilled") {
          setChapters(chaptersResult.value)
        }
        if (collectionsResult.status === "fulfilled") {
          setCollectionMeta(collectionsResult.value)
        }
        if (courseResult.status === "fulfilled") {
          setPlatformCourseMeta(courseResult.value)
        }
        if (coursesResult.status === "fulfilled") {
          setCourses(coursesResult.value)
        }
      } finally {
        if (!cancelled) {
          setTasksLoading(false)
          setMetaLoading(false)
        }
      }
    }
    loadTasksTab()
    return () => {
      cancelled = true
    }
  }, [enabled, activeTab, viewTeacherId])

  useEffect(() => {
    if (!enabled || activeTab !== "groups" || viewTeacherId) return undefined
    let cancelled = false
    listMyTeacherGroups()
      .then((groupList) => {
        if (!cancelled) setGroups(groupList)
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [enabled, activeTab, viewTeacherId])

  useEffect(() => {
    if (!enabled || activeTab !== "solutions") return undefined
    let cancelled = false
    if (viewTeacherId) return undefined
    Promise.allSettled([listMyCatalogs(), listMyTeacherGroups()]).then(([catalogResult, groupResult]) => {
      if (cancelled) return
      if (catalogResult.status === "fulfilled") setCatalogs(catalogResult.value)
      if (groupResult.status === "fulfilled") setGroups(groupResult.value)
    })
    return () => {
      cancelled = true
    }
  }, [enabled, activeTab, viewTeacherId])

  useEffect(() => {
    if (!enabled || activeTab !== "analytics") return undefined
    let cancelled = false
    const teacherId = viewTeacherId || profile?.user_id
    if (!teacherId) return undefined
    getTeacherActivity(teacherId)
      .then((data) => {
        if (!cancelled) setActivity(data)
      })
      .catch(() => {
        if (!cancelled) setActivity(null)
      })
    return () => {
      cancelled = true
    }
  }, [enabled, activeTab, viewTeacherId, profile?.user_id])

  useEffect(() => {
    if (!enabled || activeTab !== "tasks") return undefined
    let cancelled = false

    async function reloadTasks() {
      setTasksLoading(true)
      try {
        if (viewTeacherId) {
          const taskList = await getTeacherTasksList(viewTeacherId)
          if (!cancelled) setTasks(taskList || [])
          return
        }
        const taskList = await listCatalogTasks()
        if (!cancelled) setTasks(taskList)
      } catch {
        /* keep current list on transient errors */
      } finally {
        if (!cancelled) setTasksLoading(false)
      }
    }

    const onTasksChanged = () => {
      void reloadTasks()
    }

    window.addEventListener("teacher-tasks-changed", onTasksChanged)

    return () => {
      cancelled = true
      window.removeEventListener("teacher-tasks-changed", onTasksChanged)
    }
  }, [enabled, activeTab, viewTeacherId])

  useEffect(() => {
    if (!enabled || activeTab !== "analytics") return undefined
    let cancelled = false
    setAnalyticsLoading(true)
    getTeacherAnalytics()
      .then((data: unknown) => {
        if (!cancelled) setAnalytics(data)
      })
      .catch(() => {
        if (!cancelled) setAnalytics(null)
      })
      .finally(() => {
        if (!cancelled) setAnalyticsLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [enabled, activeTab])

  const canEditTasks = viewOnly ? false : Boolean(profile?.permissions?.edit_tasks)
  const canManageGroups = viewOnly ? false : Boolean(profile?.permissions?.manage_groups ?? enabled)
  const canManageCatalogs = viewOnly ? false : Boolean(profile?.permissions?.manage_catalogs ?? enabled)
  const catalogNameById = new Map(catalogs.map((c: unknown) => [c.id, c.title]))
  const groupNameById = new Map(groups.map((g: unknown) => [g.id, g.name]))

  const refreshCatalogs = async () => {
    const catalogList = await listMyCatalogs()
    setCatalogs(catalogList)
  }

  const refreshGroups = async () => {
    const groupList = await listMyTeacherGroups()
    setGroups(groupList)
  }

  const refreshTasks = async () => {
    setTasksLoading(true)
    try {
      const taskList = await listCatalogTasks()
      setTasks(taskList)
    } finally {
      setTasksLoading(false)
    }
  }

  const refreshTasksMeta = async () => {
    if (viewTeacherId) return
    setMetaLoading(true)
    try {
      const [chaptersResult, collectionsResult, courseResult, coursesResult] = await Promise.allSettled([
        listCurriculumChapters(),
        listCollectionMeta(),
        getPlatformCourseMeta(),
        listTeacherCourses(),
      ])
      if (chaptersResult.status === "fulfilled") setChapters(chaptersResult.value)
      if (collectionsResult.status === "fulfilled") setCollectionMeta(collectionsResult.value)
      if (courseResult.status === "fulfilled") setPlatformCourseMeta(courseResult.value)
      if (coursesResult.status === "fulfilled") setCourses(coursesResult.value)
    } finally {
      setMetaLoading(false)
    }
  }

  const refreshCourses = async () => {
    if (viewTeacherId) return
    const [courseResult, coursesResult] = await Promise.allSettled([
      getPlatformCourseMeta(),
      listTeacherCourses(),
    ])
    if (courseResult.status === "fulfilled") setPlatformCourseMeta(courseResult.value)
    if (coursesResult.status === "fulfilled") setCourses(coursesResult.value)
  }

  const normalizedSearch = search.trim().toLowerCase()
  const visibleTasks = normalizedSearch
    ? tasks.filter((task: unknown) => {
        const catalogNames = task.catalog_ids?.map((id: unknown) => catalogNameById.get(id) || "").join(" ").toLowerCase()
        return [task.title, task.content, task.type_id, task.activity_label, task.chapter_title, catalogNames]
          .filter(Boolean)
          .some((v: unknown) => String(v).toLowerCase().includes(normalizedSearch))
      })
    : tasks

  const handleCreateCatalog = async (event: unknown) => {
    event.preventDefault()
    if (!newCatalogTitle.trim()) return
    setError(null)
    try {
      const catalog = await createCatalog({
        title: newCatalogTitle.trim(),
        description: newCatalogDescription.trim() || null,
        visibility: newCatalogPrivate ? "private" : "public",
        group_id: newCatalogPrivate && newCatalogGroupId !== "" ? Number(newCatalogGroupId) : null,
      })
      setCatalogs((cur: unknown) => [catalog, ...cur])
      setNewCatalogTitle("")
      setNewCatalogDescription("")
      setNewCatalogPrivate(false)
      setNewCatalogGroupId("")
      toast.push({
        kind: "lime",
        title: "Каталог создан",
        body: catalog.title || newCatalogTitle.trim(),
      })
    } catch (err) {
      const message = readError(err, "Не удалось создать каталог")
      setError(message)
      toast.error("Не удалось создать каталог", message)
    }
  }

  const handleDeleteCatalog = async () => {
    if (!catalogToDelete) return
    setDeletingCatalog(true)
    setError(null)
    const title = catalogToDelete.title
    try {
      await deleteCatalog(catalogToDelete.id)
      setCatalogs((cur: unknown) => cur.filter((c: unknown) => c.id !== catalogToDelete.id))
      setCatalogToDelete(null)
      toast.push({ kind: "lime", title: "Каталог удалён", body: title })
    } catch (err) {
      const message = readError(err, "Не удалось удалить каталог")
      setError(message)
      toast.error("Не удалось удалить каталог", message)
    } finally {
      setDeletingCatalog(false)
    }
  }

  const handleCreateGroup = async (event: unknown) => {
    event.preventDefault()
    if (!newGroupName.trim()) return
    setError(null)
    try {
      const group = await createTeacherGroup({ name: newGroupName.trim() })
      setGroups((cur: unknown) => [group, ...cur])
      setNewGroupName("")
      toast.push({ kind: "lime", title: "Группа создана", body: group.name })
      refreshGroups().catch(() => {})
    } catch (err) {
      const message = readError(err, "Не удалось создать группу")
      setError(message)
      toast.error("Не удалось создать группу", message)
    }
  }

  const handleGenerateInvite = async (group, options = {}) => {
    const silent = Boolean(options.silent)
    setInvitingGroupId(group.id)
    setError(null)
    try {
      const invite = await generateGroupInvitation(group.id, { max_uses: null, expires_in_days: 30 })
      setInviteByGroupId((cur: unknown) => ({ ...cur, [group.id]: invite }))
      if (!silent) {
        toast.push({
          kind: "lime",
          title: "Инвайт-код создан",
          body: `${group.name} · ${invite.code}`,
        })
      }
    } catch (err) {
      const message = readError(err, "Не удалось создать инвайт-код")
      setError(message)
      toast.error("Не удалось создать инвайт-код", message)
    } finally {
      setInvitingGroupId(null)
    }
  }

  const copyInviteCode = async (code, groupName = null) => {
    const ok = await copyTextToClipboard(code)
    if (ok) {
      toast.push({
        kind: "lime",
        title: "Инвайт-код скопирован",
        body: groupName ? `${groupName} · ${code}` : code,
      })
      return
    }
    toast.push({
      kind: "info",
      title: "Скопируйте код вручную",
      body: groupName ? `${groupName} · ${code}` : code,
    })
  }

  const handleDeleteGroup = async (group) => {
    if (!group?.id) return
    const memberCount = group.member_count ?? 0
    const message =
      memberCount > 0
        ? `Удалить группу «${group.name}»? В ней ${memberCount} студент(ов). Назначения отвяжутся от группы.`
        : `Удалить группу «${group.name}»?`
    if (!window.confirm(message)) return

    setDeletingGroupId(group.id)
    setError(null)
    try {
      await deleteTeacherGroup(group.id)
      setGroups((cur: unknown) => cur.filter((g: unknown) => g.id !== group.id))
      setInviteByGroupId((cur: unknown) => {
        const next = { ...(cur as Record<string, unknown>) }
        delete next[group.id]
        return next
      })
      toast.push({ kind: "lime", title: "Группа удалена", body: group.name })
      refreshGroups().catch(() => {})
    } catch (err) {
      const messageText = readError(err, "Не удалось удалить группу")
      setError(messageText)
      toast.error("Не удалось удалить группу", messageText)
    } finally {
      setDeletingGroupId(null)
    }
  }

  return {
    profile,
    activity,
    loading,
    tasksLoading,
    metaLoading,
    catalogsLoading,
    chapters,
    collectionMeta,
    platformCourseMeta,
    courses,
    error,
    setError,
    tasks,
    visibleTasks,
    canEditTasks,
    canManageGroups,
    canManageCatalogs,
    canEdit: canEditTasks,
    catalogNameById,
    analytics,
    analyticsLoading,
    catalogs,
    groups,
    groupNameById,
    search,
    setSearch,
    newCatalogTitle,
    setNewCatalogTitle,
    newCatalogDescription,
    setNewCatalogDescription,
    newCatalogPrivate,
    setNewCatalogPrivate,
    newCatalogGroupId,
    setNewCatalogGroupId,
    newGroupName,
    setNewGroupName,
    inviteByGroupId,
    invitingGroupId,
    deletingGroupId,
    catalogToDelete,
    setCatalogToDelete,
    deletingCatalog,
    catalogToAssign,
    setCatalogToAssign,
    selectedGroup,
    setSelectedGroup,
    refreshCatalogs,
    refreshGroups,
    refreshTasks,
    refreshTasksMeta,
    refreshCourses,
    handleCreateCatalog,
    handleDeleteCatalog,
    handleCreateGroup,
    handleGenerateInvite,
    handleDeleteGroup,
    copyInviteCode,
    viewTeacherId,
    viewOnly,
  }
}
