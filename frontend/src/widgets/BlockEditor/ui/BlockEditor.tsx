import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react"
import ReactFlow, {
  addEdge,
  Background,
  Handle,
  MarkerType,
  Position,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from "react-flow-renderer"
import "react-flow-renderer/dist/style.css"
import { getMinimalFlowScaffoldGraph } from "@/widgets/BlockEditor/lib/flowInitialState"
import { getStarterGraph } from "@/widgets/BlockEditor/lib/flowTemplates"
import {
  buildFlowPayload,
  flowPayloadSignature,
} from "@/widgets/BlockEditor/lib/flowPayload"
import FlowchartBlockBody from "@/widgets/BlockEditor/ui/FlowchartBlockBody"
import FlowchartPalette from "@/widgets/BlockEditor/ui/FlowchartPalette"
import { FLOWCHART_BLOCKS } from "@/widgets/BlockEditor/lib/flowchartBlockConfig"

const DEFAULT_MARKER_END = {
  type: MarkerType.ArrowClosed,
  color: "#9aa6b6",
  width: 8,
  height: 8,
}

const DEFAULT_EDGE_STYLE = {
  stroke: "#9aa6b6",
  strokeWidth: 1.6,
}

const SELECTED_EDGE_STYLE = {
  stroke: "#8eff01",
  strokeWidth: 2,
}

function normalizeLoadedEdge(edge) {
  return {
    ...edge,
    animated: edge.animated !== false,
    style: { ...DEFAULT_EDGE_STYLE, ...edge.style },
    markerEnd: edge.markerEnd && edge.markerEnd.type ? edge.markerEnd : DEFAULT_MARKER_END,
  }
}

function portHandleStyle(color, active) {
  return {
    width: 12,
    height: 12,
    borderRadius: "50%",
    background: active ? color : "#0a0e15",
    border: `1.6px solid ${color}`,
    opacity: 1,
    boxShadow: active ? `0 0 0 4px ${color}33` : "none",
    zIndex: 3,
  }
}

function TypedBlockNode({ id, data, selected, isConnectable }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(data.label || "")

  useEffect(() => {
    setDraft(data.label || "")
  }, [data.label])

  const blockType = data.type || "process"
  const cfg = FLOWCHART_BLOCKS[blockType] || FLOWCHART_BLOCKS.process
  const handleStyle = portHandleStyle(cfg.color, selected)

  const commitEdit = () => {
    const next = draft.trim() || cfg.defaultText
    data.onLabelChange?.(id, next)
    setEditing(false)
  }

  return (
    <div
      className="relative inline-block"
      onDoubleClick={(event) => {
        event.stopPropagation()
        if (!data.readOnly) setEditing(true)
      }}
    >
      <Handle id="target" type="target" position={Position.Top} style={handleStyle} isConnectable={isConnectable} />
      <Handle
        id="target-left"
        type="target"
        position={Position.Left}
        style={handleStyle}
        isConnectable={isConnectable}
      />
      <Handle
        id="target-right"
        type="target"
        position={Position.Right}
        style={handleStyle}
        isConnectable={isConnectable}
      />
      <Handle id="source" type="source" position={Position.Bottom} style={handleStyle} isConnectable={isConnectable} />
      <Handle
        id="source-left"
        type="source"
        position={Position.Left}
        style={handleStyle}
        isConnectable={isConnectable}
      />
      <Handle
        id="source-right"
        type="source"
        position={Position.Right}
        style={handleStyle}
        isConnectable={isConnectable}
      />

      {editing ? (
        <div
          className="relative flex items-center justify-center"
          style={{ width: cfg.width, height: cfg.height }}
          onMouseDown={(event) => event.stopPropagation()}
        >
          <input
            autoFocus
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onBlur={commitEdit}
            onKeyDown={(event) => {
              if (event.key === "Enter") commitEdit()
              if (event.key === "Escape") {
                setDraft(data.label || "")
                setEditing(false)
              }
            }}
            className="pointer-events-auto w-[88%] rounded border border-lime/50 bg-bg-2 px-2 py-0.5 font-mono text-[12.5px] text-ink focus:outline-none"
          />
        </div>
      ) : (
        <FlowchartBlockBody
          type={blockType}
          text={data.label}
          selected={selected}
          cursorStyle={data.readOnly ? "cursor-default" : "cursor-grab active:cursor-grabbing"}
        />
      )}
    </div>
  )
}

function fromFlow(payload, taskId, { minimalScaffold = false } = {}) {
  const graphPayload = Array.isArray(payload) ? { flow: payload } : payload || {}

  if (graphPayload.nodes && Array.isArray(graphPayload.nodes) && graphPayload.nodes.length > 0) {
    const nodes = graphPayload.nodes.map((node, index) => ({
      id: String(node.id || index + 1),
      type: "typedBlock",
      position: node.position || { x: 180 + (index % 3) * 240, y: 100 + Math.floor(index / 3) * 170 },
      data: {
        label: node.text || FLOWCHART_BLOCKS[node.type]?.defaultText || `Узел ${index + 1}`,
        type: node.type || "process",
      },
    }))

    const edges = Array.isArray(graphPayload.edges)
      ? graphPayload.edges.map((edge, index) =>
          normalizeLoadedEdge({
            id: edge.id || `e${index + 1}`,
            source: String(edge.source),
            target: String(edge.target),
            label: edge.label,
            animated: edge.animated !== false,
          }),
        )
      : []

    return { nodes, edges }
  }

  const starterGraph = minimalScaffold
    ? getMinimalFlowScaffoldGraph()
    : typeof taskId === "number" || typeof taskId === "string"
      ? getStarterGraph(Number(taskId))
      : null

  const nodesSrc = starterGraph?.nodes?.length
    ? starterGraph.nodes.map((node) =>
        node.type === "typedBlock"
          ? node
          : {
              id: String(node.id),
              type: "typedBlock",
              position: node.position || { x: 260, y: 60 },
              data: {
                label: node.data?.label || node.text || FLOWCHART_BLOCKS[node.type]?.defaultText || "",
                type: node.data?.type || node.type || "process",
              },
            },
      )
    : [
        {
          id: "1",
          type: "typedBlock",
          position: { x: 260, y: 60 },
          data: { label: FLOWCHART_BLOCKS.start.defaultText, type: "start" },
        },
        {
          id: "2",
          type: "typedBlock",
          position: { x: 260, y: 340 },
          data: { label: FLOWCHART_BLOCKS.end.defaultText, type: "end" },
        },
      ]

  const edgesSrc = starterGraph?.edges?.length
    ? starterGraph.edges
    : []

  const nodes = [...nodesSrc]

  const edges = edgesSrc.map((edge, index) =>
    normalizeLoadedEdge({
      ...edge,
      id: edge.id || `e${index + 1}`,
    }),
  )

  return { nodes, edges }
}

function BlockEditorCanvas({
  flow,
  setFlow,
  taskId,
  readOnly = false,
  showModeHint = true,
  hintText = null,
  minimalScaffold = false,
  onResetScaffold = null,
  registerGetPayload = null,
}) {
  const parsed = useMemo(() => fromFlow(flow, taskId, { minimalScaffold }), [flow, taskId, minimalScaffold])
  const [nodes, setNodes, onNodesChange] = useNodesState(parsed.nodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(parsed.edges)
  const [selectedNodeId, setSelectedNodeId] = useState(null)
  const idRef = useRef(parsed.nodes.length + 1)
  const setFlowRef = useRef(setFlow)
  const reactFlowWrapper = useRef(null)
  const { project } = useReactFlow()
  const lastEmittedSignatureRef = useRef(flowPayloadSignature(buildFlowPayload(parsed.nodes, parsed.edges)))

  setFlowRef.current = setFlow

  useLayoutEffect(() => {
    const payload = buildFlowPayload(nodes, edges)
    registerGetPayload?.(() => buildFlowPayload(nodes, edges))
    const signature = flowPayloadSignature(payload)
    if (signature === lastEmittedSignatureRef.current) {
      return
    }
    lastEmittedSignatureRef.current = signature
    setFlowRef.current(payload)
  }, [nodes, edges, registerGetPayload])

  const updateNodeLabel = useCallback(
    (nodeId, label) => {
      setNodes((prev) =>
        prev.map((node) => (node.id === nodeId ? { ...node, data: { ...node.data, label } } : node)),
      )
    },
    [setNodes],
  )

  const deleteNodeById = useCallback(
    (nodeId) => {
      setNodes((prev) => prev.filter((node) => node.id !== nodeId))
      setEdges((prev) => prev.filter((edge) => edge.source !== nodeId && edge.target !== nodeId))
      setSelectedNodeId((prev) => (prev === nodeId ? null : prev))
    },
    [setEdges, setNodes],
  )

  const displayNodes = useMemo(
    () =>
      nodes.map((node) => ({
        ...node,
        draggable: !readOnly,
        selectable: !readOnly,
        data: {
          ...node.data,
          readOnly,
          onLabelChange: updateNodeLabel,
        },
      })),
    [nodes, readOnly, updateNodeLabel],
  )

  const displayEdges = useMemo(
    () =>
      edges.map((edge) => ({
        ...edge,
        style: edge.selected ? { ...SELECTED_EDGE_STYLE } : { ...DEFAULT_EDGE_STYLE },
        markerEnd: edge.selected
          ? { type: MarkerType.ArrowClosed, color: "#8eff01", width: 8, height: 8 }
          : DEFAULT_MARKER_END,
      })),
    [edges],
  )

  const nodeTypes = useMemo(() => ({ typedBlock: TypedBlockNode }), [])

  const onConnect = useCallback(
    (params) => {
      if (readOnly) return
      setEdges((prev) =>
        addEdge(
          {
            ...params,
            animated: true,
            style: DEFAULT_EDGE_STYLE,
            markerEnd: DEFAULT_MARKER_END,
          },
          prev,
        ),
      )
    },
    [readOnly, setEdges],
  )

  const addNodeAt = useCallback(
    (blockType, position) => {
      const cfg = FLOWCHART_BLOCKS[blockType]
      if (!cfg) return
      const id = String(idRef.current++)
      setNodes((prev) => [
        ...prev,
        {
          id,
          type: "typedBlock",
          position: {
            x: Math.max(8, position.x - cfg.width / 2),
            y: Math.max(8, position.y - cfg.height / 2),
          },
          data: { label: cfg.defaultText, type: blockType },
        },
      ])
    },
    [setNodes],
  )

  const onDragOver = useCallback((event) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = "move"
  }, [])

  const onDrop = useCallback(
    (event) => {
      if (readOnly) return
      event.preventDefault()
      const blockType = event.dataTransfer.getData("flowchart/block-type")
      if (!blockType || !FLOWCHART_BLOCKS[blockType]) return

      const bounds = reactFlowWrapper.current?.getBoundingClientRect()
      if (!bounds) return

      const position = project({
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top,
      })
      addNodeAt(blockType, position)
    },
    [addNodeAt, project, readOnly],
  )

  const clearGraph = () => {
    if (minimalScaffold) {
      const parsed = fromFlow({}, taskId, { minimalScaffold: true })
      setNodes(parsed.nodes)
      setEdges(parsed.edges)
      setSelectedNodeId(null)
      return
    }
    setNodes([])
    setEdges([])
    setSelectedNodeId(null)
  }

  const deleteSelectedNode = useCallback(() => {
    if (!selectedNodeId) return
    deleteNodeById(selectedNodeId)
  }, [deleteNodeById, selectedNodeId])

  useEffect(() => {
    const isTypingTarget = (target) => {
      if (!(target instanceof HTMLElement)) return false
      const tag = target.tagName?.toLowerCase()
      if (tag === "input" || tag === "textarea" || tag === "select") return true
      if (target.isContentEditable) return true
      return Boolean(target.closest("[contenteditable='true']"))
    }

    const onKeyDown = (event) => {
      if (readOnly || isTypingTarget(event.target)) return
      if ((event.key === "Delete" || event.key === "Backspace") && selectedNodeId) {
        deleteNodeById(selectedNodeId)
      }
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [selectedNodeId, deleteNodeById, readOnly])

  return (
    <div className="flex h-full min-h-[460px] flex-col bg-bg-2">
      {showModeHint ? (
        <div className="flex shrink-0 items-center gap-2 border-b border-border bg-surface/40 px-4 py-2.5">
          {onResetScaffold ? (
            <button
              type="button"
              onClick={onResetScaffold}
              className="shrink-0 rounded-md border border-border bg-surface-2 px-2.5 py-1 text-[11px] font-medium text-ink-muted transition hover:border-lime/40 hover:text-ink"
            >
              Сбросить черновик
            </button>
          ) : (
            <div className="flex-1" />
          )}
          <p className="max-w-[720px] flex-1 text-center text-[11.5px] leading-snug text-ink-faint">
            {hintText || "Нарисуй алгоритм блок-схемой"}
          </p>
          <div className="w-[120px]" />
        </div>
      ) : null}

      <div className="grid min-h-0 flex-1 grid-cols-[200px_1fr]">
        <FlowchartPalette
          onClear={clearGraph}
          onDeleteSelected={deleteSelectedNode}
          hasSelection={Boolean(selectedNodeId)}
          readOnly={readOnly}
        />

        <div
          ref={reactFlowWrapper}
          className="relative h-full min-h-[320px] overflow-hidden bg-bg-2"
          style={{
            backgroundImage: "radial-gradient(rgba(255,255,255,.05) 1px, transparent 1.5px)",
            backgroundSize: "18px 18px",
          }}
        >
          <ReactFlow
            nodes={displayNodes}
            edges={displayEdges}
            nodeTypes={nodeTypes}
            onNodesChange={readOnly ? undefined : onNodesChange}
            onEdgesChange={readOnly ? undefined : onEdgesChange}
            onConnect={onConnect}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodesDraggable={!readOnly}
            nodesConnectable={!readOnly}
            elementsSelectable={!readOnly}
            connectionMode="loose"
            defaultEdgeOptions={{
              animated: true,
              style: DEFAULT_EDGE_STYLE,
              markerEnd: DEFAULT_MARKER_END,
            }}
            onNodeClick={(_, node) => {
              if (!readOnly) setSelectedNodeId(node.id)
            }}
            onPaneClick={() => setSelectedNodeId(null)}
            fitView
            className="flowchart-canvas"
          >
            <Background variant="dots" gap={18} size={1} color="rgba(255,255,255,0.05)" />
          </ReactFlow>

          {nodes.length === 0 ? (
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <p className="text-[14px] text-ink-muted">Перетащи блок из палитры слева</p>
                <p className="mt-1 text-[12px] text-ink-faint">или начни с «Начало»</p>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}

export default function BlockEditor({
  flow,
  setFlow,
  taskId,
  readOnly = false,
  showModeHint = true,
  hintText = null,
  minimalScaffold = false,
  onResetScaffold = null,
  registerGetPayload = null,
}) {
  return (
    <ReactFlowProvider>
      <BlockEditorCanvas
        flow={flow}
        setFlow={setFlow}
        taskId={taskId}
        readOnly={readOnly}
        showModeHint={showModeHint}
        hintText={hintText}
        minimalScaffold={minimalScaffold}
        onResetScaffold={onResetScaffold}
        registerGetPayload={registerGetPayload}
      />
    </ReactFlowProvider>
  )
}
