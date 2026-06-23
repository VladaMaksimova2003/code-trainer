import { useCallback, useEffect, useRef, useState, type MouseEvent, type ReactNode } from "react"
import {
  buildTestRows,
  countTestStats,
  formatAlgorithmFeedbackForDisplay,
  formatTestDuration,
  formatTestIoCell,
  isTransferPitfallError,
  normalizePanelErrors,
  parseStandardDiagnostic,
} from "@/features/task-solving/model/testPanelUtils"
import { testInputDisplayContextFromTask } from "@/features/task-solving/model/testInputDisplay"
import { getPostSolveExplanation } from "@/features/task-solving/model/studentUiUtils"
import SubmissionCommentsTab from "@/widgets/test-panel/SubmissionCommentsTab"
import type { FlowCheckDebug } from "@/shared/types/flow"
import type { PanelError, TestCaseResult } from "@/shared/types/execution"
import type { TaskDto } from "@/shared/types/task"

interface TabButtonProps {
  active: boolean
  dotClass: string
  label: string
  badge?: string | number | null
  badgeClass: string
  onClick: () => void
}

interface StudentBottomPanelProps {
  bottomTab: string
  setBottomTab: (tab: string) => void
  task: TaskDto | null | undefined
  results: TestCaseResult[]
  compilerErrors: PanelError[]
  linterErrors: PanelError[]
  patternErrors: PanelError[]
  flowCheckDebug?: FlowCheckDebug | null
  onRun?: () => void | Promise<void>
  isSubmitting?: boolean
  isTeacherReview?: boolean
  activeSubmissionId?: number | string | null
  currentUser?: { id?: number | string } | null
  learningLanguage?: string
}

function PlayIcon() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden>
      <path d="M4 3l9 5-9 5V3z" fill="currentColor" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M3 8.5l3.5 3.5L13 5" />
    </svg>
  )
}

function CrossIcon() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M4 4l8 8M12 4l-8 8" />
    </svg>
  )
}

