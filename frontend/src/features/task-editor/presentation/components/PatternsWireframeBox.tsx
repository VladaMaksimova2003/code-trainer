import { PATTERN_CATALOG } from "@/features/task-editor/domain/patternCatalog"
import type { Pattern } from "@/features/task-editor/domain/entities"
import { AnalysisStatus } from "@/features/task-editor/domain/enums"

type Props = {
  patterns: Pattern[]
  analysisStatus: AnalysisStatus | null
  acceptAllChecked: boolean
  onAcceptAllChange: (checked: boolean) => void
  onTogglePattern: (id: string, approved: boolean) => void
  onSearchPatterns: () => void
  isSearching: boolean
}

const wireBtn =
  "w-full border-2 border-gray-800 rounded bg-white text-gray-900 px-2 py-2 text-sm font-medium"

export function PatternsWireframeBox({
  patterns,
  analysisStatus,
  acceptAllChecked,
  onAcceptAllChange,
  onTogglePattern,
  onSearchPatterns,
  isSearching,
}: Props) {
  const display =
    patterns.length > 0 ? patterns : PATTERN_CATALOG.map((p) => ({ ...p, approved: false }))

  return (
    <div className="space-y-2">
      <div className="border-2 border-gray-800 rounded-md bg-gray-50 p-3 min-h-[140px]">
        <p className="text-xs font-semibold text-gray-800 mb-2 uppercase tracking-wide">
          Patterns
        </p>
        <div className="flex flex-wrap gap-1.5">
          {display.map((p) => {
            const on = p.approved !== false
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => onTogglePattern(p.id, !on)}
                className={`px-2 py-0.5 text-xs border-2 border-gray-800 rounded ${
                  on ? "bg-gray-800 text-white" : "bg-white text-gray-800"
                }`}
              >
                {p.label}
                {p.confidence < 1 && analysisStatus === AnalysisStatus.READY
                  ? ` ${Math.round(p.confidence * 100)}%`
                  : ""}
              </button>
            )
          })}
        </div>
        <label className="mt-3 flex items-center gap-2 text-sm text-gray-800 cursor-pointer">
          <input
            type="checkbox"
            className="w-4 h-4 border-2 border-gray-800"
            checked={acceptAllChecked}
            onChange={(e) => onAcceptAllChange(e.target.checked)}
          />
          Accept all
        </label>
      </div>

      <button
        type="button"
        disabled={isSearching}
        onClick={onSearchPatterns}
        className={`${wireBtn} hover:bg-gray-100 disabled:opacity-60`}
      >
        {isSearching ? "Поиск паттернов…" : "search for patterns"}
      </button>

      <p className="text-[11px] text-gray-600 leading-snug">
        Комбинированный подход: преподаватель загружает код, программа анализирует и
        показывает найденное. Далее — «Accept all» или ручной выбор паттернов.
      </p>
    </div>
  )
}
