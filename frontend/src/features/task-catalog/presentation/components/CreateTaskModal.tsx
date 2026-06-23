import { useEffect, useState } from "react"

import {
  createCatalogTask,
  createTaskInCatalog,
  listMyCatalogs,
} from "@/features/task-catalog/infrastructure/catalogApi"
import { formatTaskTypeLabel } from "@/shared/types/taskLabels"

const TYPE_OPTIONS = [
  { value: "algorithm", label: formatTaskTypeLabel("algorithm") },
  { value: "task_build_from_blocks", label: formatTaskTypeLabel("task_build_from_blocks") },
  { value: "task_translate_full_program", label: formatTaskTypeLabel("task_translate_full_program") },
  { value: "task_flowchart_to_code", label: formatTaskTypeLabel("task_flowchart_to_code") },
]

export default function CreateTaskModal({ open, onClose, onCreated, catalogId = null }) {
  const [catalogs, setCatalogs] = useState([])
  const [selectedCatalogId, setSelectedCatalogId] = useState(catalogId ?? "")
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [typeId, setTypeId] = useState(TYPE_OPTIONS[0].value)
  const [topicId, setTopicId] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!open) return
    setTitle("")
    setContent("")
    setTypeId(TYPE_OPTIONS[0].value)
    setTopicId("")
    setSelectedCatalogId(catalogId ?? "")
    setError(null)
    if (catalogId == null) {
      listMyCatalogs()
        .then(setCatalogs)
        .catch(() => setCatalogs([]))
    }
  }, [catalogId, open])

  const handleSubmit = async (event: unknown) => {
    event.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const payload = {
        title: title.trim(),
        content,
        type_id: typeId,
        topic_id: topicId === "" ? null : Number(topicId),
      }
      const effectiveCatalogId =
        catalogId != null
          ? catalogId
          : selectedCatalogId === ""
            ? null
            : Number(selectedCatalogId)
      const task =
        effectiveCatalogId != null
          ? await createTaskInCatalog(effectiveCatalogId, payload)
          : await createCatalogTask(payload)
      onCreated(task)
      onClose()
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Не удалось создать задачу")
    } finally {
      setSaving(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-lg rounded-xl border border-gray-700 bg-gray-900 p-6 shadow-xl"
      >
        <h2 className="text-lg font-semibold text-gray-100 mb-4">
          {catalogId != null ? "Создать задачу в каталоге" : "Создать задачу"}
        </h2>
        {error && (
          <div className="mb-3 rounded border border-red-800 bg-red-900/30 px-3 py-2 text-sm text-red-100">
            {typeof error === "string" ? error : "Ошибка сохранения"}
          </div>
        )}
        <label className="block text-sm text-gray-300 mb-1">Название</label>
        <input
          className="mb-3 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-gray-100"
          value={title}
          onChange={(e: unknown) => setTitle(e.target.value)}
          required
        />
        <label className="block text-sm text-gray-300 mb-1">Описание</label>
        <textarea
          className="mb-3 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-gray-100 min-h-[80px]"
          value={content}
          onChange={(e: unknown) => setContent(e.target.value)}
        />
        <label className="block text-sm text-gray-300 mb-1">Тип</label>
        <select
          className="mb-3 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-gray-100"
          value={typeId}
          onChange={(e: unknown) => setTypeId(e.target.value)}
        >
          {TYPE_OPTIONS.map((opt: unknown) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <label className="block text-sm text-gray-300 mb-1">Topic ID (опционально)</label>
        <input
          type="number"
          className="mb-4 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-gray-100"
          value={topicId}
          onChange={(e: unknown) => setTopicId(e.target.value)}
        />
        {catalogId == null && (
          <>
            <label className="block text-sm text-gray-300 mb-1">
              Каталог (опционально)
            </label>
            <select
              className="mb-4 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-gray-100"
              value={selectedCatalogId}
              onChange={(e: unknown) => setSelectedCatalogId(e.target.value)}
            >
              <option value="">Без каталога</option>
              {catalogs.map((catalog: unknown) => (
                <option key={catalog.id} value={catalog.id}>
                  {catalog.title}
                </option>
              ))}
            </select>
          </>
        )}
        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded px-4 py-2 text-sm border border-gray-600 text-gray-300 hover:bg-gray-800"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={saving}
            className="rounded px-4 py-2 text-sm bg-teal-600 hover:bg-teal-500 text-white disabled:opacity-50"
          >
            {saving ? "Сохранение…" : "Создать"}
          </button>
        </div>
      </form>
    </div>
  )
}
