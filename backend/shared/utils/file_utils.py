"""File utilities. Previously: src/infrastructure/utils/file_utils.py"""
import os
import re
import shutil
import uuid
from pathlib import Path
from typing import List


class TempFileManager:
    ROOT_DIR = Path("./tmp")
    INPUT_DIR_NAME = "input"

    @staticmethod
    def create(code: str, ext: str) -> tuple[str, str]:
        run_id = uuid.uuid4().hex[:12]
        run_dir = TempFileManager.ROOT_DIR / run_id
        input_dir = run_dir / TempFileManager.INPUT_DIR_NAME
        input_dir.mkdir(parents=True, exist_ok=True)
        filename = f"source{ext}"
        tmp_path = input_dir / filename
        tmp_path.write_text(code, encoding="utf-8")
        container_path = f"/runner/{TempFileManager.INPUT_DIR_NAME}/{filename}"
        return str(tmp_path), container_path

    @staticmethod
    def remove(path: str) -> None:
        file_path = Path(path)
        run_dir = file_path.parents[1] if len(file_path.parents) >= 2 else file_path.parent
        if run_dir.exists():
            shutil.rmtree(run_dir, ignore_errors=True)


class ErrorParser:
    PATTERNS = [
        r".*error: (.*)",
        r".*Exception: (.*)",
        r".*Error: (.*)",
        r".*fatal: (.*)",
        r"invalid-syntax: (.*)",
        r".*expected '.*', found (.*)",
    ]

    @classmethod
    def parse(cls, output: str | List[str]) -> List[str]:
        if isinstance(output, list):
            lines = output
        else:
            lines = output.splitlines()

        parsed = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            for pattern in cls.PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    parsed.append(match.group(1).strip())
                    break
        return parsed
