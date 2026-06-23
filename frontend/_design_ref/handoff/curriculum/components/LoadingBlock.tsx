// handoff/curriculum/components/LoadingBlock.tsx
// Переиспользуемые блоки загрузки в палитре Toxic Pulse:
//  - <Spinner/>          — кольцевой индикатор
//  - <Skeleton/>         — мерцающая плашка (line/box)
//  - <LoadingBlock/>     — карточка «спиннер + подпись»
//  - <CardSkeleton/>     — скелет карточки сборника/задачи
import type { CSSProperties } from "react";

/* ---------- Spinner ---------- */
interface SpinnerProps {
  size?: number;
  className?: string;
}
export function Spinner({ size = 34, className = "" }: SpinnerProps) {
  const style: CSSProperties = { width: size, height: size, borderWidth: Math.max(2, size / 11) };
  return (
    <span
      role="status"
      aria-label="Загрузка"
      style={style}
      className={"inline-block animate-spin rounded-full border-surface-3 border-t-lime " + className}
    />
  );
}

/* ---------- Skeleton ---------- */
interface SkeletonProps {
  width?: number | string;
  height?: number | string;
  rounded?: string; // tailwind radius class
  className?: string;
}
export function Skeleton({ width = "100%", height = 14, rounded = "rounded-md", className = "" }: SkeletonProps) {
  return (
    <span
      aria-hidden
      style={{ width, height }}
      className={
        "block animate-pulse bg-[linear-gradient(90deg,var(--surface)_25%,var(--surface-3)_37%,var(--surface)_63%)] " +
        "bg-[length:400%_100%] " +
        rounded +
        " " +
        className
      }
    />
  );
}

/* ---------- LoadingBlock (spinner + caption card) ---------- */
interface LoadingBlockProps {
  text?: string;
  minHeight?: number;
  className?: string;
}
export default function LoadingBlock({ text = "Загрузка…", minHeight = 240, className = "" }: LoadingBlockProps) {
  return (
    <div
      style={{ minHeight }}
      className={
        "grid place-items-center gap-3.5 rounded-2xl border border-border bg-surface p-6 text-center " + className
      }
    >
      <Spinner />
      <span className="text-[13.5px] text-ink-muted">{text}</span>
    </div>
  );
}

/* ---------- CardSkeleton (для списков карточек) ---------- */
interface CardSkeletonProps {
  rows?: number;
}
export function CardSkeleton({ rows = 3 }: CardSkeletonProps) {
  return (
    <div className="grid gap-3.5">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="rounded-2xl border border-border bg-surface p-5">
          <div className="mb-3 flex items-center gap-3">
            <Skeleton width={40} height={40} rounded="rounded-xl" />
            <div className="flex-1">
              <Skeleton width="45%" height={15} className="mb-2" />
              <Skeleton width="70%" height={12} />
            </div>
          </div>
          <Skeleton height={8} rounded="rounded-full" />
        </div>
      ))}
    </div>
  );
}
