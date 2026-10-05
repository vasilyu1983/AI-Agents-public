# Method: Courtroom / PROClaim (Progressive Adversarial Deliberation)

## Purpose

Structure a debate as a courtroom trial with prosecution, defense, independent critic, and judicial panel. Evidence is not static — Progressive RAG dynamically retrieves new evidence during debate rounds, preventing stagnation. A role-switching consistency test after the primary debate surfaces whether reasoning was evidence-driven or position-anchored.

Based on PROClaim ([arxiv 2603.28488](https://arxiv.org/abs/2603.28488), 2026): reports accuracy gains over standard multi-agent debate on a claim-verification benchmark, with most of the gain attributed to Progressive RAG. PROClaim uses asymmetric retrieval — one query optimized to surface SUPPORTING evidence (for plaintiff) and another for CHALLENGING evidence (for defense) — to prevent the "echo chamber" effect of standard Top-K RAG.

## When To Use

- The question has a clear for/against structure (pricing change, feature kill, migration go/no-go)
- Evidence quality matters more than opinion diversity
- You need an audit trail for the decision (compliance, board, regulatory)
- Standard debate is converging too fast on an answer without sufficient evidence
- Claims or assumptions need rigorous adversarial verification
- LLM negativity bias is a concern (REFUTE positions converge 0.2-0.3 rounds faster than SUPPORT)

## When NOT To Use

- Creative exploration where there is no claim to verify (use Six Hats)
- Ongoing tension with no resolution (use Polarity Management)
- Low-stakes or easily reversible decisions (overhead not justified)
- Team members lack distinct domain expertise (heterogeneity is required)

## Roles

| Role | Job | Ideal agent |
|------|-----|-------------|
| **Plaintiff Counsel** | Argues FOR the claim/proposal. Builds case with evidence. | Domain specialist who benefits from the proposal |
| **Defense Counsel** | Argues AGAINST with evidence. Identifies weaknesses. | Domain specialist who would bear the risk or cost |
| **The Court** | Manages procedural flow, refines evidence queries | Orchestrator / lead / product-strategist |
| **Critic Agent** | Independently evaluates both sides. Not aligned with either. | Third-party reviewer (qa-test-reviewer, software-risk-reviewer) |
| **Judicial Panel** | Renders verdict. Ideally 3 heterogeneous perspectives for majority vote. | Synthesis owner + 2 additional perspectives, or lead synthesizes |

Mandatory rule: plaintiff and defense must use different specializations or model configurations. Homogeneous debaters share biases and produce correlated errors.

## Protocol

### Integration With Existing Debate Rounds

**Round 0 (setup)**: Court assigns plaintiff and defense roles. Announces the claim to be tested. Identifies the initial evidence pool.

**Round 1 (opening arguments)**:
- Plaintiff builds the case FOR with evidence citations
- Defense builds the case AGAINST with evidence citations
- Court identifies evidence gaps from both arguments
- Each side produces: position + reasoning chain + confidence + key evidence

**Round 1.5 (Progressive RAG)**:
- Court refines retrieval queries based on identified gaps
- New evidence retrieved, filtered by novelty score: `novelty(d) = 1 - max(cos(e_d, e_pool))`
- Evidence admitted only when `relevance × credibility > 0.5`
- Stops when: novelty < 0.20, redundancy ratio hit, or iteration cap (3 cycles)

**Round 2 (rebuttal with new evidence)**:
- Both sides respond to opposing arguments using newly retrieved evidence
- Must address the specific evidence, not just restate position
- Critic independently scores both sides on logic (0.4), novelty (0.3), rebuttal quality (0.3)

**Round 2.5 (role-switching consistency test)**:
- Plaintiff and defense swap positions
- Each argues the opposite case for one abbreviated round
- Analyzer flags: arguments that contradict original position, opportunistic evidence marshalling, position-anchored logic
- This diagnostic surfaces whether reasoning is genuinely evidence-driven

**Round 3 (verdict)**:
- Judicial panel (or synthesis owner) renders verdict via structured evaluation:
  - Evidence strength on each side
  - Reasoning quality on each side
  - Role-switching consistency result
  - Verdict with confidence level
  - Dissenting opinion (if panel is split)

## Launch Prompt

```text
DEBATE METHOD: Courtroom (PROClaim)

CLAIM TO TEST: [the specific claim, proposal, or decision]

PLAINTIFF (argues FOR): [agent name] — build the strongest case for the claim
DEFENSE (argues AGAINST): [agent name] — build the strongest case against
COURT (manages flow): [lead or orchestrator] — refine evidence queries, manage rounds
CRITIC (independent): [agent name] — evaluate both sides without alignment
JUDICIAL PANEL: [synthesis owner] — render verdict with dissent

EVIDENCE RULES:
- Both sides must cite specific evidence, not assertions
- Court refines retrieval queries after Round 1 to fill evidence gaps
- New evidence admitted only if novel (novelty > 0.20) and relevant (relevance × credibility > 0.5)

ROLE-SWITCHING: After Round 2, plaintiff and defense swap positions for one round.
Flag any argument that contradicts the agent's original position.

OUTPUT: Verdict + evidence summary + consistency test result + dissenting view
```

## Example: "Should we kill the free tier?"

```text
CLAIM: Removing the free tier will improve conversion and reduce support load without harming growth.

PLAINTIFF (startup-pricing-advisor): Argue FOR removing the free tier
  — cite conversion data, support cost, free-user LTV
DEFENSE (startup-growth-specialist): Argue AGAINST
  — cite viral loop dependency, top-of-funnel volume, competitive positioning
COURT (product-strategist): Manage rounds, refine evidence queries
CRITIC (marketing-product-analytics-lead): Evaluate both sides on data quality
JUDICIAL PANEL: product-strategist renders verdict

After Round 2: pricing-advisor argues FOR keeping the free tier,
growth-specialist argues FOR removing it. Flag inconsistencies.
```

## Key Findings From Research

- **Progressive RAG alone adds +7.5pp accuracy** — static evidence is the single biggest failure mode in standard debate
- **Role-switching catches -4.2pp of errors** — agents that flip positions inconsistently were using position-anchored reasoning
- **Three heterogeneous judges outperform a single judge by 3.3pp** — diverse synthesis prevents confident convergence on wrong answers
- **LLMs exhibit structural negativity bias** — REFUTE claims converge faster than SUPPORT claims. Be aware that "against" positions may reach false consensus faster.
- **Incorrect predictions display unstable reflection trajectories** — self-scoring consistency acts as a "logic lie detector"

## Variant: Post-Trained Adjudicator (DebateCV / Debate-SFT)

**Source**: *Debating Truth: Debate-driven Claim Verification with Multiple LLM Agents* ([arxiv 2507.19090](https://arxiv.org/html/2507.19090v4)).

If you have access to a moderator/adjudicator that has been fine-tuned on synthetic debate-adjudication data (Debate-SFT), the courtroom protocol simplifies:

- 2 debaters (plaintiff + defense), 1 fine-tuned moderator — no judicial panel needed
- Moderator weighs evidential strength directly without the heterogeneous-judge guardrail
- Skip Round 2.5 role-switching — the moderator's training implicitly handles position-anchoring detection

Use this variant only when you can verify the moderator was trained on debates similar to your domain. Without that fine-tune, fall back to the full PROClaim protocol with heterogeneous judges.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using the same model/specialization for plaintiff and defense | Use heterogeneous agents — shared biases produce correlated errors |
| Skipping Progressive RAG (using static evidence only) | Always refine evidence queries after Round 1 — this is the biggest accuracy lever |
| Skipping role-switching test | Always swap — it's the only way to detect position-anchored reasoning |
| Single judge instead of panel | Use 3 perspectives for judicial panel, or at minimum include the critic's independent assessment |
| Running courtroom on creative/exploratory questions | Courtroom needs a testable claim — use Six Hats for exploration |
