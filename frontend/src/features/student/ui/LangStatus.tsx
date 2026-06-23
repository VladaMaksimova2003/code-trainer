import Badge from "@/shared/ui/Badge"
import { Dot } from "@/shared/ui/StatusBadge"
import type { TaskListRow } from "@/features/student/utils/languageTrackProgress"
import { buildLanguageMatrix } from "@/features/student/utils/languageTrackProgress"

interface LangStatusProps {
  task: TaskListRow
}

export default function LangStatus({ task }: LangStatusProps) {
  const matrix = buildLanguageMatrix(task)
  const pool = matrix.filter((entry) => entry.available)
  const entries = pool.length > 0 ? pool : matrix.slice(0, 1)
  const solvedCount = entries.filter((entry) => entry.state === "solved").length
  const attemptedCount = entries.filter((entry) => entry.state === "attempted").length
  const total = entries.length

  if (solvedCount === total && total > 0) {
    return (
      <span className="lang-status-master">
        <span className="lsm-star" aria-hidden>
          ★
        </span>
        Освоено
      </span>
    )
  }
  if (solvedCount > 0) {
    return (
      <Badge kind="lime">
        <Dot /> Решено
      </Badge>
    )
  }
  if (attemptedCount > 0) {
    return (
      <Badge kind="purple">
        <Dot /> Попытка
      </Badge>
    )
  }
  return (
    <Badge kind="muted">
      <Dot /> Не начато
    </Badge>
  )
}
