import { getMonacoLanguage } from "@/shared/config/languages"

const LANG_KEYWORDS = {
  python: {
    kw: [
      "while", "if", "else", "elif", "for", "in", "return", "def", "import", "from", "as",
      "True", "False", "None", "and", "or", "not", "is", "lambda", "pass", "break", "continue",
      "yield", "class",
    ],
    fn: [
      "int", "str", "input", "print", "len", "range", "float", "list", "dict", "set", "tuple",
      "abs", "sum", "map", "filter", "open",
    ],
    cmt: "#",
  },
  javascript: {
    kw: [
      "function", "const", "let", "var", "return", "if", "else", "for", "while", "do", "break",
      "continue", "class", "new", "this", "true", "false", "null", "undefined", "of", "in",
      "typeof", "switch", "case", "default", "try", "catch", "throw", "async", "await", "export",
      "import",
    ],
    fn: [
      "parseInt", "parseFloat", "console", "prompt", "Math", "String", "Number", "Array", "Object",
      "JSON", "log", "floor",
    ],
    cmt: "//",
  },
  typescript: {
    kw: [
      "function", "const", "let", "var", "return", "if", "else", "for", "while", "break",
      "continue", "class", "new", "this", "true", "false", "null", "undefined", "of", "in",
      "typeof", "switch", "case", "default", "try", "catch", "throw", "async", "await", "export",
      "import", "interface", "type", "enum",
    ],
    fn: ["parseInt", "parseFloat", "console", "Math", "String", "Number", "Array", "Object", "JSON"],
    cmt: "//",
  },
  java: {
    kw: [
      "public", "private", "protected", "class", "static", "void", "int", "long", "double", "float",
      "boolean", "char", "byte", "short", "if", "else", "for", "while", "do", "return", "new",
      "true", "false", "null", "break", "continue", "switch", "case", "default", "try", "catch",
      "throw", "final", "import", "package",
    ],
    fn: ["System", "out", "println", "print", "String", "Math", "Integer", "Double"],
    cmt: "//",
  },
  cpp: {
    kw: [
      "int", "void", "char", "bool", "double", "float", "if", "else", "for", "while", "do",
      "return", "class", "struct", "public", "private", "include", "using", "namespace", "const",
      "true", "false", "nullptr", "new", "delete", "break", "continue", "switch", "case",
    ],
    fn: ["std", "cin", "cout", "endl", "printf", "scanf", "vector", "string"],
    cmt: "//",
  },
  c: {
    kw: [
      "int", "void", "char", "if", "else", "for", "while", "do", "return", "struct", "const",
      "break", "continue", "switch", "case", "include",
    ],
    fn: ["printf", "scanf", "malloc", "free"],
    cmt: "//",
  },
  go: {
    kw: [
      "package", "import", "func", "var", "const", "type", "struct", "if", "else", "for",
      "return", "range", "true", "false", "nil", "break", "continue", "switch", "case", "default",
    ],
    fn: ["fmt", "Println", "Print", "Printf", "make", "len", "append"],
    cmt: "//",
  },
}

export function getLangTokenSpec(language) {
  const id = String(language || "").toLowerCase()
  if (LANG_KEYWORDS[id]) {
    return LANG_KEYWORDS[id]
  }
  const monacoId = getMonacoLanguage(id)
  return LANG_KEYWORDS[monacoId] || LANG_KEYWORDS.python
}

function langSpec(language) {
  return getLangTokenSpec(language)
}

export function tokenizeCodeLine(line, language) {
  const spec = langSpec(language)
  const cmt = spec.cmt
  const tokens = []
  let i = 0

  while (i < line.length) {
    if (line.slice(i, i + cmt.length) === cmt) {
      tokens.push({ c: "cmt", t: line.slice(i) })
      break
    }

    const ch = line[i]

    if (ch === '"' || ch === "'" || ch === "`") {
      let j = i + 1
      while (j < line.length && line[j] !== ch) {
        if (line[j] === "\\") j += 1
        j += 1
      }
      tokens.push({ c: "str", t: line.slice(i, Math.min(j + 1, line.length)) })
      i = Math.min(j + 1, line.length)
      continue
    }

    if (/[A-Za-z_]/.test(ch)) {
      let j = i
      while (j < line.length && /[A-Za-z_0-9]/.test(line[j])) j += 1
      const word = line.slice(i, j)
      if (spec.kw.includes(word)) tokens.push({ c: "kw", t: word })
      else if (spec.fn.includes(word)) tokens.push({ c: "fn", t: word })
      else tokens.push({ c: "id", t: word })
      i = j
      continue
    }

    if (/[0-9]/.test(ch)) {
      let j = i
      while (j < line.length && /[0-9.]/.test(line[j])) j += 1
      tokens.push({ c: "num", t: line.slice(i, j) })
      i = j
      continue
    }

    if (/\s/.test(ch)) {
      let j = i
      while (j < line.length && /\s/.test(line[j])) j += 1
      tokens.push({ c: "ws", t: line.slice(i, j) })
      i = j
      continue
    }

    let j = i
    while (j < line.length && /[^A-Za-z_0-9\s'"`]/.test(line[j])) {
      if (line.slice(j, j + cmt.length) === cmt) break
      j += 1
    }
    tokens.push({ c: "op", t: line.slice(i, j) })
    i = j
  }

  return tokens
}
