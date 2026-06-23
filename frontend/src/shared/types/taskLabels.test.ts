import { describe, expect, it } from "vitest"
import {
  CURRICULUM_ACTION_LABELS,
  TASK_TYPE_LABELS,
  formatAssignmentTypeLabel,
  formatTaskActivityLabel,
  formatTaskModuleLabel,
  formatTaskTypeLabel,
  resolveTaskActivityAction,
  toAssignmentTypeId,
} from "@/shared/types/taskLabels"

/** Keys from pre-merge `shared/utils/taskTypeLabels.js`. */
const LEGACY_JS_MAP: Record<string, string> = {
  task_build_from_blocks: "Собрать",
  block_reorder: "Собрать",
  block_reorder_task: "Собрать",
  code_assembly: "Собрать",
  task_translate_snippet: "Написать",
  task_translate_full_program: "Написать",
  translation: "Написать",
  translation_task: "Написать",
  task_flowchart_to_code: "Блок-схема в код",
  blocks: "Блок-схема в код",
  diagram: "Блок-схема в код",
  diagram_task: "Блок-схема в код",
  algorithm: "Алгоритм",
  algorithm_task: "Алгоритм",
  base: "Базовое задание",
  base_task: "Базовое задание",
}

/** Keys from pre-merge `features/task-editor/domain/taskTypeLabel.ts`. */
const LEGACY_TS_MAP: Record<string, string> = {
  task_build_from_blocks: "Собрать",
  task_flowchart_to_code: "Блок-схема в код",
  task_translate_snippet: "Написать",
  task_translate_full_program: "Написать",
  block_reorder: "Собрать",
  block_reorder_task: "Собрать",
  code_assembly: "Собрать",
  blocks: "Блок-схема в код",
  diagram: "Блок-схема в код",
  diagram_task: "Блок-схема в код",
  translation: "Написать",
  translation_task: "Написать",
  algorithm: "Алгоритм",
  algorithm_task: "Алгоритм",
  base: "Базовое задание",
  base_task: "Базовое задание",
}

describe("TASK_TYPE_LABELS parity", () => {
  it("matches every legacy JS map entry", () => {
    for (const [key, label] of Object.entries(LEGACY_JS_MAP)) {
      expect(TASK_TYPE_LABELS[key]).toBe(label)
      expect(formatTaskTypeLabel(key)).toBe(label)
    }
  })

  it("matches every legacy TS map entry via formatAssignmentTypeLabel", () => {
    for (const [key, label] of Object.entries(LEGACY_TS_MAP)) {
      expect(TASK_TYPE_LABELS[key]).toBe(label)
      expect(formatAssignmentTypeLabel(key)).toBe(label)
    }
  })
})

describe("formatTaskActivityLabel", () => {
  it("prefers curriculum action over assignment type", () => {
    expect(
      formatTaskActivityLabel({
        type: "task_translate_full_program",
        curriculum: { action: "debug" },
      }),
    ).toBe("Исправить")
    expect(
      formatTaskActivityLabel({
        type: "task_build_from_blocks",
        curriculum: { action: "assemble" },
      }),
    ).toBe("Собрать")
  })

  it("maps block assembly types to Собрать", () => {
    expect(formatTaskActivityLabel({ type: "task_build_from_blocks" })).toBe("Собрать")
  })

  it("maps translation types to Написать", () => {
    expect(formatTaskActivityLabel({ type: "task_translate_full_program" })).toBe("Написать")
  })
})

describe("resolveTaskActivityAction", () => {
  it("returns curriculum action when present", () => {
    expect(resolveTaskActivityAction({ curriculum: { action: "debug" } })).toBe("debug")
  })
})

describe("CURRICULUM_ACTION_LABELS", () => {
  it("includes core student-facing verbs", () => {
    expect(CURRICULUM_ACTION_LABELS.assemble).toBe("Собрать")
    expect(CURRICULUM_ACTION_LABELS.implement).toBe("Написать")
    expect(CURRICULUM_ACTION_LABELS.debug).toBe("Исправить")
  })
})

describe("formatTaskTypeLabel", () => {
  it("returns dash for empty type", () => {
    expect(formatTaskTypeLabel("")).toBe("-")
    expect(formatTaskTypeLabel(null)).toBe("-")
    expect(formatTaskTypeLabel(undefined)).toBe("-")
  })

  it("labels block assembly types", () => {
    expect(formatTaskTypeLabel("task_build_from_blocks")).toBe("Собрать")
    expect(formatTaskTypeLabel("block_reorder")).toBe("Собрать")
    expect(formatTaskTypeLabel("code_assembly")).toBe("Собрать")
  })

  it("labels flowchart types", () => {
    expect(formatTaskTypeLabel("task_flowchart_to_code")).toBe("Блок-схема в код")
    expect(formatTaskTypeLabel("diagram")).toBe("Блок-схема в код")
    expect(formatTaskTypeLabel("blocks")).toBe("Блок-схема в код")
  })

  it("capitalizes unknown types (legacy JS fallback)", () => {
    expect(formatTaskTypeLabel("foo_bar")).toBe("Foo Bar")
    expect(formatTaskTypeLabel("custom_task_type")).toBe("Custom Task Type")
  })
})

describe("formatAssignmentTypeLabel", () => {
  it("labels block assembly types", () => {
    expect(formatAssignmentTypeLabel("task_build_from_blocks")).toBe("Собрать")
    expect(formatAssignmentTypeLabel("block_reorder")).toBe("Собрать")
    expect(formatAssignmentTypeLabel("code_assembly")).toBe("Собрать")
  })

  it("labels flowchart types", () => {
    expect(formatAssignmentTypeLabel("task_flowchart_to_code")).toBe("Блок-схема в код")
    expect(formatAssignmentTypeLabel("diagram")).toBe("Блок-схема в код")
    expect(formatAssignmentTypeLabel("blocks")).toBe("Блок-схема в код")
  })

  it("uses spaced slug fallback for unknown types (legacy TS fallback)", () => {
    expect(formatAssignmentTypeLabel("foo_bar")).toBe("foo bar")
    expect(formatAssignmentTypeLabel("custom_task_type")).toBe("custom task type")
  })
})

describe("toAssignmentTypeId", () => {
  it("normalizes legacy public types", () => {
    expect(toAssignmentTypeId("block_reorder")).toBe("task_build_from_blocks")
    expect(toAssignmentTypeId("code_assembly")).toBe("task_build_from_blocks")
    expect(toAssignmentTypeId("blocks")).toBe("task_flowchart_to_code")
    expect(toAssignmentTypeId("diagram")).toBe("task_flowchart_to_code")
    expect(toAssignmentTypeId("translation")).toBe("task_translate_full_program")
    expect(toAssignmentTypeId("algorithm")).toBe("algorithm")
  })

  it("passes through task_ prefixed ids", () => {
    expect(toAssignmentTypeId("task_flowchart_to_code")).toBe("task_flowchart_to_code")
    expect(toAssignmentTypeId("task_build_from_blocks")).toBe("task_build_from_blocks")
  })

  it("passes through unknown ids", () => {
    expect(toAssignmentTypeId("snippet")).toBe("snippet")
  })
})

describe("formatTaskModuleLabel", () => {
  it("strips .py and _task suffix", () => {
    expect(formatTaskModuleLabel("algorithm_task.py")).toBe("algorithm")
    expect(formatTaskModuleLabel("block_reorder_task.py")).toBe("block reorder")
  })

  it("handles module names without suffix", () => {
    expect(formatTaskModuleLabel("flowchart.py")).toBe("flowchart")
  })
})
