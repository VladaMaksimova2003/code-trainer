/** Structured I/O for test cases — supports scalar, lists, matrices, JSON. */

export enum IoValueKind {
  SCALAR = "scalar",
  MULTI = "multi",
  MATRIX = "matrix",
  JSON = "json",
}

export interface IoValue {
  kind: IoValueKind
  /** Single line / number / string */
  text?: string
  /** Multiple stdin lines or arguments */
  lines?: string[]
  /** 2D matrix — each row is one line of input */
  grid?: string[][]
  /** Raw JSON text while editing */
  jsonText?: string
}

export function createScalar(text = ""): IoValue {
  return { kind: IoValueKind.SCALAR, text }
}

export function createMulti(lines: string[] = [""]): IoValue {
  return { kind: IoValueKind.MULTI, lines: lines.length ? lines : [""] }
}

export function createMatrix(rows = 2, cols = 2): IoValue {
  const grid = Array.from({ length: rows }, () =>
    Array.from({ length: cols }, () => "")
  )
  return { kind: IoValueKind.MATRIX, grid }
}

export function createJson(jsonText = "{\n  \n}"): IoValue {
  return { kind: IoValueKind.JSON, jsonText }
}

export function createEmptyIoValue(kind: IoValueKind): IoValue {
  switch (kind) {
    case IoValueKind.MULTI:
      return createMulti()
    case IoValueKind.MATRIX:
      return createMatrix()
    case IoValueKind.JSON:
      return createJson()
    default:
      return createScalar()
  }
}

export function normalizeIoValue(raw: IoValue | string | unknown): IoValue {
  if (typeof raw === "string") {
    return createScalar(raw)
  }
  if (raw && typeof raw === "object" && "kind" in raw) {
    return raw as IoValue
  }
  if (raw && typeof raw === "object" && "type" in raw) {
    return deserializeIoValue(raw as SerializedIo)
  }
  return createScalar("")
}

export interface SerializedIo {
  type: string
  value?: unknown
  raw?: string
}

export function serializeIoValue(io: IoValue): SerializedIo {
  switch (io.kind) {
    case IoValueKind.SCALAR:
      return { type: "scalar", value: io.text ?? "" }
    case IoValueKind.MULTI:
      return {
        type: "multi",
        value: (io.lines ?? []).filter((l) => l.length > 0),
      }
    case IoValueKind.MATRIX:
      return { type: "matrix", value: io.grid ?? [] }
    case IoValueKind.JSON:
      try {
        return {
          type: "json",
          value: JSON.parse(io.jsonText || "{}"),
        }
      } catch {
        return { type: "json", raw: io.jsonText ?? "" }
      }
    default:
      return { type: "scalar", value: "" }
  }
}

export function deserializeIoValue(data: SerializedIo): IoValue {
  const t = data.type
  if (t === "multi" && Array.isArray(data.value)) {
    return {
      kind: IoValueKind.MULTI,
      lines: data.value.map(String),
    }
  }
  if (t === "matrix" && Array.isArray(data.value)) {
    return {
      kind: IoValueKind.MATRIX,
      grid: data.value.map((row) =>
        Array.isArray(row) ? row.map(String) : [String(row)]
      ),
    }
  }
  if (t === "json") {
    if (data.raw != null) {
      return { kind: IoValueKind.JSON, jsonText: String(data.raw) }
    }
    return {
      kind: IoValueKind.JSON,
      jsonText: JSON.stringify(data.value ?? {}, null, 2),
    }
  }
  return createScalar(String(data.value ?? ""))
}

/** Flat stdin/stdout string for API test_cases (inputs / output). */
export function serializeIoValueForTestCase(io: IoValue): string {
  switch (io.kind) {
    case IoValueKind.SCALAR:
      return io.text ?? ""
    case IoValueKind.MULTI:
      return (io.lines ?? []).join("\n")
    case IoValueKind.MATRIX:
      return (io.grid ?? []).map((row) => row.join(" ")).join("\n")
    case IoValueKind.JSON:
      return (io.jsonText ?? JSON.stringify({})).trim()
    default:
      return ""
  }
}

/** Human preview for tables */
export function formatIoPreview(io: IoValue, maxLen = 48): string {
  switch (io.kind) {
    case IoValueKind.SCALAR:
      return (io.text ?? "").slice(0, maxLen) || "—"
    case IoValueKind.MULTI:
      return `[${(io.lines ?? []).length} values] ${(io.lines ?? [])[0] ?? ""}`.slice(
        0,
        maxLen
      )
    case IoValueKind.MATRIX: {
      const rows = io.grid?.length ?? 0
      const cols = io.grid?.[0]?.length ?? 0
      return `matrix ${rows}×${cols}`
    }
    case IoValueKind.JSON:
      return (io.jsonText ?? "").replace(/\s+/g, " ").slice(0, maxLen) || "{}"
    default:
      return "—"
  }
}
