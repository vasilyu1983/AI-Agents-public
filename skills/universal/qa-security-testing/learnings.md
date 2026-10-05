# qa-security-testing — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] This skill had no CVSS-4.0-vs-3.1 or EPSS guidance despite being core to severity-vs-exploitability triage; added a CVSS+EPSS+reachability model to owasp-top-10-coverage.md.
- [2026-09-23] The triage model described EPSS > 0.5 as proof of mass exploitation, had no KEV override, and vuln_tracker.py ignored EPSS/KEV/reachability entirely. KEV is now the confirmed-exploitation override, EPSS is a 30-day probability with 0.7/0.3 policy cut-offs (aligned with software-security-appsec), and `vuln_tracker.py triage` enforces it with a regression test.

## Domain Knowledge

## Open Questions

## Consolidated Principles
