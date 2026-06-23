// handoff/curriculum/components/CurriculumShowcaseTaskCard.tsx
// Кликабельная карточка задачи. Вся карточка — кнопка → onOpen(task_id).
import type { ShowcaseTask } from "../types";
import { actionMetaFor, DIFFICULTY_TONE } from "../actionMeta";
import Badge from "./Badge";

interface Props {
  task: ShowcaseTask;
  /** Гость без прогресса — статусы не показываем. */
  isGuest?: boolean;
  onOpen: (taskId: number) => void;
}

export default function CurriculumShowcaseTaskCard({ task, isGuest = false, onOpen }: Props) {
  const meta = actionMetaFor(task.action);
  const status = task.progress_status;
  const showStatus = !isGuest && status && status !== "not_started";

  const borderState =
    !isGuest && status === "passed"
      ? "border-lime/40"
      : !isGuest && status === "failed"
        ? "border-amber-400/40"
        : "border-border";

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
      {/* action + difficulty + status */}
      <div className="flex items-center justify-between gap-2">
        <Badge tone={meta.tone}>
          <span aria-hidden>{meta.icon}</span> {task.action_label}
        </Badge>
        <div className="flex items-center gap-1.5">
          <Badge tone={DIFFICULTY_TONE[task.difficulty] ?? "muted"}>{task.difficulty}</Badge>
          {showStatus &&
            (status === "passed" ? (
              <Badge tone="lime">✓ Пройдено</Badge>
            ) : (
              <Badge tone="warn">Ещё раз</Badge>
            ))}
        </div>
      </div>

      {/* title + skill */}
      <div>
        <b className="block text-[15px] text-ink">{task.title}</b>
        <span className="text-[12.5px] font-semibold text-[#b89bff]">{task.action_skill_label}</span>
      </div>

      {/* what to do */}
      <p className="m-0 text-[13px] text-ink-muted">{task.action_description_ru}</p>

      {/* instruction preview (2 lines) */}
      <p className="m-0 line-clamp-2 text-[12.5px] leading-relaxed text-ink-faint">
        {task.short_instruction}
      </p>

      {/* subtopic */}
      <div className="mt-0.5 flex items-center gap-1.5 border-t border-border pt-2.5">
        <span className="text-[11.5px] text-ink-faint">◷ {task.subtopic_name_ru}</span>
      </div>
    </button>
  );
}
