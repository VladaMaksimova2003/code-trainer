interface StudentSolutionsPanelProps {
  submissions?: unknown[]
}

import { useMemo, useState } from "react"
import { Link } from "react-router-dom"
import {
  formatDateTime,
  languageLabel,
  submissionResultClass,
  submissionResultLabel,
  submissionStatusLabel,
} from "@/shared/utils/format"
import { Badge, Button, Field, Input, Select } from "@/shared/ui"

const SORT_OPTIONS = [
  { id: "time_desc", label: "Сначала новые" },
  { id: "time_asc", label: "Сначала старые" },
  { id: "success_first", label: "Сначала успешные" },
  { id: "failed_first", label: "Сначала неуспешные" },
]

function compareSuccess(a, b) {
  const rank = (value: unknown) => {
    if (value === true) return 0
    if (value === false) return 1
    return 2
  }
  return rank(a) - rank(b)
}

export default function StudentSolutionsPanel({
 submissions = [] 
}: StudentSolutionsPanelProps) {
  const [search, setSearch] = useState("")
  const [sortBy, setSortBy] = useState("time_desc")

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase()
    let items = [...submissions]

    if (query) {
      items = items.filter((item: unknown) => {
        const haystack = [
          item.task_title,
          item.task_id,
          item.language,
          submissionResultLabel(item.success),
          submissionStatusLabel(item.status),
        ]
          .join(" ")
          .toLowerCase()
        return haystack.includes(query)
      })
    }

    items.sort((a, b) => {
      if (sortBy === "time_asc") {
        return new Date(a.created_at || 0) - new Date(b.created_at || 0)
      }
      if (sortBy === "success_first") {
        const byResult = compareSuccess(a.success, b.success)
        if (byResult !== 0) return byResult
        return new Date(b.created_at || 0) - new Date(a.created_at || 0)
      }
      if (sortBy === "failed_first") {
        const byResult = compareSuccess(b.success, a.success)
        if (byResult !== 0) return byResult
        return new Date(b.created_at || 0) - new Date(a.created_at || 0)
      }
      return new Date(b.created_at || 0) - new Date(a.created_at || 0)
    })

    return items
  }, [submissions, search, sortBy])

  if (submissions.length === 0) {
    return (
      <p className="text-sm text-ink-muted">
        Вы ещё не отправляли решения. Попытки появятся здесь после первой отправки.
      </p>
    )
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-end gap-3">
        <Field label="Поиск" className="min-w-[220px] flex-1">
          <Input
            type="search"
            value={search}
            onChange={(event: unknown) => setSearch(event.target.value)}
            placeholder="Название задачи, язык, статус..."
          />
        </Field>
        <Field label="Сортировка" className="min-w-[200px]">
          <Select
            value={sortBy}
            onChange={(event: unknown) => setSortBy(event.target.value)}
          >
            {SORT_OPTIONS.map((option: unknown) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </Select>
        </Field>
      </div>

      <p className="text-xs text-ink-faint">
        Показано {filtered.length} из {submissions.length}
      </p>

      {filtered.length === 0 ? (
        <p className="text-sm text-ink-muted">По вашему запросу ничего не найдено.</p>
      ) : (
        <ul className="overflow-hidden rounded-lg border border-border bg-surface">
          {filtered.map((item: unknown) => (
            <li
              key={item.id}
              className="flex flex-wrap items-start justify-between gap-4 border-b border-border px-4 py-4 transition last:border-b-0 hover:bg-surface-2"
            >
              <div className="min-w-0 space-y-2">
                <div>
                  <p className="truncate font-semibold text-ink">
                    {item.task_title}
                  </p>
                  <p className="mt-0.5 text-xs text-ink-faint">
                    Попытка #{item.id} · {languageLabel(item.language)}
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <Badge tone="muted">
                    {submissionStatusLabel(item.status)}
                  </Badge>
                  <Badge tone={item.success === true ? "lime" : item.success === false ? "danger" : "warning"}>
                    {submissionResultLabel(item.success)}
                  </Badge>
                </div>
                <p className="text-sm text-ink-muted">
                  {formatDateTime(item.created_at)}
                </p>
              </div>
              <Button
                as={Link}
                to={`/tasks/${item.task_id}`}
                state={{ navigationMode: "adaptive", collectionId: null }}
                variant="ghost"
                size="sm"
                className="shrink-0"
              >
                Открыть задачу
              </Button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
