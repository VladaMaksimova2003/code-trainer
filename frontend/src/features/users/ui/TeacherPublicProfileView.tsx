import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import Badge from "@/shared/ui/Badge"
import ProfileSectionTitle from "@/shared/ui/ProfileSectionTitle"
import RoleAvatar from "@/shared/ui/RoleAvatar"
import { formatTaskTypeLabel } from "@/shared/types/taskLabels"
import DiffBadge from "@/shared/ui/DiffBadge"

function StatCard({ value, label, badge }) {
  return (
    <div className="card card-pad profile-stat-card">
      <div className="profile-stat-value">{value}</div>
      <div className="profile-stat-label">{label}</div>
      {badge ? <div className="profile-stat-badge">{badge}</div> : null}
    </div>
  )
}

function taskCountLabel(n: unknown) {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod100 >= 11 && mod100 <= 14) return `${n} задач`
  if (mod10 === 1) return `${n} задача`
  if (mod10 >= 2 && mod10 <= 4) return `${n} задачи`
  return `${n} задач`
}

export default function TeacherPublicProfileView({ data, viewerIsOwner = false }) {
  const navigate = useNavigate()
  const [openCatalogId, setOpenCatalogId] = useState(null)

  const catalogs = data.public_catalogs ?? []
  const stats = data.stats ?? {}
  const canBrowse = data.can_browse_catalogs && !viewerIsOwner

  const openCatalog = catalogs.find((c: unknown) => c.id === openCatalogId)

  const startTask = (catalogId, taskId) => {
    navigate(`/tasks/${taskId}`, {
      state: { navigationMode: "manual", collectionId: catalogId },
    })
  }

  return (
    <div className="profile-page">
      <div className="profile-page-top between">
        <nav className="profile-breadcrumbs mut3">
          <Link to="/student/profile?tab=groups">Преподаватели</Link>
          <span> / </span>
          <span>{data.display_name}</span>
        </nav>
        <Badge kind="pp">Преподаватель</Badge>
      </div>

      <div className="card card-pad profile-hero profile-hero--teacher">
        <div className="profile-hero-inner">
          <RoleAvatar
            user={{ id: data.user_id }}
            name={data.display_name}
            role="teacher"
            size="lg"
            className="profile-hero-avatar profile-hero-avatar--square"
            style={{ width: 72, height: 72, borderRadius: 16, fontSize: 24 }}
          />
          <div className="profile-hero-body">
            <h1 className="profile-hero-name">{data.display_name}</h1>
            {data.subtitle ? (
              <p className="profile-hero-sub mut3">{data.subtitle}</p>
            ) : null}
            <div className="row" style={{ gap: 8, marginTop: 10, flexWrap: "wrap" }}>
              <Badge kind="pp">Преподаватель</Badge>
              {data.languages?.length > 0 ? (
                <Badge kind="lime">{data.languages.slice(0, 2).join(", ")}</Badge>
              ) : null}
            </div>
            {data.bio ? (
              <p className="muted" style={{ fontSize: 14, marginTop: 12, lineHeight: 1.5 }}>
                {data.bio}
              </p>
            ) : null}
          </div>
          {data.email && !viewerIsOwner ? (
            <a
              className="btn btn-ghost btn-sm profile-contact-btn"
              href={`mailto:${data.email}`}
            >
              ✉ Написать преподавателю
            </a>
          ) : null}
          {viewerIsOwner ? (
            <Link to="/student/profile" className="btn btn-secondary btn-sm">
              Мой кабинет
            </Link>
          ) : null}
        </div>
      </div>

      <div className="profile-stat-row">
        <StatCard
          value={stats.students ?? 0}
          label="Студентов"
          badge={
            stats.students_week_delta > 0 ? (
              <Badge kind="lime">+{stats.students_week_delta} за неделю</Badge>
            ) : null
          }
        />
        <StatCard
          value={stats.active_tasks ?? stats.total_tasks ?? 0}
          label="Активных задач"
          badge={
            stats.public_catalogs > 0 ? (
              <Badge kind="pp">в {stats.public_catalogs} каталогах</Badge>
            ) : null
          }
        />
        <StatCard
          value={`${stats.avg_pass_rate ?? 0}%`}
          label="Средняя сдача"
          badge={<Badge kind="lime">по группам</Badge>}
        />
      </div>

      {catalogs.length > 0 ? (
        <section className="card card-pad profile-catalog-section">
          <ProfileSectionTitle className="profile-section-title--flush">
            Каталоги задач
          </ProfileSectionTitle>
          <p className="mut3" style={{ fontSize: 13, margin: "-6px 0 16px" }}>
            {canBrowse
              ? "Открытые каталоги — можно просматривать и решать задачи"
              : "Открытые каталоги преподавателя"}
          </p>
          <div className="profile-catalog-list">
            {catalogs.map((cat: unknown) => (
              <div key={cat.id} className="profile-catalog-row">
                <div className="profile-catalog-row-main">
                  <b>{cat.title}</b>
                  {cat.description ? (
                    <p className="mut3" style={{ fontSize: 13, margin: "4px 0 0" }}>
                      {cat.description}
                    </p>
                  ) : null}
                </div>
                <Badge kind="pp">{taskCountLabel(cat.task_count ?? 0)}</Badge>
                {canBrowse ? (
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={() =>
                      setOpenCatalogId(openCatalogId === cat.id ? null : cat.id)
                    }
                  >
                    {openCatalogId === cat.id ? "Свернуть" : "Открыть"}
                  </button>
                ) : viewerIsOwner ? (
                  <Link
                    to={`/teacher/catalogs/${cat.id}`}
                    className="btn btn-ghost btn-sm"
                  >
                    Открыть
                  </Link>
                ) : null}
              </div>
            ))}
          </div>

          {canBrowse && openCatalog?.tasks?.length > 0 ? (
            <div className="profile-catalog-tasks">
              <b style={{ fontSize: 14, display: "block", marginBottom: 12 }}>
                {openCatalog.title}
              </b>
              <table className="table">
                <thead>
                  <tr>
                    <th>Задача</th>
                    <th>Тип</th>
                    <th>Сложность</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {openCatalog.tasks.map((task: unknown) => (
                    <tr
                      key={task.id}
                      onClick={() => startTask(openCatalog.id, task.id)}
                      style={{ cursor: "pointer" }}
                    >
                      <td className="t-name">{task.title}</td>
                      <td className="muted">
                        {formatTaskTypeLabel(task.type || task.task_type)}
                      </td>
                      <td>
                        <DiffBadge diff={task.difficulty} />
                      </td>
                      <td>
                        <span className="btn btn-primary btn-xs">Решить</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </section>
      ) : null}
    </div>
  )
}
