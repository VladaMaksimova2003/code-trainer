import type { ReactNode } from "react"
import {
  configPanelFrameClass,
  configPanelSurfaceClass,
  executionPanelFrameClass,
  executionPanelSurfaceClass,
} from "@/features/task-editor/presentation/components/plaqueStyles"

type PanelVariant = "config" | "execution"

type Props = {
  header?: ReactNode
  children: ReactNode
  variant?: PanelVariant
}

export function AssignmentPanelShell({
  header,
  children,
  variant = "config",
}: Props) {
  const frameClass =
    variant === "execution" ? executionPanelFrameClass : configPanelFrameClass
  const surfaceClass =
    variant === "execution"
      ? executionPanelSurfaceClass
      : configPanelSurfaceClass

  return (
    <div className="flex min-h-[320px] w-full min-w-0 flex-col lg:min-h-0 lg:flex-1">
      <div className={frameClass}>
        {header && (
          <div className={`te-panel-head shrink-0 px-6 ${surfaceClass}`}>
            {header}
          </div>
        )}
        <div
          className={
            variant === "execution"
              ? "flex min-h-0 flex-1 flex-col overflow-hidden px-6 pb-6 pt-6"
              : `min-h-0 flex-1 overflow-x-hidden overflow-y-auto px-6 pb-6 pt-10 scrollbar-editor-config`
          }
        >
          {children}
        </div>
      </div>
    </div>
  )
}
