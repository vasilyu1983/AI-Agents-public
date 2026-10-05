#!/usr/bin/env python3
"""Extract contribution quality profiles from raw-commits.csv and mr-acceptances.csv.

Reads the commit and MR CSV format documented in scripts/README.md. Computes Tier 1
signals per person and outputs contribution-profiles.json. Unmeasured signals are
reported as unknown (None), never imputed; volume signals are context, never scored.

Usage:
    python extract-contribution-profile.py --config config/report-config.json
    python extract-contribution-profile.py --commits raw.csv --mr mrs.csv --output profiles.json
"""

import argparse
import csv
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "analysis_window_days": 90,
    "thresholds": {
        "min_commits": 30,
        "churn_14d_pct_good": 8,
        "churn_14d_pct_warning": 15,
        "churn_14d_pct_red": 25,
        "pr_size_elite": 250,
        "pr_size_good": 500,
        "self_merge_rate_warning": 5,
        "commit_msg_min_length": 10,
        "review_rate_good_per_week": 2.0,
        "test_ratio_good": 40,
    },
    "email_to_person": {},
    "person_timezone": {"_default": 0},
    "role_calibration": {},
    "target_persons": [],
    "non_working_date_ranges": [],
}

CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(feat|fix|refactor|test|docs|chore|style|perf|ci|build)(\(.+\))?: .+"
)
IMPERATIVE_VERBS = {
    "add", "fix", "update", "remove", "refactor", "implement", "change",
    "create", "delete", "move", "rename", "extract", "improve", "replace",
    "merge", "revert", "bump", "set", "use", "handle", "support", "enable",
    "disable", "configure", "integrate", "migrate", "optimize", "simplify",
    "introduce", "apply", "adjust", "clean", "resolve", "prevent", "ensure",
}
GENERIC_SUBJECTS = {
    "update", "fix", "fix bug", "changes", "wip", "temp", "misc", "stuff",
    "minor", "cleanup", "small fix", "hotfix", "patch", "quick fix",
}
REFACTOR_KEYWORDS = {"refactor", "rename", "move", "extract", "reorganize", "restructure"}
TICKET_RE = re.compile(r"^[A-Z]{2,10}-\d+")


# ---------------------------------------------------------------------------
# Identity resolution
# ---------------------------------------------------------------------------

def load_identity_aliases(config: dict, config_dir: Path) -> dict[str, str]:
    """Build email -> canonical name mapping from alias matrix + config overrides."""
    email_to_person: dict[str, str] = {}

    # Load shared alias matrix if configured.
    alias_path = config.get("identity_alias_matrix_json", "")
    if alias_path:
        resolved = (config_dir / alias_path).resolve() if not Path(alias_path).is_absolute() else Path(alias_path)
        if resolved.exists():
            with open(resolved) as f:
                alias_data = json.load(f)
            for email, name in alias_data.get("email_to_person", {}).items():
                if not email.startswith("_"):
                    email_to_person[email.lower()] = name

    # Layer config-local overrides.
    for email, name in config.get("email_to_person", {}).items():
        if not email.startswith("_"):
            email_to_person[email.lower()] = name

    return email_to_person


def resolve_person(email: str, name: str, alias_map: dict[str, str]) -> str:
    """Resolve an email+name pair to a canonical person name."""
    canonical = alias_map.get(email.lower())
    if canonical:
        return canonical
    return name


# ---------------------------------------------------------------------------
# CSV reading
# ---------------------------------------------------------------------------

REVERT_SUBJECT_RE = re.compile(r'^Revert\s+"(?P<original>.+?)"\s*$')


def read_commits_csv(path: Path) -> list[dict]:
    """Read raw-commits.csv, dedupe by (repo, commit_hash), and flag revert pairs.

    A revert pair is `Revert "X"` whose ins/del are the inverse of a prior
    commit with subject "X" in the same repo. Both rows are marked
    ``net_cancel=True`` so downstream aggregations (net_lines, churn proxy)
    can skip self-cancelling churn.
    """
    rows = []
    seen: set[tuple[str, str]] = set()
    dupes = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["insertions"] = int(row.get("insertions", 0) or 0)
            row["deletions"] = int(row.get("deletions", 0) or 0)
            row["files_changed"] = int(row.get("files_changed", 0) or 0)
            row["hour"] = int(row.get("hour", 0) or 0)
            row["is_merge"] = str(row.get("is_merge", "0")).strip() in ("1", "true", "True")
            row["is_move"] = str(row.get("is_move", "0")).strip() in ("1", "true", "True")
            row["net_cancel"] = False
            key = (row.get("repo", ""), row.get("commit_hash", "") or row.get("hash", ""))
            if key[1] and key in seen:
                dupes += 1
                continue
            if key[1]:
                seen.add(key)
            rows.append(row)
    if dupes:
        print(f"  → dedupe: dropped {dupes} duplicate (repo, commit_hash) rows")

    # Revert-pair detection: for each "Revert \"X\"" row, find a prior same-repo
    # row with subject X whose ins/del are the inverse, and mark both net_cancel.
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_repo[r.get("repo", "")].append(r)

    pairs = 0
    for repo, repo_rows in by_repo.items():
        repo_rows.sort(key=lambda x: x.get("datetime", ""))
        for i, r in enumerate(repo_rows):
            subj = (r.get("subject") or "").strip()
            m = REVERT_SUBJECT_RE.match(subj)
            if not m:
                continue
            target = m.group("original").strip()
            for j in range(i - 1, -1, -1):
                prior = repo_rows[j]
                if prior.get("net_cancel"):
                    continue
                if (prior.get("subject") or "").strip() != target:
                    continue
                if (prior["insertions"] == r["deletions"]
                        and prior["deletions"] == r["insertions"]
                        and (prior["insertions"] + prior["deletions"]) > 0):
                    prior["net_cancel"] = True
                    r["net_cancel"] = True
                    pairs += 1
                    break
    if pairs:
        print(f"  → revert pairs: {pairs} self-cancelling pair(s) flagged")
    return rows


