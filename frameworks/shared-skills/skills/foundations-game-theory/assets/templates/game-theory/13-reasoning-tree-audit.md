# Mechanism: Reasoning-Tree Audit (AgentAuditor + ACPO)

**Source**: AgentAuditor — *Auditing Multi-Agent LLM Reasoning Trees Outperforms Majority Vote and LLM-as-Judge* ([arxiv 2602.09341](https://arxiv.org/abs/2602.09341), Feb 2026). +5pp absolute accuracy over majority vote, +3pp over LLM-as-judge.

## Domain Applications

- **Compliance and audit review**: multiple reviewers produce reasoning chains on the same regulatory question; audit traces each chain to its evidence at the First Point of Disagreement; picks best-supported, not most-popular answer.
- **Medical diagnosis synthesis**: multiple clinical opinions; reasoning-tree audit traces each to primary evidence (labs, imaging, literature); identifies divergence points without relying on senior-clinician authority.
- **Security incident analysis**: multiple analysts produce incident hypotheses; audit traces each to observable indicators; rejects majority consensus if evidence trail is weak.
- **Agent team synthesis**: the primary use case — replaces majority voting with evidence-grounded synthesis; +5pp accuracy over majority vote per AgentAuditor benchmark.

## Problem

Majority voting and LLM-as-judge synthesis both fail in the same way: when members share training biases, the majority converges on a confident-but-wrong answer, and a single judge is fooled by the consensus narrative. The minority answer is often correct but invisible at synthesis time.

This mechanism replaces voting with a **structured branch audit**: build a reasoning tree across member traces, locate the First Point of Disagreement (FPD), and pick a child branch by evidence — not by who else agrees with it.

## Concept

```
1. Build the reasoning tree:
     - Root = the question
     - Each member's trace becomes a path from root → leaf (their answer)
     - Where two paths share early reasoning then split → mark the split as a divergence node

2. Locate the FPD (First Point of Disagreement):
     - The earliest divergence node where the team's traces fork
     - Everything above the FPD is shared context; everything below is contested

3. Extract the divergence packet at the FPD:
     - Shared context (above the FPD) — common ground, no audit needed
     - For each child branch: short evidence summary + claim made + members on this branch

4. Adjudicate locally at the FPD:
     - Compare evidence on each branch, not branch popularity
     - Pick the branch whose evidence best supports the question, even if it's the minority branch
     - If two branches have comparable evidence, recurse into each subtree's next FPD

5. Output the chosen leaf as the decision, plus the audit trail
```

The audit is local — the synthesis owner never has to compare full traces, only branch evidence at each split. This is what makes it tractable at scale.

## Anti-Consensus Preference Optimization (ACPO)

ACPO is the training-time companion: train the adjudicator on **majority-failure cases** — datasets where the popular answer was wrong and the minority answer was right. Reward picking the evidence-backed minority over the popular error.

You can apply this even without retraining: at synthesis time, the orchestrator's prompt explicitly states **"prefer the minority branch when its evidence is stronger; popularity is not evidence."** This is the prompt-level proxy for ACPO when fine-tuning isn't available.

## Implementation

### Synthesis owner prompt addition

```
SYNTHESIS PROTOCOL: Reasoning-tree audit.

1. From each member's output, extract: claim + evidence + reasoning chain.
2. Identify the First Point of Disagreement — the earliest step where reasoning forks.
3. At each FPD, compare evidence on each branch directly.
   - Pick the evidence-backed branch even if it's a minority position.
   - Popularity is not evidence. Two members agreeing without independent evidence
     count as one branch, not two.
4. Recurse into the chosen subtree until you reach a leaf claim.
5. Report:
   - Final decision
   - The FPD (where the team split)
   - Why this branch's evidence beat the alternative
   - The minority branch (preserved as dissenting view, not deleted)
```

### When the team has 4+ members

Multi-way disagreements are common. Group members by branch at each FPD, then audit branches — not individuals. Three members agreeing because they cite the same source = one branch's evidence weight, not three.

## When To Use

- High-stakes decisions where the cost of confident wrongness is high
- Teams with heterogeneous specializations (the conditions where minority correctness is most likely)
- Any team currently using majority voting at synthesis

Layer on top of any team with `synthesis_owner: parent-thread` or similar — this is a synthesis-protocol upgrade, not a team-shape change.

## When NOT To Use

- Trivial questions with broad agreement (overhead not justified)
- Teams of homogeneous models — there's no real branching, just shared error
- Pure-research teams producing parallel artifacts that don't conflict (no synthesis step)

## Graph-of-Thoughts Extension — When the Reasoning Isn't a Tree

Sources: *Graph of Thoughts* (arxiv 2305.10601 lineage, GoT-style aggregation), *Framework of Thoughts* (FoT, arxiv 2602.16512).

Tree-shape assumption breaks when members **converge** on shared sub-claims after diverging. Two debaters who started apart may both arrive at "we need a feature flag" via different paths. A tree audit treats these as two independent leaves; the team has actually formed a **graph** with a shared sink node.

Switch from tree to graph audit when:

- A member's reasoning explicitly **references another member's sub-claim** (cross-citation).
- Two members produce **lexically different but semantically identical** sub-conclusions (use RCS / G19 to detect — high cosine similarity at non-adjacent leaves).
- The team uses **multi-round debate** where round-2 arguments depend on round-1 outputs from peers.

Graph audit protocol:

```text
1. Build the reasoning graph: nodes = sub-claims, edges = "supports" or "depends-on".
2. Find merge nodes — sub-claims that 2+ paths converge on.
3. At each merge: audit the supporting evidence from all paths feeding in.
   A merge node with 3 weak paths feeding in is weaker than one with 1 strong path.
4. At each split: run the standard FPD audit.
5. Output: the path through the graph with strongest evidence at each merge AND split.
```

Graph audit costs more than tree audit (O(nodes + edges) vs O(leaves)). Default to tree; escalate to graph when cross-citation or semantic-merge signals appear.

FoT compatibility: if the team uses Framework-of-Thoughts orchestration, the graph is already built — reuse it directly instead of reconstructing.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Treating every member's trace as a separate branch | Group by branch — co-citing members are one branch's weight |
| Auditing the full traces instead of just the FPD | The FPD localizes the audit; full-trace comparison defeats the efficiency win |
| Discarding minority branches after adjudication | Always preserve the minority view as dissent — that's where future learning lives |
| Using ACPO prompts without examples of past majority failures | Provide 2-3 calibration examples in the launch prompt where the minority was right |

## Related

- [`02-adversarial-debate.md`](02-adversarial-debate.md) — debate produces the diverse traces; this mechanism adjudicates them
- [`07-mechanism-design-synthesis.md`](07-mechanism-design-synthesis.md) — incentive-compatible synthesis pairs naturally with reasoning-tree audit
- [`08-courtroom-proclaim.md`](08-courtroom-proclaim.md) — courtroom debate generates the evidence-rich traces this audit needs
- [`14-credibility-scoring.md`](14-credibility-scoring.md) — credibility scoring weights the evidence on each branch
