/**
 * Flowchart payload and validation types for POST /flows/check and task.flow_spec.
 * Types only — no runtime exports.
 */

export type FlowBlockType =
  | "start"
  | "end"
  | "input"
  | "output"
  | "process"
  | "decision"
  | "loop"
  | string

export interface FlowPosition {
  x: number
  y: number
}

/** Step in legacy `flow[]` array sent to /flows/check. */
export interface FlowStep {
  id?: string | number
  type: FlowBlockType
  text?: string
}

/** Node in React Flow / API `nodes[]` array. */
export interface FlowNode {
  id: string | number
  type: FlowBlockType
  text?: string
  position?: FlowPosition
}

export interface FlowEdge {
  id?: string | number
  source: string | number
  target: string | number
  label?: string | null
}

/** Payload built by BlockEditor and sent to POST /flows/check. */
export interface FlowPayload {
  flow: FlowStep[]
  nodes: FlowNode[]
  edges: FlowEdge[]
}

export interface FlowTextCheck {
  type: FlowBlockType
  contains?: string
  contains_any?: string[]
}

export interface FlowSpec {
  allowed_blocks?: FlowBlockType[]
  required_sequence?: FlowBlockType[]
  required_text_checks?: FlowTextCheck[]
  allow_extra_nodes?: boolean
  require_loop_back_edge?: boolean
  student_reference_languages?: string[]
  primary_language?: string
  [key: string]: unknown
}

export interface FlowValidationError {
  type: string
  text: string
}

export interface FlowCheckDebug {
  node_count?: number
  edge_count?: number
  submitted_types?: string[]
  reachable_types?: string[]
  detected_sequence?: string
  expected_sequence?: string
  visited_node_count?: number
  disconnected_node_count?: number
  error_types?: string[]
  used_nodes_source?: string
  [key: string]: unknown
}

/** Response from POST /flows/check (sync path; mirrors CheckFlowResultDTO). */
export interface FlowCheckResult {
  success: boolean
  errors: FlowValidationError[]
  execution_results?: Record<string, unknown>[]
  test_cases?: Record<string, string>[]
  semantic_checked?: boolean
  execution_job_id?: string | null
  status?: string | null
  debug?: FlowCheckDebug | null
}

/** Request body for POST /flows/check. */
export interface FlowCheckRequest {
  task_id: number
  flow: FlowStep[]
  nodes?: FlowNode[]
  edges?: FlowEdge[]
}
