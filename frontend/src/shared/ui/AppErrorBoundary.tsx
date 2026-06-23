import { Component, type ErrorInfo, type ReactNode } from "react"

interface AppErrorBoundaryProps {
  children: ReactNode
}

interface AppErrorBoundaryState {
  error: Error | null
}

export default class AppErrorBoundary extends Component<AppErrorBoundaryProps, AppErrorBoundaryState> {
  constructor(props: AppErrorBoundaryProps) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error: Error): AppErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("[AppErrorBoundary]", error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div
          className="auth-shell"
          style={{ padding: 24, textAlign: "center", maxWidth: 480, margin: "0 auto" }}
        >
          <h1 style={{ fontSize: 20, fontWeight: 800, marginBottom: 8 }}>Ошибка интерфейса</h1>
          <p className="muted" style={{ fontSize: 14, marginBottom: 16 }}>
            {this.state.error?.message || String(this.state.error)}
          </p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => window.location.reload()}
          >
            Обновить страницу
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
