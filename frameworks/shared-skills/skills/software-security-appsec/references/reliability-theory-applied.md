---
description: Reliability-theory patterns for AppSec — STRIDE-to-FMEA mapping, attack trees as inverted FTA, defense-in-depth redundancy math, security availability budgets, hazard curves for credential rotation, Weibull on patch-SLA aging, MTTD/MTTR for security incidents, and SBOM supply-chain reliability.
last_verified: 2026-05-02
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

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


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

Reliability engineering and application security solve adjacent problems: both ask "when and how does the system stop meeting its guarantees?" Reliability theory developed a precise vocabulary for that question — MTBF, hazard functions, fault trees, error budgets — and AppSec can borrow those tools directly.

However, the borrowing is not wholesale. Security failures are not physical wear-out events. A vulnerability does not degrade continuously like a capacitor; it exists in a binary state (present / patched) until an adversary decides to exploit it. The adversary is an intelligent agent, not a random process. This fundamentally breaks two core assumptions that underlie most reliability math:

1. **Independence of failure events.** Reliability formulas for parallel redundancy assume components fail independently. In security, two authentication servers can be compromised simultaneously by the same phishing kit or the same unpatched CVE. Shared software stack = correlated failure.

2. **Stationarity of hazard rates.** Reliability's hazard functions assume the failure rate is a property of the component. In security, the hazard rate is a property of the component *and* the adversary population, which responds to incentive structures (newly published CVEs spike attack rate), seasonality (holiday periods), and geopolitical events. It is non-stationary by design.

These two realities are called out explicitly in Anti-Pattern A1 and A2. The patterns and recipes below adapt the primitives to work within these constraints rather than assuming them away.

Where the adaptation holds, the payoff is concrete:

- FMEA gives threat modeling a structured scoring surface that links threat likelihood to business impact and detection gap.
- FTA inverted as an attack tree gives the attacker's minimal cut sets — the cheapest paths to compromise.
- Redundancy math gives defense-in-depth a quantitative floor rather than a vague "layered security" claim.
- Error budgets give security programs a mechanism to trade availability against security posture in the same unit.
- Weibull aging curves give patch-management programs a principled rotation schedule rather than arbitrary calendar rules.

---

## Pattern Catalog

### P1 — STRIDE-to-FMEA Mapping

**Problem.** Threat modeling with STRIDE produces a list of threats but no prioritization mechanism. Teams cannot decide which threats to fix first, and high-severity-but-unlikely threats compete with low-severity-but-certain ones.

**Reliability framing.** FMEA (primitive 06) assigns Risk Priority Numbers to failure modes: `RPN = Severity (S) × Occurrence (O) × Detection (D)`. STRIDE threat categories map cleanly onto FMEA failure modes. Each threat is a potential failure mode of the component under analysis.

**Operationalization.**

1. Enumerate STRIDE threats for the target component (e.g., the OAuth token endpoint):
   - **S**poofing — attacker impersonates a legitimate client.
   - **T**ampering — attacker modifies the authorization code in transit.
   - **R**epudiation — actions are taken without auditable attribution.
   - **I**nformation Disclosure — token leakage via error responses.
   - **D**enial of Service — token endpoint flooded to block legitimate logins.
   - **E**levation of Privilege — attacker obtains a token with broader scope.

2. For each STRIDE threat, fill one FMEA row:

| Component | STRIDE Category | Failure Mode | Effect | S | Cause | O | Detection Controls | D | RPN | Action |
|-----------|----------------|-------------|--------|---|-------|---|-------------------|---|-----|--------|
| OAuth endpoint | Spoofing | Client impersonation via leaked `client_secret` | Unauthorized API access | 9 | Secret in env var, logged in debug output | 5 | Secret scanning CI | 4 | 180 | Rotate to mTLS client auth; purge from logs |
| OAuth endpoint | Elevation of Privilege | Scope upgrade in authorization code exchange | Attacker gains admin scope | 10 | No scope-binding validation on code exchange | 3 | No automated check | 8 | 240 | Bind scope to code at issuance; add scope-equality assertion |
| OAuth endpoint | Denial of Service | Endpoint rate-limit bypass via distributed IPs | Login unavailable | 7 | Rate limit is per-IP only | 6 | Uptime alert (5-min lag) | 6 | 252 | Rate-limit by user identity + IP; add CAPTCHA at threshold |

3. Rank rows by RPN. Fix any row with S ≥ 9 regardless of RPN (catastrophic-severity override — see Anti-Pattern A2 in the FMEA primitive).

4. After mitigations, re-score O and D to compute residual RPN. Gate releases on residual RPN < threshold set by the security program.

**Security-specific calibration.** Score Occurrence (O) against threat-intelligence data for the component type, not intuition. For web applications, the OWASP Application Security Verification Standard (ASVS) and OWASP Top 10 provide frequency anchors. A broken access control finding (OWASP A01) should be scored O ≥ 7 for any public-facing endpoint without an explicit authorization test.

