import { tokenizeCodeLine } from "@/widgets/BlockAssemblyEditor/lib/codeTokenizer"

interface TokLineProps {
  code: string
  language: string
}

function TokLine({ code, language }: TokLineProps) {
  const tokens = tokenizeCodeLine(code, language)
  return (
    <>
      {tokens.length === 0 ? (
        <span>&nbsp;</span>
      ) : (
        tokens.map((token, index) => (
          <span key={index} className={`tk-${token.c}`}>
            {token.t}
          </span>
        ))
      )}
    </>
  )
}

interface CodeBlockViewProps {
  code?: string
  language?: string
  flagLine?: number | null
  hlLine?: number | null
}

export default function CodeBlockView({
  code = "",
  language = "python",
  flagLine = null,
  hlLine = null,
}: CodeBlockViewProps) {
  const lines = String(code ?? "").split("\n")

  return (
    <pre className="font-mono text-[13.5px] leading-[1.75] py-3 m-0">
      {lines.map((line, index) => {
        const lineNo = index + 1
        const lineClass = [
          "code-line",
          flagLine === lineNo && "is-flag-fail",
          hlLine === lineNo && "is-flag-hl",
        ]
          .filter(Boolean)
          .join(" ")

        return (
          <div key={lineNo} className={lineClass}>
            <div className="ln">{lineNo}</div>
            <div className="whitespace-pre">
              <TokLine code={line} language={language} />
            </div>
          </div>
        )
      })}
    </pre>
  )
}
