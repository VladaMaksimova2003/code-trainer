import { useEffect, useState } from "react"
import { PlusIcon, XMarkIcon } from "@heroicons/react/24/outline"
import {
  IoValueKind,
  type IoValue,
  createEmptyIoValue,
} from "@/features/task-editor/domain/ioValue"
import {
  editorButton,
  listValueAddBtnClass,
  listValueRemoveBtnClass,
} from "@/features/task-editor/presentation/components/plaqueStyles"

type Props = {
  label: string
  value: IoValue
  onChange: (next: IoValue) => void
  variant?: "light" | "dark"
  /** Тип поля задаётся схемой задания (селекторы — в блоке «Тестовые случаи») */
  expectedKind: IoValueKind
}

function lightNeutralBtn() {
  return "inline-flex items-center justify-center rounded-md border border-border-strong bg-surface-2 px-3 py-2 text-sm font-medium text-ink transition hover:border-lime/50 hover:text-lime"
}

function newListRowKey() {
  return `row-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function MultiLineValueEditor({
  lines,
  onLinesChange,
  inputClass,
}: {
  lines: string[]
  onLinesChange: (lines: string[]) => void
  inputClass: string
}) {
  const [rowKeys, setRowKeys] = useState<string[]>(() =>
    lines.map(() => newListRowKey()),
  )

  useEffect(() => {
    setRowKeys((prev) => {
      if (prev.length === lines.length) return prev
      if (prev.length < lines.length) {
        const added = Array.from(
          { length: lines.length - prev.length },
          () => newListRowKey(),
        )
        return [...prev, ...added]
      }
      return prev.slice(0, lines.length)
    })
  }, [lines.length])

  const insertAfter = (idx: number) => {
    const insertAt = idx + 1
    setRowKeys((prev) => {
      const keys = [...prev]
      keys.splice(insertAt, 0, newListRowKey())
      return keys
    })
    onLinesChange([
      ...lines.slice(0, insertAt),
      "",
      ...lines.slice(insertAt),
    ])
  }

  const removeAt = (idx: number) => {
    const nextLines = lines.filter((_, i) => i !== idx)
    const normalized = nextLines.length ? nextLines : [""]
    setRowKeys((prev) => {
      const keys = prev.filter((_, i) => i !== idx)
      return keys.length ? keys : [newListRowKey()]
    })
    onLinesChange(normalized)
  }

  return (
    <div className="flex w-full flex-col gap-3">
      {lines.map((line, idx) => (
        <div key={rowKeys[idx] ?? idx} className="flex w-full items-center gap-2">
          <input
            className={`${inputClass} min-w-0 flex-1`}
            value={line}
            placeholder={`Значение ${idx + 1}`}
            onChange={(e) => {
              const next = [...lines]
              next[idx] = e.target.value
              onLinesChange(next)
            }}
          />
          <button
            type="button"
            className={listValueRemoveBtnClass}
            aria-label="Удалить значение"
            onClick={() => removeAt(idx)}
          >
            <XMarkIcon className="h-4 w-4" strokeWidth={2} />
          </button>
          <button
            type="button"
            className={listValueAddBtnClass}
            aria-label="Добавить значение после текущего"
            onClick={() => insertAfter(idx)}
          >
            <PlusIcon className="h-4 w-4" strokeWidth={2} />
          </button>
        </div>
      ))}
    </div>
  )
}

export function IoValueEditor({
  label,
  value,
  onChange,
  variant = "light",
  expectedKind,
}: Props) {
  const isDark = variant === "dark"

  const display =
    value.kind === expectedKind ? value : createEmptyIoValue(expectedKind)

  useEffect(() => {
    if (value.kind !== expectedKind) {
      onChange(createEmptyIoValue(expectedKind))
    }
  }, [expectedKind, value.kind, onChange])

  const inputClass = isDark
    ? "tp-input w-full font-mono"
    : "w-full rounded-md border border-border-strong bg-bg-2 px-3 py-2 text-sm font-mono text-ink outline-none focus:border-lime focus:ring-2 focus:ring-lime/10"
  const labelClass = isDark
    ? "text-xs text-ink-faint"
    : "text-xs font-medium text-ink-muted"

  const neutralBtn = isDark ? editorButton("default") : lightNeutralBtn()
  const jsonFmtBtn = isDark
    ? editorButton("primary")
    : `${lightNeutralBtn()} border-purple/50 text-purple`
  const matrixCtrl = neutralBtn

  return (
    <div className="mb-4 flex flex-col gap-3">
      <span className={labelClass}>{label}</span>

      {display.kind === IoValueKind.SCALAR && (
        <input
          type="text"
          className={`${inputClass} h-10`}
          placeholder="Значение"
          value={display.text ?? ""}
          onChange={(e) => onChange({ ...display, text: e.target.value })}
        />
      )}

      {display.kind === IoValueKind.MULTI && (
        <MultiLineValueEditor
          lines={display.lines ?? [""]}
          inputClass={inputClass}
          onLinesChange={(lines) => onChange({ ...display, lines })}
        />
      )}

      {display.kind === IoValueKind.MATRIX && (
        <MatrixGrid
          grid={display.grid ?? [["", ""]]}
          onChange={(grid) => onChange({ ...display, grid })}
          isDark={isDark}
          matrixCtrl={matrixCtrl}
        />
      )}

      {display.kind === IoValueKind.JSON && (
        <div className="flex flex-col gap-3">
          <textarea
            className={`${inputClass} min-h-[320px] resize-y`}
            value={display.jsonText ?? ""}
            onChange={(e) => onChange({ ...display, jsonText: e.target.value })}
          />
          <button
            type="button"
            className={jsonFmtBtn}
            onClick={() => {
              try {
                const formatted = JSON.stringify(
                  JSON.parse(display.jsonText || "{}"),
                  null,
                  2,
                )
                onChange({ ...display, jsonText: formatted })
              } catch {
                /* invalid json */
              }
            }}
          >
            Форматировать JSON
          </button>
        </div>
      )}
    </div>
  )
}

function MatrixGrid({
  grid,
  onChange,
  isDark,
  matrixCtrl,
}: {
  grid: string[][]
  onChange: (g: string[][]) => void
  isDark: boolean
  matrixCtrl: string
}) {
  const cols = grid[0]?.length ?? 1

  const updateCell = (r: number, c: number, val: string) => {
    const next = grid.map((row, ri) =>
      row.map((cell, ci) => (ri === r && ci === c ? val : cell)),
    )
    onChange(next)
  }

  const addRow = () => onChange([...grid, Array(cols).fill("")])
  const addCol = () => onChange(grid.map((row) => [...row, ""]))
  const removeRow = () =>
    onChange(grid.length > 1 ? grid.slice(0, -1) : grid)
  const removeCol = () =>
    onChange(cols > 1 ? grid.map((row) => row.slice(0, -1)) : grid)

  const cellClass = isDark
    ? "w-16 rounded-md border border-border-strong bg-bg-2 px-2 py-2 text-center font-mono text-sm text-ink outline-none focus:border-lime"
    : "w-16 rounded-md border border-border-strong bg-bg-2 px-2 py-2 text-center font-mono text-sm text-ink"
  const wrapClass = isDark
    ? "mb-3 overflow-x-auto rounded-xl border border-border bg-surface-2 p-3"
    : "overflow-x-auto rounded-xl border border-border bg-surface p-3"

  return (
    <div className="flex flex-col gap-3">
      <div className={wrapClass}>
        <table className="border-collapse text-sm">
          <tbody>
            {grid.map((row, ri) => (
              <tr key={ri}>
                {row.map((cell, ci) => (
                  <td key={ci} className="p-1.5">
                    <input
                      className={cellClass}
                      value={cell}
                      onChange={(e) => updateCell(ri, ci, e.target.value)}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap justify-center gap-3">
        <button type="button" className={matrixCtrl} onClick={addRow}>
          + строка
        </button>
        <button type="button" className={matrixCtrl} onClick={addCol}>
          + столбец
        </button>
        <button type="button" className={matrixCtrl} onClick={removeRow}>
          − строка
        </button>
        <button type="button" className={matrixCtrl} onClick={removeCol}>
          − столбец
        </button>
      </div>
    </div>
  )
}
