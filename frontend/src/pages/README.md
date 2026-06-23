# `src/pages/` — route-level screens

**Status:** ACTIVE  
**Redesign plan:** [docs/FRONTEND_STRUCTURE_REDESIGN.md](../../../docs/FRONTEND_STRUCTURE_REDESIGN.md)  
**TaskPages decomposition:** [docs/TASKPAGES_DECOMPOSITION_PLAN.md](../../../docs/TASKPAGES_DECOMPOSITION_PLAN.md) — **FE-ARCH-5 ✅ complete**

---

## 1. What belongs here

- **One screen per route** — thin composition: load data via hooks, render layout + feature/widget children.
- Grouped by audience: `Auth/`, `Student/`, `Teacher/`, `Settings/`, `Support/`, `Demo/`, `Users/`, `task/`.
- Task route entry: `pages/task/TaskPage.jsx` → `widgets/task-workspace/StudentTaskWorkspace`.

Pages should **not** contain large editors, test panels, or pure utility modules.

---

## 2. What is here now

| Folder | Files (approx.) | Purpose |
|--------|-----------------|---------|
| `Auth/` | 4 | Login, register, callback, reset password |
| `Student/` | 6 | Home, tasks list, profile, Pascal learn/showcase, groups |
| `Teacher/` | 2 | Teacher cabinet, profile redirect |
| `Settings/` | 4 | Settings shell + tabs |
| `Support/` | 3 | Support tickets |
| `Demo/` | 3 | Demo home + demo task wrapper |
| `Users/` | 1 | Public user profile |
| **`task/`** | **1** | `TaskPage.jsx` — thin route entry |

~~`pages/TaskPages/`~~ — **deleted FE-ARCH-5.5** (workspace → `widgets/`, utils → `features/task-solving/model/`).

**Active student path:** `router` → `pages/task/TaskPage` → `useTaskSolver` → `widgets/task-workspace/StudentTaskWorkspace`.

---

## 3. Do not add here

- New editors (Monaco, React Flow, block assembly) → `widgets/`
- Business rules, feature APIs → `features/`
- Reusable buttons/modals/types → `shared/`
- Task workspace UI → `widgets/task-workspace/`

---

## 4. Where to put new files

| You need… | Put it in… |
|-----------|------------|
| New authenticated route screen | `pages/<area>/` matching router |
| Teacher assignment editor page | `features/task-editor/presentation/pages/` |
| Task workspace pane / split layout | `widgets/task-workspace/` |
| Task type predicates, panel formatters | `features/task-solving/model/` |

---

## 5. Status

| Area | Status |
|------|--------|
| `Auth/`, `Student/`, `Teacher/`, … | **ACTIVE** |
| `task/TaskPage.jsx` | **ACTIVE** |
| ~~`TaskPages/`~~ | **Deleted** — FE-ARCH-5.5 ✅ |
| FE-ARCH-5 decomposition | **Complete** |
