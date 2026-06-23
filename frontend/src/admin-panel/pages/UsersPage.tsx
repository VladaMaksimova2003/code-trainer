import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { fetchAdminUsers } from "@/admin-panel/api/admin"
import { useAsyncResource } from "@/admin-panel/hooks/useAsyncResource"
import { usePagination } from "@/shared/hooks/usePagination"
import ApBadge, { ApRoleBadge } from "@/admin-panel/components/ui/ApBadge"
import { ApSpinner, ApAlert, ApEmptyState } from "@/admin-panel/components/ui/ApFeedback"
import ApPagination from "@/admin-panel/components/ui/ApPagination"
import { ApAvatar } from "@/admin-panel/components/ui/ApPrimitives"
import { ApSortHeader, type SortDir } from "@/admin-panel/components/ui/ApSortHeader"
import { formatDateTime } from "@/shared/utils/format"
import { isProtectedSuperUserEmail } from "@/shared/utils/superUser"

type SortKey = "name" | "email" | "role" | "status" | "created_at"

type AdminUserRow = {
  id: number
  name: string
  email: string
  roles?: string[]
  is_blocked?: boolean
  is_deleted?: boolean
  created_at?: string | null
}

const ROLE_ORDER: Record<string, number> = {
  admin: 0,
  teacher: 1,
  student: 2,
}

function userStatus(user: AdminUserRow) {
  if (user.is_deleted) return { label: "Удалён", kind: "danger" as const }
  if (user.is_blocked) return { label: "Заблокирован", kind: "warn" as const }
  return { label: "Активен", kind: "muted" as const }
}

function statusSortKey(user: AdminUserRow): number {
  if (user.is_deleted) return 2
  if (user.is_blocked) return 1
  return 0
}

function roleSortKey(user: AdminUserRow): string {
  const roles = (user.roles || []).map((r) => r.toLowerCase()).sort()
  if (roles.length === 0) return "\uffff"
  const primary = roles.reduce((best, role) => {
    const rank = ROLE_ORDER[role] ?? 99
    const bestRank = ROLE_ORDER[best] ?? 99
    return rank < bestRank ? role : best
  }, roles[0])
  return primary
}

function compareUsers(a: AdminUserRow, b: AdminUserRow, key: SortKey): number {
  switch (key) {
    case "name":
      return a.name.localeCompare(b.name, "ru", { sensitivity: "base" })
    case "email":
      return a.email.localeCompare(b.email, "ru", { sensitivity: "base" })
    case "role":
      return roleSortKey(a).localeCompare(roleSortKey(b), "ru", { sensitivity: "base" })
    case "status":
      return statusSortKey(a) - statusSortKey(b)
    case "created_at": {
      const aTime = a.created_at ? Date.parse(a.created_at) : 0
      const bTime = b.created_at ? Date.parse(b.created_at) : 0
      return aTime - bTime
    }
    default:
      return 0
  }
}

function sortUsers(rows: AdminUserRow[], key: SortKey, dir: SortDir): AdminUserRow[] {
  const mul = dir === "asc" ? 1 : -1
  return [...rows].sort((a, b) => compareUsers(a, b, key) * mul)
}

function defaultSortDir(key: SortKey): SortDir {
  return key === "created_at" ? "desc" : "asc"
}

function primaryDisplayRole(user: AdminUserRow): "student" | "teacher" | "admin" {
  const roles = (user.roles || []).map((r) => r.toLowerCase())
  if (roles.includes("admin")) return "admin"
  if (roles.includes("teacher")) return "teacher"
  return "student"
}

