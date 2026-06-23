# `src/shared/` — cross-cutting infrastructure

**Status:** ACTIVE  
**Redesign plan:** [docs/FRONTEND_STRUCTURE_REDESIGN.md](../../../docs/FRONTEND_STRUCTURE_REDESIGN.md)

---

## 1. What belongs here

Reusable building blocks **without product-specific business rules**:

| Subfolder | Purpose |
|-----------|---------|
| `api/` | HTTP clients, auth tokens, typed wrappers (`taskApi.ts`) |
| `types/` | Shared DTOs: `task`, `flow`, `execution`, `taskLabels`, OpenAPI aliases in `openapi.ts` |
| `ui/` | Design-system primitives: Button, Modal, Badge, Chip, DiffBadge, StatusBadge, RoleBadge, ProtectedRoute, toast |
| `utils/` | Formatting, avatars, errors, recommendations helpers |
| `hooks/` | Generic hooks: pagination, async, languages |
| `config/` | Static config: languages, skill groups |
| `lib/` | Small pure helpers (e.g. `relativeTime`) |
| `providers/` | React Query, languages bootstrap |

`shared/` must not import from `pages/`, `features/`, or `widgets/`.

---

## 2. What is here now

| Subfolder | Key files |
|-----------|-----------|
| `api/` | Typed HTTP clients (`shared/api/index.ts`, domain modules), OpenAPI schema in `api/generated/schema.ts` |
| `types/` | `task.ts`, `flow.ts`, `execution.ts`, `taskLabels.ts`, domain DTO aliases (`groups`, `catalog`, …) |
| `ui/` | Button, Modal, Card, Badge, Chip, DiffBadge, StatusBadge, RoleBadge, Form, Progress, **EmptyState**, **Pagination**, **TaskStatusDot**, toast, … |
| `utils/` | format, errors, activityStats, studentRecommendations, … |
| `hooks/` | `useAsync`, `usePagination`, `useLanguages`, **`useProfile`**, **`useStudentStreakDays`**, **`useTasks`** |
| `config/` | `languages.js`, `skillGroups.js` |
| `providers/` | `QueryProvider.tsx`, `LanguagesBootstrap.jsx` |

**Note:** Root `src/hooks/` was removed in **FE-ARCH-3** — all hooks live under `shared/hooks/`.

**Chip/Badge:** canonical Tailwind components in **`shared/ui/`** — `Chip` auto-adapts legacy CSS props when needed. See [UI_COMPONENTS_CONSOLIDATION_PLAN.md](../../../docs/UI_COMPONENTS_CONSOLIDATION_PLAN.md).

**OpenAPI types:** `npm run openapi:export` (docker API) → `npm run codegen:api` regenerates `api/generated/schema.ts`; domain types in `shared/types/` re-export strict schemas.

**FE-ARCH-4B ✅ complete:** all former `components/ui/` files now under `shared/ui/`; `src/components/` deleted; `shared/ui/legacy/` removed.

---

## 3. Do not add here

- Feature-specific panels (teacher toxic tasks, curriculum cards) → `features/`
- Task workspace / editors → `widgets/`
- Route pages → `pages/`
- Block assembly algorithms → `domain/` today → `features/block-assembly/model/` later

---

## 4. Where to put new files

| You need… | Put it in… |
|-----------|------------|
| New API endpoint wrapper | `shared/api/` (or typed wrapper in `taskApi.ts`) |
| Shared TypeScript type | `shared/types/` |
| Reusable UI primitive | `shared/ui/` |
| Generic hook (2+ features) | `shared/hooks/` |
| One-feature hook | `features/<name>/hooks/` |

---

## 5. Status

**ACTIVE** — primary home for types, API, UI kit, and generic hooks.

**Future:** optional move `providers/` → `app/providers/` (FE-ARCH-3). Regenerate OpenAPI types when backend adds `response_model` for curriculum/analytics endpoints.