def read_mr_csv(path: Path) -> list[dict]:
    """Read mr-acceptances.csv and return list of row dicts."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["insertions"] = int(row.get("insertions", 0) or 0)
            row["deletions"] = int(row.get("deletions", 0) or 0)
            row["files_changed"] = int(row.get("files_changed", 0) or 0)
            rows.append(row)
    return rows


def parse_date(iso_str: str) -> date | None:
    """Extract date from ISO 8601 datetime string."""
    if not iso_str:
        return None
    try:
        return date.fromisoformat(iso_str[:10])
    except ValueError:
        return None


def iso_week(d: date) -> str:
    """Return ISO year-week string like '2026-W12'."""
    cal = d.isocalendar()
    return f"{cal[0]}-W{cal[1]:02d}"


# ---------------------------------------------------------------------------
# Non-working day filtering
# ---------------------------------------------------------------------------

def build_non_working_dates(ranges: list[dict]) -> set[date]:
    """Build a set of non-working dates from configured ranges."""
    dates = set()
    for r in ranges:
        start = date.fromisoformat(r["start"])
        end = date.fromisoformat(r["end"])
        current = start
        while current <= end:
            dates.add(current)
            current += timedelta(days=1)
    return dates


def expected_working_days(start: date, end: date, non_working: set[date]) -> int:
    """Count expected working days (Mon-Fri, excluding non-working ranges)."""
    count = 0
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in non_working:
            count += 1
        current += timedelta(days=1)
    return count


# ---------------------------------------------------------------------------
# Signal computation
# ---------------------------------------------------------------------------

def compute_d1_signals(commits: list[dict], mrs: list[dict],
                       window_start: date, window_end: date,
                       non_working: set[date], role_config: dict) -> dict:
    """Compute Dimension 1: Delivery Consistency signals."""
    # Weekly commit counts.
    weekly_counts: Counter[str] = Counter()
    active_dates: set[date] = set()
    for c in commits:
        d = parse_date(c.get("datetime", ""))
        if d:
            weekly_counts[iso_week(d)] += 1
            active_dates.add(d)

    # All weeks in the window.
    total_weeks = max(1, (window_end - window_start).days / 7)
    all_weeks = set()
    current = window_start
    while current <= window_end:
        all_weeks.add(iso_week(current))
        current += timedelta(days=7)
    # Fill missing weeks with 0.
    counts = [weekly_counts.get(w, 0) for w in sorted(all_weeks)]

    mean_weekly = statistics.mean(counts) if counts else 0
    std_weekly = statistics.stdev(counts) if len(counts) > 1 else 0
    cv = std_weekly / mean_weekly if mean_weekly > 0 else float("inf")

    exp_days = expected_working_days(window_start, window_end, non_working)
    active_days_coverage = len(active_dates) / exp_days if exp_days > 0 else 0

    # MR throughput.
    mr_count = len(mrs)
    mr_per_week = mr_count / total_weeks if total_weeks > 0 else 0
    mr_baseline = role_config.get("mr_baseline_per_week", 2.0)

    # Delivery trend: compare first-half vs second-half commit counts.
    mid = window_start + (window_end - window_start) / 2
    first_half = sum(1 for c in commits if (d := parse_date(c.get("datetime", ""))) and d <= mid)
    second_half = len(commits) - first_half
    if first_half > 0:
        trend_ratio = second_half / first_half
    else:
        trend_ratio = 1.0 if second_half == 0 else 2.0

    return {
        "weekly_commit_counts": counts,
        "mean_weekly_commits": round(mean_weekly, 2),
        "commit_frequency_cv": round(cv, 3),
        "active_days": len(active_dates),
        "expected_working_days": exp_days,
        "active_days_coverage_pct": round(active_days_coverage * 100, 1),
        "mr_count": mr_count,
        "mr_per_week": round(mr_per_week, 2),
        "mr_baseline_per_week": mr_baseline,
        "delivery_trend_ratio": round(trend_ratio, 2),
        "total_weeks": round(total_weeks, 1),
    }


def wilson_interval(successes: int, n: int, z: float = 1.96) -> list[float] | None:
    """95% Wilson score interval for a proportion, in percent. None when n == 0.

    Person-level rates on small samples (< ~30 changes) are wide; never call two
    people different unless their intervals separate (see scoring-model.md).
    """
    if n <= 0:
        return None
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [round(max(0.0, centre - half) * 100, 1), round(min(1.0, centre + half) * 100, 1)]


def compute_d2_signals(commits: list[dict]) -> dict:
    """Compute Dimension 2: Code Quality Signals (Tier 1 only).

    Revert pairs (``net_cancel=True``) are excluded from insertion/deletion
    totals — their churn is a data-quality artefact, not a quality signal.

    Churn, duplication and the refactoring ratio need per-file / per-line data
    (numstat with paths, or a repo checkout). The aggregate commit CSV has no
    file paths, so these are returned as ``None`` (unknown), never imputed.
    The earlier same-repo proxy summed ``min(c2.deletions, c1.insertions)`` over
    every later commit pair, which penalised small commits and could exceed 100%.
    """
    scored = [c for c in commits if not c.get("net_cancel")]
    revert_pair_commits = len(commits) - len(scored)
    total_insertions = sum(c["insertions"] for c in scored)
    total_deletions = sum(c["deletions"] for c in scored)
    code_ins = sum(int(c.get("code_ins", 0) or 0) for c in scored)
    code_del = sum(int(c.get("code_del", 0) or 0) for c in scored)

    # Subject-keyword share: context only. The D2 refactoring ratio is
    # moved/renamed lines vs net-new lines, which the CSV cannot measure.
    refactor_commits = sum(
        1 for c in scored
        if any(kw in c.get("subject", "").lower() for kw in REFACTOR_KEYWORDS)
    )
    refactor_keyword_share = (refactor_commits / len(scored) * 100) if scored else 0

    return {
        "total_insertions": total_insertions,
        "total_deletions": total_deletions,
        "net_lines": total_insertions - total_deletions,
        "churn_loc": total_insertions + total_deletions,
        "code_loc": code_ins + code_del,
        "del_ratio": round(total_deletions / (total_insertions + total_deletions), 3)
            if (total_insertions + total_deletions) > 0 else 0,
        "revert_pair_commits_excluded": revert_pair_commits,
        "churn_14d_pct": None,
        "churn_method": "unavailable_requires_per_file_line_history",
        "refactoring_ratio_pct": None,
        "refactoring_method": "unavailable_requires_move_detection_per_line",
        "refactoring_keyword_share_pct_context_only": round(refactor_keyword_share, 1),
        "duplication_ratio_pct": None,
        "duplication_method": "unavailable_requires_repo_checkout",
        "complexity_delta": None,
        "cc_compliance_rate": None,
    }


def compute_d3_signals(commits: list[dict], mrs: list[dict],
                       person: str, alias_map: dict[str, str]) -> dict:
    """Compute Dimension 3: Commit Craft signals."""
    # Commit message quality.
    msg_scores = []
    generic_count = 0
    for c in commits:
        subject = c.get("subject", "").strip()
        score = 0
        if len(subject) >= 10:
            score += 1
        if CONVENTIONAL_COMMIT_RE.match(subject):
            score += 1
        first_word = subject.split("(")[0].split(":")[0].split(" ")[0].lower()
        if first_word in IMPERATIVE_VERBS:
            score += 1
        # What/why: longer messages that aren't generic.
        if len(subject) > 30 and subject.lower().strip() not in GENERIC_SUBJECTS:
            score += 2
        elif len(subject) > 20 and subject.lower().strip() not in GENERIC_SUBJECTS:
            score += 1
        msg_scores.append(score)
        if subject.lower().strip() in GENERIC_SUBJECTS or len(subject) < 5:
            generic_count += 1

    mean_msg_score = statistics.mean(msg_scores) if msg_scores else 0

    # Commit scope: files per commit.
    files_per_commit = [c["files_changed"] for c in commits]
    mean_files = statistics.mean(files_per_commit) if files_per_commit else 0
    median_files = statistics.median(files_per_commit) if files_per_commit else 0

    # PR size discipline.
    mr_sizes = [m["insertions"] + m["deletions"] for m in mrs]
    small_pr_count = sum(1 for s in mr_sizes if s < 250)
    medium_pr_count = sum(1 for s in mr_sizes if s < 500)
    small_pr_pct = (small_pr_count / len(mr_sizes) * 100) if mr_sizes else 0
    medium_pr_pct = (medium_pr_count / len(mr_sizes) * 100) if mr_sizes else 0

    # Self-merge detection.
    # A self-merge occurs when the merger (in MR CSV) matches the commit author
    # (the person being analyzed). Compare canonical names after alias resolution.
    person_lower = person.lower()
    self_merge_count = 0
    for m in mrs:
        merger_email = m.get("merger_email", "")
        merger_name = m.get("merger_name", "")
        canonical_merger = resolve_person(merger_email, merger_name, alias_map).lower()
        if canonical_merger == person_lower:
            self_merge_count += 1
    self_merge_rate = (self_merge_count / len(mrs) * 100) if mrs else 0

    return {
        "mean_message_quality_score": round(mean_msg_score, 2),
        "max_message_score": 5,
        "generic_message_pct": round((generic_count / len(commits) * 100) if commits else 0, 1),
        "mean_files_per_commit": round(mean_files, 1),
        "median_files_per_commit": round(median_files, 1),
        "pr_count": len(mrs),
        "small_pr_pct": round(small_pr_pct, 1),
        "medium_pr_pct": round(medium_pr_pct, 1),
        "pr_size_p50": round(statistics.median(mr_sizes), 0) if mr_sizes else 0,
        "pr_size_p90": round(sorted(mr_sizes)[int(len(mr_sizes) * 0.9)] if mr_sizes else 0, 0),
        "self_merge_count": self_merge_count,
        "self_merge_rate_pct": round(self_merge_rate, 1),
        "self_merge_rate_ci95": wilson_interval(self_merge_count, len(mrs)),
        "small_pr_pct_ci95": wilson_interval(small_pr_count, len(mr_sizes)),
    }


def compute_d4_signals(mrs: list[dict], person: str,
                       all_mrs: list[dict], alias_map: dict[str, str],
                       commits: list[dict], total_weeks: float) -> dict:
    """Compute Dimension 4: Review & Collaboration signals.

    Merge events are not review events: merge queues and bots zero them and
    maintainers inflate them. Review participation needs forge review events
    (approvals, comments, requested changes); the CSV has none, so
    ``review_events_per_week`` is None and merges of others' MRs are context only.
    """
    person_lower = person.lower()

    merges_of_others = 0
    for m in all_mrs:
        merger_email = m.get("merger_email", "")
        merger_name = m.get("merger_name", "")
        canonical_merger = resolve_person(merger_email, merger_name, alias_map).lower()
        if canonical_merger != person_lower:
            continue
        # This person merged it. But is it their own MR?
        # Check source_branch for person name hints (imperfect but best available from CSV).
        source_branch = m.get("source_branch", "").lower()
        # If this MR is NOT in their authored-MR list, count it as a review.
        is_own = m in mrs
        if not is_own:
            merges_of_others += 1

    merges_per_week = merges_of_others / total_weeks if total_weeks > 0 else 0

    # Cross-repo contribution.
    repos = Counter(c.get("repo", "unknown") for c in commits)
    meaningful_repos = sum(1 for count in repos.values() if count >= 5)
    primary_repo_pct = (max(repos.values()) / len(commits) * 100) if commits and repos else 100

    return {
        "review_events_per_week": None,
        "review_participation_method": "unavailable_requires_forge_review_events",
        "merges_of_others": merges_of_others,
        "merges_of_others_per_week": round(merges_per_week, 2),
        "review_responsiveness_hours": None,
        "review_responsiveness_method": "unavailable_requires_api_data",
        "review_depth_avg_comments": None,
        "review_depth_method": "unavailable_requires_api_data",
        "distinct_repos_meaningful": meaningful_repos,
        "primary_repo_concentration_pct": round(primary_repo_pct, 1),
    }


def compute_d5_signals(commits: list[dict]) -> dict:
    """Compute Dimension 5: Test & Safety Practices (from commit subjects only).

    Note: Full D5 analysis requires file-path-level data (Tier 2).
    From CSV we can only use subject-based heuristics.
    """
    test_keywords = {"test", "spec", "tests", "testing"}
    feature_keywords = {"feat", "feature", "add", "implement", "introduce", "create"}
    fix_keywords = {"fix", "bug", "hotfix", "patch"}

    commits_with_test_signal = 0
    feature_commits = 0
    feature_with_test = 0

    for c in commits:
        subject = c.get("subject", "").lower()
        has_test = any(kw in subject for kw in test_keywords)
        is_feature = any(kw in subject for kw in feature_keywords)
        is_fix = any(kw in subject for kw in fix_keywords)

        if has_test:
            commits_with_test_signal += 1
        if is_feature or is_fix:
            feature_commits += 1
            if has_test:
                feature_with_test += 1

    test_signal_pct = (commits_with_test_signal / len(commits) * 100) if commits else 0
    feature_test_pct = (feature_with_test / feature_commits * 100) if feature_commits > 0 else 0

    return {
        "commits_with_test_signal": commits_with_test_signal,
        "test_signal_pct": round(test_signal_pct, 1),
        "feature_commits": feature_commits,
        "feature_with_test_pct": round(feature_test_pct, 1),
        "method": "subject_keyword_heuristic",
        "security_file_awareness": None,
        "security_method": "unavailable_requires_file_paths",
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
#
# Unmeasured sub-signals score ``None`` and are excluded from the achievable
# maximum: unknowns are not zeroes and never earn imputed credit. Volume
# signals (active days, MR throughput, merges of others' MRs, weighted LOC) are
# context annotations, never scored as quality.

def _band(value, cuts: list[tuple[float, int]], default: int = 0, higher_is_better: bool = True) -> int:
    for cut, pts in cuts:
        if (value >= cut) if higher_is_better else (value < cut):
            return pts
    return default


def _dimension(breakdown: dict, maxes: dict, nominal_max: int, multiplier: float = 1.0) -> dict:
    measured = {k: v for k, v in breakdown.items() if v is not None}
    max_achievable = sum(maxes[k] for k in measured)
    unmeasured = sorted(k for k, v in breakdown.items() if v is None)
    if not measured:
        return {
            "score": None,
            "max": nominal_max,
            "max_achievable": 0,
            "status": "insufficient_evidence",
            "breakdown": breakdown,
            "unmeasured": unmeasured,
            "role_multiplier": multiplier,
        }
    raw = sum(measured.values())
    return {
        "score": min(max_achievable, round(raw * multiplier)),
        "max": nominal_max,
        "max_achievable": max_achievable,
        "status": "partial" if unmeasured else "measured",
        "breakdown": breakdown,
        "unmeasured": unmeasured,
        "role_multiplier": multiplier,
    }


D2_MAX = {"churn_rate": 8, "duplication_ratio": 5, "refactoring_ratio": 5, "cc_compliance": 3}
D3_MAX = {"commit_message_quality": 5, "commit_scope_discipline": 4, "pr_size_discipline": 4, "merge_hygiene": 2}
D4_MAX = {"review_participation": 7, "review_responsiveness": 5, "review_depth": 4, "cross_repo_contribution": 4}
D5_MAX = {"test_to_code_ratio": 4, "test_presence_in_features": 3, "security_file_awareness": 3}


def score_d1(signals: dict, thresholds: dict, role_config: dict) -> dict:
    """Keep delivery cadence as context; commit timing is not a quality score."""
    return {
        "score": None, "max": 0, "max_achievable": 0,
        "status": "context_only", "breakdown": {}, "unmeasured": [],
        "role_multiplier": 1.0,
    }


def score_d2(signals: dict, thresholds: dict, role_config: dict) -> dict:
    """Score Dimension 2: Code Quality Signals (0-21 points)."""
    churn = signals.get("churn_14d_pct")
    churn_pts = None if churn is None else _band(
        churn,
        [(thresholds.get("churn_14d_pct_good", 8), 8),
         (thresholds.get("churn_14d_pct_warning", 15), 5),
         (thresholds.get("churn_14d_pct_red", 25), 2)],
        0, higher_is_better=False,
    )
    dup = signals.get("duplication_ratio_pct")
    dup_pts = None if dup is None else _band(dup, [(5, 5), (10, 3), (15, 1)], 0, higher_is_better=False)
    refactor = signals.get("refactoring_ratio_pct")
    refactor_pts = None if refactor is None else _band(refactor, [(15.0001, 5), (8.0001, 3), (3.0001, 1)], 0)
    cc = signals.get("cc_compliance_rate")
    cc_pts = None if cc is None else _band(cc, [(80.0001, 3), (60.0001, 2), (40.0001, 1)], 0)
    return _dimension(
        {"churn_rate": churn_pts, "duplication_ratio": dup_pts,
         "refactoring_ratio": refactor_pts, "cc_compliance": cc_pts},
        D2_MAX, sum(D2_MAX.values()), role_config.get("d2_multiplier", 1.0),
    )


def score_d3(signals: dict, thresholds: dict) -> dict:
    """Score Dimension 3: Commit Craft (0-15 points)."""
    msg_pts = min(5, round(signals["mean_message_quality_score"]))
    scope_pts = _band(signals["mean_files_per_commit"], [(5.0001, 4), (10.0001, 3), (20.0001, 1)], 0,
                      higher_is_better=False)
    has_prs = signals.get("pr_count", 0) > 0
    pr_pts = _band(signals["small_pr_pct"], [(70.0001, 4), (50.0001, 3), (30.0001, 1)], 0) if has_prs else None
    self_merge = signals["self_merge_rate_pct"]
    merge_pts = (2 if self_merge == 0 else 1 if self_merge < 5 else 0) if has_prs else None
    return _dimension(
        {"commit_message_quality": msg_pts, "commit_scope_discipline": scope_pts,
         "pr_size_discipline": pr_pts, "merge_hygiene": merge_pts},
        D3_MAX, sum(D3_MAX.values()),
    )


def score_d4(signals: dict, thresholds: dict, role_config: dict) -> dict:
    """Score Dimension 4: Review & Collaboration (0-20 points).

    Review participation comes from review events (approvals, comments,
    requested changes). Merges are not reviews: without review-event data the
    sub-signal is unmeasured, and merges of others' MRs stay context only.
    """
    rate = signals.get("review_events_per_week")
    review_pts = None if rate is None else _band(
        rate,
        [(thresholds.get("review_rate_good_per_week", 2.0), 7),
         (thresholds.get("review_rate_ok_per_week", 1.0), 5),
         (thresholds.get("review_rate_low_per_week", 0.5), 3)],
        0,
    )
    repos = signals["distinct_repos_meaningful"]
    repo_pts = 4 if repos >= 3 else 2 if repos >= 2 else 1
    return _dimension(
        {"review_participation": review_pts, "review_responsiveness": None,
         "review_depth": None, "cross_repo_contribution": repo_pts},
        D4_MAX, sum(D4_MAX.values()), role_config.get("d4_multiplier", 1.0),
    )


def score_d5(signals: dict, thresholds: dict) -> dict:
    """Score Dimension 5: Test & Safety Practices (0-10 points)."""
    test_pts = _band(
        signals["test_signal_pct"],
        [(thresholds.get("test_ratio_good", 40) + 0.0001, 4),
         (thresholds.get("test_ratio_ok", 25) + 0.0001, 3),
         (thresholds.get("test_ratio_low", 15) + 0.0001, 1)],
        0,
    )
    feat_pts = _band(signals["feature_with_test_pct"], [(50.0001, 3), (30.0001, 2), (15.0001, 1)], 0)
    result = _dimension(
        {"test_to_code_ratio": test_pts, "test_presence_in_features": feat_pts,
         "security_file_awareness": None},
        D5_MAX, sum(D5_MAX.values()),
    )
    result["method"] = signals["method"]
    return result


def assign_tier(dimension_scores: dict, insufficient_data: bool) -> dict:
    """Assign quality tier from measured D2-D5 evidence only.

    Returns ``tier: None`` when the window is below the data minimum. Dimensions
    with no measured sub-signal are excluded (never counted as zero) and listed;
    without measured D2 evidence the tier cannot be A.
    """
    if insufficient_data:
        return {"tier": None, "label": "insufficient data", "score": None, "max": None,
                "pct": None, "unmeasured_dimensions": [],
                "reason": "below minimum commit sample; no tier assigned"}

    measured = {k: v for k, v in dimension_scores.items() if v["score"] is not None}
    unmeasured_dims = sorted(k for k, v in dimension_scores.items()
                             if k not in measured and v.get("status") != "context_only")
    total = sum(v["score"] for v in measured.values())
    max_achievable = sum(v["max_achievable"] for v in measured.values())
    if max_achievable == 0:
        return {"tier": None, "label": "insufficient evidence", "score": None, "max": None,
                "pct": None, "unmeasured_dimensions": unmeasured_dims,
                "reason": "no dimension has measured evidence"}

    pct = total / max_achievable * 100
    if pct >= 80:
        tier, label = "A", "Exemplary"
    elif pct >= 60:
        tier, label = "B", "Solid"
    elif pct >= 40:
        tier, label = "C", "Developing"
    else:
        tier, label = "D", "Concerning"

    # Overrides: a zero-scored measured dimension, missing D2 evidence, or D2
    # below 8/21 each block tier A.
    d2 = dimension_scores.get("d2", {})
    blocks_a = (
        any(v["score"] == 0 for v in measured.values())
        or d2.get("score") is None
        or (d2.get("status") == "measured" and d2["score"] < 8)
    )
    if tier == "A" and blocks_a:
        tier, label = "B", "Solid"

    return {
        "tier": tier,
        "label": label,
        "score": total,
        "max": max_achievable,
        "pct": round(pct, 1),
        "unmeasured_dimensions": unmeasured_dims,
        "reason": None,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def build_person_profile(person: str, commits: list[dict], mrs_authored: list[dict],
                         all_mrs: list[dict], alias_map: dict[str, str],
                         config: dict, window_start: date, window_end: date,
                         non_working: set[date]) -> dict:
    """Build complete contribution profile for one person."""
    thresholds = config.get("thresholds", DEFAULT_CONFIG["thresholds"])
    role_config = config.get("role_calibration", {}).get(person, {})
    total_weeks = max(1, (window_end - window_start).days / 7)

    # Check minimum data requirements.
    insufficient = False
    if len(commits) < thresholds.get("min_commits", 30):
        insufficient = True
    active_dates = set()
    for c in commits:
        d = parse_date(c.get("datetime", ""))
        if d:
            active_dates.add(d)

    # Compute signals.
    d1_signals = compute_d1_signals(commits, mrs_authored, window_start, window_end, non_working, role_config)
    d2_signals = compute_d2_signals(commits)
    d3_signals = compute_d3_signals(commits, mrs_authored, person, alias_map)
    d4_signals = compute_d4_signals(mrs_authored, person, all_mrs, alias_map, commits, total_weeks)
    d5_signals = compute_d5_signals(commits)

    dimension_scores = {
        "d1": score_d1(d1_signals, thresholds, role_config),
        "d2": score_d2(d2_signals, thresholds, role_config),
        "d3": score_d3(d3_signals, thresholds),
        "d4": score_d4(d4_signals, thresholds, role_config),
        "d5": score_d5(d5_signals, thresholds),
    }
    tier = assign_tier(dimension_scores, insufficient)

    volume_context = {
        "_note": "Volume / activity context only. Never scored as quality; never rank people on it.",
        "active_days": d1_signals["active_days"],
        "active_days_coverage_pct": d1_signals["active_days_coverage_pct"],
        "mr_per_week": d1_signals["mr_per_week"],
        "merges_of_others_mrs_per_week": d4_signals["merges_of_others_per_week"],
        "code_loc": d2_signals["code_loc"],
    }

    return {
        "person": person,
        "window": {"start": window_start.isoformat(), "end": window_end.isoformat()},
        "data_summary": {
            "total_commits": len(commits),
            "total_mrs_authored": len(mrs_authored),
            "active_days": len(active_dates),
            "repos": list(set(c.get("repo", "unknown") for c in commits)),
            "insufficient_data": insufficient,
        },
        "role": role_config.get("role", "ic"),
        "signals": {
            "d1_delivery_consistency": d1_signals,
            "d2_code_quality": d2_signals,
            "d3_commit_craft": d3_signals,
            "d4_review_collaboration": d4_signals,
            "d5_test_safety": d5_signals,
            "d6_ai_quality": {"available": False, "method": "no_attribution_data"},
        },
        "volume_context": volume_context,
        "scores": dimension_scores,
        "tier": tier,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract contribution quality profiles from git CSV data."
    )
    parser.add_argument("--config", type=Path, help="Path to config JSON file")
    parser.add_argument("--commits", type=Path, help="Path to raw-commits.csv (overrides config)")
    parser.add_argument("--mr", type=Path, help="Path to mr-acceptances.csv (overrides config)")
    parser.add_argument("--output", type=Path, help="Output path for profiles JSON (overrides config)")
    args = parser.parse_args()

    # Load config.
    config = dict(DEFAULT_CONFIG)
    config_dir = Path(".")
    if args.config:
        config_dir = args.config.parent
        with open(args.config) as f:
            user_config = json.load(f)
        config.update(user_config)

    # Resolve paths.
    def resolve(p: str) -> Path:
        path = Path(p)
        if path.is_absolute():
            return path
        return (config_dir / path).resolve()

    missing = [key for key, flag in (("input_commits", args.commits), ("input_mr", args.mr))
               if flag is None and not config.get(key)]
    if missing:
        print(
            f"ERROR: config is missing {', '.join(missing)}. The config needs input_commits "
            "and input_mr, or pass --commits/--mr.",
            file=sys.stderr,
        )
        sys.exit(2)

    commits_path = args.commits or resolve(config["input_commits"])
    mr_path = args.mr or resolve(config["input_mr"])
    output_path = args.output or resolve(config.get("output_profiles", "contribution-profiles.json"))

    # Load identity aliases.
    alias_map = load_identity_aliases(config, config_dir)

    # Read CSVs.
    print(f"Reading commits from {commits_path}")
    raw_commits = read_commits_csv(commits_path)
    print(f"  → {len(raw_commits)} commits loaded")

    print(f"Reading MR acceptances from {mr_path}")
    raw_mrs = read_mr_csv(mr_path)
    print(f"  → {len(raw_mrs)} MR acceptances loaded")

    # Resolve identities.
    for c in raw_commits:
        c["_person"] = resolve_person(c.get("author_email", ""), c.get("author_name", ""), alias_map)
    for m in raw_mrs:
        m["_merger_person"] = resolve_person(m.get("merger_email", ""), m.get("merger_name", ""), alias_map)

    # Determine analysis window.
    all_dates = [parse_date(c.get("datetime", "")) for c in raw_commits]
    all_dates = [d for d in all_dates if d]
    if not all_dates:
        print("No commits with valid dates found. Exiting.", file=sys.stderr)
        sys.exit(1)

    window_end = max(all_dates)
    window_days = config.get("analysis_window_days", 90)
    window_start = window_end - timedelta(days=window_days)
    print(f"Analysis window: {window_start} to {window_end} ({window_days} days)")

    # Filter to window.
    def in_window(row: dict) -> bool:
        d = parse_date(row.get("datetime", ""))
        return d is not None and window_start <= d <= window_end

    commits_in_window = [c for c in raw_commits if in_window(c)]
    mrs_in_window = [m for m in raw_mrs if in_window(m)]

    # Group by person.
    person_commits: dict[str, list[dict]] = defaultdict(list)
    for c in commits_in_window:
        person_commits[c["_person"]].append(c)

    # Identify which MRs each person authored.
    # Heuristic: match source_branch commits to person's commits in the same repo.
    # Simpler approach: MRs are attributed to the person whose commits appear on the branch.
    person_mrs_authored: dict[str, list[dict]] = defaultdict(list)
    for m in mrs_in_window:
        # Check which person has commits in this repo around this time.
        # Best CSV heuristic: the most frequent commit author in that repo close to the merge date.
        # Simplified: we mark MRs as authored if NOT merged by the person (i.e., someone else merged it).
        # This is imperfect but workable from CSV data alone.
        merger_person = m["_merger_person"]
        # For each person, count their commits in this repo.
        repo = m.get("repo", "unknown")
        # Actually, without branch-to-author mapping, we can't reliably attribute MRs to authors from CSV.
        # Best available: assign MR to the merger person as "their merge activity", and track separately.
        # For "authored MRs" we need the source_branch and cross-reference with commit data.
        pass

    # Fallback: assign MRs to all persons who have commits in that repo (weighted by commit count).
    # This is a known limitation documented in the README.
    repo_person_counts: dict[str, Counter] = defaultdict(Counter)
    for c in commits_in_window:
        repo_person_counts[c.get("repo", "unknown")][c["_person"]] += 1

    for m in mrs_in_window:
        repo = m.get("repo", "unknown")
        merger = m["_merger_person"]
        # Assign to the top committer in that repo who is NOT the merger (they authored it, someone else merged).
        candidates = [
            (person, count) for person, count in repo_person_counts.get(repo, {}).items()
            if person.lower() != merger.lower()
        ]
        if candidates:
            # Assign to the most active committer in that repo.
            top = max(candidates, key=lambda x: x[1])
            person_mrs_authored[top[0]].append(m)
        else:
            # Self-authored and self-merged, or sole committer.
            person_mrs_authored[merger].append(m)

    non_working = build_non_working_dates(config.get("non_working_date_ranges", []))

    # Filter to target persons if configured.
    target_persons = config.get("target_persons", [])
    if target_persons:
        persons = [p for p in person_commits if p in target_persons]
    else:
        persons = list(person_commits.keys())

    print(f"Analyzing {len(persons)} persons")

    # Build profiles.
    profiles = []
    for person in sorted(persons):
        commits = person_commits[person]
        mrs_authored = person_mrs_authored.get(person, [])
        profile = build_person_profile(
            person, commits, mrs_authored, mrs_in_window,
            alias_map, config, window_start, window_end, non_working,
        )
        profiles.append(profile)
        tier = profile["tier"]
        if tier["tier"] is None:
            print(f"  {person}: no tier ({tier['label']})")
        else:
            gaps = ", ".join(tier["unmeasured_dimensions"]) or "none"
            print(f"  {person}: {tier['tier']} ({tier['score']}/{tier['max']} = {tier['pct']}%; "
                  f"unmeasured dimensions: {gaps})")

    # Team summary.
    scored_profiles = [p for p in profiles if p["tier"]["tier"] is not None]
    team_summary = {}
    if scored_profiles:
        tier_dist = Counter(p["tier"]["tier"] for p in scored_profiles)
        dim_medians = {}
        for dim in ["d1", "d2", "d3", "d4", "d5"]:
            scores = [p["scores"][dim]["score"] for p in scored_profiles
                      if p["scores"][dim]["score"] is not None]
            dim_medians[dim] = round(statistics.median(scores), 1) if scores else None

        team_summary = {
            "total_persons": len(profiles),
            "scored_persons": len(scored_profiles),
            "insufficient_data_persons": len(profiles) - len(scored_profiles),
            "tier_distribution": dict(tier_dist),
            "dimension_medians": dim_medians,
            "mean_overall_pct": round(
                statistics.mean(p["tier"]["pct"] for p in scored_profiles), 1
            ),
        }

    output = {
        "generated_at": datetime.now().isoformat(),
        "window": {"start": window_start.isoformat(), "end": window_end.isoformat()},
        "data_tier": "tier1_csv_only",
        "team_summary": team_summary,
        "profiles": profiles,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nProfiles written to {output_path}")


if __name__ == "__main__":
    main()
