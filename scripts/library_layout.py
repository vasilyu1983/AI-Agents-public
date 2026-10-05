#!/usr/bin/env python3
"""Where library content lives after the 2026-10-03 re-layout.

Skills sit one level down in group folders:

    skills/universal/<name>/SKILL.md
    skills/project/<name>/SKILL.md
    skills/personal/<name>/SKILL.md
    skills/client/<client>/<name>/SKILL.md

The runtime skill folders (~/.claude/skills, ~/.agents/skills) stay flat, so a
skill name must be unique across groups. Every script that walks or looks up
skills goes through this module instead of globbing ``skills/*``.

Functions take an optional ``root`` (the ``skills/`` folder) so tests can point
them at a fixture tree. Import from a script in this folder with
``from library_layout import ...``; from elsewhere, put ``REPO / "scripts"`` on
``sys.path`` first, resolving the repo with ``Path(__file__).resolve()``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

REPO = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO / "skills"
AGENTS_DIR = REPO / "agents"
GRAPH_DIR = REPO / "graph"
EVALS_DIR = REPO / "evals"
TELEMETRY_DIR = REPO / "telemetry"
HOOKS_DIR = REPO / "hooks"
CONFIG_DIR = REPO / "config"
SCRIPTS_DIR = REPO / "scripts"
PROCEDURES_DIR = REPO / "docs" / "procedures"

# Group folders that hold skills directly; "client" adds one client-name level.
FLAT_GROUPS = ("universal", "project", "personal")
NESTED_GROUPS = ("client",)


class DuplicateSkillName(ValueError):
    """Two groups hold a skill with the same name; flat runtime folders would drop one."""


def _candidate_dirs(root: Path) -> Iterator[Path]:
    for group in FLAT_GROUPS:
        base = root / group
        if base.is_dir():
            yield from base.iterdir()
    for group in NESTED_GROUPS:
        base = root / group
        if base.is_dir():
            for owner in sorted(base.iterdir()):
                if owner.is_dir() and not owner.name.startswith((".", "_")):
                    yield from owner.iterdir()


def candidate_dirs(root: Path | None = None) -> list[Path]:
    """Every entry at a skill position, valid skill or not (hidden, symlinked, stub).

    Validators use this to see and reject half-built entries; walks that want
    real skills use ``skill_dirs``.
    """
    return list(_candidate_dirs(SKILLS_ROOT if root is None else Path(root)))


def skill_dirs(root: Path | None = None) -> list[Path]:
    """Every skill folder (one that holds SKILL.md), sorted by skill name.

    Raises DuplicateSkillName when one name appears in two groups.
    """
    root = SKILLS_ROOT if root is None else Path(root)
    seen: dict[str, Path] = {}
    for d in _candidate_dirs(root):
        if not d.is_dir() or d.name.startswith((".", "_")) or not (d / "SKILL.md").is_file():
            continue
        if d.name in seen:
            raise DuplicateSkillName(f"skill name {d.name!r} in {seen[d.name]} and {d}")
        seen[d.name] = d
    return [seen[name] for name in sorted(seen)]


def skill_index(root: Path | None = None) -> dict[str, Path]:
    """Map of skill name to skill folder."""
    return {d.name: d for d in skill_dirs(root)}


def skill_names(root: Path | None = None) -> list[str]:
    return [d.name for d in skill_dirs(root)]


def skill_dir(name: str, root: Path | None = None) -> Path | None:
    """Folder of the named skill, or None when no group holds it."""
    root = SKILLS_ROOT if root is None else Path(root)
    for group in FLAT_GROUPS:
        d = root / group / name
        if (d / "SKILL.md").is_file():
            return d
    for group in NESTED_GROUPS:
        base = root / group
        if base.is_dir():
            for owner in sorted(base.iterdir()):
                d = owner / name
                if (d / "SKILL.md").is_file():
                    return d
    return None


def skill_md_files(root: Path | None = None) -> list[Path]:
    """Every SKILL.md, in skill-name order."""
    return [d / "SKILL.md" for d in skill_dirs(root)]


def group_of(skill_path: Path, root: Path | None = None) -> str:
    """Group label of a skill folder: 'universal', 'project', 'personal', or 'client/<client>'."""
    root = SKILLS_ROOT if root is None else Path(root)
    rel = Path(skill_path).resolve().relative_to(Path(root).resolve())
    return "/".join(rel.parts[:2]) if rel.parts[0] in NESTED_GROUPS else rel.parts[0]


def default_group(name: str) -> str:
    """Group folder (relative to skills/) where a new skill of this name belongs."""
    if name.startswith("project-"):
        return "project"
    return "universal"


if __name__ == "__main__":
    dirs = skill_dirs()
    print(f"{len(dirs)} skills under {SKILLS_ROOT}")
