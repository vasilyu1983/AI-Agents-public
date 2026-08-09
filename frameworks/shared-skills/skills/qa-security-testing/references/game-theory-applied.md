---
description: Game-theory patterns for security testing scheduling and coverage — scan cadence, attacker-aware fuzz seed selection, red-team simulation as Stackelberg game, secrets-rotation testing, and breach-and-attack simulation.
last_verified: 2026-05-02
status: stable
primitives:
  - foundations-game-theory/assets/templates/game-theory/07-mechanism-design-synthesis.md
  - foundations-game-theory/assets/templates/game-theory/06-cooperation-defection.md
  - foundations-game-theory/assets/templates/game-theory/02-adversarial-debate.md
---

# Game Theory Applied — Security Testing Scheduling and Coverage

> **Gate before invoking:** Check [`foundations-game-theory` § When to Apply](../../foundations-game-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


> For the defender investment and hardening-design counterpart, see
> [`software-security-appsec/references/game-theory-applied.md`](../../software-security-appsec/references/game-theory-applied.md).

## Table of Contents

- [Why Game Theory for Security Testing](#why-game-theory-for-security-testing)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Scan Scheduling as a Security Game](#p1--scan-scheduling-as-a-security-game)
  - [P2 — Fuzz Seed Selection as Multi-Armed Bandit](#p2--fuzz-seed-selection-as-multi-armed-bandit)
  - [P3 — Red Team as Iterated Stackelberg Game](#p3--red-team-as-iterated-stackelberg-game)
  - [P4 — Dependency Scanning Frequency as Repeated Game](#p4--dependency-scanning-frequency-as-repeated-game)
  - [P5 — Breach-and-Attack Simulation as Best-Response Oracle](#p5--breach-and-attack-simulation-as-best-response-oracle)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Calendar-Driven Scans (Predictable to Attacker)](#a1--calendar-driven-scans-predictable-to-attacker)
  - [A2 — Coverage-as-Metric (Goodhart's Law)](#a2--coverage-as-metric-goodharts-law)
  - [A3 — Fuzz with No Feedback Loop](#a3--fuzz-with-no-feedback-loop)
  - [A4 — Red Team Without Scoring Rubric](#a4--red-team-without-scoring-rubric)
- [Recipe Catalog](#recipe-catalog)
  - [R1 — Schedule Scans so an Attacker Cannot Time Around Them](#r1--schedule-scans-so-an-attacker-cannot-time-around-them)
  - [R2 — Choose Between Random-Fuzz and Grammar-Fuzz with a Bandit](#r2--choose-between-random-fuzz-and-grammar-fuzz-with-a-bandit)
  - [R3 — Score a Red-Team Exercise so Iteration Improves Coverage](#r3--score-a-red-team-exercise-so-iteration-improves-coverage)
- [Canonical Primitives Used](#canonical-primitives-used)
- [Sources](#sources)

---

## Why Game Theory for Security Testing

Security testing is adversarial by nature — but most testing schedules are designed as if the attacker does not observe or react to the defender's test rhythm. A predictable scan schedule tells a patient attacker when the window is open; a static fuzz corpus tells a motivated attacker which code paths the defender has already mapped. The defender who ignores attacker best-response builds a testing program that is thorough against random bugs and blind to targeted exploitation.

Game theory corrects this by modeling:

1. **Attacker timing** — a rational attacker exploits the gap between scans; the defender's optimal schedule is one that minimizes predictable gaps.
2. **Exploration vs. exploitation in testing** — which code paths deserve more fuzz investment given current knowledge of vulnerability density?
3. **Red-team iteration** — each red-team engagement is a round of a game; scoring it well lets the defender improve between rounds rather than just collecting findings.
4. **Repeated games** — dependency scanning and secrets rotation are not one-shot decisions; the equilibrium depends on the ongoing cost-benefit calculation on both sides.

---

## Pattern Catalog

### P1 — Scan Scheduling as a Security Game

**Problem.** DAST and full SAST runs cannot run on every commit — they run on a schedule. A fixed schedule creates predictable windows where new code is unscanned. A rational attacker can time a malicious supply-chain contribution or a targeted commit to land in this window.

**Model.** Inspection game (Dresher, 1962 variant). Defender chooses scan times; attacker chooses attack times. Pure strategy Nash equilibrium does not exist — the defender who always scans on Monday and the attacker who always attacks on Tuesday can both profitably deviate. The mixed strategy equilibrium is for the defender to randomize scan timing within the constraint of acceptable CI latency.

**Operationalization:**

1. Determine the maximum acceptable scan interval (e.g., no more than 4 hours between full SAST runs on main).
2. Within that interval, randomize the exact trigger time: use jitter on scheduled scans rather than fixed cron expressions.
3. For DAST against staging: randomize staging deploy triggers and decouple scan start from deploy event by a random offset (15–90 minutes).
4. For dependency scans: use Dependabot or Renovate on a randomized daily window rather than a fixed time.

**Key insight.** The defender does not need to scan continuously — only unpredictably. The attacker's expected undetected window drops faster with unpredictability than with increased scan frequency at fixed times.

**Primitive link.** This pattern uses the inspection game structure, which is a special case of the Stackelberg security game in P3 of the appsec counterpart file.

---

### P2 — Fuzz Seed Selection as Multi-Armed Bandit

**Problem.** Fuzzing a codebase requires choosing which seed corpus to use and how to allocate fuzzing time across code paths. A random corpus wastes time on well-tested paths; a deterministic corpus based on past findings misses new attack vectors. Which code paths deserve more investment?

**Model.** Multi-armed bandit (Thompson sampling variant). Each code path or fuzz target is an arm. The reward is finding a new vulnerability class. The defender must balance exploitation (keep fuzzing paths where bugs have been found before — the same vulnerability class may have sibling instances) against exploration (try new paths where no bugs have been found but where the attacker might be looking).

**Operationalization:**

1. Assign each fuzz target a prior: paths with recent fixes, high complexity (cyclomatic), or external input surfaces start with elevated priors.
2. After each fuzzing session, update posteriors: a crash or new coverage edge raises the probability that this path is rewarding; a clean run with no new coverage lowers it.
3. Allocate the next fuzzing budget proportional to Thompson samples: sample from each target's posterior, allocate time to the highest-sampled targets.
4. Attacker-aware prior injection: if threat intel identifies a new exploitation technique (e.g., integer overflow in memory allocators), manually elevate priors for relevant code paths even if no prior bugs have been found there.

**Key insight.** Grammar-aware fuzzing (knowing the structure of valid inputs) reduces wasted mutations. Use grammar-fuzz for structured inputs (JSON, protobuf, XML parsers) and random-fuzz for unstructured binary inputs. Recipe R2 formalizes the choice.

**Reference.** Coverage-guided fuzzing (AFL++, LibFuzzer) uses feedback loops that approximate multi-armed bandit exploration. The game-theory framing adds the attacker dimension: which paths is a motivated attacker most likely to probe?

---

### P3 — Red Team as Iterated Stackelberg Game

**Problem.** A red-team exercise produces a report of findings. The blue team patches. Next year a new red team runs. Is the second engagement more valuable than the first? Usually not, because neither side has a framework for iterating strategically.

**Model.** Iterated Stackelberg game. The red team (attacker-follower in each round) observes the blue team's current defenses and best-responds. The blue team (defender-leader) observes the red team's findings and updates defenses. Each round is a new Stackelberg game with the blue team's updated strategy as the starting point.

**Operationalization:**

1. After each engagement, score the red team's coverage: which ATT&CK tactic families were tested? Which were not?
2. For the next engagement, the red team's brief explicitly requires coverage of tactics not tested in prior rounds. This is the blue team acting as Stackelberg leader — shaping the attacker's move space.
3. Track blue team response latency: how long does it take to patch findings from each engagement? This is the gap the next red team should target.
4. Score red team quality separately from finding count: a red team that finds 1 novel critical is more valuable than one that re-finds 10 known issues. See R3.

**Primitive link.** Adversarial debate (#2) maps directly to the red-team structure: attacker-mindset agent (red team) vs. defender-mindset agent (blue team), with findings going through reasoning-tree audit before remediation priority is set.

---

### P4 — Dependency Scanning Frequency as Repeated Game

**Problem.** How often should dependency scans run, and when should a new CVE in a dependency trigger immediate action vs. wait for the next scheduled scan?

**Model.** Repeated game with discounting. The defender and attacker interact over time. The defender's scan frequency determines how quickly they detect a new vulnerability. The attacker's decision to exploit depends on how quickly they expect the defender to detect and patch.

**Key equilibria:**

1. **High-frequency scan + fast patch SLA**: the attacker's exploitation window is narrow. For opportunistic attackers (who exploit before defenders patch), this raises their cost substantially. For targeted attackers, it depends on their patience.
2. **Low-frequency scan + slow SLA**: the attacker exploits in the gap. This is the dominant equilibrium when defenders treat dependency scanning as a compliance checkbox.
3. **Signal-triggered scans**: when a new CVE is published in a package you use, trigger an immediate out-of-band scan rather than waiting for the next scheduled run. This breaks the attacker's ability to time around a predictable scan window.

**Operationalization:**

1. Separate base-rate scanning (Dependabot daily) from signal-triggered scanning (CVE feed → webhook → immediate scan).
2. For signal-triggered scans: subscribe to OSS vulnerability feeds (GitHub Advisory, OSV, NVD) and trigger scan on new entries matching your dependency manifest.
3. Patch SLAs are part of the game: critical SLA of 24h only matters if the scan runs within that window. Align scan frequency to SLA commitments.

**Reference.** Gordon-Loeb extended to repeated games: each scan cycle is a one-shot investment with marginal value proportional to new vulnerability probability.

---

### P5 — Breach-and-Attack Simulation as Best-Response Oracle

**Problem.** BAS tools (Cymulate, AttackIQ, SafeBreach) run automated attack sequences against live or simulated environments. How should their results be interpreted and acted on?

**Model.** Best-response oracle. BAS is the attacker's best-response function made explicit: given your current controls, here are the attack paths that succeed. The value of BAS is not in the finding count but in the response surface — it tells the defender where the attacker's expected payoff is highest given the current defense state.

**Operationalization:**

1. Run BAS after each significant control change (new WAF rule, new EDR policy, new network segmentation). This measures how the best-response surface has shifted.
2. Prioritize findings by attacker expected payoff: a BAS finding that bypasses an auth control on a high-value asset ranks above one that succeeds against a low-value asset with no data.
3. Use BAS results to update the Stackelberg allocation (see appsec counterpart, P1): if BAS shows an unexpected successful attack path, it reveals a V_i or p_i estimate that was wrong.
4. BAS cadence: run after control changes, not on a fixed calendar — avoid the calendar-driven trap (A1 below).

**Primitive link.** Mechanism-design synthesis (#7) is useful for aggregating BAS results from multiple tools (red team manual + BAS automated) before prioritization. Dissent required when tools disagree on exploitability.

---

## Anti-Pattern Catalog

### A1 — Calendar-Driven Scans (Predictable to Attacker)

**Description.** Security scans run on a fixed cron: DAST every Monday at 02:00, full dependency review every first of the month, penetration test every Q4.

**Game theory diagnosis.** A fixed schedule is a pure strategy. Pure strategies in inspection games are exploitable by a rational attacker who times malicious contributions or attacks to land just after the scan window closes. The calendar announces the gap.

**How it manifests.** Developers know that the Monday DAST won't catch a Friday deploy. Supply-chain attackers time malicious package updates to post-scan windows. Annual pen tests create a 364-day gap.

**Fix.** Add jitter to all scheduled security scans. Supplement scheduled scans with signal-triggered scans (CVE feed, PR merge event, deploy event). See R1.

---

### A2 — Coverage-as-Metric (Goodhart's Law)

**Description.** "We have 90% SAST coverage" or "we scan all dependencies" becomes the success metric. Teams optimize for coverage percentage rather than for finding attacker-relevant vulnerabilities.

**Game theory diagnosis.** Goodhart's Law: when a measure becomes a target, it ceases to be a good measure. In the testing game, 90% coverage with low-signal rules is strictly worse than 60% coverage with high-signal rules tuned to the attacker's likely technique set. Coverage percentage is not correlated with attacker success probability.

**How it manifests.** Adding dozens of low-severity Semgrep rules to raise the finding count. Declaring all scanner findings triaged even when triage is superficial. Measuring DAST coverage by request count rather than by ATT&CK tactic coverage.

**Fix.** Replace coverage as the primary metric with attacker-tactic coverage: what fraction of the relevant ATT&CK tactic families are tested by current scanning? This aligns the metric with attacker best-response rather than with scan completeness.

---

### A3 — Fuzz with No Feedback Loop

**Description.** Fuzzing runs continuously with the same seed corpus and no mechanism to update which targets receive more time based on recent results.

**Game theory diagnosis.** Without a feedback loop, fuzzing is a static strategy. The attacker's technique set evolves (new memory safety attacks, new parser exploits); the defender's fuzz corpus does not. This is the equivalent of the "static defense" anti-pattern from the appsec file applied to testing.

**How it manifests.** AFL++ running 24/7 with no corpus rotation. LibFuzzer seeds never updated after initial corpus creation. No attacker-prior injection when new CVEs in the same vulnerability class appear.

**Fix.** Implement the multi-armed bandit update (P2). After each fuzzing period, update path posteriors based on crash and coverage signal. Inject elevated priors when threat intel identifies new relevant technique families.

---

### A4 — Red Team Without Scoring Rubric

**Description.** Red-team findings are reported as a list of vulnerabilities. The next engagement is scoped independently. No cross-engagement tracking of which tactic families have been tested and which have not.

**Game theory diagnosis.** Without a scoring rubric, red-team iteration does not converge. Each engagement is a one-shot game rather than a round in an iterated game. The blue team cannot tell whether defenses are improving against the most relevant attacker tactics.

**How it manifests.** Consecutive pen tests finding the same vulnerability classes because the scope never changes. Red-team reports that list findings without mapping to ATT&CK. Blue-team remediation that addresses individual findings but never updates the defense posture against the tactic family.

**Fix.** Score each engagement against ATT&CK tactic coverage (R3). Require the next engagement brief to explicitly cover tactics not tested in prior rounds. Track blue-team response latency per tactic family as the iteration improvement metric.

---

## Recipe Catalog

### R1 — Schedule Scans so an Attacker Cannot Time Around Them

**When to use.** You are designing or auditing a CI/CD security scanning schedule and want to ensure it does not create predictable exploitation windows.

**Steps.**

1. **Audit current schedule**: list all security scans with their current triggers (cron expression, deploy event, manual). Identify any fixed-time cron scans.
2. **Convert fixed crons to jittered crons**: replace `0 2 * * 1` (Monday 02:00) with a script that picks a random offset each week within a ±4-hour window. Most CI platforms support this natively or via a pre-step.
3. **Add signal-triggered scans**: subscribe to OSV/GitHub Advisory feed for your dependency manifest. On new relevant CVE: trigger dependency scan immediately, do not wait for the next scheduled run.
4. **Decouple DAST from deploy**: add a random 15–90 minute offset between staging deploy completion and DAST scan start. This prevents an attacker who can observe deploy events from timing a probe to land in the post-deploy pre-scan window.
5. **Verify unpredictability**: log scan start times for 30 days. If an attacker observing the log could predict the next scan within a 2-hour window, add more jitter.

**Output.** Updated scan schedule with jitter parameters, signal-trigger configuration, and a 30-day scan time log to verify unpredictability.

---

### R2 — Choose Between Random-Fuzz and Grammar-Fuzz with a Bandit

**When to use.** You are allocating fuzzing resources across multiple targets and deciding which fuzzing strategy to apply to each.

**Decision inputs.**

| Signal | Implication |
|--------|-------------|
| Structured input format (JSON, XML, protobuf, SQL) | Grammar-fuzz is likely more effective — random mutations produce syntactically invalid inputs that are rejected before reaching deep code paths |
| Unstructured binary input (image decoders, archive parsers, network protocols) | Random-fuzz with coverage guidance (AFL++) — structure is too complex to enumerate |
| Recent CVE in the same vulnerability class (e.g., integer overflow in a C parser) | Elevate prior for coverage-guided fuzz on the affected target regardless of input format |
| New code path with no prior fuzzing history | Start with random-fuzz to build initial coverage map; switch to grammar-fuzz if the format is known |
| Path with prior crashes or findings | Exploitation-first: allocate 2× budget to this target before exploring new paths |

**Bandit update rule (simplified Thompson sampling).**

For each fuzz target t:
- Prior: Beta(alpha_t, beta_t), where alpha = prior crash count + 1, beta = prior clean sessions + 1.
- After each session: if crash found, alpha_t += 1; else beta_t += 1.
- Next budget allocation: sample from each Beta distribution; allocate budget to targets with highest samples.

**Output.** A fuzz target priority list updated after each session, with grammar-fuzz vs. random-fuzz assignment per target.

---

### R3 — Score a Red-Team Exercise so Iteration Improves Coverage

**When to use.** Planning a red-team engagement brief or reviewing findings from a completed engagement.

**Scoring dimensions.**

| Dimension | How to Score |
|-----------|-------------|
| ATT&CK tactic coverage | Which of the 14 MITRE ATT&CK tactics were attempted? Score = tactics attempted / tactics relevant to your threat model |
| Novel finding rate | Findings not previously known / total findings. Low novel rate means the red team is re-finding known issues |
| Escalation depth | Furthest ATT&CK technique chain reached (e.g., Initial Access → Persistence → Lateral Movement = depth 3) |
| Blue team detection rate | What fraction of red team actions triggered a blue team alert? This is the detection coverage metric |
| Response latency | How long did it take blue team to detect and respond to detected actions? |

**Iteration protocol.**

1. After engagement N: record scores on all five dimensions. Identify the lowest-scoring tactic families.
2. Engagement N+1 brief: require explicit coverage of the lowest-scoring tactic families from engagement N.
3. Measure improvement: compare scores on same dimensions across engagements. The program is improving if novel finding rate stays above 40% and ATT&CK tactic coverage increases.
4. Mechanism-design synthesis for findings: aggregate red-team report with BAS tool results and SAST/DAST findings before setting remediation priority. Findings that appear in multiple sources get higher priority. Use reasoning-tree audit (#7) when sources disagree on exploitability.

**Output.** A cross-engagement scorecard with dimension trends, tactic coverage gaps, and explicit requirements for the next engagement brief.

---

## Canonical Primitives Used

| Primitive | Where Applied |
|-----------|--------------|
| [#7 Mechanism Design for Synthesis](../../foundations-game-theory/assets/templates/game-theory/07-mechanism-design-synthesis.md) | Aggregating BAS + manual red-team findings before prioritization (P5, R3); contested exploitability assessments |
| [#6 Cooperation and Defection](../../foundations-game-theory/assets/templates/game-theory/06-cooperation-defection.md) | Dependency scanning as repeated game — attacker and defender cost-benefit over time (P4) |
| [#2 Adversarial Debate](../../foundations-game-theory/assets/templates/game-theory/02-adversarial-debate.md) | Red-team structure: attacker-mindset vs. defender-mindset agents (P3, R3) |
| [#10 Evolutionary Coordination Search](../../foundations-game-theory/assets/templates/game-theory/10-alphaevolve.md) | Fuzz seed evolution: iterative corpus update based on coverage signal (P2, R2) |

Full primitive library: [`foundations-game-theory/SKILL.md`](../../foundations-game-theory/SKILL.md).

---

## Sources

- Tambe, M. (ed.). _Security and Game Theory: Algorithms, Deployed Systems, Lessons Learned_. Cambridge University Press, 2011. Stackelberg security game formalism; ARMOR and IRIS deployed systems.
- Sandler, T., & Arce, D. G. "Terrorism and Game Theory." _Simulation & Gaming_, 34(3), 319–337, 2003. Attacker cost-benefit and timing models applicable to exploitation window analysis.
- Gordon, L. A., & Loeb, M. P. "The Economics of Information Security Investment." _ACM TISSEC_, 5(4), 438–457, 2002. Repeated-game investment framing for dependency scanning cadence (P4).
- CISA / MITRE ATT&CK Evaluations. _Adversary Emulation Plans_. [https://attackevals.mitre-engenuity.org/](https://attackevals.mitre-engenuity.org/). ATT&CK tactic coverage framework used in red-team scoring (R3). Last verified 2026-05-02.
- MITRE ATT&CK Framework. [https://attack.mitre.org/](https://attack.mitre.org/). Canonical tactic and technique taxonomy for red-team coverage scoring. Last verified 2026-05-02.
- Zalewski, M. _Fuzzing: Breaking Software in an Automated and Intelligent Way_ (AFL++ documentation and design notes). [https://aflplus.plus/](https://aflplus.plus/). Coverage-guided fuzzing feedback loop that approximates multi-armed bandit exploration (P2, R2). Last verified 2026-05-02.
- Dresher, M. _Games of Strategy: Theory and Applications_. RAND, 1961. Inspection game formalism underlying scan scheduling (P1).
