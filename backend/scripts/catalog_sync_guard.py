"""Shared guard for CLI seed/sync scripts."""

from __future__ import annotations

import argparse
import sys


def add_force_catalog_sync_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--force-catalog-sync",
        action="store_true",
        help="Allow overwriting/creating tasks from catalog files (requires CURRICULUM__CATALOG_SYNC_ENABLED=true or this flag)",
    )


def ensure_catalog_sync_allowed(*, force: bool = False) -> bool:
    from application.curriculum.catalog_sync_policy import (
        catalog_sync_disabled_message,
        is_catalog_sync_enabled,
    )

    if is_catalog_sync_enabled() or force:
        return True
    print(catalog_sync_disabled_message(), file=sys.stderr)
    return False
