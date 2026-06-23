/** Serialize React Flow nodes/edges into API payload for /flows/check. */

export function serializeFlowNodes(nodes) {
  return nodes.map((node) => ({
    id: node.id,
    type: node.data?.type || "process",
    text: node.data?.label || "",
    position: node.position,
  }))
}

export function serializeFlowEdges(edges) {
  return edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label,
  }))
}

export function toApiFlowSteps(nodes, edges) {
  if (!nodes.length) {
    return []
  }

  const outgoing = new Map()
  for (const edge of edges) {
    const list = outgoing.get(edge.source) || []
    list.push(edge.target)
    outgoing.set(edge.source, list)
  }

  const sorted = [...nodes].sort((a, b) => a.position.x - b.position.x)
  const startNode = sorted.find((node) => node.data?.type === "start") || sorted[0]
  const visited = new Set()
  const result = []
  let current = startNode
  let guard = 0
  const maxSteps = Math.max(nodes.length * 4, 12)

  while (current && guard < maxSteps) {
    guard += 1
    visited.add(current.id)
    result.push({
      id: current.id,
      type: current.data?.type || "process",
      text: current.data?.label || "",
    })

    const targets = outgoing.get(current.id) || []
    const nextTarget = targets.find((target) => !visited.has(target)) || targets[0]
    if (!nextTarget) break
    current = nodes.find((node) => node.id === nextTarget)
    if (!current) break
    if (visited.has(current.id) && targets.length <= 1) break
  }

  return result
}

export function buildFlowPayload(nodes, edges) {
  return {
    flow: toApiFlowSteps(nodes, edges),
    nodes: serializeFlowNodes(nodes),
    edges: serializeFlowEdges(edges),
  }
}

export function flowPayloadSignature(payload) {
  return JSON.stringify({
    flow: payload.flow,
    nodes: payload.nodes,
    edges: payload.edges,
  })
}

export function summarizeFlowPayload(payload) {
  const nodes = payload?.nodes || []
  const edges = payload?.edges || []
  const types = nodes.map((node) => String(node.type || "process").toLowerCase())
  return {
    nodeCount: nodes.length,
    edgeCount: edges.length,
    blockTypes: types,
    nodeTexts: nodes.map((node) => node.text || ""),
  }
}
