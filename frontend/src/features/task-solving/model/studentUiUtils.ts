import { getLanguageLabel } from "@/shared/config/languages"
import { formatAssemblyTemplate } from "@/domain/blockAssembly/formatTemplate"
import { decodeTemplateText } from "@/domain/blockAssembly/utils"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import type { LanguageVariant, TaskDto } from "@/shared/types/task"
import type { TaskDraftRecord } from "@/features/task-solving/model/taskDraftHelpers"

export const CONSTRUCTION_LABELS: Record<string, string> = {
  function_definition: "Функция",
  for_loop: "Цикл",
  while_loop: "Цикл",
  if_statement: "Условие",
  return_statement: "Return",
  binary_expression: "Арифметика",
  nested_loops: "Вложенные циклы",
  io: "Ввод / вывод",
  arith: "Арифметика",
  assign: "Присваивание",
  cond: "Условие",
  loop: "Цикл",
}

export interface ConstructionHintsMap {
  [pattern: string]: { title?: string } | undefined
}

export interface BlockLanguageVariant {
  blocks: NonNullable<TaskDto["blocks"]>
  template: string
  correct_order: number[]
}

export function getConstructionLabel(
  pattern: string,
  hints: ConstructionHintsMap = {},
): string {
  return CONSTRUCTION_LABELS[pattern] || hints?.[pattern]?.title || pattern
}

export function langFileName(lang: string | undefined, title = "solution"): string {
  const id = String(lang || "").toLowerCase()
  const ext =
    id.includes("python") || id === "py"
      ? "py"
      : id.includes("javascript") || id === "js"
        ? "js"
        : id.includes("cpp") || id === "c++"
          ? "cpp"
          : id.includes("java")
            ? "java"
            : id.includes("pascal")
              ? "pas"
              : id.includes("csharp")
                ? "csx"
                : "txt"
  const slug =
    String(title || "solution")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_|_$/g, "")
      .slice(0, 24) || "solution"
  return `${slug}.${ext}`
}

export function langDisplay(lang: string | undefined): string {
  return getLanguageLabel(lang) || String(lang || "").toUpperCase()
}

function hasNonEmptyExample(value: unknown): boolean {
  if (Array.isArray(value)) return false
  return Boolean(String(decodeTemplateText(value as string) || "").trim())
}

const NON_LANGUAGE_EXAMPLE_KEYS = new Set(["patterns", "constructions"])

const KNOWN_SOURCE_LANGUAGES = new Set(["python", "pascal", "cpp", "java", "csharp", "javascript", "js"])

const CURRICULUM_KNOWN_LANGUAGES = new Set(["python", "pascal", "cpp", "java", "csharp"])

export const CURRICULUM_LANG_ORDER = ["python", "pascal", "cpp", "csharp", "java"] as const

function knownLanguagesForTask(task: TaskDto | null | undefined): Set<string> {
  if (isCurriculumMirrorTask(task)) {
    return CURRICULUM_KNOWN_LANGUAGES
  }
  return KNOWN_SOURCE_LANGUAGES
}

export function getCurriculumLearningLanguage(task: TaskDto | null | undefined): string | null {
  if (isPythonCurriculumTask(task)) return "python"
  if (isPascalCurriculumTask(task)) return "pascal"
  if (isCppCurriculumTask(task)) return "cpp"
  if (isCsharpCurriculumTask(task)) return "csharp"
  if (isJavaCurriculumTask(task)) return "java"
  return null
}

export function getMirrorSiblingLanguage(task: TaskDto | null | undefined): string | null {
  const mirrors = getMirrorLanguages(task)
  const learning = getCurriculumLearningLanguage(task)
  if (!learning) return null
  return mirrors.find((lang) => lang !== learning) || null
}

export function getMirrorLanguages(task: TaskDto | null | undefined): string[] {
  const fromPayload = (task as { available_language_tracks?: unknown })?.available_language_tracks
  if (Array.isArray(fromPayload) && fromPayload.length > 0) {
    return fromPayload.map((lang) => String(lang).toLowerCase()).filter(Boolean)
  }
  const curriculum = task?.curriculum as { available_language_tracks?: unknown } | undefined
  const fromCurriculum = curriculum?.available_language_tracks
  if (Array.isArray(fromCurriculum) && fromCurriculum.length > 0) {
    return fromCurriculum.map((lang) => String(lang).toLowerCase()).filter(Boolean)
  }
  return []
}

