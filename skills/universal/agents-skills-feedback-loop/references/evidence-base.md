# Evidence Base — Maturity Grounding

Provenance for the maturity claims in this skill, the Layer 1 (auto-capture)
design, and the decision to keep promotion out a reviewed edit with no automated
gate. Graded with research-scout
discipline: research paper or venue = A (preprints are not evidence of peer review), primary vendor docs = B, vendor/trade blog
= C (pattern evidence only, never proof). The grades describe source type, not proven maturity. A vendor post or an open
research question cannot establish the absence of production practice; default-off
capture and reviewed promotion are repository design decisions.

The structured, machine-readable mirror of this list is `data/sources.json`
(same sources, same grades). Keep the source list and grades in sync.

## Sources

| Source | Grade | Grounds what |
|---|---|---|
| [Memory for Autonomous LLM Agents — arXiv 2603.07670](https://arxiv.org/abs/2603.07670) | A | Memory is a first-class agent discipline; names the open problems — continual consolidation, *trustworthy reflection*, learned forgetting — that justify keeping consolidation and promotion conservative. |
| [State of AI Agent Memory 2026 — mem0](https://mem0.ai/blog/state-of-ai-agent-memory-2026) | C | Vendor reports append-only ADD memory as production-ready (benchmark figures are the vendor's own; quote them from the post); **procedural memory (agent-driven self-capture/consolidation) is named explicitly as "early-stage" tooling, not production practice** — pattern evidence for the repository's conservative default, not proof of industry-wide maturity. |
| [Agentic Context Engineering (ACE) — arXiv 2510.04618, ICLR 2026](https://arxiv.org/abs/2510.04618) | A | A researched shape for Layer 2: evolving playbook via Generator/Reflector/Curator; "context collapse" and "brevity bias" are the failure modes structured incremental consolidation must avoid. |
| [ACE: evolving playbooks for self-improving agents — VentureBeat](https://venturebeat.com/ai/ace-prevents-context-collapse-with-evolving-playbooks-for-self-improving-ai) | C | Cross-source corroboration of ACE (independent of the paper); trade-press framing only. |
| [What Is the Learnings Loop — MindStudio](https://www.mindstudio.ai/blog/learnings-loop-claude-code-skills-self-improvement) | C | The base loop pattern this skill is explicitly borrowed from (see SKILL.md intro); pattern evidence, not validation. |
| [Testing Agent Skills Systematically with Evals — OpenAI](https://developers.openai.com/blog/eval-skills) | B | Establishes the eval *mechanics* this design borrows (prompt → captured run → checks → comparable score; "every manual fix is a signal, turn it into a test"). This page covers measurement, not gating — it does **not** describe threshold-based promotion or CI blocking; do not attribute a gate workflow to it. |
| [Agent observability complete guide 2026 — Braintrust](https://www.braintrust.dev/articles/agent-observability-complete-guide-2026) | C | Source for the production-failure → eval-case → CI-gate workflow ("blocks merges when a change degrades agent quality"); grounds the Promotion Out advice to add an eval case that fails when the moved rule is reverted. |
| [ICLR 2026 Workshop on Memory for LLM-Based Agentic Systems (MemAgents)](https://iclr.cc/virtual/2026/workshop/10000792) | A | Memory-for-agents is an active first-class research venue — the field is unsettled, which is why this skill keeps promotion human-reviewed. |
| [ECC (Everything Claude Code) — continuous-learning-v2, commit `51a6950`](https://github.com/affaan-m/ECC) | C (pattern evidence only, MIT-licensed source code, not a research or vendor-docs source) | Origin of the atomic confidence-scored "instinct" concept in `references/instinct-pattern.md` — a cross-cutting complement to this skill's per-skill loop. This repo does not adopt ECC's automatic project→global promotion (conflicts with the human-gate design above) or restate its "100% reliable" hook-capture claim as fact. |

## How this maps to the design

- **Layer 1 default-off** is repository policy. The survey names trustworthy
  reflection as an open challenge; that supports caution without proving that
  all autonomous self-capture is immature.
- **Layer 2 still manual** is repository policy. ACE demonstrates an automated
  reflection and curation method in its evaluated settings; effectiveness in
  this repository's per-skill files has not been measured.
- **Promotion out is a reviewed edit, not a gate script** ← OpenAI (eval
  mechanics) + Braintrust (the CI-block workflow). A separate promotion gate
  was built and dropped: across the wired library it produced no promotions,
  and it duplicated the eval tooling `agents-skills` already owns. The durable
  rule kept: a moved principle should come with an eval case that fails when
  it is reverted.

## Self-Evolving Skill Papers

| Source | Grade | Grounds what |
|---|---|---|
| [SkillOpt: Executive Strategy for Self-Evolving Agent Skills (arXiv 2605.23904)](https://arxiv.org/abs/2605.23904) | A | First systematic text-space optimizer for agent skills: a separate optimizer model turns scored rollouts into bounded add/delete/replace edits on a single skill document, accepting an edit only when it strictly improves a held-out validation score; the paper reports gains that differ by harness (quote the per-harness figures from the paper, never one flattened number). Principle: *the quality of the verifier bounds the quality of self-improvement*. |
| [CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification (arXiv 2604.01687; v1 was titled "EvoSkills")](https://arxiv.org/abs/2604.01687) | A | Co-evolutionary verification framework: Skill Generator + Surrogate Verifier without access to ground-truth test content. The paper reports a pass-rate gain on SkillsBench over a no-skill baseline; this repo has not reproduced it, so quote the figure from the paper with its benchmark, not from here. SkillOpt accepts edits only after held-out improvement; CoEvoSkills uses a co-evolving surrogate verifier. Both automate skill evolution with checks, rather than establishing a requirement for human review. |

**How these map to the design:**
- **Verify before accepting a skill edit** ← SkillOpt evaluates held-out improvement and CoEvoSkills uses surrogate feedback. This repo adopts reviewed edits and regression evidence as its own acceptance policy; it has not reproduced either method.
- **Auto-rewrite still not recommended for production markdown skills** ← SkillOpt evolves a single skill document and CoEvoSkills constructs multi-file packages. Neither paper establishes safety or effectiveness for this repository's unmeasured learnings workflow; human review remains repository policy.

## Caveats

- Grade-C vendor blogs (mem0, MindStudio, Braintrust) are PR-tinged. Their
  "wire it in an afternoon" / "learns from every run" framing is discounted;
  only their structural pattern descriptions are used.
- **MindStudio's actual "learnings loop" is the anti-pattern this skill forbids.**
  MindStudio's mechanism has Claude Code rewrite the skill's
  *persistent instructions themselves* from user corrections — i.e. autonomous
  `SKILL.md` self-modification. This design borrows only the name and the
  "accumulate corrections over sessions" shape; it deliberately inverts
  MindStudio's core move (auto-rewrite) into a human-gated one (append raw,
  consolidate by review, move rules out only by reviewed edit). Do not cite
  MindStudio as evidence that auto-rewriting `SKILL.md` is safe — it is evidence
  of the opposite pattern's existence in the wild, not of its safety.
- ACE's headline gains are the method's own claims; transfer to
  this repo's per-skill markdown memory is unproven (no benchmark here).
- SkillOpt reports separate figures per harness (direct chat, Codex loop,
  Claude Code loop) — do not flatten them into one number when citing it.
- Verify these against current sources before citing as fact — the field moves
  fast and arXiv preprints can rename between versions (see CoEvoSkills above).
