/** Pedagogical stdin display for the student test table (not execution format). */

export interface TestInputDisplayContext {
  patternId?: string
  goal?: string
  referenceCode?: string
  pascalCode?: string
  cppCode?: string
  csharpCode?: string
}

const LAYOUT_BY_PATTERN: Record<string, string> = {
  task_002: "count_target_line",
  task_005: "count_then_lines",
  task_001: "count_then_lines",
  task_006: "count_then_lines",
  task_004: "count_then_lines",
  task_007: "count_then_lines",
  task_008: "count_then_lines",
  task_018: "count_target_line",
  task_022: "count_target_line",
  task_026: "count_k_line",
  task_027: "count_pos_line",
  task_028: "count_pos_value_lines",
  task_029: "count_pos_value_lines",
  task_129: "single_line",
}

function tokenize(raw: string): string[] {
  return String(raw || "")
    .split(/\s+/)
    .map((p) => p.trim())
    .filter(Boolean)
}

function asCount(token: string, fallback: number): number {
  const n = Number.parseInt(token, 10)
  return Number.isFinite(n) ? n : fallback
}

function bracketList(values: string[]): string {
  if (!values.length) return "[]"
  return `[${values.join(", ")}]`
}

function joinScalarLine(values: string[]): string {
  return values.join(" ")
}

