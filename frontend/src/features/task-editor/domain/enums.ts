export enum TaskType {
  BUILD_FROM_BLOCKS = "task_build_from_blocks",
  TRANSLATE_SNIPPET = "task_translate_snippet",
  TRANSLATE_FULL_PROGRAM = "task_translate_full_program",
  FLOWCHART_TO_CODE = "task_flowchart_to_code",
}

export enum PatternType {
  BRANCHING = "branching",
  LOOP = "loop",
  FUNCTION = "function",
  ACCUMULATION = "accumulation",
  CONDITIONAL = "conditional",
}

export enum DifficultyLevel {
  EASY = "easy",
  MEDIUM = "medium",
  HARD = "hard",
}

export enum AnalysisStatus {
  IDLE = "idle",
  ANALYZING = "analyzing",
  READY = "ready",
  APPROVED = "approved",
  ERROR = "error",
}
