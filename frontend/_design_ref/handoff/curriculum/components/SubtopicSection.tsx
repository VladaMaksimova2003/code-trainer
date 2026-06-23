// handoff/curriculum/components/SubtopicSection.tsx
import type { ShowcaseSection } from "../types";
import ProgressBar from "./ProgressBar";
import CurriculumShowcaseTaskCard from "./CurriculumShowcaseTaskCard";

interface Props {
  section: ShowcaseSection;
  index: number; // 1-based
  isGuest?: boolean;
  onOpenTask: (taskId: number) => void;
}

export default function SubtopicSection({ section, index, isGuest = false, onOpenTask }: Props) {
  const total = section.tasks.length;
  const passed = section.tasks.filter((t) => t.progress_status === "passed").length;
  const percent = total ? Math.round((passed / total) * 100) : 0;

  return (
    <section>
      <div className="mb-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <span className="grid h-6.5 w-6.5 place-items-center rounded-lg border border-border-strong bg-surface-2 text-[12px] font-bold text-ink-muted">
            {index}
          </span>
          <h2 className="m-0 text-[16px] font-bold text-ink">{section.name_ru}</h2>
        </div>
        {!isGuest && (
          <div className="flex min-w-[180px] items-center gap-2.5">
            <span className="whitespace-nowrap font-mono text-[12px] text-ink-faint">
              {passed}/{total} · {percent}%
            </span>
            <ProgressBar percent={percent} className="w-[120px]" />
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2">
        {section.tasks.map((task) => (
          <CurriculumShowcaseTaskCard
            key={task.task_id}
            task={task}
            isGuest={isGuest}
            onOpen={onOpenTask}
          />
        ))}
      </div>
    </section>
  );
}
