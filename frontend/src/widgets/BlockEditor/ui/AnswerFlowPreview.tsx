import { useMemo } from "react"
import ReactFlow, {
  Background,
  Handle,
  MarkerType,
  Position,
  ReactFlowProvider,
  useReactFlow,
} from "react-flow-renderer"
import "react-flow-renderer/dist/style.css"
import { getStarterGraph } from "@/widgets/BlockEditor/lib/flowTemplates"
import { FLOWCHART_BLOCKS } from "@/widgets/BlockEditor/lib/flowchartBlockConfig"
import FlowchartBlockBody from "@/widgets/BlockEditor/ui/FlowchartBlockBody"

const DEFAULT_MARKER_END = {
  type: MarkerType.ArrowClosed,
  color: "#cbd5e1",
  width: 20,
  height: 20,
}

const DEFAULT_EDGE_STYLE = {
  stroke: "#94a3b8",
  strokeWidth: 1.75,
}

const HANDLE_STYLE = {
  width: 10,
  height: 10,
  background: "rgba(255,255,255,0.01)",
  border: "none",
  opacity: 0,
}

function enrichEdges(edges) {
  return (edges || []).map((edge) => ({
    ...edge,
    style: { ...DEFAULT_EDGE_STYLE, ...edge.style },
    markerEnd: edge.markerEnd && edge.markerEnd.type ? edge.markerEnd : DEFAULT_MARKER_END,
  }))
}

function PreviewNode({ data }) {
  return (
    <div className="relative inline-block">
      <Handle id="target" type="target" position={Position.Top} style={HANDLE_STYLE} isConnectable={false} />
      <Handle id="source" type="source" position={Position.Bottom} style={HANDLE_STYLE} isConnectable={false} />
      <FlowchartBlockBody
        type={data.type || "process"}
        text={data.label}
        selected={false}
        isArmedSource={false}
        cursorStyle="cursor-default"
      />
    </div>
  )
}

function FlowPreviewToolbar({ onHide }) {
  const { zoomIn, zoomOut, fitView } = useReactFlow()

  return (
    <div className="absolute right-2 top-2 z-10 flex items-center gap-1">
      <button
        type="button"
        title="Уменьшить"
        onClick={() => zoomOut({ duration: 150 })}
        className="flex h-7 w-7 items-center justify-center rounded-md border border-gray-600 bg-gray-800/90 text-[15px] font-medium text-gray-200 transition hover:border-gray-500 hover:bg-gray-700"
      >
        −
      </button>
      <button
        type="button"
        title="Увеличить"
        onClick={() => zoomIn({ duration: 150 })}
        className="flex h-7 w-7 items-center justify-center rounded-md border border-gray-600 bg-gray-800/90 text-[15px] font-medium text-gray-200 transition hover:border-gray-500 hover:bg-gray-700"
      >
        +
      </button>
      <button
        type="button"
        title="Вписать в экран"
        onClick={() => fitView({ padding: 0.15, duration: 200 })}
        className="flex h-7 w-7 items-center justify-center rounded-md border border-gray-600 bg-gray-800/90 text-[11px] font-semibold text-gray-200 transition hover:border-gray-500 hover:bg-gray-700"
      >
        ⊡
      </button>
      {onHide && (
        <button
          type="button"
          title="Скрыть блок-схему"
          onClick={onHide}
          className="ml-1 flex h-7 w-7 items-center justify-center rounded-md border border-gray-600 bg-gray-800/90 text-[15px] text-gray-300 transition hover:border-red-400/50 hover:bg-gray-700 hover:text-red-300"
        >
          ×
        </button>
      )}
    </div>
  )
}

function teacherFlowToPreviewGraph(flow) {
  if (!flow || !Array.isArray(flow.nodes) || flow.nodes.length === 0) {
    return null
  }

  const nodes = flow.nodes.map((node, index) => ({
    id: String(node.id || index + 1),
    type: "typedBlock",
    position: node.position || { x: 180 + (index % 3) * 220, y: 80 + Math.floor(index / 3) * 150 },
    data: {
      label: node.text || FLOWCHART_BLOCKS[node.type]?.defaultText || `Узел ${index + 1}`,
      type: node.type || "process",
    },
  }))

  const edges = enrichEdges(
    Array.isArray(flow.edges)
      ? flow.edges.map((edge, index) => ({
          id: edge.id || `e${index + 1}`,
          source: String(edge.source),
          target: String(edge.target),
        }))
      : [],
  )

  return { nodes, edges }
}

function AnswerFlowPreviewCanvas({ taskId, flow, onHide }) {
  const graph = useMemo(() => {
    const fromTeacher = teacherFlowToPreviewGraph(flow)
    if (fromTeacher) return fromTeacher

    const starter = getStarterGraph(taskId)
    return {
      nodes: starter.nodes || [],
      edges: enrichEdges(starter.edges),
    }
  }, [flow, taskId])
  const nodeTypes = useMemo(() => ({ typedBlock: PreviewNode }), [])

  return (
    <div className="answer-flow-preview relative h-full min-h-0 overflow-hidden rounded-lg border border-gray-700 bg-gray-900">
      <ReactFlow
        nodes={graph.nodes}
        edges={graph.edges}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={{
          animated: true,
          style: DEFAULT_EDGE_STYLE,
          markerEnd: DEFAULT_MARKER_END,
        }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        zoomOnScroll
        zoomOnPinch
        zoomOnDoubleClick={false}
        panOnDrag
        panOnScroll={false}
        minZoom={0.25}
        maxZoom={2.5}
        preventScrolling={false}
        fitView
        fitViewOptions={{ padding: 0.15 }}
      >
        <Background variant="dots" gap={18} size={1} />
        <FlowPreviewToolbar onHide={onHide} />
      </ReactFlow>
    </div>
  )
}

export default function AnswerFlowPreview({ taskId, flow = null, onHide }) {
  return (
    <ReactFlowProvider>
      <AnswerFlowPreviewCanvas taskId={taskId} flow={flow} onHide={onHide} />
    </ReactFlowProvider>
  )
}
