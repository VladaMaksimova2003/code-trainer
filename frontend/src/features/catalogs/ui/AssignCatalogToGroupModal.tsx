interface AssignCatalogToGroupModalProps {
  catalog: unknown
  groups: unknown
  onClose: (...args: unknown[]) => unknown
  onAssigned: (...args: unknown[]) => unknown
}

import { useState } from "react"
import { assignCatalogToGroup } from "@/features/groups/api/groupsApi"
import { toast } from "@/shared/ui/toast"
import { combineDateAndTime } from "@/shared/utils/deadlineInput"

export default function AssignCatalogToGroupModal({

  catalog,
  groups,
  onClose,
  onAssigned,

}: AssignCatalogToGroupModalProps) {
  const [groupId, setGroupId] = useState("")
  const [deadlineDate, setDeadlineDate] = useState("")
  const [deadlineTime, setDeadlineTime] = useState("23:59")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  if (!catalog) return null

  const alreadyAssigned = catalog.group_id != null

  const handleSubmit = async (event: unknown) => {
    event.preventDefault()
    if (!groupId) return
    setSaving(true)
    setError(null)
    try {
      const deadline_at = combineDateAndTime(deadlineDate, deadlineTime)
      await assignCatalogToGroup(Number(groupId), {
        catalog_id: catalog.id,
        deadline_at,
      })
      const group = groups.find((g: unknown) => String(g.id) === String(groupId))
      toast.push({
        kind: "lime",
        title: "Каталог назначен группе",
        body: `«${catalog.title}» → ${group?.name || "группа"}`,
      })
      onAssigned?.()
      onClose()
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Не удалось назначить каталог группе"
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      onClick={onClose}
      role="presentation"
    >
      <form
        onSubmit={handleSubmit}
        onClick={(e: unknown) => e.stopPropagation()}
        className="w-full max-w-md rounded-xl border border-gray-700 bg-gray-900 p-5 shadow-xl space-y-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assign-catalog-title"
      >
        <h3 id="assign-catalog-title" className="text-lg font-semibold text-white">
          Назначить каталог группе
        </h3>
        <p className="text-sm text-gray-400">
          Каталог «{catalog.title}» станет доступен студентам выбранной группы.
        </p>

        {alreadyAssigned && (
          <p className="text-sm text-amber-300">
            Каталог уже привязан к группе. Повторное назначение заменит привязку.
          </p>
        )}

        {error && <p className="text-sm text-red-300">{error}</p>}

        <label className="block text-xs text-gray-500">
          Группа
          <select
            value={groupId}
            onChange={(e: unknown) => setGroupId(e.target.value)}
            className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100"
            required
          >
            <option value="">Выберите группу</option>
            {groups.map((g: unknown) => (
              <option key={g.id} value={g.id}>
                {g.name}
              </option>
            ))}
          </select>
        </label>

        <fieldset className="space-y-2 rounded-lg border border-gray-800 p-3">
          <legend className="text-xs text-gray-500 px-1">Дедлайн (необязательно)</legend>
          <p className="text-xs text-gray-600">
            Укажите дату и время, до которых студенты должны выполнить задания каталога.
            Если время не важно, оставьте 23:59.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <label className="block text-xs text-gray-500">
              Дата
              <input
                type="date"
                value={deadlineDate}
                onChange={(e: unknown) => setDeadlineDate(e.target.value)}
                className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100"
              />
            </label>
            <label className="block text-xs text-gray-500">
              Время
              <input
                type="time"
                value={deadlineTime}
                onChange={(e: unknown) => setDeadlineTime(e.target.value)}
                className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100"
                step={60}
              />
            </label>
          </div>
        </fieldset>

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded border border-gray-600 px-4 py-2 text-sm text-gray-200 hover:bg-gray-800"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={saving || groups.length === 0}
            className="rounded bg-teal-600 hover:bg-teal-500 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            {saving ? "Назначение..." : "Назначить"}
          </button>
        </div>
      </form>
    </div>
  )
}
