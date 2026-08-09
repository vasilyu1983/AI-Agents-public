# Grounding & Communication — Formal Theory Map


Use this file when a task needs source-level justification, production boundaries, or a clean bridge from classical grounding theory to modern LLM-agent handoffs.

## Table of Contents

- [Canonical Stack](#canonical-stack)
- [Primitive-To-Source Map](#primitive-to-source-map)
- [Production Boundary](#production-boundary)
- [Application Layer Status](#application-layer-status)
- [Do Not Overclaim](#do-not-overclaim)

---

## Canonical Stack

| Layer | Primary sources | Use |
|---|---|---|
| Common ground and grounding criterion | Clark & Brennan (1991), Clark (1996), Clark & Schaefer (1989) | Define what it means for a contribution to be grounded enough for current purposes |
| Contributions and joint action | Clark & Schaefer (1989), Clark (1996) | Treat handoffs as presentation plus acceptance, not one-way message delivery |
| Repair | Schegloff, Jefferson, and Sacks (1977) | Design clarification and correction channels |
| Presupposition and pragmatics | Grice (1975), Stalnaker (1974), Sperber & Wilson (1986/1995) | Identify unstated assumptions and implied meaning |
| Audience design | Bell (1984), Clark & Murphy (1982), Brennan & Clark (1996) | Adapt briefs to the recipient's context and vocabulary |
| Formal common knowledge | Lewis (1969), Aumann (1976) | Model mutual belief when exact recursion matters |
| Computational grounding | Traum (1994) | Translate grounding moves into dialogue-state machinery |
| LLM multi-agent failures | Cemri et al. (2025) MAST | Map specification, context-loss, and inter-agent failures to handoff design |

## Primitive-To-Source Map

| Primitive | Source authority | Production use |
|---|---|---|
| Common Ground | Clark & Brennan; Clark; Aumann; Lewis | Verify what is mutual, not merely present in context |
| Grounding Criterion | Clark & Schaefer; Clark & Brennan | Scale confirmation to task stakes |
| Presentation + Acceptance | Clark & Schaefer | Require explicit acceptance before expensive or irreversible work |
| Evidence of Understanding | Clark & Brennan | Prefer demonstration over "ack" for high-stakes work |
| Repair | Schegloff et al.; Traum | Provide low-friction clarification and correction paths |
| Presupposition | Stalnaker; Grice | Resolve "the file", "it", and domain shorthand before handoff |
| Audience Design | Bell; Clark & Murphy; Brennan & Clark | Write for the actual recipient's tools, context, and vocabulary |
| Joint Commitment | Clark | Assign responsibility to both sender and recipient |
| Least Collaborative Effort | Clark & Wilkes-Gibbs; Clark | Minimize joint cost, not sender tokens |
| Grounding Cost / Tracks | Clark & Brennan | Price acceptance, repair, reviewability, and latency by medium |

## Production Boundary

Use grounding theory to improve communication protocol design. Do not treat it as a proof that a model understood the task. Production systems still need:

- deterministic checks for file, schema, permission, and side-effect boundaries
- trace capture for prompts, acceptances, repairs, and final actions
- escalation rules for ambiguity, irreversible actions, and user-visible sends
- regression tests for high-frequency handoff templates
- local measurement of failure rates before adopting MAST percentages as priors

## Application Layer Status

The stable layer is classical and low-drift. The application layer is high-drift: MAST v3 (last revised Oct 2025; accepted NeurIPS 2025 Datasets & Benchmarks Track) reports 1,600+ traces, 14 failure modes, and three broad categories: system design issues, inter-agent misalignment, and task verification. Emerging 2026 practitioner and research work on agent coordination layers and orchestration tracing points the same direction — message protocol, communication topology, and stopping/aggregation decisions should be explicit design surfaces, not improvised natural-language side effects — but treat this as directional signal, not a specific benchmarked result, until a citable source is added to `data/sources.json`.

## Do Not Overclaim

- Do not claim acceptance proves correctness; it proves understanding to a criterion.
- Do not claim common ground exists because a prompt contained the relevant text.
- Do not hard-code MAST percentages into policy without rerunning local trace analysis.
- Do not use grounding theory for incentive conflicts; switch to game theory when payoffs diverge.
