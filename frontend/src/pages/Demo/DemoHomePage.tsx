import DemoBanner from "@/pages/Demo/DemoBanner"
import StudentTasksPage from "@/pages/Student/TasksPage"

export default function DemoHomePage() {
  return (
    <div className="min-h-screen bg-bg">
      <DemoBanner />
      <StudentTasksPage taskPathPrefix="/demo/tasks" demoMode />
    </div>
  )
}