**Primitive link.** Primitive 06 (FMEA). See the FMEA worksheet structure and the catastrophic-severity override rule.

---

### P2 — Attack Tree as Inverted Fault Tree

**Problem.** A team wants to model how an attacker could achieve a high-value objective (e.g., exfiltrate customer PII, forge a payment) and identify the cheapest path to compromise. Traditional threat modeling produces lists of threats; what is needed is a structure that shows attacker cost and minimum viable attack paths.

**Reliability framing.** Fault Tree Analysis (primitive 05) is top-down: start from the undesired top event, decompose into lower-level causes via AND/OR gates, enumerate minimal cut sets. An attack tree is structurally identical but reframes the perspective: the "top event" is the attacker's goal, AND-gates represent prerequisites the attacker must satisfy simultaneously, OR-gates represent alternative paths. Minimal cut sets become *minimal attack paths* — the smallest set of attacker actions that achieves the goal.

**Operationalization.**

1. Define the attacker's top-level goal precisely: "Attacker reads a PII record of an arbitrary user from the production database" (not "data breach" — specificity is required to bound the tree).

2. Build the tree top-down with AND/OR gates. Example for a web application with a database backend:

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

3. Enumerate minimal attack paths (analogous to minimal cut sets):
   - {SQLi on search endpoint} — single-step; no prerequisites.
   - {IDOR on /api/users/{id}} — single-step; requires valid session only.
   - {leaked DB credential + network reachability} — two-step.
   - {phish DBA + network reachability} — two-step.

4. Assign attacker cost to each basic event:
   - SQLi: low (public tool, unpatched endpoint). Cost ≈ 1 hour for a script kiddie.
   - IDOR: very low (authenticated user, no tool needed). Cost ≈ 5 minutes.
   - Phish DBA: medium (requires spear-phishing campaign). Cost ≈ 1–2 weeks.

5. Rank minimal attack paths by attacker cost. Single-element paths with low cost are critical findings — equivalent to a single-element minimal cut set (SPOF) in reliability terms.

6. Map remediations to gate types: fixing SQLi eliminates an OR branch (removes one path); fixing missing parameterization on all queries eliminates an entire subtree; adding network segmentation to isolate the DB removes the top-level AND branch for the direct DB access path.

**Security-reliability boundary note.** In FTA, the probability of a minimal cut set is `P(MCS) = ∏ P(basic events)`, which assumes independence. In the attack tree, attacker-controlled basic events are not independent: an adversary who spends effort on the cheapest path first; if that path fails, they pivot to the next. The attacker's choice is adversarial, not random. Do not compute attack path probabilities using the FTA product formula. Instead, rank by attacker cost and use the tree to identify which gates, when eliminated, remove the most paths simultaneously — the highest-coverage control investment.

**Primitive link.** Primitive 05 (Fault Tree Analysis). The minimal cut set enumeration procedure (MOCUS algorithm) applies directly to attack tree minimal path enumeration.

---

### P3 — Defense-in-Depth as Redundancy Math

**Problem.** Security architecture specifies "multiple layers of controls" without a quantitative claim about how much defense depth actually reduces risk. Stakeholders cannot compare two architectures or justify the cost of a third layer.

**Reliability framing.** Parallel redundancy (primitive 07) gives the availability of a system where failure requires *all* components to fail simultaneously: `P(system failure) = ∏ P(component_i failure)`. For independent components in a parallel arrangement, adding one component reduces system failure probability by one order of magnitude per component.

Defense-in-depth is parallel security control redundancy: an attacker must defeat all layers to achieve the top-event objective. When controls are independent, the probability of complete bypass is:

```
P(all controls bypassed) = ∏ P(control_i bypassed)
```

**Operationalization for a three-layer web auth stack.**

| Layer | Control | P(bypassed in a given attack attempt) | Assumption |
|-------|---------|--------------------------------------|-----------|
| 1 | Phishing-resistant MFA (passkey) | 0.01 | Account for credential phishing + AiTM bypasses |
| 2 | Anomalous-login detection (IP, device, time) | 0.15 | Attacker uses residential proxy to blend in |
| 3 | Admin action re-authentication (step-up) | 0.05 | Targets high-value admin actions only |

If controls are independent:
```
P(all three bypassed) = 0.01 × 0.15 × 0.05 = 0.000075
```

Compare to a single-layer MFA-only architecture:
```
P(bypassed) = 0.01
```

Adding anomaly detection and step-up auth reduces breach probability 133× in this model.

**Critical caveat — shared failure modes.** The independence assumption breaks when controls share software dependencies, configuration, or operational teams. If the MFA provider and the anomaly detection system use the same identity token service, a compromise of that service bypasses both layers simultaneously — common-cause failure in reliability terms. Before multiplying, enumerate shared dependencies:

- Same IdP: MFA + session token both depend on it.
- Same WAF: rate limiting + input validation both depend on it.
- Same credentials store (AWS Secrets Manager): all secrets-based controls depend on it.

