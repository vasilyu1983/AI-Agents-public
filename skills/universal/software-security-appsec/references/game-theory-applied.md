---
description: Prioritize AppSec controls, patch decisions and deception using explicit attacker and defender assumptions.
status: stable
primitives:
  - foundations-game-theory/assets/templates/game-theory/07-mechanism-design-synthesis.md
  - foundations-team-theory/assets/templates/team-theory/02-adversarial-debate.md
---

# Game Theory Applied — AppSec Defender Design

Use when control choices change an attacker's incentives or when several defenders' investments affect one another. Check [foundations-game-theory's application gate](../../foundations-game-theory/SKILL.md#when-to-apply) first. For testing schedules and coverage, use [qa-security-testing's counterpart](../../qa-security-testing/references/game-theory-applied.md).

## Allocate a Hardening Budget

Treat attacker response as an assumption to test, rather than assuming every attacker is fully rational or informed. Opportunistic scanning, automated exploitation and shared compromise paths can defeat a simple single-target model.

1. Enumerate reachable assets, plausible attack paths, loss consequences and the controls already in place. Separate attacker payoff from defender loss.
2. Estimate control cost and marginal loss reduction as ranges. State uncertainty and correlated failures; a shared identity provider or build pipeline can connect several assets.
3. Compare feasible allocations under several attacker-response scenarios. For a fixed-threat approximation, minimize total residual loss subject to the budget, or maximize loss reduction. Do not maximize residual loss.
4. If modeling a Stackelberg game, specify attacker payoffs, observability and best responses to each defender strategy. A greedy ranking of static risk scores is a prioritization heuristic, not a solved Stackelberg equilibrium.
5. Record the chosen controls, displaced alternatives, assumptions and sensitivity to different attacker responses. Revisit after a material architecture or threat change.

Randomized coverage can help where a scarce inspection or patrol resource leaves predictable gaps. It is not a reason to randomize mandatory authentication, authorization, patching or baseline monitoring. Uniform allocation and deterministic defenses can be appropriate; neither is universally dominated.

Output a table of asset/path, control, cost range, residual loss range, dependencies, chosen allocation and uncertainty. Use [mechanism-design synthesis](../../foundations-game-theory/assets/templates/game-theory/07-mechanism-design-synthesis.md) when teams disagree about estimates.

## Decide Patch Now, Mitigate or Defer

Evaluate these dimensions separately; a count of answers is not a validated urgency score:

- Reachability and actual exploit preconditions, including exposure and privilege.
- Exploitation evidence, weaponization and affected versions; check vendor advisories and relevant exploited-vulnerability catalogs.
- Business impact, legal deadlines and required remediation policy.
- Compensating control effectiveness, coverage and evidence.
- Patch regression cost and the duration of exposure if delayed.

Escalate confirmed exploitation or a reachable severe compromise path using the incident process. Otherwise compare patching, temporary containment and an explicitly time-bounded deferral. Assign an owner and review trigger. Absence of targeted interest does not make a vulnerable small organization safe, and absence of a CVE or public proof does not invalidate a well-evidenced private disclosure.

Output the action, evidence, remaining exposure, owner, deadline and verification plan. Do not infer a universal patch deadline from a game-theory paper.

## Place and Evaluate Deception Assets

Choose decoys from an evidenced attacker path, such as credential collection or administrative discovery. Proximity to a valuable asset is a hypothesis to evaluate, not a theorem that guarantees detection.

1. Select a path and define what decoy interaction would indicate. Use threat reports and MITRE behavior mappings to inform the hypothesis.
2. Use inert synthetic credentials or isolated endpoints; prevent decoys from authorizing access to production resources or collecting unnecessary user data.
3. Establish benign access sources, alert ownership and response handling before deployment. A legitimate scanner or administrator may touch a decoy.
4. Validate detection in an authorized isolated exercise. Compare placements against the observed paths; do not prescribe numbered probe positions or claim optimality without a model and evidence.
5. Change appearance or placement when recognition reduces value, while preserving monitoring and the response runbook.

Use [adversarial debate](../../foundations-team-theory/assets/templates/team-theory/02-adversarial-debate.md) to challenge assumptions. An agent's simulated reaction is design feedback, not measured attacker behavior.

## Security Investment and Disclosure

Gordon–Loeb is a model of investment under specified breach-loss and protection assumptions. Use estimated loss curves and marginal cost to compare controls; do not apply an unconditional percentage cap to a real security budget. A numerical investment cap is unverified here; apply no unconditional cap.

For disclosure, judge reproductions, code paths, affected versions, reachability and vendor response. Patch availability and disclosure timing add context but do not reliably establish severity or credibility by themselves. Coordinate handling according to the vulnerability process.

For interdependent defenders, examine incentives to underinvest or rely on another party's controls. The Laszka survey addresses that setting; it explicitly excludes two-player attacker–defender games, so it is not evidence of optimal honeypot placement.

## Source Scope

The operational steps above are design heuristics; none supplies a measured effectiveness guarantee.

- [Tambe, Security and Game Theory (Cambridge, 2011)](https://www.cambridge.org/core/books/security-and-game-theory/702C9C4650502EFE4652BB90CE3B8828): publisher description/contents support resource allocation and randomized schedules. ARMOR concerns LAX; IRIS concerns Federal Air Marshals, not port security. Chapter-level results were not checked.
- [Gordon & Loeb, The Economics of Information Security Investment (2002)](https://dl.acm.org/doi/10.1145/581271.581274): publisher full text unavailable, unverified. [Coauthor's institutional summary](https://www.rhsmith.umd.edu/directory/martin-p-loeb) confirms the model's subject but does not verify a numerical bound.
- [Sandler & Arce, Terrorism & Game Theory (2003)](https://journals.sagepub.com/doi/10.1177/1046878103255492): publisher abstract describes strategic terrorism-policy analysis. Applying it to AppSec is an analogy, not a validated patch-decision rule.
- [MITRE ATT&CK Adversary Emulation Plans](https://attack.mitre.org/resources/adversary-emulation-plans/): prototype behavior mappings derived from public threat reports, with stated limitations; not a formal deception-placement model.
- [Laszka, Felegyhazi & Buttyán, A Survey of Interdependent Security Games](https://aronlaszka.com/papers/laszka2012survey.pdf): author-hosted working paper revised in 2014 and identified as accepted to ACM Computing Surveys. Its abstract concerns interdependent defenders; the publisher version was not fetched.

Per-entry verification scope and dates live in [data/sources.json](../data/sources.json).