/** True when body values are read one-by-one in a loop, not as a list/array on one line. */
function readsBodyAsScalarStream(ctx: TestInputDisplayContext): boolean {
  const code = pickCode(ctx)
  const g = String(ctx.goal || "").toLowerCase()

  if (/по одному|кажд(ый|ую|ое)\s+/i.test(g)) return true

  if (/\[int\s*\(\s*input\s*\(\s*\)\s*\)\s+for\s+_/i.test(code)) return true
  if (/for\s+_+\s+in\s+range\s*\([^)]*\)[\s\S]{0,400}int\s*\(\s*input\s*\(\s*\)\s*\)/i.test(code)) {
    return true
  }

  if (/for\s*\([^)]*\)[\s\S]{0,500}std::cin\s*>>/i.test(code)) return true
  if (/for\s+i\s*:=\s*\d+\s+to\s+n[\s\S]{0,400}readln/i.test(code)) return true
  if (/while\s+[\s\S]{0,300}(?:readln|std::cin\s*>>|int\s*\(\s*input)/i.test(code)) return true

  if (/list\s*\(\s*map|=\s*list\s*\(|input\s*\(\s*\)\s*\.split\s*\(/i.test(code)) return false
  if (/Array\.ConvertAll/i.test(code)) return false

  return false
}

function formatBodyValues(values: string[], ctx: TestInputDisplayContext): string {
  if (!values.length) return readsBodyAsScalarStream(ctx) ? "" : "[]"
  return readsBodyAsScalarStream(ctx) ? joinScalarLine(values) : bracketList(values)
}

function pickCode(ctx: TestInputDisplayContext): string {
  return (
    ctx.pascalCode?.trim() ||
    ctx.cppCode?.trim() ||
    ctx.csharpCode?.trim() ||
    ctx.referenceCode?.trim() ||
    ""
  )
}

export function inferStdinLayout(ctx: TestInputDisplayContext = {}): string {
  const pid = String(ctx.patternId || "").trim()
  if (LAYOUT_BY_PATTERN[pid]) return LAYOUT_BY_PATTERN[pid]

  const code = pickCode(ctx)
  const g = String(ctx.goal || "").toLowerCase()

  if (/readln\s*\(\s*n\s*,\s*target/i.test(code) || (g.includes("первой строке") && g.includes("искомый код"))) {
    return "count_target_line"
  }
  if (/std::cin\s*>>\s*n\s*>>\s*target/i.test(code)) return "count_target_line"
  if (/readln\s*\(\s*n\s*,\s*k\s*\)/i.test(code) || /\bn,\s*k\b/i.test(g)) return "count_k_line"
  if (/std::cin\s*>>\s*n\s*>>\s*k\b/i.test(code)) return "count_k_line"
  if (g.includes("затем искомое значение") && !["task_002", "task_018", "task_022"].includes(pid)) {
    return "count_values_query"
  }
  if (g.includes("стоп-значения 0") || g.includes("пока не встретите 0") || g.includes("до появления стоп")) {
    return "lines_all"
  }
  if (/дано целое\s+n/i.test(g) || pid === "task_129") return "single_line"

  const readlnMatch = code.match(/readln\s*\(\s*([^)]+)\s*\)/i)
  if (readlnMatch) {
    const args = readlnMatch[1].split(",").map((a) => a.trim()).filter(Boolean)
    if (args.length === 1 && args[0].toLowerCase() === "n" && /for\s+i\s*:=\s*1\s+to\s+n/i.test(code)) {
      return "count_then_lines"
    }
    if (args.length >= 2 && args.length <= 6 && args.every((a) => /^[a-z_]\w*$/i.test(a))) {
      return `first_line_${args.length}`
    }
  }

  if (/std::cin\s*>>\s*n\s*;/i.test(code) && /for\s*\([^)]*\)[\s\S]*std::cin\s*>>/i.test(code)) {
    return "count_then_lines"
  }
  if (/int\.Parse\(Console\.ReadLine\(\)\)/i.test(code) && /for\s*\([^)]*\)[\s\S]*ReadLine/i.test(code)) {
    return "count_then_lines"
  }

  const cinMulti = code.match(/std::cin\s*>>\s*([a-z_]\w*)(?:\s*>>\s*([a-z_]\w*))+/i)
  if (cinMulti && !/for\s*\(/i.test((code.split(cinMulti[0])[0] || ""))) {
    const head = cinMulti[0].match(/>>\s*([a-z_]\w*)/gi) || []
    return `first_line_${head.length}`
  }

  const splitAssign = code.match(
    /^([a-z_][\w]*(?:\s*,\s*[a-z_][\w]*)+)\s*=\s*map\([^)]+\)\s*,\s*input\(\)\.split\(\)/im,
  )
  if (splitAssign) {
    const count = splitAssign[1].split(",").filter(Boolean).length
    if (count >= 2) return `first_line_${count}`
  }

  if (/list\(map\(int,\s*input\(\)\.split\(\)\)\)/i.test(code)) return "single_line_list"

  if (/n\s*=\s*int\(input\(\)\)/i.test(code) && /\[int\(input\(\)\)\s+for\s+_+\s+in\s+range\(n\)\]/i.test(code)) {
    return "count_then_lines"
  }
  if (/n\s*=\s*int\(input\(\)\)/i.test(code) && /range\(n\)/i.test(code)) return "count_then_lines"
  if (/while\s+.*!=\s*0/i.test(code)) return "lines_all"
  if ((code.match(/int\(input\(\)\)/g) || []).length === 1 && !/for\s|while\s/i.test(code)) return "single_line"
  if (g.includes("количество") || g.includes("вводится количество")) return "count_then_lines"
  if (g.includes("три целых числа") || g.includes("три стороны")) return "first_line_3"
  if (g.includes("день") && g.includes("месяц")) return "first_line_3"
  return ""
}

export function formatStdinForDisplay(raw: string, ctx: TestInputDisplayContext = {}): string {
  const parts = tokenize(raw)
  if (!parts.length) return ""

  const layout = inferStdinLayout(ctx)
  if (!layout) {
    const lines = String(raw || "")
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.length > 0)
    if (lines.length > 1) return lines.join("\n")
    return parts.join(" ")
  }

  if (layout === "single_line") return parts[0]
  if (layout === "single_line_list") return bracketList(parts)

  if (layout.startsWith("first_line_")) {
    const k = Number.parseInt(layout.split("_").pop() || "1", 10)
    if (parts.length <= k) return parts.join(" ")
    const head = parts.slice(0, k).join(" ")
    const rest = parts.slice(k)
    return rest.length ? `${head}\n${formatBodyValues(rest, ctx)}` : head
  }

  if (layout === "count_target_line") {
    if (parts.length < 2) return parts.join("\n")
    const n = asCount(parts[0], Math.max(parts.length - 2, 0))
    const head = `${parts[0]} ${parts[1]}`
    const body = parts.slice(2, 2 + n)
    return `${head}\n${formatBodyValues(body, ctx)}`
  }

  if (layout === "count_k_line") {
    if (parts.length < 2) return parts.join("\n")
    const n = asCount(parts[0], Math.max(parts.length - 2, 0))
    const head = `${parts[0]} ${parts[1]}`
    const body = parts.slice(2, 2 + n)
    return `${head}\n${formatBodyValues(body, ctx)}`
  }

  if (layout === "count_then_lines") {
    const n = asCount(parts[0], Math.max(parts.length - 1, 0))
    const body = parts.slice(1, 1 + n)
    return `${parts[0]}\n${formatBodyValues(body, ctx)}`
  }

  if (layout === "count_values_query") {
    const n = asCount(parts[0], Math.max(parts.length - 2, 0))
    const body = parts.slice(1, 1 + n)
    const tail = parts.slice(1 + n)
    const lines = [parts[0], formatBodyValues(body, ctx)]
    if (tail.length) lines.push(tail.join(" "))
    return lines.join("\n")
  }

  if (layout === "count_pos_line") {
    const n = asCount(parts[0], Math.max(parts.length - 2, 0))
    const body = parts.slice(1, 1 + n)
    const pos = parts[1 + n] ?? parts[parts.length - 1]
    return `${parts[0]}\n${formatBodyValues(body, ctx)}\n${pos}`
  }

  if (layout === "count_pos_value_lines") {
    const n = asCount(parts[0], Math.max(parts.length - 3, 0))
    const body = parts.slice(1, 1 + n)
    const tail = parts.slice(1 + n)
    const lines = [parts[0], formatBodyValues(body, ctx)]
    if (tail.length) lines.push(tail.join(" "))
    return lines.join("\n")
  }

  if (layout === "lines_all") {
    const sentinelIdx = parts.findIndex((p) => p === "0")
    if (sentinelIdx >= 0) {
      const before = parts.slice(0, sentinelIdx)
      const after = parts.slice(sentinelIdx)
      if (before.length) {
        const beforeFmt = formatBodyValues(before, ctx)
        return after.length ? `${beforeFmt}\n${after.join("\n")}` : beforeFmt
      }
    }
    return parts.join("\n")
  }

  return parts.join("\n")
}

export function testInputDisplayContextFromTask(
  task:
    | {
        description?: string | null
        code_examples?: Record<string, string> | null
        curriculum?: Record<string, unknown> | null
      }
    | null
    | undefined,
  learningLanguage?: string,
): TestInputDisplayContext {
  const codes = task?.code_examples ?? {}
  const curriculum = task?.curriculum ?? {}
  const lang = String(learningLanguage || "pascal").toLowerCase()
  return {
    patternId: String(
      curriculum.slot_pattern_id ||
        curriculum.exercise_pattern_id ||
        curriculum.pattern_id ||
        "",
    ),
    goal: String(task?.description || ""),
    referenceCode: codes.python || codes[lang] || "",
    pascalCode: codes.pascal || "",
    cppCode: codes.cpp || "",
    csharpCode: codes.csharp || "",
  }
}

export function formatTestInputCell(
  value: unknown,
  ctx: TestInputDisplayContext = {},
): string {
  if (value === "") return "∅"
  const raw = typeof value === "string" ? value : String(value ?? "")
  if (!raw.trim()) return "—"
  return formatStdinForDisplay(raw, ctx).trim() || "—"
}
