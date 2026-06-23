import { useMemo, useState } from "react"
import { buildPatternUsageMap } from "@/features/task-solving/model/constructionHintsUtils"
import StudentExpectedConcepts, {
  pickTransferTextForTask,
  taskHasExpectedConceptsForLanguage,
  taskPedagogyMatchesLanguagePair,
} from "@/widgets/task-workspace/StudentExpectedConcepts"
import { getConstructionLabel, getTaskHints, getTaskPrimaryAction, isCppCurriculumTask, isPascalCurriculumTask, isPythonCurriculumTask } from "@/features/task-solving/model/studentUiUtils"
import { renderInlineMd } from "@/widgets/task-workspace/renderInlineMd"
import ConstructPopover from "@/widgets/task-workspace/ConstructPopover"
import TaskHintsPanel from "@/widgets/task-workspace/TaskHintsPanel"
import {
  TASK_LEFT_RAIL_MIN_WIDTH,
  useTaskLeftRailWidth,
} from "@/widgets/task-workspace/useTaskLeftRailWidth"
import type { TaskDto } from "@/shared/types/task"

interface AnchorRect {
  left: number
  bottom: number
}

interface ConstructPopoverState {
  pattern: string
  anchorRect: AnchorRect
}

interface StudentLeftRailProps {
  task: TaskDto | null | undefined
  userLanguage: string
  knownLanguage?: string
  learnedCode: string
  isAlgorithmTask: boolean
  isPedagogyRefreshing?: boolean
}

