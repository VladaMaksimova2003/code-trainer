import { useState, type ReactNode } from "react"
import AnswerFlowPreview from "@/widgets/BlockEditor/ui/AnswerFlowPreview"
import type { FlowPayload } from "@/shared/types/flow"

interface StudentFlowchartSplitProps {
  taskId?: number | string
  referenceFlow?: FlowPayload | null
  showReference?: boolean
  referencePanel?: ReactNode | null
  workspacePanel?: ReactNode
  modeBar?: ReactNode | null
}

export default function StudentFlowchartSplit({
  taskId,
  referenceFlow = null,
  showReference = true,
  referencePanel,
  workspacePanel,
  modeBar = null,
}: StudentFlowchartSplitProps) {
  const [referenceVisible, setReferenceVisible] = useState(showReference)

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      {modeBar && (
        <div className="shrink-0 border-b border-border bg-surface/40">
          <div className={referenceVisible ? "grid grid-cols-2" : undefined}>
            <div
              className={`flex justify-center py-2.5 ${
                referenceVisible ? "col-span-2" : ""
              }`}
            >
              {modeBar}
            </div>
          </div>
        </div>
      )}
      <div
        className={`grid min-h-0 flex-1 grid-rows-1 ${
          referenceVisible ? "grid-cols-2" : "grid-cols-1"
        }`}
      >
        {referenceVisible && (
          <div className="flex min-h-0 flex-col overflow-hidden border-r border-border bg-[#141a24]">
            <div className="min-h-0 flex-1 p-2">
              {referencePanel || (
                <AnswerFlowPreview
                  taskId={taskId}
                  flow={referenceFlow}
                  onHide={() => setReferenceVisible(false)}
                />
              )}
            </div>
          </div>
        )}
        <div className="flex min-h-0 flex-col overflow-hidden bg-surface">
          {!referenceVisible && (
            <div className="shrink-0 border-b border-border bg-surface/40 px-4 py-2">
              <button
                type="button"
                onClick={() => setReferenceVisible(true)}
                className="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface-2 px-2.5 py-1 text-[12px] font-medium text-ink-muted transition hover:border-lime/40 hover:text-ink"
              >
                <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden>
                  <path
                    d="M2 3h5v5H2V3zm7 0h5v5H9V3zM2 10h5v3H2v-3zm7 0h5v3H9v-3z"
                    fill="currentColor"
                    opacity="0.7"
                  />
                </svg>
                Показать эталон
              </button>
            </div>
          )}
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden">{workspacePanel}</div>
        </div>
      </div>
    </div>
  )
}
