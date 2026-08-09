# Traps & Anti-Patterns

The negative knowledge behind the advisor: the mistakes that look reasonable in the moment and
cost the most later. Most are restatements of a decision rule from SKILL.md, surfaced here as
pattern-interrupts. Read before committing to a build.

## Table of Contents

- [Known Traps](#known-traps)
- [Common Anti-Patterns](#common-anti-patterns)

---

## Known Traps

- recommending fine-tuning when the real gap is missing knowledge (use RAG), weak prompts, or *reasoning* (use a reasoning model)
- fine-tuning to fix a multi-step logic gap that a reasoning model / extended thinking would close more cheaply
- reaching for deep learning on tabular data where gradient-boosted trees win with less data and cost
- assuming "trees always win on tabular" — within a tabular foundation model's envelope (TabPFN-3 ≤~1M rows; TabICL v2 open) it now beats tuned GBDTs; but quoting a stale size limit (the "50k rows" of TabPFN-2.5 is already superseded) is its own trap — verify the current version
- treating *pure* SSM (Mamba) as Transformer-competitive — only the **hybrid** (mostly-SSM + a few attention layers, e.g. Jamba/Granite-4/Nemotron-H) is; pure SSM fails in-context learning
- skipping the **post-training** rung — treating RLHF/DPO/GRPO as the same as SFT, or fine-tuning when the gap is *preference/safety/reasoning* (needs a reward signal), not format
- treating older nets as obsolete — RNN/GRU still win on tiny/streaming footprints, CNN on spatial images, and encoder-only (BERT-class) is the standard embedding/classification backbone behind RAG and rankers
- reflexively building RAG when a static corpus fits affordably in a long-context window (with prompt caching)
- trusting long-context recall: single-fact "needle" tests pass at 99%+, but *multi-fact* recall across a big window degrades sharply and the failure is **silent** — eval multi-fact before betting on it
- ignoring cost cliffs when scoring options: at high query volume, long-context can cost orders of magnitude more per query than RAG, and multi-agent many times a single call — put the order-of-magnitude number in the comparison
- jumping to multi-agent when a single agent or a linear tool-use workflow would do (multi-agent can *lower* quality on sequential tasks via coordination overhead)
- treating embedding-model choice as throwaway config — it has lock-in (swap = full re-index); decide it deliberately
- modeling a recommender as vector-RAG (implicit feedback + <50ms + dynamic catalog is a different lane)
- debating dense-vs-MoE-vs-SSM-vs-diffusion for a builder who only calls a hosted API (the architecture is invisible there)
- choosing a library from benchmarks alone without checking data size, categoricals, or interpretability needs
- conflating the meanings of "scale" (data/params, test-time compute, training, serving, pipeline) and answering the wrong one
- silently dropping a candidate approach instead of eliminating it with a stated reason
- locking into a closed provider's fine-tuned model or proprietary embedding format with no exit plan — the migration cost only shows up when you need to leave; weigh portability (open weights, standard embedding formats) against short-term convenience whenever switching cost is plausible
- claiming "the simpler rung failed" without a golden-set eval harness to back it — promotion decisions made on vibes are the same mistake as adopting on hype, just pointed the other direction; "start simple, promote on evidence" requires the evidence to exist before it can be cited

## Common Anti-Patterns

- architecture chosen before the problem and constraints are classified
- "use an LLM for everything" including problems trees solve better and cheaper
- promoting complexity (RAG -> fine-tune -> agent) without evidence the simpler rung failed
- comparing approaches without holding the eval/problem constant
- this skill re-teaching GBDT or transformer internals instead of handing off to the deep skill
