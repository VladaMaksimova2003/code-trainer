import LanguageTrackPage from "@/pages/Student/LanguageTrackPage"

interface CppLanguagePageProps {
  user?: { id?: number | string } | null
  onSignOut?: () => void
}

export default function CppLanguagePage(props: CppLanguagePageProps) {
  return <LanguageTrackPage language="cpp" {...props} />
}
