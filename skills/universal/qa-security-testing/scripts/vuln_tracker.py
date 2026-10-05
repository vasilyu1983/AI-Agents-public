#!/usr/bin/env python3
"""Vulnerability tracker and security posture scorer.

Subcommands:
  status    -- Count by severity, SLA compliance rate, overdue items, posture score.
  sla       -- Per-vuln SLA compliance check; list overdue items with days overdue.
  coverage  -- Scanner coverage across attack surfaces; flag uncovered areas.
  triage    -- Rank open vulns by exploitation evidence: KEV > EPSS > reachability > CVSS.
  report    -- Full Markdown security testing report combining vulns + coverage.

Optional per-vulnerability triage fields (all may be absent):
  kev        bool   listed in CISA Known Exploited Vulnerabilities (confirmed exploitation)
  epss       float  FIRST EPSS probability (0-1) of exploitation activity in the next 30 days
  reachable  bool   vulnerable code path reachable from your code (null/absent = unknown)
  cvss       float  base score; take it from the CNA/ADP record, NVD may not score it
"""

import argparse
import json
import math
import sys
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Bundled illustrative defaults only. Every compliance/overdue computation in this
# script (sla, report) uses each finding's own recorded `due_date`, never these
# numbers — a real program's SLA policy may set different windows per severity.
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

# EPSS cut-offs aligned with software-security-appsec (org policy, not a FIRST standard).
EPSS_HIGH = 0.7
EPSS_LOW = 0.3

# Used only when a finding has no numeric CVSS.
SEVERITY_CVSS_FALLBACK = {"critical": 9.0, "high": 7.0, "medium": 4.0, "low": 0.1}

PRIORITY_LABELS = {
    0: "P0 act now",
    1: "P1 expedite",
    2: "P2 standard SLA",
    3: "P3 track",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        sys.exit(f"Error: file not found: {path}")
    try:
        with p.open() as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"Error: cannot read JSON in {path}: {exc}")
    if not isinstance(data, dict):
        sys.exit(f"Error: input must be a JSON object: {path}")
    return data


def _vulns(data: dict) -> list:
    """Return the vulnerabilities list; exit if it is missing or malformed.

    A scanner export without the key must not read as "no vulnerabilities".
    """
    vulns = data.get("vulnerabilities") if isinstance(data, dict) else None
    if not isinstance(vulns, list):
        sys.exit("Error: input must be a JSON object with a 'vulnerabilities' list")
    seen = set()
    for index, vuln in enumerate(vulns):
        label = f"vulnerabilities[{index}]"
        if not isinstance(vuln, dict):
            sys.exit(f"Error: {label} must be an object")
        for field in ("id", "title"):
            if not isinstance(vuln.get(field), str) or not vuln[field].strip():
                sys.exit(f"Error: {label}.{field} must be a nonempty string")
        if vuln["id"] in seen:
            sys.exit(f"Error: duplicate vulnerability id: {vuln['id']}")
        seen.add(vuln["id"])
        if vuln.get("severity") not in tuple(SLA_DAYS):
            sys.exit(f"Error: {label}.severity must be critical, high, medium or low")
        if vuln.get("status") not in ("open", "in_progress", "resolved"):
            sys.exit(f"Error: {label}.status must be open, in_progress or resolved")
        if vuln["status"] in OPEN_STATUSES:
            _parse_date(vuln.get("due_date"))
        for field, ceiling in (("epss", 1), ("cvss", 10)):
            value = vuln.get(field)
            if value is not None and (type(value) not in (int, float)
                                      or not math.isfinite(value) or not 0 <= value <= ceiling):
                sys.exit(f"Error: {label}.{field} must be a finite number from 0 to {ceiling}")
        if "kev" in vuln and type(vuln["kev"]) is not bool:
            sys.exit(f"Error: {label}.kev must be boolean")
        if vuln.get("reachable") is not None and type(vuln["reachable"]) is not bool:
            sys.exit(f"Error: {label}.reachable must be boolean or null")
    return vulns


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
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


