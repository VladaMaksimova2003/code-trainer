import type { ReactNode } from "react"
import LoadingBlock from "@/shared/ui/LoadingBlock"

interface CurriculumStatesProps {
  loading: boolean
  error?: string | null
  empty?: boolean
  loadingText?: string
  onRetry?: () => void
  children: ReactNode
}

export default function CurriculumStates({
  loading,
  error,
  empty,
  loadingText = "Загрузка…",
  onRetry,
  children,
}: CurriculumStatesProps) {
  if (loading) {
    return <LoadingBlock text={loadingText} minHeight={240} />
  }
  if (error) {
    return (
      <div className="rounded-2xl border border-border bg-surface p-12 text-center">
        <div className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-2xl border border-danger/30 bg-danger/15 text-2xl text-danger">
          !
        </div>
        <p className="mb-1 text-[16px] font-semibold text-ink">Ошибка загрузки</p>
        <p className="mx-auto mb-5 max-w-sm text-[13.5px] text-ink-muted">{error}</p>
        {onRetry && (
          <button type="button" onClick={onRetry} className="btn btn-primary">
            ↻ Повторить
          </button>
        )}
      </div>
    )
  }
  if (empty) {
    return (
      <div className="rounded-2xl border border-border bg-surface p-12 text-center">
        <div className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-2xl border border-border bg-surface-2 text-2xl text-ink-faint">
          📚
        </div>
        <p className="mb-1 text-[16px] font-semibold text-ink">Пока пусто</p>
        <p className="mx-auto max-w-sm text-[13.5px] text-ink-muted">
          Здесь появятся материалы, как только они будут добавлены.
        </p>
      </div>
    )
  }
  return <>{children}</>
}
