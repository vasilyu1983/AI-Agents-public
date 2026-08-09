#!/usr/bin/env python3
"""Extract contribution quality profiles from raw-commits.csv and mr-acceptances.csv.

Reads the same CSV format produced by the project-scoped counterpart skill extraction
scripts. Computes Tier 1 signals per person and outputs contribution-profiles.json.

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
        "min_active_days": 20,
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


def compute_d2_signals(commits: list[dict]) -> dict:
    """Compute Dimension 2: Code Quality Signals (Tier 1 only).

    Revert pairs (``net_cancel=True``) are excluded from insertion/deletion
    totals and from the churn proxy — their churn is a data-quality artefact,
    not a quality signal.
    """
    scored = [c for c in commits if not c.get("net_cancel")]
    revert_pair_commits = len(commits) - len(scored)
    total_insertions = sum(c["insertions"] for c in scored)
    total_deletions = sum(c["deletions"] for c in scored)

    # Approximate churn: commits touching the same repo within 14 days.
    # Group commits by repo, sort by date, find overlapping changes.
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for c in scored:
        by_repo[c.get("repo", "unknown")].append(c)

    churn_insertions = 0
    churn_window_days = 14
    for repo, repo_commits in by_repo.items():
        sorted_commits = sorted(repo_commits, key=lambda x: x.get("datetime", ""))
        for i, c1 in enumerate(sorted_commits):
            d1 = parse_date(c1.get("datetime", ""))
            if not d1:
                continue
            for j in range(i + 1, len(sorted_commits)):
                c2 = sorted_commits[j]
                d2 = parse_date(c2.get("datetime", ""))
                if not d2:
                    continue
                delta = (d2 - d1).days
                if delta > churn_window_days:
                    break
                if delta > 0 and c2["deletions"] > 0:
                    churn_insertions += min(c2["deletions"], c1["insertions"])

    churn_rate = (churn_insertions / total_insertions * 100) if total_insertions > 0 else 0

    # Refactoring ratio: proxy from commit subjects (exclude cancelled pairs).
    refactor_commits = sum(
        1 for c in scored
        if any(kw in c.get("subject", "").lower() for kw in REFACTOR_KEYWORDS)
    )
    refactor_ratio = (refactor_commits / len(scored) * 100) if scored else 0

    # Duplication proxy: not reliably detectable from CSV alone.
    # Mark as unavailable; Tier 2 (repo checkout) needed for accuracy.

    return {
        "total_insertions": total_insertions,
        "total_deletions": total_deletions,
        "net_lines": total_insertions - total_deletions,
        "churn_loc": total_insertions + total_deletions,
        "del_ratio": round(total_deletions / (total_insertions + total_deletions), 3)
            if (total_insertions + total_deletions) > 0 else 0,
        "revert_pair_commits_excluded": revert_pair_commits,
        "churn_14d_approximate_pct": round(churn_rate, 1),
        "churn_method": "csv_same_repo_14d_approximation_post_revert_pairing",
        "refactoring_ratio_pct": round(refactor_ratio, 1),
        "refactoring_method": "subject_keyword_proxy",
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
    }


def compute_d4_signals(mrs: list[dict], person: str,
                       all_mrs: list[dict], alias_map: dict[str, str],
                       commits: list[dict], total_weeks: float) -> dict:
    """Compute Dimension 4: Review & Collaboration signals."""
    person_lower = person.lower()

    # Review participation: MRs where this person is the merger but NOT the author.
    # We approximate "author" by checking if the source_branch commits were by this person.
    # Simpler heuristic: merger is this person AND the MR subject doesn't contain their work.
    # Best available from CSV: count MRs in all_mrs where merger = this person.
    reviews_given = 0
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
            reviews_given += 1

    review_rate_per_week = reviews_given / total_weeks if total_weeks > 0 else 0

    # Cross-repo contribution.
    repos = Counter(c.get("repo", "unknown") for c in commits)
    meaningful_repos = sum(1 for count in repos.values() if count >= 5)
    primary_repo_pct = (max(repos.values()) / len(commits) * 100) if commits and repos else 100

    return {
        "reviews_given": reviews_given,
        "review_rate_per_week": round(review_rate_per_week, 2),
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

def score_d1(signals: dict, thresholds: dict, role_config: dict) -> dict:
    """Score Dimension 1: Delivery Consistency (0-20 points)."""
    cv = signals["commit_frequency_cv"]
    d1_mult = role_config.get("d1_multiplier", 1.0)

    if cv < 0.5:
        freq_pts = 7
    elif cv < 0.8:
        freq_pts = 5
    elif cv < 1.2:
        freq_pts = 3
    else:
        freq_pts = 0

    cov = signals["active_days_coverage_pct"]
    if cov > 70:
        active_pts = 5
    elif cov > 50:
        active_pts = 3
    elif cov > 30:
        active_pts = 1
    else:
        active_pts = 0

    mr_ratio = signals["mr_per_week"] / signals["mr_baseline_per_week"] if signals["mr_baseline_per_week"] > 0 else 0
    if mr_ratio >= 1.0:
        mr_pts = 5
    elif mr_ratio >= 0.7:
        mr_pts = 3
    elif mr_ratio >= 0.4:
        mr_pts = 1
    else:
        mr_pts = 0

    trend = signals["delivery_trend_ratio"]
    if trend >= 0.85:
        trend_pts = 3
    elif trend >= 0.6:
        trend_pts = 1
    else:
        trend_pts = 0

    raw = freq_pts + active_pts + mr_pts + trend_pts
    adjusted = min(20, round(raw * d1_mult))

    return {
        "score": adjusted,
        "max": 20,
        "breakdown": {
            "commit_frequency_stability": freq_pts,
            "active_days_coverage": active_pts,
            "mr_throughput": mr_pts,
            "delivery_trend": trend_pts,
        },
        "role_multiplier": d1_mult,
    }


def score_d2(signals: dict, thresholds: dict, role_config: dict) -> dict:
    """Score Dimension 2: Code Quality Signals (0-25 points)."""
    d2_mult = role_config.get("d2_multiplier", 1.0)
    churn = signals["churn_14d_approximate_pct"]

    if churn < thresholds.get("churn_14d_pct_good", 8):
        churn_pts = 8
    elif churn < thresholds.get("churn_14d_pct_warning", 15):
        churn_pts = 5
    elif churn < thresholds.get("churn_14d_pct_red", 25):
        churn_pts = 2
    else:
        churn_pts = 0

    # Duplication: unavailable from CSV, give partial credit.
    dup_pts = 3  # Neutral (middle) when unavailable.

    refactor = signals["refactoring_ratio_pct"]
    if refactor > 15:
        refactor_pts = 5
    elif refactor > 8:
        refactor_pts = 3
    elif refactor > 3:
        refactor_pts = 1
    else:
        refactor_pts = 0

    # Complexity delta and CC-* compliance: unavailable from CSV.
    complexity_pts = 0  # Tier 2 only.
    cc_pts = 0  # Tier 2 only.
    tier2_available = signals.get("complexity_delta") is not None

    raw = churn_pts + dup_pts + refactor_pts + complexity_pts + cc_pts
    adjusted = min(25, round(raw * d2_mult))

    return {
        "score": adjusted,
        "max": 25,
        "max_achievable_csv_only": 16,
        "breakdown": {
            "churn_rate": churn_pts,
            "duplication_ratio": dup_pts,
            "refactoring_ratio": refactor_pts,
            "complexity_delta": complexity_pts,
            "cc_compliance": cc_pts,
        },
        "tier2_available": tier2_available,
        "role_multiplier": d2_mult,
    }


def score_d3(signals: dict, thresholds: dict) -> dict:
    """Score Dimension 3: Commit Craft (0-15 points)."""
    msg = signals["mean_message_quality_score"]
    msg_pts = min(5, round(msg))

    mean_files = signals["mean_files_per_commit"]
    if mean_files <= 5:
        scope_pts = 4
    elif mean_files <= 10:
        scope_pts = 3
    elif mean_files <= 20:
        scope_pts = 1
    else:
        scope_pts = 0

    small_pct = signals["small_pr_pct"]
    if small_pct > 70:
        pr_pts = 4
    elif small_pct > 50:
        pr_pts = 3
    elif small_pct > 30:
        pr_pts = 1
    else:
        pr_pts = 0

    self_merge = signals["self_merge_rate_pct"]
    if self_merge == 0:
        merge_pts = 2
    elif self_merge < 5:
        merge_pts = 1
    else:
        merge_pts = 0

    return {
        "score": msg_pts + scope_pts + pr_pts + merge_pts,
        "max": 15,
        "breakdown": {
            "commit_message_quality": msg_pts,
            "commit_scope_discipline": scope_pts,
            "pr_size_discipline": pr_pts,
            "merge_hygiene": merge_pts,
        },
    }


def score_d4(signals: dict, thresholds: dict, role_config: dict) -> dict:
    """Score Dimension 4: Review & Collaboration (0-20 points)."""
    d4_mult = role_config.get("d4_multiplier", 1.0)
    rate = signals["review_rate_per_week"]

    good = thresholds.get("review_rate_good_per_week", 2.0)
    ok = thresholds.get("review_rate_ok_per_week", 1.0)
    low = thresholds.get("review_rate_low_per_week", 0.5)

    if rate >= good:
        review_pts = 7
    elif rate >= ok:
        review_pts = 5
    elif rate >= low:
        review_pts = 3
    else:
        review_pts = 0

    # Responsiveness and depth: unavailable from CSV.
    responsiveness_pts = 0
    depth_pts = 0

    repos = signals["distinct_repos_meaningful"]
    if repos >= 3:
        repo_pts = 4
    elif repos >= 2:
        repo_pts = 2
    else:
        repo_pts = 1

    raw = review_pts + responsiveness_pts + depth_pts + repo_pts
    adjusted = min(20, round(raw * d4_mult))

    return {
        "score": adjusted,
        "max": 20,
        "max_achievable_csv_only": 11,
        "breakdown": {
            "review_participation_rate": review_pts,
            "review_responsiveness": responsiveness_pts,
            "review_depth": depth_pts,
            "cross_repo_contribution": repo_pts,
        },
        "api_data_available": signals.get("review_responsiveness_hours") is not None,
        "role_multiplier": d4_mult,
    }


def score_d5(signals: dict, thresholds: dict) -> dict:
    """Score Dimension 5: Test & Safety Practices (0-10 points)."""
    test_pct = signals["test_signal_pct"]
    good = thresholds.get("test_ratio_good", 40)
    ok = thresholds.get("test_ratio_ok", 25)
    low = thresholds.get("test_ratio_low", 15)

    if test_pct > good:
        test_pts = 4
    elif test_pct > ok:
        test_pts = 3
    elif test_pct > low:
        test_pts = 1
    else:
        test_pts = 0

    feat_test = signals["feature_with_test_pct"]
    if feat_test > 50:
        feat_pts = 3
    elif feat_test > 30:
        feat_pts = 2
    elif feat_test > 15:
        feat_pts = 1
    else:
        feat_pts = 0

    # Security awareness: unavailable from subject-only analysis.
    security_pts = 0

    return {
        "score": test_pts + feat_pts + security_pts,
        "max": 10,
        "max_achievable_csv_only": 7,
        "breakdown": {
            "test_to_code_ratio": test_pts,
            "test_presence_in_features": feat_pts,
            "security_file_awareness": security_pts,
        },
        "method": signals["method"],
    }


def assign_tier(total_d1_d5: int, max_d1_d5: int, dimension_scores: dict) -> dict:
    """Assign quality tier based on D1-D5 total score."""
    # Proportional thresholds when max < 90 (due to missing Tier 2 data).
    ratio = total_d1_d5 / max_d1_d5 if max_d1_d5 > 0 else 0
    pct = ratio * 100

    if pct >= 80:
        tier = "A"
        label = "Exemplary"
    elif pct >= 60:
        tier = "B"
        label = "Solid"
    elif pct >= 40:
        tier = "C"
        label = "Developing"
    else:
        tier = "D"
        label = "Concerning"

    # Override: if any dimension scores 0, cannot be A.
    for dim, score_data in dimension_scores.items():
        if dim == "d6":
            continue
        if score_data["score"] == 0 and tier == "A":
            tier = "B"
            label = "Solid"
            break

    # Override: if D2 < 8/25, cannot be A.
    if dimension_scores.get("d2", {}).get("score", 0) < 8 and tier == "A":
        tier = "B"
        label = "Solid"

    return {
        "tier": tier,
        "label": label,
        "score": total_d1_d5,
        "max": max_d1_d5,
        "pct": round(pct, 1),
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
    if len(active_dates) < thresholds.get("min_active_days", 20):
        insufficient = True

    # Compute signals.
    d1_signals = compute_d1_signals(commits, mrs_authored, window_start, window_end, non_working, role_config)
    d2_signals = compute_d2_signals(commits)
    d3_signals = compute_d3_signals(commits, mrs_authored, person, alias_map)
    d4_signals = compute_d4_signals(mrs_authored, person, all_mrs, alias_map, commits, total_weeks)
    d5_signals = compute_d5_signals(commits)

    # Score dimensions.
    d1_score = score_d1(d1_signals, thresholds, role_config)
    d2_score = score_d2(d2_signals, thresholds, role_config)
    d3_score = score_d3(d3_signals, thresholds)
    d4_score = score_d4(d4_signals, thresholds, role_config)
    d5_score = score_d5(d5_signals, thresholds)

    dimension_scores = {
        "d1": d1_score,
        "d2": d2_score,
        "d3": d3_score,
        "d4": d4_score,
        "d5": d5_score,
    }

    total = sum(s["score"] for s in dimension_scores.values())
    max_total = sum(s["max"] for s in dimension_scores.values())
    # Use max_achievable (CSV-only) when Tier 2 is not available.
    max_achievable = sum(
        s.get("max_achievable_csv_only", s["max"]) for s in dimension_scores.values()
    )

    tier = assign_tier(total, max_achievable, dimension_scores)

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
        status = "⚠ insufficient data" if profile["data_summary"]["insufficient_data"] else ""
        print(f"  {person}: {tier['tier']} ({tier['score']}/{tier['max']} = {tier['pct']}%) {status}")

    # Team summary.
    scored_profiles = [p for p in profiles if not p["data_summary"]["insufficient_data"]]
    team_summary = {}
    if scored_profiles:
        tier_dist = Counter(p["tier"]["tier"] for p in scored_profiles)
        dim_medians = {}
        for dim in ["d1", "d2", "d3", "d4", "d5"]:
            scores = [p["scores"][dim]["score"] for p in scored_profiles]
            dim_medians[dim] = round(statistics.median(scores), 1) if scores else 0

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
