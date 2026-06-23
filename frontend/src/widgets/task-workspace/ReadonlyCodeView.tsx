import CodeBlockView from "@/widgets/task-workspace/CodeBlockView"

interface ReadonlyCodeViewProps {
  code?: string
  language?: string
  flagLine?: number | null
}

export default function ReadonlyCodeView({
  code = "",
  language = "python",
  flagLine = null,
}: ReadonlyCodeViewProps) {
  return <CodeBlockView code={code} language={language} flagLine={flagLine} />
}
