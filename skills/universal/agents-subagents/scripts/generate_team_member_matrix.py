#!/usr/bin/env python3
"""Generate the team/member inventory from canonical member and team assets."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re
import sys
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
# The agent catalog lives outside this skill, at <repo>/agents (see scripts/library_layout.py).
AGENTS_DIR = Path(__file__).resolve().parents[4] / "agents"
CLAUDE_MEMBERS = AGENTS_DIR / "claude"
TEAMS_DIR = AGENTS_DIR / "teams"
OUTPUT = ROOT / "references" / "team-member-matrix.md"


class Team(NamedTuple):
    name: str
    family: str
    install: str
    members: tuple[str, ...]
    candidates: tuple[str, ...]


def scalar(text: str, key: str, default: str = "") -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.*?)\s*$", text, re.MULTILINE)
    return match.group(1) if match else default


def top_level_list(text: str, key: str) -> tuple[str, ...]:
    lines = text.splitlines()
    values: list[str] = []
    for index, line in enumerate(lines):
        key_match = re.match(rf"^(\s*){re.escape(key)}:\s*$", line)
        if key_match:
            indent = len(key_match.group(1))
            for item in lines[index + 1 :]:
                match = re.match(r"^(\s*)-\s+([^#]+?)(?:\s+#.*)?$", item)
                if match and len(match.group(1)) >= indent:
                    values.append(match.group(2).strip())
                    continue
                item_indent = len(item) - len(item.lstrip())
                if not item.strip() or item_indent > indent:
                    continue
                break
            break
    return tuple(values)


def load_catalog(
    members_dir: Path = CLAUDE_MEMBERS, teams_dir: Path = TEAMS_DIR
) -> tuple[set[str], list[Team]]:
    members = {
        path.stem for path in members_dir.glob("*.md") if path.name != "README.md"
    }
    teams: list[Team] = []
    for path in sorted(teams_dir.glob("*/team.yaml")):
        text = path.read_text(encoding="utf-8")
        name = scalar(text, "name")
        if not name:
            raise ValueError(f"{path}: missing name")
        if name != path.parent.name:
            raise ValueError(f"{path}: name {name!r} does not match directory")
        team = Team(
            name=name,
            family=scalar(text, "family", "unknown"),
            install=scalar(text, "install", "default"),
            members=top_level_list(text, "members"),
            candidates=top_level_list(text, "candidate_specialists"),
        )
        unknown = (set(team.members) | set(team.candidates)) - members
        if unknown:
            raise ValueError(f"{path}: unknown members: {', '.join(sorted(unknown))}")
        teams.append(team)
    return members, teams


def member_family(member: str) -> str:
    return member.split("-", 1)[0]


def joined(values: list[str] | tuple[str, ...], empty: str = "—") -> str:
    return ", ".join(f"`{value}`" for value in values) if values else empty


def render_matrix(members: set[str], teams: list[Team]) -> str:
    core: dict[str, list[str]] = defaultdict(list)
    candidates: dict[str, list[str]] = defaultdict(list)
    for team in teams:
        for member in team.members:
            core[member].append(team.name)
        for member in team.candidates:
            candidates[member].append(team.name)

    cross_cutting = sorted(
        (member for member, names in core.items() if len(names) >= 2),
        key=lambda member: (-len(core[member]), member),
    )
    specialists = sorted(member for member, names in core.items() if len(names) == 1)
    candidate_only = sorted(set(candidates) - set(core))
    uncomposed = sorted(members - set(core) - set(candidates))
    default_teams = sum(team.install == "default" for team in teams)
    opt_in_teams = len(teams) - default_teams
    composed = len(set(core) | set(candidates))
    density = round(100 * len(cross_cutting) / len(core)) if core else 0

    lines = [
        "---",
        "description: Generated team-to-members and member-to-teams inventory.",
        "status: generated",
        "---",
        "",
        "# Team ↔ Member Matrix",
        "",
        "This file is generated from `agents/teams/*/team.yaml` and the canonical Claude member filenames. Do not edit it manually.",
        "",
        "Core membership and expansion candidates are reported separately: a candidate is available only after its team's expansion gate fires.",
        "",
        "## Table of Contents",
        "",
        "- [Summary](#summary)",
        "- [Reuse Matrix](#reuse-matrix)",
        "- [Team → Members](#team--members)",
        "- [Member → Teams](#member--teams)",
        "- [Regeneration](#regeneration)",
        "- [Related References](#related-references)",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Default teams | {default_teams} |",
        f"| Opt-in teams | {opt_in_teams} |",
        f"| Teams (total) | {len(teams)} |",
        f"| Canonical members | {len(members)} |",
        f"| Composed members (core or candidate) | {composed} |",
        f"| Cross-cutting core members (2+ teams) | {len(cross_cutting)} |",
        f"| Single-team core specialists | {len(specialists)} |",
        f"| Candidate-only members | {len(candidate_only)} |",
        f"| Uncomposed members | {len(uncomposed)} |",
        "",
        f"Core reuse density: **{density}%** ({len(cross_cutting)} of {len(core)} core-composed members appear in two or more teams).",
        "",
        "## Reuse Matrix",
        "",
        "Core members appearing in two or more teams, ordered by breadth and then member ID.",
        "",
        "| Member | Core teams | Teams |",
        "|---|---:|---|",
    ]
    for member in cross_cutting:
        team_names = sorted(core[member])
        lines.append(f"| `{member}` | {len(team_names)} | {joined(team_names)} |")

    lines += [
        "",
        "## Team → Members",
        "",
        "| Team | Install | Core members | Expansion candidates |",
        "|---|---|---|---|",
    ]
    for team in sorted(teams, key=lambda item: item.name):
        lines.append(
            f"| `{team.name}` | {team.install} | {joined(team.members)} | {joined(team.candidates)} |"
        )

    lines += [
        "",
        "## Member → Teams",
        "",
        "### Cross-cutting core members",
        "",
        "See the [Reuse Matrix](#reuse-matrix).",
        "",
        "### Single-team core specialists",
        "",
    ]
    grouped: dict[str, list[str]] = defaultdict(list)
    for member in specialists:
        grouped[member_family(member)].append(member)
    for family in sorted(grouped):
        lines += [f"#### {family}", ""]
        for member in grouped[family]:
            candidate_note = (
                f"; candidate for {joined(sorted(candidates[member]))}"
                if candidates.get(member)
                else ""
            )
            lines.append(f"- `{member}` → `{core[member][0]}`{candidate_note}")
        lines.append("")

    lines += ["### Candidate-only members", ""]
    if candidate_only:
        for member in candidate_only:
            lines.append(f"- `{member}` → {joined(sorted(candidates[member]))}")
    else:
        lines.append("None.")

    lines += ["", "### Uncomposed members", ""]
    if uncomposed:
        for member in uncomposed:
            lines.append(f"- `{member}`")
    else:
        lines.append("None.")

    lines += [
        "",
        "## Regeneration",
        "",
        "```bash",
        "python3 scripts/generate_team_member_matrix.py",
        "python3 scripts/generate_team_member_matrix.py --check",
        "```",
        "",
        "The catalog integrity validator also runs the drift check.",
        "",
        "## Related References",
        "",
        "- [members-and-teams.md](members-and-teams.md) — canonical library structure and member-vs-variant rule",
        "- [team-coverage.md](team-coverage.md) — domain coverage",
        "- [team-scenarios.md](team-scenarios.md) — launch examples",
        "- [team-diagrams.md](team-diagrams.md) — generated team diagrams",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when output is stale")
    args = parser.parse_args()
    try:
        members, teams = load_catalog()
        rendered = render_matrix(members, teams)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != rendered:
            print(f"STALE: {OUTPUT.relative_to(ROOT)}; regenerate with {Path(__file__).name}")
            return 1
        print(f"PASS: {OUTPUT.relative_to(ROOT)} is current")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