For each shared dependency, model a worst-case correlated failure scenario: if the dependency fails, which controls fail together? Replace the independent product with a correlated-failure estimate for that subtree.

**Primitive link.** Primitive 07 (Redundancy Math), specifically the common-cause failure correction. Primitive 10 (System Reliability) for mixed series-parallel architectures with shared dependencies.

---

### P4 — Security Availability Budget Alongside CIA

**Problem.** SRE error budgets track system availability (uptime) but do not track security posture over time. Security controls can degrade — credentials drift, WAF rules age, certificate pinning becomes stale — without triggering availability SLOs. The result is a system that is "five nines available" but whose security controls are in a partially failed state.

**Reliability framing.** Error budgets (primitive 08) define an acceptable failure rate for a given time window. The same mechanics apply to security controls: define a security availability metric for each control, set a budget for how long it may be degraded, and treat exhaustion of that budget as a reliability breach requiring remediation.

**Security availability metrics — example definitions.**

| Control | Security Availability Definition | SLO Target | Budget (30-day) |
|---------|----------------------------------|-----------|----------------|
| MFA coverage | % of accounts with active MFA enrolled | ≥ 99% | 0.43 hours below threshold |
| Secrets rotation | % of production secrets within rotation window | ≥ 95% | 36 hours below threshold |
| WAF rule freshness | % of OWASP rule set in current version | ≥ 98% | 14.4 hours stale |
| TLS certificate validity | % of endpoints with cert expiry > 14 days | 100% | 0 hours below threshold |

**CIA framing.** Standard CIA (Confidentiality, Integrity, Availability) treats availability as one of three properties. Security availability budget tracks the *operational health of the controls that enforce CIA* — not just whether the system is up. A system can be available (users can log in) while its integrity controls (HMAC verification) are degraded because the signing key expired. Security availability budget makes this visible.

**Budget tracking mechanics.**

1. Instrument each control with a health metric (e.g., a daily count of accounts with MFA enrolled).
2. Define the SLO as a percentage or binary threshold.
3. Each minute the metric is below threshold, consume budget proportionally.
4. When budget is exhausted: freeze new feature deploys until the control is restored (mirroring SRE error budget policy).
5. Review budget consumption in the security team's weekly sync as a leading indicator, not a lagging incident signal.

**Primitive link.** Primitive 08 (Error Budgets). The burn rate concept from error budgets applies: a fast burn (control degraded badly for a short period) costs more budget than a slow burn (control slightly degraded for a long period), so alert on burn rate, not only on absolute budget remaining.

---

### P5 — Hazard Curves for Credential Rotation

**Problem.** Credential rotation schedules are often set by calendar policy (rotate every 90 days) without evidence that 90 days is the right interval for any given credential type. Long-lived API keys, service account passwords, and OAuth client secrets accumulate risk as they age.

**Reliability framing.** The hazard function `h(t)` (primitive 03) gives the instantaneous failure rate at age `t` for components that have survived to time `t`. Applied to credentials: `h(t)` is the conditional probability that a credential is compromised at age `t`, given that it has not been compromised up to `t`. As credentials age, hazard generally increases — more time for exposure via logs, git history, employee departures, vendor breaches.

**Operationalization.**

1. Collect a sample of past credential compromise incidents with time-to-compromise `t` (time from credential issuance to first observed malicious use). Source: your SIEM correlated with credential issuance records, breach notification data.

2. Fit a Weibull distribution (primitive 09) to the time-to-compromise data:
   - Shape parameter `β > 1` indicates increasing hazard with age (wear-out). Most long-lived credentials exhibit this pattern.
   - Shape parameter `β < 1` indicates decreasing hazard (infant mortality) — uncommon for credentials but possible if newly issued credentials are frequently leaked in provisioning workflows.

3. Derive the hazard rate curve from the fitted Weibull:
   ```
   h(t) = (β/η) × (t/η)^(β−1)
   ```
   where `η` is the scale parameter (characteristic life).

4. Set the rotation interval at the age `t*` where `h(t*)` crosses an organizationally acceptable threshold. If your threat model accepts no more than `p = 0.01` conditional probability per week of undetected compromise for a given credential class:
   ```
   Find t* such that: 1 − exp(−(t*/η)^β) = 0.01
   ```
   That `t*` is your evidence-based rotation interval for that credential class.

5. Differentiate by credential class. High-value credentials (production DB passwords, signing keys) will have a shorter `t*` than low-value ones (read-only reporting API keys). Calendar-uniform rotation treats them the same; hazard-based rotation does not.

**Where random-process assumptions hold here.** Unlike exploit timing (which is adversarially chosen), credential exposure follows patterns closer to random leakage: accidental log output, developer workstation compromise, dependency vulnerability. Hazard modeling is more defensible for credential exposure than for targeted attack timing, because many exposure channels are not adversarially controlled.

