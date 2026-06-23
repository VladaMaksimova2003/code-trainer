# `features/task-solving/` — student task solve feature

**Status:** ACTIVE — **fully TypeScript** ✅ (FE-ARCH-7 + Frontend-TS-2 + Frontend-TS-2.1)

---

## Purpose

Student task solve path: hooks, facade, pure model helpers, and teacher-review comment UI.

### Hooks (`hooks/`) — all TypeScript

| File | Role |
|------|------|
| `useTaskSolver.ts` | **Public facade** — composes sub-hooks; stable API for `TaskPage` / `DemoTaskPage` |
| `useTaskNavigation.ts` | Collection / adaptive navigation context |
| `useTaskLoader.ts` | Task fetch + hydration |
| `useDraftState.ts` | localStorage drafts |
| `useLanguageSelection.ts` | User / block / example language |
| `useExecutionResultState.ts` | Bottom panel results/errors |
| `useCodeSubmission.ts` | Code + guest submit |
| `useBlockAssemblySubmission.ts` | Block reorder submit |
| `useFlowchartSubmission.ts` | Flow check submit |
| `index.ts` | Internal barrel (includes `useTaskSolver`, `UseTaskSolverReturn`) |

### Model (`model/`) — all TypeScript

| File | Role |
|------|------|
| `isFlowchartTask.ts` | Flowchart task type detection |
| `testPanelUtils.ts` | Test panel rows, error formatting |
| `navigationContext.ts` | Task navigation sessionStorage |
| `taskNavigationHelpers.ts` | Pure navigation decisions |
| `taskDraftHelpers.ts` | Draft localStorage keys/signatures |
| `taskHydrationHelpers.ts` | Task load hydration (+ `TaskHydrationSnapshot`) |
| `executionResultHelpers.ts` | Execution result mapping |
| `flowSubmitHelpers.ts` | Flow submit payload helpers |
| `studentUiUtils.ts` | Task-type / language / editor-mode matrix |
| `constructionHintsUtils.ts` | Pattern usage hints for left rail |

### Components (`components/`)

| File | Role |
|------|------|
| `TeacherCommentComposer.tsx` | Teacher review comment textarea (used by `SubmissionCommentsTab`) |

---

## Imports

```js
import { useTaskSolver } from "@/features/task-solving/hooks/useTaskSolver"
import { isFlowchartTask } from "@/features/task-solving/model/isFlowchartTask"
import TeacherCommentComposer from "@/features/task-solving/components/TeacherCommentComposer"
```

**TS migration:** [docs/TASK_SOLVING_TS_MIGRATION_REPORT.md](../../../../docs/TASK_SOLVING_TS_MIGRATION_REPORT.md)

**Plan history:** [docs/TASKPAGES_DECOMPOSITION_PLAN.md](../../../../docs/TASKPAGES_DECOMPOSITION_PLAN.md)
