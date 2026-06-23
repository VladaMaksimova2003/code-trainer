/** Shared code-block chip UI for flowchart palette chips. */

export function parseBlockIndent(blockText) {
  const match = blockText.match(/^([ \t]*)(.*)$/s)
  if (!match) return { code: blockText, indentLevel: 0, indentStr: "" }
  const indentStr = match[1]
  const tabSize = 4
  const indentLevel =
    indentStr.replace(/\t/g, " ".repeat(tabSize)).length / tabSize
  return { code: blockText, indentStr, indentLevel: Math.round(indentLevel) }
}

export const codeBlockBankClassName =
  "shrink-0 text-left px-2 py-1 rounded border border-cyan-500/40 bg-cyan-500/10 text-cyan-100 hover:bg-cyan-500/20 transition-colors max-w-[320px] cursor-grab active:cursor-grabbing"

export const codeBlockFrameClassName =
  "shrink-0 rounded border border-green-500/40 bg-green-500/10 text-green-100 px-2 py-1 cursor-grab active:cursor-grabbing max-w-[320px]"

/** Inline chip inside unified code document (no width cap, stays in text flow). */
export const codeBlockInlineFrameClassName =
  "inline-flex max-w-full align-baseline rounded border border-green-500/40 bg-green-500/10 text-green-100 px-2 py-1"

export const codeBlockTextClassName =
  "whitespace-pre-wrap break-words font-mono text-sm"

export function CodeBlockChip({
  content,
  variant = "bank",
  layout = "default",
  editable = false,
  draggable = false,
  onDragStart,
  onContentChange,
  onFocus,
  className = "",
}) {
  const { code } = parseBlockIndent(content)
  const shellClass =
    layout === "inline"
      ? codeBlockInlineFrameClassName
      : variant === "frame"
        ? codeBlockFrameClassName
        : codeBlockBankClassName

  const shellProps = {
    draggable: layout === "inline" ? false : draggable,
    className: `${shellClass} ${className}`.trim(),
    onFocus,
    onDragStart: draggable ? onDragStart : undefined,
    tabIndex: onFocus ? 0 : undefined,
  }

  const inner = editable ? (
    <textarea
      className={`${codeBlockTextClassName} ${
        layout === "inline"
          ? "inline-block min-w-[2ch] resize-none bg-transparent p-0 outline-none align-baseline"
          : "block w-full min-h-[1.5rem] resize-y bg-transparent p-0 outline-none"
      }`}
      value={content}
      onChange={(e) => onContentChange?.(e.target.value)}
      onFocus={onFocus}
      spellCheck={false}
      rows={layout === "inline" ? 1 : undefined}
    />
  ) : (
    <span className={codeBlockTextClassName}>{code}</span>
  )

  if (layout === "inline") {
    return <span {...shellProps}>{inner}</span>
  }

  return <div {...shellProps}>{inner}</div>
}
