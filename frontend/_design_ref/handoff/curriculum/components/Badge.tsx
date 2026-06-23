// handoff/curriculum/components/Badge.tsx
// Лёгкий бейдж в палитре Toxic Pulse. Замените на свой общий Badge при наличии.
import type { ReactNode } from "react";
import type { BadgeTone } from "../actionMeta";
import { BADGE_TONE_CLASS } from "../actionMeta";

interface BadgeProps {
  tone?: BadgeTone;
  children: ReactNode;
  className?: string;
}

export default function Badge({ tone = "muted", children, className = "" }: BadgeProps) {
  return (
    <span
      className={
        "inline-flex h-6 items-center gap-1.5 rounded-full border px-2.5 text-[12px] font-semibold " +
        BADGE_TONE_CLASS[tone] +
        " " +
        className
      }
    >
      {children}
    </span>
  );
}
