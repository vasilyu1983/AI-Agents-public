#!/usr/bin/env python3
"""Generate contribution quality reports from profiles and optional sample data.

Reads contribution-profiles.json and optional sample-quality.json, then produces
markdown reports in person or team mode.

Usage:
    python generate-quality-report.py --config config/report-config.json --mode person
    python generate-quality-report.py --profiles profiles.json --output report.md --mode team
"""

import argparse
import json
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Report generation: Person mode
# ---------------------------------------------------------------------------

def generate_person_report(profiles: list[dict], samples: dict | None,
                           output_path: Path) -> None:
    """Generate individual quality reports for each person."""
    lines = []
    lines.append("# Contribution Quality Report\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    if profiles:
        window = profiles[0].get("window", {})
        lines.append(f"Analysis window: {window.get('start', '?')} to {window.get('end', '?')}\n")
        data_tier = profiles[0].get("data_tier", "unknown")
        if data_tier == "tier1_csv_only":
            lines.append("> **Note**: This report uses CSV-only (Tier 1) data. Churn, duplication, "
                         "refactoring ratio, CC-\\* compliance and review events are unmeasured "
                         "(unknown, not zero). Scores cover measured sub-signals only.\n")

    for profile in profiles:
        person = profile["person"]
        tier = profile["tier"]
        data = profile["data_summary"]
        scores = profile["scores"]

        lines.append(f"\n---\n\n## {person}\n")

        if data["insufficient_data"]:
            lines.append(f"**Insufficient data** — {data['total_commits']} commits. "
                         "Minimum sample: 30 commits; active days are context only.\n")
            continue

        # At a glance.
        if tier.get("tier") is None:
            lines.append(f"**No tier** — {tier.get('label')}: {tier.get('reason')}\n")
            continue
        lines.append(f"**Tier {tier['tier']}** — {tier['label']} "
                      f"({tier['score']}/{tier['max']} = {tier['pct']}% of measured evidence)\n")
        if tier.get("unmeasured_dimensions"):
            lines.append(f"Unmeasured dimensions (insufficient evidence, excluded): "
                          f"{', '.join(tier['unmeasured_dimensions'])}\n")
        lines.append(f"Role: {profile.get('role', 'ic')} | "
                      f"Commits: {data['total_commits']} | "
                      f"MRs authored: {data['total_mrs_authored']} | "
                      f"Active days: {data['active_days']} | "
                      f"Repos: {', '.join(data['repos'][:5])}\n")

        # Dimension table.
        lines.append("\n| Dimension | Score | Max | Key Signal |")
        lines.append("|-----------|-------|-----|------------|")
        dim_labels = {
            "d1": "D1 Delivery cadence",
            "d2": "D2 Code Quality",
            "d3": "D3 Commit Craft",
            "d4": "D4 Review & Collaboration",
            "d5": "D5 Test & Safety",
        }
        for dim_key, dim_label in dim_labels.items():
            s = scores.get(dim_key, {})
            score = s.get("score")
            mx = s.get("max_achievable", s.get("max", 0))
            measured = {k: v for k, v in s.get("breakdown", {}).items() if v is not None}
            if s.get("status") == "context_only":
                lines.append(f"| {dim_label} | context only | — | — |")
                continue
            if score is None or not measured:
                lines.append(f"| {dim_label} | insufficient evidence | — | — |")
                continue
            top_signal = max(measured.items(), key=lambda x: x[1])
            lines.append(f"| {dim_label} | {score} | {mx} | {top_signal[0]}: {top_signal[1]}pts |")

        lines.append("")

        # Detailed dimension breakdowns.
        signals = profile.get("signals", {})

        # D1.
        d1 = signals.get("d1_delivery_consistency", {})
        lines.append("### D1: Delivery cadence (context only; not in tier)\n")
        lines.append(f"- Weekly commits: mean {d1.get('mean_weekly_commits', 0)}, "
                      f"CV {d1.get('commit_frequency_cv', 0)}")
        lines.append(f"- Volume context (not scored): active days {d1.get('active_days', 0)}/"
                      f"{d1.get('expected_working_days', 0)}, MR throughput {d1.get('mr_per_week', 0)}/week")
        lines.append(f"- Within-window commit-count ratio: {d1.get('delivery_trend_ratio', 1.0)} "
                      "(second half / first half; not a quality trend)\n")

        # D2.
        d2 = signals.get("d2_code_quality", {})
        lines.append(f"### D2: Code Quality ({_dim_cell(scores['d2'])})\n")
        churn = d2.get("churn_14d_pct")
        lines.append(f"- Churn (14-day): {'unknown' if churn is None else f'{churn}%'} "
                      f"({d2.get('churn_method', 'unknown')})")
        refactor = d2.get("refactoring_ratio_pct")
        lines.append(f"- Refactoring ratio: {'unknown' if refactor is None else f'{refactor}%'} "
                      f"({d2.get('refactoring_method', 'unknown')})")
        lines.append(f"- Net lines: +{d2.get('total_insertions', 0)}/-{d2.get('total_deletions', 0)} "
                      f"= {d2.get('net_lines', 0)} net")
        if d2.get("duplication_ratio_pct") is None:
            lines.append("- Duplication: unavailable (requires repo checkout)")
        if d2.get("complexity_delta") is None:
            lines.append("- Complexity delta: unavailable (requires repo checkout)")
        lines.append("")

        # D3.
        d3 = signals.get("d3_commit_craft", {})
        lines.append(f"### D3: Commit Craft ({_dim_cell(scores['d3'])})\n")
        lines.append(f"- Message quality: {d3.get('mean_message_quality_score', 0)}/5 "
                      f"({d3.get('generic_message_pct', 0)}% generic)")
        lines.append(f"- Scope: mean {d3.get('mean_files_per_commit', 0)} files/commit, "
                      f"median {d3.get('median_files_per_commit', 0)}")
        lines.append(f"- PR size: P50={d3.get('pr_size_p50', 0)} LOC, P90={d3.get('pr_size_p90', 0)} LOC "
                      f"({d3.get('small_pr_pct', 0)}% under 250 LOC)")
        lines.append(f"- Self-merge: {d3.get('self_merge_count', 0)} "
                      f"({d3.get('self_merge_rate_pct', 0)}%, 95% CI {d3.get('self_merge_rate_ci95')})\n")

        # D4.
        d4 = signals.get("d4_review_collaboration", {})
        lines.append(f"### D4: Review & Collaboration ({_dim_cell(scores['d4'])})\n")
        if d4.get("review_events_per_week") is None:
            lines.append("- Review participation: unavailable (requires forge review events; "
                          "merges are not reviews)")
        lines.append(f"- Context only: merged others' MRs {d4.get('merges_of_others', 0)} "
                      f"({d4.get('merges_of_others_per_week', 0)}/week)")
        lines.append(f"- Cross-repo: {d4.get('distinct_repos_meaningful', 0)} meaningful repos "
                      f"({d4.get('primary_repo_concentration_pct', 100)}% in primary)")
        if d4.get("review_responsiveness_hours") is None:
            lines.append("- Review responsiveness: unavailable (requires API data)")
        if d4.get("review_depth_avg_comments") is None:
            lines.append("- Review depth: unavailable (requires API data)")
        lines.append("")

        # D5.
        d5 = signals.get("d5_test_safety", {})
        lines.append(f"### D5: Test & Safety ({_dim_cell(scores['d5'])})\n")
        lines.append(f"- Commits with test signal: {d5.get('commits_with_test_signal', 0)} "
                      f"({d5.get('test_signal_pct', 0)}%)")
        lines.append(f"- Feature commits with tests: {d5.get('feature_with_test_pct', 0)}%")
        lines.append(f"- Method: {d5.get('method', 'unknown')}\n")

        # Code quality samples (if available).
        person_samples = (samples or {}).get(person, [])
        if person_samples:
            lines.append(f"### Sampled Commits ({len(person_samples)} samples)\n")
            for s in person_samples:
                finding_count = len(s.get("findings", []))
                cc_delta = s.get("complexity_after", 0) - s.get("complexity_before", 0)
                test_icon = "+" if s.get("has_test_files") else "-"
                lines.append(f"- `{s['commit_hash']}` {s['date']} — {s['subject'][:60]}")
                lines.append(f"  {s.get('files_changed', 0)} files, "
                              f"+{s.get('insertions', 0)}/-{s.get('deletions', 0)} | "
                              f"msg:{s.get('message_quality_score', 0)}/5 | "
                              f"findings:{finding_count} | "
                              f"cc_delta:{cc_delta:+d} | tests:{test_icon}")
                for f in s.get("findings", []):
                    lines.append(f"  - **{f['priority']} {f['rule_id']}**: {f['description']}")
            lines.append("")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Person report written to {output_path}")


# ---------------------------------------------------------------------------
# Report generation: Team mode
# ---------------------------------------------------------------------------

def _dim_cell(dim: dict) -> str:
    """Render a dimension score over its measured maximum; unknown stays 'n/a'."""
    if dim.get("status") == "context_only":
        return "context"
    if dim.get("score") is None:
        return "n/a"
    return f"{dim['score']}/{dim.get('max_achievable', dim.get('max'))}"


def generate_team_report(profiles: list[dict], output_path: Path) -> None:
    """Generate team calibration report."""
    lines = []
    lines.append("# Team Contribution Quality Calibration\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    if profiles:
        window = profiles[0].get("window", {})
        lines.append(f"Analysis window: {window.get('start', '?')} to {window.get('end', '?')}\n")

    scored = [p for p in profiles if p["tier"].get("tier") is not None]
    insufficient = [p for p in profiles if p["tier"].get("tier") is None]

    # Team summary.
    lines.append(f"## Team Summary\n")
    lines.append(f"- Analyzed: {len(profiles)} persons ({len(scored)} scored, "
                  f"{len(insufficient)} insufficient data)\n")

    if scored:
        tier_dist = Counter(p["tier"]["tier"] for p in scored)
        lines.append(f"- Tier distribution: " + ", ".join(
            f"{t}: {c}" for t, c in sorted(tier_dist.items())
        ))
        mean_pct = statistics.mean(p["tier"]["pct"] for p in scored)
        lines.append(f"- Mean quality score: {mean_pct:.1f}%\n")

    # Comparison table.
    if scored:
        lines.append("## Comparison Matrix\n")
        lines.append("| Person | Tier | Score | D1 (context) | D2 | D3 | D4 | D5 |")
        lines.append("|--------|------|-------|----|----|----|----|----|")
        # Alphabetical on purpose: this matrix is calibration input, not a ranking.
        for p in sorted(scored, key=lambda x: x["person"]):
            s = p["scores"]
            lines.append(
                f"| {p['person']} "
                f"| {p['tier']['tier']} "
                f"| {p['tier']['pct']}% "
                + "".join(f"| {_dim_cell(s[k])} " for k in ("d1", "d2", "d3", "d4", "d5"))
                + "|"
            )
        lines.append("")

        # Dimension medians.
        lines.append("## Dimension Medians (Team Baseline)\n")
        lines.append("| Dimension | Median | Max | Team % |")
        lines.append("|-----------|--------|-----|--------|")
        dim_labels = {
            "d2": "D2 Code Quality",
            "d3": "D3 Commit Craft",
            "d4": "D4 Review & Collaboration",
            "d5": "D5 Test & Safety",
        }
        for dim_key, label in dim_labels.items():
            dims = [p["scores"][dim_key] for p in scored if p["scores"][dim_key].get("score") is not None]
            if not dims:
                lines.append(f"| {label} | insufficient evidence | — | — |")
                continue
            med = statistics.median(d["score"] for d in dims)
            max_pts = statistics.median(d.get("max_achievable", d.get("max", 0)) for d in dims)
            pct = round(med / max_pts * 100, 1) if max_pts > 0 else 0
            lines.append(f"| {label} | {med:.1f} | {max_pts:g} | {pct}% |")
        lines.append("")

        # No outlier flags: dimension scores carry no uncertainty interval, and
        # person-level rates on < ~30 changes are too wide to separate people.
        lines.append("## Reading the Spread\n")
        lines.append("- This matrix is calibration input, not a ranking. Do not call two people "
                      "different, or label anyone an outlier, unless their rate intervals "
                      "(e.g. `self_merge_rate_ci95`) separate; otherwise report "
                      "\"no detectable difference\".")
        lines.append("- Volume context (active days, MR throughput, LOC) is never a quality signal.\n")

    # Insufficient data.
    if insufficient:
        lines.append("## Insufficient Data\n")
        for p in insufficient:
            d = p["data_summary"]
            lines.append(f"- **{p['person']}**: {d['total_commits']} commits, "
                          f"{d['active_days']} active days")
        lines.append("")

    lines.append("---\n")
    lines.append("## Method and Limitations\n")
    lines.append("- Scoring model: D2-D5 scored; D1 and D6 context-only")
    lines.append("- Data tier: Tier 1 (CSV-only) unless repo checkouts provided")
    lines.append("- CC-\\* rules from software-clean-code-standard used for quality rubric")
    lines.append("- Self-merge detection based on identity alias resolution (may have false positives)")
    lines.append("- MR authorship attribution is approximate when only merger data is available")
    lines.append("- Review participation, depth and responsiveness require forge review events "
                  "(GitLab/GitHub API); merges are not counted as reviews")
    lines.append("- Unmeasured sub-signals are unknown, not zero, and are excluded from scores")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Team report written to {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate contribution quality reports."
    )
    parser.add_argument("--config", type=Path, help="Path to config JSON file")
    parser.add_argument("--profiles", type=Path, help="Path to contribution-profiles.json")
    parser.add_argument("--samples", type=Path, help="Path to sample-quality.json (optional)")
    parser.add_argument("--output", type=Path, help="Output markdown path")
    parser.add_argument("--mode", choices=["person", "team"], default="person",
                        help="Report mode (default: person)")
    args = parser.parse_args()

    # Load config.
    config = {}
    config_dir = Path(".")
    if args.config:
        config_dir = args.config.parent
        with open(args.config) as f:
            config = json.load(f)

    report_options = config.get("report_options", {})
    mode = args.mode or report_options.get("mode", "person")

    # Resolve paths.
    def resolve(p: str) -> Path:
        path = Path(p)
        if path.is_absolute():
            return path
        return (config_dir / path).resolve()

    profiles_path = args.profiles or resolve(config.get("output_profiles", "../derived/contribution-profiles.json"))
    output_path = args.output or resolve(config.get("output_report", "../reports/quality-report.md"))

    # Load profiles.
    with open(profiles_path) as f:
        profiles_data = json.load(f)
    profiles = profiles_data.get("profiles", [])
    print(f"Loaded {len(profiles)} profiles from {profiles_path}")

    # Load samples (optional).
    samples = None
    samples_path = args.samples
    if not samples_path:
        default_samples = resolve("../derived/sample-quality.json")
        if default_samples.exists():
            samples_path = default_samples

    if samples_path and samples_path.exists():
        with open(samples_path) as f:
            samples_data = json.load(f)
        samples = samples_data.get("persons", {})
        print(f"Loaded samples for {len(samples)} persons")

    # Generate report.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "person":
        generate_person_report(profiles, samples, output_path)
    elif mode == "team":
        generate_team_report(profiles, output_path)

    # Also output machine-readable JSON.
    json_output = output_path.with_suffix(".json")
    json_data = {
        "generated_at": datetime.now().isoformat(),
        "mode": mode,
        "profiles_count": len(profiles),
        "profiles": profiles,
    }
    with open(json_output, "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"JSON scores written to {json_output}")


if __name__ == "__main__":
    main()
