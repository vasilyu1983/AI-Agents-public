#!/usr/bin/env python3
"""Consolidate raw learnings.md into learnings.consolidated.md.

Modes:
  --dry-run  propose changes, do not write (default)
  --apply    print human-edit instructions (no auto-write; promotion stays a human gate)
  --audit    one-line status report; non-zero exit if not ok
  --queue    routing-log review queue (no skill_dir): exit 1 for aged open lessons,
             failed results, or fixes awaiting verification; exit 2 for invalid dates

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

# Aged-lesson queue over skills/routing-log.md. FAILURE_RE matches plain and bullet log
# lines, like FAILURE_RE in scripts/catalog/plan-skill-batches.py; MISS is not a log class.
QUEUE_DAYS = 14
LOG_LINE_RE = re.compile(r"^(?:- )?\d{4}-\d{2}-\d{2}\s+[A-Z]+\b")
FAILURE_RE = re.compile(r"^(?:- )?(\S+)\s+(STALL|MISROUTE)\b")
# This queue checks result syntax; audit/skill-status.py verifies the evidence.
# Historical fix notes stay visible until a verified result replaces them.
FIX_NOTE_RE = re.compile(r"→ fix\b|\bFIXED\b")
RECEIPT_RE = re.compile(
    r"→ fix [0-9a-f]{9} → result (pending|verifier passed|verifier failed|WIN (\S+))\s*$"
)
DEFERRED_RE = re.compile(r"\{deferred: user-decision ([^\s}]+)\}\s*$")
DEFAULT_LOG = Path(__file__).resolve().parents[3] / "routing-log.md"


def parse(text: str) -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {s: [] for s in SECTIONS}
    current = None
    in_comment = False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if in_comment:
            if "-->" in stripped and stripped.split("-->", 1)[1].strip():
                raise ValueError(f"line {number}: content after comment terminator")
            in_comment = "-->" not in stripped
            continue
        if stripped.startswith("<!--"):
            if "-->" in stripped and stripped.split("-->", 1)[1].strip():
                raise ValueError(f"line {number}: content after comment terminator")
            in_comment = "-->" not in stripped
            continue
        h = re.match(r"^## (.+?)\s*$", line)
        if h:
            current = h.group(1).strip()
            if current not in out and current != "Filter Override":
                raise ValueError(f"line {number}: unknown section")
            continue
        if not stripped or current == "Filter Override":
            continue
        if current in out:
            m = ENTRY_RE.match(line)
            if not m or not m.group(2).strip():
                raise ValueError(f"line {number}: expected one dated, nonempty entry")
            try:
                dt.date.fromisoformat(m.group(1))
            except ValueError:
                raise ValueError(f"line {number}: invalid calendar date") from None
            out[current].append((m.group(1), m.group(2).strip()))
        elif stripped.startswith(("- ", "* ", "+ ")):
            raise ValueError(f"line {number}: entry outside a canonical section")
    if in_comment:
        raise ValueError("unterminated comment")
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


def is_stale(date_str: str, today: dt.date, days: int = AGE_OUT_DAYS) -> bool:
    try:
        d = dt.date.fromisoformat(date_str)
    except ValueError:
        return False
    return (today - d).days > days


def lesson_queue(text: str, today: dt.date, days: int) -> dict:
    """Sort routing-log failure lines into open (aged, no state), deferred, and awaiting result."""
    if days < 0:
        raise ValueError("--days must be zero or greater")
    if not any(LOG_LINE_RE.match(line) for line in text.splitlines()):
        raise ValueError("no dated `YYYY-MM-DD CLASS` lines; is this the routing log?")
    q = {"open": [], "deferred": [], "awaiting": []}
    for number, line in enumerate(text.splitlines(), 1):
        m = FAILURE_RE.match(line)
        if not m:
            continue
        deferred = DEFERRED_RE.search(line)
        receipt = RECEIPT_RE.search(line)
        try:
            dates = [m.group(1)]
            if deferred:
                dates.append(deferred.group(1))
            if receipt and receipt.group(2):
                dates.append(receipt.group(2))
            for value in dates:
                if dt.date.fromisoformat(value).isoformat() != value:
                    raise ValueError("use YYYY-MM-DD")
            started = dt.date.fromisoformat(m.group(1))
            if deferred:
                if dt.date.fromisoformat(deferred.group(1)) > today:
                    raise ValueError("deferred date is in the future")
            if receipt and receipt.group(2):
                finished = dt.date.fromisoformat(receipt.group(2))
                if finished < started or finished > today:
                    raise ValueError("result date precedes the lesson or is in the future")
            if started > today:
                raise ValueError("lesson date is in the future")
        except ValueError as exc:
            raise ValueError(f"routing-log line {number}: invalid date: {exc}") from None
        if deferred:
            q["deferred"].append(line.strip())
        elif receipt and receipt.group(1) == "verifier failed":
            q["open"].append(line.strip())
        elif receipt and receipt.group(1) != "pending":
            continue
        elif FIX_NOTE_RE.search(line):
            q["awaiting"].append(line.strip())
        elif (today - started).days > days:
            q["open"].append(line.strip())
    return q


def render_queue(q: dict, days: int) -> str:
    heads = {"open": f"OPEN ({len(q['open'])}), failed verification or older than {days} days without a result:",
             "deferred": f"DEFERRED ({len(q['deferred'])}):", "awaiting": f"AWAITING RESULT ({len(q['awaiting'])}):"}
    out = []
    for key, head in heads.items():
        if q[key]:
            out += [head] + [f"  {line}" for line in q[key]]
    out.append(f"{len(q['open'])} open, {len(q['deferred'])} deferred, {len(q['awaiting'])} awaiting result")
    return "\n".join(out)


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
    p.add_argument("skill_dir", type=Path, nargs="?")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True)
    g.add_argument("--apply", action="store_true")
    g.add_argument("--audit", action="store_true")
    g.add_argument("--queue", action="store_true", help="aged-lesson queue over the routing log")
    p.add_argument("--log", type=Path, default=DEFAULT_LOG, help="routing log for --queue")
    p.add_argument("--days", type=int, default=QUEUE_DAYS, help="age in days before a lesson is open")
    args = p.parse_args()

    if args.queue:
        try:
            q = lesson_queue(args.log.read_text(encoding="utf-8"), dt.date.today(), args.days)
        except (ValueError, OSError) as exc:
            print(f"consolidate: cannot read routing log {args.log}: {exc}", file=sys.stderr)
            return 2
        print(render_queue(q, args.days))
        return 1 if q["open"] or q["awaiting"] else 0
    if args.skill_dir is None:
        p.error("skill_dir is required unless --queue is given")

    if not args.skill_dir.is_dir():
        print(f"consolidate: not a directory: {args.skill_dir}", file=sys.stderr)
        return 1

    if args.audit:
        try:
            line, code = audit(args.skill_dir)
        except (ValueError, OSError) as exc:
            print(f"consolidate: invalid learning file: {exc}", file=sys.stderr)
            return 1
        print(line)
        return code

    raw_path = args.skill_dir / "learnings.md"
    cons_path = args.skill_dir / "learnings.consolidated.md"
    if not raw_path.exists():
        print("consolidate: no learnings.md — nothing to do")
        return 0

    try:
        raw = parse(raw_path.read_text())
        consolidated = parse(cons_path.read_text()) if cons_path.exists() else {s: [] for s in SECTIONS}
    except (ValueError, OSError) as exc:
        print(f"consolidate: invalid learning file: {exc}", file=sys.stderr)
        return 1
    proposals = propose(raw, consolidated, dt.date.today())
    print(render_proposals(proposals))

    if args.apply:
        print(
            "\n--apply requested. This script does not auto-write yet — promotion is a human gate.\n"
            "Copy approved proposals into learnings.consolidated.md by hand; retain raw "
            "learnings.md as append-only history.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
