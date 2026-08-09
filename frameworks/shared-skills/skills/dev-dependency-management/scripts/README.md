# dep_auditor.py

Stdlib-only Python CLI for dependency health scoring and security auditing. No external dependencies — runs with any Python 3.9+ installation.

## Purpose

Gives developers and platform teams fast, reproducible answers to three core questions:

1. **Health** — How well does each ecosystem follow lockfile, pinning, update-policy, scanning, and SBOM best practices? Scored 0–100 with weighted dimensions.
2. **Audit** — Which packages have known vulnerabilities? Which are unmaintained or outdated (>180 days)?
3. **Report** — A full Markdown dependency health report combining both views.

## Quick Start

Run from the `dev-dependency-management/` directory:

```bash
# Overall dependency health score across all ecosystems
python scripts/dep_auditor.py health --input data/sample-dependency-manifest.json

# Security audit: vulnerability summary, unmaintained, outdated packages
python scripts/dep_auditor.py audit --input data/sample-dependency-manifest.json

# Full Markdown report to stdout
python scripts/dep_auditor.py report --input data/sample-dependency-manifest.json

# Full Markdown report written to file
python scripts/dep_auditor.py report \
  --input data/sample-dependency-manifest.json \
  --output report.md
```

## Health Score Dimensions

The score is a weighted combination of five dimensions:

| Dimension | Weight | What it checks |
|-----------|-------:|----------------|
| `lockfile_present` | 25% | Lockfile file exists; `--frozen-lockfile` or equivalent used in CI |
| `package_manager_pinned` | 20% | `packageManager` field set; PM version specified |
| `update_policy_defined` | 15% | Patch/minor/major cadence defined; automation tool configured |
| `security_scanning_active` | 20% | Scanning active; runs in CI; last run within 30 days |
| `sbom_generation_active` | 20% | SBOM tool and format specified; generation active |

**Health tiers:**

| Score | Tier |
|------:|------|
| ≥ 80 | HEALTHY |
| 60–79 | ADEQUATE |
| 40–59 | NEEDS_WORK |
| < 40 | CRITICAL |

## Audit Thresholds

| Check | Threshold |
|-------|-----------|
| Outdated | > 180 days since last update |
| Unmaintained | `is_maintained: false` in manifest |
| Vulnerability | `known_vulnerability: true` with `severity` field |

Exit code is `1` when critical or high vulnerabilities are detected — suitable for blocking CI.

## Input File Format

The manifest is a JSON file describing one or more ecosystems. See `data/sample-dependency-manifest.json` for a full Node.js + Python polyglot example.

Key structure:

```json
{
  "project_name": "my-project",
  "ecosystems": [
    {
      "name": "nodejs",
      "package_manager": "pnpm",
      "lockfile_present": true,
      "package_manager_pinned": true,
      "frozen_install_in_ci": true,
      "update_policy": { "patch": "weekly", "minor": "monthly", "major": "manual", "automation_tool": "renovate" },
      "security_scanning": { "tool": "npm audit", "active": true, "last_run_date": "2026-03-20", "runs_in_ci": true },
      "sbom_generation": { "tool": "npm sbom", "active": false, "format": "spdx" },
      "dependencies": [
        {
          "name": "express",
          "version": "4.18.2",
          "type": "prod",
          "known_vulnerability": false,
          "severity": "none",
          "days_since_update": 40,
          "is_maintained": true
        }
      ]
    }
  ]
}
```

| Field | Values | Notes |
|-------|--------|-------|
| `name` (ecosystem) | `nodejs` / `python` / `rust` / `go` | Identifies the ecosystem |
| `type` (dependency) | `prod` / `dev` | Dependency category |
| `severity` | `critical` / `high` / `medium` / `low` / `none` | Worst known CVE severity |
| `days_since_update` | integer | Days since the package version was published |
| `is_maintained` | bool | Whether the package is actively maintained |

## Subcommand Reference

```bash
python scripts/dep_auditor.py health  --help
python scripts/dep_auditor.py audit   --help
python scripts/dep_auditor.py report  --help
```
