#!/usr/bin/env python3
"""Summarise code-focused contribution activity from an augmented commit CSV.

The input must include code, test, configuration, documentation, and other
insert/delete buckets. Merge commits are ignored. Results are written as a
per-person CSV and, optionally, a compact Markdown table.

The score is a transparent heuristic, not a performance assessment. It uses
source insertions as the base, then applies bounded adjustments for the share of
source changes, number of files touched, and insertion-heavy work. Interpret it
with review quality, role, tenure, delivery outcomes, and the source data's
coverage.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


CATEGORIES = ("code", "test", "config", "docs", "other")
MIN_COMMITS_FOR_MEDIAN = 5


def integer(value: object) -> int:
    """Convert a CSV value to a non-negative integer, defaulting to zero."""
    try:
        return max(0, int(str(value or "0")))
    except (TypeError, ValueError):
        return 0


def load_aliases(path: Path | None) -> dict[str, str]:
    """Load supported email-to-person JSON shapes."""
    if path is None or not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("identity mapping must be a JSON object")

    wrapped = payload.get("email_to_person")
    if isinstance(wrapped, dict):
        return {
            str(email).strip().lower(): str(person).strip()
            for email, person in wrapped.items()
            if str(email).strip() and str(person).strip()
        }

    if all(isinstance(value, str) for value in payload.values()):
        return {
            str(email).strip().lower(): str(person).strip()
            for email, person in payload.items()
            if str(email).strip() and str(person).strip()
        }

    aliases: dict[str, str] = {}
    for person, metadata in payload.items():
        if not isinstance(metadata, dict):
            continue
        for email in metadata.get("emails", []):
            normalized = str(email).strip().lower()
            if normalized:
                aliases[normalized] = str(person).strip()
    return aliases


def row_counts(row: dict[str, str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for category in CATEGORIES:
        counts[f"{category}_ins"] = integer(row.get(f"{category}_ins"))
        counts[f"{category}_del"] = integer(row.get(f"{category}_del"))
    return counts


def activity_weight(row: dict[str, str], counts: dict[str, int]) -> float:
    """Return a bounded, auditable score for one non-merge commit."""
    added = counts["code_ins"]
    removed = counts["code_del"]
    source_churn = added + removed
    total_churn = sum(counts.values())
    if added == 0 or source_churn == 0 or total_churn == 0:
        return 0.0

    source_share = source_churn / total_churn
    file_spread = min(integer(row.get("files_changed")), 12) / 12

    # A deliberately modest proxy: at most 20 points, based on how much of the
    # change is source code and how broadly it is distributed.
    complexity_proxy = 20 * source_share * file_spread

    insertion_share = added / source_churn
    if insertion_share >= 0.95:
        novelty_adjustment = 0.50
    elif insertion_share >= 0.75:
        novelty_adjustment = 0.25
    else:
        novelty_adjustment = 0.0

    multiplier = 1 + (0.05 * complexity_proxy) + novelty_adjustment
    return added * multiplier


@dataclass
class PersonTotals:
    commits: int = 0
    code_ins: int = 0
    code_del: int = 0
    test_ins: int = 0
    test_del: int = 0
    config_ins: int = 0
    config_del: int = 0
    docs_ins: int = 0
    docs_del: int = 0
    other_ins: int = 0
    other_del: int = 0
    weighted_code_lines: float = 0.0

    def add(self, row: dict[str, str]) -> None:
        counts = row_counts(row)
        self.commits += 1
        for key, value in counts.items():
            setattr(self, key, getattr(self, key) + value)
        self.weighted_code_lines += activity_weight(row, counts)

    def churn(self, category: str) -> int:
        return getattr(self, f"{category}_ins") + getattr(self, f"{category}_del")

    @property
    def code_loc(self) -> int:
        return self.code_ins - self.code_del

    @property
    def support_churn(self) -> int:
        return sum(self.churn(category) for category in CATEGORIES if category != "code")


def collect(
    rows: Iterable[dict[str, str]], aliases: dict[str, str]
) -> dict[str, PersonTotals]:
    people: dict[str, PersonTotals] = {}
    for row in rows:
        if integer(row.get("is_merge")) == 1:
            continue
        email = (row.get("author_email") or "").strip().lower()
        identity = aliases.get(email, email)
        if not identity:
            continue
        totals = people.setdefault(identity, PersonTotals())
        totals.add(row)
    return people


def rating_band(score: float, team_median: float) -> str:
    if team_median <= 0:
        return "U"
    relative = score / team_median
    if relative >= 1.5:
        return "A"
    if relative >= 0.7:
        return "B"
    if relative >= 0.3:
        return "C"
    return "D"


def output_rows(
    people: dict[str, PersonTotals], team_median: float
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    ordered = sorted(
        people.items(), key=lambda item: (-item[1].weighted_code_lines, item[0])
    )
    for person, totals in ordered:
        code_churn = totals.churn("code")
        all_churn = code_churn + totals.support_churn
        support_share = totals.support_churn / all_churn if all_churn else 0.0
        relative = totals.weighted_code_lines / team_median if team_median else 0.0
        result.append(
            {
                "person": person,
                "commits": totals.commits,
                "code_loc": totals.code_loc,
                "code_churn": code_churn,
                "test_loc": totals.churn("test"),
                "config_loc": totals.churn("config"),
                "docs_loc": totals.churn("docs"),
                "other_loc": totals.churn("other"),
                "support_share": f"{support_share:.3f}",
                "weighted_code_lines": f"{totals.weighted_code_lines:.1f}",
                "weighted_vs_median": f"{relative:.2f}",
                "band": rating_band(totals.weighted_code_lines, team_median),
            }
        )
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "person",
        "commits",
        "code_loc",
        "code_churn",
        "test_loc",
        "config_loc",
        "docs_loc",
        "other_loc",
        "support_share",
        "weighted_code_lines",
        "weighted_vs_median",
        "band",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]], team_median: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Code Contribution Activity",
        "",
        f"Median weighted code lines for contributors with at least "
        f"{MIN_COMMITS_FOR_MEDIAN} commits: **{team_median:.1f}**.",
        "",
        "Bands compare this heuristic with the eligible team median: "
        "A >= 1.5x, B >= 0.7x, C >= 0.3x, D below 0.3x, U unavailable.",
        "",
        "This is an activity signal, not an individual performance score. "
        "Review source-data coverage and contribution context before use.",
        "",
        "| Person | Commits | Code LOC | Code churn | Test | Config | Docs | "
        "Other | Support share | Weighted | x median | Band |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:-:|",
    ]
    for row in rows:
        lines.append(
            "| {person} | {commits} | {code_loc} | {code_churn} | {test_loc} | "
            "{config_loc} | {docs_loc} | {other_loc} | {support_share} | "
            "{weighted_code_lines} | {weighted_vs_median} | {band} |".format(**row)
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Augmented commit CSV")
    parser.add_argument("--out-csv", required=True, type=Path, help="Summary CSV")
    parser.add_argument("--out-md", type=Path, help="Optional Markdown summary")
    parser.add_argument("--identity", type=Path, help="Optional identity alias JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    aliases = load_aliases(args.identity)
    with args.input.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            print("Input CSV has no header.")
            return 2
        required = {"author_email", "is_merge", "code_ins", "code_del"}
        missing = sorted(required.difference(reader.fieldnames))
        if missing:
            print(f"Input CSV is missing required columns: {', '.join(missing)}")
            return 2
        people = collect(reader, aliases)

    eligible = [
        totals.weighted_code_lines
        for totals in people.values()
        if totals.commits >= MIN_COMMITS_FOR_MEDIAN
    ]
    team_median = statistics.median(eligible) if eligible else 0.0
    rows = output_rows(people, team_median)
    write_csv(args.out_csv, rows)
    if args.out_md is not None:
        write_markdown(args.out_md, rows, team_median)

    print(
        f"Wrote {args.out_csv} for {len(rows)} contributors "
        f"(eligible median {team_median:.1f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
