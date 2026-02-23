---
name: product-antifraud
description: Use when building log-based fraud detection for fintech applications, analyzing registration or authentication logs for behavioral patterns, bot detection, credential stuffing, velocity abuse, GDPR PII exposure in logs, or designing rule-based antifraud systems with tunable thresholds.
---

# Product Antifraud -- Log-Based Fraud Detection

| Aspect | Detail |
|--------|--------|
| Purpose | Rule-based fraud detection from application logs (registration + auth flows) |
| Approach | Pure Python + pandas -- counting, grouping, threshold problems |
| Not for | ML classification -- use at moderate volumes (~50K entries/day) |
| Outputs | Markdown report + CSV alerts for security teams |

---

## When to Use This Skill

| Task | This Skill Applies |
|------|--------------------|
| Building fraud detection scripts for registration or auth logs | Yes |
| Analyzing K8s application logs for suspicious behavioral patterns | Yes |
| Detecting bots, credential stuffing, or velocity abuse from structured logs | Yes |
| Auditing logs for GDPR PII exposure (unmasked emails, phones, names) | Yes |
| Designing tunable threshold-based rule engines with JSON config | Yes |
| Reviewing or extending existing antifraud detection rules | Yes |
| Building fraud alerting reports (Markdown + CSV) for security teams | Yes |
| ML-based fraud scoring (real-time model inference) | No -- use [ai-ml-data-science](../ai-ml-data-science/SKILL.md) |
| Application security hardening (OWASP, auth implementation) | No -- use [software-security-appsec](../software-security-appsec/SKILL.md) |
| Infrastructure log analysis (access logs, firewall, WAF) | No -- use [ops-devops-platform](../ops-devops-platform/SKILL.md) |
| Real-time streaming fraud detection | No -- use [data-lake-platform](../data-lake-platform/SKILL.md) |

---

## Quick-Start Checklist

| Step | Action | Notes |
|------|--------|-------|
| 1 | Identify log type | Registration (`.txt.gz`/`.debug.gz`) or auth (`.log`/`.log.gz`) |
| 2 | Create directory structure | `config/`, `reports/`, script file |
| 3 | Build LogParser | Correct timestamp format: `,` for registration ms, `.` for auth ms |
| 4 | Implement SessionAggregator | pandas groupby for key dimensions (token, IP, device, email) |
| 5 | Create JSON config | Default thresholds (see Configuration Pattern below) |
| 6 | Implement velocity rules | R1-R12 or A1-A13 -- highest signal-to-noise ratio |
| 7 | Add bot detection rules | R13-R17 or A14-A19 |
| 8 | Add behavioral analysis rules | R18-R22 or A20-A25 |
| 9 | Enable PIIScanner | GDPR compliance pass on all log lines |
| 10 | Test in discover mode | `--mode discover` against example data |
| 11 | Tune thresholds | Reduce false positives, verify known fraud patterns surface |
| 12 | Cross-node correlation | Merge by token/session_id before aggregation |

---

## Quick Reference

### Architecture (4 Layers)

Every fraud detection script follows this pattern:

```text
Log Files (.gz, .log)
    |
    v
[1] LogFileReader       -- Walk dirs, handle .gz decompression, iterate lines
    |
    v
[2] LogParser           -- Regex extraction -> dataclass (RegistrationEvent / AuthEvent)
    |
    v
[3] SessionAggregator   -- Group by token/IP/device/email, compute features
    |
    v
[4] RuleEngine + Report -- Evaluate rules, produce Markdown + CSV alerts
```

### Detection Rule Categories

