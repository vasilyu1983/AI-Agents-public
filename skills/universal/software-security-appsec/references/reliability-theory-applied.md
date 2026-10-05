---
description: Reliability-theory patterns for AppSec — STRIDE-to-FMEA mapping, attack trees as inverted FTA, defense-in-depth redundancy math, security availability budgets, hazard curves for credential rotation, Weibull on patch-SLA aging, MTTD/MTTR for security incidents, and SBOM supply-chain reliability.
last_verified: 2026-09-23
status: stable
primitives:
  - foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md
  - foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md
  - foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md
  - foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md
  - foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md
  - foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md
  - foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md
  - foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md
  - foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md
  - foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md
  - foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md
---

# Reliability Theory Applied — AppSec

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. This file is an adapter: definitions, formulas, and generic worked math live in the foundation and its [templates](../../foundations-reliability-theory/assets/templates/reliability-theory/). Validation rules live in [decision-and-validation.md](../../foundations-reliability-theory/references/decision-and-validation.md). Only the AppSec-specific decisions, calibration, and pitfalls are kept here.

## Table of Contents

- [Why Reliability Theory for AppSec](#why-reliability-theory-for-appsec)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — STRIDE-to-FMEA Mapping](#p1--stride-to-fmea-mapping)
  - [P2 — Attack Tree as Inverted Fault Tree](#p2--attack-tree-as-inverted-fault-tree)
  - [P3 — Defense-in-Depth as Redundancy Math](#p3--defense-in-depth-as-redundancy-math)
  - [P4 — Security Availability Budget Alongside CIA](#p4--security-availability-budget-alongside-cia)
  - [P5 — Hazard Curves for Credential Rotation](#p5--hazard-curves-for-credential-rotation)
  - [P6 — Weibull Analysis on Patch-SLA Aging](#p6--weibull-analysis-on-patch-sla-aging)
  - [P7 — MTTD and MTTR for Security Incidents](#p7--mttd-and-mttr-for-security-incidents)
  - [P8 — Supply-Chain Reliability via SBOM](#p8--supply-chain-reliability-via-sbom)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Importing Independence Assumptions into Security Models](#a1--importing-independence-assumptions-into-security-models)
  - [A2 — Using MTBF for Security Events as if They Were Random Failures](#a2--using-mtbf-for-security-events-as-if-they-were-random-failures)
  - [A3 — Treating Redundancy as Elimination of Attack Surface](#a3--treating-redundancy-as-elimination-of-attack-surface)
  - [A4 — Conflating Security Availability with System Availability](#a4--conflating-security-availability-with-system-availability)
- [Recipe Catalog](#recipe-catalog)
  - [R1 — Security FMEA for a New Auth Flow](#r1--security-fmea-for-a-new-auth-flow)
  - [R2 — Attack-Tree Quantification for Credential Compromise](#r2--attack-tree-quantification-for-credential-compromise)
  - [R3 — Patch-SLA Reliability Budget and Rotation Schedule](#r3--patch-sla-reliability-budget-and-rotation-schedule)
- [Cross-References](#cross-references)

---

## Why Reliability Theory for AppSec

Reliability and AppSec both ask when a system stops meeting its guarantees, so AppSec can borrow the vocabulary — but two assumptions behind most reliability math break against an adversary:

1. **Independence.** Parallel-redundancy math assumes independent failures. Two controls sharing an IdP, secrets store, WAF, or unpatched CVE fail together (A1).
2. **Stationarity.** Hazard rates in security depend on the adversary population, which reacts to CVE disclosure, PoC release, takedowns, and geopolitics (A2).

Where the adaptation holds, it gives threat modeling a scoring surface (FMEA), cheapest-path analysis (attack trees), a quantitative floor for defense-in-depth, budgets for control health, and evidence-based rotation and patch deadlines.

---

## Pattern Catalog

### P1 — STRIDE-to-FMEA Mapping

**Decision driven.** Which STRIDE threats get fixed first. Worksheet structure and scoring: [06-fmea.md](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md).

**Mapping.** Each STRIDE threat for a component is one FMEA failure mode row. Example rows for an OAuth token endpoint:

| Component | STRIDE | Failure Mode | Effect | S | Cause | O | Detection Controls | D | RPN | Action |
|-----------|--------|-------------|--------|---|-------|---|-------------------|---|-----|--------|
| OAuth endpoint | Spoofing | Client impersonation via leaked `client_secret` | Unauthorized API access | 9 | Secret in env var, logged in debug output | 5 | Secret scanning CI | 4 | 180 | Rotate to mTLS client auth; purge from logs |
| OAuth endpoint | Elevation of Privilege | Scope upgrade in authorization code exchange | Attacker gains admin scope | 10 | No scope-binding validation on code exchange | 3 | No automated check | 8 | 240 | Bind scope to code at issuance; add scope-equality assertion |
| OAuth endpoint | Denial of Service | Rate-limit bypass via distributed IPs | Login unavailable | 7 | Rate limit is per-IP only | 6 | Uptime alert (5-min lag) | 6 | 252 | Rate-limit by identity + IP; CAPTCHA at threshold |

**Triage.** Never rank by RPN alone: review every S ≥ 9 row independently of RPN (here the S = 9 and S = 10 rows are escalated even though the S = 7 DoS row has the highest RPN), then use RPN as a secondary screen within comparable rows. After mitigation, re-score O and D for residual RPN only once tests support the change.

**AppSec calibration.** Anchor O to threat-intelligence and OWASP Top 10 / ASVS data for the component type, not intuition. Treat broken access control (OWASP A01) on a public endpoint without an explicit authorization test as high occurrence (local calibration choice, not an OWASP-published score).

---

### P2 — Attack Tree as Inverted Fault Tree

**Decision driven.** Which control removes the most attack paths. Gate semantics and minimal-cut-set enumeration (MOCUS): [05-fault-tree-analysis.md](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md).

**Mapping.** Top event = attacker goal (state it precisely: "attacker reads arbitrary user PII from production DB", not "data breach"). AND = prerequisites the attacker must all satisfy; OR = alternative paths; minimal cut sets = minimal attack paths.

```
Top event: Attacker reads arbitrary user PII from production DB
└─ OR
   ├─ Direct DB access path (AND: network reachable AND credentials known)
   │  ├─ Network reachable from internet: DB in public subnet [rare, verify]
   │  └─ Credentials known (OR: leaked secret OR brute-forced OR phished DBA)
   ├─ Application-layer path (OR: SQLi OR IDOR)
   │  ├─ SQL injection on search endpoint [no parameterization]
   │  └─ IDOR on /api/users/{id} [no ownership check]
   └─ Insider path (AND: insider access AND no access controls)
      ├─ Rogue employee with DB access [existing role]
      └─ No row-level security enforcement
```

Minimal attack paths: {SQLi}, {IDOR} (single-step — the security analogue of an SPOF); {leaked credential + reachability}, {phished DBA + reachability} (two-step). Rank by attacker cost (IDOR: minutes with a valid session; SQLi: hours with public tooling; spear-phishing a DBA: weeks — illustrative estimates). Segmenting the DB network removes the whole direct-access AND branch; parameterizing all queries removes the SQLi subtree.

**Security boundary.** Do not compute path probabilities with the FTA product `P(MCS) = ∏ P(basic events)`: attacker events are chosen, not random — an adversary tries the cheapest path and pivots when it fails. Rank by attacker cost and by how many paths a control eliminates.

---

### P3 — Defense-in-Depth as Redundancy Math

**Decision driven.** Whether an extra control layer is worth its cost, and whether two architectures differ. Parallel-redundancy and common-cause (beta-factor) math: [07-redundancy-math.md](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md); mixed series-parallel: [10-system-reliability.md](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md).

**Worked example (three-layer web auth; illustrative per-attempt bypass probabilities).**

| Layer | Control | P(bypassed per attempt) | Assumption |
|-------|---------|------------------------|-----------|
| 1 | Phishing-resistant MFA (passkey) | 0.01 | Includes credential phishing + AiTM bypasses |
| 2 | Anomalous-login detection | 0.15 | Attacker uses residential proxy |
| 3 | Step-up re-auth on admin actions | 0.05 | High-value actions only |

If independent: `0.01 × 0.15 × 0.05 = 0.000075` (0.0075%) versus `0.01` for MFA alone — about 133× lower in this model.

**Before multiplying,** list shared dependencies (same IdP behind MFA and session tokens; same WAF behind rate limiting and input validation; same secrets store behind every secret-based control). Collapse each cluster sharing a dependency into one layer and replace the product with the shared dependency's compromise probability for that subtree (A1).

---

### P4 — Security Availability Budget Alongside CIA

**Decision driven.** When degraded security controls force a deploy freeze, even while uptime SLOs are green. Budget and burn-rate mechanics: [08-error-budgets.md](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md). SLO design and alert implementation are owned by [qa-observability slo-design-guide.md](../../qa-observability/references/slo-design-guide.md).

**Example control SLOs (targets are local choices; budget = (1 − target) × window, window = 30 days = 720 h).**

| Control | Security availability definition | SLO target | Budget (30 days) |
|---------|----------------------------------|-----------|------------------|
| MFA coverage | % of accounts with active MFA | ≥ 99% | 7.2 h below threshold |
| Secrets rotation | % of production secrets within rotation window | ≥ 95% | 36 h below threshold |
| WAF rule freshness | % of OWASP rule set on current version | ≥ 98% | 14.4 h stale |
| TLS certificate validity | % of endpoints with cert expiry > 14 days | 100% | 0 h (any breach is a violation) |

**CIA framing.** CIA availability asks whether users can reach the system; security availability asks whether the controls enforcing C and I are operational. A system can serve logins while HMAC verification is degraded by an expired signing key.

**Mechanics.** Instrument each control with a health metric; consume budget for each interval below threshold; on exhaustion, freeze feature deploys until the control is restored; review consumption weekly as a leading indicator. Alert on burn rate, not only remaining budget. If you page on a security SLO, use the foundation's multi-window rule (SRE Workbook ch. 5, Table 5-8: both long and short window must exceed the burn rate) rather than inventing tiers.

---

### P5 — Hazard Curves for Credential Rotation

**Decision driven.** Rotation interval per credential class, replacing calendar-uniform rules (e.g. "every 90 days"). Hazard and Weibull fitting: [03-hazard-functions.md](../../foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md), [09-weibull-analysis.md](../../foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md); β interpretation: [04-bathtub-curve.md](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md).

**Mapping.** Lifetime = time from credential issuance to first observed malicious use (SIEM correlated with issuance records). Credentials not yet compromised are right-censored — include them. β > 1 means exposure accumulates with age (logs, git history, departures, vendor breaches); β < 1 points at leaky provisioning workflows.

**Setting the interval.** Pick an acceptable cumulative compromise probability `p` per credential class and solve `F(t*) = p`, i.e. `t* = η · (−ln(1 − p))^(1/β)`. Example: η = 365 days, β = 2, p = 0.05 → t* ≈ 83 days. High-value classes (production DB passwords, signing keys) get a smaller `p`, hence shorter `t*`. Decide sample adequacy from the confidence interval on β and on `t*`, not from a fixed failure count.

**Why the model is more defensible here than for exploit timing.** Many exposure channels (accidental logging, workstation compromise, dependency leaks) are not adversarially timed, so a smooth hazard is a better approximation for exposure than for targeted attacks.

---

### P6 — Weibull Analysis on Patch-SLA Aging

**Decision driven.** Patch deadlines per CVE class, derived from time-to-exploitation data instead of fixed policy numbers. Fitting with censoring: [09-weibull-analysis.md](../../foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md).

**Mapping.** Lifetime = CVE publication → first documented in-the-wild exploitation (CISA KEV, vendor threat reports). CVEs not (yet) in KEV are right-censored at the analysis date; fit by censored MLE (e.g. `lifelines`). η is the characteristic life (≈63.2% of the modelled population exploited by η), not a median.

**Readouts.** `F(7)` and `F(30)` estimate residual exploitation risk under 7-day and 30-day SLAs. Stratify by EPSS at publication and check whether high-EPSS strata have shorter η or different β in your own data before tiering. An example tiering to test, not a sourced standard: Critical + high EPSS → 48 h; Critical + low EPSS → 14 days; High → 30 days. Refit quarterly; exploitation timelines drift.

**Security boundary.** Public PoC release is a step change a smooth Weibull does not capture. Override: if a PoC appears for an unpatched CVE in your stack, the deadline becomes 24 h regardless of the model (local policy choice). Do not extrapolate β beyond the observed data range.

---

### P7 — MTTD and MTTR for Security Incidents

**Decision driven.** Which detection channels and response processes to invest in. MTTR semantics: [01-mtbf-mttr.md](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md).

**Definitions per incident.** `MTTD_i = T_detect − T_start` (earliest attacker action in forensic data → first acted-on alert). `MTTR_i = T_contain − T_detect` (→ access revoked / exfiltration closed). Durations are usually right-skewed; report medians or geometric means with log-scale intervals, not only arithmetic means.

**AppSec use.**
- Set targets against the dwell time of your threat model (local choices, e.g. MTTD < 1 h and MTTR < 4 h for critical-asset incidents): ransomware operators move in hours; APT dwell time is longer, so the same MTTD can be adequate for one and fatal for the other.
- Stratify MTTD by detection source (SIEM rule, EDR, threat hunt, external notification). If SIEM-sourced MTTD is not lower than external notification, rule quality is the problem.
- Stratify MTTR by incident type (credential compromise, injection, insider, supply chain) to expose slow revocation workflows or out-of-hours gaps.
- Review MTTD/MTTR quarterly with P4 budgets: good P4 with high MTTD means prevention without detection; low MTTD with high MTTR means detection without playbooks.

Do not use MTBF to forecast incident frequency (A2).

---

### P8 — Supply-Chain Reliability via SBOM

**Decision driven.** Which dependencies to remediate or reject first. Series/parallel structure: [10-system-reliability.md](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md); allocation: [11-reliability-allocation.md](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md).

**Mapping.** SBOM (CycloneDX or SPDX, PURL-identified) gives the component inventory. Per component, `P_i` = probability of an actively exploitable vulnerability (EPSS for known CVEs affecting that version, or a binary "unpatched High/Critical" flag). A dependency chain is a series system: `P(chain compromised) = 1 − ∏(1 − P_i)`. Ten links at `P_i = 0.02` give `1 − 0.98^10 ≈ 0.183` — an 18% chance at least one link is compromised, which component-by-component scans hide. The independence caveat of A1 applies when links share a maintainer or build pipeline.

**AppSec use.** Allocate remediation effort to the components that reduce chain-level probability most per unit effort; a high-`P` component in a long chain can outrank a higher-CVSS component in isolation. Diff SBOMs per release and gate new transitive dependencies on a chain-level threshold. SBOM generation and integrity: [supply-chain-security.md](supply-chain-security.md).

---

## Anti-Pattern Catalog

### A1 — Importing Independence Assumptions into Security Models

**Description.** Multiplying bypass probabilities (`P_1 × P_2`) for controls that share a dependency — e.g. MFA and session validation behind one IdP — and using the small result to skip a third control.

**Why it fails.** A single compromise of the shared dependency bypasses every control derived from it, so the relevant probability is `P(shared dependency compromised)`, not the product. Three IdP-dependent layers are one effective layer against IdP compromise: the P3 product gives 0.0075%, while the real bypass probability is the IdP compromise probability.

**Fix.** Draw the control dependency graph; treat each cluster sharing a dependency as one control; build real depth from independent trust roots (on-device passkey, anomaly detector on its own pipeline, egress filter from a separate vendor). Common-cause models: [07-redundancy-math.md](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md).

---

### A2 — Using MTBF for Security Events as if They Were Random Failures

**Description.** "4 incidents in 24 months, so MTBF = 6 months, so 2 incidents next year" — used for budgets or insurance.

**Why it fails.** MTBF-based forecasting assumes a stationary rate; adversarial incident rates jump with CVE disclosure, new RaaS campaigns targeting your sector, takedowns, and your public profile. A quiet-period MTBF understates risk in a high-threat period.

**Fix.** Use MTBF only retrospectively (how often incidents occurred while defenses were in a known state). Forecast with threat-intelligence scenarios, scaling historical frequency by an explicit, documented elevated-threat factor when intelligence warrants. Keep MTTR semantics (P7).

---

### A3 — Treating Redundancy as Elimination of Attack Surface

**Description.** Adding a second factor or a second firewall rule and declaring the attack surface halved.

**Why it fails.** Each control is itself a target: a second factor brings OTP phishing, MFA-fatigue push spam, insecure backup codes, and compromised authenticator devices; a new rule set can be stale or misconfigured. Teams that treat MFA as closing account takeover miss AiTM proxies that steal post-MFA session tokens.

**Fix.** For every new control, run a mini attack tree (P2) for the basic events it introduces. In tree terms, a control that adds an AND prerequisite to existing paths helps; one that adds a new OR branch (a new way in) widens the surface.

---

### A4 — Conflating Security Availability with System Availability

**Description.** Reporting "99.9% availability SLO met" as evidence of security health.

**Why it fails.** Availability SLOs cannot see an over-broad RBAC rule, an unapplied WAF rule for a two-month-old CVE, or lapsed MFA enrollment. The typical outcome: an IAM role granting excessive permissions for months is found in an audit, not by an alert.

**Fix.** Keep a separate security availability dashboard with its own budgets (P4), in the same review cadence as reliability SLOs, and treat budget exhaustion as severity-equivalent to an SLO violation.

---

## Recipe Catalog

### R1 — Security FMEA for a New Auth Flow

**When to use.** Before a new or significantly changed authentication/authorization flow is finalized.

1. **Scope.** List every component (token issuer, validator, session store, MFA service, IdP, client library, enforcing endpoints) with a one-sentence function each.
2. **Threats.** Enumerate all six STRIDE categories per component ([threat-modeling-guide.md](threat-modeling-guide.md)); mark structurally impossible ones "mitigated by design" with the reason. Expect a few threats per component; a long list usually means scope has drifted into a neighbouring component.
3. **Score.** One FMEA row per threat (P1). Local calibration anchors: S from ASVS level of the failed control; O from OWASP Top 10 and EPSS data; D low only if an existing test or alert catches it before production.
4. **Triage (thresholds are local choices).** Every S ≥ 9 row (account takeover, privilege escalation to admin, PII exfiltration) is a mandatory fix regardless of RPN. Then screen the rest by RPN within comparable severity, e.g. > 200 before launch, 100–200 in the first post-launch sprint, < 100 accepted with owner and review date.
5. **Mitigate.** Name the exact control (e.g. "embed scope in the code at issuance; at exchange assert requested scope ⊆ bound scope"), owner, and date; re-score O and D after deployment.
6. **Verify.** Scan the flow (OWASP ZAP, Burp Suite) and add one test per high-severity row (e.g. upscoped token exchange → HTTP 400, no token issued).

**Output.** FMEA worksheet, triage table, mitigation plan with owners and dates, test checklist mapped to high-severity rows.

---

### R2 — Attack-Tree Quantification for Credential Compromise

**When to use.** Design review of any system issuing or relying on long-lived credentials (API keys, service-account tokens, OAuth client secrets, SSH keys, DB passwords).

1. **Goal.** e.g. "attacker obtains a valid credential with write access to the production DB, rotation interval ≥ 24 h".
2. **Tree.** OR branches: secrets-store exfiltration, git history, interception in transit (AND: network position AND TLS absent/downgraded), developer phishing, brute force, CI/CD supply-chain compromise. Keep depth to 3–4 levels.
3. **Score leaves by attacker cost** — skill (script kiddie / intermediate / nation-state), time (hours / days / weeks), detectability (detected / partial / undetected). This is a cost model, not probabilities (P2 boundary, A1).
4. **Rank minimal attack paths** by lowest cost and lowest detectability; that path is the primary exposure.
5. **Map controls** to the OR branches they eliminate, preferring controls high in the tree; record residual paths as accepted risks.
6. **Rotation.** Derive the interval per P5. Without historical data, a conservative local default (e.g. 30 days for broad-access secrets, 90 days for narrow read-only credentials) is a policy choice to revisit once data exists, not a derived value.

**Output.** Attack tree, ranked minimal attack paths, control mapping, residual risk register, rotation schedule with its basis stated.

---

### R3 — Patch-SLA Reliability Budget and Rotation Schedule

**When to use.** Setting or defending patch SLA policy for a stack.

1. **Data.** CISA KEV, EPSS feed, vendor advisories; CVEs affecting your runtimes, frameworks, and infrastructure over the last 24 months: publication date, CVSS, EPSS at publication, first-exploitation date, days to exploitation.
2. **Fit** a censored Weibull per P6; plot `S(t)`; stratify by EPSS.
3. **Deadlines.** Choose acceptable residual risk `p` per class (e.g. ≤ 5% for Critical) and compute `t* = η · (−ln(1 − p))^(1/β)` for Critical-high-EPSS, Critical-low-EPSS, High, Medium.
4. **Budget.** SLO per class: "100% of class-X CVEs patched within `t*`"; each system-day unpatched past `t*` consumes budget. Escalate to engineering leadership when 50% of the budget is consumed (a budget-consumed threshold, local choice — not a burn-rate alert).
5. **SBOM hook.** On a new CVE, find affected SBOM components and systems, start a per-system timer, and track aggregate exposure with the P8 series formula.
6. **PoC override.** Monitor NVD, GitHub advisories, and threat intel; a public PoC for an unpatched CVE sets the deadline to 24 h (P6).

**Output.** CVE-class SLA table with derived deadlines, budget definition, escalation threshold, SBOM hooks, PoC-override policy.

---

## Cross-References

| Primitive | Where Applied in This File |
|-----------|---------------------------|
| [01 — MTBF/MTTR](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md) | P7, A2 |
| [02 — Availability Formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md) | P4, A4 |
| [03 — Hazard Functions](../../foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md) | P5, P6 |
| [04 — Bathtub Curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md) | P5 β interpretation |
| [05 — Fault Tree Analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md) | P2, R2, A3 |
| [06 — FMEA](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md) | P1, R1 |
| [07 — Redundancy Math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) | P3, A1 |
| [08 — Error Budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md) | P4, R3, A4 |
| [09 — Weibull Analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md) | P5, P6, R3 |
| [10 — System Reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md) | P3, P8 |
| [11 — Reliability Allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md) | P8, R3 |

**Foundation:** [SKILL.md](../../foundations-reliability-theory/SKILL.md) · [decision-and-validation.md](../../foundations-reliability-theory/references/decision-and-validation.md) · [ai-agent-reliability.md](../../foundations-reliability-theory/references/ai-agent-reliability.md) (for AI-agent attack surfaces). Safety-II / STPA: [foundations-safety-engineering](../../foundations-safety-engineering/SKILL.md).

**Adjacent AppSec references:**

- [threat-modeling-guide.md](threat-modeling-guide.md) — STRIDE workflow feeding P1 and R1.
- [supply-chain-security.md](supply-chain-security.md) — SBOM inputs for P8.
- [incident-response-playbook.md](incident-response-playbook.md) — containment playbooks that MTTR (P7) measures.
- [game-theory-applied.md](game-theory-applied.md) — adversarial modeling where independence assumptions fail (A1, A2).
- [cryptography-standards.md](cryptography-standards.md) — credential types and rotation primitives for P5.
