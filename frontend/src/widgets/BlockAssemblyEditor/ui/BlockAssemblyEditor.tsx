import { isAssemblyComplete } from "@/domain/blockAssembly"
import { isTemplateAssemblyMode } from "@/widgets/BlockAssemblyEditor/lib/blockAssemblyMode"
import FreeBlockAssemblyView from "@/widgets/BlockAssemblyEditor/ui/FreeBlockAssemblyView"
import TemplateBlockAssemblyView from "@/widgets/BlockAssemblyEditor/ui/TemplateBlockAssemblyView"
import { getAllLanguageIds } from "@/shared/config/languages"

export default function BlockAssemblyEditor({
  blocks = [],
  baseCode: baseCodeProp,
  code: codeProp,
  rawTemplate,
  correctOrder,
  placements,
  onChange,
  language,
  primaryLanguage,
  languageVariants,
  onLanguageChange,
  shuffleKey = "",
  hideLanguageSelect = false,
}) {
  const baseCode = baseCodeProp ?? codeProp ?? ""
  const isTemplate = isTemplateAssemblyMode(baseCode, rawTemplate)

  const availableLanguages = (() => {
    const langs = []
    if (primaryLanguage) langs.push(primaryLanguage)
    if (language && !langs.includes(language)) langs.push(language)
    if (languageVariants) {
      Object.keys(languageVariants).forEach((lang) => {
        if (!langs.includes(lang)) langs.push(lang)
      })
    }
    return langs
  })()

  const selectableLanguages = [...new Set([...getAllLanguageIds(), ...availableLanguages])]

  const isLanguageAvailable = (lang) => {
    if (lang === primaryLanguage) return true
    if (lang === language) return true
    return Boolean(languageVariants && languageVariants[lang])
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col bg-bg-2">
      {!hideLanguageSelect && availableLanguages.length > 1 ? (
        <div className="shrink-0 border-b border-border px-4 py-2">
          <select
            value={language || primaryLanguage || availableLanguages[0] || ""}
            onChange={(event) => onLanguageChange?.(event.target.value)}
            className="rounded-md border border-[#333d4f] bg-surface-2 px-2 py-1 font-mono text-[12.5px] text-ink focus:outline-none focus:ring-1 focus:ring-lime/40"
          >
            {selectableLanguages.map((lang) => (
              <option key={lang} value={lang} disabled={!isLanguageAvailable(lang)}>
                {lang.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <div className="flex min-h-0 flex-1 flex-col">
        {isTemplate ? (
          <TemplateBlockAssemblyView
            blocks={blocks}
            baseCode={baseCode}
            rawTemplate={rawTemplate}
            placements={placements}
            onChange={onChange}
            language={language}
            primaryLanguage={primaryLanguage}
            correctOrder={correctOrder}
            shuffleKey={shuffleKey}
          />
        ) : (
          <FreeBlockAssemblyView
            blocks={blocks}
            placements={placements}
            onChange={onChange}
            shuffleKey={shuffleKey}
          />
        )}
      </div>
    </div>
  )
}

export { isAssemblyComplete }
