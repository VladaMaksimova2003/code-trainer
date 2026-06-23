# Code Trainer — UI brief для Claude (комментарии, поддержка, уведомления)

Используй этот файл как **единственный контекст** о проекте. Генерируй **React + Tailwind JSX** (не TypeScript, если не указано иное), в стиле существующего приложения.

---

## 1. О проекте

**Code Trainer** — образовательная веб-платформа для программирования (дипломный проект).

- **Стек:** React 18, Vite, React Router, Tailwind CSS, Axios, Monaco Editor
- **Роли:** student, teacher, admin
- **Язык UI:** русский
- **Тема:** тёмная, акцент **lime** `#8eff01`, вторичный **purple** `#8b53fe`

Студент решает задачи на странице `/tasks/:id`. Препод смотрит решения студентов из групп и переходит на ту же страницу в режиме **teacher review** (код read-only).

---

## 2. Design system (обязательно соблюдать)

### Цвета (Tailwind tokens)

| Token | Hex / value | Назначение |
|-------|-------------|------------|
| `bg` | `#0a0e15` | фон страницы |
| `surface` | `#141a24` | карточки, панели |
| `surface-2` | `#1d2331` | вторичные блоки |
| `border` | `#262e3c` | границы |
| `ink` | `#eef2f7` | основной текст |
| `ink-muted` | `#9aa6b6` | вторичный текст |
| `ink-faint` | `#626d7e` | подписи |
| `lime` | `#8eff01` | primary CTA («Прогнать») |
| `lime-soft` | `rgba(142,255,1,.14)` | подсветка непрочитанного |
| `purple` | `#8b53fe` | режим просмотра препода |
| `purple-soft` | `rgba(139,83,254,.16)` | баннер teacher review |
| `danger` | `#ff4d6a` | ошибки, провал тестов |

### Шрифты

- UI: `Inter` (`font-sans`)
- Код: `JetBrains Mono` (`font-mono`)

### Готовые CSS-классы (из `index.css`)

- Кнопки: `btn`, `btn-ghost`, `btn-sm`, `btn-primary` (lime)
- Иконка в шапке: `icon-btn`
- Вкладки настроек: `tabbar` + класс `on` для активной
- Шапка задачи: `topbar`, `crumb`, `badge`, `badge-muted`, `badge-purple`

### Паттерны

- Скругления: `rounded-md` (8px), `rounded-xl` (22px для dropdown)
- Тонкие границы: `border border-border`
- Primary action — **lime** на тёмном фоне, не синий
- Destructive / errors — `danger`, не generic red-500

---

## 3. Ключевая страница: решение задачи

**Маршрут:** `/tasks/:id`  
**Layout:** full-screen, **без** бокового StudentAppShell (своя шапка).

```
┌─────────────────────────────────────────────────────────────────┐
│ topbar: ← Каталог | тип / название | badge | 🔔 | avatar        │
│         Задача N из M | ← Предыдущая | Следующая →               │
├──────────┬──────────────────────────────────────────────────────┤
│ LeftRail │ EditorMain (Monaco / blocks / flowchart)             │
│ условие  │                                                      │
│ теория   │                                                      │
│ ~280px   │                                                      │
├──────────┴──────────────────────────────────────────────────────┤
│ StudentBottomPanel (height ~220px + tab bar 44px)               │
│ [● Тесты  2/5] [● Ошибки  1]              [▶ Прогнать]        │
│ ─────────────────────────────────────────────────────────────── │
│ содержимое активной вкладки (таблица тестов или список ошибок)  │
└─────────────────────────────────────────────────────────────────┘
```

**Файлы:**

| Файл | Роль |
|------|------|
| `src/pages/TaskPages/student/StudentTaskWorkspace.jsx` | compositor |
| `src/pages/TaskPages/student/StudentTaskHeader.jsx` | шапка |
| `src/pages/TaskPages/student/StudentLeftRail.jsx` | левая колонка |
| `src/pages/TaskPages/student/StudentEditorMain.jsx` | редактор |
| `src/pages/TaskPages/StudentBottomPanel.jsx` | **нижняя панель: вкладки Тесты / Ошибки** |
| `src/features/solve-task/hooks/useTaskSolver.js` | логика, teacher review |

