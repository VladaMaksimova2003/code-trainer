import { useId } from "react"

interface BrandLogoProps {
  size?: number
  className?: string
}

export default function BrandLogo({ size = 30, className = "" }: BrandLogoProps) {
  const uid = useId().replace(/:/g, "")
  const limeId = `brand-lime-${uid}`
  const glowId = `brand-glow-${uid}`

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 512 512"
      width={size}
      height={size}
      className={["brand-logo", className].filter(Boolean).join(" ")}
      role="img"
      aria-label="Code Trainer"
      draggable={false}
    >
      <defs>
        <linearGradient id={limeId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#a8ff3a" />
          <stop offset="1" stopColor="#8eff01" />
        </linearGradient>
        <filter id={glowId} x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="7" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <rect
        x="150"
        y="150"
        width="196"
        height="196"
        rx="52"
        fill="none"
        stroke="#8b53fe"
        strokeWidth="26"
        opacity="0.85"
      />
      <g filter={`url(#${glowId})`}>
        <rect
          x="196"
          y="196"
          width="196"
          height="196"
          rx="52"
          fill="none"
          stroke={`url(#${limeId})`}
          strokeWidth="30"
        />
      </g>
    </svg>
  )
}