/** C# curriculum: target language is always C#; other tracks only in «Я знаю». */
export function isCsharpCurriculumTask(task: TaskDto | null | undefined): boolean {
  const curriculumLang = String(task?.curriculum?.language || "").toLowerCase()
  if (curriculumLang === "csharp") return true
  const target = String(task?.target_language || "").toLowerCase()
  if (target === "csharp") return true
  const showcase = (task?.code_examples as Record<string, unknown> | undefined)?.curriculum_showcase as
    | { target_language?: string }
    | undefined
  return String(showcase?.target_language || "").toLowerCase() === "csharp"
}

/** Java curriculum: target language is always Java; other tracks only in «Я знаю». */
export function isJavaCurriculumTask(task: TaskDto | null | undefined): boolean {
  const curriculumLang = String(task?.curriculum?.language || "").toLowerCase()
  if (curriculumLang === "java") return true
  const target = String(task?.target_language || "").toLowerCase()
  if (target === "java") return true
  const showcase = (task?.code_examples as Record<string, unknown> | undefined)?.curriculum_showcase as
    | { target_language?: string }
    | undefined
  return String(showcase?.target_language || "").toLowerCase() === "java"
}

export function isCurriculumMirrorTask(task: TaskDto | null | undefined): boolean {
  return (
    isPythonCurriculumTask(task) ||
    isPascalCurriculumTask(task) ||
    isCppCurriculumTask(task) ||
    isCsharpCurriculumTask(task) ||
    isJavaCurriculumTask(task)
  )
}

export function getCurriculumSlotId(task: TaskDto | null | undefined): string {
  const curriculum = task?.curriculum as { slot_id?: string } | undefined
  if (curriculum?.slot_id) return String(curriculum.slot_id)
  const showcase = (task?.code_examples as Record<string, unknown> | undefined)?.curriculum_showcase as
    | { slot_id?: string }
    | undefined
  return String(showcase?.slot_id || "")
}

function knownLanguageVariantsRecord(task: TaskDto | null | undefined): Record<string, { source_code?: string }> {
  const fromPayload = task?.known_language_variants
  if (fromPayload && typeof fromPayload === "object" && !Array.isArray(fromPayload)) {
    return fromPayload as Record<string, { source_code?: string }>
  }
  const curriculum = task?.curriculum as Record<string, unknown> | undefined
  const fromCurriculum = curriculum?.known_language_variants
  if (fromCurriculum && typeof fromCurriculum === "object" && !Array.isArray(fromCurriculum)) {
    return fromCurriculum as Record<string, { source_code?: string }>
  }
  return {}
}

function referenceCodeFromVariants(
  variants: Record<string, { source_code?: string }>,
  language: string,
): string | null {
  const lang = String(language || "").toLowerCase()
  if (!lang) return null
  const direct = variants[lang]?.source_code
  if (direct != null && hasNonEmptyExample(direct)) {
    return decodeDisplayCode(direct)
  }
  const matchedKey = Object.keys(variants).find((key) => key.toLowerCase() === lang)
  const matched = matchedKey ? variants[matchedKey]?.source_code : null
  if (matched != null && hasNonEmptyExample(matched)) {
    return decodeDisplayCode(matched)
  }
  return null
}

function languageVariantsRecord(task: TaskDto): Record<string, LanguageVariant & { correct_order?: number[] }> {
  const raw = task.language_variants
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    return raw as Record<string, LanguageVariant & { correct_order?: number[] }>
  }
  return {}
}

/** Pascal curriculum: target language is always Pascal; «Я знаю» only switches source example. */
export function isPascalCurriculumTask(task: TaskDto | null | undefined): boolean {
  const curriculumLang = String(task?.curriculum?.language || "").toLowerCase()
  if (curriculumLang === "pascal") return true
  const target = String(task?.target_language || "").toLowerCase()
  return target === "pascal"
}

/** Python curriculum: target language is always Python; Pascal/C++ only in «Я знаю». */
export function isPythonCurriculumTask(task: TaskDto | null | undefined): boolean {
  const curriculumLang = String(task?.curriculum?.language || "").toLowerCase()
  if (curriculumLang === "python") return true
  const target = String(task?.target_language || "").toLowerCase()
  if (target === "python") return true
  const showcase = (task?.code_examples as Record<string, unknown> | undefined)?.curriculum_showcase as
    | { target_language?: string }
    | undefined
  return String(showcase?.target_language || "").toLowerCase() === "python"
}

