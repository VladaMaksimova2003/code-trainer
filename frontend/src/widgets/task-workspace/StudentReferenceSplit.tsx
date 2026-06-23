import type { ReactNode } from "react"
import ReadonlyCodeView from "@/widgets/task-workspace/ReadonlyCodeView"

interface StudentReferenceSplitProps {
  referenceLanguage: string
  referenceCode: string | null | undefined
  referenceMissing?: boolean
  referenceMissingLabel?: string | null
  children: ReactNode
  header?: ReactNode | null
}

export default function StudentReferenceSplit({
  referenceLanguage,
  referenceCode,
  referenceMissing = false,
  referenceMissingLabel = null,
  children,
  header = null,
}: StudentReferenceSplitProps) {
  const showMissing =
    referenceMissing || referenceCode == null || String(referenceCode).trim() === ""

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      {header}
      <div className="grid min-h-0 flex-1 grid-cols-2 grid-rows-1">
        <div className="min-h-0 overflow-auto border-r border-border bg-[#141a24]">
          {showMissing ? (
            <div className="flex h-full items-center justify-center p-6 text-center text-sm text-ink-muted">
              {referenceMissingLabel || "Эталонный код для выбранного языка не задан."}
            </div>
          ) : (
            <ReadonlyCodeView code={referenceCode} language={referenceLanguage} />
          )}
        </div>
        <div className="flex min-h-0 flex-col overflow-hidden bg-surface">{children}</div>
      </div>
    </div>
  )
}
