import { Spinner } from "@/shared/ui/LoadingBlock"

export default function RoutePageFallback() {
  return (
    <div
      className="content"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "40vh",
      }}
    >
      <Spinner size={40} />
    </div>
  )
}