/** C++ curriculum: target language is always C++; other tracks only in «Я знаю». */
export function isCppCurriculumTask(task: TaskDto | null | undefined): boolean {
  const curriculumLang = String(task?.curriculum?.language || "").toLowerCase()
  if (curriculumLang === "cpp") return true
  const target = String(task?.target_language || "").toLowerCase()
  if (target === "cpp") return true
  const showcase = (task?.code_examples as Record<string, unknown> | undefined)?.curriculum_showcase as
    | { target_language?: string }
    | undefined
  return String(showcase?.target_language || "").toLowerCase() === "cpp"
}

/** Языки с непустым эталоном в code_examples — только они в селекторе «Я знаю». */
export function getKnownLanguages(task: TaskDto | null | undefined): string[] {
  const allowed = knownLanguagesForTask(task)
  const langs = new Set<string>()
  if (task?.code_examples) {
    for (const [key, value] of Object.entries(task.code_examples)) {
      const lang = String(key).toLowerCase()
      if (
        !NON_LANGUAGE_EXAMPLE_KEYS.has(lang) &&
        allowed.has(lang) &&
        hasNonEmptyExample(value)
      ) {
        langs.add(lang)
      }
    }
  }
  for (const lang of Object.keys(knownLanguageVariantsRecord(task))) {
    const normalized = String(lang).toLowerCase()
    if (allowed.has(normalized) && referenceCodeFromVariants(knownLanguageVariantsRecord(task), normalized)) {
      langs.add(normalized)
    }
  }
  const sourceLanguage = String(task?.source_language || "").toLowerCase()
  if (
    sourceLanguage &&
    allowed.has(sourceLanguage) &&
    String(task?.source_code || "").trim()
  ) {
    langs.add(sourceLanguage)
  }
  return [...langs]
}

/** Языки для сборки / решения («Учу»): язык сборника + зеркало, если есть. */
function isAlgoV4SlotId(slotId: string): boolean {
  return /^(py_|pas_|cpp_|cs_|java_)\d+$/i.test(String(slotId || "").trim())
}

export function getLearningLanguages(task: TaskDto | null | undefined): string[] {
  if (!task) return []
  if (isCurriculumMirrorTask(task)) {
    const slotId = getCurriculumSlotId(task)
    if (isAlgoV4SlotId(slotId)) {
      return [...CURRICULUM_LANG_ORDER]
    }
    const mirrors = getMirrorLanguages(task)
    if (mirrors.length >= 2) {
      return CURRICULUM_LANG_ORDER.filter((lang) => mirrors.includes(lang))
    }
    const learning = getCurriculumLearningLanguage(task)
    if (learning) {
      const sibling = getMirrorSiblingLanguage(task)
      return sibling ? [learning, sibling] : [learning]
    }
  }
  const learning = getCurriculumLearningLanguage(task)
  if (learning) {
    const sibling = getMirrorSiblingLanguage(task)
    return sibling ? [learning, sibling] : [learning]
  }
  const langs = new Set<string>()
  const primary = String(task.language || "").toLowerCase()
  if (primary) langs.add(primary)
  for (const key of Object.keys(languageVariantsRecord(task))) {
    if (key) langs.add(String(key).toLowerCase())
  }
  if (isTranslationTask(task)) {
    for (const key of getKnownLanguages(task)) {
      langs.add(key)
    }
  }
  const to = String(task.language_to || "").toLowerCase()
  if (to) langs.add(to)
  return [...langs]
}

export function hasReferenceCode(task: TaskDto | null | undefined): boolean {
  if (getKnownLanguages(task).length > 0) return true
  return Boolean(String(task?.reference_code || "").trim())
}

export function decodeDisplayCode(text = ""): string {
  return decodeTemplateText(text)
}

/** Эталон для выбранного языка «Я знаю»; без подстановки другого языка. */
export function getReferenceCode(task: TaskDto | null | undefined, language: string): string | null {
  const lang = String(language || "").toLowerCase()
  if (!lang || !task) return null
  const examples = task.code_examples || {}
  const direct = examples[lang]
  if (direct != null && hasNonEmptyExample(direct)) {
    return decodeDisplayCode(direct)
  }
  const matchedKey = Object.keys(examples).find((key) => key.toLowerCase() === lang)
  if (matchedKey != null && hasNonEmptyExample(examples[matchedKey])) {
    return decodeDisplayCode(examples[matchedKey])
  }
  const fromVariants = referenceCodeFromVariants(knownLanguageVariantsRecord(task), lang)
  if (fromVariants) return fromVariants
  const sourceLanguage = String(task.source_language || "").toLowerCase()
  if (lang === sourceLanguage && String(task.source_code || "").trim()) {
    return decodeDisplayCode(task.source_code)
  }
  return null
}

