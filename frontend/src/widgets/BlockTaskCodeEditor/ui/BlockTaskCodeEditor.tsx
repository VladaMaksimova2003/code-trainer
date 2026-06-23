import { useCallback, useEffect, useRef } from "react"
import Editor from "@monaco-editor/react"
import {
  addBlockRangeFromSelection,
  expandSelectionToCoveringBlocks,
  findRangesIntersectingSelection,
  removeBlockRanges,
  applyModelChangesToRanges,
  normalizeRanges,
  rangesOverlap,
  resolveBlockConversionSpan,
} from "@/domain/codeBlockRanges"
import { isIgnorableRange, trimRangeEdges } from "@/domain/codeInputNormalize"
import {
  collectScaffoldGapRanges,
  isFullyBlockedExceptWhitespace,
} from "@/domain/blockAssembly/blockScaffold"
import {
  BLOCK_EDITOR_LINE_HEIGHT,
  computeBlockOverlayRects,
  ensureBlockOverlayLayer,
  expandRectToOverlayBox,
  renderBlockOverlayLayer,
} from "@/widgets/BlockEditor/lib/blockEditorOverlay"
import {
  ASSEMBLY_MONACO_THEME,
  assemblyMonacoOptions,
  defineAssemblyMonacoTheme,
} from "@/widgets/BlockAssemblyEditor/lib/blockAssemblyMonaco"
import { getMonacoLanguage } from "@/shared/config/languages"

function changesFromMonacoEvent(event) {
  return event.changes.map((c) => ({
    rangeOffset: c.rangeOffset,
    rangeLength: c.rangeLength,
    text: c.text,
  }))
}

