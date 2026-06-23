import { useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"

import {
  activateAssignmentVersion,
  archiveAdminAssignment,
  createAssignmentVersion,
  fetchAdminAssignments,
  fetchAssignmentVersions,
  patchAssignmentWorkflow,
} from "@/admin-panel/api/admin"
import { useAsyncResource } from "@/admin-panel/hooks/useAsyncResource"
import ApBadge from "@/admin-panel/components/ui/ApBadge"
import { ApSpinner, ApAlert, ApEmptyState } from "@/admin-panel/components/ui/ApFeedback"
import ApModal, { ApConfirmDialog } from "@/admin-panel/components/ui/ApModal"
import { ApSortHeader, type SortDir } from "@/admin-panel/components/ui/ApSortHeader"
import { formatDateTime, workflowStatusLabel } from "@/shared/utils/format"
import { toast } from "@/shared/ui/toast"

const WORKFLOW_OPTIONS = [
  { value: "active", label: "Активно" },
  { value: "archived", label: "В архиве" },
]

type SortKey = "id" | "title" | "placement" | "owner" | "status" | "version"

type AssignmentRow = {
  id: number
  title: string
  task_type: string
  version: number
  workflow_status?: string | null
  collection_title?: string | null
  chapter_title?: string | null
  chapter_key?: string | null
  language?: string | null
  chapter_slug?: string | null
  teacher_id?: number | null
  teacher_name?: string | null
  teacher_email?: string | null
  teacher_is_deleted?: boolean | null
}

function formatPlacement(row: AssignmentRow) {
  if (!row.collection_title && !row.chapter_title) {
    return "Вне учебного сборника"
  }
  const parts: string[] = []
  if (row.collection_title) parts.push(`Сборник «${row.collection_title}»`)
  if (row.chapter_title) parts.push(`глава «${row.chapter_title}»`)
  return parts.join(" · ")
}

function formatOwner(row: AssignmentRow) {
  if (row.teacher_is_deleted) {
    return "Пользователь удалён"
  }
  if (!row.teacher_id && !row.teacher_name && !row.teacher_email) {
    return "Не указан"
  }
  const name = row.teacher_name?.trim() || `ID ${row.teacher_id}`
  if (row.teacher_email) return `${name} · ${row.teacher_email}`
  return name
}

function learnChapterHref(row: AssignmentRow): string | null {
  const slug = row.chapter_slug?.trim()
  if (!slug) return null
  const language = (row.language || "python").toLowerCase()
  return `/learn/${language}/${slug}`
}

function ownerHref(row: AssignmentRow): string | null {
  if (row.teacher_is_deleted || !row.teacher_id) return null
  return `/admin/users/${row.teacher_id}`
}

function ownerSortKey(row: AssignmentRow): string {
  if (row.teacher_is_deleted) return "\uffff"
  return (row.teacher_name || row.teacher_email || (row.teacher_id ? `id:${row.teacher_id}` : "")).toLowerCase()
}

function statusSortKey(row: AssignmentRow): number {
  const status = String(row.workflow_status || "active").toLowerCase()
  if (status === "active") return 0
  if (status === "archived") return 1
  return 2
}

function compareRows(a: AssignmentRow, b: AssignmentRow, key: SortKey): number {
  switch (key) {
    case "id":
      return a.id - b.id
    case "version":
      return a.version - b.version
    case "title":
      return a.title.localeCompare(b.title, "ru", { sensitivity: "base" })
    case "placement":
      return formatPlacement(a).localeCompare(formatPlacement(b), "ru", { sensitivity: "base" })
    case "owner":
      return ownerSortKey(a).localeCompare(ownerSortKey(b), "ru", { sensitivity: "base" })
    case "status":
      return statusSortKey(a) - statusSortKey(b)
    default:
      return 0
  }
}

function sortAssignments(rows: AssignmentRow[], key: SortKey, dir: SortDir): AssignmentRow[] {
  const mul = dir === "asc" ? 1 : -1
  return [...rows].sort((a, b) => compareRows(a, b, key) * mul)
}

function defaultSortDir(key: SortKey): SortDir {
  return key === "id" || key === "version" ? "desc" : "asc"
}

export default function AssignmentsPage() {
  const [statusFilter, setStatusFilter] = useState("")
  const [search, setSearch] = useState("")
  const [busy, setBusy] = useState(false)
  const [confirm, setConfirm] = useState<{
    title: string
    body: string
    danger?: boolean
    confirmLabel: string
    action: () => void
  } | null>(null)
  const [versionsModal, setVersionsModal] = useState<number | null>(null)
  const [versions, setVersions] = useState<
    Array<{
      id: number
      version_number: number
      title: string
      is_active: boolean
      created_at?: string | null
    }>
  >([])
  const [versionsLoading, setVersionsLoading] = useState(false)
  const [sortKey, setSortKey] = useState<SortKey>("id")
  const [sortDir, setSortDir] = useState<SortDir>("desc")

  const { data, loading, error, reload } = useAsyncResource(() => fetchAdminAssignments(true), [])

  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === "visible") {
        void reload()
      }
    }
    document.addEventListener("visibilitychange", onVisible)
    return () => document.removeEventListener("visibilitychange", onVisible)
  }, [reload])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return (data || []).filter((row: AssignmentRow) => {
      if (statusFilter && String(row.workflow_status).toLowerCase() !== statusFilter) return false
      if (!q) return true
      return (
        row.title?.toLowerCase().includes(q) ||
        String(row.id).includes(q) ||
        row.task_type?.toLowerCase().includes(q) ||
        row.collection_title?.toLowerCase().includes(q) ||
        row.chapter_title?.toLowerCase().includes(q) ||
        row.teacher_name?.toLowerCase().includes(q) ||
        row.teacher_email?.toLowerCase().includes(q)
      )
    })
  }, [data, search, statusFilter])

  const sorted = useMemo(
    () => sortAssignments(filtered, sortKey, sortDir),
    [filtered, sortKey, sortDir],
  )

  const handleSort = (column: SortKey) => {
    if (sortKey === column) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"))
      return
    }
    setSortKey(column)
    setSortDir(defaultSortDir(column))
  }

  const counts = useMemo(
    () => ({
      active: (data || []).filter((i) => String(i.workflow_status).toLowerCase() === "active").length,
      archived: (data || []).filter((i) => String(i.workflow_status).toLowerCase() === "archived")
        .length,
    }),
    [data],
  )

  const run = async (fn: () => Promise<void>, toastTitle: string, toastBody?: string) => {
    setBusy(true)
    try {
      await fn()
      toast.success(toastTitle, toastBody)
      await reload()
      if (versionsModal) {
        await openVersions(versionsModal)
      }
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось выполнить действие"
      toast.error("Ошибка", message)
    } finally {
      setBusy(false)
      setConfirm(null)
    }
  }

  const openVersions = async (taskId: number) => {
    setVersionsModal(taskId)
    setVersionsLoading(true)
    try {
      const list = await fetchAssignmentVersions(taskId)
      setVersions(list)
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось загрузить версии"
      toast.error("Ошибка", message)
    } finally {
      setVersionsLoading(false)
    }
  }

  return (
    <>
      <div className="ap-card filter-toolbar">
        <div className="ap-toolbar">
          <input
            className="ap-input"
            placeholder="Поиск по названию или ID…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="ap-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Все статусы</option>
            {WORKFLOW_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="ap-btn ap-btn-ghost"
            onClick={() => {
              setSearch("")
              setStatusFilter("")
              void reload()
              toast.info("Список обновлён")
            }}
          >
            ↻ Обновить
          </button>
        </div>
      </div>

      <ApAlert message={error} />

      <div className="ap-summary">
        <span className="ap-sumchip lime">
          <span className="d" />
          Активно <b>{counts.active}</b>
        </span>
        <span className="ap-sumchip muted">
          <span className="d" />
          В архиве <b>{counts.archived}</b>
        </span>
      </div>

      <div className="ap-card ap-assignments-card">
        {loading && !data ? (
          <div style={{ padding: "10px 18px" }}>
            <ApSpinner />
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: "10px 18px" }}>
            <ApEmptyState
              icon="📚"
              title="Заданий нет"
              text="Попробуйте изменить фильтры или поисковый запрос."
            />
          </div>
        ) : (
          <div className="ap-table-wrap">
            <table className="ap-table ap-assignments-table">
              <thead>
                <tr>
                  <th>
                    <ApSortHeader label="ID" column="id" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                  </th>
                  <th>
                    <ApSortHeader
                      label="Название"
                      column="title"
                      sortKey={sortKey}
                      sortDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th>
                    <ApSortHeader
                      label="Размещение"
                      column="placement"
                      sortKey={sortKey}
                      sortDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th>
                    <ApSortHeader
                      label="Владелец"
                      column="owner"
                      sortKey={sortKey}
                      sortDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th>
                    <ApSortHeader
                      label="Статус"
                      column="status"
                      sortKey={sortKey}
                      sortDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th>
                    <ApSortHeader
                      label="Версия"
                      column="version"
                      sortKey={sortKey}
                      sortDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th className="ap-table-actions-head">Действия</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((row: AssignmentRow) => {
                  const placementLink = learnChapterHref(row)
                  const ownerLink = ownerHref(row)
                  const status = String(row.workflow_status || "active").toLowerCase()

                  return (
                    <tr key={row.id}>
                      <td className="ap-id">#{row.id}</td>
                      <td className="ap-table-name">
                        <Link to={`/tasks/${row.id}`} className="ap-table-link">
                          {row.title}
                        </Link>
                        <span className="sub">{row.task_type}</span>
                      </td>
                      <td className="ap-table-meta">
                        {placementLink ? (
                          <Link to={placementLink} className="ap-table-link ap-table-link-soft">
                            {formatPlacement(row)}
                          </Link>
                        ) : (
                          <span className="ap-table-meta-main">{formatPlacement(row)}</span>
                        )}
                        {row.chapter_key ? <span className="sub ap-mono">{row.chapter_key}</span> : null}
                      </td>
                      <td className="ap-table-meta">
                        {ownerLink ? (
                          <Link to={ownerLink} className="ap-table-link ap-table-link-soft">
                            {formatOwner(row)}
                          </Link>
                        ) : (
                          <span className="ap-table-meta-main">{formatOwner(row)}</span>
                        )}
                        {row.teacher_id && !row.teacher_is_deleted ? (
                          <span className="sub ap-mono">teacher #{row.teacher_id}</span>
                        ) : null}
                      </td>
                      <td className="ap-table-status">
                        <select
                          className="ap-select ap-status-select"
                          value={status === "archived" ? "archived" : "active"}
                          disabled={busy}
                          aria-label="Статус задания"
                          onChange={(e) =>
                            run(
                              () => patchAssignmentWorkflow(row.id, e.target.value),
                              "Статус обновлён",
                              workflowStatusLabel(e.target.value),
                            )
                          }
                        >
                          {WORKFLOW_OPTIONS.map((o) => (
                            <option key={o.value} value={o.value}>
                              {o.label}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td className="ap-ver ap-mono">v{row.version}</td>
                      <td className="ap-table-actions">
                        <button
                          type="button"
                          className="ap-btn ap-btn-secondary ap-btn-sm"
                          disabled={busy}
                          onClick={() => openVersions(row.id)}
                        >
                          Версии
                        </button>
                        {status !== "archived" ? (
                          <button
                            type="button"
                            className="ap-btn ap-btn-danger ap-btn-sm"
                            disabled={busy}
                            onClick={() =>
                              setConfirm({
                                title: "Архивировать задание?",
                                body: `«${row.title}» будет скрыто из активных и недоступно для назначения. Действие обратимо через смену статуса.`,
                                danger: true,
                                confirmLabel: "В архив",
                                action: () =>
                                  run(
                                    () => archiveAdminAssignment(row.id),
                                    "Задание архивировано",
                                    row.title,
                                  ),
                              })
                            }
                          >
                            В архив
                          </button>
                        ) : null}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ApModal
        open={Boolean(versionsModal)}
        title={`Версии задания #${versionsModal}`}
        onClose={() => {
          setVersionsModal(null)
          setVersions([])
        }}
        footer={
          <>
            <button
              type="button"
              className="ap-btn ap-btn-ghost ap-btn-sm"
              onClick={() => {
                setVersionsModal(null)
                setVersions([])
              }}
            >
              Закрыть
            </button>
            <button
              type="button"
              className="ap-btn ap-btn-primary ap-btn-sm"
              disabled={busy || !versionsModal}
              onClick={() =>
                run(
                  () => createAssignmentVersion(versionsModal!),
                  "Снимок создан",
                  `Задание #${versionsModal}`,
                )
              }
            >
              + Создать снимок вручную
            </button>
          </>
        }
      >
        {versionsLoading ? (
          <ApSpinner />
        ) : versions.length === 0 ? (
          <p className="ap-muted" style={{ fontSize: 13, margin: 0 }}>
            Версий пока нет. Снимок появится после первого сохранения изменений в редакторе задания.
          </p>
        ) : (
          <div className="ap-grid" style={{ gap: 10 }}>
            {versions.map((v) => (
              <div
                key={v.id}
                className="ap-between"
                style={{ padding: "11px 13px", border: "1px solid var(--border)", borderRadius: 11 }}
              >
                <div style={{ minWidth: 0 }}>
                  <div className="ap-row" style={{ gap: 8 }}>
                    <b className="ap-mono" style={{ fontSize: 13 }}>
                      v{v.version_number}
                    </b>
                    <span style={{ fontSize: 13.5 }}>{v.title}</span>
                  </div>
                  <span className="ap-mut3" style={{ fontSize: 12 }}>
                    {formatDateTime(v.created_at)}
                  </span>
                  {v.is_active ? (
                    <span style={{ marginLeft: 8 }}>
                      <ApBadge kind="lime" dot>
                        активна
                      </ApBadge>
                    </span>
                  ) : null}
                </div>
                {!v.is_active ? (
                  <button
                    type="button"
                    className="ap-btn ap-btn-primary ap-btn-sm"
                    disabled={busy}
                    onClick={() =>
                      run(
                        () => activateAssignmentVersion(versionsModal!, v.id),
                        "Версия активирована",
                        `v${v.version_number}`,
                      )
                    }
                  >
                    Активировать
                  </button>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </ApModal>

      <ApConfirmDialog
        open={Boolean(confirm)}
        title={confirm?.title}
        body={confirm?.body}
        danger={confirm?.danger}
        confirmLabel={confirm?.confirmLabel}
        loading={busy}
        onClose={() => setConfirm(null)}
        onConfirm={() => confirm?.action?.()}
      />
    </>
  )
}