/** Pick «Я знаю» language that has a real reference snippet. */
export function resolveKnownLanguageWithReference(
  task: TaskDto | null | undefined,
  preferred = "",
): string {
  const known = getKnownLanguages(task)
  const pref = String(preferred || "").toLowerCase()
  if (pref && known.includes(pref) && getReferenceCode(task, pref)) return pref
  for (const lang of known) {
    if (getReferenceCode(task, lang)) return lang
  }
  return known[0] || pref || ""
}

export function getTaskPrimaryAction(task: TaskDto | null | undefined): string {
  return String(task?.curriculum?.action || task?.primary_action || "").toLowerCase()
}

/** Teacher-authored «Учу» code for debug tasks — only from DB (`buggy_{lang}`), never catalog starters. */
export function getInitialStudentCode(
  task: TaskDto | null | undefined,
  learningLanguage?: string,
): string {
  if (!task || isFlowchartTask(task)) return ""
  if (getTaskPrimaryAction(task) !== "debug") return ""

  const lang = String(
    learningLanguage ||
      getCurriculumLearningLanguage(task) ||
      task.language ||
      "",
  ).toLowerCase()
  const examples = (task.code_examples || {}) as Record<string, unknown>
  const buggyKey = `buggy_${lang}`

  if (hasNonEmptyExample(examples[buggyKey])) {
    return decodeDisplayCode(examples[buggyKey] as string)
  }

  const curriculum = (task.curriculum || {}) as Record<string, unknown>
  if (hasNonEmptyExample(curriculum[buggyKey])) {
    return decodeDisplayCode(curriculum[buggyKey] as string)
  }

  const codeExamples = task.code_examples as Record<string, unknown> | undefined
  const teacherOverride = Boolean(
    task.teacher_assembly_override || codeExamples?.teacher_assembly_override,
  )
  if (teacherOverride) {
    return ""
  }

  const legacyStarterKey = `starter_${lang}`
  const fromCurriculum = String(curriculum[legacyStarterKey] || "")
  if (fromCurriculum.trim()) return decodeDisplayCode(fromCurriculum)

  const showcase = (codeExamples?.curriculum_showcase || {}) as Record<string, unknown>
  const legacyShowcase = String(showcase[legacyStarterKey] || "")
  if (legacyShowcase.trim()) return decodeDisplayCode(legacyShowcase)

  return ""
}

function readStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.map((item) => String(item || "").trim()).filter(Boolean)
}

/** Teacher-authored step hints (debug import) from top-level payload or code_examples fallback. */
export function getTaskHints(task: TaskDto | null | undefined): string[] {
  if (!task) return []
  const top = readStringList((task as Record<string, unknown>).hints)
  if (top.length > 0) return top

  const curriculum = (task.curriculum || {}) as Record<string, unknown>
  const fromCurriculum = readStringList(curriculum.hints)
  if (fromCurriculum.length > 0) return fromCurriculum

  const examples = (task.code_examples || {}) as Record<string, unknown>
  return readStringList(examples.hints)
}

/** Post-solve explanation shown after all tests pass. */
export function getPostSolveExplanation(task: TaskDto | null | undefined): string {
  if (!task) return ""
  const top = String((task as Record<string, unknown>).post_solve_explanation || "").trim()
  if (top) return top

  const curriculum = (task.curriculum || {}) as Record<string, unknown>
  const fromCurriculum = String(curriculum.post_solve_explanation || "").trim()
  if (fromCurriculum) return fromCurriculum

  const examples = (task.code_examples || {}) as Record<string, unknown>
  return String(examples.post_solve_explanation || "").trim()
}

export function shouldShowPascalLearningBar(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask = false,
): boolean {
  if (!isPascalCurriculumTask(task)) return false
  if (isBlockAssemblyTask || isFlowchartTask(task) || isAnalyzeTask(task)) return false
  return !hasParallelExamples(task, isBlockAssemblyTask)
}

export function shouldShowPythonLearningBar(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask = false,
): boolean {
  if (!isPythonCurriculumTask(task)) return false
  if (isBlockAssemblyTask || isFlowchartTask(task) || isAnalyzeTask(task)) return false
  return !hasParallelExamples(task, isBlockAssemblyTask)
}

export function shouldShowCppLearningBar(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask = false,
): boolean {
  if (!isCppCurriculumTask(task)) return false
  if (isBlockAssemblyTask || isFlowchartTask(task) || isAnalyzeTask(task)) return false
  return !hasParallelExamples(task, isBlockAssemblyTask)
}

