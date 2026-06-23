/** Autolint debounce — fast tools get shorter delay; heavy compilers wait longer. */
export function lintDebounceMs(language: string): number {
  switch (String(language || "").toLowerCase()) {
    case "pascal":
      return 650
    case "java":
    case "cpp":
    case "csharp":
      return 500
    default:
      return 450
  }
}
