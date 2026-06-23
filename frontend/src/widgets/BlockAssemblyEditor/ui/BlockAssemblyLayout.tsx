import { useRef, type ComponentProps, type ReactNode } from "react"
import {
  DEFAULT_BANK_HEIGHT,
  MIN_BANK_HEIGHT,
  useBlockBankResize,
} from "@/widgets/BlockAssemblyEditor/lib/useBlockBankResize"
import { BlockAssemblyBank } from "@/widgets/BlockAssemblyEditor/ui/BlockAssemblyBank"

type BankProps = ComponentProps<typeof BlockAssemblyBank>

type Props = {
  solution: ReactNode
  bank: BankProps
}

export default function BlockAssemblyLayout({ solution, bank }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const { bankHeight, handleResizeStart, handleResizeReset, getMaxHeight } =
    useBlockBankResize(containerRef)

  return (
    <div ref={containerRef} className="flex min-h-0 flex-1 flex-col overflow-hidden">
      <div className="min-h-0 flex-1 overflow-y-auto bg-surface">{solution}</div>

      <div className="flex shrink-0 flex-col border-t border-border bg-bg">
        <div
          role="separator"
          aria-orientation="horizontal"
          aria-valuenow={bankHeight}
          aria-valuemin={MIN_BANK_HEIGHT}
          aria-valuemax={getMaxHeight()}
          title="Потяните вверх или вниз, чтобы изменить высоту банка блоков. Двойной клик — сброс."
          onMouseDown={handleResizeStart}
          onDoubleClick={handleResizeReset}
          className="group flex h-2 w-full shrink-0 cursor-ns-resize touch-none items-center justify-center hover:bg-surface/70 active:bg-surface"
        >
          <div className="h-1 w-10 rounded-full bg-ink-faint/35 transition group-hover:bg-ink-faint/60 group-active:bg-lime/70" />
        </div>

        <div
          className="min-h-0 overflow-y-auto"
          style={{
            height: bankHeight,
            minHeight: MIN_BANK_HEIGHT,
            maxHeight: getMaxHeight(),
          }}
        >
          <BlockAssemblyBank {...bank} embedded />
        </div>
      </div>
    </div>
  )
}

export { DEFAULT_BANK_HEIGHT }
