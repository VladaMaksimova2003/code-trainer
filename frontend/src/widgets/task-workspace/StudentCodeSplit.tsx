import StudentCodePane from "@/widgets/task-workspace/StudentCodePane"
import { StudentParallelLanguageBar } from "@/widgets/task-workspace/StudentLanguageBar"
import type { PanelError } from "@/shared/types/execution"

interface StudentCodeSplitProps {
  className?: string
  knownLanguage: string
  knownCode: string
  learningLanguage: string
  learnedCode: string
  setLearnedCode: (code: string) => void
  knownLanguages?: string[]
  learningLanguages?: string[]
  languages?: string[]
  onKnownLanguageChange?: (language: string) => void
  onLearningLanguageChange?: (language: string) => void
  onSwap?: () => void
  compilerErrors?: PanelError[]
  linterErrors?: PanelError[]
  highlightLine?: number | null
}

export default function StudentCodeSplit({
  className = "",
  knownLanguage,
  knownCode,
  learningLanguage,
  learnedCode,
  setLearnedCode,
  knownLanguages = [],
  learningLanguages = [],
  languages = [],
  onKnownLanguageChange,
  onLearningLanguageChange,
  onSwap,
  compilerErrors,
  linterErrors,
  highlightLine = null,
}: StudentCodeSplitProps) {
  return (
    <div className={`flex min-h-0 flex-1 flex-col ${className}`.trim()}>
      <StudentParallelLanguageBar
        knownLanguage={knownLanguage}
        learningLanguage={learningLanguage}
        knownLanguages={knownLanguages}
        learningLanguages={learningLanguages}
        languages={languages}
        onKnownLanguageChange={onKnownLanguageChange}
        onLearningLanguageChange={onLearningLanguageChange}
        onSwap={onSwap}
      />

      <div className="relative grid min-h-0 flex-1 grid-cols-2 grid-rows-1">
        <StudentCodePane
          side="known"
          language={knownLanguage}
          code={knownCode}
          readOnly
        />
        <StudentCodePane
          side="learning"
          language={learningLanguage}
          code={learnedCode}
          onChange={setLearnedCode}
          languages={learningLanguages.length ? learningLanguages : languages}
          onLanguageChange={onLearningLanguageChange}
          blockedLanguage={knownLanguage}
          compilerErrors={compilerErrors}
          linterErrors={linterErrors}
          highlightLine={highlightLine}
        />
      </div>
    </div>
  )
}
