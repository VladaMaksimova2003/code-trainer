/** Format minified block-assembly templates for display (preserves `{n}` slots). */

const SLOT_MARKER_RE = /\{\d+\}/
const SLOT_REPLACE_RE = /\{(\d+)\}/g

function protectSlots(text: string): { body: string; slots: string[] } {
  const slots: string[] = []
  const body = text.replace(SLOT_REPLACE_RE, (_, index) => {
    slots.push(`{${index}}`)
    return `__CT_ASM_SLOT_${slots.length - 1}__`
  })
  return { body, slots }
}

function restoreSlots(text: string, slots: string[]): string {
  let out = text
  slots.forEach((slot, index) => {
    out = out.split(`__CT_ASM_SLOT_${index}__`).join(slot)
  })
  return out
}

function collapseWs(text: string): string {
  return String(text || "").replace(/\s+/g, " ").trim()
}

function formatPythonShell(code: string): string {
  let one = collapseWs(code)
  one = one.replace(/\)(?=[a-z_[(])/gi, ")\n")
  one = one.replace(/\](?=[a-z_[(])/gi, "]\n")
  one = one.replace(/(\d)(?=\s*for\b)/gi, "$1\n")
  let formatted = one
  const keywords = [
    "print",
    "input",
    "if",
    "elif",
    "else",
    "for",
    "while",
    "def",
    "class",
    "return",
    "import",
    "from",
    "try",
    "except",
    "with",
  ]
  for (const kw of keywords) {
    formatted = formatted.replace(new RegExp(`(?<=[A-Za-z0-9_\\)\\]])(?=${kw}\\b)`, "g"), "\n")
    formatted = formatted.replace(new RegExp(`(?<!\\w)(${kw}\\b)`, "g"), "\n$1")
  }
  formatted = formatted.replace(/](?=\S)/g, "]\n")
  return formatted
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .join("\n")
}

function formatPascalShell(code: string): string {
  let one = collapseWs(code)
  one = one.replace(/\s*\bvar\b\s*/gi, "\nvar ")
  one = one.replace(/\s*\bbegin\b\s*/gi, "\nbegin\n")
  one = one.replace(/\s*\bfor\b\s*/gi, "\nfor ")
  one = one.replace(/\s*\bif\b\s*/gi, "\n  if ")
  one = one.replace(/\s*\bwriteln\b\s*/gi, "\n  writeln")
  one = one.replace(/\s*\bwrite\b\s*/gi, "\n  write")
  one = one.replace(/\s*\bend\.\s*/gi, "\nend.")
  one = one.replace(/;\s*/g, ";\n")

  const lines: string[] = []
  for (const raw of one.split("\n")) {
    const stripped = raw.trim()
    if (!stripped) continue
    if (stripped === "begin" || stripped === "end.") {
      lines.push(stripped)
    } else if (/^(var |program )/i.test(stripped)) {
      lines.push(stripped)
    } else {
      lines.push(stripped.startsWith("  ") ? stripped : `  ${stripped.replace(/^\s+/, "")}`)
    }
  }
  return lines.join("\n")
}

function formatBraceLangShell(code: string): string {
  let one = collapseWs(code)
  one = one.replace(/#include/g, "\n#include")
  one = one.replace(/using System;/g, "using System;\n")
  one = one.replace(/\{(?=\S)/g, "{\n  ")
  one = one.replace(/\}(?=\S)/g, "}\n")
  one = one.replace(/;(?=\S)/g, ";\n")
  return one
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .join("\n")
}

function formatShell(code: string, language: string): string {
  const lang = String(language || "python").toLowerCase()
  if (lang === "python") return formatPythonShell(code)
  if (lang === "pascal") return formatPascalShell(code)
  if (lang === "cpp" || lang === "csharp" || lang === "java" || lang === "cs" || lang === "c#") {
    return formatBraceLangShell(code)
  }
  return code
}

export function formatAssemblyTemplate(template: string, language: string): string {
  const raw = String(template ?? "").trim()
  if (!raw || !SLOT_MARKER_RE.test(raw)) return raw

  // API already returns multi-line scaffolds — re-running brace/python formatters
  // collapses whitespace and destroys slot line alignment.
  if (raw.includes("\n")) {
    return raw
      .split("\n")
      .map((line) => line.trimEnd())
      .join("\n")
  }

  const { body, slots } = protectSlots(raw)
  const formatted = formatShell(body, language)
  return restoreSlots(formatted, slots)
}