export default function StudentLeftRail({
  task,
  userLanguage,
  knownLanguage = "python",
  learnedCode,
  isAlgorithmTask,
  isPedagogyRefreshing = false,
}: StudentLeftRailProps) {
  const { width: railWidth, maxWidth, handleResizeStart, handleResizeReset } =
    useTaskLeftRailWidth()
  const constructions = (task?.constructions as string[] | undefined) || []
  const hints = (task?.construction_hints as Record<string, unknown> | undefined) || {}
  const [popover, setPopover] = useState<ConstructPopoverState | null>(null)
  const isPascalCurriculum = isPascalCurriculumTask(task)
  const isPythonCurriculum = isPythonCurriculumTask(task)
  const isCppCurriculum = isCppCurriculumTask(task)
  const learningLanguageLabel = isPythonCurriculum
    ? "Python"
    : isCppCurriculum
      ? "C++"
      : "Pascal"
  const curriculumMeta = task?.curriculum as { task_format?: string } | undefined
  const taskFormat = String(curriculumMeta?.task_format || "")
  const isDebugTask = getTaskPrimaryAction(task) === "debug"
  const debugHint =
    taskFormat === "поиск_ошибки"
      ? "Найдите ошибку в коде справа, исправьте его и нажмите «Проверить». Задача засчитывается, когда код компилируется без ошибок."
      : taskFormat === "исправление"
        ? `Исправьте код ${learningLanguageLabel} справа так, чтобы он выполнялся и проходил тесты, затем нажмите «Проверить».`
        : isDebugTask
          ? `Исправьте код ${learningLanguageLabel} справа и нажмите «Проверить».`
          : null
  const hasExpectedConcepts = taskHasExpectedConceptsForLanguage(task, userLanguage)
  const pedagogyReady = taskPedagogyMatchesLanguagePair(task, knownLanguage, userLanguage)
  const transferWarning = useMemo(
    () => (pedagogyReady ? pickTransferTextForTask(task) : null),
    [task, knownLanguage, userLanguage, pedagogyReady],
  )
  const taskHints = useMemo(
    () => getTaskHints(task),
    [task],
  )
  const showPedagogyRefreshNote =
    isPedagogyRefreshing &&
    !pedagogyReady &&
    !hasExpectedConcepts &&
    constructions.length === 0 &&
    taskHints.length === 0

  const usedMap = useMemo(
    () => buildPatternUsageMap(constructions, learnedCode),
    [constructions, learnedCode],
  )

  const onConstructClick = (pattern: string, element: HTMLElement) => {
    const rect = element.getBoundingClientRect()
    setPopover((current) =>
      current?.pattern === pattern ? null : { pattern, anchorRect: rect },
    )
  }

  return (
    <>
      <div
        className="task-left-rail-wrap relative flex shrink-0 flex-col bg-surface/30 border-r border-border overflow-hidden"
        style={{ width: railWidth }}
      >
        <aside className="flex min-h-0 flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-7">
          <section>
            <div className="text-[11px] font-semibold uppercase tracking-[0.1em] text-ink-faint mb-2">
              Задача
            </div>
            <h1 className="text-[26px] font-bold leading-[1.15] tracking-[-0.4px] text-ink">
              {task?.title || "Без названия"}
            </h1>
          </section>

          <section>
            <h3 className="text-[11px] font-semibold uppercase tracking-[0.1em] text-ink-faint mb-3">
              Условие
            </h3>
            <div className="text-[14px] text-ink-muted leading-relaxed whitespace-pre-line">
              {task?.description ? renderInlineMd(task.description) : "Описание не задано."}
            </div>
            {debugHint ? (
              <p className="mt-3 text-[13px] text-ink-muted leading-relaxed border-l-2 border-lime/40 pl-3">
                {debugHint}
              </p>
            ) : null}
            {showPedagogyRefreshNote ? (
              <p className="mt-3 text-[13px] text-ink-faint leading-relaxed border-l-2 border-border pl-3">
                Обновляем подсказки для выбранной пары языков…
              </p>
            ) : null}
            {transferWarning ? (
              <p className="mt-3 text-[13px] text-amber-200/90 leading-relaxed border-l-2 border-amber-400/50 pl-3 whitespace-pre-line">
                {transferWarning}
              </p>
            ) : null}
            {taskHints.length > 0 ? (
              <TaskHintsPanel hints={taskHints} taskId={task?.id} />
            ) : null}
          </section>

          {isAlgorithmTask && task?.solution_description && (
            <section className="rounded-xl border border-[rgba(139,83,254,.35)] bg-purple-soft p-4">
              <h3 className="text-[11px] font-semibold uppercase tracking-[0.1em] text-purple mb-2">
                Как решить
              </h3>
              <div className="text-[13px] text-ink-muted leading-relaxed whitespace-pre-line">
                {task.solution_description}
              </div>
            </section>
          )}

          {hasExpectedConcepts ? (
            <StudentExpectedConcepts
              task={task}
              knownLanguage={knownLanguage}
              learnedCode={learnedCode}
              learningLanguage={userLanguage}
            />
          ) : constructions.length > 0 ? (
            <section>
              <h3 className="text-[11px] font-semibold uppercase tracking-[0.1em] text-ink-faint mb-3">
                Ожидаемые конструкции
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {constructions.map((pattern) => {
                  const active = popover?.pattern === pattern
                  const used = usedMap[pattern]
                  return (
                    <button
                      key={pattern}
                      type="button"
                      data-construct-id={pattern}
                      onClick={(event) => onConstructClick(pattern, event.currentTarget)}
                      className={[
                        "inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[13px] font-medium transition",
                        used
                          ? "border border-[rgba(142,255,1,.32)] bg-[rgba(142,255,1,.12)] text-lime"
                          : "border border-border bg-surface-2 text-ink-faint hover:border-border-2 hover:text-ink-muted",
                        active ? "ring-1 ring-lime/12 text-[#c5ff6b]" : "",
                      ].join(" ")}
                    >
                      {getConstructionLabel(pattern, hints)}
                    </button>
                  )
                })}
              </div>
            </section>
          ) : null}
          </div>
        </aside>

        <div
          role="separator"
          aria-orientation="vertical"
          aria-valuenow={railWidth}
          aria-valuemin={TASK_LEFT_RAIL_MIN_WIDTH}
          aria-valuemax={maxWidth}
          title="Потяните влево или вправо, чтобы изменить ширину. Двойной клик — сброс."
          onMouseDown={handleResizeStart}
          onDoubleClick={handleResizeReset}
          className="task-left-rail-resize group absolute inset-y-0 right-0 z-10 flex w-2 cursor-ew-resize touch-none items-center justify-center hover:bg-surface/70 active:bg-surface"
        >
          <span className="h-10 w-0.5 rounded-full bg-border opacity-0 transition group-hover:opacity-100 group-active:opacity-100" />
        </div>
      </div>

      <ConstructPopover
        pattern={popover?.pattern}
        anchorRect={popover?.anchorRect}
        hints={hints}
        learningLang={userLanguage}
        used={popover?.pattern ? usedMap[popover.pattern] : false}
        onClose={() => setPopover(null)}
      />
    </>
  )
}
