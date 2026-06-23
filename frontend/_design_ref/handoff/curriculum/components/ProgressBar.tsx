// handoff/curriculum/components/ProgressBar.tsx
// Если ProgressBar уже есть в проекте — используйте свой и удалите этот файл.

interface ProgressBarProps {
  /** 0..100 */
  percent: number;
  /** purple-вариант (для curriculum/текущего сборника) */
  purple?: boolean;
  className?: string;
}

export default function ProgressBar({ percent, purple = false, className = "" }: ProgressBarProps) {
  const value = Math.max(0, Math.min(100, percent));
  return (
    <div className={`h-2 overflow-hidden rounded-full bg-surface-3 ${className}`}>
      <div
        className={
          "h-full rounded-full transition-[width] duration-500 " +
          (purple
            ? "bg-gradient-to-r from-purple to-[#a877ff]"
            : "bg-gradient-to-r from-lime to-lime-600")
        }
        style={{ width: `${value}%` }}
      />
    </div>
  );
}