**Primitive link.** Primitive 03 (Hazard Functions), Primitive 09 (Weibull Analysis). Fit using maximum likelihood estimation on your incident sample.

---

### P6 — Weibull Analysis on Patch-SLA Aging

**Problem.** Patch SLAs define how long a team has to apply a patch after a CVE is published (e.g., Critical: 7 days, High: 30 days). But the SLA is an arbitrary policy target, not a data-driven estimate of when exploitation probability crosses a risk threshold. Some Critical CVEs are weaponized within hours; others are never exploited in the wild.

**Reliability framing.** Weibull analysis (primitive 09) fits a time-to-failure distribution from historical data. For patch SLAs, the "failure" event is a confirmed exploitation of the CVE in the wild. Time `t` is measured from CVE publication date to first documented exploitation in threat-intelligence sources (CISA KEV, NVD EPSS, vendor threat reports).

**Operationalization.**

1. Pull a dataset of past CVEs relevant to your tech stack with: CVE ID, publication date, EPSS score at publication, and confirmed exploitation date (from CISA KEV or equivalent). Filter to CVEs with CVSS ≥ 7.

2. For CVEs that were exploited, compute `t = (exploitation date − publication date)` in days. For CVEs not yet exploited (right-censored observations), note the censoring time. Use Weibull MLE with censoring (the `lifelines` Python library handles this).

3. Fitted Weibull for a representative web-application stack will typically show `β > 1`, confirming increasing exploitation hazard with age. The characteristic life `η` (50th percentile of time-to-exploitation for exploited CVEs) is the empirical "half-life" of unpatched vulnerabilities.

4. Compute the probability of exploitation by patch-day target:
   - `P(exploited before day 7)` — the fraction of exploited CVEs weaponized within 7 days.
   - `P(exploited before day 30)` — the fraction weaponized within 30 days.
   Use these as the residual risk estimates for Critical and High patch SLAs respectively.

5. Stratify by EPSS score at publication. High EPSS CVEs (> 0.7) have a significantly higher `β` — they age faster. Propose a tiered SLA:
   - CVSS Critical + EPSS > 0.7: 48-hour SLA (Weibull curve crosses risk threshold fast).
   - CVSS Critical + EPSS < 0.3: 14-day SLA (exploitation is slower to materialize).
   - CVSS High: 30-day SLA for most.

6. Review the fitted model quarterly as new CVE exploitation data arrives. The Weibull parameters are not stable year-over-year — exploitation timelines have generally compressed as attacker tooling improves.

**Reliability-security boundary note.** Weibull shape parameters should not be extrapolated far beyond the empirical data range. Exploitation timelines are subject to step-changes driven by public PoC release, which creates a spike in exploitation hazard that a smooth Weibull does not capture. Supplement the Weibull model with an alert rule: if a public PoC is released for an unpatched CVE in your stack, override the SLA to 24 hours regardless of the model output.

**Primitive link.** Primitive 09 (Weibull Analysis), Primitive 03 (Hazard Functions).

---

### P7 — MTTD and MTTR for Security Incidents

**Problem.** Security teams measure detection and response quality qualitatively. "We detected it quickly" and "we responded well" are not actionable. Without quantitative baselines, improvement targets cannot be set and regressions cannot be detected.

**Reliability framing.** MTBF and MTTR (primitive 01) define mean time between failures and mean time to repair. For security incidents:
- **MTTD** (Mean Time to Detect): the mean time from the moment a breach or security event begins to the moment the security team has a confirmed detection alert.
- **MTTR** (Mean Time to Respond): the mean time from confirmed detection to the moment the threat is contained (attacker access revoked, malicious process terminated, exfiltration channel closed).

These are security-program reliability metrics, not system availability metrics.

**Operationalization.**

1. For each security incident in the trailing 12 months, record:
   - `T_start`: earliest evidence of the incident in forensic data (earliest attacker action visible in logs).
   - `T_detect`: timestamp of the first detection alert that was acted on.
   - `T_contain`: timestamp when containment was confirmed (access revoked, lateral movement stopped).
   - `MTTD_i = T_detect − T_start`
   - `MTTR_i = T_contain − T_detect`

2. Compute means and distributions. MTTD and MTTR are often log-normally distributed — use geometric mean and log-normal confidence intervals rather than arithmetic mean if the data is skewed.

3. Set improvement targets:
   - MTTD target: < 1 hour for critical asset incidents; < 24 hours for standard incidents.
   - MTTR target: < 4 hours for critical asset incidents.
   - Align targets to your threat model's dwell time sensitivity: ransomware operators move in hours; APT dwell time is weeks, so MTTD of 24 hours is still within response window for APT but fatal for ransomware.

4. Stratify MTTD by detection source: SIEM rule, EDR alert, threat hunt, external notification. Source-level MTTD identifies which detection channels are underperforming. SIEM-sourced detections should have lower MTTD than external notifications; if they do not, SIEM rule quality is the problem.

