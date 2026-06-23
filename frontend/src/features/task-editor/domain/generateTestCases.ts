import { createEmptyIoValue, createMulti, createScalar } from "@/features/task-editor/domain/ioValue"
import type { CodeSnippet, IoSchema, Pattern, TestCase } from "@/features/task-editor/domain/entities"
import { PatternType } from "@/features/task-editor/domain/enums"

export function generateTestCasesFromPatterns(
  code: CodeSnippet,
  patterns: Pattern[],
  ioSchema: IoSchema
): TestCase[] {
  const approved = patterns.filter((p) => p.approved !== false)
  const base: TestCase[] = [
    {
      id: "tc-smoke",
      name: "Smoke",
      input: createEmptyIoValue(ioSchema.inputFormat),
      expectedOutput: createEmptyIoValue(ioSchema.outputFormat),
      description: "Пустой ввод",
    },
  ]

  if (approved.some((p) => p.type === PatternType.LOOP)) {
    base.push({
      id: "tc-loop",
      name: "Loop",
      input: createScalar("3"),
      expectedOutput: createScalar(""),
      description: "Количество итераций",
    })
  }
  if (approved.some((p) => p.type === PatternType.BRANCHING)) {
    base.push({
      id: "tc-branch",
      name: "Branch",
      input: createMulti(["0", "1"]),
      expectedOutput: createScalar(""),
      description: "Несколько веток ввода",
    })
  }
  if (code.code.trim() && base.length === 1) {
    base.push({
      id: "tc-matrix-sample",
      name: "Matrix sample",
      input: createScalar(""),
      expectedOutput: createScalar(""),
      description: "Замените на матрицу при необходимости",
    })
  }
  return base
}
