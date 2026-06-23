import { describe, expect, it } from "vitest"
import { pickConceptTransferHint, pickExamplesForConcept } from "@/widgets/task-workspace/ConceptPopover"
import {
  pickAlgorithmDebugHint,
  pickExpectedConceptsForLanguage,
  pickTransferTextForTask,
  shouldShowAlgorithmDebugHint,
  shouldShowTransferBanner,
  taskHasExpectedConceptsForLanguage,
  taskPedagogyMatchesLanguagePair,
} from "@/widgets/task-workspace/StudentExpectedConcepts"
import type { TaskDto } from "@/shared/types/task"

describe("pickExpectedConceptsForLanguage", () => {
  const task = {
    id: "1",
    curriculum: {
      language: "python",
      expected_concepts_by_language: {
        pascal: [{ id: "tc_console_io", name_ru: "Вывод в консоль" }],
        python: [{ id: "tc_loops", name_ru: "Циклы" }],
      },
      expected_concepts: [{ id: "tc_loops", name_ru: "Циклы" }],
    },
  } as unknown as TaskDto

  it("returns concepts for the requested learning language", () => {
    expect(pickExpectedConceptsForLanguage(task, "pascal").map((item) => item.id)).toEqual([
      "tc_console_io",
    ])
    expect(pickExpectedConceptsForLanguage(task, "python").map((item) => item.id)).toEqual([
      "tc_loops",
    ])
  })

  it("does not merge all languages when by-language map exists", () => {
    expect(pickExpectedConceptsForLanguage(task, "cpp")).toEqual([])
  })

  it("detects presence per language", () => {
    expect(taskHasExpectedConceptsForLanguage(task, "pascal")).toBe(true)
    expect(taskHasExpectedConceptsForLanguage(task, "cpp")).toBe(false)
  })

  it("prefers per-language ids over a shorter top-level card list", () => {
    const partialTask = {
      target_language: "java",
      expected_concepts: [
        { id: "tc_program_structure", name_ru: "Структура программы" },
        { id: "tc_console_io", name_ru: "Ввод и вывод (консоль)" },
      ],
      curriculum: {
        language: "java",
        target_language: "java",
        expected_concepts: {
          java: [
            "tc_program_structure",
            "tc_variables_types",
            "tc_assignment",
            "tc_console_io",
            "tc_loops",
            "tc_aggregate",
            "tc_arithmetic",
          ],
        },
        expected_concept_ids_by_language: {
          java: [
            "tc_program_structure",
            "tc_variables_types",
            "tc_assignment",
            "tc_console_io",
            "tc_loops",
            "tc_aggregate",
            "tc_arithmetic",
          ],
        },
        expected_concepts_by_language: {
          java: [
            { id: "tc_program_structure", name_ru: "Структура программы" },
            { id: "tc_variables_types", name_ru: "Переменные и типы" },
            { id: "tc_assignment", name_ru: "Присваивание" },
            { id: "tc_console_io", name_ru: "Ввод и вывод (консоль)" },
            { id: "tc_loops", name_ru: "Циклы" },
            { id: "tc_aggregate", name_ru: "Накопление и свёртка" },
            { id: "tc_arithmetic", name_ru: "Арифметика и операции" },
          ],
        },
      },
    } as unknown as TaskDto

    expect(pickExpectedConceptsForLanguage(partialTask, "java").map((item) => item.id)).toEqual([
      "tc_program_structure",
      "tc_variables_types",
      "tc_assignment",
      "tc_console_io",
      "tc_loops",
      "tc_aggregate",
      "tc_arithmetic",
    ])
  })

  it("resolves ids from dict when top-level cards are incomplete", () => {
    const partialTask = {
      target_language: "java",
      expected_concepts: [
        { id: "tc_program_structure", name_ru: "Структура программы" },
        { id: "tc_console_io", name_ru: "Ввод и вывод (консоль)" },
      ],
      curriculum: {
        language: "java",
        expected_concepts: {
          java: [
            "tc_program_structure",
            "tc_variables_types",
            "tc_assignment",
            "tc_console_io",
          ],
        },
      },
    } as unknown as TaskDto

    const ids = pickExpectedConceptsForLanguage(partialTask, "java").map((item) => item.id)
    expect(ids).toContain("tc_variables_types")
    expect(ids).toHaveLength(4)
  })
})

