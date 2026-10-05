# vuln_tracker.py

Stdlib-only Python CLI for vulnerability tracking and security posture scoring. No external dependencies — runs with any Python 3.9+ installation.

## Purpose

Gives security teams and developers fast, reproducible answers to five core questions:

1. **Status** — What is the current security posture? Count vulnerabilities by severity and measure SLA compliance; a posture score requires coverage data in `report`.
2. **SLA** — Which open vulnerabilities are overdue? By how many days?
3. **Coverage** — Which attack surfaces have no scanner assigned?
4. **Triage** — Which open vulnerabilities to fix first, by exploitation evidence (KEV > EPSS > reachability > CVSS) rather than scanner severity.
5. **Report** — A full Markdown security testing report combining all of the above.

## Quick Start

Run from the `qa-security-testing/` directory:

```bash
# Vulnerability counts and SLA rate (score unavailable without coverage)
python scripts/vuln_tracker.py status --input data/sample-vulnerabilities.json

# SLA compliance check — lists overdue items with days overdue
python scripts/vuln_tracker.py sla --input data/sample-vulnerabilities.json

# Scanner coverage across all attack surfaces — flags gaps
python scripts/vuln_tracker.py coverage --input data/sample-scan-coverage.json

# Triage order: KEV override, then EPSS, reachability, CVSS
python scripts/vuln_tracker.py triage --input data/sample-vulnerabilities.json

# Full Markdown report to stdout
python scripts/vuln_tracker.py report \
  --input data/sample-vulnerabilities.json \
  --coverage data/sample-scan-coverage.json

# Full Markdown report written to file
python scripts/vuln_tracker.py report \
  --input data/sample-vulnerabilities.json \
  --coverage data/sample-scan-coverage.json \
  --output report.md
```

## Bundled SLA Policy

These are bundled policy defaults, not a universal remediation standard.

| Severity | Max Remediation Time |
|----------|---------------------|
| CRITICAL | 24 hours (1 day) |
| HIGH | 7 days |
| MEDIUM | 30 days |
| LOW | 90 days |

## Triage Priority

| Priority | Rule |
|----------|------|
| P0 act now | CISA KEV-listed (confirmed exploitation), unless marked unreachable; or EPSS ≥ 0.7 and reachable |
| P1 expedite | KEV-listed but marked unreachable (verify, then fix); EPSS ≥ 0.7 with unknown reachability; CVSS ≥ 9.0 with EPSS ≥ 0.3 or unknown |
| P2 standard SLA | CVSS ≥ 7.0 without the signals above |
| P3 track | Not reachable and not KEV, or low CVSS with no exploitation signal. Never auto-closed |

Ties are ordered by EPSS (descending), then CVSS (descending). The EPSS 0.7/0.3 cut-offs match `software-security-appsec`. They are org policy, not a FIRST standard. EPSS is a 30-day exploitation probability, not proof of exploitation; only KEV (or your own threat intel) confirms exploitation. The `report` subcommand orders open vulnerabilities by this priority.

## Security Posture Score (0–100)

With validated coverage supplied to `report --coverage`, the bundled heuristic score combines three components. It is an inventory summary, not proof of security:

| Component | Weight | Calculation |
|-----------|--------|-------------|
| SLA compliance rate | 40% | `compliant_open / total_open` |
| Scanner coverage breadth | 30% | `covered_surfaces / total_surfaces` |
| Critical/High vuln count | 30% | Inverted: 0 C/H = 100%, each C/H vuln reduces by 10pts |

**Posture tiers:**

| Score | Tier |
|-------|------|
| ≥ 80 | STRONG |
| 60–79 | ADEQUATE |
| 40–59 | AT_RISK |
| < 40 | CRITICAL |

`status` and `report` without `--coverage` mark the score unavailable. Missing coverage is never replaced by an assumed percentage. Use `report --coverage` to compute the score.

## Input File Formats

### Vulnerabilities (`data/sample-vulnerabilities.json`)

```json
{
  "product_name": "My SaaS App",
  "scan_date": "2026-03-10",
  "vulnerabilities": [
    {
      "id": "VULN-001",
      "title": "Reflected XSS in search parameter",
      "severity": "high",
      "status": "open",
      "discovered_date": "2026-03-10",
      "due_date": "2026-03-17",
      "scanner": "OWASP ZAP",
      "category": "xss",
      "affected_component": "web-app/search"
    }
  ]
}
```

| Field | Values | Notes |
|-------|--------|-------|
| `severity` | `critical` / `high` / `medium` / `low` | Severity grouping; `due_date` supplies the actual deadline |
| `status` | `open` / `in_progress` / `resolved` | `open` and `in_progress` are counted as active |
| `id`, `title` | nonempty strings | IDs must be unique |
| `due_date` | `YYYY-MM-DD` | Required for active findings; compared to today for SLA compliance |
| `kev` | `true` / `false` (optional) | Listed in CISA KEV; overrides CVSS |
| `epss` | `0.0`–`1.0` (optional) | FIRST EPSS score |
| `reachable` | `true` / `false` / `null` (optional) | Reachability analysis result; `null` = unknown |
| `cvss` | finite number from 0 to 10 (optional) | Take from the CNA/ADP record; NVD may not score it. Falls back to a severity-derived value |

### Scanner Coverage (`data/sample-scan-coverage.json`)

```json
{
  "scan_date": "2026-03-10",
  "scanners": [
    { "name": "Semgrep", "type": "SAST", "last_run": "2026-03-10" }
  ],
  "attack_surfaces": [
    {
      "name": "Web App",
      "scanners": {
        "Semgrep": true
      }
    }
  ]
}
```

Coverage requires a scanner inventory and a nonempty attack-surface list. Scanner names and surface names must each be unique; scanners require nonempty names and types. Each surface maps registered scanner names to JSON booleans. A surface is covered when at least one flag is `true`; no scanners means zero coverage, not a clean scan.

Malformed input exits nonzero before a status or report is emitted. Optional EPSS/CVSS values must be finite and in range; KEV is boolean and reachability is boolean or null. Explicit empty `vulnerabilities` is valid.

Run offline regressions with `python3 scripts/test_vuln_tracker.py` from the skill directory.

## Subcommand Reference

```
python scripts/vuln_tracker.py status   --help
python scripts/vuln_tracker.py sla      --help
python scripts/vuln_tracker.py coverage --help
python scripts/vuln_tracker.py triage   --help
python scripts/vuln_tracker.py report   --help
```
