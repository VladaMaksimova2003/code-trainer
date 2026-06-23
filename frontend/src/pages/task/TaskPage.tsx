import { useTaskSolver } from "@/features/task-solving/hooks/useTaskSolver"
import DemoBanner from "@/pages/Demo/DemoBanner"
import LoadingPage from "@/shared/ui/LoadingPage"
import StudentTaskWorkspace from "@/widgets/task-workspace/StudentTaskWorkspace"

export default function TaskPage({ user = null }) {
  const isGuest = !user
  const solver = useTaskSolver(
    isGuest
      ? { guestMode: true, homePath: "/", taskPathPrefix: "/tasks" }
      : { userId: user?.id },
  )
  const {
    id,
    task,
    isTaskLoading,
    taskLoadError,
    navigate,
  } = solver

  if (isTaskLoading) {
    return (
      <>
        {isGuest ? <DemoBanner /> : null}
        <LoadingPage text="Загрузка задачи…" />
      </>
    )
  }

  if (!task) {
    return (
      <>
        {isGuest ? <DemoBanner /> : null}
        <div className="flex h-screen flex-col items-center justify-center gap-4 bg-bg text-ink">
          <div className="text-ink-muted">{taskLoadError || "Задача сейчас недоступна."}</div>
          <button
            type="button"
            className="rounded-md border border-border bg-surface-2 px-4 py-2 text-sm hover:border-lime"
            onClick={() => navigate("/")}
          >
            Вернуться к задачам
          </button>
        </div>
      </>
    )
  }

  return (
    <>
      {isGuest ? <DemoBanner /> : null}
      <StudentTaskWorkspace id={id} task={task} user={user} guestMode={isGuest} {...solver} />
    </>
  )
}
