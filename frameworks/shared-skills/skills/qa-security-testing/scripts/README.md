# vuln_tracker.py

Stdlib-only Python CLI for vulnerability tracking and security posture scoring. No external dependencies — runs with any Python 3.9+ installation.

## Purpose

Gives security teams and developers fast, reproducible answers to four core questions:

1. **Status** — What is the current security posture? Count vulns by severity, measure SLA compliance, and compute an overall score.
2. **SLA** — Which open vulnerabilities are overdue? By how many days?
3. **Coverage** — Which attack surfaces have no scanner assigned?
4. **Report** — A full Markdown security testing report combining all of the above.

## Quick Start

Run from the `qa-security-testing/` directory:

```bash
# Overall security posture (vuln counts, SLA rate, score)
python scripts/vuln_tracker.py status --input data/sample-vulnerabilities.json

# SLA compliance check — lists overdue items with days overdue
python scripts/vuln_tracker.py sla --input data/sample-vulnerabilities.json

# Scanner coverage across all attack surfaces — flags gaps
python scripts/vuln_tracker.py coverage --input data/sample-scan-coverage.json

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

## SLA Rules

| Severity | Max Remediation Time |
|----------|---------------------|
| CRITICAL | 24 hours (1 day) |
| HIGH | 7 days |
| MEDIUM | 30 days |
| LOW | 90 days |

## Security Posture Score (0–100)

The score is a weighted combination of three components:

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

Note: when running `status` without a `--coverage` file, the coverage breadth component defaults to 50% as a neutral placeholder. Use `report --coverage` for the full score.

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
| `severity` | `critical` / `high` / `medium` / `low` | Drives SLA deadline |
| `status` | `open` / `in_progress` / `resolved` | `open` and `in_progress` are counted as active |
| `due_date` | `YYYY-MM-DD` | Compared to today for SLA compliance |

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
        "Semgrep": true,
        "OWASP ZAP": true,
        "gitleaks": false
      }
    }
  ]
}
```

Each attack surface lists every scanner by name with a `true`/`false` flag. A surface is considered covered if at least one scanner is `true`.

## Subcommand Reference

```
python scripts/vuln_tracker.py status   --help
python scripts/vuln_tracker.py sla      --help
python scripts/vuln_tracker.py coverage --help
python scripts/vuln_tracker.py report   --help
```
