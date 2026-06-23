import type { ShowcaseTask } from "../types"
import { actionMetaFor, difficultyLabel, difficultyTone } from "../actionMeta"
import CurriculumBadge from "./CurriculumBadge"
import LangPills from "@/features/student/ui/LangPills"
import LangStatus from "@/features/student/ui/LangStatus"

interface CurriculumShowcaseTaskCardProps {
  task: ShowcaseTask
  isGuest?: boolean
  onOpen: (taskId: number) => void
}

export default function CurriculumShowcaseTaskCard({
  task,
  isGuest = false,
  onOpen,
}: CurriculumShowcaseTaskCardProps) {
  const meta = actionMetaFor(task.action)
  const status = task.progress_status
  const showStatus = !isGuest && status && status !== "not_started"
  const trackTask = {
    id: task.task_id,
    available_language_tracks: task.available_language_tracks,
    language_track_states: task.language_track_states,
    solved: status === "passed",
    attempted: status === "failed",
  }

  const borderState =
    !isGuest && status === "passed"
      ? "border-lime/40"
      : !isGuest && status === "failed"
        ? "border-amber-400/40"
        : "border-border"

  const subtopic = task.subtopic_name_ru || "—"

  return (
    <button
      type="button"
      onClick={() => onOpen(task.task_id)}
      className={
        "flex w-full flex-col gap-2.5 rounded-2xl border bg-surface p-4 text-left transition " +
        "hover:-translate-y-0.5 hover:border-lime/45 hover:bg-surface-2 " +
        "hover:shadow-[0_16px_38px_-26px_rgba(142,255,1,0.45)] focus:outline-none " +
        "focus-visible:border-lime focus-visible:ring-2 focus-visible:ring-lime/20 " +
        borderState
      }
    >
      <div className="flex items-center justify-between gap-2">
        <CurriculumBadge tone={meta.tone}>
          <span aria-hidden>{meta.icon}</span> {task.action_label || meta.label}
        </CurriculumBadge>
        <div className="flex items-center gap-1.5">
          <CurriculumBadge tone={difficultyTone(task.difficulty)}>
            {difficultyLabel(task.difficulty)}
          </CurriculumBadge>
          {!isGuest && task.language_track_states ? (
            <LangStatus task={trackTask} />
          ) : showStatus ? (
            status === "passed" ? (
              <CurriculumBadge tone="lime">✓ Пройдено</CurriculumBadge>
            ) : (
              <CurriculumBadge tone="warn">Ещё раз</CurriculumBadge>
            )
          ) : null}
        </div>
      </div>

      <div>
        <b className="block text-[15px] text-ink">{task.title}</b>
        {task.action_skill_label ? (
          <span className="text-[12.5px] font-semibold text-[#b89bff]">{task.action_skill_label}</span>
        ) : null}
      </div>

      {task.action_description_ru ? (
        <p className="m-0 text-[13px] text-ink-muted">{task.action_description_ru}</p>
      ) : null}

      {task.short_instruction ? (
        <p className="m-0 line-clamp-2 text-[12.5px] leading-relaxed text-ink-faint">
          {task.short_instruction}
        </p>
      ) : null}

      <div className="mt-0.5 flex flex-wrap items-center justify-between gap-2 border-t border-border pt-2.5">
        <span className="text-[11.5px] text-ink-faint">◷ {subtopic}</span>
        {!isGuest && task.language_track_states ? <LangPills task={trackTask} /> : null}
      </div>
    </button>
  )
}
