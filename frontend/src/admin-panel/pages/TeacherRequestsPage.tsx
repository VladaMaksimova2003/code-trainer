import { useState } from "react"

import {

  approveTeacherRoleRequest,

  fetchTeacherRoleRequests,

  rejectTeacherRoleRequest,

} from "@/admin-panel/api/admin"

import { useAsyncResource } from "@/admin-panel/hooks/useAsyncResource"

import ApBadge from "@/admin-panel/components/ui/ApBadge"

import { ApAvatar } from "@/admin-panel/components/ui/ApPrimitives"

import { ApSpinner, ApAlert, ApEmptyState } from "@/admin-panel/components/ui/ApFeedback"

import { ApConfirmDialog } from "@/admin-panel/components/ui/ApModal"

import { formatDateTime, requestStatusLabel } from "@/shared/utils/format"

import { toast } from "@/shared/ui/toast"



function statusKind(status) {

  const s = String(status).toLowerCase()

  if (s === "approved") return "lime"

  if (s === "rejected") return "danger"

  return "warn"

}



export default function TeacherRequestsPage() {

  const [filter, setFilter] = useState("pending")

  const [busy, setBusy] = useState(false)

  const [confirm, setConfirm] = useState(null)



  const { data, loading, error, reload } = useAsyncResource(

    () => fetchTeacherRoleRequests(filter || null),

    [filter]

  )



  const handleReview = async (requestId, approve) => {

    setBusy(true)

    try {

      if (approve) {

        await approveTeacherRoleRequest(requestId)

        toast.success("Заявка одобрена", `Заявка #${requestId} принята`)

      } else {

        await rejectTeacherRoleRequest(requestId)

        toast.success("Заявка отклонена", `Заявка #${requestId} отклонена`)

      }

      await reload()

    } catch (err) {

      toast.error("Ошибка", err?.response?.data?.detail || err?.message || "Не удалось обработать заявку")

    } finally {

      setBusy(false)

      setConfirm(null)

    }

  }



  const rows = data || []



  return (
    <>
      <div className="ap-page-toolbar">
        <select className="ap-select" style={{ width: 180, height: 38, marginLeft: "auto" }} value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="pending">Ожидают</option>
          <option value="approved">Одобренные</option>
          <option value="rejected">Отклонённые</option>
          <option value="">Все</option>
        </select>
      </div>

      <ApAlert message={error} />



      <div className="ap-card ap-card-pad">

        {loading && !data ? (

          <ApSpinner />

        ) : rows.length === 0 ? (

          <ApEmptyState icon="📋" title="Заявок нет" text="По выбранному фильтру заявки не найдены." />

        ) : (

          <table className="ap-table">

            <thead>

              <tr>

                <th>Пользователь</th>

                <th>Статус</th>

                <th>Почта</th>

                <th>Дата</th>

                <th />

              </tr>

            </thead>

            <tbody>

              {rows.map((row) => (

                <tr key={row.id}>

                  <td>
                    <div className="ap-row" style={{ gap: 10 }}>
                      <ApAvatar name={row.user_name} role="teacher" />
                      <span className="ap-t-name">{row.user_name || "—"}</span>
                    </div>
                  </td>

                  <td>

                    <ApBadge kind={statusKind(row.status)} dot>

                      {requestStatusLabel(row.status)}

                    </ApBadge>

                  </td>

                  <td className="ap-mono ap-muted" style={{ fontSize: 12.5 }}>

                    {row.user_email || "—"}

                  </td>

                  <td className="ap-muted" style={{ fontSize: 12.5 }}>

                    {formatDateTime(row.created_at)}

                  </td>

                  <td style={{ textAlign: "right" }}>

                    {String(row.status).toLowerCase() === "pending" ? (

                      <div className="ap-row" style={{ justifyContent: "flex-end", gap: 8 }}>

                        <button

                          type="button"

                          className="ap-btn ap-btn-primary ap-btn-sm"

                          disabled={busy}

                          onClick={() =>

                            setConfirm({

                              requestId: row.id,

                              approve: true,

                              title: "Одобрить заявку?",

                              body: `${row.user_name || "Пользователь"} (${row.user_email || "—"}) получит роль преподавателя.`,

                            })

                          }

                        >

                          Одобрить

                        </button>

                        <button

                          type="button"

                          className="ap-btn ap-btn-danger ap-btn-sm"

                          disabled={busy}

                          onClick={() =>

                            setConfirm({

                              requestId: row.id,

                              approve: false,

                              title: "Отклонить заявку?",

                              body: "Заявка будет отмечена как отклонённая.",

                              danger: true,

                              confirmLabel: "Отклонить",

                            })

                          }

                        >

                          Отклонить

                        </button>

                      </div>

                    ) : (

                      <span className="ap-mut3" style={{ fontSize: 12 }}>—</span>

                    )}

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        )}

      </div>



      <ApConfirmDialog

        open={Boolean(confirm)}

        title={confirm?.title}

        body={confirm?.body}

        danger={confirm?.danger}

        confirmLabel={confirm?.confirmLabel || (confirm?.approve ? "Одобрить" : "Отклонить")}

        loading={busy}

        onClose={() => setConfirm(null)}

        onConfirm={() => handleReview(confirm.requestId, confirm.approve)}

      />

    </>

  )

}


