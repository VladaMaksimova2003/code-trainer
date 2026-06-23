# Pascal Curriculum — методология (v1)

Документы в этой папке **не подключаются к runtime**. Это зафиксированная методология до реализации БД.

| Файл | Содержание |
|------|------------|
| `learning_concepts.yaml` | 14 Learning Concepts (LC) |
| `technical_concepts.yaml` | 60 Technical Concepts (TC) + привязка к LC |
| `exercise_pattern_catalog.yaml` | Полный каталог Exercise Patterns |
| `mastery_rules.yaml` | Пороги, освоение TC/LC, открытие глав |
| `review_rules.yaml` | Spaced repetition, forgetting, rotation |
| `pascal_curriculum_track.yaml` | Полный маршрут Pascal + матрицы TC×action по главам |
| `pascal_tc_action_matrix.yaml` | Action masks + плоский индекс матриц |

Загрузка в runtime: `infrastructure/curriculum/loader.py` → `CurriculumService`.
API: `GET /curriculum/{language}/...` (read-only).

Источник языка (known): Python, C++, Java, C#.  
Целевой язык (target): **Pascal** (Free Pascal / Delphi mode).

## Порядок next task (showcase)

Для учеников, которые **уже знают Python / C++ / Java / C#**, маршрут next task в showcase использует action-order **B**:

`translate → assemble → analyze → debug → implement → recognize`

**Почему translate первым, а не assemble**

| Вариант | Плюсы | Минусы |
|---------|--------|--------|
| A: assemble → translate → … | Мягкий вход через блоки, меньше синтаксиса сразу | Не использует уже имеющиеся знания другого языка |
| B: translate → assemble → … | Сразу перенос ментальной модели (Python → Pascal), мотивация «я уже почти умею» | Требует уверенности в базовом синтаксисе source |

Для целевой аудитории platform (переход с известного языка на Pascal) выбран **вариант B**.  
Первая задача в Pascal / Циклы: `counted_loop_tr_python` (Python → Pascal, counted loop).

Реализация: `application/curriculum/curriculum_next_service.py` → `NEXT_TASK_ACTION_ORDER`.

Внутри TC порядок: `study_order_tc` из YAML, затем action-order, затем seed-order спецификации.

## Порядок collections (showcase)

Pascal showcase идёт **conditions → loops** — как в `pascal_curriculum_track.yaml` (глава «Циклы» зависит от «Условия»).

| # | collection_id | LC | route |
|---|---------------|-----|-------|
| 1 | `pascal_conditions_showcase` | conditions | `/learn/pascal/conditions` |
| 2 | `pascal_loops_showcase` | loops | `/learn/pascal/loops` |

`/curriculum/next` обходит collections по этому порядку: пока не завершён conditions — next из conditions; после — из loops; оба завершены — `completed=true`.

Реализация: `application/curriculum/curriculum_collections_registry.py`.
