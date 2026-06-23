import LanguageTrackPage from "@/pages/Student/LanguageTrackPage"

interface PascalLanguagePageProps {
  user?: { id?: number | string } | null
  onSignOut?: () => void
}

export default function PascalLanguagePage(props: PascalLanguagePageProps) {
  return <LanguageTrackPage language="pascal" {...props} />
}