export function getBlockVariantForLanguage(
  task: TaskDto | null | undefined,
  language: string | undefined,
): BlockLanguageVariant | null {
  if (!task) return null
  const lang = String(language || task.language || "").toLowerCase()
  const primary = String(task.language || "").toLowerCase()
  const variants = languageVariantsRecord(task)
  const variant = variants[lang] || variants[language ?? ""]

  const normalizeBlocks = (blocks: string[] | undefined): string[] => {
    const source = blocks ?? task.blocks ?? []
    const expanded: string[] = []
    for (const block of source) {
      const text = decodeDisplayCode(String(block))
      if (
        lang === "python" &&
        text &&
        !text.includes("\n") &&
        /input\(\)[a-z_]|\)[a-z_][a-z0-9_]*\s*=|\]\s*[a-z_]/i.test(text.replace(/\s+/g, ""))
      ) {
        expanded.push(
          ...formatAssemblyTemplate(text, lang)
            .split("\n")
            .map((line) => line.trim())
            .filter(Boolean),
        )
        continue
      }
      expanded.push(text)
    }
    return expanded
  }

  if (variant) {
    return {
      blocks: normalizeBlocks(variant.blocks),
      template: decodeDisplayCode(String(variant.template ?? task.template ?? "")),
      correct_order: (variant.correct_order as number[] | undefined) ?? (task.correct_order as number[] | undefined) ?? [],
    }
  }
  if (lang === primary) {
    return {
      blocks: normalizeBlocks(task.blocks),
      template: decodeDisplayCode(String(task.template ?? "")),
      correct_order: (task.correct_order as number[] | undefined) ?? [],
    }
  }
  return null
}

/** @deprecated Use getKnownLanguages / getLearningLanguages. */
export function getParallelLanguages(task: TaskDto | null | undefined): string[] {
  return [...new Set([...getKnownLanguages(task), ...getLearningLanguages(task)])]
}

export function resolveKnownLanguageBarOptions(task: TaskDto | null | undefined): string[] {
  return getKnownLanguages(task)
}

export function resolveLearningLanguageBarOptions(
  task: TaskDto | null | undefined,
  serverLanguageIds: string[] = [],
): string[] {
  if (isCurriculumMirrorTask(task)) {
    return getLearningLanguages(task)
  }
  const fromTask = getLearningLanguages(task)
  const studentRefs = getStudentReferenceLanguages(task)
  const server = Array.isArray(serverLanguageIds)
    ? serverLanguageIds.map((id) => String(id).toLowerCase()).filter(Boolean)
    : []
  const merged = [...new Set([...fromTask, ...studentRefs, ...server])]
  if (merged.length > 0) return merged
  return server.length ? server : fromTask
}

/** Языки для панели «Учу» (и legacy callers). */
export function resolveLanguageBarOptions(
  task: TaskDto | null | undefined,
  serverLanguageIds: string[] = [],
): string[] {
  return resolveLearningLanguageBarOptions(task, serverLanguageIds)
}

export function hasParallelExamples(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask = false,
): boolean {
  if (isFlowchartBlockAssemblyTask(task, isBlockAssemblyTask)) return false
  if (isBlockAssemblyTask) {
    return getKnownLanguages(task).length > 0 || getLearningLanguages(task).length > 0
  }
  return getKnownLanguages(task).length > 0
}

function normalizeLangList(languages: string[] | undefined): string[] {
  if (!Array.isArray(languages)) return []
  return languages.map((id) => String(id).toLowerCase()).filter(Boolean)
}

const KNOWN_LANGUAGES_NOT_READY_FOR_SWAP = new Set(["cpp", "java", "csharp"])

export function canSwapCurriculumMirrorLearning(task: TaskDto | null | undefined): boolean {
  if (!isCurriculumMirrorTask(task)) return false
  const mirrors = getMirrorLanguages(task)
  return mirrors.includes("pascal") && mirrors.includes("python")
}

/** Можно ли переключить сборник Pascal ↔ Python (не роли «знаю/учу»). */
export function canSwapCurriculumMirrorTrack(
  task: TaskDto | null | undefined,
  knownLanguage: string,
  learningLanguage: string,
): boolean {
  if (!canSwapCurriculumMirrorLearning(task)) return false
  const known = String(knownLanguage || "").toLowerCase()
  const learning = String(learningLanguage || "").toLowerCase()
  if (KNOWN_LANGUAGES_NOT_READY_FOR_SWAP.has(known)) return false
  if (known !== "python" && known !== "pascal") return false
  return learning === "pascal" || learning === "python"
}

