#!/usr/bin/env python3
"""dep_auditor.py — Dependency health scorer and security auditor.

Stdlib-only. No external dependencies. Runs with Python 3.9+.

Subcommands:
  health  -- Score dependency health across 5 dimensions with weighted tiers.
  audit   -- Simulate security audit: vulnerabilities, unmaintained, outdated.
  report  -- Full Markdown dependency health report.
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Health dimension weights (must sum to 1.0)
DIMENSION_WEIGHTS: dict[str, float] = {
    "lockfile_present":         0.25,
    "package_manager_pinned":   0.20,
    "update_policy_defined":    0.15,
    "security_scanning_active": 0.20,
    "sbom_generation_active":   0.20,
}

HEALTH_TIERS: list[tuple[int, str]] = [
    (80, "HEALTHY"),
    (60, "ADEQUATE"),
    (40, "NEEDS_WORK"),
    (0,  "CRITICAL"),
]

OUTDATED_DAYS = 180  # threshold for "outdated"

SEVERITIES = ("critical", "high", "medium", "low", "none")
SEVERITY_ORDER = {s: i for i, s in enumerate(SEVERITIES)}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        sys.exit(f"Error: file not found: {path}")
    try:
        with p.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: invalid JSON in {path}: {exc}")


def _today() -> date:
    return date.today()


def _health_tier(score: float) -> str:
    for threshold, label in HEALTH_TIERS:
        if score >= threshold:
            return label
    return "CRITICAL"


def _score_lockfile(eco: dict) -> dict[str, object]:
    """25% weight — lockfile present and used in CI."""
    present = bool(eco.get("lockfile_present", False))
    frozen_ci = bool(eco.get("frozen_install_in_ci", False))
    # sub-checks
    sub = {
        "lockfile_file_exists": present,
        "frozen_install_in_ci": frozen_ci,
    }
    # full credit if both; half credit if only lockfile present
    if present and frozen_ci:
        raw = 100.0
    elif present:
        raw = 60.0
    else:
        raw = 0.0
    return {"score": raw, "sub_checks": sub}


def _score_pm_pinned(eco: dict) -> dict[str, object]:
    """20% weight — package manager version pinned."""
    pinned = bool(eco.get("package_manager_pinned", False))
    pm_version = bool(eco.get("package_manager_version", ""))
    sub = {
        "packageManager_field_set": pinned,
        "pm_version_specified": pm_version,
    }
    if pinned and pm_version:
        raw = 100.0
    elif pm_version:
        raw = 50.0
    else:
        raw = 0.0
    return {"score": raw, "sub_checks": sub}


def _score_update_policy(eco: dict) -> dict[str, object]:
    """15% weight — update policy defined with cadence and tooling."""
    policy = eco.get("update_policy", {})
    has_patch = bool(policy.get("patch"))
    has_minor = bool(policy.get("minor"))
    has_major = bool(policy.get("major"))
    has_tool = bool(policy.get("automation_tool"))
    sub = {
        "patch_cadence_defined": has_patch,
        "minor_cadence_defined": has_minor,
        "major_cadence_defined": has_major,
        "automation_tool_configured": has_tool,
    }
    defined_count = sum([has_patch, has_minor, has_major, has_tool])
    raw = (defined_count / 4) * 100.0
    return {"score": raw, "sub_checks": sub}


def _score_security_scanning(eco: dict) -> dict[str, object]:
    """20% weight — security scanning active with recent run."""
    scanning = eco.get("security_scanning", {})
    active = bool(scanning.get("active", False))
    runs_in_ci = bool(scanning.get("runs_in_ci", False))
    # Check recency: last run within 30 days
    last_run_str = scanning.get("last_run_date", "")
    recent = False
    if last_run_str:
        try:
            last_run = datetime.strptime(last_run_str, "%Y-%m-%d").date()
            recent = (_today() - last_run).days <= 30
        except ValueError:
            recent = False
    sub = {
        "scanning_active": active,
        "runs_in_ci": runs_in_ci,
        "last_run_within_30_days": recent,
    }
    if active and runs_in_ci and recent:
        raw = 100.0
    elif active and runs_in_ci:
        raw = 75.0
    elif active:
        raw = 50.0
    else:
        raw = 0.0
    return {"score": raw, "sub_checks": sub}


def _score_sbom(eco: dict) -> dict[str, object]:
    """20% weight — SBOM generation configured and active."""
    sbom = eco.get("sbom_generation", {})
    active = bool(sbom.get("active", False))
    has_tool = bool(sbom.get("tool", ""))
    has_format = bool(sbom.get("format", ""))
    sub = {
        "sbom_generation_active": active,
        "sbom_tool_specified": has_tool,
        "sbom_format_specified": has_format,
    }
    if active and has_tool and has_format:
        raw = 100.0
    elif has_tool and has_format:
        raw = 50.0
    elif active:
        raw = 40.0
    else:
        raw = 0.0
    return {"score": raw, "sub_checks": sub}


def _score_ecosystem(eco: dict) -> dict:
    """Compute weighted health score for one ecosystem."""
    dimensions = {
        "lockfile_present":         _score_lockfile(eco),
        "package_manager_pinned":   _score_pm_pinned(eco),
        "update_policy_defined":    _score_update_policy(eco),
        "security_scanning_active": _score_security_scanning(eco),
        "sbom_generation_active":   _score_sbom(eco),
    }
    weighted_score = sum(
        dimensions[dim]["score"] * DIMENSION_WEIGHTS[dim]
        for dim in DIMENSION_WEIGHTS
    )
    overall = round(weighted_score, 1)
    return {
        "ecosystem": eco.get("name", "unknown"),
        "package_manager": eco.get("package_manager", "unknown"),
        "overall_score": overall,
        "tier": _health_tier(overall),
        "dimensions": dimensions,
    }


# ---------------------------------------------------------------------------
# Subcommand: health
# ---------------------------------------------------------------------------

def cmd_health(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    ecosystems = data.get("ecosystems", [])
    if not ecosystems:
        print("No ecosystems found in manifest.")
        return 1

    print(f"Dependency Health — {data.get('project_name', 'Unknown')}  ({data.get('manifest_date', '?')})")
    print()

    scores_for_summary: list[dict] = []

    for eco in ecosystems:
        result = _score_ecosystem(eco)
        scores_for_summary.append(result)

        tier = result["tier"]
        overall = result["overall_score"]
        print(f"  Ecosystem : {result['ecosystem'].upper()}  ({result['package_manager']})")
        print(f"  Score     : {overall:.1f}/100  [{tier}]")
        print()

        print(f"  {'Dimension':<30} {'Weight':>7}  {'Score':>6}  {'Sub-checks'}")
        print("  " + "-" * 75)
        for dim_name, weight in DIMENSION_WEIGHTS.items():
            dim_result = result["dimensions"][dim_name]
            dim_score = dim_result["score"]
            sub_checks = dim_result["sub_checks"]
            passing = sum(1 for v in sub_checks.values() if v)
            total_sub = len(sub_checks)
            sub_summary = f"{passing}/{total_sub} passing"
            bar = "PASS" if dim_score >= 80 else ("WARN" if dim_score >= 40 else "FAIL")
            print(
                f"  {dim_name:<30} {weight*100:>5.0f}%  {dim_score:>5.0f}  "
                f"[{bar}] {sub_summary}"
            )

        # Show failing sub-checks
        failing_subs: list[str] = []
        for dim_name, dim_result in result["dimensions"].items():
            for sub_name, sub_val in dim_result["sub_checks"].items():
                if not sub_val:
                    failing_subs.append(f"{dim_name} → {sub_name}")
        if failing_subs:
            print()
            print("  Failing sub-checks:")
            for fs in failing_subs:
                print(f"    - {fs}")
        print()

    # Overall project summary
    if len(scores_for_summary) > 1:
        avg_score = sum(r["overall_score"] for r in scores_for_summary) / len(scores_for_summary)
        avg_tier = _health_tier(avg_score)
        print(f"  PROJECT OVERALL: {avg_score:.1f}/100  [{avg_tier}]")
        print()

    print("Tiers: HEALTHY ≥80 | ADEQUATE 60-79 | NEEDS_WORK 40-59 | CRITICAL <40")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: audit
# ---------------------------------------------------------------------------

def cmd_audit(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    ecosystems = data.get("ecosystems", [])
    if not ecosystems:
        print("No ecosystems found in manifest.")
        return 1

    print(f"Security Audit — {data.get('project_name', 'Unknown')}  ({data.get('manifest_date', '?')})")
    print()

    vuln_counts: dict[str, int] = {s: 0 for s in SEVERITIES if s != "none"}
    unmaintained: list[dict] = []
    outdated: list[dict] = []
    vuln_list: list[dict] = []

    for eco in ecosystems:
        eco_name = eco.get("name", "unknown")
        for dep in eco.get("dependencies", []):
            name = dep.get("name", "?")
            version = dep.get("version", "?")
            vuln = dep.get("known_vulnerability", False)
            severity = dep.get("severity", "none").lower()
            days = dep.get("days_since_update", 0)
            maintained = dep.get("is_maintained", True)
            dep_type = dep.get("type", "prod")

            if vuln and severity in vuln_counts:
                vuln_counts[severity] += 1
                vuln_list.append({
                    "ecosystem": eco_name,
                    "name": name,
                    "version": version,
                    "type": dep_type,
                    "severity": severity,
                    "days_since_update": days,
                })

            if not maintained:
                unmaintained.append({
                    "ecosystem": eco_name,
                    "name": name,
                    "version": version,
                    "type": dep_type,
                    "days_since_update": days,
                })

            if days > OUTDATED_DAYS:
                outdated.append({
                    "ecosystem": eco_name,
                    "name": name,
                    "version": version,
                    "type": dep_type,
                    "days_since_update": days,
                    "is_maintained": maintained,
                })

    # Vulnerability summary
    total_vulns = sum(vuln_counts.values())
    print(f"Vulnerability Summary  (total: {total_vulns})")
    print(f"  {'Severity':<10}  {'Count':>5}")
    print("  " + "-" * 20)
    for sev in ("critical", "high", "medium", "low"):
        count = vuln_counts[sev]
        flag = " *** ACTION REQUIRED ***" if sev in ("critical", "high") and count > 0 else ""
        print(f"  {sev.upper():<10}  {count:>5}{flag}")
    print()

    # Vulnerability details
    if vuln_list:
        vuln_list.sort(key=lambda x: SEVERITY_ORDER.get(x["severity"], 99))
        print("Vulnerable Packages")
        print(f"  {'Ecosystem':<10}  {'Package':<25}  {'Version':<12}  {'Severity':<10}  {'Days Old':>8}  Type")
        print("  " + "-" * 85)
        for v in vuln_list:
            print(
                f"  {v['ecosystem']:<10}  {v['name']:<25}  {v['version']:<12}  "
                f"{v['severity'].upper():<10}  {v['days_since_update']:>8}  {v['type']}"
            )
        print()

    # Unmaintained packages
    if unmaintained:
        print(f"Unmaintained Packages  ({len(unmaintained)} total)")
        print(f"  {'Ecosystem':<10}  {'Package':<25}  {'Version':<12}  {'Days Old':>8}  Type")
        print("  " + "-" * 70)
        for u in sorted(unmaintained, key=lambda x: -x["days_since_update"]):
            print(
                f"  {u['ecosystem']:<10}  {u['name']:<25}  {u['version']:<12}  "
                f"{u['days_since_update']:>8}  {u['type']}"
            )
        print()
    else:
        print("Unmaintained Packages: none detected")
        print()

    # Outdated packages (>180 days)
    if outdated:
        print(f"Outdated Packages  (>{OUTDATED_DAYS} days since update, {len(outdated)} total)")
        print(f"  {'Ecosystem':<10}  {'Package':<25}  {'Version':<12}  {'Days Old':>8}  {'Maintained':<11}  Type")
        print("  " + "-" * 90)
        for o in sorted(outdated, key=lambda x: -x["days_since_update"]):
            maint = "yes" if o["is_maintained"] else "NO"
            print(
                f"  {o['ecosystem']:<10}  {o['name']:<25}  {o['version']:<12}  "
                f"{o['days_since_update']:>8}  {maint:<11}  {o['type']}"
            )
        print()
    else:
        print(f"Outdated Packages (>{OUTDATED_DAYS} days): none detected")
        print()

    # Exit code: non-zero if critical or high vulns found
    if vuln_counts["critical"] > 0 or vuln_counts["high"] > 0:
        ch = vuln_counts["critical"] + vuln_counts["high"]
        print(f"ACTION REQUIRED: {ch} critical/high vulnerability(ies) found.")
        return 1
    return 0


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    ecosystems = data.get("ecosystems", [])
    today = _today()

    lines: list[str] = []
    a = lines.append

    a(f"# Dependency Health Report — {data.get('project_name', 'Unknown')}")
    a("")
    a(f"**Report date:** {today}  ")
    a(f"**Manifest date:** {data.get('manifest_date', '?')}  ")
    a(f"**Description:** {data.get('description', '')}")
    a("")
    a("---")
    a("")

    # --- Overall health section ---
    a("## Health Summary")
    a("")
    a("| Ecosystem | Package Manager | Score | Tier |")
    a("|-----------|-----------------|------:|------|")

    eco_results: list[dict] = []
    for eco in ecosystems:
        result = _score_ecosystem(eco)
        eco_results.append(result)
        a(f"| {result['ecosystem']} | {result['package_manager']} | {result['overall_score']:.1f} | **{result['tier']}** |")

    if eco_results:
        avg_score = sum(r["overall_score"] for r in eco_results) / len(eco_results)
        avg_tier = _health_tier(avg_score)
        a(f"| **Project overall** | — | **{avg_score:.1f}** | **{avg_tier}** |")

    a("")
    a("> Tiers: **HEALTHY** ≥80 | **ADEQUATE** 60–79 | **NEEDS_WORK** 40–59 | **CRITICAL** <40")
    a("")
    a("---")
    a("")

    # --- Per-ecosystem health detail ---
    a("## Health Dimensions")
    a("")
    dim_labels = {
        "lockfile_present":         "Lockfile present (25%)",
        "package_manager_pinned":   "Package manager pinned (20%)",
        "update_policy_defined":    "Update policy defined (15%)",
        "security_scanning_active": "Security scanning active (20%)",
        "sbom_generation_active":   "SBOM generation active (20%)",
    }

    for result in eco_results:
        a(f"### {result['ecosystem'].upper()} — {result['package_manager']} — {result['overall_score']:.1f}/100 [{result['tier']}]")
        a("")
        a("| Dimension | Weight | Score | Sub-checks |")
        a("|-----------|-------:|------:|-----------|")
        for dim_name, weight in DIMENSION_WEIGHTS.items():
            dim_result = result["dimensions"][dim_name]
            dim_score = dim_result["score"]
            sub = dim_result["sub_checks"]
            passing = sum(1 for v in sub.values() if v)
            total_sub = len(sub)
            status = "PASS" if dim_score >= 80 else ("WARN" if dim_score >= 40 else "FAIL")
            a(
                f"| {dim_labels[dim_name]} | {weight*100:.0f}% | {dim_score:.0f} "
                f"| [{status}] {passing}/{total_sub} |"
            )
        a("")

        # Failing sub-checks detail
        failing: list[str] = []
        for dim_name, dim_result in result["dimensions"].items():
            for sub_name, sub_val in dim_result["sub_checks"].items():
                if not sub_val:
                    failing.append(f"`{sub_name}` (in `{dim_name}`)")
        if failing:
            a("**Failing sub-checks:**")
            a("")
            for f_item in failing:
                a(f"- {f_item}")
            a("")

    a("---")
    a("")

    # --- Security audit section ---
    a("## Security Audit")
    a("")

    vuln_counts: dict[str, int] = {s: 0 for s in SEVERITIES if s != "none"}
    unmaintained: list[dict] = []
    outdated: list[dict] = []
    vuln_list: list[dict] = []

    for eco in ecosystems:
        eco_name = eco.get("name", "unknown")
        for dep in eco.get("dependencies", []):
            name = dep.get("name", "?")
            version = dep.get("version", "?")
            vuln = dep.get("known_vulnerability", False)
            severity = dep.get("severity", "none").lower()
            days = dep.get("days_since_update", 0)
            maintained = dep.get("is_maintained", True)
            dep_type = dep.get("type", "prod")

            if vuln and severity in vuln_counts:
                vuln_counts[severity] += 1
                vuln_list.append({
                    "ecosystem": eco_name, "name": name, "version": version,
                    "type": dep_type, "severity": severity,
                    "days_since_update": days,
                })
            if not maintained:
                unmaintained.append({
                    "ecosystem": eco_name, "name": name, "version": version,
                    "type": dep_type, "days_since_update": days,
                })
            if days > OUTDATED_DAYS:
                outdated.append({
                    "ecosystem": eco_name, "name": name, "version": version,
                    "type": dep_type, "days_since_update": days,
                    "is_maintained": maintained,
                })

    total_vulns = sum(vuln_counts.values())
    a("### Vulnerability Summary")
    a("")
    a("| Severity | Count | Action |")
    a("|----------|------:|--------|")
    severity_actions = {
        "critical": "Remediate immediately",
        "high":     "Remediate within 7 days",
        "medium":   "Remediate within 30 days",
        "low":      "Schedule for next update batch",
    }
    for sev in ("critical", "high", "medium", "low"):
        count = vuln_counts[sev]
        action = severity_actions[sev] if count > 0 else "—"
        a(f"| {sev.capitalize()} | {count} | {action} |")
    a(f"| **Total** | **{total_vulns}** | |")
    a("")

    if vuln_list:
        vuln_list.sort(key=lambda x: SEVERITY_ORDER.get(x["severity"], 99))
        a("### Vulnerable Packages")
        a("")
        a("| Ecosystem | Package | Version | Severity | Days Since Update | Type |")
        a("|-----------|---------|---------|----------|-------------------|------|")
        for v in vuln_list:
            a(
                f"| {v['ecosystem']} | {v['name']} | {v['version']} "
                f"| **{v['severity'].upper()}** | {v['days_since_update']} | {v['type']} |"
            )
        a("")

    if unmaintained:
        a(f"### Unmaintained Packages ({len(unmaintained)})")
        a("")
        a("| Ecosystem | Package | Version | Days Since Update | Type |")
        a("|-----------|---------|---------|-------------------|------|")
        for u in sorted(unmaintained, key=lambda x: -x["days_since_update"]):
            a(f"| {u['ecosystem']} | {u['name']} | {u['version']} | {u['days_since_update']} | {u['type']} |")
        a("")

    if outdated:
        a(f"### Outdated Packages (>{OUTDATED_DAYS} days, {len(outdated)} total)")
        a("")
        a("| Ecosystem | Package | Version | Days Since Update | Maintained | Type |")
        a("|-----------|---------|---------|-------------------|------------|------|")
        for o in sorted(outdated, key=lambda x: -x["days_since_update"]):
            maint = "yes" if o["is_maintained"] else "**NO**"
            a(f"| {o['ecosystem']} | {o['name']} | {o['version']} | {o['days_since_update']} | {maint} | {o['type']} |")
        a("")

    a("---")
    a("")

    # --- Recommendations ---
    a("## Recommendations")
    a("")
    priority = 1
    if vuln_counts["critical"] > 0:
        a(f"{priority}. **[CRITICAL]** Remediate {vuln_counts['critical']} critical vulnerability(ies) immediately.")
        priority += 1
    if vuln_counts["high"] > 0:
        a(f"{priority}. **[HIGH]** Remediate {vuln_counts['high']} high vulnerability(ies) within 7 days.")
        priority += 1

    for result in eco_results:
        for dim_name, dim_result in result["dimensions"].items():
            if dim_result["score"] < 40:
                eco_label = result["ecosystem"]
                a(f"{priority}. **[{eco_label.upper()}]** Fix `{dim_name}` — score {dim_result['score']:.0f}/100.")
                priority += 1

    for result in eco_results:
        for dim_name, dim_result in result["dimensions"].items():
            if 40 <= dim_result["score"] < 80:
                eco_label = result["ecosystem"]
                a(f"{priority}. **[{eco_label.upper()}]** Improve `{dim_name}` — score {dim_result['score']:.0f}/100.")
                priority += 1

    if not unmaintained and total_vulns == 0:
        a("No critical issues found. Maintain current cadence.")

    a("")
    a("---")
    a("")
    a(f"*Generated by dep_auditor.py on {today}*")

    report_text = "\n".join(lines)

    if args.output:
        out = Path(args.output)
        out.write_text(report_text, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report_text)

    return 0


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dep_auditor.py",
        description="Dependency health scorer and security auditor (stdlib-only).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # health
    p_health = sub.add_parser(
        "health",
        help="Score dependency health across 5 dimensions with weighted tiers.",
    )
    p_health.add_argument(
        "--input", required=True, metavar="FILE",
        help="Path to sample-dependency-manifest.json",
    )

    # audit
    p_audit = sub.add_parser(
        "audit",
        help="Security audit: vulnerabilities, unmaintained packages, outdated packages.",
    )
    p_audit.add_argument(
        "--input", required=True, metavar="FILE",
        help="Path to sample-dependency-manifest.json",
    )

    # report
    p_report = sub.add_parser(
        "report",
        help="Full Markdown dependency health report combining health + audit.",
    )
    p_report.add_argument(
        "--input", required=True, metavar="FILE",
        help="Path to sample-dependency-manifest.json",
    )
    p_report.add_argument(
        "--output", default=None, metavar="FILE",
        help="Write report to this file instead of stdout",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "health": cmd_health,
        "audit":  cmd_audit,
        "report": cmd_report,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
