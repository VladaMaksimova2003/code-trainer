import { useEffect, useMemo, useRef } from "react"
import Editor from "@monaco-editor/react"
import { getMonacoLanguage } from "@/shared/config/languages"
import { applyStudentMonacoSyntax } from "@/widgets/CodeEditorBoard/lib/studentMonacoSyntax"

const parseDiagnostic = (error, source) => {
  const text = error?.text || ""
  const lineColumnMatch = text.match(/Line\s+(\d+):(\d+):\s*(.*)/i)
  if (lineColumnMatch) {
    return {
      line: Number(lineColumnMatch[1]),
      column: Number(lineColumnMatch[2]),
      message: lineColumnMatch[3],
      source,
    }
  }

  const lineOnlyMatch = text.match(/Line\s+(\d+):\s*(.*)/i)
  if (lineOnlyMatch) {
    return {
      line: Number(lineOnlyMatch[1]),
      column: 1,
      message: lineOnlyMatch[2],
      source,
    }
  }

  return {
    line: 1,
    column: 1,
    message: text,
    source,
  }
}

function CodeEditorBoard({
  code,
  setCode,
  userLanguage,
  setUserLanguage,
  selectedExampleLanguage,
  languages,
  compilerErrors,
  linterErrors,
  hideLanguageSelect = false,
  readOnly = false,
  variant = "default",
  highlightLine = null,
}) {
  const isStudent = variant === "student"
  const editorRef = useRef(null)
  const monacoRef = useRef(null)
  const failDecorationRef = useRef([])

  const diagnostics = useMemo(() => {
    const compilerDiagnostics = (compilerErrors || []).map((error) => parseDiagnostic(error, "Compiler"))
    const lintDiagnostics = (linterErrors || []).map((error) => parseDiagnostic(error, "Lint"))
    return [...compilerDiagnostics, ...lintDiagnostics]
  }, [compilerErrors, linterErrors])

  useEffect(() => {
    if (!editorRef.current || !monacoRef.current) {
      return
    }

    const model = editorRef.current.getModel()
    if (!model) {
      return
    }

    const markers = diagnostics.map((diagnostic) => ({
      startLineNumber: diagnostic.line,
      startColumn: diagnostic.column,
      endLineNumber: diagnostic.line,
      endColumn: Math.max(diagnostic.column + 1, diagnostic.column),
      message: `[${diagnostic.source}] ${diagnostic.message}`,
      severity: monacoRef.current.MarkerSeverity.Error,
    }))

    monacoRef.current.editor.setModelMarkers(model, "code-trainer", markers)
  }, [diagnostics, code, userLanguage])

  useEffect(() => {
    const editor = editorRef.current
    const monaco = monacoRef.current
    if (!editor || !monaco || !isStudent) {
      return
    }

    const line = Number(highlightLine)
    if (!Number.isFinite(line) || line < 1) {
      failDecorationRef.current = editor.deltaDecorations(failDecorationRef.current, [])
      return
    }

    failDecorationRef.current = editor.deltaDecorations(failDecorationRef.current, [
      {
        range: new monaco.Range(line, 1, line, 1),
        options: {
          isWholeLine: true,
          className: "student-editor-line-fail",
          linesDecorationsClassName: "student-editor-line-fail-gutter",
        },
      },
    ])
  }, [highlightLine, code, isStudent])

  const handleEditorWillMount = (monaco) => {
    monaco.editor.defineTheme("gray800", {
      base: "vs-dark",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#1f2937",
        "editorGutter.background": "#1f2937",
        "editorLineNumber.foreground": "#6b7280",
        "editorLineNumber.activeForeground": "#d1d5db",
        "editor.lineHighlightBackground": "#111827",
        "editor.lineHighlightBorder": "#111827",
        "minimap.background": "#1f2937",
        "editorOverviewRuler.background": "#1f2937",
        "editorOverviewRuler.border": "#1f2937",
      },
    })
    if (isStudent) {
      applyStudentMonacoSyntax(monaco, userLanguage)
    }
    monaco.editor.setTheme(isStudent ? "studentSurface" : "gray800")
  }

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor
    monacoRef.current = monaco
    monaco.editor.setTheme(isStudent ? "studentSurface" : "gray800")
  }

  const themeName = isStudent ? "studentSurface" : "gray800"
  const monacoLanguage = getMonacoLanguage(userLanguage)

  useEffect(() => {
    if (!isStudent || !monacoRef.current) {
      return
    }
    applyStudentMonacoSyntax(monacoRef.current, userLanguage)
    const model = editorRef.current?.getModel()
    if (model && model.getLanguageId() !== monacoLanguage) {
      monacoRef.current.editor.setModelLanguage(model, monacoLanguage)
    }
  }, [isStudent, userLanguage, monacoLanguage])

  return (
    <div
      className={
        isStudent
          ? "student-code-editor flex min-h-0 flex-1 flex-col overflow-hidden bg-[#141a24] font-mono scrollbar-dark"
          : "flex min-h-0 flex-1 flex-col overflow-hidden rounded bg-[#1f2937] font-mono text-sm scrollbar-dark"
      }
    >
      {!hideLanguageSelect && (
        <div className="p-3 border-b border-gray-700 flex items-center justify-between gap-3">
          <select
            className="w-40 p-1 rounded bg-gray-700 text-white font-mono text-sm border border-gray-600 cursor-pointer hover:bg-gray-600 focus:outline-none focus:ring-1 focus:ring-slate-400 focus:border-slate-400 transition-colors"
            value={userLanguage}
            onChange={(e) => setUserLanguage(e.target.value)}
          >
            {languages.map((lang) => (
              <option key={lang} value={lang} disabled={lang === selectedExampleLanguage}>
                {lang.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="flex-1 min-h-0 overflow-x-auto scrollbar-dark">
        <Editor
          key={isStudent ? `student-${monacoLanguage}` : "default"}
          className="monaco-editor-scrollbar-dark"
          height="100%"
          language={monacoLanguage}
          value={code}
          onChange={(value) => setCode(value || "")}
          beforeMount={handleEditorWillMount}
          onMount={handleEditorDidMount}
          theme={themeName}
          options={{
            readOnly,
            fontSize: isStudent ? 13.5 : 14,
            fontFamily: "var(--mono), Consolas, 'Courier New', monospace",
            fontLigatures: false,
            "semanticHighlighting.enabled": !isStudent,
            minimap: { enabled: false },
            overviewRulerLanes: 0,
            overviewRulerBorder: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: isStudent ? 4 : 2,
            insertSpaces: true,
            padding: isStudent ? { top: 12, bottom: 12 } : { top: 16 },
            wordWrap: "on",
            glyphMargin: true,
            lineNumbersMinChars: isStudent ? 2 : 3,
            renderLineHighlight: "all",
            ...(isStudent
              ? {
                  lineHeight: 24,
                  indentSize: 4,
                  detectIndentation: false,
                }
              : {}),
            scrollbar: {
              vertical: "visible",
              horizontal: "hidden",
              horizontalScrollbarSize: 0,
              verticalScrollbarSize: 12,
              verticalHasArrows: false,
              arrowSize: 0,
              useShadows: false,
            },
          }}
        />
      </div>
    </div>
  )
}

export default CodeEditorBoard