function BlockTaskCodeEditor({
  code,
  blockRanges,
  language,
  onChange,
  onConvertStateChange,
  className = "",
}) {
  const editorRef = useRef(null)
  const monacoRef = useRef(null)
  const overlayLayerRef = useRef(null)
  const textDecorationIdsRef = useRef([])
  const scaffoldDecorationIdsRef = useRef([])
  const selectionPreviewIdsRef = useRef([])
  const blockRangesRef = useRef(blockRanges)
  const codeRef = useRef(code)
  const isApplyingExternalRef = useRef(false)

  blockRangesRef.current = blockRanges
  codeRef.current = code

  const emitChange = useCallback(
    (nextCode, nextRanges) => {
      onChange({
        code: nextCode,
        blockRanges: normalizeRanges(nextRanges, nextCode),
      })
    },
    [onChange],
  )

  const updateBlockOverlays = useCallback(() => {
    const editor = editorRef.current
    const monaco = monacoRef.current
    if (!editor || !monaco) return

    const model = editor.getModel()
    if (!model) return

    const layer =
      overlayLayerRef.current ?? ensureBlockOverlayLayer(editor)
    if (!layer) return
    overlayLayerRef.current = layer

    const editorCode = model.getValue()
    const ranges = normalizeRanges(blockRangesRef.current, editorCode)

    const lineHeight = editor.getOption(
      monaco.editor.EditorOption.lineHeight,
    )

    const boxes = ranges.flatMap((range) => {
      const rects = computeBlockOverlayRects(editor, model, range)
      if (rects.length === 0) return []
      return rects.map((rect) => ({
        key: range.id,
        ...expandRectToOverlayBox(rect, lineHeight),
      }))
    })

    renderBlockOverlayLayer(layer, boxes, {
      onBlockClick: (box, event) => {
        const range = ranges.find((item) => item.id === box.key)
        const editor = editorRef.current
        const monaco = monacoRef.current
        const model = editor?.getModel()
        if (!range || !editor || !monaco || !model) return

        event.preventDefault()
        event.stopPropagation()

        const startPos = model.getPositionAt(range.start)
        const endPos = model.getPositionAt(range.end)
        const blockSelection = new monaco.Selection(
          startPos.lineNumber,
          startPos.column,
          endPos.lineNumber,
          endPos.column,
        )

        if (event.shiftKey) {
          const current = editor.getSelection()
          if (current && !current.isEmpty()) {
            const mergedStart = Math.min(
              model.getOffsetAt(current.getStartPosition()),
              range.start,
            )
            const mergedEnd = Math.max(
              model.getOffsetAt(current.getEndPosition()),
              range.end,
            )
            const expanded = expandSelectionToCoveringBlocks(
              ranges,
              mergedStart,
              mergedEnd,
              editorCode,
            )
            const from = model.getPositionAt(expanded.start)
            const to = model.getPositionAt(expanded.end)
            editor.setSelection(
              new monaco.Selection(
                from.lineNumber,
                from.column,
                to.lineNumber,
                to.column,
              ),
            )
          } else {
            editor.setSelection(blockSelection)
          }
        } else {
          editor.setSelection(blockSelection)
        }

        editor.focus()
        requestAnimationFrame(() => updateBlockOverlays())
      },
    })

    const selection = editor.getSelection()
    const selStart = model.getOffsetAt(selection.getStartPosition())
    const selEnd = model.getOffsetAt(selection.getEndPosition())
    const selectionEmpty = selStart === selEnd
    const activeSpan = selectionEmpty
      ? findRangesIntersectingSelection(ranges, selStart, selEnd)[0] ?? null
      : null
    const previewBounds =
      selectionEmpty && activeSpan
        ? { start: activeSpan.start, end: activeSpan.end }
        : findRangesIntersectingSelection(ranges, selStart, selEnd).length > 0
          ? expandSelectionToCoveringBlocks(ranges, selStart, selEnd, editorCode)
          : resolveBlockConversionSpan(editorCode, ranges, selStart, selEnd)
    const { start: previewStart, end: previewEnd } = trimRangeEdges(
      editorCode,
      previewBounds.start,
      previewBounds.end,
    )
    const previewCandidate = { id: "", start: previewStart, end: previewEnd }
    const overlapsExisting =
      !selectionEmpty &&
      !activeSpan &&
      ranges.some((range) => rangesOverlap(range, previewCandidate))
    const canPreview =
      previewStart < previewEnd &&
      !isIgnorableRange(editorCode, previewStart, previewEnd) &&
      (selectionEmpty ? Boolean(activeSpan) : !overlapsExisting)

    const selectionDecorations = canPreview
      ? [
          {
            range: new monaco.Range(
              model.getPositionAt(previewStart).lineNumber,
              model.getPositionAt(previewStart).column,
              model.getPositionAt(previewEnd).lineNumber,
              model.getPositionAt(previewEnd).column,
            ),
            options: {
              inlineClassName: "monaco-block-selection-preview",
              stickiness:
                monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
            },
          },
        ]
      : []

    selectionPreviewIdsRef.current = editor.deltaDecorations(
      selectionPreviewIdsRef.current,
      selectionDecorations,
    )

    const textDecorations = ranges.map((range) => {
      const start = model.getPositionAt(range.start)
      const end = model.getPositionAt(range.end)
      return {
        range: new monaco.Range(
          start.lineNumber,
          start.column,
          end.lineNumber,
          end.column,
        ),
        options: {
          inlineClassName: "monaco-block-range-text",
          stickiness:
            monaco.editor.TrackedRangeStickiness
              .NeverGrowsWhenTypingAtEdges,
        },
      }
    })

    textDecorationIdsRef.current = editor.deltaDecorations(
      textDecorationIdsRef.current,
      textDecorations,
    )

    const fullyBlocked = isFullyBlockedExceptWhitespace(editorCode, ranges)
    const scaffoldDecorations = fullyBlocked
      ? []
      : collectScaffoldGapRanges(editorCode, ranges).map((gap) => {
          const start = model.getPositionAt(gap.start)
          const end = model.getPositionAt(gap.end)
          return {
            range: new monaco.Range(
              start.lineNumber,
              start.column,
              end.lineNumber,
              end.column,
            ),
            options: {
              inlineClassName: "monaco-scaffold-placeholder",
              stickiness:
                monaco.editor.TrackedRangeStickiness
                  .NeverGrowsWhenTypingAtEdges,
            },
          }
        })

    scaffoldDecorationIdsRef.current = editor.deltaDecorations(
      scaffoldDecorationIdsRef.current,
      scaffoldDecorations,
    )
  }, [])

  const readSelectionOffsets = useCallback(() => {
    const editor = editorRef.current
    const model = editor?.getModel()
    if (!editor || !model) {
      return { start: 0, end: 0, isEmpty: true }
    }
    const selection = editor.getSelection()
    const start = model.getOffsetAt(selection.getStartPosition())
    const end = model.getOffsetAt(selection.getEndPosition())
    return { start, end, isEmpty: start === end }
  }, [])

  const publishConvertState = useCallback(() => {
    const { start, end, isEmpty } = readSelectionOffsets()
    const ranges = blockRangesRef.current

    const editor = editorRef.current
    const model = editor?.getModel()
    const codeText = model?.getValue() ?? ""
    const selStart = Math.min(start, end)
    const selEnd = Math.max(start, end)
    const conversionSpan = resolveBlockConversionSpan(
      codeText,
      ranges,
      selStart,
      selEnd,
    )
    const blockStart = conversionSpan.start
    const blockEnd = conversionSpan.end
    const selectionCandidate = { id: "", start: blockStart, end: blockEnd }
    const overlapsBlock = ranges.some((r) => rangesOverlap(r, selectionCandidate))
    const cursorInBlock = isEmpty && findRangesIntersectingSelection(ranges, start, end).length > 0

    const canConvertToBlock =
      !cursorInBlock &&
      !isIgnorableRange(codeText, blockStart, blockEnd) &&
      !overlapsBlock
    const canConvertToCode =
      isEmpty
        ? cursorInBlock
        : findRangesIntersectingSelection(ranges, start, end).length > 0

    onConvertStateChange?.({
      canConvertToBlock,
      canConvertToCode,
      convertToBlock: () => {
        const editor = editorRef.current
        const model = editor?.getModel()
        if (!editor || !model) return

        const sel = readSelectionOffsets()
        const text = model.getValue()
        const nextRanges = addBlockRangeFromSelection(
          blockRangesRef.current,
          sel.start,
          sel.end,
          text,
        )
        emitChange(text, nextRanges)
        requestAnimationFrame(() => updateBlockOverlays())
        publishConvertState()
      },
      convertToCode: () => {
        const editor = editorRef.current
        const model = editor?.getModel()
        if (!editor || !model) return

        const sel = readSelectionOffsets()
        const expanded = expandSelectionToCoveringBlocks(
          blockRangesRef.current,
          sel.start,
          sel.end,
          model.getValue(),
        )
        const toRemove = findRangesIntersectingSelection(
          blockRangesRef.current,
          expanded.start,
          expanded.end,
        )
        if (toRemove.length === 0) return

        const text = model.getValue()
        const nextRanges = removeBlockRanges(
          blockRangesRef.current,
          toRemove.map((r) => r.id),
        )
        emitChange(text, nextRanges)
        requestAnimationFrame(() => updateBlockOverlays())
        publishConvertState()
      },
    })
  }, [
    emitChange,
    onConvertStateChange,
    readSelectionOffsets,
    updateBlockOverlays,
  ])

  useEffect(() => {
    updateBlockOverlays()
  }, [blockRanges, code, updateBlockOverlays])

  useEffect(() => {
    publishConvertState()
  }, [blockRanges, code, publishConvertState])

  const handleEditorWillMount = (monaco) => {
    defineAssemblyMonacoTheme(monaco)
  }

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor
    monacoRef.current = monaco
    overlayLayerRef.current = ensureBlockOverlayLayer(editor)

    const scheduleOverlayUpdate = () => {
      requestAnimationFrame(() => updateBlockOverlays())
    }

    editor.onDidChangeCursorSelection(() => {
      publishConvertState()
      scheduleOverlayUpdate()
    })

    editor.onDidScrollChange(scheduleOverlayUpdate)
    editor.onDidLayoutChange(scheduleOverlayUpdate)
    editor.onDidChangeModelContent((event) => {
      if (isApplyingExternalRef.current) return

      const model = editor.getModel()
      if (!model) return

      const nextCode = model.getValue()
      const nextRanges = applyModelChangesToRanges(
        blockRangesRef.current,
        changesFromMonacoEvent(event),
        nextCode,
      )

      codeRef.current = nextCode
      blockRangesRef.current = nextRanges
      emitChange(nextCode, nextRanges)
      scheduleOverlayUpdate()
    })

    scheduleOverlayUpdate()
    publishConvertState()
  }

  useEffect(() => {
    const editor = editorRef.current
    const model = editor?.getModel()
    if (!editor || !model) return

    const current = model.getValue()
    if (current !== code) {
      isApplyingExternalRef.current = true
      editor.executeEdits("external-sync", [
        {
          range: model.getFullModelRange(),
          text: code,
        },
      ])
      isApplyingExternalRef.current = false
      requestAnimationFrame(() => updateBlockOverlays())
    }
  }, [code, updateBlockOverlays])

  return (
    <div
      className={`block-task-code-editor flex h-full min-h-0 flex-col overflow-hidden bg-surface ${className}`.trim()}
    >
      <div className="min-h-0 flex-1">
        <Editor
          className="monaco-editor-scrollbar-dark block-task-monaco h-full"
          height="100%"
          language={getMonacoLanguage(language)}
          value={code}
          onChange={() => {
            /* handled in onDidChangeModelContent */
          }}
          beforeMount={handleEditorWillMount}
          onMount={handleEditorDidMount}
          theme={ASSEMBLY_MONACO_THEME}
          options={{
            ...assemblyMonacoOptions,
            scrollBeyondLastLine: false,
          }}
        />
      </div>
    </div>
  )
}

export default BlockTaskCodeEditor