### Режим teacher review

Включается через `navigate('/tasks/:id', { state: { teacherReview: { submissionId, studentName } } })`.

- Фиолетовый баннер: «Просмотр · {имя студента} · статус решения»
- Редактор **readOnly**
- Кнопка «Прогнать» **скрыта** (`isTeacherReview={true}`)
- API: `GET /teacher/submissions/:submissionId` — код и метаданные

---

## 4. Backend API (уже реализован)

Base URL: `VITE_API_BASE_URL` (dev: `http://127.0.0.1:8001`).

### 4.1 Комментарии преподавателя к submission

| Method | Path | Кто |
|--------|------|-----|
| GET | `/teacher/submissions/{submission_id}/comments` | teacher |
| POST | `/teacher/submissions/{submission_id}/comments` | teacher |
| PATCH | `/teacher/submissions/{submission_id}/comments/{comment_id}` | teacher (свои) |
| DELETE | `/teacher/submissions/{submission_id}/comments/{comment_id}` | teacher |
| GET | `/student/submissions/{submission_id}/comments` | student (своё) |

**POST body:** `{ "body": "текст комментария" }` (1–4096 символов)

**Response item:**

```json
{
  "id": 1,
  "submission_id": 42,
  "teacher_id": 5,
  "teacher_name": "Иванов",
  "body": "Проверь граничный случай n=0",
  "created_at": "2026-06-04T12:00:00+00:00",
  "updated_at": "2026-06-04T12:00:00+00:00"
}
```

### 4.2 Поддержка / обратная связь

| Method | Path | Кто |
|--------|------|-----|
| GET | `/support/templates?context=task\|general` | student/teacher |
| POST | `/support/tickets` | создать обращение |
| GET | `/support/tickets/mine` | мои тикеты |
| GET | `/support/tickets/inbox` | teacher inbox |
| GET | `/support/tickets/admin/inbox` | admin |
| GET | `/support/tickets/{id}` | детали + messages |
| POST | `/support/tickets/{id}/messages` | сообщение в диалоге |
| PATCH | `/support/tickets/{id}` | `{ "status" }` или `{ "escalate": true }` |

**Категории:** `task_content`, `autograder`, `technical`, `account`, `other`

**POST create:**

```json
{
  "category": "task_content",
  "body": "минимум 20 символов...",
  "subject": "опционально",
  "task_id": 12,
  "submission_id": 55,
  "context": { "page_url": "/tasks/12" }
}
```

**Маршрутизация:** `task_content` / `autograder` → препод-автор задания; `technical` / `account` / `other` → админ.

**GET templates** — chips для UI (категория + draft-текст).

### 4.3 In-app уведомления

| Method | Path |
|--------|------|
| GET | `/notifications?unread_only=false` |
| GET | `/notifications/unread-count` |
| PATCH | `/notifications/{id}/read` |
| POST | `/notifications/read-all` |

**Kinds:** `ticket_created`, `ticket_reply`, `ticket_status` (+ в будущем комментарии)

**Существующий UI:** `src/features/student/layout/StudentNotificationsButton.jsx` — dropdown с mock-данными, нужно подключить к API.

---

## 5. Функции — UX-решения (рекомендуемые)

### 5.1 Комментарий преподавателя (твоё видение + детали)

**Где:** третья вкладка в `StudentBottomPanel`: **«Комментарии»** (рядом с «Тесты» и «Ошибки»).

| Режим | Поведение вкладки |
|-------|-------------------|
| Student | read-only список; badge с числом комментариев; если 0 — вкладка видна, empty state |
| Teacher review | список + textarea + «Отправить»; edit/delete своих комментариев (⋯ меню) |

**Визуал комментария:**

```
┌─────────────────────────────────────────────┐
│ Иванов · 4 июн, 14:32                       │
│ Проверь граничный случай n=0 — цикл не      │
│ обрабатывает пустой ввод.                   │
└─────────────────────────────────────────────┘
```

