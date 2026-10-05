"""Eval harness entry point.

Phase 1: minimal runner that loads a suite (a directory of `test_*.py`) and
delegates to pytest. The point is not to reinvent pytest; it's to give the
suites a common entrypoint and shared fakes.

Phase 4 will extend this with custom reporting (per-failure-mode rollups,
threshold gates, eval comparisons across runs).
"""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    import pytest

    argv = argv or sys.argv[1:]
    if not argv:
        argv = [str(Path(__file__).parent / "suites" / "smoke")]
    return pytest.main(["-v", *argv])


if __name__ == "__main__":
    raise SystemExit(main())
