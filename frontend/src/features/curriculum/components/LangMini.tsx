import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import {
  CURRICULUM_LANGUAGE_OPTIONS,
  type CurriculumLanguageOption,
} from "@/features/curriculum/curriculumLanguageUi"
import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"

interface LangMiniProps {
  language: CurriculumLearningLanguage
  availableLanguages?: Array<{ language: string; available?: boolean }>
}

export default function LangMini({ language, availableLanguages = [] }: LangMiniProps) {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onDoc = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", onDoc)
    return () => document.removeEventListener("mousedown", onDoc)
  }, [])

  const isAvailable = (opt: CurriculumLanguageOption) => {
    if (!availableLanguages.length) return true
    const row = availableLanguages.find((l) => l.language === opt.id)
    if (row) return row.available !== false
    return true
  }

  const current = CURRICULUM_LANGUAGE_OPTIONS.find((l) => l.id === language) ?? CURRICULUM_LANGUAGE_OPTIONS[0]

  const pick = (opt: CurriculumLanguageOption) => {
    if (!isAvailable(opt)) return
    setOpen(false)
    if (opt.id !== language) navigate(opt.route)
  }

  return (
    <div className="lang-mini" ref={ref}>
      <button type="button" className="lang-mini-btn" onClick={() => setOpen((v) => !v)} title="Сменить язык">
        <span className="g">{current.glyph}</span>
        <span>{current.label}</span>
        <span style={{ fontSize: 10, color: "var(--text-3)" }}>▾</span>
      </button>
      {open ? (
        <div className="lang-mini-menu">
          {CURRICULUM_LANGUAGE_OPTIONS.map((opt) => {
            const soon = !isAvailable(opt)
            return (
              <div
                key={opt.id}
                role="button"
                tabIndex={0}
                className={`lang-mini-opt${opt.id === language ? " on" : ""}`}
                onClick={() => pick(opt)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault()
                    pick(opt)
                  }
                }}
              >
                <span className="g">{opt.glyph}</span>
                {opt.label}
                {soon ? <span className="soon">скоро</span> : null}
              </div>
            )
          })}
        </div>
      ) : null}
    </div>
  )
}
