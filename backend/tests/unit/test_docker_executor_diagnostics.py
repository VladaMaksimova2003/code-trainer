from infrastructure.execution.docker_executor import (
    _docker_failure_diagnostics,
    _looks_like_docker_failure,
)


def test_docker_failure_detects_missing_runner_image():
    text = (
        "Unable to find image 'python_runner:latest' locally\n"
        "docker: Error response from daemon: pull access denied for python_runner"
    )
    assert _looks_like_docker_failure(text)
    msgs = _docker_failure_diagnostics(text, "python_runner")
    assert len(msgs) == 1
    assert "python_runner" in msgs[0]
    assert msgs[0].startswith("Line 1:")
