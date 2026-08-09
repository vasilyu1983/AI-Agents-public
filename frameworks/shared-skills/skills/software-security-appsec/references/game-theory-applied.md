---
description: Game-theory patterns for the defender's design problem in AppSec — investment allocation, hardening priority, honeypot placement, deception strategy, patch vs. risk-accept, and vulnerability disclosure.
last_verified: 2026-05-02
status: stable
primitives:
  - foundations-game-theory/assets/templates/game-theory/07-mechanism-design-synthesis.md
  - foundations-game-theory/assets/templates/game-theory/06-cooperation-defection.md
  - foundations-game-theory/assets/templates/game-theory/02-adversarial-debate.md
---

# Game Theory Applied — AppSec Defender Design

> **Gate before invoking:** Check [`foundations-game-theory` § When to Apply](../../foundations-game-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


> For the testing-scheduling and coverage-side counterpart, see
> [`qa-security-testing/references/game-theory-applied.md`](../../qa-security-testing/references/game-theory-applied.md).

## Table of Contents

- [Why Game Theory for AppSec](#why-game-theory-for-appsec)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Stackelberg Defender-Attacker Allocation](#p1--stackelberg-defender-attacker-allocation)
  - [P2 — Honeypot Placement Under Budget](#p2--honeypot-placement-under-budget)
  - [P3 — Patch vs. Risk-Accept (Cost-Benefit with Attacker Rationality)](#p3--patch-vs-risk-accept-cost-benefit-with-attacker-rationality)
  - [P4 — Vulnerability Disclosure as Signaling Game](#p4--vulnerability-disclosure-as-signaling-game)
  - [P5 — Security Investment Under Uncertainty (Gordon-Loeb)](#p5--security-investment-under-uncertainty-gordon-loeb)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Static Defense (No Randomization)](#a1--static-defense-no-randomization)
  - [A2 — Equal-Spread Budget (Tambe's Anti-Pattern)](#a2--equal-spread-budget-tambes-anti-pattern)
  - [A3 — Deterministic Honeypots](#a3--deterministic-honeypots)
  - [A4 — Compliance Theatre](#a4--compliance-theatre)
- [Recipe Catalog](#recipe-catalog)
  - [R1 — Allocate a Hardening Budget Across N Assets Using Stackelberg](#r1--allocate-a-hardening-budget-across-n-assets-using-stackelberg)
  - [R2 — Decide Patch-Now vs. Accept-Risk in 5 Questions](#r2--decide-patch-now-vs-accept-risk-in-5-questions)
  - [R3 — Place Honeypots so Attacker Payoff Is Minimized](#r3--place-honeypots-so-attacker-payoff-is-minimized)
- [Canonical Primitives Used](#canonical-primitives-used)
- [Sources](#sources)

---

## Why Game Theory for AppSec

AppSec is a two-player game with asymmetric information. The defender chooses controls first; the attacker observes defenses (or infers them) and selects the best attack path. Classical risk management ignores attacker rationality — it treats threats as random events rather than as best-responses to the defender's own choices. The result is systematic over-investment in visible controls and under-investment where attacker payoff is highest.

Game theory corrects this by modeling:

1. **Attacker best-response** — given my defenses, which asset will a rational attacker target?
2. **Budget optimality** — where does the marginal dollar of hardening reduce expected loss most?
3. **Deception value** — when does making the attacker uncertain about defense state pay off more than hardening itself?
4. **Signaling equilibria** — what does voluntary vulnerability disclosure communicate, and when does it improve ecosystem outcomes?

---

## Pattern Catalog

### P1 — Stackelberg Defender-Attacker Allocation

**Problem.** The defender must allocate a finite hardening budget across N assets before the attacker moves. Which assets deserve investment?

**Model.** Stackelberg security game (Tambe, 2011). Defender is leader; attacker is follower. Defender chooses a mixed strategy (probability distribution over defended assets); attacker best-responds. Defender solves for the mixed strategy that minimizes expected attacker payoff.

Key insight: the optimal defender strategy is almost always a mixed strategy — randomize coverage so the attacker cannot exploit a deterministic gap. ARMOR (airport) and IRIS (port) both deploy this: randomized patrol schedules that are unpredictable to observers.

**Operationalization:**

1. Enumerate assets with value V_i (breach cost) and base vulnerability p_i (exploit probability without additional control).
2. Assign hardening effectiveness e_i: how much does one unit of budget reduce p_i?
3. Solve (or approximate): maximize sum over covered assets of (V_i × p_i × (1 − e_i × budget_share_i)) subject to budget constraint.
4. Output: budget allocation vector. Re-run when asset values or threat landscape changes.

**Primitive link.** Use mechanism-design synthesis (#7) to aggregate multiple team estimates of V_i and p_i before running the allocation. Dissent required on contested asset values.

**Reference.** Tambe, _Security and Game Theory_ (2011), Chapters 2–4.

---

### P2 — Honeypot Placement Under Budget

**Problem.** Given K available deception assets (honeypots, canary tokens, fake credentials) and M real assets, where should deception be deployed so a rational attacker is most likely to trigger it?

**Model.** The attacker samples from assets until finding a real target. The defender inserts honeypots into the asset set to maximize the probability that the attacker encounters a honeypot before a real target. This is a decoy placement game; optimal placement is a function of the attacker's prior over asset locations and their sampling strategy.

Key insight: honeypots placed adjacent to high-value real assets offer the highest detection probability because a rational attacker searching near high-value targets encounters them first. Honeypots placed in obscure locations are skipped by rational attackers — they only catch random scanners, not targeted ones.

**Operationalization:**

1. Model attacker prior: which assets does the attacker think are high-value?
2. Place honeypots in the neighborhood of assets the attacker is most likely to probe first.
3. Budget: if K < M, prioritize coverage near the top-V assets.
4. Vary honeypot appearance (credential age, endpoint naming) so attacker cannot distinguish by static signal.

**Primitive link.** Adversarial debate (#2) is useful here: run an attacker-mindset agent against a defender-mindset agent to stress-test the placement before deployment.

**Reference.** Albanese et al., "Deceiving attackers by creating fake attack graphs," 2012. MITRE ATT&CK Deception sub-techniques (T1580 family).

---

### P3 — Patch vs. Risk-Accept (Cost-Benefit with Attacker Rationality)

**Problem.** A CVE exists. Should you patch now, patch deferred, accept risk, or mitigate with a compensating control?

**Standard framing failure.** CVSS score × probability of exploit = expected loss. But this ignores attacker rationality: if you are a small, low-value target, a rational attacker will not invest in exploiting a difficult CVE when easier targets exist. Conversely, if your asset value is high, even a low-CVSS CVE with a public PoC may be exploited because the attacker's expected return exceeds cost.

**Game-theoretic framing:**

1. **Attacker's decision**: exploit this target vs. exploit alternatives.
   - Exploit if: V_target × p_exploit > cost_of_exploit + opportunity_cost_of_alternatives.
2. **Defender's decision**: patch vs. accept.
   - Patch if: cost_of_patch < V_asset × (p_exploit − p_exploit_post_patch) × probability_attacker_rational_and_motivated.

**Five-question filter (R2)** operationalizes this. The key variables are:
- Asset value (breach cost, including regulatory, reputational, operational)
- Attacker motivation class (opportunistic vs. targeted)
- Exploit accessibility (public PoC, weaponized kit, or manual research required)
- Compensating control effectiveness
- Time sensitivity of the patch window

**Reference.** Gordon-Loeb model (2002) — see P5 for the investment variant. Sandler & Arce terrorism survey on attacker cost-benefit.

---

### P4 — Vulnerability Disclosure as Signaling Game

**Problem.** When a vendor or researcher discloses a vulnerability, what signal does the timing and form of disclosure send? How should a defender reason about disclosures from third parties?

**Model.** Signaling game (Spence). The disclosing party has private information about severity. The market (users, defenders) updates their beliefs based on the signal (timing, detail level, patch readiness). Cheap-talk disclosure without patch is a weak signal; coordinated disclosure with patch is a strong credible signal.

**Key implications for defenders:**

1. **Receiving a disclosure without a patch**: treat as a stronger threat signal than the CVSS score alone — the disclosing party had incentive to wait for patch but chose not to.
2. **Unverified third-party claims**: disclosures with no CVE, no PoC, and no vendor acknowledgment are cheap talk. Weight accordingly.
3. **Race conditions**: once a PoC is public, attacker cost drops sharply. The equilibrium shifts — the rational defender must patch faster than attacker deployment.
4. **Internal disclosure**: when your own team finds a bug, the signaling game reverses — disclosure delay creates liability if an external party finds it simultaneously.

**Primitive link.** Per-claim credibility scoring (#14) maps directly to evaluating third-party disclosure quality.

---

### P5 — Security Investment Under Uncertainty (Gordon-Loeb Model)

**Problem.** How much should the security budget be? What is the optimal total spend on information security?

**Model.** Gordon-Loeb (2002). The optimal security investment is a function of breach probability and breach cost. Key result: the optimal spend is at most 37% of the expected loss (1/e of expected loss). Spending more than this exhibits diminishing returns that outweigh the risk reduction.

**Extensions for practitioners:**

1. **Attacker-aware Gordon-Loeb**: original model assumes random threats. Replace the static breach probability with an attacker best-response function — breach probability is not fixed but responds to how much you invest relative to the attacker's cost.
2. **Portfolio application**: treat each asset class (auth, API, supply chain, data store) as a separate Gordon-Loeb calculation. Budget allocation across classes should maximize total expected loss reduction.
3. **Marginal dollar rule**: invest the next dollar where the slope of the loss-reduction curve is steepest — i.e., in the asset class with highest V_i × ∂p_i/∂budget_i.

**Caution.** Gordon-Loeb assumes independence of attack events. Correlated attacks (a single exploit hitting multiple assets) require a modified model. The 37% heuristic is an upper bound, not a target.

**Reference.** Gordon & Loeb, "The Economics of Information Security Investment," ACM TISSEC, 2002.

---

## Anti-Pattern Catalog

### A1 — Static Defense (No Randomization)

**Description.** Security controls are fixed and predictable: the same firewall rules, the same WAF thresholds, the same credential rotation schedule, published or inferrable by a persistent attacker.

**Game theory diagnosis.** Pure strategy equilibrium is exploitable. A rational attacker observing a deterministic defense can route around it at zero additional cost.

**How it manifests.** WAF rules that only block known signatures. Penetration tests run on a fixed annual schedule. Honeypots that are statically named and location-stable. Monitoring thresholds that never change.

**Fix.** Move to mixed strategies: randomize scan schedules, rotate honeypot naming and placement, vary response thresholds. The attacker's expected exploitation cost rises because they cannot rely on the defense being absent at a predictable time. See P1 (Stackelberg).

---

### A2 — Equal-Spread Budget (Tambe's Anti-Pattern)

**Description.** Security budget is distributed evenly across all assets — equal investment in authentication, logging, API security, supply-chain controls, and data stores regardless of asset value or attacker preference.

**Game theory diagnosis.** Uniform allocation is never optimal in a Stackelberg game unless all assets have equal value and equal exploit cost. In practice, attacker attention is concentrated on high-value, low-cost targets. Equal spread over-invests in low-value assets and under-invests where the attacker actually looks.

**How it manifests.** Compliance-driven checklists that require equal coverage. Security programs with identical control intensity across all microservices. Budget negotiations that defend every line item equally rather than prioritizing by attacker payoff.

**Fix.** Run P1 (Stackelberg allocation) or at minimum apply the Gordon-Loeb marginal rule: next dollar goes to the highest V_i × ∂p_i/∂budget_i asset.

---

### A3 — Deterministic Honeypots

**Description.** Honeypots are placed once, named consistently (e.g., `admin-old`, `backup-db`), and never rotated. Their network positions and naming patterns are stable.

**Game theory diagnosis.** A rational attacker learns to avoid static deception assets after the first encounter. The honeypot yields high early detection but zero long-term detection value as attacker knowledge propagates. Against a sufficiently persistent attacker, static honeypots become a false-confidence signal.

**How it manifests.** Canary tokens placed in the same directory for years. Fake credentials with the same username prefix pattern. Honeypot IPs in a stable subnet range that the attacker's recon has already flagged as traps.

**Fix.** Rotate naming, placement, and appearance on a schedule that is unpredictable to the attacker but manageable for the defender. Use attacker best-response reasoning (P2) to place new honeypots in locations where an updated attacker model would search next.

---

### A4 — Compliance Theatre

**Description.** Security investments are allocated to satisfy audit requirements rather than to reduce attacker payoff. Controls are designed and documented for the auditor, not sized for the threat.

**Game theory diagnosis.** Auditors are not the adversary. Designing for the audit maximizes compliance score, not expected loss reduction. The attacker does not read the audit report; they probe the actual control surface. Compliance theatre creates a systematic gap between documented controls and actual attacker deterrence.

**How it manifests.** Purchasing a WAF and tuning it for zero findings during the audit window, then leaving thresholds loose. Logging everything to satisfy a log-retention requirement but building no alerts. Security training completed annually for compliance rather than timed to threat campaigns.

**Fix.** Run the Stackelberg allocation (P1) alongside the compliance mapping. Ensure that controls that satisfy audit also rank well on attacker-payoff reduction. Flag controls that only satisfy audit (compliance value > security value) as candidates for reallocation.

---

## Recipe Catalog

### R1 — Allocate a Hardening Budget Across N Assets Using Stackelberg

**When to use.** You have a finite hardening budget (sprint capacity, tooling spend, pen-test scope) to allocate across N assets or control areas.

**Inputs required.**

| Input | Description |
|-------|-------------|
| Asset list | N assets with estimated breach cost V_i |
| Base vulnerability | Estimated exploit probability p_i without additional control |
| Hardening effectiveness | How much does one unit of budget reduce p_i for each asset? Call this e_i |
| Total budget | B units (time, spend, or abstract) |

**Steps.**

1. Compute expected loss per asset: L_i = V_i × p_i.
2. Compute marginal value of hardening per asset: M_i = V_i × p_i × e_i (loss reduction per unit of budget).
3. Rank assets by M_i descending. Allocate budget greedily to the highest-M_i assets until B is exhausted.
4. Sanity check: does the top asset receive disproportionate share? If yes, it is the correct answer — that is where the attacker looks. Resist the urge to spread.
5. Re-run quarterly or when a new CVE, architectural change, or threat intel update changes V_i or p_i.

**Output.** A ranked allocation table: asset, V_i, p_i, e_i, budget_share, expected loss before/after.

**Mechanism design link.** Use mechanism-design synthesis (#7) to aggregate estimates from security engineer, threat intel analyst, and product owner before running step 1. Contested asset values go to a reasoning-tree audit before proceeding.

---

### R2 — Decide Patch-Now vs. Accept-Risk in 5 Questions

**When to use.** A CVE or internal finding requires a patch/no-patch decision. Standard CVSS scoring gives a number but not a decision.

**Five questions (answer each; decision follows).**

1. **Asset value**: Is the affected asset high-value (customer PII, payment flow, auth system, admin surface)? If yes, lower your risk tolerance.
2. **Attacker motivation class**: Is there evidence of targeted attacker interest (threat intel, industry sector campaigns, public PoC)? If yes, treat p_exploit as attacker-rational, not base-rate.
3. **Exploit accessibility**: Is there a weaponized PoC or kit available publicly? If yes, attacker cost is low — p_exploit rises sharply.
4. **Compensating controls**: Does an existing control (WAF rule, network segmentation, auth layer) meaningfully reduce p_exploit? If yes, defer may be viable.
5. **Patch cost vs. window**: Is the patch straightforward, or does it require extensive regression testing? How long is the exposure window if deferred?

**Decision matrix.**

| Questions with "risk-raising" answer | Recommendation |
|--------------------------------------|---------------|
| 4–5 | Patch immediately (P0) |
| 3 | Patch this sprint or apply compensating control within 48 hours |
| 2 | Patch in normal SLA; track in vulnerability backlog |
| 0–1 | Accept risk; document reasoning; revisit if threat landscape changes |

**Key principle.** The decision is not about CVSS score in isolation — it is about whether a rational attacker's best-response to your asset value and exploit accessibility makes exploitation more likely than your compensating controls can absorb.

---

### R3 — Place Honeypots so Attacker Payoff Is Minimized

**When to use.** You are deploying deception assets (honeypots, canary tokens, fake credentials, synthetic endpoints) and want placement to maximize detection probability against a rational attacker.

**Steps.**

1. **Model attacker prior**: where does a rational attacker expect high-value assets? Common priors: admin interfaces, credential stores, backup paths, high-traffic API endpoints.
2. **Identify probe order**: a rational attacker probes in order of expected value. Map the top-10 probe targets.
3. **Insert honeypots in the probe path**: place deception assets at positions 2, 4, and 6 in the probe order (not position 1 — the attacker expects obvious traps at the most obvious location).
4. **Make them indistinguishable**: honeypot credentials should have realistic age, usage history, and naming. Fake endpoints should return plausible but slightly slow responses. Canary tokens should appear in files that a credential thief would plausibly access.
5. **Alert on first touch**: honeypot activity is a high-confidence signal — no legitimate user should reach a well-placed honeypot. First touch triggers incident response, not just logging.
6. **Rotate quarterly**: update naming, placement, and appearance. Assume a persistent attacker updates their attacker model after each campaign.

**Output.** A deception deployment map: honeypot type, placement rationale (which probe order position), naming convention, rotation schedule, and alert linkage.

**Adversarial debate link.** Before finalizing placement, run an attacker-mindset agent (#2) against the proposed map. If the attacker agent skips all honeypots in simulation, redesign before deployment.

---

## Canonical Primitives Used

| Primitive | Where Applied |
|-----------|--------------|
| [#7 Mechanism Design for Synthesis](../../foundations-game-theory/assets/templates/game-theory/07-mechanism-design-synthesis.md) | Aggregating contested asset-value estimates before budget allocation (R1, P1) |
| [#6 Cooperation and Defection](../../foundations-game-theory/assets/templates/game-theory/06-cooperation-defection.md) | Modeling attacker incentive structure in patch decisions (P3); disclosure game equilibria (P4) |
| [#2 Adversarial Debate](../../foundations-game-theory/assets/templates/game-theory/02-adversarial-debate.md) | Stress-testing honeypot placement and hardening decisions (P2, R3) |
| [#14 Per-Claim Credibility Scoring](../../foundations-game-theory/assets/templates/game-theory/14-credibility-scoring.md) | Evaluating third-party vulnerability disclosure quality (P4) |

Full primitive library: [`foundations-game-theory/SKILL.md`](../../foundations-game-theory/SKILL.md).

---

## Sources

- Tambe, M. (ed.). _Security and Game Theory: Algorithms, Deployed Systems, Lessons Learned_. Cambridge University Press, 2011. Covers ARMOR (LAX), IRIS (port security), and Stackelberg security game formalism.
- Gordon, L. A., & Loeb, M. P. "The Economics of Information Security Investment." _ACM Transactions on Information and System Security_, 5(4), 438–457, 2002. Original Gordon-Loeb model with the 37% result.
- Sandler, T., & Arce, D. G. "Terrorism and Game Theory." _Simulation & Gaming_, 34(3), 319–337, 2003. Survey of attacker cost-benefit reasoning applicable to AppSec adversary modeling.
- CISA / MITRE. _Adversary Emulation Plans_ and ATT&CK Evaluations. [https://attackevals.mitre-engenuity.org/](https://attackevals.mitre-engenuity.org/) and [https://www.cisa.gov/](https://www.cisa.gov/). Operationalized attacker behavior patterns that ground the attacker-prior models in P2 and R3. Last verified 2026-05-02.
- Albanese, M., Jajodia, S., & Noel, S. "Time-efficient and cost-effective network hardening using attack graphs." In _DSN 2012_. Honeypot placement and network deception formalization.
- Laszka, A., Felegyhazi, M., & Buttyan, L. "A survey of interdependent information security games." _ACM Computing Surveys_, 47(2), 2014. Comprehensive survey of security games including signaling, deception, and investment models.
