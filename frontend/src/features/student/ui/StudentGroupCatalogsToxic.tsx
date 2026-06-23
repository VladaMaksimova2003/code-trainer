interface StudentGroupCatalogsToxicProps {
  catalogs?: unknown[]
  groupId?: number | string | null
}

import { useState } from "react"
import { useNavigate } from "react-router-dom"
import Chip from "@/shared/ui/Chip"
import DiffBadge from "@/shared/ui/DiffBadge"
import StatusBadge from "@/shared/ui/StatusBadge"

const STATUS_MAP = {
  solved: "solved",
  in_progress: "attempted",
  not_started: "todo",
}

export default function StudentGroupCatalogsToxic({
 catalogs = [],
 groupId = null,
}: StudentGroupCatalogsToxicProps) {
  const navigate = useNavigate()
  const [activeCat, setActiveCat] = useState(catalogs[0]?.catalog_id ?? catalogs[0]?.id)

  const openCatalog = (catalog: { catalog_id?: number; id?: number }) => {
    const catalogId = catalog.catalog_id ?? catalog.id
    if (groupId && catalogId) {
      navigate(`/learn/assigned/${catalogId}?group=${groupId}`)
      return
    }
    setActiveCat(catalogId)
  }

  if (!catalogs.length) {
    return <p className="muted">Преподаватель пока не назначил каталоги.</p>
  }

  const cat =
    catalogs.find((c: unknown) => (c.catalog_id ?? c.id) === activeCat) || catalogs[0]
  const tasks = cat?.tasks || []

  return (
    <div style={{ display: "grid", gridTemplateColumns: "230px 1fr", gap: 18, alignItems: "start" }}>
      <aside className="card card-pad">
        <b style={{ fontSize: 14 }}>Каталоги</b>
        <div className="grid" style={{ gap: 6, marginTop: 12 }}>
          {catalogs.map((c: unknown) => {
            const id = c.catalog_id ?? c.id
            return (
              <Chip
                key={id}
                active={activeCat === id}
                style={{ width: "100%", justifyContent: "flex-start", height: 34 }}
                onClick={() => openCatalog(c)}
              >
                {c.catalog_title || c.name}
              </Chip>
            )
          })}
        </div>
      </aside>

      <div className="card card-pad">
        <table className="table">
          <thead>
            <tr>
              <th>Задача</th>
              <th>Сложность</th>
              <th>Статус</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {tasks.map((t: unknown) => {
              const st = STATUS_MAP[t.status] || "todo"
              return (
                <tr key={t.task_id} className="no-hover">
                  <td className="t-name">{t.title || t.task_title}</td>
                  <td>
                    <DiffBadge diff={t.difficulty} />
                  </td>
                  <td>
                    <StatusBadge status={st} />
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      type="button"
                      className={`btn btn-sm ${
                        st === "solved"
                          ? "btn-ghost"
                          : st === "attempted"
                            ? "btn-primary"
                            : "btn-ghost"
                      }`}
                      onClick={() =>
                        navigate(`/tasks/${t.task_id}`, {
                          state: {
                            navigationMode: "manual",
                            collectionId: cat.catalog_id ?? cat.id,
                          },
                        })
                      }
                    >
                      {st === "solved" ? "Открыть" : st === "attempted" ? "Продолжить" : "Начать"}
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