def _cvss(v: dict) -> float:
    if isinstance(v.get("cvss"), (int, float)):
        return float(v["cvss"])
    return SEVERITY_CVSS_FALLBACK.get(str(v.get("severity", "")).lower(), 0.0)


def triage_priority(v: dict) -> tuple[int, str]:
    """Return (priority 0-3, reason). Lower number = fix first.

    KEV is confirmed exploitation and overrides CVSS. EPSS is a probability,
    not proof. An unreachable finding is deprioritised, never auto-closed.
    """
    kev = v.get("kev") is True
    epss = v.get("epss")
    epss = float(epss) if isinstance(epss, (int, float)) else None
    reachable = v.get("reachable")  # True / False / None (unknown)
    cvss = _cvss(v)

    if kev:
        if reachable is False:
            return 1, "KEV-listed but marked unreachable: verify reachability, then fix"
        return 0, "KEV-listed (confirmed exploitation)"
    if epss is not None and epss >= EPSS_HIGH:
        if reachable is True:
            return 0, f"EPSS {epss:.2f} >= {EPSS_HIGH} and reachable"
        if reachable is None:
            return 1, f"EPSS {epss:.2f} >= {EPSS_HIGH}, reachability unknown"
    if reachable is False:
        return 3, "not reachable, not KEV: track, do not auto-close"
    if cvss >= 9.0 and (epss is None or epss >= EPSS_LOW):
        return 1, f"CVSS {cvss:.1f} with EPSS {'unknown' if epss is None else f'{epss:.2f}'}"
    if cvss >= 7.0:
        return 2, f"CVSS {cvss:.1f}, EPSS {'unknown' if epss is None else f'{epss:.2f}'}"
    return 3, f"CVSS {cvss:.1f}, no exploitation signal"


def rank_vulns(vulns: list[dict]) -> list[dict]:
    """Sort by priority, then EPSS (desc), then CVSS (desc)."""
    def key(v: dict) -> tuple:
        pri, _ = triage_priority(v)
        epss = v.get("epss") if isinstance(v.get("epss"), (int, float)) else -1.0
        return (pri, -epss, -_cvss(v))
    return sorted(vulns, key=key)


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
    if not isinstance(coverage_data, dict):
        sys.exit("Error: coverage must be a JSON object")
    scanners = coverage_data.get("scanners")
    surfaces = coverage_data.get("attack_surfaces")
    if not isinstance(scanners, list) or not isinstance(surfaces, list) or not surfaces:
        sys.exit("Error: coverage requires a scanners list and a nonempty attack_surfaces list")
    names = set()
    for scanner in scanners:
        if not isinstance(scanner, dict) or any(
            not isinstance(scanner.get(field), str) or not scanner[field].strip()
            for field in ("name", "type")
        ):
            sys.exit("Error: each scanner requires nonempty name and type strings")
        if scanner["name"] in names:
            sys.exit(f"Error: duplicate scanner name: {scanner['name']}")
        names.add(scanner["name"])
    surface_names = set()
    for surface in surfaces:
        if not isinstance(surface, dict) or not isinstance(surface.get("name"), str) or not surface["name"].strip():
            sys.exit("Error: each attack surface requires a nonempty name")
        if surface["name"] in surface_names:
            sys.exit(f"Error: duplicate attack surface: {surface['name']}")
        surface_names.add(surface["name"])
        mapping = surface.get("scanners")
        if not isinstance(mapping, dict) or any(name not in names or type(flag) is not bool
                                                for name, flag in mapping.items()):
            sys.exit(f"Error: {surface['name']}.scanners must map registered scanner names to booleans")
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
    vulns = _vulns(data)
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
    print("Security posture score : unavailable — supply --coverage to 'report'")
    return 0


