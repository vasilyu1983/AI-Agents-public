# Idea Extraction Framework

How to convert a paper, blog post, or newsletter item into a stealable idea card.

## Table of Contents

- [Method Shapes](#method-shapes)
- [The Extraction Template](#the-extraction-template)
- [Evidence Grades](#evidence-grades)
- [Naming the Idea](#naming-the-idea)
- [When the Paper Has No Stealable Idea](#when-the-paper-has-no-stealable-idea)

## Method Shapes

Every stealable idea fits one or more of these shapes. Tag each idea card with all that apply.

| Shape | What it is | Examples | Typical lift |
|-------|-----------|----------|--------------|
| `prompting-pattern` | New way to structure prompts or chains | CoT, ReAct, Reflexion, Tree-of-Thoughts | Low (hours-days) |
| `architecture-tweak` | A modification to a model architecture | RoPE, GQA, MoE routing, KV cache compression | High (weeks) |
| `training-recipe` | A change in how a model is trained | DPO, ORPO, RLAIF, curriculum schedules | High (weeks-months) |
| `evaluation-method` | A new way to measure quality | LLM-as-judge variants, agent benchmarks, contamination checks | Medium (days-weeks) |
| `data-construction-recipe` | A way to build training or eval data | Self-instruct, Constitutional AI data, synthetic agent traces | Medium (days-weeks) |
| `inference-time-method` | A method applied at inference, not training | Speculative decoding, beam variants, self-consistency, test-time RL | Medium (days-weeks) |
| `system-design-pattern` | An architectural choice for a system | Retrieval rerank stages, agent memory tiers, tool-use orchestration | Medium (days-weeks) |
| `theoretical-bound` | A claim about what is or isn't possible | Scaling laws, lower bounds, impossibility results | Low to apply (read), high to verify |
| `negative-result` | A method that *doesn't* work | "X doesn't help when Y", failed scaling claims | Low (saves time) |
| `survey-or-taxonomy` | Synthesis without a new method | Survey papers, position papers | Not stealable as method — list as background only |
| `monetizable-feature-pattern` | A product feature empirically tied to retention, conversion, or revenue at a specific company (engineering / PM blog post-mortem, HCI retention paper, founder talk with metrics) | Figma multiplayer cursors → freemium conversion; Linear sub-50ms keyboard shortcuts → enterprise upsell; Netflix carousel ranking → $1B/yr retention | Variable (replication is product work, not research) — see [feature-precedent-mining.md](feature-precedent-mining.md) |

**Multi-shape signal:** Methods that span shapes (e.g., a `prompting-pattern` + `inference-time-method`) often generalize. Pure single-shape ideas in `architecture-tweak` or `training-recipe` rarely transfer outside their training context.

## The Extraction Template

Use this template for every idea card. If you can't fill in 5+ of these without copying paper phrasing, the paper doesn't contain a stealable idea — discard.

```markdown
### Idea: {{Clean name (invent if buried)}}

**Source(s):** {{paper URL}} {{| code URL}} {{| blog/newsletter URL}}
**Method shape(s):** {{tags from the shape catalog}}

**What it does (1-2 sentences):**
{{Plain-language description of the mechanism. No jargon shield. No "we propose".}}

**Inputs / outputs / preconditions:**
- Inputs: {{what you need going in}}
- Outputs: {{what comes out}}
- Preconditions: {{model size, data type, infra requirements}}

**Evidence:**
- Empirical claim: {{X improves Y by Z%}}
- Claim type: {{absolute-performance | relative-gain | efficiency | robustness}}
- Benchmark(s): {{name + version}}
- N: {{number of runs / examples}}
- Baselines: {{what it was compared against}}
- Evidence grade: {{A | B | C | D | F}}

**Reproducibility:**
- Code: {{repo URL or "none"}}
- Benchmarks: {{linked or "none"}}
- Compute: {{rough budget — affects who can replicate}}
- Reproducibility tag: {{code+benchmarks | code_only | paper_only | proprietary}}

**Why it might transfer to {{my target}}:**
- {{Specific reason 1}}
- {{Specific reason 2}}

**Why it might NOT transfer:**
- {{Specific risk 1}}
- {{Specific risk 2}}

**Lift estimate:**
- Days to first prototype: {{1-3 / 1-2 weeks / >2 weeks}}
- Skills required: {{e.g., training infra, prompt iteration, eval design}}

**Kill criteria** (when to stop pursuing):
- {{Concrete metric or threshold}}
- {{Concrete metric or threshold}}

**Trap tags:** {{from known-traps.md, multi-tag allowed}}

**Status:** {{promote | validate | kill}} — {{one-line reason}}
```

## Claim Types

Every empirical claim in the extraction template should be tagged with one of these `claim_type` values (also a column in the findings TSV):

| Value | What it means | Transfer note |
| --- | --- | --- |
| `absolute-performance` | "Method X achieves Y% on benchmark Z" — no baseline comparison | Hardest to transfer; benchmark may not match your setting |
| `relative-gain` | "Method X improves over baseline B by Y%" | Transferable if the baseline is comparable to your current approach |
| `efficiency` | Latency, memory, compute, or throughput improvement (with or without accuracy trade-off) | **Best transfer candidates** — efficiency gains are largely setting-agnostic; a D-grade efficiency claim often beats an A-grade SOTA claim that requires full retraining |
| `robustness` | Performance is stable across distribution shift, input variation, or adversarial conditions | **Second-best transfer candidates** — robustness claims generalise across datasets better than absolute-performance claims |

Practical rule: when ranking ideas for steal priority, an `efficiency` or `robustness` claim at evidence grade D can outrank an `absolute-performance` claim at grade A if adopting the latter requires retraining infrastructure you don't have.

## Evidence Grades

Adapted from the ACM artifact-review badging system and the Pineau Reproducibility Checklist.

| Grade | Criteria | Examples |
|-------|----------|----------|
| **A** | Multi-benchmark, ≥3 baselines, error bars, code + data released, peer-reviewed at top venue | NeurIPS-published method with reproducibility badge |
| **B** | ≥2 benchmarks, ≥2 baselines, code released, preprint with strong methodology section | arXiv preprint with public repo and clear ablations |
| **C** | ≥1 benchmark, ≥1 baseline, code released or paper has full hyperparameters | Solid arXiv preprint without third-party verification |
| **D** | Single benchmark, single baseline, no code, no detailed setup | Demo paper, blog post with screenshots only |
| **F** | No benchmark, no baseline, anecdote or vibe | "We tried X and it felt better" |

Notes:
- An A-grade method can still be the wrong fit; grade is *evidence quality*, not *applicability*.
- A D-grade idea can still be worth tracking if novelty is high — mark as `validate`, not `promote`.
- Industry blog posts rarely hit A. Most cap at B; ones with no eval section are D regardless of source prestige.
- Curator newsletters do not carry their own grade — they inherit the grade of the methods they cover. The newsletter is a discovery mechanism, not the evidence source.

## Naming the Idea

Many papers bury their actual contribution under acronyms or marketing names. Re-name the idea by what it *does*, not what the paper calls it. Good names answer: "What's the one-line description of the mechanism?"

- Bad (paper's name): `RAFT-MAX`
- Better (mechanism): `Train-time retrieval over distractor passages`
- Best (mechanism + applicability hint): `Distractor-aware retrieval training (RAG eval transfer)`

If you can't name the mechanism without using the paper's term, you don't understand the idea yet. Re-read the method section.

## When the Paper Has No Stealable Idea

Some papers won't yield a stealable unit. Common patterns:

- **Pure survey or position paper** — List as background, don't extract.
- **System paper with no transferable component** — A whole-system description (e.g., "we built X end-to-end") often has no decomposable method. Look for a narrower contribution: an evaluation, a dataset construction recipe, an architectural choice.
- **Wrapper around an existing method** — "We applied Method M to Domain D and it worked" — the steal is M itself, which you already knew about. Skip unless D matches your target.
- **Proprietary method with no replicable details** — Hard kill (Trap 11).
- **Pure benchmark paper without baselines** — Discard. A benchmark without a method to compare is reference material, not an idea.

If the paper doesn't yield an idea on the first read, don't force one. Mark as "no extractable idea" in the findings TSV with a one-line reason. Empty extractions are useful information for the scan report.
