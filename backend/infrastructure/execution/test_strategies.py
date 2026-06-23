"""Test strategies — Docker-only execution."""
from __future__ import annotations

import base64
import textwrap
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from domain.entities.language import LanguageConfig
from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.execution_profiler import ExecutionProfiler, profiling_enabled
from infrastructure.execution.execution_workspace import (
    binary_path,
    new_workspace_id,
    source_path,
)
from infrastructure.execution.output_parser import parse_diagnostics, remap_wrapped_source_lines
from infrastructure.execution.test_case_result import TestCaseResult


def _case_value_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return str(value)

    value_type = value.get("type")
    raw_value = value.get("value")
    if value_type == "multi" and isinstance(raw_value, list):
        return "\n".join(str(item) for item in raw_value)
    if value_type == "matrix" and isinstance(raw_value, list):
        return "\n".join(
            " ".join(str(cell) for cell in row) if isinstance(row, list) else str(row)
            for row in raw_value
        )
    if value_type == "json":
        return str(value.get("raw") if value.get("raw") is not None else raw_value or "")
    if "value" in value:
        return str(raw_value if raw_value is not None else "")
    return str(value)


def case_inputs(tc: dict) -> str:
    return _case_value_to_text(tc.get("inputs", tc.get("input", "")))


def case_output(tc: dict) -> str:
    return _case_value_to_text(
        tc.get("output", tc.get("expected_output", tc.get("expected", "")))
    )


def stdin_lines_from_inputs(inputs_str: str, reference_code: str = "") -> list[str]:
    """Split stored test inputs into lines for patched ``input()`` / line-based stdin."""
    from application.curriculum.content.v4_test_cases_io import stdin_tokens_to_lines

    raw = str(inputs_str or "")
    if not raw.strip():
        return []
    normalized = stdin_tokens_to_lines(raw, reference_code)
    if "\n" in normalized:
        return [line for line in normalized.splitlines() if line.strip() or line == "0"]
    parts = [part for part in raw.split() if part]
    return parts if parts else [raw]


def truncate(text: str, max_len: int = 300) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text


def _diagnostic_text_from_run(result: Any, *, line_offset: int = 0) -> str:
    parts: list[str] = []
    for blob in (getattr(result, "stderr", None), getattr(result, "stdout", None)):
        text = str(blob or "").strip()
        if not text:
            continue
        if line_offset:
            text = remap_wrapped_source_lines(text, line_offset)
        parsed = parse_diagnostics(text)
        if parsed:
            parts.extend(parsed)
            continue
        for line in text.splitlines():
            candidate = line.strip()
            if candidate.lower().startswith(("error:", "fatal:", "warning:")):
                parts.append(candidate)

    seen: set[str] = set()
    ordered: list[str] = []
    for msg in parts:
        if msg not in seen:
            seen.add(msg)
            ordered.append(msg)
    if ordered:
        return "\n".join(ordered[:3])
    stderr = str(getattr(result, "stderr", "") or "").strip()
    return truncate(stderr) if stderr else ""


def _case_marker(case_num: int) -> str:
    return f"__CT_CASE_{case_num}__"


def _parse_batch_stdout(stdout: str, case_count: int) -> list[str]:
    text = stdout or ""
    outputs: list[str] = []
    for case_num in range(1, case_count + 1):
        marker = _case_marker(case_num)
        start = text.find(marker)
        if start == -1:
            outputs.append("")
            continue
        start += len(marker)
        while start < len(text) and text[start] in "\r\n":
            start += 1
        end = text.find(_case_marker(case_num + 1), start)
        chunk = text[start:end] if end != -1 else text[start:]
        outputs.append(chunk.strip())
    return outputs


def _strip_case_markers(text: str) -> str:
    cleaned = text or ""
    for case_num in range(1, 32):
        cleaned = cleaned.replace(_case_marker(case_num), " ")
    return " ".join(cleaned.split()).strip()


def _actual_from_run(result: Any) -> str:
    actual = _strip_case_markers((result.stdout or "").strip())
    if actual:
        return actual
    diagnostic = _diagnostic_text_from_run(result)
    if diagnostic:
        return diagnostic
    if result.returncode != 0:
        return f"(код выхода {result.returncode})"
    return "(пустой вывод)"


class TestStrategy(ABC):
    def __init__(self, docker: DockerExecutor) -> None:
        self._docker = docker

    @abstractmethod
    def run(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict],
    ) -> list[TestCaseResult]:
        ...


