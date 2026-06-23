import { Link, useNavigate } from "react-router-dom"

import {
  learnCourseFootnote,
  learnCourseGlyph,
  type LearnCourse,
} from "@/features/curriculum/learnTracksUi"
import { writeStoredLearningLanguage } from "@/features/curriculum/curriculumLanguageUi"

interface LearnCourseCardProps {
  course: LearnCourse
}

export default function LearnCourseCard({ course }: LearnCourseCardProps) {
  const navigate = useNavigate()

  const openCourse = () => {
    writeStoredLearningLanguage(course.preferredLanguage)
    navigate(course.hubRoute)
  }

  const pct = course.progressPercent

  return (
    <button type="button" className="track-card" onClick={openCourse}>
      <div className="tc-top">
        <span className="tc-glyph">{learnCourseGlyph(course.title)}</span>
        <div className="tc-langtags">
          {course.languages.map((lang) => (
            <span
              key={lang.id}
              className={`tc-langtag${lang.available ? "" : " empty"}`}
              title={lang.available ? lang.label : `${lang.label} — скоро`}
            >
              {lang.glyph}
            </span>
          ))}
        </div>
      </div>
      <b className="tc-name">{course.title}</b>
      {course.description ? <p className="tc-desc">{course.description}</p> : null}
      {course.authorProfilePath ? (
        <Link
          to={course.authorProfilePath}
          className="tc-author tc-author-link"
          onClick={(event) => event.stopPropagation()}
        >
          {course.author}
        </Link>
      ) : (
        <div className="tc-author">{course.author}</div>
      )}
      <div className="tc-foot">
        <div className="between mb-[7px]">
          <span className="mut3 text-[12px]">{learnCourseFootnote(course)}</span>
          <span className="mono text-[12px]" style={{ color: pct ? "var(--lime)" : "var(--text-3)" }}>
            {pct}%
          </span>
        </div>
        <div className="progress">
          <i style={{ width: `${pct}%` }} />
        </div>
      </div>
    </button>
  )
}