| Category | Registration (R) | Authentication (A) | Reference |
|----------|------------------|--------------------|-----------|
| Fraud velocity | R1-R12 | A1-A13 | [references/registration-fraud-rules.md](references/registration-fraud-rules.md), [references/auth-fraud-rules.md](references/auth-fraud-rules.md) |
| Bot vs human | R13-R17 | A14-A19 | [references/bot-detection-patterns.md](references/bot-detection-patterns.md) |
| Behavioral analysis | R18-R22 | A20-A25 | [references/behavioral-analysis-rules.md](references/behavioral-analysis-rules.md) |
| GDPR PII scanning | Both scripts | Both scripts | [references/gdpr-pii-scanning.md](references/gdpr-pii-scanning.md) |

### Rule Severity Quick Map

| Severity | Registration Examples | Auth Examples |
|----------|----------------------|---------------|
| CRITICAL | JNDI injection (R10), national ID exposure | Personal data API response leaks |
| HIGH | Email/device velocity (R1-R2), IP hopping (R6) | Brute force (A1), credential stuffing (A2), session hijack (A4) |
| MEDIUM | Partial phone masking, confirmation brute force (R8) | Captcha trigger rate (A8), off-hours surge (A10) |
| LOW | Sequential email patterns (R17) | Auth method escalation (A21) |

---

## Decision Tree

```text
New fraud detection task:
    |
    +-- Registration logs?
    |   +-- .txt.gz / .debug.gz format?
    |   |   -> Use RegistrationEvent parser (references/log-parser-architecture.md)
    |   +-- What signals available?
    |       +-- Token, IP, DeviceSerial, Email, Phone -> R1-R12 velocity rules
    |       +-- Timing data -> R13-R15 bot detection
    |       +-- Platform field -> R12, R16 device fingerprinting
    |
    +-- Authentication logs?
    |   +-- .log / .log.gz format?
    |   |   -> Use AuthEvent parser (references/log-parser-architecture.md)
    |   +-- What signals available?
    |       +-- user_id, IP, device_id -> A1-A6 velocity rules
    |       +-- Fraud check weights -> A5, A11 risk scoring
    |       +-- Country field -> A4, A20 impossible travel
    |       +-- Auth type field -> A12, A21 method switching
    |
    +-- GDPR compliance audit?
        -> Run PIIScanner pass on both log types
        -> See references/gdpr-pii-scanning.md
```

---

## CLI Interface Pattern

```bash
# Discover mode: analyze example logs, output pattern statistics
python registration_fraud.py examples/epa-registration/ --mode discover --output reports/

# Detect mode: apply rules to new logs, generate alerts
python registration_fraud.py /path/to/new-day-logs/ \
  --config config/registration_rules.json --output reports/

# Auth fraud (same pattern)
python auth_fraud.py examples/epa-identity-auth-publicapi/ --mode discover --output reports/
```

### Output Format

| Output | Filename | Contents |
|--------|----------|----------|
| Markdown report | `report_YYYYMMDD_HHMMSS.md` | Summary table, severity breakdown, detailed alerts with log line evidence |
| CSV export | `alerts_YYYYMMDD_HHMMSS.csv` | One row per alert, importable into SIEM/ticketing |

---

## Tech Stack

| Component | Tool | Notes |
|-----------|------|-------|
| Runtime | Python 3.10+ | Standard library: re, gzip, json, csv, argparse, dataclasses, collections, datetime, pathlib, statistics |
| Data analysis | pandas | Time-window grouping and aggregation (only pip dependency) |
| Report formatting | tabulate (optional) | Pretty markdown tables |

---

## Configuration Pattern

Rules use external JSON configs for tunable thresholds (no code changes needed):

```json
{
  "gdpr_pii_scanner": {
    "enabled": true,
    "check_emails": true,
    "check_phones": true,
    "check_names": true,
    "check_national_ids": true
  },
  "bot_detection": {
    "timing_variance_threshold_ms": 50,
    "min_human_step_interval_seconds": 2,
    "known_emulator_serials": ["000000000000000", "emulator-5554"],
    "scripting_user_agents": ["python-requests", "curl", "Go-http-client"]
  },
  "behavioral": {
    "impossible_travel_speed_kmh": 900,
    "burst_silence_ratio_threshold": 5.0,
    "session_abandonment_rate_threshold": 0.8
  }
}
```

