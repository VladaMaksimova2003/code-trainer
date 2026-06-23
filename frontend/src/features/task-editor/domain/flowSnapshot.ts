export type FlowSnapshot = {
  flow?: unknown[]
  nodes?: unknown[]
  edges?: unknown[]
}

export function serializeFlowSnapshot(flow: FlowSnapshot | undefined | null): string {
  if (!flow) return '{"flow":[],"nodes":[],"edges":[]}'
  return JSON.stringify({
    flow: flow.flow ?? [],
    nodes: flow.nodes ?? [],
    edges: flow.edges ?? [],
  })
}

export function flowsEqual(
  a: FlowSnapshot | undefined | null,
  b: FlowSnapshot | undefined | null
): boolean {
  return serializeFlowSnapshot(a) === serializeFlowSnapshot(b)
}
