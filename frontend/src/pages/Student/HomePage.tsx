import DemoBanner from "@/pages/Demo/DemoBanner"
import StudentTasksPage from "@/pages/Student/TasksPage"

/** Code Trainer — task list at `/` for guests and authenticated users. */
export default function HomePage({ user, onSignOut }) {
  const isGuest = !user

  return (
    <>
      {isGuest ? <DemoBanner /> : null}
      <StudentTasksPage user={user} onSignOut={onSignOut} />
    </>
  )
}
