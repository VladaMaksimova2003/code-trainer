import { BLOCK_EDITOR_LINE_HEIGHT } from "@/widgets/BlockEditor/lib/blockEditorOverlay"

export const ASSEMBLY_MONACO_THEME = "tpAssembly"

export function defineAssemblyMonacoTheme(monaco) {
  monaco.editor.defineTheme(ASSEMBLY_MONACO_THEME, {
    base: "vs-dark",
    inherit: true,
    rules: [],
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
  monaco.editor.setTheme(ASSEMBLY_MONACO_THEME)
}

export const assemblyMonacoOptions = {
  fontSize: 14,
  lineHeight: BLOCK_EDITOR_LINE_HEIGHT,
  fontFamily: '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
  fontLigatures: false,
  minimap: { enabled: false },
  overviewRulerLanes: 0,
  overviewRulerBorder: false,
  scrollBeyondLastLine: true,
  automaticLayout: true,
  tabSize: 4,
  insertSpaces: true,
  padding: { top: 12, bottom: 12 },
  wordWrap: "off",
  lineNumbers: "on",
  glyphMargin: false,
  renderLineHighlight: "line",
  scrollbar: {
    vertical: "visible",
    horizontal: "auto",
    verticalScrollbarSize: 12,
    useShadows: false,
  },
}
