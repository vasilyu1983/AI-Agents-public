#!/usr/bin/env python3
"""Compute per-person code-only LOC and a complexity-weighted rating from raw-commits.csv.

Reads the augmented schema produced by extract-commits.sh (with code_ins/code_del,
test_ins/test_del, config_ins/config_del, docs_ins/docs_del, other_ins/other_del).
Older CSVs without the per-class columns produce zeros for those splits — re-run the
extractor first.

Outputs:
  - tables/code-rating.csv: one row per person with code_loc, churn_loc, complexity
    proxy, weighted code lines, band, and supporting-activity ratio.
  - reports/code-rating.md: short markdown summary banded against the team median.

Tier-1 rating uses a numstat-only complexity proxy (file diversity, novelty share,
max-extension share). For Tier-2 cyclomatic complexity, run a separate static-analysis
pass (lizard, scc, sonar) against repo checkouts and merge the result on commit_hash.

See:
  references/loc-measurement-best-practices.md → "Code LOC: Extension-Level Filtering"
  references/loc-measurement-best-practices.md → "Complexity-Weighted Rating"
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

# Tunable rating weights. Mirror the formula in loc-measurement-best-practices.md.
ALPHA = 0.05   # cyclomatic-delta multiplier (per +1 ΔCC)
BETA = 1.0     # novelty multiplier
DELTA_CC_CAP = 20

# Numstat-only complexity proxy. See module docstring for the upgrade path.
def complexity_proxy(commit: dict[str, int]) -> float:
    """Return a non-negative ΔCC proxy in [0, DELTA_CC_CAP].

    Without a repo checkout we cannot compute real cyclomatic delta. The proxy
    rewards commits that touch more code files (broader change surface) and
    have a higher code share (less config noise). It is intentionally weak —
    swap for real CC when checkouts and lizard/scc are available.
    """
    files = max(commit.get("files_changed", 0), 1)
    code_ins = commit.get("code_ins", 0)
    code_del = commit.get("code_del", 0)
    code_lines = code_ins + code_del
    total_lines = (
        code_lines
        + commit.get("test_ins", 0) + commit.get("test_del", 0)
        + commit.get("config_ins", 0) + commit.get("config_del", 0)
        + commit.get("docs_ins", 0) + commit.get("docs_del", 0)
        + commit.get("other_ins", 0) + commit.get("other_del", 0)
    )
    if total_lines == 0 or code_lines == 0:
        return 0.0
    code_share = code_lines / total_lines
    # File-spread proxy: log-shaped, capped.
    spread = min(files, 10) / 10.0  # 0.1 .. 1.0
    proxy = DELTA_CC_CAP * code_share * spread
    return max(0.0, min(proxy, DELTA_CC_CAP))


def novelty(commit: dict[str, int]) -> float:
    """Coarse novelty estimate from numstat shape.

    Without per-file new/modified/deleted classification we approximate with the
    insertion / total ratio. Pure refactors (heavy deletes) get 0; new modules
    where deletions are minimal get up to 0.5. Matches the bands in the spec.
    """
    code_ins = commit.get("code_ins", 0)
    code_del = commit.get("code_del", 0)
    total = code_ins + code_del
    if total == 0:
        return 0.0
    add_ratio = code_ins / total
    if add_ratio >= 0.95:
        return 0.5
    if add_ratio >= 0.7:
        return 0.25
    return 0.0


def weighted_code_lines(commit: dict[str, int]) -> float:
    """Per-commit weighted code lines: code_loc × (1 + α·ΔCC + β·novelty)."""
    net_code = commit.get("code_ins", 0) - commit.get("code_del", 0)
    if net_code <= 0:
        # Refactors that net-delete still earn baseline credit on insertions only,
        # so the rating does not punish cleanup. ΔCC stays floored at 0.
        net_code = max(0, commit.get("code_ins", 0))
    factor = 1.0 + ALPHA * complexity_proxy(commit) + BETA * novelty(commit)
    return net_code * factor


def parse_int(value: str | None) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(value)
    except ValueError:
        return 0


def aggregate(rows: list[dict], identity_map: dict[str, str] | None) -> dict[str, dict]:
    by_person: dict[str, dict] = defaultdict(lambda: {
        "commits": 0,
        "code_ins": 0, "code_del": 0,
        "test_ins": 0, "test_del": 0,
        "config_ins": 0, "config_del": 0,
        "docs_ins": 0, "docs_del": 0,
        "other_ins": 0, "other_del": 0,
        "weighted_code_lines": 0.0,
    })
    for row in rows:
        if parse_int(row.get("is_merge")) == 1:
            continue
        email = (row.get("author_email") or "").lower()
        person = identity_map.get(email, email) if identity_map else email
        if not person:
            continue
        commit = {
            "files_changed": parse_int(row.get("files_changed")),
            "code_ins": parse_int(row.get("code_ins")),
            "code_del": parse_int(row.get("code_del")),
            "test_ins": parse_int(row.get("test_ins")),
            "test_del": parse_int(row.get("test_del")),
            "config_ins": parse_int(row.get("config_ins")),
            "config_del": parse_int(row.get("config_del")),
            "docs_ins": parse_int(row.get("docs_ins")),
            "docs_del": parse_int(row.get("docs_del")),
            "other_ins": parse_int(row.get("other_ins")),
            "other_del": parse_int(row.get("other_del")),
        }
        agg = by_person[person]
        agg["commits"] += 1
        for k, v in commit.items():
            if k == "files_changed":
                continue
            agg[k] += v
        agg["weighted_code_lines"] += weighted_code_lines(commit)
    return by_person


def band(weighted: float, median: float) -> str:
    if median <= 0:
        return "U"  # undetermined: team has no signal
    ratio = weighted / median
    if ratio >= 1.5:
        return "A"
    if ratio >= 0.7:
        return "B"
    if ratio >= 0.3:
        return "C"
    return "D"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path, help="raw-commits.csv (augmented schema)")
    ap.add_argument("--out-csv", required=True, type=Path, help="Per-person table output")
    ap.add_argument("--out-md", type=Path, help="Optional markdown summary output")
    ap.add_argument("--identity", type=Path, help="identity-aliases.json (email -> person)")
    args = ap.parse_args()

    identity_map = None
    if args.identity and args.identity.exists():
        raw = json.loads(args.identity.read_text())
        identity_map = {}
        # Three accepted shapes:
        # 1. Flat {email: person}
        # 2. Wrapped {"email_to_person": {email: person}, ...metadata}
        # 3. Catalog {person: {"emails": [...]}}
        if isinstance(raw, dict) and isinstance(raw.get("email_to_person"), dict):
            for email, person in raw["email_to_person"].items():
                identity_map[email.lower()] = person
        elif isinstance(raw, dict) and all(isinstance(v, str) for v in raw.values()):
            identity_map = {k.lower(): v for k, v in raw.items()}
        else:
            for person, info in raw.items():
                if isinstance(info, dict):
                    for email in info.get("emails", []):
                        identity_map[email.lower()] = person

    with args.input.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("No commits in input.", flush=True)
        return 0
    if "code_ins" not in rows[0]:
        print(
            "ERROR: input CSV is missing per-class columns (code_ins, etc.). "
            "Re-run extract-commits.sh against the augmented schema.",
            flush=True,
        )
        return 2

    by_person = aggregate(rows, identity_map)
    weighted_values = [p["weighted_code_lines"] for p in by_person.values() if p["commits"] >= 5]
    team_median = statistics.median(weighted_values) if weighted_values else 0.0

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "person", "commits",
        "code_loc", "code_churn", "test_loc", "config_loc", "docs_loc", "other_loc",
        "support_share",
        "weighted_code_lines", "weighted_vs_median", "band",
    ]
    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for person, agg in sorted(by_person.items(), key=lambda kv: -kv[1]["weighted_code_lines"]):
            code_loc = agg["code_ins"] - agg["code_del"]
            code_churn = agg["code_ins"] + agg["code_del"]
            test_loc = agg["test_ins"] + agg["test_del"]
            config_loc = agg["config_ins"] + agg["config_del"]
            docs_loc = agg["docs_ins"] + agg["docs_del"]
            other_loc = agg["other_ins"] + agg["other_del"]
            non_code_total = test_loc + config_loc + docs_loc + other_loc
            denom = code_churn + non_code_total
            support_share = (non_code_total / denom) if denom else 0.0
            ratio = (agg["weighted_code_lines"] / team_median) if team_median else 0.0
            writer.writerow({
                "person": person,
                "commits": agg["commits"],
                "code_loc": code_loc,
                "code_churn": code_churn,
                "test_loc": test_loc,
                "config_loc": config_loc,
                "docs_loc": docs_loc,
                "other_loc": other_loc,
                "support_share": f"{support_share:.3f}",
                "weighted_code_lines": f"{agg['weighted_code_lines']:.1f}",
                "weighted_vs_median": f"{ratio:.2f}",
                "band": band(agg["weighted_code_lines"], team_median),
            })

    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        with args.out_md.open("w") as f:
            f.write("# Code-Only LOC and Complexity-Weighted Rating\n\n")
            f.write(f"Team median weighted code lines (>= 5 commits): **{team_median:.1f}**\n\n")
            f.write("Bands: A (>=1.5x median), B (0.7-1.5x), C (0.3-0.7x), D (<0.3x).\n\n")
            f.write("Rating uses a numstat-only complexity proxy. For real cyclomatic complexity, ")
            f.write("run a static-analysis pass (lizard, scc, sonar) against repo checkouts and ")
            f.write("merge on commit_hash.\n\n")
            f.write(
                "Buckets: **Code** = py/ts/go/rs/java/swift/sql/css/sh… "
                "**Test** = test/spec dirs + `_test`/`.test`. "
                "**Config** = json/yaml/toml/xml/.env/Dockerfile… "
                "**Docs** = md/mdx/rst/txt/adoc. "
                "**Other** = lockfiles, minified, generated, vendored, binary. "
                "Code% = code churn / (code + non-code churn). "
                "Full recognition rules: "
                "`packs/it-insider-risk/references/loc-bucket-classification.md`.\n\n"
            )
            f.write(
                "| Person | Commits | Code LOC | Code Churn | Test | Config | Docs | Other | Code% | Weighted | x Median | Band |\n"
            )
            f.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:-:|\n")
            for person, agg in sorted(by_person.items(), key=lambda kv: -kv[1]["weighted_code_lines"]):
                code_loc = agg["code_ins"] - agg["code_del"]
                code_churn = agg["code_ins"] + agg["code_del"]
                test_loc = agg["test_ins"] + agg["test_del"]
                config_loc = agg["config_ins"] + agg["config_del"]
                docs_loc = agg["docs_ins"] + agg["docs_del"]
                other_loc = agg["other_ins"] + agg["other_del"]
                non_code_total = test_loc + config_loc + docs_loc + other_loc
                denom = code_churn + non_code_total
                code_share = (code_churn / denom) if denom else 0.0
                ratio = (agg["weighted_code_lines"] / team_median) if team_median else 0.0
                f.write(
                    f"| {person} | {agg['commits']} | {code_loc} | {code_churn} | "
                    f"{test_loc} | {config_loc} | {docs_loc} | {other_loc} | "
                    f"{code_share:.0%} | {agg['weighted_code_lines']:.0f} | "
                    f"{ratio:.2f} | {band(agg['weighted_code_lines'], team_median)} |\n"
                )

    print(f"Wrote {args.out_csv} ({len(by_person)} people, median weighted = {team_median:.1f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
