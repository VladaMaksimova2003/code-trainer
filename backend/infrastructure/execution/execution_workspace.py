"""Per-submit isolated workspace under /tmp/home/<workspace_id> inside runners."""
from __future__ import annotations

import os
import uuid

# Shared tool caches (NuGet, Roslyn) live in /home/runner — never user workspaces.


def new_workspace_id() -> str:
    return uuid.uuid4().hex[:16]


def workspace_root(workspace_id: str) -> str:
    safe = "".join(ch for ch in workspace_id if ch.isalnum())
    if not safe:
        safe = uuid.uuid4().hex[:16]
    return f"/tmp/home/{safe}"


def source_path(workspace_id: str, ext: str) -> str:
    normalized_ext = ext if ext.startswith(".") else f".{ext}"
    return f"{workspace_root(workspace_id)}/source{normalized_ext}"


def binary_path(workspace_id: str) -> str:
    return f"{workspace_root(workspace_id)}/app"


def isolation_shell_prefix(workspace_id: str) -> str:
    root = workspace_root(workspace_id)
    return (
        f'CT_WORKSPACE="{root}"; '
        f'mkdir -p "$CT_WORKSPACE" && '
        f'trap \'rm -rf "$CT_WORKSPACE"\' EXIT INT TERM; '
    )


def warm_runner_recycle_after() -> int:
    raw = os.getenv("WARM_RUNNER_RECYCLE_AFTER", "500")
    try:
        return max(1, int(raw))
    except ValueError:
        return 500