function AlgorithmFeedbackView({ text }: { text: string }) {
  const feedback = formatAlgorithmFeedbackForDisplay(text)
  return (
    <div className="text-[13px] mt-1.5 leading-relaxed text-ink space-y-2">
      <ul className="space-y-2 list-none pl-0">
        {feedback.sections.map((section, sectionIndex) => (
          <li
            key={`algorithm-section-${sectionIndex}`}
            className="rounded-md border border-[var(--line)] bg-surface-2/40 px-2.5 py-2"
          >
            {section.label ? (
              <div className="text-[10.5px] font-semibold uppercase tracking-[0.06em] text-ink-muted mb-1">
                {section.label}
              </div>
            ) : null}
            <p className="whitespace-pre-wrap">{section.body}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}

function MpltHintView({ text }: { text: string }) {
  const sections = String(text || "")
    .split(/\n{2,}/)
    .map((part) => part.trim())
    .filter(Boolean)

  return (
    <div className="mt-2 space-y-2 text-[13px] leading-relaxed text-ink">
      {sections.map((section, index) => {
        const labelMatch = section.match(/^([^:\n]{2,32}):\n([\s\S]+)$/)
        if (labelMatch) {
          return (
            <div key={`mplt-section-${index}`} className="rounded-md border border-[var(--line)] bg-surface-2/50 p-2.5">
              <div className="mb-1.5 text-[10.5px] font-semibold uppercase tracking-[0.07em] text-ink-muted">
                {labelMatch[1]}
              </div>
              <pre className="m-0 whitespace-pre-wrap font-mono text-[12.5px] leading-relaxed text-ink">
                {labelMatch[2]}
              </pre>
            </div>
          )
        }

        return (
          <p key={`mplt-section-${index}`} className="m-0 whitespace-pre-wrap">
            {section}
          </p>
        )
      })}
    </div>
  )
}

const THIN_BORDER = "border border-[var(--line)]"
const DEFAULT_PANEL_HEIGHT = 220
const MIN_PANEL_HEIGHT = 140
const PANEL_HEIGHT_STORAGE_KEY = "ct-student-bottom-panel-h"

function getMaxPanelHeight() {
  if (typeof window === "undefined") return 480
  return Math.min(window.innerHeight * 0.75, window.innerHeight - 160)
}

function readStoredPanelHeight() {
  if (typeof window === "undefined") return DEFAULT_PANEL_HEIGHT
  const parsed = Number(window.sessionStorage.getItem(PANEL_HEIGHT_STORAGE_KEY))
  if (!Number.isFinite(parsed)) return DEFAULT_PANEL_HEIGHT
  return Math.min(getMaxPanelHeight(), Math.max(MIN_PANEL_HEIGHT, parsed))
}

function clampPanelHeight(height) {
  return Math.min(getMaxPanelHeight(), Math.max(MIN_PANEL_HEIGHT, height))
}

function TabButton({ active, dotClass, label, badge, badgeClass, onClick }: TabButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`h-11 px-3 inline-flex items-center gap-2 text-[13px] font-medium border-b-2 transition -mb-px ${
        active
          ? "border-lime text-ink"
          : "border-transparent text-ink-faint hover:text-ink"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dotClass}`} />
      <span>{label}</span>
      {badge != null && (
        <span
          className={`inline-flex items-center justify-center h-5 min-w-[28px] px-1.5 rounded-md text-[11px] font-mono font-semibold ${THIN_BORDER} ${badgeClass}`}
        >
          {badge}
        </span>
      )}
    </button>
  )
}

function resultBadge(status: string): ReactNode {
  if (status === "PASSED") {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-lime-soft text-lime border border-[rgba(142,255,1,.35)] text-[11.5px] font-semibold">
        <CheckIcon />
        Пройден
      </span>
    )
  }
  if (status === "FAILED" || status === "ERROR") {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-danger-soft text-danger border border-[rgba(255,77,106,.35)] text-[11.5px] font-semibold">
        <CrossIcon />
        Провал
      </span>
    )
  }
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-surface-2 text-ink-faint text-[11.5px] font-semibold ${THIN_BORDER}`}
    >
      ○ Ожидает
    </span>
  )
}

const ERROR_PRESENTATION = {
  purple: {
    card: "rounded-lg border px-3.5 py-2.5 flex items-start gap-3 bg-purple-soft border-[rgba(139,83,254,.35)] text-[#b89bff]",
    iconBox: "h-7 w-7 shrink-0 rounded-md flex items-center justify-center bg-purple/15",
    icon: "i",
    tagBorder: THIN_BORDER,
  },
  warning: {
    card: "rounded-lg border px-3.5 py-2.5 flex items-start gap-3 bg-warning-soft/40 border-[rgba(255,180,61,.3)] text-warning",
    iconBox: "h-7 w-7 shrink-0 rounded-md flex items-center justify-center bg-warning/15",
    icon: "!",
    tagBorder: THIN_BORDER,
  },
  danger: {
    card: "rounded-lg border px-3.5 py-2.5 flex items-start gap-3 bg-danger-soft/30 border-[rgba(255,77,106,.3)] text-danger",
    iconBox: "h-7 w-7 shrink-0 rounded-md flex items-center justify-center bg-danger/15",
    icon: "!",
    tagBorder: THIN_BORDER,
  },
}

const REDUNDANT_ERROR_TYPES = new Set([
  "COMPILER",
  "LINT",
  "LINTER",
  "RUNTIME",
  "PATTERN",
  "INTERNAL_ERROR",
  "TIMEOUT",
  "ALGORITHM",
  "CONSTRUCTION_WARNING",
  "CONSTRUCTION",
  "TRANSFER_PITFALL",
])

function getErrorPresentation(tone: string) {
  return ERROR_PRESENTATION[tone as keyof typeof ERROR_PRESENTATION] || ERROR_PRESENTATION.danger
}

function findConstructionHint(error: PanelError, hints: Record<string, unknown> = {}) {
  if (!hints || typeof hints !== "object") return null
  const text = String(error?.text || "")
  for (const [patternId, hint] of Object.entries(hints)) {
    const hintRecord = hint as { title?: string; description?: string; hint?: string }
    const title = hintRecord?.title || patternId
    if (text.includes(title) || text.includes(patternId)) {
      return hintRecord?.description || hintRecord?.hint || null
    }
  }
  return null
}

function formatErrorLocation(error: PanelError) {
  if (error?.line != null) {
    return `строка ${error.line}${error?.column != null ? `, колонка ${error.column}` : ""}`
  }
  const parsed = parseStandardDiagnostic(error?.text)
  if (!parsed) return null
  return `строка ${parsed.line}${parsed.column != null ? `, колонка ${parsed.column}` : ""}`
}

export default function StudentBottomPanel({
  bottomTab,
  setBottomTab,
  task,
  results,
  compilerErrors,
  linterErrors,
  patternErrors,
  flowCheckDebug = null,
  onRun,
  isSubmitting = false,
  isTeacherReview = false,
  activeSubmissionId = null,
  currentUser = null,
  learningLanguage = "pascal",
}: StudentBottomPanelProps) {
  const [commentCount, setCommentCount] = useState(0)
  const [panelHeight, setPanelHeight] = useState(readStoredPanelHeight)
  const resizeStateRef = useRef({ dragging: false, startY: 0, startHeight: DEFAULT_PANEL_HEIGHT })

  const handleResizeStart = useCallback(
    (event: MouseEvent) => {
      event.preventDefault()
      resizeStateRef.current = {
        dragging: true,
        startY: event.clientY,
        startHeight: panelHeight,
      }
      document.body.style.cursor = "ns-resize"
      document.body.style.userSelect = "none"
    },
    [panelHeight],
  )

  const handleResizeReset = useCallback(() => {
    setPanelHeight(DEFAULT_PANEL_HEIGHT)
  }, [])

  useEffect(() => {
    const onMouseMove = (event) => {
      if (!resizeStateRef.current.dragging) return
      const delta = resizeStateRef.current.startY - event.clientY
      setPanelHeight(clampPanelHeight(resizeStateRef.current.startHeight + delta))
    }

    const stopResize = () => {
      if (!resizeStateRef.current.dragging) return
      resizeStateRef.current.dragging = false
      document.body.style.cursor = ""
      document.body.style.userSelect = ""
    }

    window.addEventListener("mousemove", onMouseMove)
    window.addEventListener("mouseup", stopResize)
    return () => {
      window.removeEventListener("mousemove", onMouseMove)
      window.removeEventListener("mouseup", stopResize)
      document.body.style.cursor = ""
      document.body.style.userSelect = ""
    }
  }, [])

  useEffect(() => {
    window.sessionStorage.setItem(PANEL_HEIGHT_STORAGE_KEY, String(panelHeight))
  }, [panelHeight])

  useEffect(() => {
    const onWindowResize = () => {
      setPanelHeight((current) => clampPanelHeight(current))
    }
    window.addEventListener("resize", onWindowResize)
    return () => window.removeEventListener("resize", onWindowResize)
  }, [])

  const testRows = buildTestRows(
    task?.test_cases,
    results,
    testInputDisplayContextFromTask(task, learningLanguage),
  )
  const stats = countTestStats(testRows)
  const postSolveExplanation = getPostSolveExplanation(task)
  const errors = normalizePanelErrors(compilerErrors, linterErrors, patternErrors)
  const activeTab =
    bottomTab === "errors" ? "errors" : bottomTab === "comments" ? "comments" : "tests"

  const testsBadge = stats.total > 0 ? `${stats.passed} / ${stats.total}` : "0"
  const testsBadgeClass =
    stats.failed > 0
      ? "bg-danger-soft text-danger !border-[rgba(255,77,106,.28)]"
      : stats.passed > 0
        ? "bg-lime-soft text-lime !border-[rgba(142,255,1,.28)]"
        : "bg-surface-2 text-ink-faint"

  const errorsBadgeClass =
    errors.length > 0
      ? "bg-danger-soft text-danger !border-[rgba(255,77,106,.28)]"
      : "bg-lime-soft text-lime !border-[rgba(142,255,1,.28)]"

  return (
    <div className="shrink-0 w-full border-t border-border bg-bg flex flex-col">
      <div
        role="separator"
        aria-orientation="horizontal"
        aria-valuenow={panelHeight}
        aria-valuemin={MIN_PANEL_HEIGHT}
        aria-valuemax={getMaxPanelHeight()}
        title="Потяните вверх или вниз, чтобы изменить высоту. Двойной клик — сброс."
        onMouseDown={handleResizeStart}
        onDoubleClick={handleResizeReset}
        className="group flex h-2 w-full shrink-0 cursor-ns-resize items-center justify-center touch-none hover:bg-surface/70 active:bg-surface"
      >
        <div className="h-1 w-10 rounded-full bg-ink-faint/35 transition group-hover:bg-ink-faint/60 group-active:bg-lime/70" />
      </div>
      <div className="flex items-center gap-1 px-5 border-b border-border bg-surface/40 h-11 shrink-0">
        <TabButton
          active={activeTab === "tests"}
          dotClass={stats.failed > 0 ? "bg-danger" : stats.passed > 0 ? "bg-lime" : "bg-ink-faint"}
          label="Тесты"
          badge={testsBadge}
          badgeClass={testsBadgeClass}
          onClick={() => setBottomTab("case")}
        />
        <TabButton
          active={activeTab === "errors"}
          dotClass={errors.length > 0 ? "bg-danger" : "bg-lime"}
          label="Ошибки"
          badge={String(errors.length)}
          badgeClass={errorsBadgeClass}
          onClick={() => setBottomTab("errors")}
        />
        <TabButton
          active={activeTab === "comments"}
          dotClass={commentCount > 0 ? "bg-purple" : "bg-ink-faint"}
          label="Комментарии"
          badge={commentCount > 0 ? String(commentCount) : undefined}
          badgeClass={
            commentCount > 0
              ? "bg-purple-soft text-purple !border-[rgba(139,83,254,.28)]"
              : "bg-surface-2 text-ink-faint"
          }
          onClick={() => setBottomTab("comments")}
        />
        <div className="flex-1" />
        {!isTeacherReview && (
          <button
            type="button"
            onClick={onRun}
            disabled={isSubmitting || !onRun}
            className="inline-flex items-center gap-1.5 h-8 px-3.5 rounded-md text-[13px] font-semibold transition shrink-0 bg-lime text-bg hover:bg-[#a4ff3a] disabled:cursor-not-allowed disabled:opacity-60"
          >
            <PlayIcon />
            {isSubmitting ? "Проверка…" : "Прогнать"}
          </button>
        )}
      </div>

      <div className="overflow-y-auto min-h-0" style={{ height: panelHeight }}>
        {activeTab === "tests" && (
          <div className="px-5 py-3">
            {testRows.length === 0 ? (
              <div className="text-sm text-ink-muted">Тесты не заданы.</div>
            ) : (
              <>
                {flowCheckDebug?.validator?.expected_sequence ? (
                  <div className="mb-3 rounded-lg border border-border bg-surface-2/70 px-3 py-2.5 text-[12.5px] leading-relaxed text-ink-muted">
                    <div>
                      <span className="text-ink-faint">Ожидаемая структура: </span>
                      {flowCheckDebug.validator.expected_sequence}
                    </div>
                    {flowCheckDebug.validator.detected_sequence ? (
                      <div className="mt-1">
                        <span className="text-ink-faint">Построено: </span>
                        {flowCheckDebug.validator.detected_sequence}
                      </div>
                    ) : null}
                  </div>
                ) : null}
                <table className="w-full text-[13px] border-collapse">
                  <thead>
                    <tr className="text-[10.5px] uppercase tracking-[0.08em] text-ink-faint">
                      <th className="w-14 py-2 px-3 text-left font-semibold border-b border-border">#</th>
                      <th className="py-2 px-3 text-left font-semibold border-b border-border">Вход</th>
                      <th className="w-32 py-2 px-3 text-left font-semibold border-b border-border">Ожидаемый</th>
                      <th className="w-32 py-2 px-3 text-left font-semibold border-b border-border">Получили</th>
                      <th className="w-24 py-2 px-3 text-right font-semibold border-b border-border">Время</th>
                      <th className="w-32 py-2 px-3 text-right font-semibold border-b border-border">Результат</th>
                    </tr>
                  </thead>
                  <tbody>
                    {testRows.map((row) => {
                      const isFailed = row.status === "FAILED" || row.status === "ERROR"
                      const isPassed = row.status === "PASSED"
                      const rowClass = isFailed
                        ? "transition bg-danger-soft/25 border-b border-border last:border-b-0"
                        : isPassed
                          ? "transition hover:bg-lime-soft/15 border-b border-border last:border-b-0"
                          : "transition border-b border-border last:border-b-0"

                      return (
                        <tr key={row.case} className={rowClass}>
                          <td className="py-1.5 px-3">
                            <div className="flex items-center gap-2">
                              <span
                                className={`h-2 w-2 rounded-full ${
                                  isPassed
                                    ? "bg-lime"
                                    : isFailed
                                      ? "bg-danger"
                                      : "border border-[var(--line)]"
                                }`}
                              />
                              <span className="font-mono text-ink-muted">#{row.case}</span>
                            </div>
                          </td>
                          <td
                            className="py-1.5 px-3 font-mono text-ink whitespace-pre-line break-words align-top max-w-[12rem]"
                            title={row.input ?? ""}
                          >
                            {formatTestIoCell(row.input)}
                          </td>
                          <td className="py-1.5 px-3 font-mono text-lime whitespace-pre-line break-words align-top">
                            {formatTestIoCell(row.expected)}
                          </td>
                          <td className={`py-1.5 px-3 font-mono ${isFailed ? "text-danger" : isPassed ? "text-lime" : "text-ink-faint"}`}>
                            {row.actual || (row.status === "PENDING" ? "—" : "")}
                          </td>
                          <td className="py-1.5 px-3 text-right font-mono text-ink-faint text-[12px]">
                            {formatTestDuration(row.durationMs)}
                          </td>
                          <td className="py-1.5 px-3 text-right">{resultBadge(row.status)}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>

                <div className="mt-3 space-y-2 text-[12.5px]">
                  <div className="flex flex-wrap items-center gap-3">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-medium bg-surface-2 text-ink-muted ${THIN_BORDER}`}
                    >
                      <CheckIcon />
                      Пройдено {stats.passed} из {stats.total}
                    </span>
                    {stats.failed > 0 && (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border font-medium bg-danger-soft text-danger border-[rgba(255,77,106,.4)]">
                        <CrossIcon />
                        Провалено {stats.failed}
                      </span>
                    )}
                    {stats.total > 0 && stats.failed === 0 && stats.passed === stats.total && (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border font-medium bg-lime-soft text-lime border-[rgba(142,255,1,.35)]">
                        <CheckIcon />
                        Все тесты пройдены
                      </span>
                    )}
                    {stats.pending > 0 && stats.passed === 0 && stats.failed === 0 && (
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-medium bg-surface-2 text-ink-faint ${THIN_BORDER}`}>
                        Нажмите «Прогнать», чтобы проверить решение
                      </span>
                    )}
                  </div>
                  {stats.failed > 0 && postSolveExplanation ? (
                    <div className="w-full rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2.5 text-[13px] leading-relaxed text-ink-muted">
                      <div className="text-[10.5px] font-semibold uppercase tracking-[0.08em] text-amber-400/90 mb-1">
                        Разбор решения
                      </div>
                      <p>{postSolveExplanation}</p>
                    </div>
                  ) : null}
                </div>
              </>
            )}
          </div>
        )}

        {activeTab === "errors" && (
          <div className="px-5 py-3">
            {errors.length === 0 ? (
              <div className="text-sm text-ink-muted">Ошибок нет.</div>
            ) : (
              <ul className="space-y-1.5">
                {errors.map((error, index) => {
                  const location = formatErrorLocation(error)
                  const presentation = getErrorPresentation(error.tone)
                  const constructionHint =
                    error.tone === "purple" ? findConstructionHint(error, task?.construction_hints) : null
                  return (
                    <li key={`${error.source}-${error.type}-${index}`} className={presentation.card}>
                      <div className={presentation.iconBox}>
                        <span className="font-bold text-[12px] leading-none">{presentation.icon}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-[10.5px] uppercase tracking-[0.08em] font-semibold opacity-80">
                            {error.sourceLabel}
                          </span>
                          {error.type &&
                            !REDUNDANT_ERROR_TYPES.has(String(error.type).toUpperCase()) && (
                            <span
                              className={`font-mono text-[10.5px] px-1.5 py-0.5 rounded bg-surface-2 text-ink-muted ${presentation.tagBorder}`}
                            >
                              {error.type}
                            </span>
                          )}
                          {location && (
                            <span className="font-mono text-[10.5px] text-ink-faint">{location}</span>
                          )}
                        </div>
                        {error.source === "Алгоритм" ? (
                          <AlgorithmFeedbackView text={String(error.text ?? "")} />
                        ) : isTransferPitfallError(error) ? (
                          <MpltHintView text={String(error.text ?? "")} />
                        ) : (
                          <div
                            className={`text-[13px] mt-1 leading-snug ${
                              error.tone === "purple" || isTransferPitfallError(error)
                                ? "text-ink whitespace-pre-wrap"
                                : "text-ink whitespace-pre-wrap font-mono"
                            }`}
                          >
                            {error.text}
                          </div>
                        )}
                        {constructionHint && (
                          <div className="text-[12px] text-ink-muted mt-1 leading-relaxed whitespace-pre-wrap font-mono">
                            {constructionHint}
                          </div>
                        )}
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
            {import.meta.env.DEV && flowCheckDebug && (
              <div className="mt-4 rounded-md border border-border bg-surface-2/60 p-3 font-mono text-[11.5px] leading-relaxed text-ink-muted">
                <div className="mb-2 text-[10px] uppercase tracking-[0.08em] text-ink-faint">
                  Flow debug
                </div>
                {flowCheckDebug.request && (
                  <div className="mb-2">
                    <div>Sent: {flowCheckDebug.request.nodeCount} nodes, {flowCheckDebug.request.edgeCount} edges</div>
                    <div>Block types: {(flowCheckDebug.request.blockTypes || []).join(" → ")}</div>
                  </div>
                )}
                {flowCheckDebug.payloadMismatch && (
                  <div className="mb-2 text-warning">Editor graph ≠ React state (stale state was fixed at submit)</div>
                )}
                {flowCheckDebug.validator?.detected_sequence && (
                  <div className="mb-1">
                    Detected sequence: {flowCheckDebug.validator.detected_sequence}
                  </div>
                )}
                {flowCheckDebug.validator?.expected_sequence && (
                  <div className="mb-1">
                    Expected sequence: {flowCheckDebug.validator.expected_sequence}
                  </div>
                )}
                {flowCheckDebug.response && (
                  <div className="mb-1">
                    Response success: {String(flowCheckDebug.response.success)}; errors:{" "}
                    {(flowCheckDebug.response.errorTypes || []).join(", ") || "none"}
                  </div>
                )}
                {flowCheckDebug.validator?.error_types?.length > 0 && (
                  <div>Validator: {flowCheckDebug.validator.error_types.join(", ")}</div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === "comments" && (
          <SubmissionCommentsTab
            submissionId={activeSubmissionId}
            isTeacherReview={isTeacherReview}
            currentTeacherId={currentUser?.id}
            onCountChange={setCommentCount}
          />
        )}
      </div>
    </div>
  )
}
