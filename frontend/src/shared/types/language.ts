/** Language catalog item from GET /languages. */

export interface LanguageItem {
  id: string
  label?: string
  monaco_language?: string
  supported_features?: string[]
  [key: string]: unknown
}
