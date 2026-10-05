# dep_auditor.py

Stdlib-only Python CLI (Python 3.9+) that scores a hand-written dependency **policy manifest**. It is a teaching and policy-review aid, not a vulnerability scanner.

## Limits (read first)

- It does **not** query any advisory database (OSV, GitHub Advisory Database, NVD, registry audit endpoints).
- It does **not** read `package.json`, lockfiles, `pyproject.toml`, or any real package manifest; it refuses them with exit 2.
- Its "audit" only counts `known_vulnerability` flags that a person or another tool wrote into the manifest. A clean result means "nothing was declared", never "no vulnerabilities".

For vulnerability detection, use the ecosystem's native audit tool as the default: `npm audit` (plus `npm audit signatures`), `pnpm audit`, `pip-audit`, `cargo audit`, `govulncheck`, `composer audit`, `dotnet list package --vulnerable --include-transitive`, or `osv-scanner` for polyglot repos. Triage the findings with [references/security-scanning.md](../references/security-scanning.md#vulnerability-triage).

## What it is useful for

1. **Health** — Does each ecosystem declare lockfile, pinning, update-policy, scanning, and SBOM practices? Scored 0–100 with weighted dimensions; weights and cutoffs are local policy heuristics.
2. **Audit** — Summarize declared vulnerability, maintenance, and age flags (for example, flags copied in from a native audit run).
3. **Report** — A Markdown report combining both views for a policy review.

## Quick Start

Run from the `dev-dependency-management/` directory:

```bash
python scripts/dep_auditor.py health --input data/sample-dependency-manifest.example.json
python scripts/dep_auditor.py audit  --input data/sample-dependency-manifest.example.json
python scripts/dep_auditor.py report --input data/sample-dependency-manifest.example.json --output report.md
```

## Exit Codes (fail closed)

| Code | Meaning |
|-----:|---------|
| 0 | `health`: policy scored; `audit`/`report`: no self-declared critical/high flags |
| 1 | Self-declared critical/high flags present (`audit` and `report`) |
| 2 | Invalid or unchecked input. Requires an explicit dependency list, typed policy flags, non-negative integer ages, and valid non-future scan dates; `audit`/`report` require boolean `known_vulnerability` and valid severity when true |

## Health Score Dimensions

The score is a weighted combination of five dimensions:

| Dimension | Weight | What it checks |
|-----------|-------:|----------------|
| `lockfile_present` | 25% | Declared lockfile presence and frozen CI install policy |
| `package_manager_pinned` | 20% | Declared package-manager pinning and version |
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
| Vulnerability flag | `known_vulnerability: true` with a `severity` of critical/high/medium/low |
| Cannot check | `known_vulnerability` missing or not boolean, or `true` without a valid `severity` → exit 2 |

Do not use exit code 1 as a CI vulnerability gate: the flags are self-declared. Gate CI on the native audit tool instead.

## Input File Format

The manifest is a JSON file describing one or more ecosystems. Each ecosystem must include `dependencies` (an explicit `[]` is valid); each dependency needs a non-empty string name and version. Policy flags must be booleans, ages must be non-negative integers, and supplied scan dates must be valid YYYY-MM-DD dates no later than today. See `data/sample-dependency-manifest.example.json` for a full Node.js + Python polyglot example.

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
      "security_scanning": { "tool": "npm audit", "active": true, "last_run_date": "YYYY-MM-DD", "runs_in_ci": true },
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
| `known_vulnerability` | bool | Required for `audit`/`report`. Copy from a native audit run; missing → exit 2 for those commands |
| `severity` | `critical` / `high` / `medium` / `low` / `none` | Worst declared severity (severity is not risk; triage by reachability and exploitation evidence) |
| `days_since_update` | integer | Non-negative days since the package version was published |
| `is_maintained` | bool | Whether the package is actively maintained |

## Subcommand Reference

```bash
python scripts/dep_auditor.py health  --help
python scripts/dep_auditor.py audit   --help
python scripts/dep_auditor.py report  --help
```