export default function UsersPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState("")
  const [role, setRole] = useState("all")
  const [status, setStatus] = useState("all")
  const [includeDeleted, setIncludeDeleted] = useState(false)
  const [sortKey, setSortKey] = useState<SortKey>("name")
  const [sortDir, setSortDir] = useState<SortDir>("asc")

  const { data, loading, error, reload } = useAsyncResource(
    () => fetchAdminUsers(includeDeleted),
    [includeDeleted],
  )

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
    return (data || []).filter((user: AdminUserRow) => {
      if (role !== "all" && !(user.roles || []).map((r) => r.toLowerCase()).includes(role)) return false
      if (status === "active" && (user.is_blocked || user.is_deleted)) return false
      if (status === "blocked" && !user.is_blocked) return false
      if (status === "deleted" && !user.is_deleted) return false
      if (!q) return true
      return (
        user.name?.toLowerCase().includes(q) ||
        user.email?.toLowerCase().includes(q) ||
        String(user.id).includes(q)
      )
    })
  }, [data, search, role, status])

  const sorted = useMemo(() => sortUsers(filtered, sortKey, sortDir), [filtered, sortKey, sortDir])

  const { page, setPage, totalPages, pageItems, resetPage } = usePagination(sorted, 8)

  useEffect(() => {
    resetPage()
  }, [search, role, status, includeDeleted, sortKey, sortDir, resetPage])

  const handleSort = (column: SortKey) => {
    if (sortKey === column) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"))
      return
    }
    setSortKey(column)
    setSortDir(defaultSortDir(column))
  }

  return (
    <>
      <div className="ap-page-toolbar">
        <input
          className="ap-input"
          style={{ width: 240, height: 38 }}
          placeholder="Поиск по имени/email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="ap-row" style={{ gap: 10, flexWrap: "wrap", marginLeft: "auto" }}>
          <select
            className="ap-select"
            style={{ width: 160, height: 38 }}
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="all">Все роли</option>
            <option value="student">Студент</option>
            <option value="teacher">Преподаватель</option>
            <option value="admin">Админ</option>
          </select>
          <select
            className="ap-select"
            style={{ width: 160, height: 38 }}
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="all">Все статусы</option>
            <option value="active">Активные</option>
            <option value="blocked">Заблокированные</option>
            <option value="deleted">Удалённые</option>
          </select>
          <label className="ap-check-row">
            <span
              className={`ap-checkbox${includeDeleted ? " on" : ""}`}
              onClick={(e) => {
                e.preventDefault()
                setIncludeDeleted((v) => !v)
              }}
              role="checkbox"
              aria-checked={includeDeleted}
            />
            Удалённые
          </label>
          <button type="button" className="ap-btn ap-btn-ghost ap-btn-sm" onClick={() => void reload()}>
            Обновить
          </button>
        </div>
      </div>

      <ApAlert message={error} />

      <div className="ap-card ap-users-card">
        {loading && !data ? (
          <div style={{ padding: "18px" }}>
            <ApSpinner />
          </div>
        ) : sorted.length === 0 ? (
          <div style={{ padding: "18px" }}>
            <ApEmptyState icon="⌕" title="Ничего не найдено" text="Попробуйте сбросить фильтры." />
          </div>
        ) : (
          <>
            <div className="ap-table-wrap">
              <table className="ap-table ap-users-table">
                <thead>
                  <tr>
                    <th>
                      <ApSortHeader
                        label="Пользователь"
                        column="name"
                        sortKey={sortKey}
                        sortDir={sortDir}
                        onSort={handleSort}
                      />
                    </th>
                    <th>
                      <ApSortHeader
                        label="Почта"
                        column="email"
                        sortKey={sortKey}
                        sortDir={sortDir}
                        onSort={handleSort}
                      />
                    </th>
                    <th>
                      <ApSortHeader
                        label="Роль"
                        column="role"
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
                        label="Регистрация"
                        column="created_at"
                        sortKey={sortKey}
                        sortDir={sortDir}
                        onSort={handleSort}
                      />
                    </th>
                    <th className="ap-table-actions-head" />
                  </tr>
                </thead>
                <tbody>
                  {pageItems.map((user: AdminUserRow) => {
                    const st = userStatus(user)
                    const displayRole = primaryDisplayRole(user)
                    const protectedUser = isProtectedSuperUserEmail(user.email)
                    const profilePath = `/admin/users/${user.id}`

                    return (
                      <tr
                        key={user.id}
                        className={protectedUser ? "ap-row-protected ap-no-hover" : undefined}
                        style={protectedUser ? { opacity: 0.72 } : undefined}
                      >
                        <td className="ap-user-cell">
                          <div className="ap-row" style={{ gap: 10, minWidth: 0 }}>
                            <ApAvatar name={user.name} role={displayRole} />
                            {protectedUser ? (
                              <span className="ap-t-name">{user.name}</span>
                            ) : (
                              <Link to={profilePath} className="ap-table-link ap-t-name">
                                {user.name}
                              </Link>
                            )}
                          </div>
                        </td>
                        <td>
                          {protectedUser ? (
                            <span className="ap-muted ap-mono ap-user-email">{user.email}</span>
                          ) : (
                            <Link to={profilePath} className="ap-table-link ap-table-link-soft ap-user-email ap-mono">
                              {user.email}
                            </Link>
                          )}
                        </td>
                        <td>
                          <div className="ap-wrap">
                            {(user.roles || []).map((r) => (
                              <ApRoleBadge key={r} role={r} />
                            ))}
                          </div>
                        </td>
                        <td>
                          <ApBadge kind={st.kind} dot>
                            {st.label}
                          </ApBadge>
                        </td>
                        <td className="ap-muted" style={{ fontSize: 12.5 }}>
                          {formatDateTime(user.created_at)}
                        </td>
                        <td className="ap-table-actions">
                          {protectedUser ? null : (
                            <button
                              type="button"
                              className="ap-btn ap-btn-ghost ap-btn-sm"
                              onClick={() => navigate(profilePath)}
                            >
                              Открыть
                            </button>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
            <div className="ap-between ap-users-table-footer">
              <span className="ap-mut3" style={{ fontSize: 13 }}>
                {(page - 1) * 8 + 1}–{Math.min(page * 8, sorted.length)} из {sorted.length}
              </span>
              <ApPagination page={page} totalPages={totalPages} onPageChange={setPage} />
            </div>
          </>
        )}
      </div>
    </>
  )
}