function defaultKnownLanguageForTask(
  task: TaskDto | null | undefined,
  knownAvailable: string[],
): string {
  const sibling = getMirrorSiblingLanguage(task)
  if (sibling && knownAvailable.includes(sibling)) return sibling
  for (const pref of ["python", "pascal", "cpp", "csharp", "java"]) {
    if (knownAvailable.includes(pref)) return pref
  }
  return knownAvailable[0] || ""
}

/** Показывать селектор «Я знаю» (источник эталона). */
export function shouldShowKnownLanguageSelector(task: TaskDto | null | undefined): boolean {
  if (!task || getKnownLanguages(task).length === 0) return false
  if (isCurriculumMirrorTask(task)) return true
  return true
}

/** Показывать панель с кодом «Я знаю» слева от редактора. */
export function shouldShowKnownReferenceCode(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask = false,
): boolean {
  if (!task) return false
  if (isFlowchartBlockAssemblyTask(task, isBlockAssemblyTask)) return false
  if (isCurriculumMirrorTask(task)) {
    return getKnownLanguages(task).length > 0
  }
  if (isBlockAssemblyTask) return false
  if (isFlowchartTask(task)) {
    return isCodeToFlowchartTask(task) && Boolean(getReferenceCode(task, "python") || getReferenceCode(task, "pascal"))
  }
  return hasReferenceCode(task)
}

/** Показывать панель «Я знаю / Учу» над рабочей областью. */
export function shouldShowParallelLanguageBar(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask = false,
): boolean {
  if (canSwapCurriculumMirrorLearning(task)) return true
  if (shouldShowKnownLanguageSelector(task)) return getKnownLanguages(task).length > 0
  return hasParallelExamples(task, isBlockAssemblyTask)
}

export function isLearningLanguageOptionDisabled(
  lang: string,
  knownLanguage: string,
  task?: TaskDto | null,
): boolean {
  const option = String(lang || "").toLowerCase()
  const known = String(knownLanguage || "").toLowerCase()
  if (isCurriculumMirrorTask(task) && CURRICULUM_KNOWN_LANGUAGES.has(option)) {
    return option === known
  }
  return option === known
}

export function isKnownLanguageOptionDisabled(
  lang: string,
  learningLanguage: string,
  task?: TaskDto | null,
): boolean {
  const option = String(lang || "").toLowerCase()
  const learning = String(learningLanguage || "").toLowerCase()
  if (isCurriculumMirrorTask(task) && CURRICULUM_KNOWN_LANGUAGES.has(option)) {
    return option === learning
  }
  return option === learning
}

/** Можно ли поменять «Знаю» и «Учу» местами (оба языка есть в обеих ролях и они различаются). */
export function canSwapParallelLanguages(
  knownLanguage: string,
  learningLanguage: string,
  knownLanguages: string[],
  learningLanguages: string[],
  task?: TaskDto | null,
): boolean {
  if (isCurriculumMirrorTask(task) && learningLanguages.length > 2) {
    const known = String(knownLanguage || "").toLowerCase()
    const learning = String(learningLanguage || "").toLowerCase()
    return Boolean(known && learning && known !== learning)
  }
  if (canSwapCurriculumMirrorLearning(task)) {
    return canSwapCurriculumMirrorTrack(task, knownLanguage, learningLanguage)
  }
  const known = String(knownLanguage || "").toLowerCase()
  const learning = String(learningLanguage || "").toLowerCase()
  if (!known || !learning || known === learning) return false
  if (KNOWN_LANGUAGES_NOT_READY_FOR_SWAP.has(known) || KNOWN_LANGUAGES_NOT_READY_FOR_SWAP.has(learning)) {
    return false
  }
  const knownSet = new Set(normalizeLangList(knownLanguages))
  const learningSet = new Set(normalizeLangList(learningLanguages))
  return knownSet.has(learning) && learningSet.has(known)
}

export interface ParallelLanguagePairOptions {
  defaultId?: string
  languageOptions?: string[]
}

export interface ParallelLanguagePair {
  knownLanguage: string
  learningLanguage: string
  languages: string[]
  knownLanguages: string[]
  learningLanguages: string[]
}

