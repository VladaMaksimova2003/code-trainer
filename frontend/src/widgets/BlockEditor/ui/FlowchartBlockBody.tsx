import {
  getFlowchartBlockConfig,
  getFlowchartNodeChrome,
} from "@/widgets/BlockEditor/lib/flowchartBlockConfig"

function ShapeFrame({ cfg, chrome }) {
  const shell = {
    position: "absolute",
    inset: 0,
    boxShadow: chrome.boxShadow,
  }

  if (cfg.shape === "pill") {
    return (
      <div
        style={{
          ...shell,
          background: cfg.fill,
          border: `1.5px solid ${cfg.color}`,
          borderRadius: 999,
        }}
      />
    )
  }

  if (cfg.shape === "rect") {
    return (
      <div
        style={{
          ...shell,
          background: cfg.fill,
          border: `1.5px solid ${cfg.color}`,
          borderRadius: 10,
        }}
      />
    )
  }

  if (cfg.shape === "diamond") {
    return (
      <svg
        width="100%"
        height="100%"
        preserveAspectRatio="none"
        viewBox={`0 0 ${cfg.width} ${cfg.height}`}
        style={shell}
      >
        <polygon
          points={`${cfg.width / 2},0 ${cfg.width},${cfg.height / 2} ${cfg.width / 2},${cfg.height} 0,${cfg.height / 2}`}
          fill={cfg.fill}
          stroke={cfg.color}
          strokeWidth="1.5"
        />
      </svg>
    )
  }

  if (cfg.shape === "paral") {
    return (
      <svg
        width="100%"
        height="100%"
        preserveAspectRatio="none"
        viewBox={`0 0 ${cfg.width} ${cfg.height}`}
        style={shell}
      >
        <polygon
          points={`${cfg.width * 0.14},0 ${cfg.width},0 ${cfg.width * 0.86},${cfg.height} 0,${cfg.height}`}
          fill={cfg.fill}
          stroke={cfg.color}
          strokeWidth="1.5"
        />
      </svg>
    )
  }

  if (cfg.shape === "paral-r") {
    return (
      <svg
        width="100%"
        height="100%"
        preserveAspectRatio="none"
        viewBox={`0 0 ${cfg.width} ${cfg.height}`}
        style={shell}
      >
        <polygon
          points={`0,0 ${cfg.width * 0.86},0 ${cfg.width},${cfg.height} ${cfg.width * 0.14},${cfg.height}`}
          fill={cfg.fill}
          stroke={cfg.color}
          strokeWidth="1.5"
        />
      </svg>
    )
  }

  if (cfg.shape === "hex") {
    return (
      <svg
        width="100%"
        height="100%"
        preserveAspectRatio="none"
        viewBox={`0 0 ${cfg.width} ${cfg.height}`}
        style={shell}
      >
        <polygon
          points={`${cfg.width * 0.1},0 ${cfg.width * 0.9},0 ${cfg.width},${cfg.height / 2} ${cfg.width * 0.9},${cfg.height} ${cfg.width * 0.1},${cfg.height} 0,${cfg.height / 2}`}
          fill={cfg.fill}
          stroke={cfg.color}
          strokeWidth="1.5"
        />
      </svg>
    )
  }

  return (
    <div
      style={{
        ...shell,
        background: cfg.fill,
        border: `1.5px solid ${cfg.color}`,
        borderRadius: 10,
      }}
    />
  )
}

/** Shared visual body for both editor nodes and read-only previews. */
export default function FlowchartBlockBody({
  type = "process",
  text,
  selected = false,
  isArmedSource = false,
  cursorStyle = "cursor-pointer",
}) {
  const cfg = getFlowchartBlockConfig(type)
  const displayText = text ?? cfg.defaultText
  const chrome = getFlowchartNodeChrome(type, selected, isArmedSource)

  return (
    <div
      className={`relative select-none transition ${cursorStyle}`}
      style={{ width: cfg.width, height: cfg.height }}
    >
      <ShapeFrame cfg={cfg} chrome={chrome} />
      <div className="absolute inset-0 grid place-items-center px-3 pointer-events-none">
        <div className="text-[12.5px] text-ink font-medium text-center leading-tight font-mono">
          {displayText}
        </div>
      </div>
    </div>
  )
}
