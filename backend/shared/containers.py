"""DI container. Previously: src/config/containers.py"""
from dependency_injector import containers, providers

from shared.config import CheckerSettings
from application.execution.use_cases.check_solution import CheckSolutionUseCase
from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.checker_factory import CheckerFactory
from application.execution.services.checker_service import CheckerService
from application.execution.services.linter_observer import LinterObserver


class Container(containers.DeclarativeContainer):
    checker_settings = providers.Singleton(CheckerSettings)

    docker_runner = providers.Singleton(DockerExecutor)

    checker_factory = providers.Factory(
        CheckerFactory,
        checker_settings=checker_settings,
    )

    checker_service = providers.Factory(
        CheckerService,
        factory=checker_factory,
    )

    linter_observer = providers.Factory(
        LinterObserver,
        factory=checker_factory,
    )

    check_solution_use_case = providers.Factory(
        CheckSolutionUseCase,
        checker=checker_service,
    )