- Карточка: `bg-surface-2 border border-border rounded-lg px-3.5 py-2.5`
- Имя препода: `text-[13px] font-semibold text-ink`
- Текст: `text-[13px] text-ink-muted leading-snug`

**Не делать:** read receipts, «прочитано».

**Уведомление ученику:** колокольчик → «Преподаватель оставил комментарий к задаче «…»» → клик открывает `/tasks/:taskId?tab=comments` (или state) и вкладку «Комментарии».

**Точка входа препода:** уже есть `TeacherSolutionsPanel` → «К заданию» → teacher review → вкладка «Комментарии» активна по умолчанию (optional).

---

### 5.2 «Сообщить об ошибке» (на странице задачи)

**Не отдельная страница** — **модальное окно** (centered или slide-over справа).

**Точка входа (ghost, не lime):**

- В `StudentTaskHeader` справа от breadcrumb: текстовая кнопка `Сообщить об ошибке` (`btn-ghost btn-sm`, `text-ink-faint`)
- Или ссылка внизу `StudentLeftRail` мелким шрифтом

**Модалка — один экран (hybrid, не wizard-бот):**

```
┌─ Сообщить об ошибке ─────────────────── [×] ┐
│ Задание: «Сумма чисел» (автоподстановка)    │
│                                              │
│ Что не так?                                  │
│ [Ошибка в условии] [Неверный тест]           │
│ [Автопроверка] [Другое]     ← chips из API   │
│                                              │
│ Описание *                                   │
│ ┌──────────────────────────────────────────┐ │
│ │ Тест №3: ожидается 0, но...              │ │
│ └──────────────────────────────────────────┘ │
│ мин. 20 символов                             │
│                                              │
│        [Отмена]  [Отправить]                 │
└──────────────────────────────────────────────┘
```

- Chip клик **подставляет draft** в textarea (редактируемый)
- `task_id`, `submission_id` (последняя попытка), `page_url` — **скрыто**, в `context`
- Успех: toast «Обращение #12 отправлено преподавателю» + ссылка «Мои обращения»

**Категории на странице задачи:** по умолчанию `task_content` или `autograder` (переключатель chips), **не** technical — для tech есть «Помощь».

---

### 5.3 «Помощь / Поддержка» (технические проблемы)

**Отдельный раздел**, не смешивать с комментариями к оценке.

**Точки входа:**

1. **Настройки** — новая вкладка `Помощь` в `SettingsLayout` (`/settings/help`)
2. **Sidebar** — пункт «Помощь» внизу (опционально)
3. **Footer dropdown уведомлений** — «Все обращения →»

**Страница `/settings/help` (или `/support`):**

```
┌─ Помощь ─────────────────────────────────────┐
│ [+ Новое обращение]                          │
├──────────────────────────────────────────────┤
│ ● Техническая · Редактор не сохраняет код    │
│   Открыто · обновлено 2 ч назад              │
├──────────────────────────────────────────────┤
│ ○ Аккаунт · Не могу войти                    │
│   Решено · 1 день назад                      │
└──────────────────────────────────────────────┘
```

**Деталь тикета `/support/tickets/:id` — chat-layout:**

```
┌─ #12 · Техническая проблема ─── статус: В работе ─┐
│ [system] Статус изменён: Открыто → В работе       │
│ [Вы] Редактор не сохраняет код после...           │
│ [Поддержка] Уточните браузер и ОС                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ Напишите ответ...                           │ │
│ └─────────────────────────────────────────────┘ │
│ [Отправить]                                       │
└───────────────────────────────────────────────────┘
```

**Создание:** модалка или отдельный экран с `GET /support/templates?context=general`.

**Teacher:** inbox в кабинете препода — вкладка «Обращения по заданиям» (список из `/support/tickets/inbox`).

**Admin:** `/admin/support` — inbox `/support/tickets/admin/inbox`.

---

## 6. Уведомления (колокольчик)

Расширить dropdown (`StudentNotificationsButton`):

