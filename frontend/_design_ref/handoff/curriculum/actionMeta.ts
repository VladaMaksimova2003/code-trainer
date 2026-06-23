// handoff/curriculum/actionMeta.ts
// Маппинг типа действия задачи → цвет бейджа и иконка.
// Цвета: translate=lime, assemble=purple, implement/debug=warn, analyze/recognize=muted.
import type { ActionType } from "./types";

export type BadgeTone = "lime" | "purple" | "warn" | "muted";

export interface ActionMeta {
  label: string;
  tone: BadgeTone;
  icon: string;
}

export const ACTION_META: Record<ActionType, ActionMeta> = {
  translate: { label: "Перенести", tone: "lime", icon: "⇄" },
  assemble: { label: "Собрать", tone: "purple", icon: "⧉" },
  implement: { label: "Реализовать", tone: "warn", icon: "⌨" },
  debug: { label: "Отладить", tone: "warn", icon: "⊘" },
  analyze: { label: "Разобрать", tone: "muted", icon: "◎" },
  recognize: { label: "Опознать", tone: "muted", icon: "?" },
};

// Классы Tailwind для бейджа по тону (Toxic Pulse).
export const BADGE_TONE_CLASS: Record<BadgeTone, string> = {
  lime: "border-lime/30 bg-lime/15 text-lime",
  purple: "border-purple/35 bg-purple/15 text-[#b89bff]",
  warn: "border-amber-400/35 bg-amber-400/15 text-amber-300",
  muted: "border-border-strong bg-surface-2 text-ink-muted",
};

export const DIFFICULTY_TONE: Record<string, BadgeTone> = {
  "Лёгкая": "muted",
  "Средняя": "warn",
  "Сложная": "muted",
};

export function actionMetaFor(action: ActionType): ActionMeta {
  return ACTION_META[action] ?? { label: action, tone: "muted", icon: "•" };
}