/** «Знаю» = язык эталона слева; «Учу» = язык решения справа (всегда разные, если возможно). */
export function resolveParallelLanguagePair(
  task: TaskDto | null | undefined,
  { defaultId = "python", languageOptions = [] }: ParallelLanguagePairOptions = {},
  draft: TaskDraftRecord | null = null,
): ParallelLanguagePair {
  const knownAvailable = getKnownLanguages(task)
  const isPascal = isPascalCurriculumTask(task)
  const isPython = isPythonCurriculumTask(task)
  const isCpp = isCppCurriculumTask(task)
  const learningAvailable = getLearningLanguages(task)
  const optionList = languageOptions.length ? languageOptions : learningAvailable
  const pickOtherLearning = (lang: string) =>
    learningAvailable.find((item) => item !== lang) ||
    optionList.find((item) => item !== lang) ||
    ""

  const defaultKnown = isCurriculumMirrorTask(task)
    ? defaultKnownLanguageForTask(task, knownAvailable)
    : knownAvailable[0] || ""

  const defaultLearning = isPascal
    ? "pascal"
    : isPython
      ? "python"
      : isCpp
        ? "cpp"
        : learningAvailable.find((lang) => lang !== defaultKnown) ||
      optionList.find((lang) => lang !== defaultKnown) ||
      (defaultId && learningAvailable.includes(defaultId) && defaultId !== defaultKnown
        ? defaultId
        : "") ||
      (defaultId && optionList.includes(defaultId) && defaultId !== defaultKnown ? defaultId : "") ||
      learningAvailable[0] ||
      optionList[0] ||
      ""

  const known = isCurriculumMirrorTask(task)
    ? resolveKnownLanguageWithReference(task, defaultKnown)
    : resolveKnownLanguageWithReference(
        task,
        typeof draft?.selectedExampleLanguage === "string" && draft.selectedExampleLanguage
          ? draft.selectedExampleLanguage
          : defaultKnown,
      )
  let learning =
    typeof draft?.userLanguage === "string" && draft.userLanguage ? draft.userLanguage : defaultLearning

  if (known && learning && known === learning) {
    learning = pickOtherLearning(known) || learning
  }

  return {
    knownLanguage: known,
    learningLanguage: learning,
    languages: learningAvailable.length ? learningAvailable : optionList,
    knownLanguages: knownAvailable,
    learningLanguages: learningAvailable.length ? learningAvailable : optionList,
  }
}

const TRANSLATION_TYPES = new Set([
  "translation",
  "task_translate_snippet",
  "task_translate_full_program",
  "translation_task",
])

export function isTranslationTask(task: TaskDto | null | undefined): boolean {
  const action = getTaskPrimaryAction(task)
  if (action === "translate") return true
  if (action && action !== "translate") return false
  return TRANSLATION_TYPES.has(String(task?.type))
}

export function isTranslationSnippetTask(task: TaskDto | null | undefined): boolean {
  return task?.type === "task_translate_snippet"
}

export function isMcqTask(task: TaskDto | null | undefined): boolean {
  const flowSpec = (task?.flow_spec || {}) as { mcq_mode?: boolean }
  return Boolean(flowSpec.mcq_mode)
}

export function getMcqOptions(task: TaskDto | null | undefined): string[] {
  const examples = (task?.code_examples || {}) as { mcq_options?: unknown }
  const raw = examples.mcq_options
  return Array.isArray(raw) ? raw.map((item) => String(item)) : []
}

/** Task 2 style: two editable code panes (знаю | учу). Non-Pascal only. */
export function isDualCodeTask(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask = false,
): boolean {
  if (isBlockAssemblyTask || isFlowchartTask(task)) return false
  if (isPascalCurriculumTask(task) || isPythonCurriculumTask(task)) return false
  return isTranslationTask(task) && hasParallelExamples(task, false)
}

export function isAnalyzeTask(task: TaskDto | null | undefined): boolean {
  const action = String(task?.curriculum?.action || task?.primary_action || "").toLowerCase()
  return action === "analyze"
}

/** Left = reference code, right = editor. Block assembly uses full-width assembly only. */
export function isReferenceSplitTask(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask = false,
): boolean {
  if (!shouldShowKnownReferenceCode(task, isBlockAssemblyTask)) return false
  if (isAnalyzeTask(task)) return false
  if (isDualCodeTask(task, isBlockAssemblyTask)) return false
  if (isFlowchartTask(task)) return false
  if (isBlockAssemblyTask) return false
  if (isPascalCurriculumTask(task) || isPythonCurriculumTask(task)) {
    return hasReferenceCode(task)
  }
  return hasReferenceCode(task)
}

