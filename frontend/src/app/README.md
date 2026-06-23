# `src/app/` — application bootstrap

**Status:** ACTIVE  
**Redesign plan:** [docs/FRONTEND_STRUCTURE_REDESIGN.md](../../../docs/FRONTEND_STRUCTURE_REDESIGN.md)

---

## 1. What belongs here

- Application entry wiring: root `App` component, global router.
- Route table (`router.jsx`) — which URL maps to which page.
- *(Future)* `providers/`, `layouts/` when moved from `shared/` (FE-ARCH-3+).

This layer **starts** the app; it does not contain business logic or heavy UI.

---

## 2. What is here now

| File | Role |
|------|------|
| `App.jsx` | Auth bootstrap, token refresh, streak prefetch, wraps `BrowserRouter` + `AppRouter` |
| `router.jsx` | All `<Routes>`: student, teacher, admin, task, demo, auth, support |

Related (not in this folder yet):

- `src/main.jsx` — Vite entry (imports `@/app/App`)
- `src/shared/providers/` — QueryProvider, LanguagesBootstrap

---

## 3. Do not add here

- Page content or feature screens → `pages/` or `features/`
- Editors, task workspace → `widgets/`
- API clients, types, generic UI → `shared/`
- New routes should be registered in `router.jsx`, but route **components** live under `pages/` or `features/`

---

## 4. Where to put new files

| You need… | Put it in… |
|-----------|------------|
| New route | Add `<Route>` in `router.jsx`; screen in `pages/` or `features/.../presentation/pages/` |
| Global provider | `shared/providers/` today; `app/providers/` after FE-ARCH-3 |
| App-wide layout shell | `features/*/layout/` or future `app/layouts/` |

---

## 5. Status

**ACTIVE** — canonical bootstrap path. `main.jsx` → `@/app/App` → `router.jsx`.