5. Track MTTR by incident type: credential compromise, injection attack, insider threat, supply-chain incident. Incident types with high MTTR expose process bottlenecks (e.g., slow credential revocation workflows, insufficient out-of-hours response coverage).

6. Include MTTD and MTTR in the security program's quarterly review alongside security availability budgets (P4). A security program with excellent P4 metrics but high MTTD is investing in prevention but not in detection; a program with low MTTD but high MTTR has detection but no response playbooks.

**Reliability-security boundary note.** MTBF (mean time between failures) translates poorly to security incidents. MTBF assumes failures are random and independent. Security incidents are not random — their frequency is driven by threat-actor activity, vulnerability disclosure cycles, and organizational defense posture. Do not use MTBF to project future incident frequency. Use threat-intelligence-based scenario planning instead.

**Primitive link.** Primitive 01 (MTBF/MTTR). Use MTTR semantics for containment time; replace MTBF semantics with threat-intelligence-driven frequency estimates.

---

### P8 — Supply-Chain Reliability via SBOM

**Problem.** Modern applications have hundreds of transitive dependencies. Each dependency is a component with its own failure modes: vulnerability disclosure, end-of-life, maintainer abandonment, malicious compromise of the package. The security risk of the application depends on the combined reliability of this component graph.

**Reliability framing.** System reliability (primitive 10) models the reliability of a system as a function of the reliability of its components and their structural arrangement (series, parallel, k-of-n). For a software supply chain: the application's security posture is the system-level reliability function over its dependency graph. Components in a series arrangement mean a single vulnerable dependency can compromise the whole application (series: `R_system = ∏ R_i`). Parallel arrangements (multiple implementations of a function) provide redundancy.

**Operationalization with SBOM.**

1. Generate or ingest an SBOM in CycloneDX or SPDX format for the application. The SBOM provides the component inventory: all direct and transitive dependencies with PURL identifiers and versions.

2. For each SBOM component, compute a component reliability score:
   - `R_i = 1 − P(component has an actively exploitable vulnerability)`.
   - Source `P(...)` from: EPSS scores for known CVEs affecting the component version, or from a binary "any known High/Critical CVE unpatched" flag if EPSS data is unavailable.

3. Identify the dependency graph structure. Most application stacks are dominated by series paths: the web server depends on the framework, which depends on the serialization library, which depends on the crypto library. A vulnerability in any link breaks the chain.

4. Compute system-level vulnerability probability for critical paths:
   ```
   P(any component in critical path compromised) = 1 − ∏ (1 − P(component_i compromised))
   ```
   For a chain of 10 dependencies each with `P = 0.02`:
   ```
   P(chain compromised) = 1 − (0.98)^10 ≈ 0.183
   ```
   That is an 18% probability of at least one compromised component in a 10-link chain — often surprising to teams focused on individual-component scans.

5. Apply reliability allocation (primitive 11) to prioritize remediation: allocate improvement effort to the components that reduce system-level vulnerability probability most per unit of effort. High-P components in long series chains should be prioritized over low-P components even if the low-P component has a higher CVSS score in isolation.

6. Track SBOM drift: each new release generates a new SBOM. Diffing SBOMs across releases surfaces newly added transitive dependencies that introduce new series elements into the chain. Gate new dependencies on a reliability-adjusted vulnerability probability threshold.

**Primitive link.** Primitive 10 (System Reliability), Primitive 11 (Reliability Allocation).

---

## Anti-Pattern Catalog

### A1 — Importing Independence Assumptions into Security Models

**Description.** A security architect applies parallel-redundancy math (`P(bypass) = P_1 × P_2`) to two controls that share an underlying dependency — for example, MFA and session-token validation both backed by the same identity provider. The calculation yields a small bypass probability that is then used to justify not adding a third control.

**Why it fails.** Reliability redundancy math is valid when components fail independently. Security controls backed by the same IdP, the same secrets store, the same WAF, or the same shared library do not fail independently — they fail together when the shared dependency is compromised. The product formula gives the probability of simultaneous independent failures; the relevant security scenario is a single compromise of the shared dependency that bypasses all controls derived from it simultaneously. The actual bypass probability equals `P(shared dependency compromised)`, not the product of the individual bypass probabilities.

**Consequence.** A three-layer defense-in-depth architecture with three IdP-dependent controls provides one effective layer of security against an IdP compromise, not three. The product formula gives 0.001% bypass probability; the real bypass probability is the IdP compromise probability — potentially 1% or higher.

**Fix.** Before applying redundancy math, draw the dependency graph for all controls. For each shared dependency, compute a correlated-failure scenario: "If this dependency is compromised, which controls fail simultaneously?" Treat each cluster of controls sharing a dependency as a *single control* for the purpose of bypass-probability calculation. Design genuine defense-in-depth with independent trust roots: an on-device authenticator (passkey), a behavioral anomaly detector with its own ML pipeline, and a network egress filter using a separate vendor. Three distinct trust roots allow the product formula to be applied with much lower correlation.

