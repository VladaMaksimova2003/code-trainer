import { useEffect, useState } from "react"
import { createEmptyIoValue, formatIoPreview } from "@/features/task-editor/domain/ioValue"
import type { IoSchema, TestCase } from "@/features/task-editor/domain/entities"
import { IoValueEditor } from "@/features/task-editor/presentation/components/IoValueEditor"
import { IoSchemaFields } from "@/features/task-editor/presentation/components/IoSchemaFields"
import {
  editorFieldGroupClass,
  editorSectionDividerClass,
  primarySubmitButton,
  secondaryActionButton,
  testDataFrameClass,
  testDataFrameTitleClass,
} from "@/features/task-editor/presentation/components/plaqueStyles"

type Props = {
  testCases: TestCase[]
  ioSchema: IoSchema
  onIoSchemaChange: (schema: IoSchema) => void
  onChange: (cases: TestCase[]) => void
}

function withSequentialNames(cases: TestCase[]): TestCase[] {
  return cases.map((tc, i) => ({
    ...tc,
    name: `Тест ${i + 1}`,
  }))
}

export function TestCasesSection({
  testCases,
  ioSchema,
  onIoSchemaChange,
  onChange,
}: Props) {
  const [activeId, setActiveId] = useState<string | null>(
    testCases[0]?.id ?? null,
  )

  useEffect(() => {
    if (testCases.length === 0) {
      setActiveId(null)
      return
    }
    if (!activeId || !testCases.some((tc) => tc.id === activeId)) {
      setActiveId(testCases[0].id)
    }
  }, [activeId, testCases])

  const applyIoSchema = (next: IoSchema) => {
    const inCh = next.inputFormat !== ioSchema.inputFormat
    const outCh = next.outputFormat !== ioSchema.outputFormat
    onIoSchemaChange(next)
    if (testCases.length === 0 || (!inCh && !outCh)) return
    onChange(
      testCases.map((tc) => ({
        ...tc,
        ...(inCh ? { input: createEmptyIoValue(next.inputFormat) } : {}),
        ...(outCh
          ? { expectedOutput: createEmptyIoValue(next.outputFormat) }
          : {}),
      })),
    )
  }

  const addCase = () => {
    const id = `tc-${Date.now()}`
    const next: TestCase = {
      id,
      name: "",
      input: createEmptyIoValue(ioSchema.inputFormat),
      expectedOutput: createEmptyIoValue(ioSchema.outputFormat),
    }
    const merged = withSequentialNames([...testCases, next])
    onChange(merged)
    setActiveId(id)
  }

  const updateCase = (tcId: string, patch: Partial<TestCase>) => {
    onChange(
      testCases.map((tc) => (tc.id === tcId ? { ...tc, ...patch } : tc)),
    )
  }

  const removeCase = (id: string) => {
    const next = testCases.filter((tc) => tc.id !== id)
    onChange(withSequentialNames(next))
    if (activeId === id) setActiveId(next[0]?.id ?? null)
  }

  return (
    <div className={`${editorSectionDividerClass} flex flex-col gap-4`}>
      <div className={`${testDataFrameClass} ${editorFieldGroupClass}`}>
        <h3 className={testDataFrameTitleClass}>Тестовые данные</h3>
        <IoSchemaFields schema={ioSchema} onChange={applyIoSchema} />

        {testCases.length === 0 ? (
          <div className="flex flex-col gap-3">
            <p className="text-sm text-ink-faint">Тестовые случаи не заданы</p>
            <button type="button" onClick={addCase} className={primarySubmitButton()}>
              Добавить тестовый случай
            </button>
          </div>
        ) : (
          <>
            <ul className="flex flex-col">
              {testCases.map((tc, i) => {
                const isActive = tc.id === activeId
                return (
                  <li key={tc.id} className="border-b border-border last:border-b-0">
                    <div
                      role="button"
                      tabIndex={0}
                      onClick={() => setActiveId(tc.id)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault()
                          setActiveId(tc.id)
                        }
                      }}
                      className="py-5"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-ink">
                            {tc.name || `Тест ${i + 1}`}
                          </p>
                          <p className="mt-1 truncate text-xs text-ink-faint">
                            Вход: {formatIoPreview(tc.input, 36)} → Ожидаемый:{" "}
                            {formatIoPreview(tc.expectedOutput, 28)}
                          </p>
                        </div>
                        <button
                          type="button"
                          className={secondaryActionButton()}
                          onClick={(e) => {
                            e.stopPropagation()
                            removeCase(tc.id)
                          }}
                        >
                          Удалить
                        </button>
                      </div>

                      {isActive && (
                        <div className="mt-4 border-t border-border pt-4">
                          <IoValueEditor
                            key={`${tc.id}-in-${ioSchema.inputFormat}`}
                            label="Вход"
                            value={tc.input}
                            expectedKind={ioSchema.inputFormat}
                            onChange={(input) => updateCase(tc.id, { input })}
                            variant="dark"
                          />
                          <IoValueEditor
                            key={`${tc.id}-out-${ioSchema.outputFormat}`}
                            label="Ожидаемый результат"
                            value={tc.expectedOutput}
                            expectedKind={ioSchema.outputFormat}
                            onChange={(expectedOutput) =>
                              updateCase(tc.id, { expectedOutput })
                            }
                            variant="dark"
                          />
                        </div>
                      )}
                    </div>
                  </li>
                )
              })}
            </ul>

            <button type="button" onClick={addCase} className={primarySubmitButton()}>
              Добавить тестовый случай
            </button>
          </>
        )}
      </div>
    </div>
  )
}
