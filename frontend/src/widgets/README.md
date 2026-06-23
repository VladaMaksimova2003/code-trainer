# `src/widgets/` — large UI compositions & editors

**Status:** ACTIVE  
**Redesign plan:** [docs/FRONTEND_STRUCTURE_REDESIGN.md](../../../docs/FRONTEND_STRUCTURE_REDESIGN.md)

---

## 1. What belongs here

- **Heavy, reusable UI blocks**: code editors, flowchart editor, block-assembly board, task workspace.
- Multi-part widgets with local `lib/` and `ui/` (or flat folder for task widgets).
- Task solve UI: `task-workspace/`, `test-panel/`, `task-header/`.

Widgets compose `features/` + `shared/`; imported by `pages/` and `features/`, not the other way around.

---

## 2. What is here now

| Widget | Contents | Used by |
|--------|----------|---------|
| `BlockEditor/` | React Flow diagram editor | `StudentEditorMain`, task editor |
| `BlockAssemblyEditor/` | Drag-and-drop code assembly | `StudentEditorMain`, task editor |
| `CodeEditorBoard/` | Monaco wrapper | `StudentEditorMain` |
| `BlockTaskCodeEditor/` | Block-task Monaco variant | Task editor |
| `GithubContributionGraph/` | Contribution heatmap | Profile / student UI |
| **`task-workspace/`** | 16 files — workspace shell, editor splits, left rail, popovers | `TaskPage`, `DemoTaskPage` |
| **`test-panel/`** | `StudentBottomPanel`, `SubmissionCommentsTab` | `StudentTaskWorkspace` |
| **`task-header/`** | `StudentTaskHeader` | `StudentTaskWorkspace` |

---

## 3. Do not add here

- Route screens → `pages/`
- Task orchestration / submit logic → `features/task-solving/` (hooks + model)
- Generic Button/Modal/Badge → `shared/ui/`

---

## 4. Where to put new files

| You need… | Put it in… |
|-----------|------------|
| New editor or large pane | `widgets/<name>/` |
| Task workspace pane | `widgets/task-workspace/` |
| Test / errors bottom panel | `widgets/test-panel/` |
| Task page header bar | `widgets/task-header/` |

---

## 5. Status

**ACTIVE** — all listed widgets on production student task path.

**FE-ARCH-5 ✅:** `pages/TaskPages/` dissolved into `task-workspace/`, `test-panel/`, `task-header/`.

**Do not change** `BlockEditor` behavior during structure-only phases (flowchart-sensitive).
