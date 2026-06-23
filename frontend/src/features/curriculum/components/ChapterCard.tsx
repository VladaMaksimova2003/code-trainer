import type { Collection } from "../types"
import { progressPercent, displayCollectionTotal } from "../actionMeta"
import Badge from "@/shared/ui/Badge"

interface ChapterCardProps {
  chapter: Collection
  isCurrent?: boolean
  isLast?: boolean
  onOpen: (chapter: Collection) => void
  onContinue?: (chapter: Collection) => void
}

export default function ChapterCard({
  chapter,
  isCurrent = false,
  isLast = false,
  onOpen,
  onContinue,
}: ChapterCardProps) {
  const { progress, completed } = chapter
  const totalTasks = displayCollectionTotal(progress)
  const percent = progressPercent({
    ...progress,
    catalog_tasks: progress?.catalog_tasks ?? totalTasks,
  })
  const showCompleted = completed && totalTasks > 0
  const hasTasks = totalTasks > 0

  const cardClass = [
    "chapter-card",
    showCompleted ? "done" : "",
    !showCompleted && isCurrent ? "current" : "",
  ]
    .filter(Boolean)
    .join(" ")

  return (
    <div className={cardClass}>
      <div className="chapter-node">
        <div className="chapter-num">{showCompleted ? "✓" : chapter.order}</div>
        {!isLast ? <div className="chapter-connector" /> : null}
      </div>

      <div className="min-w-0">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <b className="text-[16px] text-ink">{chapter.title_ru}</b>
          {showCompleted ? (
            <Badge kind="lime">✓ Все пройдены</Badge>
          ) : isCurrent ? (
            <Badge kind="purple">Текущий</Badge>
          ) : null}
        </div>
        {chapter.description_ru ? (
          <p className="m-0 text-[13.5px] text-ink-muted">{chapter.description_ru}</p>
        ) : null}

        <div className="mt-3 grid grid-cols-1 items-center gap-3.5 sm:grid-cols-[1fr_auto]">
          <div>
            <div className="mb-1.5 font-mono text-[12px] text-ink-faint">
              {hasTasks
                ? `${progress.passed_tasks}/${totalTasks} · ${percent}%`
                : "0 задач · сборник пуст"}
            </div>
            <div className={`progress${!showCompleted && isCurrent ? " pp" : ""}`}>
              <i style={{ width: `${percent}%` }} />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => onOpen(chapter)}>
              Открыть сборник
            </button>
            {onContinue ? (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                disabled={!hasTasks}
                onClick={() => onContinue(chapter)}
              >
                {chapter.button_label || (showCompleted ? "Повторить" : "Продолжить")}
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
