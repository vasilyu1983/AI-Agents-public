---
description: Continuous red-plus-blue attack-defense cycle for security-sensitive teams.
last_verified: 2026-09-16
status: stable
---

# Purple Team Pattern (Continuous Red+Blue)

Continuous attack-defense cycle in a single session. Every vulnerability found feeds directly into a fix, and the fix is verified before moving to the next finding. Not episodic (red phase → blue phase → done) but continuous (find → fix → verify → find next).

## Why Separate Red/Blue Fails for Agent Teams
Traditional red/blue teaming produces a report that a separate team addresses later. In agent teams, this gap means: findings lose context, fixes don't get verified against the original attack, and new vulnerabilities introduced by fixes go undetected. Purple teaming closes the loop.

## Mechanism
Single session with 3 roles:
- Red Agent: finds vulnerabilities, creates attack scenarios, tests fixes
- Blue Agent: patches vulnerabilities, implements defenses, hardens code
- Purple Lead: coordinates, ensures findings connect to fixes, tracks completion

Cycle: Red finds → Blue fixes → Red verifies fix → Red finds next

## Protocol
Phase 1: Red agent scans for issues (security, performance, test gaps)
Phase 2: Red reports finding with severity and reproduction steps
Phase 3: Blue implements fix
Phase 4: Red verifies fix resolves the issue AND doesn't introduce new problems
Phase 5: Log finding + fix + verification. Move to next finding.

## Team Mapping
- software-code-review-board: security-reviewer (red) + performance-reviewer (blue) → continuous find-fix
- `expert-board` release-readiness mode: test-reviewer (red) + runbook-auditor (blue) → test gap → fix → verify
- Any code review where findings should be ACTED ON, not just reported

## When To Use
- Pre-release security hardening
- Post-incident remediation (after the `expert-board` incident mode identifies root cause)
- Code review when you want fixes, not just a findings list
- Any time "we found 12 issues" should become "we fixed 12 issues"

## When NOT To Use
- When you only need a report (standard code-review-board is sufficient)
- When red and blue roles need different repos or contexts
- Exploratory research where there's nothing to "fix"

## Key Findings
- Agentic Purple Teaming (Lasso Security 2026): real-time remediation instead of scheduled assessments
- OWASP 2026 Top 10 for Agentic Applications: goal misalignment, tool misuse, delegated trust, inter-agent communication, persistent memory, emergent autonomous behavior
- Agent security harness (GitHub msaleme): 430-test security harness for autonomous AI agents [unverified as of 2026-09-16: repository not located — check the GitHub source before citing the test count]

## Common Mistakes
- Red agent reporting without reproduction steps (blue can't fix what it can't reproduce)
- Blue agent fixing without red verification (fix may not resolve the issue or may introduce new ones)
- Not logging the find-fix-verify chain (loses the audit trail)
- Running purple team without clear scope (becomes an endless audit)

## Sources
- Agentic Purple Teaming. Lasso Security 2026.
- OWASP Top 10 for Agentic Applications 2026.
- Red-Team Blue-Team Agent Fabric. GitHub msaleme.
