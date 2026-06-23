type FlowNode = {
  id?: string
  type?: string
  text?: string
  data?: { type?: string; label?: string }
}

type FlowEdge = {
  source?: string
  target?: string
}

const BLOCK_LABELS: Record<string, string> = {
  start: "Начало",
  end: "Конец",
  input: "Ввод",
  process: "Действие",
  decision: "Условие",
  loop: "Цикл",
  output: "Вывод",
}

function nodeType(node: FlowNode): string {
  return String(node.type || node.data?.type || "").trim().toLowerCase()
}

function blockLabel(type: string): string {
  return BLOCK_LABELS[type] || type
}

/** Structural checks for teacher-authored flowcharts (block types + graph). */
export function validateFlowchartStructure(
  flow: { nodes?: FlowNode[]; edges?: FlowEdge[] } | undefined,
): string[] {
  const nodes = Array.isArray(flow?.nodes) ? flow.nodes : []
  const edges = Array.isArray(flow?.edges) ? flow.edges : []
  const errors: string[] = []

  if (!nodes.length) {
    errors.push("Добавьте блок-схему")
    return errors
  }

  const types = nodes.map(nodeType)
  if (!types.includes("start")) {
    errors.push("Добавьте блок «Начало»")
  }
  if (!types.includes("end")) {
    errors.push("Добавьте блок «Конец»")
  }

  if (!edges.length) {
    if (nodes.length > 1) {
      errors.push("Соедините блоки стрелками")
    }
    return errors
  }

  const nodeById = new Map(nodes.map((node, index) => [String(node.id || index + 1), node]))
  const adjacency = new Map<string, string[]>()
  for (const edge of edges) {
    const source = String(edge.source || "")
    const target = String(edge.target || "")
    if (!source || !target || !nodeById.has(target)) continue
    const list = adjacency.get(source) || []
    list.push(target)
    adjacency.set(source, list)
  }

  const startNode = nodes.find((node) => nodeType(node) === "start")
  const startId = startNode ? String(startNode.id) : ""
  const visited = new Set<string>()

  if (startId) {
    const queue = [startId]
    while (queue.length) {
      const current = queue.shift()!
      if (visited.has(current)) continue
      visited.add(current)
      for (const target of adjacency.get(current) || []) {
        if (!visited.has(target)) queue.push(target)
      }
    }
  }

  const disconnected = nodes.filter((node, index) => {
    const id = String(node.id || index + 1)
    return startId ? !visited.has(id) : false
  })
  if (disconnected.length) {
    errors.push(
      `Есть несоединённые блоки: ${disconnected.map((node) => blockLabel(nodeType(node))).join(", ")}`,
    )
  }

  const endReachable = nodes.some(
    (node) => nodeType(node) === "end" && visited.has(String(node.id || "")),
  )
  if (types.includes("end") && startId && !endReachable) {
    errors.push("Блок «Конец» не связан со стартом — проверьте стрелки")
  }

  for (const node of nodes) {
    const id = String(node.id || "")
    if (startId && !visited.has(id)) continue

    const type = nodeType(node)
    const outgoing = adjacency.get(id) || []

    if (type === "decision" && outgoing.length < 2) {
      errors.push("У блока «Условие» должно быть две ветви (да и нет)")
    }
    if (type !== "end" && !outgoing.length) {
      errors.push(`Блок «${blockLabel(type)}» не ведёт дальше — добавьте стрелку`)
    }
  }

  return errors
}