**Primitive anchor.** Primitive 07 (Redundancy Math) — common-cause failure correction. This is the most important primitive-level warning for AppSec practitioners importing reliability math.

---

### A2 — Using MTBF for Security Events as if They Were Random Failures

**Description.** A security program computes MTBF from historical incident data (e.g., "we had 4 incidents in 24 months, so MTBF = 6 months") and uses this to project future incident frequency, set insurance premiums, or justify security investment levels.

**Why it fails.** MTBF assumes an exponential inter-arrival time distribution, which requires that failure events occur at a constant, independent hazard rate. Security incidents are adversarially driven: attack frequency increases after public CVE disclosure, decreases after takedowns of specific threat actors, spikes during geopolitical events, and correlates with your organization's public profile and industry sector. These are not stationary random processes. An MTBF computed from a quiet period will underestimate risk during a high-threat period; an MTBF from a breach-heavy period will overestimate ongoing risk if the underlying threat actor was removed.

**Consequence.** A 6-month MTBF projected forward looks like "we will have 2 incidents next year." If the threat landscape shifts (a new ransomware-as-a-service targeting your sector launches), actual frequency may be 10× higher. Security budget and insurance based on the projected MTBF is dangerously underestimated.

**Fix.** Use threat-intelligence-based frequency estimates rather than historical MTBF for forward projections. MTBF is valid as a *retrospective program performance metric* (how often did incidents occur in the period we controlled our defenses?), not as a *predictive model* for future incident rates. Pair retrospective MTBF tracking with a threat-landscape multiplier: if threat intelligence indicates elevated targeting of your sector, multiply historical frequency by the elevated-threat factor when projecting forward.

**Primitive anchor.** Primitive 01 (MTBF/MTTR) — use MTTR semantics (response performance) but not MTBF semantics (future frequency prediction) in adversarial contexts.

---

### A3 — Treating Redundancy as Elimination of Attack Surface

**Description.** A team adds a second authentication factor and concludes that the attack surface has been halved, or adds a second firewall rule and concludes that firewall bypass risk has been reduced by 50%.

**Why it fails.** Redundancy in reliability theory reduces the probability of simultaneous component failure. In security, each additional layer is also an additional attack surface. A second authentication factor adds a second authentication component — which is itself a target for token theft, replay attack, OTP phishing, or MFA fatigue. A second firewall rule adds a second rule set — which can be misconfigured, stale, or bypassed via a different protocol. Adding a control reduces certain failure modes while introducing new ones.

**Consequence.** The team deploys MFA, concludes that account takeover risk is negligible, and does not address session token security. Attackers pivot to AiTM phishing (attacker-in-the-middle proxies that steal session tokens post-MFA), which bypasses the MFA control entirely. The new attack surface introduced by the session token was not modeled.

**Fix.** For each new control added, run a mini attack-tree analysis (P2): what new basic events does this control introduce? A second authentication factor introduces: "OTP phishing page," "MFA fatigue via repeated push," "backup code stored insecurely," "authenticator app on compromised device." These new events must be modeled and mitigated. Defense-in-depth reduces *existing* attack paths; it does not eliminate the need to analyze new paths introduced by each layer.

**Primitive anchor.** Primitive 05 (Fault Tree Analysis) — new AND-gate prerequisites do not increase attack surface; new OR-gate branches do.

---

### A4 — Conflating Security Availability with System Availability

**Description.** A team reports system uptime (99.9% availability SLO met) as evidence of security health. Security control degradations — expired WAF rules, unrotated credentials, lapsed MFA enrollment — do not appear in uptime dashboards and are not reported.

**Why it fails.** System availability measures whether the application serves requests successfully. Security availability (P4) measures whether the controls that enforce confidentiality and integrity are operational. A system can be 100% available while its authorization controls are broken (a misconfigured RBAC rule silently grants over-broad access) or its integrity controls are stale (a WAF rule updated for a CVE that was published two months ago was never applied). These are invisible to availability SLOs.

**Consequence.** The security team declares "system is healthy" based on uptime metrics. A misconfigured IAM role that has been granting excessive permissions for 3 months is discovered only during an audit, not in an automated SLO breach.

**Fix.** Maintain a separate security availability dashboard with its own SLOs and error budgets (P4). Include it in the same review cadence as reliability SLOs. Report security control health as a first-class operational metric alongside p99 latency and error rate. Treat a security availability budget exhaustion as a severity-equivalent event to an SLO violation.

**Primitive anchor.** Primitive 08 (Error Budgets). Security availability budget is a parallel construct to reliability error budget, not a subset of it.

---

## Recipe Catalog

### R1 — Security FMEA for a New Auth Flow

**When to use.** A new or significantly changed authentication or authorization flow is about to be designed or reviewed. Use before architecture is finalized, not after.

**Steps.**

