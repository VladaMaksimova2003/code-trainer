import LanguageTrackPage from "@/pages/Student/LanguageTrackPage"

interface CsharpLanguagePageProps {
  user?: { id?: number | string } | null
  onSignOut?: () => void
}

export default function CsharpLanguagePage(props: CsharpLanguagePageProps) {
  return <LanguageTrackPage language="csharp" {...props} />
}
