# Pascal Curriculum MVP — статус и маршрут

Документ фиксирует **runtime showcase MVP** (без Review, Mastery, adaptive learning, изменений worker/solver).

## Что уже работает (Stage 1–9)

| Компонент | Статус |
|-----------|--------|
| YAML curriculum v2 (LC → TC → patterns) | ✅ загрузка, validation API |
| `task_curriculum_link` + primary link | ✅ |
| `student_curriculum_progress` (passed/failed) | ✅ на submission |
| Student UI: human titles, action labels | ✅ |
| `/` — компактный блок «Языки обучения» | ✅ |
| `/learn/pascal` — список 14 сборников | ✅ |
| `/learn/pascal/:chapterSlug` — generic showcase page | ✅ |
| `GET /curriculum/collections`, `/next` | ✅ |
| Showcase seed (idempotent) + E2E verify | ✅ |

## Showcase collections — целевой маршрут (14)

Порядок обучения (`/curriculum/next` и registry):

| # | chapter_key | title_ru | YAML LC (основной) | Задач MVP |
|---|-------------|----------|---------------------|-----------|
| 1 | `variables_and_io` | Переменные и ввод-вывод | program_structure, data_and_variables, operators, files | 6 |
| 2 | `conditions` | Условия | conditions | 6 |
| 3 | `loops` | Циклы | loops | 7 |
| 4 | `functions` | Функции | functions | 6 |
| 5 | `arrays` | Массивы | collections | 6 |
| 6 | `strings` | Строки | collections | 6 |
| 7 | `records` | Записи | collections | 6 |
| 8 | `files` | Файлы | files | 6 |
| 9 | `procedures_and_parameters` | Процедуры и параметры | functions | 6 |
| 10 | `modules` | Модули | modules | 6 |
| 11 | `recursion` | Рекурсия | functions | 6 |
| 12 | `algorithms` | Алгоритмы | data_processing / algorithms | 6 |
| 13 | `data_structures` | Структуры данных | advanced_structures | 6 |
| 14 | `oop` | ООП | oop | 6 |

**Итого:** ~85 showcase-задач (5–7 на сборник).

## Actions в showcase

| action | pattern (примеры) | builder |
|--------|-------------------|---------|
| translate | tr_python_to_pascal_code, tr_cpp_to_pascal_code | translation_to_pascal |
| assemble | asm_blocks_to_code_pascal | block_reorder_pascal |
| implement | imp_text_spec_to_pascal, imp_io_tests_pascal | pascal_io_program |
| analyze | ana_pascal_code_predict_output | pascal_io_program |
| debug | dbg_pascal_code_fix, dbg_pascal_logic_fix*, dbg_transfer_syntax_fix | pascal_debug_starter |

\* `dbg_pascal_logic_fix` — только TC с loop-матрицей.

**recognize** (`rec_*`) — в YAML есть, в showcase **не сидится** (нет quiz task type).

## API (student)

```
GET /curriculum/collections
GET /curriculum/next
GET /curriculum/pascal/showcase/{route_suffix}
GET /curriculum/pascal/showcase/{route_suffix}/student
GET /curriculum/pascal/showcase/{route_suffix}/next
```

Admin/debug сохраняет slug, group, TC, pattern в `code_examples.curriculum_showcase`.

## Seed

```bash
cd backend
# все сборники
poetry run python scripts/seed_pascal_curriculum_showcase.py
# один сборник
poetry run python scripts/seed_pascal_curriculum_showcase.py --collection loops
```

## E2E

```bash
# из worker-контейнера (нужен Docker для Pascal runner)
docker exec code_trainer_dev-worker-1 sh -c "cd /app && python scripts/verify_pascal_showcase_e2e.py"

# один сборник (локально или в api-контейнере — без execution smoke)
poetry run python scripts/verify_pascal_showcase_e2e.py --collection conditions
```

## Вне scope MVP

- Review / spaced repetition
- Mastery gates / chapter unlock
- Adaptive next-task
- Изменения worker, solver, Docker
- Новые task types (quiz/recognize)

## Next-task order

1. Внутри сборника: `study_order_tc` → action-order B (`translate → assemble → analyze → debug → implement`) → seed order.
2. Между сборниками: порядок таблицы выше; незавершённый сборник блокирует следующий.

См. также `README.md` в этой папке.
