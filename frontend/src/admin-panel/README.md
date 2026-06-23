# `src/admin-panel/` — admin mini-application

**Status:** LEGACY (separate module, still in production)  
**Redesign plan:** [docs/FRONTEND_STRUCTURE_REDESIGN.md](../../../docs/FRONTEND_STRUCTURE_REDESIGN.md)

---

## 1. What belongs here (current)

Self-contained **admin UI**: shell layout, admin-only pages, admin API client, admin CSS.

Imported as a barrel from `@/admin-panel` in `app/router.jsx` for `/admin/*` routes.

---

## 2. What is here now

| Area | Contents |
|------|----------|
| `pages/` | Dashboard, Users, Assignments, Curriculum, Concepts, CreateTeacher/Admin, … |
| `components/layout/` | `AdminShell` |
| `components/ui/` | Admin-specific UI |
| `api/admin.js` | Admin HTTP client |
| `config/adminSections.js` | Sidebar navigation |
| `hooks/useAsyncResource.js` | Admin data loading |
| `styles/admin-panel.css` | Imported from `main.jsx` |
| `index.js` | Barrel exports for router |

**Not** under `pages/admin/` — historical separation from the rest of `src/pages/`.

---

## 3. Do not add here (during redesign)

- **Do not merge** into `pages/` or refactor routes until a dedicated admin phase (FE-ARCH-5+).
- New student/teacher features → `features/` + `pages/`, not admin-panel.
- Shared types/API already used elsewhere → `shared/`

Admin-only screens may still be added here **short term** if required for ops — but plan to migrate to `pages/admin/` + `features/admin/` later.

---

## 4. Where to put new files

| You need… | Put it in… |
|-----------|------------|
| New admin page (now) | `admin-panel/pages/` + register in router + `adminSections.js` |
| New admin page (future) | `pages/admin/` + `features/admin/` |
| Shared DTO | `shared/types/` |

---

## 5. Status

**LEGACY** mini-app — **ACTIVE** at `/admin/*`.

**TO BE MOVED** (optional, high effort): split into `pages/admin/` + `features/admin/` + `widgets/admin-shell/` — **do not touch** in FE-ARCH-2/3/4 without explicit approval.

**Do not change** admin routes or barrel exports during low-risk structure phases.