class UnsupportedTestStrategy(TestStrategy):
    def run(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict],
    ) -> list[TestCaseResult]:
        from infrastructure.execution.test_case_result import TestCaseResult

        return [
            TestCaseResult(
                case=i + 1,
                status="SKIPPED",
                inputs=case_inputs(tc),
                expected=case_output(tc),
                actual="",
                message=(
                    f"Language '{cfg.id}' does not support test execution "
                    f"(strategy={cfg.test.strategy})."
                ),
            )
            for i, tc in enumerate(test_cases)
        ]


class StdinLinesTestStrategy(TestStrategy):
    @staticmethod
    def stdin_wrapper_line_offset() -> int:
        return len(StdinLinesTestStrategy._wrap("", "").splitlines())

    @staticmethod
    def _remap_wrapped_error(text: str) -> str:
        return remap_wrapped_source_lines(text, StdinLinesTestStrategy.stdin_wrapper_line_offset())

    def run(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict],
    ) -> list[TestCaseResult]:
        from infrastructure.execution.test_case_result import TestCaseResult

        if not cfg.docker or not cfg.docker.image:
            return UnsupportedTestStrategy(self._docker).run(cfg, code, test_cases)

        run_cmd = cfg.docker.run or "python {filename}"
        timeout = cfg.test.timeout_seconds

        results: list[TestCaseResult] = []

        for i, tc in enumerate(test_cases):
            inputs_str = case_inputs(tc)
            expected = case_output(tc).strip()
            wrapped = self._wrap(code, inputs_str)
            try:
                result = self._docker.run_shell(
                    cfg.docker.image,
                    run_cmd,
                    wrapped,
                    cfg.file_extension,
                    timeout=timeout,
                )
                actual = self._remap_wrapped_error(_actual_from_run(result))
                stderr = self._remap_wrapped_error(result.stderr.strip())
                duration_ms = getattr(result, "duration_ms", 0) or 0
                if result.returncode != 0 and stderr:
                    err_text = self._remap_wrapped_error(
                        _diagnostic_text_from_run(result, line_offset=self.stdin_wrapper_line_offset())
                        or truncate(stderr)
                    )
                    results.append(
                        TestCaseResult(
                            case=i + 1,
                            status="ERROR",
                            inputs=inputs_str,
                            expected=expected,
                            actual="",
                            message=err_text,
                            duration_ms=duration_ms,
                        )
                    )
                elif (result.stdout or "").strip() == expected:
                    results.append(
                        TestCaseResult(
                            case=i + 1,
                            status="PASSED",
                            inputs=inputs_str,
                            expected=expected,
                            actual=(result.stdout or "").strip(),
                            duration_ms=duration_ms,
                        )
                    )
                else:
                    fail_msg = ""
                    if not actual or "__CT_CASE_" in actual:
                        fail_msg = "Неверный или пустой вывод программы"
                    results.append(
                        TestCaseResult(
                            case=i + 1,
                            status="FAILED",
                            inputs=inputs_str,
                            expected=expected,
                            actual=actual,
                            message=self._remap_wrapped_error(fail_msg) if fail_msg else fail_msg,
                            duration_ms=duration_ms,
                        )
                    )
            except Exception as exc:
                message = str(exc)
                if "TimeoutExpired" in type(exc).__name__:
                    message = f"Time limit exceeded ({timeout}s)"
                message = self._remap_wrapped_error(message)
                results.append(
                    TestCaseResult(
                        case=i + 1,
                        status="ERROR",
                        inputs=inputs_str,
                        expected=expected,
                        actual="",
                        message=message,
                    )
                )

        return results

    def _run_batch(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict],
        run_cmd: str,
        timeout: int,
    ) -> list[TestCaseResult]:
        from infrastructure.execution.test_case_result import TestCaseResult

        batch_code = self._build_batch_script(code, test_cases)
        total_timeout = max(timeout * (len(test_cases) + 1), timeout + 2)
        try:
            result = self._docker.run_shell(
                cfg.docker.image,
                run_cmd,
                batch_code,
                cfg.file_extension,
                timeout=total_timeout,
            )
        except Exception as exc:
            message = str(exc)
            if "TimeoutExpired" in type(exc).__name__:
                message = f"Time limit exceeded ({total_timeout}s)"
            return [
                TestCaseResult(
                    case=i + 1,
                    status="ERROR",
                    inputs=case_inputs(tc),
                    expected=case_output(tc).strip(),
                    actual="",
                    message=message,
                )
                for i, tc in enumerate(test_cases)
            ]

        outputs = _parse_batch_stdout(result.stdout, len(test_cases))
        per_case_ms = max(
            1,
            int(getattr(result, "duration_ms", 0) / max(len(test_cases), 1)),
        )
        stderr = (result.stderr or "").strip()
        results: list[TestCaseResult] = []

        if result.returncode != 0 and stderr and not any(outputs):
            compile_error = _diagnostic_text_from_run(result)
            for i, tc in enumerate(test_cases):
                inputs_str = case_inputs(tc)
                expected = case_output(tc).strip()
                results.append(
                    TestCaseResult(
                        case=i + 1,
                        status="ERROR",
                        inputs=inputs_str,
                        expected=expected,
                        actual="",
                        message=compile_error,
                        duration_ms=per_case_ms,
                    )
                )
            return results

        for i, tc in enumerate(test_cases):
            inputs_str = case_inputs(tc)
            expected = case_output(tc).strip()
            stdout = outputs[i] if i < len(outputs) else ""
            if result.returncode != 0 and stderr and not stdout:
                actual = _actual_from_run(result)
                results.append(
                    TestCaseResult(
                        case=i + 1,
                        status="ERROR",
                        inputs=inputs_str,
                        expected=expected,
                        actual="",
                        message=_diagnostic_text_from_run(result) or truncate(stderr),
                        duration_ms=per_case_ms,
                    )
                )
            elif stdout == expected:
                results.append(
                    TestCaseResult(
                        case=i + 1,
                        status="PASSED",
                        inputs=inputs_str,
                        expected=expected,
                        actual=stdout,
                        duration_ms=per_case_ms,
                    )
                )
            else:
                results.append(
                    TestCaseResult(
                        case=i + 1,
                        status="FAILED",
                        inputs=inputs_str,
                        expected=expected,
                        actual=stdout or _actual_from_run(result),
                        duration_ms=per_case_ms,
                    )
                )
        return results

    @staticmethod
    def _build_batch_script(code: str, test_cases: list[dict]) -> str:
        blocks: list[str] = [
            "import builtins as _builtins",
            "_input_lines = []",
            "_input_idx = 0",
            "def _patched_input(prompt=''):",
            "    global _input_idx",
            "    if _input_idx < len(_input_lines):",
            "        val = _input_lines[_input_idx]; _input_idx += 1; return val",
            "    return ''",
            "_builtins.input = _patched_input",
        ]
        for case_num, tc in enumerate(test_cases, start=1):
            inputs_str = case_inputs(tc)
            lines = [repr(line) for line in stdin_lines_from_inputs(inputs_str)]
            if not lines:
                lines = ["''"]
            blocks.append(f"print({_case_marker(case_num)!r})")
            blocks.append(f"_input_lines = [{', '.join(lines)}]")
            blocks.append("_input_idx = 0")
            blocks.append("try:")
            for line in code.splitlines():
                blocks.append(f"    {line}" if line else "")
            blocks.append("except Exception:")
            blocks.append("    import traceback")
            blocks.append("    traceback.print_exc()")
        return "\n".join(blocks) + "\n"

    @staticmethod
    def _wrap(code: str, inputs_str: str) -> str:
        lines = [repr(line) for line in stdin_lines_from_inputs(inputs_str)]
        if not lines:
            lines = ["''"]
        lines_literal = "[" + ", ".join(lines) + "]"
        wrapper = textwrap.dedent(f"""\
            import builtins as _builtins
            _input_lines = {lines_literal}
            _input_idx = 0
            def _patched_input(prompt=''):
                global _input_idx
                if _input_idx < len(_input_lines):
                    val = _input_lines[_input_idx]; _input_idx += 1; return val
                return ''
            _builtins.input = _patched_input

        """)
        return wrapper + code


