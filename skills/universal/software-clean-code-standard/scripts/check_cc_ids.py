#!/usr/bin/env python3
"""Check that every cited CC-* rule ID exists in the clean-code catalog.

Usage:
    python3 check_cc_ids.py [PATH ...]

PATH may be a file or a directory (scanned recursively for *.md). With no
PATH, the skill directory is scanned. learnings*.md files are skipped because
they record historical mistakes verbatim.

Checks:
- `CC-<CAT>-<NN>` (2-3 digits): the ID must be a row in the catalog table.
- `CC-<CAT>-*` wildcards: <CAT> must be a catalog category.

Exit codes: 0 = all cited IDs exist; 1 = unknown IDs found;
2 = the catalog could not be read or parsed (fails closed).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CATALOG = SKILL_DIR / "references" / "clean-code-standard.md"

CATALOG_ROW = re.compile(r"^\|\s*(CC-([A-Z]+)-\d{2})\s*\|", re.MULTILINE)
CITED_ID = re.compile(r"\bCC-([A-Z]+)-(\d{2,3})\b")
CITED_WILDCARD = re.compile(r"\bCC-([A-Z]+)-\*")


def load_catalog(path: Path) -> tuple[set[str], set[str]]:
    text = path.read_text(encoding="utf-8")
    ids = {m.group(1) for m in CATALOG_ROW.finditer(text)}
    cats = {m.group(2) for m in CATALOG_ROW.finditer(text)}
    return ids, cats


def iter_files(paths: list[Path]):
    for p in paths:
        if p.is_dir():
            yield from sorted(f for f in p.rglob("*.md") if not f.name.startswith("learnings"))
        elif p.is_file():
            yield p
        else:
            raise FileNotFoundError(p)


def check(paths: list[Path], catalog: Path = CATALOG) -> tuple[list[str], int]:
    ids, cats = load_catalog(catalog)
    if not ids:
        raise ValueError(f"no CC-* rows parsed from {catalog}")
    problems = []
    for f in iter_files(paths):
        for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in CITED_ID.finditer(line):
                rule = m.group(0)
                if rule not in ids:
                    problems.append(f"{f}:{lineno}: unknown rule ID {rule}")
            for m in CITED_WILDCARD.finditer(line):
                if m.group(1) not in cats:
                    problems.append(f"{f}:{lineno}: unknown category {m.group(0)}")
    return problems, len(ids)


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv] or [SKILL_DIR]
    try:
        problems, n = check(paths)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for p in problems:
        print(p)
    if problems:
        print(f"FAIL: {len(problems)} unknown CC-* reference(s); catalog has {n} rules", file=sys.stderr)
        return 1
    print(f"OK: all CC-* references exist ({n} rules in catalog)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
