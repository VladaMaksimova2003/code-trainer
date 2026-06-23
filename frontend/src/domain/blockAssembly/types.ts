export interface BlockPlacement {
  id: string
  blockIndex: number
  /** 1-based line in baseCode */
  line: number
  /** 1-based column in line */
  column: number
  /** Order among blocks on the same line */
  slot: number
  /** Template marker {n} this placement occupies (may differ from blockIndex). */
  templateSlot?: number
}
