/** Shared visual config for the student flowchart editor and answer preview. */
export const FLOWCHART_BLOCKS = {
  start: {
    label: "Начало",
    color: "#8eff01",
    fill: "rgba(142,255,1,.08)",
    defaultText: "Начало",
    shape: "pill",
    width: 130,
    height: 48,
  },
  input: {
    label: "Ввод",
    color: "#79d0ff",
    fill: "rgba(121,208,255,.08)",
    defaultText: "Ввести данные",
    shape: "paral",
    width: 170,
    height: 52,
  },
  process: {
    label: "Действие",
    color: "#8b53fe",
    fill: "rgba(139,83,254,.10)",
    defaultText: "Действие",
    shape: "rect",
    width: 170,
    height: 58,
  },
  decision: {
    label: "Условие",
    color: "#ffb43d",
    fill: "rgba(255,180,61,.08)",
    defaultText: "Условие?",
    shape: "diamond",
    width: 180,
    height: 100,
  },
  loop: {
    label: "Цикл",
    color: "#8b53fe",
    fill: "rgba(139,83,254,.10)",
    defaultText: "Пока условие…",
    shape: "hex",
    width: 170,
    height: 54,
  },
  output: {
    label: "Вывод",
    color: "#79d0ff",
    fill: "rgba(121,208,255,.08)",
    defaultText: "Вывести результат",
    shape: "paral-r",
    width: 170,
    height: 52,
  },
  end: {
    label: "Конец",
    color: "#ff4d6a",
    fill: "rgba(255,77,106,.08)",
    defaultText: "Конец",
    shape: "pill",
    width: 130,
    height: 48,
  },
}

export const FLOWCHART_BLOCK_ORDER = ["start", "input", "process", "decision", "loop", "output", "end"]

export function getFlowchartBlockConfig(type) {
  return FLOWCHART_BLOCKS[type] || FLOWCHART_BLOCKS.process
}

export function getFlowchartBlockBounds(type) {
  const cfg = getFlowchartBlockConfig(type)
  return { width: cfg.width, height: cfg.height }
}

export function getFlowchartNodeChrome(type, selected = false, armed = false) {
  const cfg = getFlowchartBlockConfig(type)
  return {
    color: cfg.color,
    fill: cfg.fill,
    boxShadow: selected
      ? `0 0 0 2px ${cfg.color}40`
      : armed
        ? `0 0 0 2px ${cfg.color}22`
        : "none",
  }
}
