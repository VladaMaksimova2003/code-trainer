import { useTaskSolver } from "@/features/task-solving/hooks/useTaskSolver"
import DemoBanner from "@/pages/Demo/DemoBanner"
import LoadingBlock from "@/shared/ui/LoadingBlock"
import StudentTaskWorkspace from "@/widgets/task-workspace/StudentTaskWorkspace"

export default function DemoTaskPage() {
  const solver = useTaskSolver({
    guestMode: true,
    homePath: "/demo",
    taskPathPrefix: "/demo/tasks",
  })
  const {
    id,
    task,
    isTaskLoading,
    taskLoadError,
    navigate,
    homePath,
  } = solver

  if (isTaskLoading) {
    return (
      <div className="min-h-screen bg-bg">
        <DemoBanner />
        <div className="px-6 py-10">
          <LoadingBlock text="Загрузка задачи…" minHeight={320} />
        </div>
      </div>
    )
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-bg">
        <DemoBanner />
        <div className="flex h-[calc(100vh-40px)] flex-col items-center justify-center gap-4 text-ink">
          <div className="text-ink-muted">{taskLoadError || "Задача недоступна в демо-режиме."}</div>
          <button
            type="button"
            className="rounded-md border border-border bg-surface-2 px-4 py-2 text-sm hover:border-lime"
            onClick={() => navigate(homePath || "/demo")}
          >
            К списку задач
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-bg">
      <DemoBanner />
      <StudentTaskWorkspace id={id} task={task} user={null} guestMode {...solver} />
    </div>
  )
}
