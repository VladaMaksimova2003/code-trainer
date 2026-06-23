import LanguageTrackPage from "@/pages/Student/LanguageTrackPage"

interface PythonLanguagePageProps {
  user?: { id?: number | string } | null
  onSignOut?: () => void
}

export default function PythonLanguagePage(props: PythonLanguagePageProps) {
  return <LanguageTrackPage language="python" {...props} />
}
