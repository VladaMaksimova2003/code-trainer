import { useState } from "react"
import ReadonlyCodeView from "@/widgets/task-workspace/ReadonlyCodeView"
import { langDisplay } from "@/features/task-solving/model/studentUiUtils"
import type { TaskDto } from "@/shared/types/task"

interface AnalyzeFeedback {
  ok: boolean
  text: string
}

interface StudentAnalyzePredictProps {
  task: TaskDto | null | undefined
  referenceLanguage?: string
  referenceCode: string
  onSubmitAnswer?: (answer: string) => void | Promise<void>
  isSubmitting?: boolean
}

function normalizeOutput(text = "") {
  return String(text).replace(/\r\n/g, "\n").trimEnd()
}

export default function StudentAnalyzePredict({
  task,
  referenceLanguage = "pascal",
  referenceCode,
  onSubmitAnswer,
  isSubmitting = false,
}: StudentAnalyzePredictProps) {
  const curriculum = task?.curriculum as { expected_output?: string } | undefined
  const expected =
    curriculum?.expected_output ??
    task?.expected_output ??
    task?.test_cases?.[0]?.output ??
    ""
  const [answer, setAnswer] = useState("")
  const [feedback, setFeedback] = useState<AnalyzeFeedback | null>(null)

  const handleCheck = async () => {
    const ok = normalizeOutput(answer) === normalizeOutput(String(expected))
    setFeedback(
      ok
        ? { ok: true, text: "Верно! Ответ совпадает с ожидаемым выводом." }
        : {
            ok: false,
            text: "Пока не совпало. Сравните вывод построчно и попробуйте ещё раз.",
          },
    )
    if (ok && onSubmitAnswer) {
      await onSubmitAnswer(normalizeOutput(answer))
    }
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="grid min-h-0 flex-1 grid-cols-2 grid-rows-1">
        <div className="min-h-0 overflow-auto border-r border-border bg-[#141a24]">
          <ReadonlyCodeView code={referenceCode} language={referenceLanguage} />
        </div>
        <div className="flex min-h-0 flex-col gap-4 overflow-auto bg-surface p-6">
          <div>
            <p className="text-sm font-medium text-ink">Предскажите результат</p>
            <p className="mt-1 text-sm text-ink-muted">
              Изучите фрагмент {langDisplay(referenceLanguage)} слева и введите ожидаемый вывод
              программы.
            </p>
          </div>
          <label className="flex flex-col gap-2 text-sm">
            <span className="font-medium text-ink">Ваш ответ (stdout)</span>
            <textarea
              className="min-h-[140px] rounded-lg border border-border bg-bg-2 p-3 font-mono text-sm text-ink outline-none focus:border-accent"
              value={answer}
              onChange={(event) => {
                setAnswer(event.target.value)
                setFeedback(null)
              }}
              placeholder="Например: 42 или yes"
              spellCheck={false}
            />
          </label>
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
              onClick={handleCheck}
              disabled={isSubmitting || !String(answer).trim()}
            >
              Проверить ответ
            </button>
            {feedback ? (
              <span className={feedback.ok ? "text-sm text-green-600" : "text-sm text-amber-700"}>
                {feedback.text}
              </span>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
