export type { BlockPlacement } from "@/domain/blockAssembly/types"
export {
  assembleSlotTemplate,
  buildCode,
  deriveSubmitPayload,
  getInitialBaseCode,
} from "@/domain/blockAssembly/buildCode"
export { prepareBlockAssemblyScaffold, buildAssemblyPreviewCode } from "@/domain/blockAssembly/scaffold"
export { formatAssemblyTemplate } from "@/domain/blockAssembly/formatTemplate"
export {
  deriveBaseCodeFromReference,
  deriveTemplateWithSlotMarkers,
  extractBlocksFromRanges,
} from "@/domain/blockAssembly/authoring"
export {
  collectScaffoldGapRanges,
  isFullyBlockedExceptWhitespace,
  isWhitespaceOnlyText,
  templateScaffoldIsWhitespaceOnly,
} from "@/domain/blockAssembly/blockScaffold"
export {
  normalizePlacements,
  isAssemblyComplete,
  assemblyCompletionStats,
  requiredTemplateSlotIds,
  isTemplateAssemblyComplete,
  isSlotAssemblyOrderCorrect,
  BLOCK_ORDER_ERROR_MESSAGE,
} from "@/domain/blockAssembly/normalize"
export {
  applyDrop,
  addPlacement,
  removePlacement,
  removePlacementsByIds,
  resolveDropTarget,
  shiftPlacementColumn,
} from "@/domain/blockAssembly/drop"
export { resolveDropPosition } from "@/domain/blockAssembly/dropPosition"
export {
  blockFirstLineWidth,
  formatBlockDisplayText,
  trimBlockText,
  blockLineSpan,
  BLOCK_ASSEMBLY_TAB_SIZE,
  getBaseLine,
  getLineIndentLen,
  normalizeCodeColumn,
  padBaseCodeToLine,
  maxPlacementLine,
  placementsOnLine,
  snapColumnToTab,
} from "@/domain/blockAssembly/utils"
