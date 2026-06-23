import { getMonacoLanguage } from "@/shared/config/languages"
import { getLangTokenSpec } from "@/widgets/BlockAssemblyEditor/lib/codeTokenizer"

const STUDENT_THEME_RULES = [
  { token: "keyword", foreground: "f472b6" },
  { token: "keyword.control", foreground: "f472b6" },
  { token: "storage.type", foreground: "f472b6" },
  { token: "storage.modifier", foreground: "f472b6" },
  { token: "identifier", foreground: "eef2f7" },
  { token: "variable", foreground: "eef2f7" },
  { token: "number", foreground: "fcd34d" },
  { token: "string", foreground: "86efac" },
  { token: "comment", foreground: "626d7e" },
  { token: "entity.name.function", foreground: "a3e635" },
  { token: "support.function", foreground: "a3e635" },
  { token: "support.class", foreground: "a3e635" },
  { token: "keyword.operator", foreground: "9aa6b6" },
  { token: "delimiter", foreground: "9aa6b6" },
  { token: "operator", foreground: "9aa6b6" },
  { token: "meta.preprocessor", foreground: "9aa6b6" },
]

function escapeRegexWord(word) {
  return word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

function buildKeywordPattern(words) {
  if (!words.length) {
    return /$^/
  }
  return new RegExp(`\\b(${words.map(escapeRegexWord).join("|")})\\b`)
}

function buildMonarchTokenizer(spec) {
  const kwPattern = buildKeywordPattern(spec.kw)
  const fnPattern = buildKeywordPattern(spec.fn)
  const lineComment = spec.cmt === "#" ? /#.*/ : /\/\/.*/

  return {
    defaultToken: "identifier",
    ignoreCase: false,
    tokenizer: {
      root: [
        [lineComment, "comment"],
        [/"(?:\\.|[^"\\])*"/, "string"],
        [/'(?:\\.|[^'\\])*'/, "string"],
        [/#\s*include\b/, "keyword"],
        [kwPattern, "keyword"],
        [fnPattern, "support.function"],
        [/\b\d+(?:\.\d+)?\b/, "number"],
        [/[{}()[\];,.<>]/, "delimiter"],
        [/[=+\-*/%!&|^~?:]+/, "operator"],
        [/#/, "operator"],
        [/[A-Za-z_]\w*/, "identifier"],
        [/\s+/, ""],
      ],
    },
  }
}

export function applyStudentMonacoSyntax(monaco, languageId) {
  const spec = getLangTokenSpec(languageId)
  const monacoLang = getMonacoLanguage(languageId) || "plaintext"

  monaco.editor.defineTheme("studentSurface", {
    base: "vs-dark",
    inherit: false,
    rules: STUDENT_THEME_RULES,
    colors: {
      "editor.background": "#141a24",
      "editorGutter.background": "#141a24",
      "editorLineNumber.foreground": "#626d7e",
      "editorLineNumber.activeForeground": "#9aa6b6",
      "editor.lineHighlightBackground": "#1d2331",
      "editor.lineHighlightBorder": "#1d2331",
      "minimap.background": "#141a24",
      "editorOverviewRuler.background": "#141a24",
      "editorOverviewRuler.border": "#141a24",
    },
  })

  if (monacoLang !== "plaintext") {
    monaco.languages.setMonarchTokensProvider(monacoLang, buildMonarchTokenizer(spec))
  }

  monaco.editor.setTheme("studentSurface")
}
