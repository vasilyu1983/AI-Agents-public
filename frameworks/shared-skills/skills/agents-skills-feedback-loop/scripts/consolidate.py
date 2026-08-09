#!/usr/bin/env python3
"""Consolidate raw learnings.md into learnings.consolidated.md.

Modes:
  --dry-run  propose changes, do not write (default)
  --apply    print human-edit instructions (no auto-write; promotion stays a human gate)
  --audit    one-line status report; non-zero exit if not ok

Never edits the host skill's SKILL.md. Never moves entries to references/.
Those are human jobs by design.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import re
import sys
from pathlib import Path

SECTIONS = (
    "Patterns That Work",
    "Mistakes to Avoid",
    "Domain Knowledge",
    "Open Questions",
    "Consolidated Principles",
)
RAW_CAP = 150
CONSOLIDATED_CAP = 60
AGE_OUT_DAYS = 90
PROMOTION_MIN_RECURRENCE = 2
NEAR_DUP_RATIO = 0.82

ENTRY_RE = re.compile(r"^- \[(\d{4}-\d{2}-\d{2})\] (.+)$")


def parse(text: str) -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {s: [] for s in SECTIONS}
    current = None
    for line in text.splitlines():
        h = re.match(r"^## (.+?)\s*$", line)
        if h:
            current = h.group(1).strip()
            continue
        if current in out:
            m = ENTRY_RE.match(line)
            if m:
                out[current].append((m.group(1), m.group(2).strip()))
    return out


def cluster_near_duplicates(entries: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    clusters: list[list[tuple[str, str]]] = []
    for date, body in entries:
        placed = False
        for c in clusters:
            if difflib.SequenceMatcher(None, body.lower(), c[0][1].lower()).ratio() >= NEAR_DUP_RATIO:
                c.append((date, body))
                placed = True
                break
        if not placed:
            clusters.append([(date, body)])
    return clusters


def is_stale(date_str: str, today: dt.date) -> bool:
    try:
        d = dt.date.fromisoformat(date_str)
    except ValueError:
        return False
    return (today - d).days > AGE_OUT_DAYS


def propose(raw: dict, consolidated: dict, today: dt.date) -> dict:
    proposals = {"promote": [], "age_out": [], "warn_cap": False}
    consolidated_count = sum(len(v) for v in consolidated.values())

    for section, entries in raw.items():
        clusters = cluster_near_duplicates(entries)
        for cluster in clusters:
            if len(cluster) >= PROMOTION_MIN_RECURRENCE:
                first = min(c[0] for c in cluster)
                latest_body = cluster[-1][1]
                proposals["promote"].append(
                    {
                        "section": section,
                        "body": latest_body,
                        "first_seen": first,
                        "n": len(cluster),
                        "originals": cluster,
                    }
                )
            else:
                date, body = cluster[0]
                if is_stale(date, today):
                    proposals["age_out"].append({"section": section, "date": date, "body": body})

    new_total = consolidated_count + len(proposals["promote"])
    if new_total > CONSOLIDATED_CAP:
        proposals["warn_cap"] = (consolidated_count, new_total)

    return proposals


def audit(skill_dir: Path) -> tuple[str, int]:
    raw_path = skill_dir / "learnings.md"
    cons_path = skill_dir / "learnings.consolidated.md"
    skill_md = skill_dir / "SKILL.md"

    raw_count = 0
    raw_oldest = "n/a"
    if raw_path.exists():
        raw = parse(raw_path.read_text())
        all_entries = [e for v in raw.values() for e in v]
        raw_count = len(all_entries)
        if all_entries:
            raw_oldest = min(d for d, _ in all_entries)

    cons_count = 0
    if cons_path.exists():
        cons = parse(cons_path.read_text())
        cons_count = sum(len(v) for v in cons.values())

    addendum = "no"
    if skill_md.exists() and "## Learnings Loop" in skill_md.read_text():
        addendum = "yes"

    status = "ok"
    if raw_count > RAW_CAP or cons_count > CONSOLIDATED_CAP:
        status = "warn"
    if cons_path.exists() and addendum == "no":
        status = "orphan"

    line = (
        f"{skill_dir.name}  raw={raw_count}/{RAW_CAP}  "
        f"consolidated={cons_count}/{CONSOLIDATED_CAP}  "
        f"oldest={raw_oldest}  addendum={addendum}  status={status}"
    )
    return line, 0 if status == "ok" else 1


def render_proposals(p: dict) -> str:
    out = []
    if p["promote"]:
        out.append(f"PROMOTE ({len(p['promote'])}):")
        for x in p["promote"]:
            out.append(f"  [{x['section']}] (seen {x['n']}x since {x['first_seen']}) {x['body']}")
    if p["age_out"]:
        out.append(f"AGE OUT ({len(p['age_out'])}):")
        for x in p["age_out"]:
            out.append(f"  [{x['section']}] [{x['date']}] {x['body']}")
    if p["warn_cap"]:
        cur, new = p["warn_cap"]
        out.append(
            f"WARN: consolidated would grow {cur} → {new} (cap {CONSOLIDATED_CAP}). "
            f"Promote some entries to references/ of the host skill first."
        )
    if not out:
        out.append("nothing to do.")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("skill_dir", type=Path)
    g = p.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True)
    g.add_argument("--apply", action="store_true")
    g.add_argument("--audit", action="store_true")
    args = p.parse_args()

    if not args.skill_dir.is_dir():
        print(f"consolidate: not a directory: {args.skill_dir}", file=sys.stderr)
        return 1

    if args.audit:
        line, code = audit(args.skill_dir)
        print(line)
        return code

    raw_path = args.skill_dir / "learnings.md"
    cons_path = args.skill_dir / "learnings.consolidated.md"
    if not raw_path.exists():
        print("consolidate: no learnings.md — nothing to do")
        return 0

    raw = parse(raw_path.read_text())
    consolidated = parse(cons_path.read_text()) if cons_path.exists() else {s: [] for s in SECTIONS}
    proposals = propose(raw, consolidated, dt.date.today())
    print(render_proposals(proposals))

    if args.apply:
        print(
            "\n--apply requested. This script does not auto-write yet — promotion is a human gate.\n"
            "Copy the proposed lines into learnings.consolidated.md by hand, then delete promoted/aged "
            "entries from learnings.md.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