class CompileAndRunTestStrategy(TestStrategy):
    def _format_one_shot(
        self,
        cfg: LanguageConfig,
        container_path: str,
        app_path: str,
    ) -> str:
        one_shot = cfg.test.docker_one_shot
        if not one_shot:
            compile_parts = cfg.test.compile or ()
            run_parts = cfg.test.run or ()
            if compile_parts and run_parts:
                one_shot = " ".join(compile_parts) + " && " + " ".join(run_parts)
        if not one_shot:
            raise ValueError("docker_one_shot is required for batch execution")
        return one_shot.format(
            filename=container_path,
            source=container_path,
            binary=app_path,
            output=app_path,
        )

    def _run_one_shot_batch(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict],
        timeout: int,
        one_shot: str,
    ) -> list[TestCaseResult]:
        from infrastructure.execution.test_case_result import TestCaseResult

        ext = cfg.file_extension
        ws_id = new_workspace_id()
        container_path = source_path(ws_id, ext)
        app_path = binary_path(ws_id)
        run_cmd = self._format_one_shot(cfg, container_path, app_path)
        code_b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")

        steps = [f"echo {code_b64} | base64 -d > {container_path}"]
        for index, tc in enumerate(test_cases, start=1):
            inputs_str = case_inputs(tc)
            steps.append(f"echo {_case_marker(index)}")
            if inputs_str:
                inp_b64 = base64.b64encode(inputs_str.encode("utf-8")).decode("ascii")
                # Redirect stdin to a file: piping into run_cmd breaks leading
                # shell assignments (e.g. ws="$CT_WORKSPACE" in C# one-shot).
                steps.append(f'echo {inp_b64} | base64 -d > "$CT_WORKSPACE/.stdin"')
                steps.append(f"{run_cmd} < \"$CT_WORKSPACE/.stdin\"")
            else:
                steps.append(run_cmd)

        shell_cmd = " && ".join(steps)
        total_timeout = max(timeout * (len(test_cases) + 1), timeout + 2)
        profile = ExecutionProfiler(language=cfg.id, op="batch_one_shot")
        with profile.stage("write_source_and_run_all_tests", test_count=len(test_cases)):
            batch_result = self._docker.run_raw_shell(
                cfg.docker.image,
                shell_cmd,
                timeout=total_timeout,
                workspace_id=ws_id,
                profile=profile,
            )
        if profiling_enabled():
            profile.finish(
                test_count=len(test_cases),
                transport_ms=batch_result.duration_ms,
            )

        per_case_ms = max(
            1,
            int(batch_result.duration_ms / max(len(test_cases), 1)),
        )
        outputs = _parse_batch_stdout(batch_result.stdout, len(test_cases))
        results: list[TestCaseResult] = []

        if batch_result.returncode != 0 and not any(outputs):
            compile_error = _diagnostic_text_from_run(batch_result)
            for index, tc in enumerate(test_cases, start=1):
                inputs_str = case_inputs(tc)
                expected = case_output(tc).strip()
                results.append(
                    TestCaseResult(
                        case=index,
                        status="ERROR",
                        inputs=inputs_str,
                        expected=expected,
                        actual="",
                        message=compile_error,
                        duration_ms=per_case_ms,
                    )
                )
            return results

        for index, tc in enumerate(test_cases, start=1):
            inputs_str = case_inputs(tc)
            expected = case_output(tc).strip()
            stdout = outputs[index - 1] if index - 1 < len(outputs) else ""
            if stdout == expected:
                status = "PASSED"
                actual = stdout
                message = ""
            elif not stdout:
                status = "FAILED"
                actual = _actual_from_run(batch_result)
                message = _diagnostic_text_from_run(batch_result)
            else:
                status = "FAILED"
                actual = stdout
                message = ""
            results.append(
                TestCaseResult(
                    case=index,
                    status=status,
                    inputs=inputs_str,
                    expected=expected,
                    actual=actual,
                    message=message,
                    duration_ms=per_case_ms,
                )
            )
        return results

    def _run_compile_once_batch(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict],
        timeout: int,
    ) -> list[TestCaseResult]:
        from infrastructure.execution.test_case_result import TestCaseResult

        ext = cfg.file_extension
        ws_id = new_workspace_id()
        container_path = source_path(ws_id, ext)
        app_path = binary_path(ws_id)
        compile_cmd = (
            cfg.docker.compile
            if cfg.docker and cfg.docker.compile
            else f"g++ -std=c++17 {container_path} -o {binary_path} 2>&1"
        )
        compile_cmd = compile_cmd.format(
            filename=container_path,
            source=container_path,
            binary=app_path,
            output=app_path,
        )

        code_b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
        steps: list[str] = [
            f"echo {code_b64} | base64 -d > {container_path}",
            compile_cmd,
            f"chmod +x {app_path}",
        ]
        for index, tc in enumerate(test_cases, start=1):
            inputs_str = case_inputs(tc)
            inp_b64 = base64.b64encode(inputs_str.encode("utf-8")).decode("ascii")
            steps.append(f"echo {_case_marker(index)}")
            steps.append(f"echo {inp_b64} | base64 -d | {app_path}")
        shell_cmd = " && ".join(steps)

        total_timeout = max(timeout * (len(test_cases) + 1), timeout + 2)
        batch_result = self._docker.run_raw_shell(
            cfg.docker.image,
            shell_cmd,
            timeout=total_timeout,
            workspace_id=ws_id,
        )

        per_case_ms = max(
            1,
            int(batch_result.duration_ms / max(len(test_cases), 1)),
        )
        outputs = _parse_batch_stdout(batch_result.stdout, len(test_cases))
        results: list[TestCaseResult] = []

        if batch_result.returncode != 0 and not any(outputs):
            compile_error = _diagnostic_text_from_run(batch_result)
            for index, tc in enumerate(test_cases, start=1):
                inputs_str = case_inputs(tc)
                expected = case_output(tc).strip()
                results.append(
                    TestCaseResult(
                        case=index,
                        status="ERROR",
                        inputs=inputs_str,
                        expected=expected,
                        actual="",
                        message=compile_error,
                        duration_ms=per_case_ms,
                    )
                )
            return results

        for index, tc in enumerate(test_cases, start=1):
            inputs_str = case_inputs(tc)
            expected = case_output(tc).strip()
            stdout = outputs[index - 1] if index - 1 < len(outputs) else ""
            if stdout == expected:
                status = "PASSED"
                actual = stdout
                message = ""
            elif not stdout:
                status = "FAILED"
                actual = _actual_from_run(batch_result)
                message = ""
            else:
                status = "FAILED"
                actual = stdout
                message = ""
            results.append(
                TestCaseResult(
                    case=index,
                    status=status,
                    inputs=inputs_str,
                    expected=expected,
                    actual=actual,
                    message=message,
                    duration_ms=per_case_ms,
                )
            )
        return results

    def run(
        self,
        cfg: LanguageConfig,
        code: str,
        test_cases: list[dict],
    ) -> list[TestCaseResult]:
        from infrastructure.execution.test_case_result import TestCaseResult

        if not cfg.docker or not cfg.docker.image:
            return UnsupportedTestStrategy(self._docker).run(cfg, code, test_cases)

        timeout = cfg.test.timeout_seconds
        if cfg.test.compile_once and test_cases:
            return self._run_compile_once_batch(cfg, code, test_cases, timeout)

        one_shot = cfg.test.docker_one_shot
        if not one_shot:
            compile_parts = cfg.test.compile or ()
            run_parts = cfg.test.run or ()
            if compile_parts and run_parts:
                one_shot = " ".join(compile_parts) + " && " + " ".join(run_parts)
            else:
                return UnsupportedTestStrategy(self._docker).run(cfg, code, test_cases)

        if cfg.test.batch_one_shot and test_cases:
            return self._run_one_shot_batch(cfg, code, test_cases, timeout, one_shot)

        results: list[TestCaseResult] = []
        for i, tc in enumerate(test_cases):
            inputs_str = case_inputs(tc)
            expected = case_output(tc).strip()
            try:
                result = self._docker.run_shell(
                    cfg.docker.image,
                    one_shot,
                    code,
                    cfg.file_extension,
                    timeout=timeout,
                    stdin=inputs_str if inputs_str else None,
                )
                actual = _actual_from_run(result)
                stderr = result.stderr.strip()
                duration_ms = getattr(result, "duration_ms", 0) or 0
                stdout = (result.stdout or "").strip()
                if result.returncode != 0 and stderr:
                    diag = _diagnostic_text_from_run(result)
                    results.append(
                        TestCaseResult(
                            case=i + 1,
                            status="ERROR",
                            inputs=inputs_str,
                            expected=expected,
                            actual="",
                            message=diag or truncate(stderr),
                            duration_ms=duration_ms,
                        )
                    )
                elif stdout == expected:
                    results.append(
                        TestCaseResult(
                            case=i + 1,
                            status="PASSED",
                            inputs=inputs_str,
                            expected=expected,
                            actual=stdout,
                            duration_ms=duration_ms,
                        )
                    )
                else:
                    fail_msg = ""
                    if not actual or "__CT_CASE_" in actual:
                        fail_msg = "Неверный или пустой вывод программы"
                    results.append(
                        TestCaseResult(
                            case=i + 1,
                            status="FAILED",
                            inputs=inputs_str,
                            expected=expected,
                            actual=actual,
                            message=fail_msg,
                            duration_ms=duration_ms,
                        )
                    )
            except Exception as exc:
                message = str(exc)
                if "TimeoutExpired" in type(exc).__name__:
                    message = f"Time limit exceeded ({timeout}s)"
                results.append(
                    TestCaseResult(
                        case=i + 1,
                        status="ERROR",
                        inputs=inputs_str,
                        expected=expected,
                        actual="",
                        message=message,
                    )
                )

        return results


def get_test_strategy(name: str, docker: DockerExecutor) -> TestStrategy:
    strategies: dict[str, type[TestStrategy]] = {
        "stdin_lines": StdinLinesTestStrategy,
        "compile_and_run": CompileAndRunTestStrategy,
        "unsupported": UnsupportedTestStrategy,
    }
    cls = strategies.get(name, UnsupportedTestStrategy)
    return cls(docker)
