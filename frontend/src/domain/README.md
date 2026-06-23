# `src/domain/` — pure logic (temporary top-level layer)

**Status:** TO BE MOVED  
**Redesign plan:** [docs/FRONTEND_STRUCTURE_REDESIGN.md](../../../docs/FRONTEND_STRUCTURE_REDESIGN.md)

---

## 1. What belongs here (target)

**Nothing new at top level.** Pure algorithms should eventually live in:

- `features/block-assembly/model/` — block assembly / `buildCode`
- `features/block-reorder/model/` — code document / ranges
- or `shared/lib/` — truly generic, feature-agnostic helpers

This folder is a **temporary** home for TypeScript domain code without React.

---

## 2. What is here now

| Path | Role | Importers |
|------|------|-----------|
| `blockAssembly/` | `buildCode`, `applyDrop`, `normalize`, types, tests | `useTaskSolver`, widgets, `task-editor` |
| `blockReorderAssembly.ts` | Block reorder assembly | task editor |
| `codeBlockRanges.ts` | Code block range math | widgets, domain |
| `codeDocument.ts` | Document model | widgets |
| `codeInputNormalize.ts` | Input normalization | editor pipeline |

All files are **TypeScript**, no JSX.

---

## 3. Do not add here

- React components → `widgets/` or `features/`
- API calls → `shared/api/`
- New top-level `domain/` modules — add under the relevant **`features/*/model/`** instead (even before physical move)

---

## 4. Where to put new files

| You need… | Put it in… |
|-----------|------------|
| Block assembly algorithm | `features/block-assembly/model/` *(target)* — or extend `domain/blockAssembly/` until FE-ARCH-5 move |
| Flowchart payload pure fn | `widgets/flowchart-editor/lib/` or `features/flowchart/model/` |
| Shared string/format pure fn | `shared/lib/` |

---

## 5. Status

**Status:** `domain/blockAssembly` active. Target home: `features/block-assembly/model/` (post FE-ARCH-5; not blocking FE-ARCH-6).

Still **ACTIVE** — production imports must keep working until move phase.

**Do not rename/move** during flowchart-sensitive work without regression on `/tasks/13`, `/tasks/25`.
