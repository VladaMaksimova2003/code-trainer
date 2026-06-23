// handoff/curriculum/components/ChapterCard.tsx
import type { Collection } from "../types";
import ProgressBar from "./ProgressBar";
import Badge from "./Badge";

interface Props {
  chapter: Collection;
  isCurrent?: boolean;
  isLast?: boolean;
  onOpen: (chapter: Collection) => void;
  onContinue: (chapter: Collection) => void;
}

export default function ChapterCard({
  chapter,
  isCurrent = false,
  isLast = false,
  onOpen,
  onContinue,
}: Props) {
  const { progress, completed } = chapter;
  const percent = progress.total_tasks
    ? Math.round((progress.passed_tasks / progress.total_tasks) * 100)
    : 0;

  const nodeClass = completed
    ? "border-lime/45 bg-lime/15 text-lime"
    : isCurrent
      ? "border-purple/50 bg-purple/15 text-[#b89bff]"
      : "border-border-strong bg-surface-2 text-ink-muted";

  return (
    <div
      className={
        "relative grid grid-cols-1 gap-2.5 rounded-2xl border bg-surface p-5 transition sm:grid-cols-[52px_1fr] sm:gap-4 " +
        "hover:border-lime/35 hover:shadow-[0_18px_44px_-28px_rgba(142,255,1,0.45)] " +
        (completed ? "border-lime/25" : "border-border")
      }
    >
      {/* node + connector */}
      <div className="relative flex flex-row items-center gap-2.5 sm:flex-col">
        <div
          className={
            "z-[1] grid h-10 w-10 flex-none place-items-center rounded-xl border text-[16px] font-extrabold " +
            nodeClass
          }
        >
          {completed ? "✓" : chapter.order}
        </div>
        {!isLast && (
          <span className="absolute left-1/2 top-10 bottom-[-32px] hidden w-0.5 -translate-x-1/2 bg-gradient-to-b from-border-strong to-transparent sm:block" />
        )}
      </div>

      {/* body */}
      <div className="min-w-0">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <b className="text-[16px] text-ink">{chapter.title_ru}</b>
          {completed ? (
            <Badge tone="lime">✓ Все пройдены</Badge>
          ) : isCurrent ? (
            <Badge tone="purple">Текущий</Badge>
          ) : null}
        </div>
        <p className="m-0 text-[13.5px] text-ink-muted">{chapter.description_ru}</p>

        <div className="mt-3 grid grid-cols-1 items-center gap-3.5 sm:grid-cols-[1fr_auto]">
          <div>
            <div className="mb-1.5 font-mono text-[12px] text-ink-faint">
              {progress.passed_tasks}/{progress.total_tasks} · {percent}%
            </div>
            <ProgressBar percent={percent} purple={!completed && isCurrent} />
          </div>
          <div className="flex gap-2">
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => onOpen(chapter)}>
              Открыть сборник
            </button>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              disabled={!chapter.next_task}
              onClick={() => onContinue(chapter)}
            >
              {chapter.button_label}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
