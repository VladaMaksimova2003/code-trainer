import { tokenizeCodeLine } from "@/widgets/BlockAssemblyEditor/lib/codeTokenizer"
import { isWhitespaceOnlyText } from "@/domain/blockAssembly/blockScaffold"
import { formatBlockDisplayText } from "@/domain/blockAssembly"

export function FixedCodeTokens({ text, language }) {
  if (isWhitespaceOnlyText(text)) {
    return <span className="whitespace-pre">{text}</span>
  }
  const tokens = tokenizeCodeLine(text, language)
  return (
    <>
      {tokens.map((token, index) => (
        <span key={`${index}-${token.c}`} className={`tk-${token.c}`}>
          {token.t}
        </span>
      ))}
    </>
  )
}

export function TemplateSlot({ blockText, onDragOver, onDrop, onClear, compact = false }) {
  const filled = blockText != null && blockText !== ""
  const displayText = filled ? formatBlockDisplayText(String(blockText)) : ""
  const multiline = filled && displayText.includes("\n")

  return (
    <span
      onDragOver={onDragOver}
      onDrop={onDrop}
      onClick={() => {
        if (filled) onClear?.()
      }}
      className={[
        "mx-0.5 cursor-pointer rounded-md px-2 py-0.5 font-mono text-[13.5px] transition",
        multiline
          ? "inline-block max-w-[min(100%,28rem)] align-top text-left"
          : "inline-flex min-w-[64px] items-center justify-center",
        filled
          ? "border border-border-2 bg-surface-3 text-ink hover:border-danger/60 hover:bg-danger-soft hover:text-danger"
          : compact
            ? "min-w-[1ch] border border-transparent bg-transparent px-0 text-transparent hover:border-lime/40 hover:bg-lime/5"
            : "border border-dashed border-border-2 bg-bg-2 text-ink-faint hover:border-lime/50 hover:bg-surface-2",
      ].join(" ")}
      title={filled ? "Клик — убрать" : "Перетащи сюда блок"}
    >
      {filled ? (
        <span className={multiline ? "whitespace-pre-wrap" : "whitespace-pre"}>
          {displayText}
        </span>
      ) : compact ? (
        "\u00a0"
      ) : (
        "___"
      )}
    </span>
  )
}
