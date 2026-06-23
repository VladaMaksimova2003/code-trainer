import type { CurriculumShowcaseStudentDto } from "@/shared/types/curriculum"
import { progressPercent } from "../actionMeta"
import CurriculumProgressBar from "./CurriculumProgressBar"
import CurriculumShowcaseTaskCard from "./CurriculumShowcaseTaskCard"

export interface SubtopicSectionData {
  id?: string | null
  name_ru?: string | null
  tasks?: unknown[]
  progress?: {
    total_tasks?: number | null
    passed_tasks?: number | null
    progress_percent?: number | null
  } | null
}

interface SubtopicSectionProps {
  section: SubtopicSectionData
  index: number
  isGuest?: boolean
  onOpenTask: (taskId: number) => void
}

function mapTask(task: unknown) {
  const row = (task ?? {}) as Record<string, unknown>
  return {
    task_id: Number(row.task_id),
    title: String(row.title ?? ""),
    action: String(row.action ?? ""),
    action_label: String(row.action_label ?? ""),
    action_skill_label: String(row.action_skill_label ?? ""),
    action_description_ru: String(row.action_description_ru ?? ""),
    difficulty: String(row.difficulty ?? ""),
    progress_status: row.progress_status as string | null | undefined,
    short_instruction: String(row.short_instruction ?? ""),
    subtopic_name_ru: String(row.subtopic_name_ru ?? row.technical_concept_name_ru ?? ""),
    available_language_tracks: Array.isArray(row.available_language_tracks)
      ? row.available_language_tracks.map(String)
      : undefined,
    language_track_states: row.language_track_states as
      | Record<string, "solved" | "attempted" | "todo">
      | undefined,
  }
}

export default function SubtopicSection({
  section,
  index,
  isGuest = false,
  onOpenTask,
}: SubtopicSectionProps) {
  const tasks = (section.tasks ?? []).map(mapTask)
  const total = tasks.length
  const passed = tasks.filter((t) => t.progress_status === "passed").length
  const percent = total ? Math.round((passed / total) * 100) : progressPercent(section.progress)

  if (!total) return null

  return (
    <section>
      <div className="mb-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <span className="grid h-7 w-7 place-items-center rounded-lg border border-border-strong bg-surface-2 text-[12px] font-bold text-ink-muted">
            {index}
          </span>
          <h2 className="m-0 text-[16px] font-bold text-ink">{section.name_ru}</h2>
        </div>
        {!isGuest && (
          <div className="flex min-w-[180px] items-center gap-2.5">
            <span className="whitespace-nowrap font-mono text-[12px] text-ink-faint">
              {passed}/{total} · {percent}%
            </span>
            <CurriculumProgressBar percent={percent} className="w-[120px]" />
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2">
        {tasks.map((task) => (
          <CurriculumShowcaseTaskCard
            key={task.task_id}
            task={task}
            isGuest={isGuest}
            onOpen={onOpenTask}
          />
        ))}
      </div>
    </section>
  )
}

export function sectionsOf(res: CurriculumShowcaseStudentDto) {
  const sections = res.subtopics ?? res.technical_concepts ?? []
  if (sections.length > 0) return sections
  const flat = (res as CurriculumShowcaseStudentDto & { tasks?: unknown[] }).tasks
  if (flat?.length) {
    return [{ name_ru: res.title_ru ?? "Задачи", tasks: flat }]
  }
  return []
}

/** @deprecated Use SubtopicSection */
export const TechnicalConceptSection = SubtopicSection
