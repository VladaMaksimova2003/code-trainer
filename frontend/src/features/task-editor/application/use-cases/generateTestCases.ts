import { generateTestCasesFromPatterns } from "@/features/task-editor/domain/generateTestCases"
import type { CodeSnippet, IoSchema, Pattern, TestCase } from "@/features/task-editor/domain/entities"

export function generateTestCases(
  code: CodeSnippet,
  patterns: Pattern[],
  ioSchema: IoSchema
): TestCase[] {
  return generateTestCasesFromPatterns(code, patterns, ioSchema)
}
