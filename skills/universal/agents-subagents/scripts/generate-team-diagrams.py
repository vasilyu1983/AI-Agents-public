#!/usr/bin/env python3
"""Generate Mermaid flowchart diagrams for every team under <repo>/agents/teams/.

Walks each team.yaml, parses the minimal structure we use (top-level fields
plus the members/perspectives lists and the debate block), and writes a single
consolidated markdown file at references/team-diagrams.md with one diagram per
team. Regenerate by running this script whenever manifests change.

Diagrams are communication artifacts, not runtime logic. The dispatch behavior
lives in the lead thread and synthesizer templates. See
references/dynamic-team-expansion.md for the end-to-end flow.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
# The agent catalog lives outside this skill, at <repo>/agents (see scripts/library_layout.py).
TEAMS_DIR = SCRIPT_DIR.parents[3] / "agents" / "teams"
OUTPUT_PATH = SKILL_DIR / "references" / "team-diagrams.md"


def strip_inline_comment(val: str) -> str:
    """Strip simple YAML comments from unquoted list/scalar values."""
    quote: str | None = None
    for idx, char in enumerate(val):
        if char in {"'", '"'}:
            quote = None if quote == char else char if quote is None else quote
        if char == "#" and quote is None:
            if idx == 0 or val[idx - 1].isspace():
                return val[:idx].rstrip()
    return val


def parse_team_yaml(path: Path) -> dict:
    """Minimal YAML parser for our team.yaml structure.

    Handles top-level scalars, top-level lists, and one level of nesting for
    the `debate:` block. Avoids a PyYAML dependency so the script runs on any
    Python 3.8+ without extra installs.
    """
    data: dict = {}
    current_top: str | None = None
    current_list: list | None = None
    current_map: dict | None = None
    current_map_list_key: str | None = None
    block_scalar_key: str | None = None
    block_scalar_lines: list[str] = []

    def flush_block_scalar() -> None:
        nonlocal block_scalar_key, block_scalar_lines
        if block_scalar_key is None:
            return
        data[block_scalar_key] = " ".join(line.strip() for line in block_scalar_lines).strip()
        block_scalar_key = None
        block_scalar_lines = []

    with path.open() as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue

            # Top-level key (no indentation)
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
            if m:
                flush_block_scalar()
                key, val = m.group(1), m.group(2).strip()
                current_top = key
                current_list = None
                current_map = None
                current_map_list_key = None
                if val in {">", ">-", "|", "|-"}:
                    block_scalar_key = key
                    block_scalar_lines = []
                elif key == "debate":
                    current_map = {}
                    data[key] = current_map
                elif val == "":
                    current_list = []
                    data[key] = current_list
                else:
                    data[key] = parse_inline_value(strip_inline_comment(val).strip())
                continue

            if block_scalar_key is not None:
                block_scalar_lines.append(line)
                continue

            # Top-level list item: "- item" (or indented by two spaces)
            m = re.match(r"^\s{0,2}-\s+(.+)$", line)
            if m and current_list is not None and current_map is None:
                current_list.append(strip_quotes(strip_inline_comment(m.group(1).strip())))
                continue

            # Nested key under debate: "  key: value"
            m = re.match(r"^  ([a-z_]+):\s*(.*)$", line)
            if m and current_top == "debate" and current_map is not None:
                k, v = m.group(1), m.group(2).strip()
                if v == "":
                    current_map_list_key = k
                    current_map[k] = []
                else:
                    current_map[k] = parse_inline_value(strip_inline_comment(v).strip())
                    current_map_list_key = None
                continue

            # Nested list item under debate: "  - item" or "    - item"
            m = re.match(r"^\s{2,4}-\s+(.+)$", line)
            if m and current_map is not None and current_map_list_key is not None:
                current_map[current_map_list_key].append(
                    strip_quotes(strip_inline_comment(m.group(1).strip()))
                )
                continue

            # Anything else (deeper nesting, comments with indentation) is ignored.
            # The parser only needs top-level + one-level debate; enough for diagrams.
    flush_block_scalar()
    return data


def strip_quotes(val: str) -> str:
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    return val


def parse_inline_value(val: str):
    """Parse simple inline values: booleans, bracketed lists, or plain strings."""
    if val.lower() in ("true", "false"):
        return val.lower() == "true"
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [strip_quotes(s.strip()) for s in inner.split(",") if s.strip()]
    return strip_quotes(val)


def safe_id(member_name: str, prefix: str = "M") -> str:
    """Mermaid node IDs: replace hyphens and dots with underscores."""
    return prefix + re.sub(r"[^A-Za-z0-9]", "_", member_name)


def generate_diagram(team: dict) -> str | None:
    members = team.get("members") or []
    if not members:
        return None

    synth = team.get("synthesis_owner", "synthesis")
    mode = team.get("concurrency_mode", "parallel")
    debate = team.get("debate") or {}
    debate_on = bool(debate.get("enabled", False))
    method = debate.get("method")

    lines: list[str] = ["```mermaid", "flowchart TD"]
    lines.append("    Lead[Lead Thread]")

    member_ids = {m: safe_id(m) for m in members}
    for m, mid in member_ids.items():
        lines.append(f"    {mid}[{m}]")

    synth_label = "parent thread" if synth == "parent-thread" else synth
    lines.append(f"    Synth[[{synth_label}]]")
    lines.append("    Out([Decision Log])")

    if mode == "staged":
        prev = "Lead"
        for m in members:
            lines.append(f"    {prev} --> {member_ids[m]}")
            prev = member_ids[m]
        lines.append(f"    {prev} --> Synth")
    else:  # parallel or hybrid — render as fan-out
        for m in members:
            lines.append(f"    Lead --> {member_ids[m]}")
            lines.append(f"    {member_ids[m]} --> Synth")

    lines.append("    Synth --> Out")
    lines.append("    Synth -. clarify .-> Lead")
    lines.append("    Synth -. expand .-> Lead")

    if debate_on and method:
        # Theme-safe emphasis: no fill or stroke hex, so the host theme supplies
        # colors in both light and dark. Weight and dash carry the meaning instead.
        lines.append("    classDef debateOn stroke-width:3px,stroke-dasharray:4 2;")
        lines.append(f"    class Synth debateOn;")
        lines.append(f"    %% debate method: {method}")

    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    check = False
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] not in {"--check", "-h", "--help"}):
        print("usage: generate-team-diagrams.py [--check]", file=sys.stderr)
        return 2
    if len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"}:
        print("usage: generate-team-diagrams.py [--check]")
        return 0
    if len(sys.argv) == 2 and sys.argv[1] == "--check":
        check = True

    if not TEAMS_DIR.is_dir():
        print(f"error: teams dir not found at {TEAMS_DIR}", file=sys.stderr)
        return 1

    teams: list[tuple[str, dict]] = []
    for tdir in sorted(TEAMS_DIR.iterdir()):
        if not tdir.is_dir():
            continue
        yaml_path = tdir / "team.yaml"
        if not yaml_path.exists():
            continue
        team = parse_team_yaml(yaml_path)
        teams.append((tdir.name, team))

    if not teams:
        print(f"error: no team.yaml files found under {TEAMS_DIR}", file=sys.stderr)
        return 1

    out: list[str] = []
    out.append("# Team Diagrams")
    out.append("")
    out.append(
        "Auto-generated Mermaid flowcharts — one per shared team. Diagrams show "
        "lead-thread dispatch, member fan-out, synthesis owner, and the two "
        "defensive-output feedback loops (dotted: clarification and expansion "
        "back to the lead). Highlighted synthesis nodes indicate debate is on."
    )
    out.append("")
    out.append("Diagrams are communication artifacts, not runtime logic. Actual "
               "dispatch behavior lives in the lead thread. See "
               "[dynamic-team-expansion.md](dynamic-team-expansion.md) for the "
               "end-to-end flow and "
               "[clarification-questions-protocol.md](clarification-questions-protocol.md) "
               "for the anti-slop gates.")
    out.append("")
    # Build TOC before emitting sections (teams list already collected above)
    out.append("## Table of Contents")
    out.append("")
    out.append("- [Regeneration](#regeneration)")
    out.append("- [Summary](#summary)")
    for tdir, team in teams:
        name = team.get("name", tdir)
        # Generate slug: backtick-wrapped name → anchor: lowercase, spaces→hyphens, drop punctuation except hyphens
        import re as _re
        slug = _re.sub(r"[^a-z0-9\-]", "", name.lower().replace(" ", "-").replace("_", "-"))
        out.append(f"- [`{name}`](#{slug})")
    out.append("")
    out.append("## Regeneration")
    out.append("")
    out.append("```bash")
    out.append("python3 scripts/generate-team-diagrams.py")
    out.append("```")
    out.append("")
    out.append("Regenerate after any `team.yaml` change. Do not edit this file by hand — edits will be overwritten.")
    out.append("")
    out.append("## Summary")
    out.append("")

    install_counts = {"default": 0, "opt-in": 0}
    debate_on_count = 0
    concurrency_counts: dict = {}
    for _, t in teams:
        install = t.get("install", "default")
        install_counts[install] = install_counts.get(install, 0) + 1
        if (t.get("debate") or {}).get("enabled"):
            debate_on_count += 1
        mode = t.get("concurrency_mode", "parallel")
        concurrency_counts[mode] = concurrency_counts.get(mode, 0) + 1

    out.append(f"- **Total teams:** {len(teams)}")
    out.append(f"- **Install modes:** " + ", ".join(f"{k}: {v}" for k, v in install_counts.items() if v))
    out.append(f"- **Debate on:** {debate_on_count} / {len(teams)}")
    out.append(f"- **Concurrency:** " + ", ".join(f"{k}: {v}" for k, v in concurrency_counts.items()))
    out.append("")
    out.append("---")
    out.append("")

    for tdir, team in teams:
        name = team.get("name", tdir)
        family = team.get("family", "—")
        install = team.get("install", "default")
        mode = team.get("concurrency_mode", "parallel")
        desc = team.get("description", "")
        debate = team.get("debate") or {}
        debate_on = bool(debate.get("enabled"))
        method = debate.get("method", "—")
        masks = debate.get("decision_masks") or []

        out.append(f"## `{name}`")
        out.append("")
        out.append(f"**Family:** {family}")
        out.append(f"**Install:** {install}")
        out.append(f"**Concurrency:** {mode}")
        out.append(f"**Debate:** {'on' if debate_on else 'off'}"
                   + (f" (method: `{method}`" if debate_on and method != "—" else "")
                   + (f", masks: {', '.join(f'`{m}`' for m in masks)}" if masks else "")
                   + (")" if debate_on and method != "—" else ""))
        out.append(f"**Manifest:** [agents/teams/{tdir}/team.yaml](../../../../agents/teams/{tdir}/team.yaml)")
        out.append("")
        if desc:
            out.append(f"> {desc}")
            out.append("")
        diagram = generate_diagram(team)
        if diagram:
            out.append(diagram)
        out.append("")
        out.append("---")
        out.append("")

    generated = "\n".join(out).rstrip() + "\n"
    if check:
        if not OUTPUT_PATH.exists():
            print(f"error: {OUTPUT_PATH.relative_to(SKILL_DIR)} does not exist", file=sys.stderr)
            return 1
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != generated:
            print(f"error: {OUTPUT_PATH.relative_to(SKILL_DIR)} is stale; regenerate with scripts/generate-team-diagrams.py", file=sys.stderr)
            return 1
        print(f"ok: {OUTPUT_PATH.relative_to(SKILL_DIR)} is current")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(generated, encoding="utf-8")
    print(f"wrote {len(teams)} team diagrams → {OUTPUT_PATH.relative_to(SKILL_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