| kind | title пример | действие по клику |
|------|--------------|-------------------|
| comment (future) | Комментарий к задаче | `/tasks/:id` + tab comments |
| ticket_reply | Ответ в обращении #12 | `/support/tickets/12` |
| ticket_created | Новое обращение по заданию | teacher inbox |
| ticket_status | Статус обращения изменён | `/support/tickets/:id` |

- Непрочитанные: `bg-lime-soft/20`, без lime border на всём item
- Badge на колокольчике: `GET /notifications/unread-count`
- Клик по item: `PATCH .../read` + navigate

**Teacher topbar:** тот же компонент или shared `NotificationsButton`.

---

## 7. Что нужно сгенерировать

Попроси Claude выдать **готовые JSX-компоненты** (можно несколькими файлами) + краткую карту интеграции:

### Must have

1. **`SubmissionCommentsTab.jsx`** — содержимое вкладки для `StudentBottomPanel`
2. **`TeacherCommentComposer.jsx`** — textarea + submit (teacher review)
3. **`ReportTaskIssueModal.jsx`** — модалка «Сообщить об ошибке»
4. **`SupportTicketsPage.jsx`** — список моих обращений
5. **`SupportTicketDetailPage.jsx`** — диалог тикета
6. **`CreateSupportTicketModal.jsx`** — создание (general context)
7. **`NotificationsDropdown.jsx`** — улучшенный dropdown с API shape
8. **`TeacherSupportInboxPanel.jsx`** — для кабинета препода

### Patches (опиши diff, не обязательно полный файл)

- `StudentBottomPanel.jsx` — добавить TabButton «Комментарии»
- `StudentTaskHeader.jsx` — кнопка «Сообщить об ошибке»
- `SettingsLayout.jsx` — вкладка «Помощь»
- `router.jsx` — маршруты `/settings/help`, `/support/tickets/:id`

### API layer (заглушки)

```javascript
// features/support/api/supportApi.js
// features/notifications/api/notificationsApi.js
// features/analytics/api/submissionCommentsApi.js
```

С паттерном как в `features/analytics/api/analyticsApi.js` (axios + optional mock).

---

## 8. Ограничения для генерации

- **Не** менять общую цветовую схему (не светлая тема, не синий primary)
- **Не** использовать Material UI / shadcn — только Tailwind + существующие классы
- **Не** показывать «прочитано» / typing indicator
- Модалки: `bg-surface border border-border rounded-xl shadow`
- Mobile: bottom panel stack vertically; modals `w-[min(480px,calc(100vw-24px))]`
- Accessibility: `aria-label`, focus trap в модалках
- Тексты UI на **русском**

---

## 9. Mock data для прототипа

```javascript
export const MOCK_COMMENTS = [
  {
    id: 1,
    teacher_name: "Петрова А.",
    body: "Хорошее решение, но добавь проверку на пустой ввод.",
    created_at: "2026-06-04T10:00:00Z",
  },
]

export const MOCK_TICKETS = [
  {
    id: 12,
    subject: "Ошибка в задании: Сумма чисел",
    category: "task_content",
    status: "open",
    target: "teacher",
    updated_at: "2026-06-04T09:00:00Z",
  },
]
```

---

## 10. Referenced existing code snippets

### Tab bar pattern (StudentBottomPanel)

```jsx
<TabButton
  active={activeTab === "comments"}
  dotClass={commentCount > 0 ? "bg-purple" : "bg-ink-faint"}
  label="Комментарии"
  badge={String(commentCount)}
  badgeClass={commentCount > 0 ? "bg-purple-soft text-purple ..." : "..."}
  onClick={() => setBottomTab("comments")}
/>
```

### Teacher review banner (StudentTaskWorkspace)

```jsx
{isTeacherReview && (
  <div className="shrink-0 border-b border-purple/30 bg-purple-soft/40 px-5 py-2.5 text-sm text-[#d4bcff]">
    Просмотр · {studentName} · ...
  </div>
)}
```

---

*Конец брифа. Версия: 2026-06-05*
