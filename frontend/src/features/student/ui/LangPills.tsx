import type { TaskListRow } from "@/features/student/utils/languageTrackProgress"
import {
  buildLanguageMatrix,
  languageStatusLabel,
} from "@/features/student/utils/languageTrackProgress"

interface LangPillsProps {
  task: TaskListRow
}

export default function LangPills({ task }: LangPillsProps) {
  const matrix = buildLanguageMatrix(task)

  return (
    <div className="lang-dots" aria-label="Прогресс по языкам">
      {matrix.map((entry) => (
        <span
          key={entry.id}
          className={`lang-dot ${entry.state}${entry.available ? "" : " inactive"}`}
          title={`${entry.label} — ${languageStatusLabel(entry.state)}`}
        />
      ))}
    </div>
  )
}