---

## Common Anti-Patterns

| Anti-Pattern | Why It Fails | Instead |
|--------------|-------------|---------|
| Hardcoded thresholds in code | Cannot tune without redeployment | External JSON config per rule |
| Single-dimension rules only | Easy to evade by changing one variable | Cross-correlate IP + device + email + timing |
| No deduplication | Duplicate log lines inflate counts | Deduplicate by (timestamp, request_id, message hash) |
| Ignoring multi-line entries | Auth logs have stack traces across lines | Parser must detect continuation lines |
| Treating all timestamps alike | Registration uses `,` for ms; auth uses `.` | Normalize timestamp parsing per log type |
| Cross-node blind spots | Same session spans K8s nodes | Merge by token/session_id before aggregation |
| PII in fraud reports | GDPR violation in the detection output itself | Mask PII in report output, reference by hash/ID |

---

## Known Challenges

| Challenge | Impact | Mitigation |
|-----------|--------|------------|
| Multi-line log entries | Auth logs have stack traces across lines | Detect continuation lines (leading whitespace, `at `, `Caused by:`) |
| Duplicate log lines | Registration logs inflate counts | Deduplicate by (timestamp, request_id, message hash) |
| Masked data (`***MASKED***`) | Auth logs limit email/phone correlation | IP/device/user_id analysis still works |
| Different timestamp formats | Registration `,` for ms; auth `.` for ms | Normalize parsing per log type |
| Cross-node correlation | Same session spans K8s nodes | Merge by token/session_id before aggregation |
| Internal scanner noise | Qualys scanner IP `10.7.2.171` triggers R10 | Flag but annotate as likely internal scan |

---

## Trend Awareness Protocol

When users ask about current fraud detection approaches, search before answering:

| # | Search Query | Domain |
|---|-------------|--------|
| 1 | `"fintech fraud detection patterns 2026"` | Fraud patterns |
| 2 | `"application log fraud analysis tools 2026"` | Tooling |
| 3 | `"GDPR log compliance requirements 2026"` | Compliance |
| 4 | `"bot detection registration abuse 2026"` | Bot detection |

---

## Navigation

### Reference Guides

| File | Coverage |
|------|----------|
| [references/registration-fraud-rules.md](references/registration-fraud-rules.md) | Registration fraud rules R1-R12: thresholds, signals, detection logic |
| [references/auth-fraud-rules.md](references/auth-fraud-rules.md) | Auth fraud rules A1-A13: thresholds, signals, detection logic |
| [references/bot-detection-patterns.md](references/bot-detection-patterns.md) | Bot vs human: timing analysis, UA fingerprinting, speed checks, emulators |
| [references/behavioral-analysis-rules.md](references/behavioral-analysis-rules.md) | Behavioral: impossible travel, session abandonment, burst-then-silence |
| [references/gdpr-pii-scanning.md](references/gdpr-pii-scanning.md) | GDPR PII scanner: regex patterns, severity levels, config, report format |
| [references/log-parser-architecture.md](references/log-parser-architecture.md) | 4-layer architecture: LogFileReader, LogParser, SessionAggregator, RuleEngine |
| [data/sources.json](data/sources.json) | 18 curated antifraud, OWASP, GDPR, and log analysis resources |

### Related Skills

| Skill | Use For |
|-------|---------|
| [software-security-appsec](../software-security-appsec/SKILL.md) | Application security patterns, OWASP Top 10 |
| [ai-ml-data-science](../ai-ml-data-science/SKILL.md) | ML-based fraud classification (when rule-based is insufficient) |
| [data-analytics-engineering](../data-analytics-engineering/SKILL.md) | Data pipeline patterns for log aggregation |
| [qa-observability](../qa-observability/SKILL.md) | Observability, structured logging, SIEM integration |
