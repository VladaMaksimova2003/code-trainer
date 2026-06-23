"""Hot reload for backend/languages/*.yml."""
from __future__ import annotations

import threading
import time
from pathlib import Path

from infrastructure.execution.language_loader import (
    _languages_dir,
    load_languages,
    reload_language_file,
)


class LanguageWatcher:
    def __init__(self, interval_seconds: float = 2.0) -> None:
        self._interval = interval_seconds
        self._root = _languages_dir()
        self._mtimes: dict[Path, float] = {}
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._refresh_snapshot()
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        while not self._stop.wait(self._interval):
            self.poll()

    def poll(self) -> bool:
        changed = False
        if not self._root.is_dir():
            return False

        current_files = sorted(self._root.glob("*.yml"))
        current_set = set(current_files)

        for path in list(self._mtimes):
            if path not in current_set:
                del self._mtimes[path]
                changed = True

        for path in current_files:
            mtime = path.stat().st_mtime
            previous = self._mtimes.get(path)
            if previous is None:
                self._mtimes[path] = mtime
                try:
                    reload_language_file(path)
                    changed = True
                except Exception as exc:
                    print(f"[language_watcher] skip {path.name}: {exc}")
                continue
            if mtime > previous:
                self._mtimes[path] = mtime
                try:
                    reload_language_file(path)
                    changed = True
                    print(f"[language_watcher] reloaded {path.name}")
                except Exception as exc:
                    print(f"[language_watcher] reload failed {path.name}: {exc}")

        if changed and not self._mtimes:
            load_languages()

        return changed

    def _refresh_snapshot(self) -> None:
        self._mtimes.clear()
        for path in self._root.glob("*.yml"):
            self._mtimes[path] = path.stat().st_mtime


_watcher: LanguageWatcher | None = None


def start_language_watcher() -> LanguageWatcher:
    global _watcher
    if _watcher is None:
        _watcher = LanguageWatcher()
        _watcher.start()
    return _watcher