**Step 1: Define scope and component list.**
- List every component in the auth flow: token issuer, token validator, session store, MFA service, identity provider, client library, and the application endpoints that enforce access control.
- For each component, write its function in one sentence: "OAuth token endpoint: accepts authorization code, validates it against the code_verifier, and issues access token and refresh token."

**Step 2: Generate STRIDE threats per component (Primitive 05 and 06).**
- For each component, enumerate threats in all six STRIDE categories.
- Prune quickly: if a STRIDE category is structurally impossible for a component (e.g., no persistent state means Repudiation requires logging — check that logging exists), note it as "mitigated by design" and move on.
- Aim for 2–4 threats per component. Fewer means you stopped too early; more than 6 is usually an indicator of scope creep into a different component.

**Step 3: Fill the FMEA worksheet.**
- One row per threat. Score S, O, D on the 1–10 scale anchored to your organization's calibration:
  - S: use OWASP ASVS level as an anchor (ASVS Level 3 control failure = S ≥ 8).
  - O: use OWASP Top 10 frequency data and CVE EPSS scores where applicable.
  - D: score as 1 if the threat would be caught by an existing test or alert before reaching production; score 8–10 if no automated detection exists.
- Compute RPN.

**Step 4: Triage.**
- All rows with S ≥ 9: mandatory fix, regardless of RPN. These are catastrophic-severity findings (account takeover, privilege escalation to admin, PII exfiltration).
- RPN > 200: fix before launch.
- RPN 100–200: fix within first sprint post-launch.
- RPN < 100: document as accepted risk with owner and review date.

**Step 5: Assign mitigations and owners.**
- For each high-priority row, specify the exact control: "Add scope binding: at code issuance, embed the scope into the code object; at exchange, assert that requested scope ≤ bound scope."
- Assign owner (engineer, team) and target date.
- Schedule a re-score of O and D after mitigation is deployed to compute residual RPN.

**Step 6: Verify.**
- Run the auth flow through an automated security scan (OWASP ZAP, Burp Suite) after implementation.
- Write a unit test for each high-RPN row that validates the mitigation: "Test: attempt token exchange with upscoped scope value; assert HTTP 400 and no token issued."

**Output.** FMEA worksheet, triage table, mitigation plan with owners and dates, and a test checklist mapped to each high-severity finding.

---

### R2 — Attack-Tree Quantification for Credential Compromise

**When to use.** A security design review for any system that issues or relies on long-lived credentials: API keys, service account tokens, OAuth client secrets, SSH keys, database passwords.

**Steps.**

**Step 1: Define the top-level attacker goal.**
- Example: "Attacker obtains a valid long-lived credential that grants write access to the production database."
- Confirm the scope is correct: "long-lived" means the credential has a rotation interval ≥ 24 hours; "write access" specifies the privilege level.

**Step 2: Build the attack tree (Primitive 05 inverted).**
- Enumerate all OR branches: ways to obtain the credential (exfiltrate from secrets store, find in git history, intercept in transit, phish a developer, brute-force, supply-chain compromise of a CI/CD pipeline that consumes the credential).
- For each branch that requires prerequisites, add AND sub-gates: "intercept in transit" requires "network position" AND "TLS downgrade or absence."
- Limit tree depth to 3–4 levels to keep it actionable.

**Step 3: Score each leaf node by attacker cost.**
- Assign three values per leaf: attacker skill required (script kiddie / intermediate / nation-state), time cost (hours / days / weeks), and detectability by current controls (detected / partially detected / undetected).
- This is not a random probability — it is an attacker cost model. Do not use FTA product formula here (see Anti-Pattern A1 and the boundary note in P2).

**Step 4: Identify minimal attack paths.**
- A minimal attack path is a set of leaf nodes whose joint success achieves the top goal.
- Rank paths by: total attacker cost (lower is higher priority to defend) and detectability (undetected paths are higher priority than detected paths).
- The path with lowest attacker cost and lowest detectability is your primary exposure.

**Step 5: Map controls to tree structure.**
- For each OR branch, identify which control, if applied, eliminates the branch.
- Prioritize controls that eliminate OR branches at the top of the tree (they remove entire subtrees of attack paths simultaneously).
- Document residual minimal attack paths after all planned controls are applied: these are your acknowledged residual risks.

**Step 6: Define rotation schedule from hazard curve (Primitive 03 and 09).**
- For the credential type, fit a Weibull distribution to historical compromise data or use industry benchmarks (P5 of this file).
- Set the rotation interval at the age where cumulative compromise probability crosses your threshold.
- For credentials with no historical data: default to 30 days for secrets with broad access, 90 days for narrowly scoped read-only credentials.

**Output.** Attack tree diagram, ranked minimal attack paths with attacker cost, control mapping table, residual risk register, and evidence-based rotation schedule.

---

### R3 — Patch-SLA Reliability Budget and Rotation Schedule

