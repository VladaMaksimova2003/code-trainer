/**
 * Стили редактора заданий — Toxic Pulse (surface, lime, ink, border).
 */

export const PLAQUE_PAD = "px-3 py-2"

export const teacherProfileLinkClass =
  "text-sm font-semibold text-lime transition-colors hover:text-lime-600"

const chipToggle = (active: boolean) =>
  active
    ? "tp-chip tp-chip-active h-9 rounded-md px-3 py-1.5 text-sm font-medium"
    : "tp-chip h-9 rounded-md px-3 py-1.5 text-sm font-medium"

export function optionToggle(active: boolean) {
  return `${chipToggle(active)} flex-1 text-center`
}

export function segmentToggle(active: boolean) {
  return chipToggle(active)
}

export function segmentToggleLight(active: boolean) {
  return `${PLAQUE_PAD} text-sm font-medium rounded-lg border-2 transition-colors ${
    active
      ? "border-lime/45 bg-lime/15 text-lime"
      : "border-border-strong bg-surface-2 text-ink-muted hover:text-ink"
  }`
}

export type PlaqueVariant =
  | "blue"
  | "red"
  | "green"
  | "amber"
  | "gray"
  | "violet"
  | "teal"

export const editorBtnTextPadding = "px-4 py-2.5"

export const teacherGhostBtn =
  "inline-flex min-h-10 items-center justify-center rounded-xl border border-border-strong " +
  "bg-transparent text-sm font-medium text-ink-muted transition hover:border-lime hover:text-ink " +
  "disabled:cursor-not-allowed disabled:opacity-50"

export const teacherPrimaryBtn =
  "inline-flex min-h-10 items-center justify-center rounded-xl bg-lime text-sm font-semibold text-bg " +
  "transition hover:bg-lime-600 shadow-[0_6px_22px_-10px_rgba(142,255,1,.5)] " +
  "disabled:cursor-not-allowed disabled:opacity-50"

export const teacherDangerBtn =
  "inline-flex min-h-10 items-center justify-center rounded-xl border border-danger/40 " +
  "bg-danger/15 text-sm font-medium text-[#ff8198] transition hover:bg-danger hover:text-white " +
  "disabled:cursor-not-allowed disabled:opacity-50"

const taskSolidBtn = `${teacherGhostBtn} ${editorBtnTextPadding}`

export function plaqueBtn(_variant: PlaqueVariant, extraClass = "") {
  return `${taskSolidBtn} ${extraClass}`.trim()
}

export function outlineMutedBtn(extraClass = "") {
  return `${taskSolidBtn} ${extraClass}`.trim()
}

export function solidButton(
  _role: "add" | "delete" | "clear" | "submit" | "done" | "secondary",
  extra = "",
) {
  return `${taskSolidBtn} ${extra}`.trim()
}

export function editorButton(
  role: "default" | "edit" | "danger" | "primary",
  extra = "",
) {
  if (role === "danger") return `${teacherDangerBtn} ${editorBtnTextPadding} ${extra}`.trim()
  if (role === "primary") return `${teacherPrimaryBtn} ${editorBtnTextPadding} ${extra}`.trim()
  return `${taskSolidBtn} ${extra}`.trim()
}

export function footerActionButton(role: "clear" | "submit", extra = "") {
  if (role === "submit") {
    return `${teacherPrimaryBtn} h-10 flex-1 ${extra}`.trim()
  }
  return `${teacherGhostBtn} h-10 flex-1 ${editorBtnTextPadding} ${extra}`.trim()
}

export function patternDropdownDoneBtn(extra = "") {
  return `${teacherPrimaryBtn} w-full ${extra}`.trim()
}

export const configPanelFrameClass =
  "te-frame flex min-h-0 flex-1 flex-col overflow-hidden"

export const executionPanelFrameClass =
  "te-frame flex min-h-0 flex-1 flex-col overflow-hidden"

export const configPanelSurfaceClass = "bg-surface"
export const executionPanelSurfaceClass = "bg-surface"

export const testDataFrameClass = "te-test-card"
export const testDataFrameTitleClass =
  "mb-4 text-sm font-semibold tracking-wide text-ink"

export const editorInputClass = "tp-input h-10"

export const editorSelectClass = "tp-select h-10"

export const editorSelectCompactClass =
  "h-9 w-auto min-w-[8rem] rounded-md border border-border-strong bg-bg-2 px-3 py-1.5 text-sm text-ink outline-none transition focus:border-lime focus:ring-2 focus:ring-lime/10"

export const editorSelectGhostClass =
  "h-10 w-auto min-w-[10rem] appearance-none rounded-md border border-border-strong bg-bg-2 px-4 py-2.5 text-sm text-ink shadow-sm outline-none transition focus:border-lime focus:ring-2 focus:ring-lime/10"

export const editorSelectClassLight =
  "w-full rounded-md border border-border-strong bg-bg-2 px-3 py-2 text-sm text-ink outline-none focus:border-lime focus:ring-2 focus:ring-lime/10"

export const editorLabelClass = "tp-label"

export const editorFieldBlockClass = "flex flex-col gap-3"

export const editorFieldGroupClass = "flex flex-col gap-5"

export const editorSectionDividerClass = "te-divider pt-6"

export const editorCardClass = editorFieldBlockClass

export function primarySubmitButton(extra = "") {
  return `${teacherGhostBtn} min-h-10 w-full ${editorBtnTextPadding} ${extra}`.trim()
}

export function secondaryActionButton(extra = "") {
  return `${teacherDangerBtn} ${editorBtnTextPadding} ${extra}`.trim()
}

export const patternChipListClass = "flex flex-wrap gap-2"

export const patternChipClass =
  "inline-flex max-w-full items-center gap-1 rounded-full border border-lime/45 bg-lime/15 py-1 pl-3 pr-1 text-[13px] font-medium text-lime"

export const patternChipLabelClass =
  "min-w-0 max-w-[220px] truncate text-left hover:underline decoration-lime/50 underline-offset-2"

export const patternChipRemoveBtnClass =
  "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-lime/70 transition hover:bg-danger/20 hover:text-danger"

export const patternDropdownPanelClass =
  "absolute left-0 right-0 z-40 mt-1 overflow-hidden rounded-xl border border-border bg-surface text-ink shadow-card"

export const listValueRemoveBtnClass =
  "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border-strong bg-surface-2 text-ink-faint transition hover:border-danger/60 hover:bg-danger/15 hover:text-danger"

export const listValueAddBtnClass =
  "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border-strong bg-surface-2 text-ink-faint transition hover:border-lime/50 hover:bg-lime/10 hover:text-lime"
