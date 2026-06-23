interface TaskStatusDotProps {
  status?: "solved" | "attempted" | string
}

export default function TaskStatusDot({ status }: TaskStatusDotProps) {
  if (status === "solved") {
    return (
      <span
        className="badge badge-lime btn-icon"
        aria-label="Решено"
        style={{
          width: 24,
          height: 24,
          padding: 0,
          justifyContent: "center",
          borderRadius: "50%",
        }}
      >
        ✓
      </span>
    )
  }
  if (status === "attempted") {
    return (
      <span
        aria-label="В процессе"
        style={{
          display: "inline-block",
          width: 24,
          height: 24,
          borderRadius: "50%",
          border: "2px solid var(--purple)",
        }}
      />
    )
  }
  return (
    <span
      aria-label="Не начато"
      style={{
        display: "inline-block",
        width: 24,
        height: 24,
        borderRadius: "50%",
        border: "2px dashed var(--border-2)",
      }}
    />
  )
}
