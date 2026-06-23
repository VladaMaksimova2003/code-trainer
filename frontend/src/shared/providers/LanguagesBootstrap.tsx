import type { ReactNode } from "react"
import { useLanguages } from "@/shared/hooks/useLanguages"

interface LanguagesBootstrapProps {
  children: ReactNode
}

/** Prefetches GET /languages so runtime cache is warm for non-hook callers. */
export function LanguagesBootstrap({ children }: LanguagesBootstrapProps) {
  useLanguages()
  return children
}
