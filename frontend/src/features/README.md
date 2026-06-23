# `src/features/` — business capabilities

**Status:** ACTIVE  
**Redesign plan:** [docs/FRONTEND_STRUCTURE_REDESIGN.md](../../../docs/FRONTEND_STRUCTURE_REDESIGN.md)

---

## 1. What belongs here

- **Product features** scoped by domain: auth, curriculum, task solving, task authoring, analytics, etc.
- Feature hooks, feature API clients, feature-only UI components.
- Internal layering where mature (e.g. `task-editor`: `application/`, `domain/`, `presentation/`).

Features may import from `shared/` and `widgets/`. They should **not** import from `pages/`.

---

## 2. What is here now

| Module | Files (approx.) | Notes |
|--------|-----------------|-------|
| `task-solving/` | 26+ | **Facade**, hooks, model, `TeacherCommentComposer` (FE-ARCH-6.8 ✅) |
| `task-editor/` | 55 | Teacher assignment editor — mostly TS, clean layering |
| `student/` | 24 | Student home UI, layout, progress/toxic tabs — includes **home/catalog UI** (FE-ARCH-4A) |
| `teacher/` | 10 | Teacher cabinet panels |
| `analytics/` | 7 | Progress / solutions panels |
| `auth/` | 7 | Login UI, auth hooks |
| `support/` | 7 | Support tickets |
| `users/` | 6 | Profile views |
| `curriculum/` | 5 | Pascal curriculum API + showcase UI |
| `settings/` | 4 | Settings API + layout |
| `task-catalog/` | 4 | Teacher task list / catalog pages |
| `groups/` | 3 | Group assignment UI |
| `notifications/` | 2 | Notification components |
| `tasks/` | 1 | `recommendationsApi.js` only — naming orphan |
| `catalogs/` | 1 | Single modal — orphan |
| `teacher-profile/` | 1 | Teacher profile hook |

**Task solve facade:** `features/task-solving/hooks/useTaskSolver.js` — composes sub-hooks (FE-ARCH-6 ✅, FE-ARCH-6.8 ✅ folder consolidation).

**FE-ARCH-5 ✅:** `pages/TaskPages/` deleted — workspace in `widgets/task-workspace/`, utils in `task-solving/model/`.

---

## 3. Do not add here

- Route-only thin pages → `pages/` (or `feature/.../presentation/pages/` if feature-owned route)
- Large editors (Monaco board, BlockEditor) → `widgets/`
- Generic design-system primitives → `shared/ui/`
- Pure algorithms shared across features → `domain/` today; `features/*/model/` later

---

## 4. Where to put new files

| You need… | Put it in… |
|-----------|------------|
| New product area | `features/<feature-name>/` with `api/`, `ui/`, `hooks/` as needed |
| Task solve helpers (not god-hook) | `features/task-solving/model/` |
| Teacher editor logic | `features/task-editor/` |
| Student home / catalog UX | `features/student/` or future `features/student-home/` |
| Cross-feature HTTP | `shared/api/` |

---

## 5. Status

| Item | Status |
|------|--------|
| Most feature folders | **ACTIVE** |
| `task-solving/` (hooks + facade + model) | **ACTIVE** — FE-ARCH-6.8 complete |
| `tasks/`, `catalogs/` (1-file orphans) | **ACTIVE** — consolidate in FE-ARCH-4/5 |

**Done:** legacy solver folder merged into `task-solving` (FE-ARCH-6.8). **Later:** merge `task-catalog` + `task-editor` under `task-authoring/`.
