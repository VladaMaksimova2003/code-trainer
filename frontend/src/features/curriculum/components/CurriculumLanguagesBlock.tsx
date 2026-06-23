interface CurriculumLanguagesBlockProps {
  languages?: unknown[]
  loading?: boolean
  error?: unknown | null
}

import { useNavigate } from "react-router-dom"
import Badge from "@/shared/ui/Badge"
import LoadingBlock from "@/shared/ui/LoadingBlock"
import { ProgressBar } from "@/features/curriculum/components/CurriculumProgressBar"
import { displayTrackTotal, progressPercent } from "@/features/curriculum/actionMeta"

const LANGUAGE_ROUTES = {
  pascal: "/learn/pascal",
  python: "/learn/python",
  cpp: "/learn/cpp",
  csharp: "/learn/csharp",
  java: "/learn/java",
}

function LanguageCard({ language, onOpenLanguage, onOpenTopics }) {
  const progress = language.progress || {}
  const totalTasks = displayTrackTotal(language)
  const percent = progressPercent({
    ...progress,
    catalog_tasks: progress.catalog_tasks ?? totalTasks,
  })
  const available = language.available
  const languageRoute = LANGUAGE_ROUTES[language.language]

  return (
    <article
      className={`rounded-lg border p-3 space-y-2 ${
        available
          ? "border-border bg-surface/80"
          : "border-border/60 bg-surface/40 opacity-60"
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <button
          type="button"
          disabled={!available}
          onClick={() => available && languageRoute && onOpenLanguage(languageRoute)}
          className={`text-left font-medium text-ink ${available && languageRoute ? "hover:text-lime" : ""}`}
        >
          {language.language_label}
        </button>
        {available ? <Badge kind="purple">Доступно</Badge> : <Badge kind="muted">Скоро</Badge>}
      </div>

      {available ? (
        <>
          <p className="text-sm text-ink-muted">
            {progress.passed_tasks ?? 0}/{totalTasks} задач
          </p>
          <ProgressBar percent={percent} />
          <div className="flex flex-wrap gap-2 pt-1">
            {languageRoute ? (
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={() => onOpenTopics(languageRoute)}
              >
                Открыть сборники
              </button>
            ) : null}
          </div>
        </>
      ) : (
        <p className="text-sm text-ink-muted">Темы появятся позже</p>
      )}
    </article>
  )
}

export default function CurriculumLanguagesBlock({

  languages = [],
  loading = false,
  error = null,

}: CurriculumLanguagesBlockProps) {
  const navigate = useNavigate()

  if (loading) {
    return (
      <section className="card card-pad space-y-2">
        <h2 className="text-base font-semibold text-ink">Языки обучения</h2>
        <LoadingBlock text="Загрузка…" minHeight={120} className="border-0 bg-transparent p-0" />
      </section>
    )
  }

  if (error) {
    return (
      <section className="card card-pad space-y-2">
        <h2 className="text-base font-semibold text-ink">Языки обучения</h2>
        <p className="text-sm text-red-400" role="alert">
          {String(error)}
        </p>
      </section>
    )
  }

  if (!languages.length) {
    return null
  }

  return (
    <section className="card card-pad space-y-3">
      <h2 className="text-base font-semibold text-ink">Языки обучения</h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {languages.map((language: unknown) => (
          <LanguageCard
            key={language.language}
            language={language}
            onOpenLanguage={navigate}
            onOpenTopics={navigate}
          />
        ))}
      </div>
    </section>
  )
}