export function resolveEditorMode(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask: boolean,
): "code" | "blocks" {
  if (isFlowchartTask(task)) return "code"
  if (isBlockAssemblyTask) return "blocks"
  return "code"
}

/** Task diagram from API only (not localStorage / starter templates). */
export function hasTeacherDiagramInTask(task: TaskDto | null | undefined): boolean {
  if (!task) return false
  const diagram = task.diagram
  if (diagram && typeof diagram === "object") {
    if (Array.isArray(diagram.nodes) && diagram.nodes.length > 0) return true
    if (Array.isArray(diagram.flow) && diagram.flow.length > 0) return true
  }
  return false
}

export function getFlowchartMode(task: TaskDto | null | undefined): string {
  const examples = task?.code_examples as Record<string, unknown> | undefined
  const showcase = examples?.curriculum_showcase as { flowchart_mode?: string } | undefined
  return task?.curriculum?.flowchart_mode || showcase?.flowchart_mode || ""
}

/** code → flowchart: Pascal reference on the left, student builds diagram. */
export function isCodeToFlowchartTask(task: TaskDto | null | undefined): boolean {
  if (!isFlowchartTask(task)) return false
  const mode = getFlowchartMode(task)
  if (mode === "code_to_flowchart") return true
  if (mode === "flowchart_to_code" || mode === "flowchart_to_blocks") return false
  return hasFlowchartCompositionCodeReference(task) && !hasTeacherDiagramInTask(task)
}

/** Block-assembly task with teacher diagram on the left (flowchart → blocks). */
export function isFlowchartBlockAssemblyTask(
  task: TaskDto | null | undefined,
  isBlockAssemblyTask = false,
): boolean {
  if (!isBlockAssemblyTask || !task) return false
  return hasTeacherDiagramInTask(task)
}

/** Преподаватель задал эталонную блок-схему (API diagram, не шаблон ответа). */
export function hasTeacherFlowchartReference(task: TaskDto | null | undefined): boolean {
  return hasTeacherDiagramInTask(task)
}

/** Преподаватель задал эталонный код (code_examples / reference_code). */
export function hasTeacherCodeReference(task: TaskDto | null | undefined): boolean {
  return hasReferenceCode(task)
}

/** Языки эталонного кода, которые преподаватель явно открыл студенту (flow_spec). */
export function getStudentReferenceLanguages(task: TaskDto | null | undefined): string[] {
  const fromSpec = task?.flow_spec?.student_reference_languages
  if (Array.isArray(fromSpec) && fromSpec.length > 0) {
    return fromSpec
      .map((id) => String(id).toLowerCase())
      .filter((lang) => lang && getReferenceCode(task, lang) != null)
  }
  if (!isFlowchartTask(task)) return getKnownLanguages(task)
  return []
}

/**
 * Эталонный код, по которому студент может составлять схему.
 * В задачах «схема → код» code_examples в API часто служебный;
 * переключение доступно только при student_reference_languages в flow_spec.
 */
export function hasFlowchartCompositionCodeReference(task: TaskDto | null | undefined): boolean {
  if (!isFlowchartTask(task)) return false
  return getStudentReferenceLanguages(task).length > 0
}

/** Стрелка активна: преподаватель дал и блок-схему, и эталонный код студенту. */
export function canSwapFlowchartSolutionModes(task: TaskDto | null | undefined): boolean {
  if (!isFlowchartTask(task)) return false
  if (isCodeToFlowchartTask(task)) return false
  return hasTeacherDiagramInTask(task) && hasFlowchartCompositionCodeReference(task)
}

export function getDefaultFlowchartSolutionMode(task: TaskDto | null | undefined): string {
  if (isCodeToFlowchartTask(task)) return "flow"
  if (hasTeacherDiagramInTask(task)) return "code"
  if (hasFlowchartCompositionCodeReference(task)) return "flow"
  return "code"
}

export interface UsedConstructsMap {
  loop: boolean
  cond: boolean
  io: boolean
  arith: boolean
  assign: boolean
}

export function detectUsedConstructs(code = ""): UsedConstructsMap {
  const source = String(code)
  return {
    loop: /\b(while|for)\b/.test(source),
    cond: /\bif\b/.test(source) || /\?\s*\w+\s*:/.test(source),
    io: /\b(print|console\.log|cout|fmt\.Print|Println|printf|input|prompt|cin|Scan)\b/.test(source),
    arith: /[+\-*/%]/.test(source) || /\/\//.test(source) || /Math\.floor/.test(source),
    assign: /=/.test(source) || /:=/.test(source),
  }
}
