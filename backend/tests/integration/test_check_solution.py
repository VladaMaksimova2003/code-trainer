import pytest
from typing import Iterator

from application.execution.dto import CheckSolutionDTO
from application.execution.use_cases.check_solution import CheckSolutionUseCase
from application.execution.services.linter_observer import LinterObserver
from infrastructure.execution.execution_guard import mark_worker_context
from shared.containers import Container


@pytest.fixture(autouse=True)
def _allow_worker_execution():
    mark_worker_context()
    yield


@pytest.fixture
def constructions():
    return [
        "function_definition",
        "for_loop",
        "if_statement",
        "binary_expression",
        "function_call",
        "return_statement",
        "identifier",
    ]


@pytest.fixture
def code_samples():
    return {
        "python": {
            "correct": """
def sum_positive_numbers(numbers):
    total = 0
    for n in numbers:
        if n > 0:
            total += n
    print(total)
    return total
""",
            "incorrect": """
def sum_positive_numbers(numbers):
    total = 0
    for n in numbers
        if n > 0:
            total += n
    return total
""",
        },
        "cpp": {
            "correct": """
#include <iostream>

int sum_positive_numbers(int numbers[], int size) {
    int total = 0;
    for (int i = 0; i < size; i++) {
        if (numbers[i] > 0) {
            total += numbers[i];
        }
    }
    std::cout << total << std::endl;
    return total;
}

int main() {
    int arr[5] = {1, -2, 3, 0, 5};
    sum_positive_numbers(arr, 5);
    return 0;
}
""",
            "incorrect": """
#include <iostream>
int main() {
    int sum = 0
    for (int i = 0; i < 5; i++) {
        sum += i;
    }
    std::cout << sum;
    return 0;
}
""",
        },
    }


@pytest.fixture(scope="function")
def container() -> Iterator[Container]:
    yield Container()


@pytest.fixture(scope="function")
def check_solution_use_case(container: Container) -> CheckSolutionUseCase:
    return container.check_solution_use_case()


@pytest.fixture(scope="function")
def linter_observer(container: Container) -> LinterObserver:
    return container.linter_observer()


@pytest.mark.parametrize("language", ["python", "cpp"])
def test_check_solution_success(
    check_solution_use_case: CheckSolutionUseCase,
    code_samples,
    constructions,
    language,
):
    dto = CheckSolutionDTO(
        code=code_samples[language]["correct"],
        language=language,
        constructions=constructions,
        task_id=1,
    )

    result = check_solution_use_case.execute(dto)

    if not result.success:
        print("\n--- DEBUG INFO ---")
        print("Errors:")
        for e in result.errors:
            print(" -", e)
    assert result.success is True, f"Ожидалось успешное выполнение для языка {language}"
    assert (
        result.errors == []
    ), f"Ошибки при корректном коде {language}: {result.errors}"


@pytest.mark.parametrize("language", ["python", "cpp"])
def test_check_solution_with_error(
    check_solution_use_case: CheckSolutionUseCase,
    code_samples,
    constructions,
    language,
):
    dto = CheckSolutionDTO(
        code=code_samples[language]["incorrect"],
        language=language,
        constructions=constructions,
        task_id=2,
    )

    result = check_solution_use_case.execute(dto)

    print(f"\nОшибки ({language}):")
    for e in result.errors:
        print(e)

    assert result.success is False, f"Должны быть ошибки для языка {language}"
    assert len(result.errors) > 0, f"Ошибки не найдены для языка {language}"


@pytest.mark.parametrize("language", ["python", "cpp"])
def test_linter_with_error(linter_observer, code_samples, constructions, language):
    dto = CheckSolutionDTO(
        code=code_samples[language]["incorrect"],
        language=language,
        constructions=constructions,
        task_id=3,
    )

    result = linter_observer.update(dto)

    print(f"\nЛинтер ошибки ({language}):")
    for e in result.errors:
        print(e)

    assert (
        result.success is False
    ), f"Линтер должен обнаружить ошибки для языка {language}"
    assert len(result.errors) > 0, f"Линтер не нашёл ошибок для {language}"


@pytest.mark.parametrize("language", ["python", "cpp"])
def test_linter_success(linter_observer, code_samples, constructions, language):
    dto = CheckSolutionDTO(
        code=code_samples[language]["correct"],
        language=language,
        constructions=constructions,
        task_id=4,
    )

    result = linter_observer.update(dto)

    print(f"\nЛинтер проверка корректного кода ({language}):")
    for e in result.errors:
        print(e)

    assert (
        result.success is True
    ), f"Линтер не должен находить ошибки для корректного кода {language}"
    assert (
        result.errors == []
    ), f"Линтер ошибочно нашёл ошибки для {language}: {result.errors}"