**When to use.** Setting or reviewing patch SLA policy for a technology stack, or justifying a specific patch deadline to a business stakeholder.

**Steps.**

**Step 1: Pull CVE exploitation data for your stack.**
- Source: CISA KEV (Known Exploited Vulnerabilities), NVD EPSS data feed, vendor security advisories.
- Filter to CVEs affecting your primary runtime languages, frameworks, and infrastructure components in the last 24 months.
- For each CVE: record publication date, CVSS score, EPSS score at publication, first-exploitation date (if in KEV), and days-to-exploitation.

**Step 2: Fit Weibull distribution on time-to-exploitation (Primitive 09).**
- Use right-censored MLE: CVEs not yet exploited are censored at today's date.
- Compute `β` (shape) and `η` (scale) parameters.
- Plot the survival function `S(t) = exp(−(t/η)^β)` to visualize "fraction of CVEs still unexploited at day t."
- Stratify by EPSS score: high-EPSS CVEs will show a much shorter `η`.

**Step 3: Read off risk-threshold patch deadlines.**
- Decide your acceptable residual exploitation risk `p` (e.g., accept ≤ 5% probability of exploitation before patching for Critical CVEs).
- Solve for `t*`: `1 − S(t*) = p`, so `t* = η × (−ln(1−p))^(1/β)`.
- For each CVE class (Critical-EPSS-high, Critical-EPSS-low, High-CVSS, Medium-CVSS), compute `t*` and express it as a days-to-patch SLA.

**Step 4: Build the patch security availability budget (Primitive 08).**
- For each CVE class, define the security availability SLO: "100% of Critical-EPSS-high CVEs patched within `t*` days."
- Each day a system remains unpatched past `t*` consumes budget.
- Set a burn-rate alert at 50% budget consumed: at that point, escalate to engineering leadership if patch is blocked by a dependency or test failure.

**Step 5: Integrate with SBOM (P8).**
- When a new CVE is published affecting a component in your SBOM, compute which SBOM-dependent systems are in scope.
- Trigger a patch-SLA timer per affected system per CVE.
- Track aggregate unpatched-CVE exposure across the system portfolio using the series-reliability formula from P8.

**Step 6: Add PoC-release override.**
- Monitor NVD, GitHub advisories, and threat-intelligence feeds for public PoC publication for unpatched CVEs.
- If a PoC is published for an unpatched CVE in your stack: override the SLA timer to 24 hours regardless of the Weibull model output. PoC publication creates a step-function increase in exploitation hazard that the smooth Weibull does not capture.

**Output.** CVE-class patch SLA table with Weibull-derived deadlines, security availability budget definition, burn-rate alert configuration, SBOM integration hooks, and PoC-override policy statement.

---

## Cross-References

| Primitive | Where Applied in This File |
|-----------|---------------------------|
| [01 — MTBF/MTTR](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md) | P7 MTTD/MTTR for security incidents; A2 boundary note on MTBF inapplicability to adversarial events |
| [02 — Availability Formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md) | P4 security availability budget; A4 conflation with system availability |
| [03 — Hazard Functions](../../foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md) | P5 credential rotation hazard curves; P6 patch-SLA aging |
| [04 — Bathtub Curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md) | P5 Weibull shape interpretation (β < 1 infant mortality, β > 1 wear-out for credentials) |
| [05 — Fault Tree Analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md) | P2 attack tree as inverted FTA; R2 attack-tree quantification; A1 independence assumption boundary |
| [06 — FMEA](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md) | P1 STRIDE-to-FMEA mapping; R1 security FMEA for auth flow |
| [07 — Redundancy Math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) | P3 defense-in-depth as redundancy; A1 common-cause failure correction; A3 attack surface added by each layer |
| [08 — Error Budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md) | P4 security availability budget; R3 patch SLA budget; A4 boundary with system availability |
| [09 — Weibull Analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md) | P5 credential rotation curves; P6 patch-SLA aging Weibull fit; R3 Steps 2–3 |
| [10 — System Reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md) | P8 SBOM supply-chain reliability; P3 series-parallel mixed architecture |
| [11 — Reliability Allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md) | P8 SBOM prioritization; R3 Step 5 aggregate exposure allocation |

**Adjacent AppSec references:**

- [threat-modeling-guide.md](threat-modeling-guide.md) — STRIDE methodology and threat enumeration workflow that feeds P1 and R1.
- [supply-chain-security.md](supply-chain-security.md) — SBOM generation, lockfile policy, and artifact integrity; P8 depends on SBOM inputs from this reference.
- [incident-response-playbook.md](incident-response-playbook.md) — Containment and recovery playbooks that MTTR (P7) measures.
- [game-theory-applied.md](game-theory-applied.md) — Adversarial modeling that complements the boundary caveats in A1 and A2; use game theory where reliability independence assumptions fail.
- [cryptography-standards.md](cryptography-standards.md) — Credential type definitions and rotation primitives that inform P5 rotation schedules.
