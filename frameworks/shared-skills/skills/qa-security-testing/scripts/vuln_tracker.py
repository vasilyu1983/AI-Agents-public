#!/usr/bin/env python3
"""Vulnerability tracker and security posture scorer.

Subcommands:
  status    -- Count by severity, SLA compliance rate, overdue items, posture score.
  sla       -- Per-vuln SLA compliance check; list overdue items with days overdue.
  coverage  -- Scanner coverage across attack surfaces; flag uncovered areas.
  report    -- Full Markdown security testing report combining vulns + coverage.
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SLA_DAYS: dict[str, int] = {
    "critical": 1,   # 24 hours → 1 calendar day
    "high": 7,
    "medium": 30,
    "low": 90,
}

POSTURE_TIERS: list[tuple[int, str]] = [
    (80, "STRONG"),
    (60, "ADEQUATE"),
    (40, "AT_RISK"),
    (0,  "CRITICAL"),
]

OPEN_STATUSES = {"open", "in_progress"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        sys.exit(f"Error: file not found: {path}")
    try:
        with p.open() as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: invalid JSON in {path}: {exc}")


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        sys.exit(f"Error: cannot parse date '{value}' — expected YYYY-MM-DD")


def _today() -> date:
    return date.today()


def _posture_tier(score: float) -> str:
    for threshold, label in POSTURE_TIERS:
        if score >= threshold:
            return label
    return "CRITICAL"


def _open_vulns(vulnerabilities: list[dict]) -> list[dict]:
    return [v for v in vulnerabilities if v.get("status") in OPEN_STATUSES]


def _compute_posture(vulnerabilities: list[dict]) -> dict:
    """Return posture score (0–100) and its component breakdown."""
    open_vulns = _open_vulns(vulnerabilities)

    # --- Component 1: SLA compliance rate (40% weight) ---
    if not open_vulns:
        sla_rate = 1.0
    else:
        today = _today()
        compliant = sum(
            1 for v in open_vulns
            if _parse_date(v["due_date"]) >= today
        )
        sla_rate = compliant / len(open_vulns)

    # --- Component 2: placeholder breadth (30% weight) — filled by caller ---
    # Returned as None here; coverage subcommand computes it separately.
    coverage_score = None

    # --- Component 3: critical/high vuln count (30% weight, inverted) ---
    ch_count = sum(
        1 for v in open_vulns
        if v.get("severity") in ("critical", "high")
    )
    # 0 critical/high → 100%, each one reduces score; floor at 0
    ch_penalty = min(ch_count * 10, 100)
    ch_score = (100 - ch_penalty) / 100.0

    return {
        "sla_compliance_rate": sla_rate,
        "coverage_breadth": coverage_score,  # None until coverage data supplied
        "critical_high_score": ch_score,
        "open_count": len(open_vulns),
        "critical_high_open": ch_count,
    }


def _posture_score(sla_rate: float, coverage_breadth: float, ch_score: float) -> float:
    """Weighted posture score 0–100."""
    return round(
        sla_rate * 40.0
        + coverage_breadth * 30.0
        + ch_score * 30.0,
        1,
    )


def _coverage_breadth(coverage_data: dict) -> float:
    """Fraction of attack surfaces that have at least one scanner covering them."""
    surfaces = coverage_data.get("attack_surfaces", [])
    if not surfaces:
        return 0.0
    covered = sum(
        1 for s in surfaces
        if any(s.get("scanners", {}).values())
    )
    return covered / len(surfaces)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_status(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    vulns = data.get("vulnerabilities", [])
    today = _today()

    # Counts by severity (all statuses)
    counts: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    open_by_sev: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in vulns:
        sev = v.get("severity", "").lower()
        if sev in counts:
            counts[sev] += 1
        if v.get("status") in OPEN_STATUSES and sev in open_by_sev:
            open_by_sev[sev] += 1

    open_vulns = _open_vulns(vulns)
    overdue = [v for v in open_vulns if _parse_date(v["due_date"]) < today]
    sla_compliant = len(open_vulns) - len(overdue)
    sla_rate = sla_compliant / len(open_vulns) if open_vulns else 1.0

    ch_count = open_by_sev["critical"] + open_by_sev["high"]
    ch_penalty = min(ch_count * 10, 100)
    ch_score = (100 - ch_penalty) / 100.0

    # Coverage breadth: unknown without coverage file — use neutral 0.5
    coverage_breadth = 0.5
    score = _posture_score(sla_rate, coverage_breadth, ch_score)
    tier = _posture_tier(score)

    print(f"Security Status — {data.get('product_name', 'Unknown')}  (scan: {data.get('scan_date', '?')})")
    print()
    print("Vulnerability counts (all statuses)")
    for sev in ("critical", "high", "medium", "low"):
        open_n = open_by_sev[sev]
        total_n = counts[sev]
        print(f"  {sev.upper():8s}  total={total_n}  open={open_n}")
    print()
    print(f"Open vulnerabilities : {len(open_vulns)}")
    print(f"SLA compliant        : {sla_compliant}/{len(open_vulns)} ({sla_rate*100:.0f}%)")
    print(f"Overdue              : {len(overdue)}")
    print(f"Critical/High open   : {ch_count}")
    print()
    print(f"Security posture score : {score:.1f}/100  [{tier}]")
    print("  (coverage breadth component set to 50% — run 'coverage' for full score)")
    print()
    print("Posture tiers: STRONG ≥80 | ADEQUATE 60-79 | AT_RISK 40-59 | CRITICAL <40")
    return 0


def cmd_sla(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    vulns = data.get("vulnerabilities", [])
    today = _today()

    open_vulns = _open_vulns(vulns)
    if not open_vulns:
        print("No open or in-progress vulnerabilities found.")
        return 0

    overdue: list[dict] = []
    compliant: list[dict] = []
    for v in open_vulns:
        due = _parse_date(v["due_date"])
        days_remaining = (due - today).days
        entry = {**v, "_due": due, "_days_remaining": days_remaining}
        if days_remaining < 0:
            overdue.append(entry)
        else:
            compliant.append(entry)

    # Sort overdue by most overdue first
    overdue.sort(key=lambda x: x["_days_remaining"])

    print(f"SLA Check — {data.get('product_name', 'Unknown')}  (as of {today})")
    print()
    print(f"SLA rules: CRITICAL={SLA_DAYS['critical']}d  HIGH={SLA_DAYS['high']}d  MEDIUM={SLA_DAYS['medium']}d  LOW={SLA_DAYS['low']}d")
    print()

    if overdue:
        print(f"OVERDUE ({len(overdue)} items)")
        print(f"  {'ID':<12} {'SEVERITY':<10} {'DAYS OVERDUE':>12}  {'DUE DATE':<12}  TITLE")
        print("  " + "-" * 80)
        for v in overdue:
            days_over = abs(v["_days_remaining"])
            print(
                f"  {v['id']:<12} {v['severity'].upper():<10} {days_over:>12}  "
                f"{str(v['_due']):<12}  {v['title']}"
            )
    else:
        print("No overdue vulnerabilities.")

    print()
    if compliant:
        print(f"WITHIN SLA ({len(compliant)} items)")
        print(f"  {'ID':<12} {'SEVERITY':<10} {'DAYS LEFT':>9}  {'DUE DATE':<12}  TITLE")
        print("  " + "-" * 80)
        for v in sorted(compliant, key=lambda x: x["_days_remaining"]):
            print(
                f"  {v['id']:<12} {v['severity'].upper():<10} {v['_days_remaining']:>9}  "
                f"{str(v['_due']):<12}  {v['title']}"
            )

    sla_rate = len(compliant) / len(open_vulns) * 100
    print()
    print(f"SLA compliance: {len(compliant)}/{len(open_vulns)} open items ({sla_rate:.0f}%)")
    return 0


def cmd_coverage(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    scanners = data.get("scanners", [])
    surfaces = data.get("attack_surfaces", [])

    scanner_names = [s["name"] for s in scanners]
    breadth = _coverage_breadth(data)

    print(f"Scanner Coverage Report  (scan: {data.get('scan_date', '?')})")
    print()

    # Scanner inventory
    print("Active scanners")
    print(f"  {'NAME':<20} {'TYPE':<20} LAST RUN")
    print("  " + "-" * 60)
    for s in scanners:
        print(f"  {s['name']:<20} {s['type']:<20} {s.get('last_run', '?')}")
    print()

    # Coverage matrix
    print("Attack surface coverage")
    header_scanners = scanner_names
    col_w = 10
    name_w = 28
    header = f"  {'SURFACE':<{name_w}}" + "".join(f"{n[:col_w-1]:^{col_w}}" for n in header_scanners)
    print(header)
    print("  " + "-" * (name_w + col_w * len(header_scanners)))

    gaps: list[str] = []
    for surface in surfaces:
        covered_by = surface.get("scanners", {})
        any_covered = any(covered_by.get(n, False) for n in scanner_names)
        if not any_covered:
            gaps.append(surface["name"])
        cells = "".join(
            f"{'YES':^{col_w}}" if covered_by.get(n, False) else f"{'---':^{col_w}}"
            for n in scanner_names
        )
        flag = " *** GAP ***" if not any_covered else ""
        print(f"  {surface['name']:<{name_w}}{cells}{flag}")

    print()
    covered_count = len(surfaces) - len(gaps)
    print(f"Coverage breadth: {covered_count}/{len(surfaces)} surfaces ({breadth*100:.0f}%)")

    if gaps:
        print()
        print(f"COVERAGE GAPS ({len(gaps)} surfaces with no scanner)")
        for g in gaps:
            print(f"  - {g}")
    else:
        print("All attack surfaces are covered by at least one scanner.")

    return 0


def cmd_report(args: argparse.Namespace) -> int:
    vuln_data = _load_json(args.input)
    vulns = vuln_data.get("vulnerabilities", [])
    today = _today()

    # Optionally load coverage
    coverage_data: dict | None = None
    breadth = 0.5
    if args.coverage:
        coverage_data = _load_json(args.coverage)
        breadth = _coverage_breadth(coverage_data)

    # Compute components
    open_vulns = _open_vulns(vulns)
    overdue = [v for v in open_vulns if _parse_date(v["due_date"]) < today]
    sla_compliant = len(open_vulns) - len(overdue)
    sla_rate = sla_compliant / len(open_vulns) if open_vulns else 1.0

    open_by_sev: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in open_vulns:
        sev = v.get("severity", "").lower()
        if sev in open_by_sev:
            open_by_sev[sev] += 1

    ch_count = open_by_sev["critical"] + open_by_sev["high"]
    ch_score = (100 - min(ch_count * 10, 100)) / 100.0
    score = _posture_score(sla_rate, breadth, ch_score)
    tier = _posture_tier(score)

    lines: list[str] = []
    a = lines.append  # shorthand

    a(f"# Security Testing Report — {vuln_data.get('product_name', 'Unknown')}")
    a("")
    a(f"**Report date:** {today}  ")
    a(f"**Scan date:** {vuln_data.get('scan_date', '?')}  ")
    a(f"**Coverage data:** {'included' if coverage_data else 'not provided'}")
    a("")
    a("---")
    a("")
    a("## Security Posture")
    a("")
    a(f"| Metric | Value |")
    a(f"|--------|-------|")
    a(f"| Posture score | **{score:.1f} / 100** |")
    a(f"| Posture tier | **{tier}** |")
    a(f"| SLA compliance | {sla_compliant}/{len(open_vulns)} open ({sla_rate*100:.0f}%) |")
    a(f"| Scanner coverage | {breadth*100:.0f}%{' (estimated)' if not coverage_data else ''} |")
    a(f"| Critical/High open | {ch_count} |")
    a("")
    a("> Posture tiers: STRONG ≥80 | ADEQUATE 60–79 | AT_RISK 40–59 | CRITICAL <40")
    a("")
    a("---")
    a("")
    a("## Vulnerability Summary")
    a("")
    all_counts: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in vulns:
        sev = v.get("severity", "").lower()
        if sev in all_counts:
            all_counts[sev] += 1
    resolved_count = sum(1 for v in vulns if v.get("status") == "resolved")

    a("| Severity | Total | Open/In-Progress | Resolved |")
    a("|----------|-------|-----------------|---------|")
    for sev in ("critical", "high", "medium", "low"):
        total = all_counts[sev]
        open_n = open_by_sev[sev]
        resolved_n = total - open_n
        a(f"| {sev.capitalize()} | {total} | {open_n} | {resolved_n} |")
    a(f"| **Total** | **{len(vulns)}** | **{len(open_vulns)}** | **{resolved_count}** |")
    a("")
    a("---")
    a("")
    a("## SLA Compliance")
    a("")
    a(f"| Rule | Threshold |")
    a(f"|------|-----------|")
    for sev, days in SLA_DAYS.items():
        label = "24 hours" if days == 1 else f"{days} days"
        a(f"| {sev.capitalize()} | {label} |")
    a("")

    if overdue:
        a(f"### Overdue Items ({len(overdue)})")
        a("")
        a("| ID | Severity | Days Overdue | Due Date | Title |")
        a("|----|----------|-------------|---------|-------|")
        for v in sorted(overdue, key=lambda x: _parse_date(x["due_date"])):
            days_over = (today - _parse_date(v["due_date"])).days
            a(f"| {v['id']} | {v['severity'].capitalize()} | {days_over} | {v['due_date']} | {v['title']} |")
        a("")
    else:
        a("All open vulnerabilities are within SLA.")
        a("")

    a("---")
    a("")
    a("## Open Vulnerabilities")
    a("")
    a("| ID | Severity | Status | Category | Scanner | Due Date | Title |")
    a("|----|----------|--------|----------|---------|---------|-------|")
    for v in sorted(open_vulns, key=lambda x: ("critical", "high", "medium", "low").index(x["severity"])):
        a(
            f"| {v['id']} | {v['severity'].capitalize()} | {v['status']} "
            f"| {v.get('category', '?')} | {v.get('scanner', '?')} "
            f"| {v.get('due_date', '?')} | {v['title']} |"
        )
    a("")
    a("---")
    a("")

    # Coverage section
    if coverage_data:
        surfaces = coverage_data.get("attack_surfaces", [])
        scanner_names = [s["name"] for s in coverage_data.get("scanners", [])]
        gaps = [s["name"] for s in surfaces if not any(s.get("scanners", {}).values())]

        a("## Scanner Coverage")
        a("")
        a(f"| Scanner | Type | Last Run |")
        a(f"|---------|------|---------|")
        for s in coverage_data.get("scanners", []):
            a(f"| {s['name']} | {s['type']} | {s.get('last_run', '?')} |")
        a("")
        a(f"**Coverage breadth:** {breadth*100:.0f}% ({len(surfaces) - len(gaps)}/{len(surfaces)} surfaces)")
        a("")
        if gaps:
            a("### Coverage Gaps")
            a("")
            for g in gaps:
                a(f"- {g} — no scanner assigned")
            a("")
        a("---")
        a("")

    a("## Recommendations")
    a("")
    if overdue:
        ch_overdue = [v for v in overdue if v.get("severity") in ("critical", "high")]
        if ch_overdue:
            a(f"1. **Immediate action**: {len(ch_overdue)} critical/high overdue items require escalation.")
    if open_by_sev["critical"] > 0:
        a(f"- Remediate {open_by_sev['critical']} open CRITICAL vulnerability(ies) within 24 hours.")
    if open_by_sev["high"] > 0:
        a(f"- Remediate {open_by_sev['high']} open HIGH vulnerability(ies) within 7 days.")
    if coverage_data:
        gap_names = [s["name"] for s in coverage_data.get("attack_surfaces", []) if not any(s.get("scanners", {}).values())]
        for g in gap_names:
            a(f"- Assign a scanner to cover **{g}** attack surface.")
    if sla_rate < 0.8:
        a("- Review triage and remediation workflow — SLA compliance is below 80%.")
    a("")
    a("---")
    a("")
    a(f"*Generated by vuln_tracker.py on {today}*")

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
        prog="vuln_tracker.py",
        description="Vulnerability tracker and security posture scorer (stdlib-only).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = sub.add_parser(
        "status",
        help="Count vulns by severity, SLA compliance rate, overdue count, posture score.",
    )
    p_status.add_argument("--input", required=True, metavar="FILE",
                          help="Path to sample-vulnerabilities.json")

    # sla
    p_sla = sub.add_parser(
        "sla",
        help="Check SLA compliance for each open vuln; list overdue items with days overdue.",
    )
    p_sla.add_argument("--input", required=True, metavar="FILE",
                       help="Path to sample-vulnerabilities.json")

    # coverage
    p_cov = sub.add_parser(
        "coverage",
        help="Check scanner coverage across attack surfaces; flag gaps.",
    )
    p_cov.add_argument("--input", required=True, metavar="FILE",
                       help="Path to sample-scan-coverage.json")

    # report
    p_rep = sub.add_parser(
        "report",
        help="Full Markdown security testing report combining vulns and coverage.",
    )
    p_rep.add_argument("--input", required=True, metavar="FILE",
                       help="Path to sample-vulnerabilities.json")
    p_rep.add_argument("--coverage", default=None, metavar="FILE",
                       help="Path to sample-scan-coverage.json (optional, improves score accuracy)")
    p_rep.add_argument("--output", default=None, metavar="FILE",
                       help="Write report to this file instead of stdout")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "status":   cmd_status,
        "sla":      cmd_sla,
        "coverage": cmd_coverage,
        "report":   cmd_report,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
