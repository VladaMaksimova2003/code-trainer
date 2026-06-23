import { useEffect, useState } from "react"
import Badge from "@/shared/ui/Badge"
import BrandLogo from "@/features/auth/ui/BrandLogo"
import { getServerLanguages, getTaskOverview } from "@/shared/api"
import { getLanguagesCache } from "@/shared/config/languages"
import {
  formatLanguageCountBadge,
  formatTaskCountBadge,
} from "@/features/auth/utils/formatAuthBadges"

interface AuthBrandProps {
  centered?: boolean
}

function useAuthHeroStats() {
  const [taskCount, setTaskCount] = useState<number | null>(null)
  const [languageCount, setLanguageCount] = useState<number | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const [overview, languages] = await Promise.all([
          getTaskOverview({ page: 1, pageSize: 1 }).catch(() => ({
            tasks: [],
            total: 0,
            page: 1,
            page_size: 0,
          })),
          getServerLanguages().catch(() => getLanguagesCache()),
        ])
        if (cancelled) return
        setTaskCount(typeof overview.total === "number" ? overview.total : overview.tasks?.length ?? 0)
        setLanguageCount(Array.isArray(languages) ? languages.length : getLanguagesCache().length)
      } catch {
        if (!cancelled) {
          setTaskCount(0)
          setLanguageCount(getLanguagesCache().length)
        }
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  return { taskCount, languageCount, isLoading: taskCount === null }
}

export default function AuthBrand({ centered = false }: AuthBrandProps) {
  const logoSize = centered ? 54 : 46

  return (
    <div
      className={["brand", centered ? "brand--stacked" : "brand--inline"].filter(Boolean).join(" ")}
    >
      <BrandLogo size={logoSize} />
      <b>
        Code<span className="pulse"> Trainer</span>
      </b>
    </div>
  )
}

export function AuthHeroPanel() {
  const { taskCount, languageCount, isLoading } = useAuthHeroStats()
  const taskLabel = isLoading ? "…" : formatTaskCountBadge(taskCount)
  const langLabel = isLoading ? "…" : formatLanguageCountBadge(languageCount)

  return (
    <div className="auth-brand">
      <AuthBrand />
      <div>
        <div style={{ fontSize: 34, fontWeight: 800, letterSpacing: "-1px", lineHeight: 1.1 }}>
          Тренажёр, который
          <br />
          учит писать{" "}
          <em
            style={{
              fontFamily: "var(--serif)",
              fontStyle: "italic",
              fontWeight: 400,
              color: "var(--lime)",
            }}
          >
            код
          </em>
        </div>
        <div className="wrap" style={{ marginTop: 22 }}>
          <Badge kind="lime">{taskLabel}</Badge>
          <Badge kind="purple">{langLabel}</Badge>
        </div>
      </div>
      <span className="mut3" style={{ fontSize: 12 }}>
        © 2026 Code Trainer
      </span>
    </div>
  )
}
