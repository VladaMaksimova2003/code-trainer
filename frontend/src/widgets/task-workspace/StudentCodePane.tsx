import CodeEditorBoard from "@/widgets/CodeEditorBoard/ui/CodeEditorBoard"
import ReadonlyCodeView from "@/widgets/task-workspace/ReadonlyCodeView"
import type { PanelError } from "@/shared/types/execution"

interface StudentCodePaneProps {
  side: "known" | "learning" | string
  language: string
  code: string
  onChange?: (code: string) => void
  readOnly?: boolean
  compilerErrors?: PanelError[]
  linterErrors?: PanelError[]
  highlightLine?: number | null
  languages?: string[]
  onLanguageChange?: (language: string) => void
  blockedLanguage?: string
}

export default function StudentCodePane({
  side,
  language,
  code,
  onChange,
  readOnly = false,
  compilerErrors = [],
  linterErrors = [],
  highlightLine = null,
  languages = [],
  onLanguageChange,
  blockedLanguage,
}: StudentCodePaneProps) {
  const isLearning = side === "learning"

  return (
    <div
      className={`flex min-h-0 flex-col h-full ${side === "known" ? "border-r border-border" : ""}`}
    >
      <div
        className={`flex-1 min-h-0 overflow-hidden ${isLearning ? "bg-[#141a24]" : "bg-[#141a24]"} ${
          readOnly ? "overflow-auto" : ""
        }`}
      >
        {readOnly ? (
          <ReadonlyCodeView code={code} language={language} />
        ) : (
          <div className="flex h-full min-h-0 flex-col">
            <CodeEditorBoard
              code={code}
              setCode={onChange ?? (() => {})}
              userLanguage={language}
              setUserLanguage={onLanguageChange ?? (() => {})}
              selectedExampleLanguage={blockedLanguage}
              languages={languages}
              compilerErrors={compilerErrors}
              linterErrors={linterErrors}
              highlightLine={highlightLine}
              hideLanguageSelect
              readOnly={false}
              variant="student"
            />
          </div>
        )}
      </div>
    </div>
  )
}