describe("pickTransferTextForTask", () => {
  it("task_001 TCC — no transfer banner", () => {
    const task = {
      transfer: {
        transfer_type: "TCC",
        proactive: { text: null, zone: null, concept_ids: [] },
        reference_warning_ru: "Не показывать для TCC",
      },
    } as unknown as TaskDto
    expect(pickTransferTextForTask(task)).toBeNull()
    expect(shouldShowTransferBanner(task)).toBe(false)
  })

  it("task_004 AlgorithmDebug — TCC with debug_id, no transfer banner", () => {
    const task = {
      transfer: {
        transfer_type: "TCC",
        debug_id: "filter_positive",
        reference_warning_ru: "Старый FCC banner",
      },
    } as unknown as TaskDto
    expect(pickTransferTextForTask(task)).toBeNull()
  })

  it("task_004 AlgorithmDebug — proactive algorithm hint from debug_meta", () => {
    const task = {
      transfer: {
        transfer_type: "TCC",
        debug_id: "filter_positive",
        algorithm_proactive: {
          debug_id: "filter_positive",
          text: "Считайте только положительные значения; ноль и отрицательные не подходят.",
        },
      },
    } as unknown as TaskDto
    expect(pickAlgorithmDebugHint(task)).toBe(
      "Считайте только положительные значения; ноль и отрицательные не подходят.",
    )
    expect(shouldShowAlgorithmDebugHint(task)).toBe(true)
    expect(shouldShowTransferBanner(task)).toBe(false)
  })

  it("task_003 AFCC — banner from proactive.text", () => {
    const task = {
      transfer: {
        transfer_type: "AFCC",
        pitfall_id: "input_line_model",
        proactive: {
          zone: "model",
          text: "В Python несколько чисел часто разбирают через input().split(); в Pascal их можно читать через readln(a, b, c) или разобрать строку вручную.",
          concept_ids: ["stdin_read"],
        },
        reference_warning_ru: "legacy fallback",
      },
    } as unknown as TaskDto
    expect(pickTransferTextForTask(task)).toBe(
      "В Python несколько чисел часто разбирают через input().split(); в Pascal их можно читать через readln(a, b, c) или разобрать строку вручную.",
    )
    expect(shouldShowTransferBanner(task)).toBe(true)
  })

  it("non-TCC falls back to reference_warning_ru when proactive.text is empty", () => {
    const task = {
      transfer: {
        transfer_type: "FCC",
        proactive: { text: null },
        reference_warning_ru: "Индексация с единицы.",
      },
    } as unknown as TaskDto
    expect(pickTransferTextForTask(task)).toBe("Индексация с единицы.")
  })

  it("ignores pedagogy and hint when transfer_type is TCC", () => {
    const task = {
      curriculum: {
        transfer: {
          transfer_type: "TCC",
          pedagogy_note_ru: "Сравните округление 2.5.",
          hint_ru: "a[1]",
        },
      },
    } as unknown as TaskDto
    expect(pickTransferTextForTask(task)).toBeNull()
  })

  it("returns null when transfer meta is absent", () => {
    expect(pickTransferTextForTask({} as TaskDto)).toBeNull()
  })

  it("prefers root transfer over stale curriculum.transfer", () => {
    const task = {
      transfer: {
        transfer_type: "FCC",
        proactive: {
          text: "В Python: total // n\nВ Java: total / n",
        },
      },
      curriculum: {
        transfer: {
          transfer_type: "TCC",
          proactive: { text: "Устаревшее предупреждение Pascal" },
        },
      },
    } as unknown as TaskDto
    expect(pickTransferTextForTask(task)).toContain("Java")
    expect(pickTransferTextForTask(task)).not.toContain("Pascal")
  })
})

describe("taskPedagogyMatchesLanguagePair", () => {
  it("matches requested pair from backend payload", () => {
    const task = {
      requested_source_language: "python",
      requested_target_language: "java",
    } as unknown as TaskDto
    expect(taskPedagogyMatchesLanguagePair(task, "python", "java")).toBe(true)
    expect(taskPedagogyMatchesLanguagePair(task, "cpp", "java")).toBe(false)
  })
})

describe("pickConceptTransferHint", () => {
  it("chip outside in_proactive_scope — no transfer hint", () => {
    expect(
      pickConceptTransferHint({
        id: "program_entry",
        transfer_hint_ru: "Подсказка не должна показываться",
        in_proactive_scope: false,
      }),
    ).toBeNull()
  })

  it("chip inside in_proactive_scope — transfer hint visible", () => {
    expect(
      pickConceptTransferHint({
        id: "stdin_read",
        transfer_hint_ru: "readln + Val в Pascal",
        in_proactive_scope: true,
      }),
    ).toBe("readln + Val в Pascal")
  })

  it("missing in_proactive_scope treated as out of scope", () => {
    expect(
      pickConceptTransferHint({
        id: "stdin_read",
        transfer_hint_ru: "hint",
      }),
    ).toBeNull()
  })
})

describe("pickExamplesForConcept", () => {
  it("shows division examples for both languages when MPLT pair is active", () => {
    const rows = pickExamplesForConcept(
      {
        id: "tc_arithmetic",
        in_proactive_scope: true,
        transfer_hint_ru: "в Python целое частное — //; в Pascal — div",
        examples_by_language: {
          python: [{ title: "Целочисленное // и %", code: "q = a // b" }],
          pascal: [{ title: "div и mod", code: "q := a div b;" }],
        },
      },
      "pascal",
      "python",
    )
    expect(rows).toHaveLength(2)
    expect(rows[0]?.code).toContain("//")
    expect(rows[1]?.code).toContain("div")
  })
})
