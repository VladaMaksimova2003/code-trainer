# Curriculum (Pascal) — TypeScript handoff

Чистый React + TypeScript под ваш репозиторий (Vite + Tailwind, дизайн Toxic Pulse).
Это перенос двух страниц-прототипа в строго типизированный TSX. **Не** рендерится в превью-прототипе — открывать в реальном проекте.

## Файлы

```
handoff/curriculum/
├─ types.ts                              ← доменные типы + CurriculumNavState
├─ actionMeta.ts                         ← action → {label, tone, icon} + классы бейджей
├─ api/curriculumApi.ts                  ← getLanguageTrack / getShowcase / getShowcaseNext
├─ PascalLanguagePage.tsx                ← хаб трека   (/learn/pascal)
├─ PascalShowcasePage.tsx                ← сборник     (/learn/pascal/:chapterSlug)
└─ components/
   ├─ ChapterCard.tsx                    ← карточка сборника (roadmap)
   ├─ SubtopicSection.tsx                ← секция подтемы + grid задач
   ├─ CurriculumShowcaseTaskCard.tsx     ← кликабельная карточка задачи
   ├─ CurriculumStates.tsx               ← loading / error / empty
   ├─ ProgressBar.tsx                    ← lime/purple progress (замените на свой)
   └─ Badge.tsx                          ← бейдж (замените на свой общий)
```

## Куда положить в реальном репо
- `PascalLanguagePage.tsx` → `frontend/src/pages/Student/`
- `PascalShowcasePage.tsx` → `frontend/src/pages/Student/`
- `CurriculumShowcaseTaskCard.tsx` (+ остальные components) → `frontend/src/features/curriculum/components/`
- `types.ts`, `actionMeta.ts`, `api/` → `frontend/src/features/curriculum/`

## Что переиспользовать из вашего кода
- Если уже есть `Badge`, `ProgressBar`, `PageHeader` — удалите локальные копии и поправьте импорты.
- `api/curriculumApi.ts` использует `axios` — замените на ваш http-инстанс/интерсепторы.
- Страницы оборачиваются в `LearningAppShell` на уровне роутинга (здесь не дублируется).

## Сохранённая навигация (не менять)
```ts
navigate(`/tasks/${taskId}`, {
  state: { returnTo, navigationMode: "curriculum", collectionId },
});
```
- Хаб «Продолжить» → первый незавершённый сборник `next_task.task_id`, `returnTo: "/learn/pascal"`.
- Showcase «Продолжить сборник» / клик по задаче → `returnTo: "/learn/pascal/:slug"`.
- Кнопка continue `disabled`, если нет `next_task`.

## Состояния
`CurriculumStates` закрывает loading / error (+retry) / empty. Гость (`progress === null`)
→ карточка прогресса скрыта, статусы на задачах не показываются (`isGuest`).

## Tailwind токены (ожидаются в вашем config)
`bg, surface, surface-2, surface-3, border, border-strong, ink, ink-muted, ink-faint, lime, lime-600, purple`
и утилиты-классы `btn / btn-primary / btn-ghost / btn-sm`. Если имена другие — замените по таблице маппинга из предыдущего хэндоффа.

## TS-заметки
- Все ответы API типизированы (`LanguageTrack`, `ShowcaseResponse`, …) — поправьте поля под реальную схему.
- `sectionsOf()` нормализует `subtopics` | `technical_concepts`.
- Никаких `any`; пропсы компонентов — явные интерфейсы.
