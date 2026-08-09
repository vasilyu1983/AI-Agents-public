# Evidence Base — Maturity Grounding (re-verified July 2026)

Provenance for the maturity claims in this skill and the Layer 1 (auto-capture)
and Layer 3 (eval-gated promotion) designs. Graded with research-scout
discipline: peer-reviewed/venue = A, primary vendor docs = B, vendor/trade blog
= C (pattern evidence only, never proof). The load-bearing conclusions rest on
A/B sources and on one corroborated *absence* (no production-practice source
documents trustworthy autonomous self-capture).

The structured, machine-readable mirror of this list is `data/sources.json`
(same 8 sources, same grades). Keep the two in sync — update both or neither.

## Sources

| Source | Grade | Grounds what |
|---|---|---|
| [Memory for Autonomous LLM Agents — arXiv 2603.07670](https://arxiv.org/abs/2603.07670) | A | Memory is a first-class agent discipline in 2026; names the open problems — continual consolidation, *trustworthy reflection*, learned forgetting — that justify keeping Layers 2–3 conservative. |
| [State of AI Agent Memory 2026 — mem0](https://mem0.ai/blog/state-of-ai-agent-memory-2026) | C | Append-only ADD memory is production-ready (92.5 on LoCoMo, corrected July 2026 from a stale 91.6 figure); **procedural memory (agent-driven self-capture/consolidation) is named explicitly as "early-stage" tooling, not production practice** — the corroborating gap that validates disabling auto-capture by default. |
| [Agentic Context Engineering (ACE) — arXiv 2510.04618, ICLR 2026](https://arxiv.org/abs/2510.04618) | A | SOTA shape for Layer 2: evolving playbook via Generator/Reflector/Curator; "context collapse" and "brevity bias" are the failure modes structured incremental consolidation must avoid. |
| [ACE: evolving playbooks for self-improving agents — VentureBeat](https://venturebeat.com/ai/ace-prevents-context-collapse-with-evolving-playbooks-for-self-improving-ai) | C | Cross-source corroboration of ACE (independent of the paper); trade-press framing only. |
| [What Is the Learnings Loop — MindStudio](https://www.mindstudio.ai/blog/learnings-loop-claude-code-skills-self-improvement) | C | The base loop pattern this skill is explicitly borrowed from (see SKILL.md intro); pattern evidence, not validation. |
| [Testing Agent Skills Systematically with Evals — OpenAI](https://developers.openai.com/blog/eval-skills) | B | Establishes the eval *mechanics* this design borrows (prompt → captured run → checks → comparable score; "every manual fix is a signal, turn it into a test"). Re-verified July 2026: this page covers measurement, not gating — it does **not** describe threshold-based promotion or CI blocking; that half comes from Braintrust below. Corrected from an earlier overclaim that attributed the gate workflow to this source. |
| [Agent observability complete guide 2026 — Braintrust](https://www.braintrust.dev/articles/agent-observability-complete-guide-2026) | C | The actual source for the production-failure → eval-case → CI-gate workflow ("blocks merges when a change degrades agent quality"); this is the pattern Layer 3's `--gate` mirrors at zero cost. |
| [ICLR 2026 Workshop on Memory for LLM-Based Agentic Systems (MemAgents)](https://iclr.cc/virtual/2026/workshop/10000792) | A | Memory-for-agents is an active first-class research venue in 2026 — the field is unsettled, which is why this skill keeps promotion human-gated. |
| [ECC (Everything Claude Code) — continuous-learning-v2, commit `51a6950`](https://github.com/affaan-m/ECC) | C (pattern evidence only, MIT-licensed source code, not a research or vendor-docs source) | Origin of the atomic confidence-scored "instinct" concept in `references/instinct-pattern.md` — a cross-cutting complement to this skill's per-skill loop. This repo does not adopt ECC's automatic project→global promotion (conflicts with the human-gate design above) or restate its "100% reliable" hook-capture claim as fact. |

## How this maps to the design

- **Layer 1 default-off** ← mem0 absence + arXiv 2603.07670 "trustworthy
  reflection" open problem: autonomous self-capture is not mature; manual
  `append_learning.py` is the safe floor.
- **Layer 2 still manual** ← ACE shows the *target* shape but consolidation at
  scale is an open research problem, not solved engineering.
- **Layer 3 built as a gate** ← OpenAI (eval mechanics) + Braintrust (the
  gate/CI-block workflow itself): eval-gated promotion is the mature pattern;
  implemented here as a zero-cost discriminating-eval gate that never auto-edits
  skill logic.

## June 2026 Additions

| Source | Grade | Grounds what |
|---|---|---|
| [SkillOpt: Executive Strategy for Self-Evolving Agent Skills (arXiv 2605.23904)](https://arxiv.org/abs/2605.23904) | A | First systematic text-space optimizer for agent skills: a separate optimizer model turns scored rollouts into bounded add/delete/replace edits on a single skill document, accepting an edit only when it strictly improves a held-out validation score (+23.5 points on GPT-5.5; tested across Claude Code and Codex). Confirms the Layer 3 gate principle: *the quality of the verifier bounds the quality of self-improvement*. |
| [CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification (arXiv 2604.01687, v2 — renamed from the v1 "EvoSkills" title, confirmed July 2026)](https://arxiv.org/abs/2604.01687) | A | Co-evolutionary verification framework: Skill Generator + Surrogate Verifier, no ground-truth needed; achieves 71.1% pass rate on SkillsBench (+40.5pp over no-skill baseline). Validates the human-gated promotion model — both SkillOpt and CoEvoSkills use held-out/surrogate validation gates, not autonomous self-rewrite. |

**How these map to the design:**
- **Layer 3 gate confirmed** ← SkillOpt and CoEvoSkills both show that a held-out discriminating eval is the standard 2026 practice for deciding whether a skill edit is accepted; this design's `promote_learning.py --gate` is the conservative zero-cost version of this pattern.
- **Auto-rewrite still not recommended for production markdown skills** ← SkillOpt and CoEvoSkills operate on structured skill documents with automated test harnesses and a scored optimizer/verifier loop, not free-form human-reviewed markdown; the gap means the human-gate remains the right default for this repo.

## Caveats

- Grade-C vendor blogs (mem0, MindStudio, Braintrust) are PR-tinged. Their
  "wire it in an afternoon" / "learns from every run" framing is discounted;
  only their structural pattern descriptions are used.
- **MindStudio's actual "learnings loop" is the anti-pattern this skill forbids.**
  Re-read July 2026: MindStudio's mechanism has Claude Code rewrite the skill's
  *persistent instructions themselves* from user corrections — i.e. autonomous
  `SKILL.md` self-modification. This design borrows only the name and the
  "accumulate corrections over sessions" shape; it deliberately inverts
  MindStudio's core move (auto-rewrite) into a human-gated one (append raw,
  consolidate by review, promote only behind an eval gate). Do not cite
  MindStudio as evidence that auto-rewriting `SKILL.md` is safe — it is evidence
  of the opposite pattern's existence in the wild, not of its safety.
- ACE's headline gains (+10.6% agents) are the method's own claims; transfer to
  this repo's per-skill markdown memory is unproven (no benchmark here).
- SkillOpt's headline figure (+23.5 points) is specifically *direct-chat GPT-5.5*;
  its Codex-agentic-loop (+24.8) and Claude-Code-loop (+19.1) numbers differ —
  do not flatten all three into one number when citing this paper.
- Verify these against current sources before citing as fact — the field moved
  fast through 2026, arXiv preprints can rename between v1 and v2 (see
  CoEvoSkills above), and several of these are < 6 months old at time of writing.