def cmd_sla(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    vulns = _vulns(data)
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
    print(
        f"Bundled illustrative SLA defaults (not used below — overdue status uses each "
        f"finding's recorded due_date): CRITICAL={SLA_DAYS['critical']}d  "
        f"HIGH={SLA_DAYS['high']}d  MEDIUM={SLA_DAYS['medium']}d  LOW={SLA_DAYS['low']}d"
    )
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
    breadth = _coverage_breadth(data)
    scanners = data.get("scanners", [])
    surfaces = data.get("attack_surfaces", [])

    scanner_names = [s["name"] for s in scanners]

    print(f"Scanner Coverage Report  (scan: {data.get('scan_date', '?')})")
    print()

    # Scanner inventory
    print("Declared scanners")
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
        print("All attack surfaces have at least one declared scanner assignment.")

    return 0


def cmd_triage(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    open_vulns = _open_vulns(_vulns(data))
    if not open_vulns:
        print("No open or in-progress vulnerabilities found.")
        return 0
    print(f"Triage order — {data.get('product_name', 'Unknown')}")
    print(f"Rules: KEV override > EPSS >= {EPSS_HIGH} (+reachable) > CVSS; unreachable = track, never auto-close")
    print()
    print(f"  {'#':>2} {'PRIORITY':<16} {'ID':<12} {'CVSS':>5} {'EPSS':>5} {'KEV':<4} {'REACH':<6} REASON")
    print("  " + "-" * 96)
    for i, v in enumerate(rank_vulns(open_vulns), 1):
        pri, reason = triage_priority(v)
        epss = v.get("epss")
        reach = {True: "yes", False: "no"}.get(v.get("reachable"), "?")
        print(
            f"  {i:>2} {PRIORITY_LABELS[pri]:<16} {v['id']:<12} {_cvss(v):>5.1f} "
            f"{(f'{epss:.2f}' if isinstance(epss, (int, float)) else '-'):>5} "
            f"{('yes' if v.get('kev') is True else 'no'):<4} {reach:<6} {reason}"
        )
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    vuln_data = _load_json(args.input)
    vulns = _vulns(vuln_data)
    today = _today()

    # Optionally load coverage
    coverage_data: dict | None = None
    breadth = None
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
    score = _posture_score(sla_rate, breadth, ch_score) if breadth is not None else None
    tier = _posture_tier(score) if score is not None else "unavailable"

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
    score_text = f"{score:.1f} / 100" if score is not None else "unavailable (coverage not provided)"
    a(f"| Posture score | **{score_text}** |")
    a(f"| Posture tier | **{tier}** |")
    a(f"| SLA compliance | {sla_compliant}/{len(open_vulns)} open ({sla_rate*100:.0f}%) |")
    coverage_text = f"{breadth*100:.0f}%" if breadth is not None else "unavailable"
    a(f"| Scanner coverage | {coverage_text} |")
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
    a("Bundled illustrative defaults, shown for reference only. The overdue items below")
    a("use each finding's own recorded `due_date`, not this table.")
    a("")
    a(f"| Rule | Illustrative Default |")
    a(f"|------|-----------------------|")
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
    a("Ordered by triage priority (KEV > EPSS > reachability > CVSS), not by scanner severity.")
    a("")
    a("| Priority | ID | Severity | Status | Category | Scanner | Due Date | Title |")
    a("|----------|----|----------|--------|----------|---------|---------|-------|")
    for v in rank_vulns(open_vulns):
        a(
            f"| {PRIORITY_LABELS[triage_priority(v)[0]]} "
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
    for finding in rank_vulns(open_vulns):
        if finding["severity"] in ("critical", "high"):
            a(f"- Remediate **{finding['id']}** ({finding['severity']}) by recorded due date "
              f"**{finding['due_date']}**; escalate if overdue.")
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

    # triage
    p_tri = sub.add_parser(
        "triage",
        help="Rank open vulns by KEV, EPSS, reachability, then CVSS.",
    )
    p_tri.add_argument("--input", required=True, metavar="FILE",
                       help="Path to sample-vulnerabilities.json")

    # report
    p_rep = sub.add_parser(
        "report",
        help="Full Markdown security testing report combining vulns and coverage.",
    )
    p_rep.add_argument("--input", required=True, metavar="FILE",
                       help="Path to sample-vulnerabilities.json")
    p_rep.add_argument("--coverage", default=None, metavar="FILE",
                       help="Path to coverage JSON (required to compute a posture score)")
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
        "triage":   cmd_triage,
        "report":   cmd_report,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
