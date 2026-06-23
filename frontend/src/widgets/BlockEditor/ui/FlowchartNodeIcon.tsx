import { getFlowchartBlockConfig } from "@/widgets/BlockEditor/lib/flowchartBlockConfig"

/** Mini shape preview for the flowchart palette (matches Claude design). */
export default function FlowchartNodeIcon({ type }) {
  const cfg = getFlowchartBlockConfig(type)
  const color = cfg.color

  return (
    <svg width="22" height="14" viewBox="0 0 22 14" aria-hidden>
      {cfg.shape === "pill" && (
        <rect x="0.5" y="0.5" width="21" height="13" rx="6.5" fill="none" stroke={color} strokeWidth="1.4" />
      )}
      {cfg.shape === "rect" && (
        <rect x="0.5" y="0.5" width="21" height="13" rx="2" fill="none" stroke={color} strokeWidth="1.4" />
      )}
      {cfg.shape === "diamond" && (
        <polygon points="11,1 21,7 11,13 1,7" fill="none" stroke={color} strokeWidth="1.4" />
      )}
      {cfg.shape === "paral" && (
        <polygon points="4,1 21,1 18,13 1,13" fill="none" stroke={color} strokeWidth="1.4" />
      )}
      {cfg.shape === "paral-r" && (
        <polygon points="1,1 18,1 21,13 4,13" fill="none" stroke={color} strokeWidth="1.4" />
      )}
      {cfg.shape === "hex" && (
        <polygon points="3,1 19,1 21,7 19,13 3,13 1,7" fill="none" stroke={color} strokeWidth="1.4" />
      )}
    </svg>
  )
}
