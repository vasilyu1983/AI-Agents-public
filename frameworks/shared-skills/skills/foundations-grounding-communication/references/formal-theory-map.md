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
| Dynamic (multi-turn) grounding | Yao, Zou, Hawkins (2026) | Separate one-shot interpretation from sustained joint plan formation and commitment |
| Protocol semantic layer | Yuan et al. (2026) | Decide what A2A/MCP-class transport gives you vs. what the application must build |

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

The stable layer is classical and low-drift. The application layer is high-drift: MAST v3 (last revised Oct 2025; accepted NeurIPS 2025 Datasets & Benchmarks Track) reports 1,600+ traces, 14 failure modes, and three broad categories: system design issues, inter-agent misalignment, and task verification.

The 2026 layer resolves what was previously directional signal here — that message protocol and coordination structure should be explicit design surfaces rather than improvised natural-language side effects — into citable work:

- **Protocol semantics** (`SemanticProtocols2026`, arXiv 2604.02369): 18 protocols surveyed against a communication / syntactic / semantic taxonomy. Most protocols provide limited protocol-level clarification, context alignment, and verification; semantic responsibilities land in prompts and orchestration logic. Confirms the grounding layer is application-owned today.
- **Dynamic grounding** (`DynamicGrounding2026`, arXiv 2605.01750): separates static (one-shot interpretation) from dynamic (multi-turn joint plan formation, commitment, execution) grounding, and shows the dyadic coordination gap is not explained by individual reasoning limits or information exchange volume.
- **Human-AI common ground** (`CommonGroundBench2026`, arXiv 2602.21337): a controlled Helper/Worker benchmark measuring grounding at task, object, and communication levels; finds AI collaborators do not show the cross-trial efficiency gains humans do, and fail to update assumptions after repair.
- **Conversational competence** (`NCBench2026`, arXiv 2601.06426): repair is the weakest measured competence class relative to plain answering.

All four are arXiv preprints as of 2026-08-14. Treat the *direction* as well-supported and the *numbers* as provisional.

## Do Not Overclaim

- Do not claim acceptance proves correctness; it proves understanding to a criterion.
- Do not claim common ground exists because a prompt contained the relevant text.
- Do not hard-code MAST percentages into policy without rerunning local trace analysis.
- Do not use grounding theory for incentive conflicts; switch to game theory when payoffs diverge.
- Do not treat a completed repair as a completed common-ground update; the correction can be acknowledged without the shared model moving (`CommonGroundBench2026`).
- Do not infer dynamic grounding ability from static benchmark scores. Agents that interpret a brief correctly in one shot still fail to sustain a joint plan across turns (`DynamicGrounding2026`).
- Do not treat a structured protocol payload (A2A, MCP, ACP) as evidence of shared interpretation; those layers standardize transport and schema, not meaning (`SemanticProtocols2026`).
