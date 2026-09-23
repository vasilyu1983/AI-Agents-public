#!/usr/bin/env python3
"""Bulk-wire the learnings loop into every eligible skill.

Eligibility:
  - has SKILL.md
  - prefix not in EXCLUDE_PREFIXES
  - skill name not in EXCLUDE_NAMES
  - not already wired (no '## Learnings Loop' in SKILL.md)

For each eligible skill:
  - insert the addendum before '## See Also' (or at end if absent)
  - seed learnings.consolidated.md from the template

Run with --dry-run first. Re-run safe (idempotent).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EXCLUDE_PREFIXES = ("router-",)
EXCLUDE_NAMES = {
    "agents-skills-feedback-loop",  # no self-loop
}

ADDENDUM = """## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

"""

def consolidated_template(skill_name: str) -> str:
    """Use the same bundle-owned template as the manual wiring protocol."""
    template = Path(__file__).resolve().parents[1] / "assets/learnings.template.md"
    return template.read_text(encoding="utf-8").replace("<SKILL_NAME>", skill_name)


def insert_addendum(skill_md_text: str) -> str:
    """Insert addendum before '## See Also' if present, else at end."""
    m = re.search(r"^## See Also\b", skill_md_text, re.M)
    if m:
        return skill_md_text[: m.start()] + ADDENDUM + skill_md_text[m.start():]
    if not skill_md_text.endswith("\n"):
        skill_md_text += "\n"
    return skill_md_text + "\n" + ADDENDUM


def is_eligible(skill_dir: Path) -> tuple[bool, str]:
    name = skill_dir.name
    if not (skill_dir / "SKILL.md").exists():
        return False, "no SKILL.md"
    for p in EXCLUDE_PREFIXES:
        if name.startswith(p):
            return False, f"excluded prefix '{p}'"
    if name in EXCLUDE_NAMES:
        return False, "excluded by name"
    skill_md = (skill_dir / "SKILL.md").read_text()
    if "## Learnings Loop" in skill_md:
        return False, "already wired"
    return True, "eligible"


def wire(skill_dir: Path, dry_run: bool) -> str:
    skill_md_path = skill_dir / "SKILL.md"
    consolidated_path = skill_dir / "learnings.consolidated.md"

    actions = []
    new_skill_md = insert_addendum(skill_md_path.read_text())
    actions.append("addendum")
    if not consolidated_path.exists():
        actions.append("seed-consolidated")

    if not dry_run:
        skill_md_path.write_text(new_skill_md)
        if "seed-consolidated" in actions:
            consolidated_path.write_text(consolidated_template(skill_dir.name))

    return ", ".join(actions)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("skills_root", type=Path, help="frameworks/shared-skills/skills")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()

    if args.dry_run == args.apply:
        if not args.apply:
            args.dry_run = True
        else:
            print("pick one: --dry-run or --apply", file=sys.stderr)
            return 1

    if not args.skills_root.is_dir():
        print(f"not a directory: {args.skills_root}", file=sys.stderr)
        return 1

    wired = 0
    skipped: dict[str, list[str]] = {}
    for skill_dir in sorted(args.skills_root.iterdir()):
        if not skill_dir.is_dir():
            continue
        ok, reason = is_eligible(skill_dir)
        if not ok:
            skipped.setdefault(reason, []).append(skill_dir.name)
            continue
        actions = wire(skill_dir, dry_run=args.dry_run)
        print(f"{'DRY' if args.dry_run else 'WIRE'}  {skill_dir.name}  [{actions}]")
        wired += 1

    print()
    print(f"summary: {wired} wired, {sum(len(v) for v in skipped.values())} skipped")
    for reason, names in sorted(skipped.items()):
        print(f"  skipped ({reason}, n={len(names)}): {', '.join(names[:8])}"
              + (f", … +{len(names)-8} more" if len(names) > 8 else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
