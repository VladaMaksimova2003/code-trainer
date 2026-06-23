import LanguageTrackPage from "@/pages/Student/LanguageTrackPage"

interface JavaLanguagePageProps {
  user?: { id?: number | string } | null
  onSignOut?: () => void
}

export default function JavaLanguagePage(props: JavaLanguagePageProps) {
  return <LanguageTrackPage language="java" {...props} />
}
