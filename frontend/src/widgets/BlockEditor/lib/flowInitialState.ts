import { FLOWCHART_BLOCKS } from "@/widgets/BlockEditor/lib/flowchartBlockConfig"
import {
  getFlowchartMode,
  hasTeacherDiagramInTask,
  isCodeToFlowchartTask,
} from "@/features/task-solving/model/studentUiUtils"
import type { FlowPayload } from "@/shared/types/flow"
import type { TaskDto } from "@/shared/types/task"

/** Bump when code>flowchart starter or flow_spec validation changes ? invalidates old drafts. */
export const CODE_TO_FLOWCHART_STARTER_VERSION = 2

/** True when the student has not drawn anything yet (empty draft / fresh task). */
export function isFlowEmpty(flow: FlowPayload | unknown[] | null | undefined): boolean {
  if (flow == null) return true
  if (Array.isArray(flow)) return flow.length === 0
  if (typeof flow !== "object") return true

  const record = flow as FlowPayload
  const nodes = record.nodes
  const steps = record.flow
  if (Array.isArray(nodes) && nodes.length > 0) return false
  if (Array.isArray(steps) && steps.length > 0) return false
  return true
}

interface StarterNode {
  id: string | number
  type?: string
  text?: string
  data?: { type?: string; label?: string }
  position?: { x: number; y: number }
}

interface StarterGraph {
  nodes: StarterNode[]
  edges: { id?: string | number; source: string | number; target: string | number; label?: string }[]
}

function serializeStarterGraph(graph: StarterGraph): FlowPayload {
  const nodes = graph.nodes.map((node) => ({
    id: node.id,
    type: node.data?.type || node.type || "process",
    text: node.data?.label || node.text || "",
    position: node.position,
  }))

  const edges = graph.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label,
  }))

  const flowSteps = nodes.map((node) => ({
    id: node.id,
    type: node.type,
    text: node.text,
  }))

  return { flow: flowSteps, nodes, edges }
}

/** Empty canvas for flowchart > code (reference diagram is shown separately). */
export function getEmptyFlowPayload(): FlowPayload {
  return { flow: [], nodes: [], edges: [] }
}

/** Minimal scaffold for code > flowchart: only Start and End, no solution blocks. */
export function getMinimalFlowScaffoldGraph(): StarterGraph {
  return {
    nodes: [
      {
        id: "1",
        type: "start",
        text: FLOWCHART_BLOCKS.start.defaultText,
        position: { x: 260, y: 60 },
      },
      {
        id: "2",
        type: "end",
        text: FLOWCHART_BLOCKS.end.defaultText,
        position: { x: 260, y: 280 },
      },
    ],
    edges: [],
  }
}

/** Key stored in draft ? when it changes, student flow draft is discarded. */
export function getFlowDraftKey(task: TaskDto | null | undefined): string {
  if (!isCodeToFlowchartTask(task)) return ""
  const fs = (task?.flow_spec || {}) as Record<string, unknown>
  return JSON.stringify({
    starter: CODE_TO_FLOWCHART_STARTER_VERSION,
    mode: getFlowchartMode(task),
    required_sequence: fs.required_sequence || [],
    required_text_checks: fs.required_text_checks || [],
    allow_extra_nodes: fs.allow_extra_nodes ?? null,
    require_loop_back_edge: fs.require_loop_back_edge ?? null,
  })
}

/** Initial student flow: empty for diagram>code; minimal scaffold for code>flowchart. */
export function getStudentFlowStarterPayload(task: TaskDto | null | undefined): FlowPayload {
  if (!task || hasTeacherDiagramInTask(task)) {
    return getEmptyFlowPayload()
  }
  if (isCodeToFlowchartTask(task)) {
    return serializeStarterGraph(getMinimalFlowScaffoldGraph())
  }
  return getEmptyFlowPayload()
}

/** Resolve flow from localStorage draft or task starter. */
export function resolveStudentFlowFromDraft(
  task: TaskDto | null | undefined,
  draftFlow: FlowPayload | null | undefined,
  draft: { flowDraftKey?: string } | null | undefined,
): FlowPayload {
  const defaultFlow = getStudentFlowStarterPayload(task)

  if (!draftFlow || isFlowEmpty(draftFlow)) {
    return defaultFlow
  }

  const flowDraftKey = getFlowDraftKey(task)
  if (flowDraftKey && draft?.flowDraftKey !== flowDraftKey) {
    return defaultFlow
  }

  return draftFlow
}

/** Hint above BlockEditor for code > flowchart tasks. */
export function getComposeFlowchartHint(task: TaskDto | null | undefined): string | null {
  if (!isCodeToFlowchartTask(task)) return null
  return "????????? ????-????? ?? Pascal-???? ?????. ?????????? ????? ?? ?????? ? ????????? ?? ?????????."
}
