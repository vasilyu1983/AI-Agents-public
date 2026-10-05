---
name: ai-architecture-advisor
description: "Chooses among AI/ML approaches: classical ML, LLM, RAG, fine-tuning, agents, embeddings, MoE or SSM. Use when picking or scaling an architecture, or self-host vs API."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.7"
last_validated: 2026-09-27
---

# AI Architecture Advisor

The **front-door decision skill** for "I have problem X — what should I build with?" It owns
the **choice** — which approach fits, when to promote complexity (and when *not* to), how to
transfer knowledge, how to scale — then **hands off** to the deep skill that owns the depth. It
spans the whole modeling space in one place so you can compare options that normally live in
separate skills side by side:

```text
tabular GBDT  ·  deep net  ·  Transformer/LLM  ·  RAG  ·  fine-tuning  ·  agents
multimodal/omni  ·  embeddings & retrieval  ·  recsys/ranking  ·  model architecture (dense/MoE/SSM/diffusion)
```

No theory dumps — decision tables, elimination logic, tradeoffs, and a pointer to the deep skill.

**The architect's move is to ask before answering.** The amateur hears "build an AI feature"
and reaches for the model they know ("we'll fine-tune Kimi"). The architect first asks: *what
data type? what volume? what task? what's the success metric? do you even need a Transformer?*
The skill that distinguishes an architect is the willingness to say **"for this, CatBoost wins,"**
**"here you need a Transformer,"** or **"LoRA is enough here"** — and to refuse to name an
approach until the problem is classified. Never jump to a model before the Intake questions
below are answered.

## Intake: Ask Before You Answer

A request like "let's fine-tune model X" is a *proposed solution*, not a problem statement.
Do not accept it at face value. Surface the six questions that decide the architecture, and
hold any model name until they're answered. If the user can't answer one, that gap is itself a
finding (most often: no success metric, or no labeled data).

| Ask | Why it changes the answer |
|---|---|
| **What's the task?** classify / rank / generate / extract / retrieve / act | Picks the lane before anything else — tabular-classify and open-ended-generate share no architecture |
| **What's the data?** type (tabular/text/image/audio), volume, labeled? private? fresh? | Tabular+small → trees; private/fresh knowledge → RAG not fine-tune; no labels → no SFT |
| **What's the success metric & bar?** accuracy / latency / cost-per-outcome / interpretability | "Make it work" can't be scored; the binding constraint eliminates most options |
| **What are the constraints?** p99 latency, $/query at volume, on-prem/cloud, no-hallucination | A <50ms or AWS-only or no-hallucination constraint forces the design more than the task does |
| **Is there a regulatory/compliance driver?** high-risk classification (EU AI Act), data residency, right-to-explanation, audit trail | Can force an inherently-interpretable model (trees, not a black-box net), ban sending data to a third-party API, or mandate human-in-the-loop — overriding an accuracy-only ranking |
| **Do you even need an LLM/Transformer?** | The cheapest thing that clears the bar wins — often a tree, a regex, or a single API call beats a fine-tune |

**Breaking ties among survivors:** hard constraints (a p99 ceiling, an on-prem requirement, a
regulatory bar) are *gates* — fail one and the option is out, no matter how it scores elsewhere.
Only among options that clear every gate do the soft criteria (cost, developer familiarity,
marginal accuracy) act as tie-breakers. Don't let a soft criterion overrule a failed hard
constraint, and don't eliminate an option on a soft criterion before checking whether a rival
actually clears every gate.

## Quick Reference

| You're choosing between | Default first move | Promote when | Deep skill |
|---|---|---|---|
| Tabular model family | Gradient-boosted trees (XGBoost) | Table is within a tabular foundation model's current row/feature limits (read the model card), raw accuracy is the bar, and the licence permits your use | [ai-ml-data-science](../ai-ml-data-science/SKILL.md) |
| Trees vs deep learning (tabular) | Trees | Huge data + raw signals (images/text/audio) embedded in features | [ai-ml-data-science](../ai-ml-data-science/SKILL.md) |
| Thinking effort on one model | Low/no thinking | Gap is multi-step *logic/planning*: raise the thinking budget (it's a dial, not a separate model) before fine-tuning | [thinking-budget matrix](references/decision-matrices.md#thinking-budget-how-much-test-time-compute) |
| LLM prompt vs RAG | Prompt-only | Needs current/private knowledge or citations (and the corpus won't fit affordably in a long-context window) | [ai-rag](../ai-rag/SKILL.md) |
| RAG vs fine-tuning | RAG | Behavior/format gap persists after RAG+prompt fixes; combine both (RAFT) for domain-specific RAG | [ai-llm](../ai-llm/SKILL.md) |
| Adapt vs post-train (RLHF/DPO/GRPO) | Prompt → thinking → RAG → SFT first | Behavior/preference/reasoning gap survives SFT and you own preference or verifiable-reward data | [ai-post-training](../ai-post-training/SKILL.md) |
| Single LLM call vs agent | Single call / workflow | Needs tools (via MCP), multi-step planning, or external actions | [ai-agents](../ai-agents/SKILL.md) |
| Omni model vs specialist pipeline | Omni/VLM to validate | Accuracy KPI, cost-at-volume, or no-hallucination needs → disaggregate to specialists | [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md) |
| Embedding / retrieval model | Strong general embedder + reranker | Domain/multilingual fit, latency, or late-interaction needs (note: swap = full re-index) | [ai-rag](../ai-rag/SKILL.md) |
| Search/rank vs recommend | — | Implicit feedback + <50ms + dynamic M-item catalog → it's recsys, not RAG | [ai-ml-data-science](../ai-ml-data-science/SKILL.md) |
| Sequence/perception net family | Transformer (text), ViT (vision) | Streaming/tiny-footprint → RNN/GRU; spatial images → CNN; text-to-text transform → encoder-decoder; encode-for-retrieval → encoder-only (BERT-class) | [ai-ml-data-science](../ai-ml-data-science/SKILL.md) |
| Model architecture (dense/MoE/SSM/diffusion) | Whatever the API serves | Only when self-hosting/training: MoE (cost), SSM/hybrid (>100k-tok throughput), diffusion-LM (tokens/sec); attention = GQA default, MLA/NSA for KV-cache/long-context | [ai-llm-inference](../ai-llm-inference/SKILL.md) |
| Train from scratch vs adapt | Adapt (prompt/RAG/fine-tune) | Research goal *is* the pre-training, or no suitable base model | [ai-pretraining](../ai-pretraining/SKILL.md) |
| Hosted API vs self-hosted open weights | Hosted API | Sustained, predictable volume passes the fully loaded breakeven (GPU + engineering + on-call vs API spend), or residency/on-prem forces self-hosting | [ai-api-cost-guide](../ops-cost-optimization/references/ai-api-cost-guide.md) (breakeven), [ai-llm-inference](../ai-llm-inference/SKILL.md) (throughput inputs) |

## When to Use This Skill

Activate (in any language) on "What architecture should I use for X?" / "Как выбрать
архитектуру?" and on any row of the Quick Reference above: CatBoost vs Transformer vs RAG vs
fine-tuning vs agent; trees vs neural net on tabular; one call vs multi-agent; omni vs
specialist; which embedder / do I need a reranker; search vs recommendation; dense vs MoE /
Mamba / diffusion-LM; self-host open weights vs API breakeven; how to transfer knowledge, scale
a model, or vet a newer architecture — any side-by-side comparison before committing to a build.

If the user has **already** chosen the approach and wants to build it, skip this skill and
go straight to the deep skill.

## Scope Boundaries (Use These Skills for Depth)

This skill decides; these implement. Hand off once the approach is chosen. Primary skill per
lane below — the **[full AI skill map](references/ai-skill-map.md)** catalogs the `ai-*`
skills (supporting + adjacent) grouped by lane, with one-line "owns what" descriptions.

- **Classical ML / data** → [ai-ml-data-science](../ai-ml-data-science/SKILL.md) (GBDT, EDA, train a specialist), [ai-ml-timeseries](../ai-ml-timeseries/SKILL.md)
- **LLM lifecycle & prompting** → [ai-llm](../ai-llm/SKILL.md) (SFT/PEFT, distillation, compression recovery), [ai-mlops](../ai-mlops/SKILL.md) (model/provider migration), [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md), [ai-post-training](../ai-post-training/SKILL.md) (RLHF/DPO/GRPO/RLVR)
- **Retrieval & context** → [ai-rag](../ai-rag/SKILL.md), [ai-context-layer](../ai-context-layer/SKILL.md), [ai-vector-brain](../ai-vector-brain/SKILL.md)
- **Agents & applied bots** → [ai-agents](../ai-agents/SKILL.md), [ai-bot-builder](../ai-bot-builder/SKILL.md), [ai-voice-bots](../ai-voice-bots/SKILL.md), [ai-coding-agents](../ai-coding-agents/SKILL.md)
- **Pre-training** → [ai-pretraining](../ai-pretraining/SKILL.md), [ai-distributed-training](../ai-distributed-training/SKILL.md), [ai-scaling-laws](../ai-scaling-laws/SKILL.md), [ai-data-curation-pretraining](../ai-data-curation-pretraining/SKILL.md)
- **Serving, evals & ops** → [ai-llm-inference](../ai-llm-inference/SKILL.md), [ai-local-model-ops](../ai-local-model-ops/SKILL.md), [ai-evals](../ai-evals/SKILL.md), [ai-deep-research](../ai-deep-research/SKILL.md), [ai-mlops](../ai-mlops/SKILL.md), [ai-product-operating-model](../ai-product-operating-model/SKILL.md)
- **Scouting new architectures** → [research-arxiv-scout](../research-arxiv-scout/SKILL.md), [research-scout](../research-scout/SKILL.md)
- **Beyond the AI family** → [foundations-decision-theory](../foundations-decision-theory/SKILL.md) (choice under uncertainty), [software-architecture-design](../software-architecture-design/SKILL.md) (system/runtime topology)

## Default Workflow

1. **Classify the problem.** What is the output and the data?
   - Structured/tabular rows -> classical ML lane.
   - Natural-language understanding or generation -> LLM lane.
   - Retrieve-then-answer over a corpus -> RAG lane.
   - Multi-step actions / tool use -> agent lane.
   - Images/audio/raw signals -> deep-learning lane.
2. **Eliminate ineligible options with a reason.** Never silently drop a candidate. E.g.
   "fine-tuning eliminated: the gap is missing knowledge, not behavior — RAG first."
3. **Score the survivors independently** on: accuracy ceiling, latency, cost-per-outcome,
   data required, interpretability, and operational burden. Don't pre-commit before scoring.
4. **Pick the simplest option that clears the bar.** Start simple; promote complexity only
   on evidence of a repeated, stable failure the simpler option can't fix.
5. **State the decision and hand off** to the deep skill, with the *reason* and the
   *promotion trigger* ("revisit if X").

## Decision Tree: The Lanes

```text
What are you predicting / producing?
    |
    +- A value/label from columns (tabular) ............ CLASSICAL ML
    |     small data or need interpretability? ............ trees / linear
    |     within a tabular-FM's limits, max accuracy? ..... tabular foundation model (check limits + licence)
    |     accuracy on large/wide structured data? ......... gradient-boosted trees
    |
    +- Rank items for a user from behavior ............. RECSYS / RANKING
    |     implicit feedback + <50ms + dynamic catalog? ... two-tower retrieve -> ranker (not RAG)
    |
    +- Text understanding/generation .................... LLM
    |     stable instructions, no private data? .......... prompt-only
    |     multi-step logic/planning gap? ................. raise thinking budget (dial, not a separate model)
    |     needs current/private knowledge? ............... + RAG / context engineering
    |     stable behavior/format gap remains? ............ + fine-tune (SFT)
    |     preference/safety/reasoning gap after SFT? ..... + post-train (RLHF/DPO/GRPO/RLVR) -> ai-post-training
    |
    +- Answer grounded in a document corpus ............. RAG (pick the embedder + reranker first)
    |     relational/multi-hop over many entities? ...... GraphRAG / agentic RAG
    |
    +- Take actions / call tools / multi-step .......... AGENT
    |     one tool, linear? .............................. tool-use workflow
    |     planning + many tools? ......................... single agent (tools via MCP)
    |     distinct specialized + parallel roles? ........ multi-agent (only if single provably can't)
    |
    +- Images / audio / video + text ................... MULTIMODAL
    |     validating a product? .......................... omni / VLM model
    |     accuracy / cost-at-volume / no-hallucination? .. specialist per modality -> LLM reasoning
    |
    +- Images / audio / raw signals (no language) ...... DEEP LEARNING
    |     spatial grid (images)? ......................... CNN / Vision Transformer (ViT)
    |     ordered sequence, tiny/streaming footprint? .... RNN / LSTM / GRU (else Transformer)
    |     text-to-text transform (translate/summarize)? .. encoder-decoder (T5-class seq2seq)
    |     encode text for classification/retrieval? ...... encoder-only (BERT-class)
    |     generate images/audio? ......................... diffusion / GAN / VAE (see emerging note)

Orthogonal to the lane — only when self-hosting or training the weights:
    model architecture = dense | MoE | SSM/hybrid | diffusion-LM   (invisible behind an API)
    attention variant   = MHA -> GQA (default) | MLA (KV-cache) | NSA/sliding-window (long-context)
```

**Older/foundational nets are still the right call sometimes** (RNN/GRU for tiny or streaming
footprints, CNN for spatial images, encoder-only BERT-class as the embedding/classification
backbone, encoder-decoder for fixed text-to-text transforms) — name and route them, never drop
them silently. Family table in
[decision-matrices.md](references/decision-matrices.md#older--foundational-net-family).

## Classical ML: Trees First, Tabular FM When It Fits

For tabular data, gradient-boosted trees are the strong default. The libraries are the *same
algorithm* with different engineering, so pick by the deciding feature, not hype: **start
RandomForest (baseline) -> XGBoost (tune) -> LightGBM if too slow on big data, or CatBoost if
categorical-heavy.** Per-library table in
[decision-matrices.md](references/decision-matrices.md#gbdt-library-selection). Reach for deep
learning on tabular only when raw images/text/audio are part of the row.

**Tabular foundation models.** "Trees always win on tabular" (Grinsztajn 2022) no longer holds
inside an in-context tabular FM's limits. **Try one first when the table is within the current
row/feature limits on the model card and raw accuracy is the bar; trees stay the default beyond
those limits, on very wide tables, and where a natively inspectable, CPU-cheap model matters.**
**Licence gate:** TabPFN weights are non-commercial by default — an evaluation that informs a
commercial decision already counts as commercial use, and training or distilling another model
from TabPFN or its outputs for commercial use needs a commercial licence. An open-weight
alternative (TabICL) avoids this; check its licence too. Size regimes, the comparison protocol,
and the licence detail live in
[ai-ml-data-science](../ai-ml-data-science/references/modelling-patterns.md#31-tabular-data).

## LLM Lane: Prompt -> Thinking -> RAG -> Fine-tune -> Post-train (Agent Is a Separate Axis)

This is the library's single build ladder; other skills link here instead of restating it.
Promote one rung only when the current rung provably fails. Match the rung to the *gap type* —
reasoning, knowledge, and behavior are different failures with different fixes. Tools and
actions are an orthogonal axis: add an agent at whatever rung the task needs, not as a rung above post-training.

| Rung | Promote here when the gap is | Key caveat |
|---|---|---|
| **Prompt-only** | nothing missing — stable instructions, public knowledge, no actions | cheapest/fastest; the default |
| **+ More thinking (test-time compute)** | *multi-step logic/planning* | a **dial on one model** (thinking-token budget), not a separate "reasoning model"; try *before* fine-tuning; tokens = $ + lag |
| **+ RAG** | *current/private knowledge* or citations | fixes knowledge **not** behavior; first check if the corpus just fits in long context (w/ prompt caching) |
| **+ Fine-tune (SFT)** | *stable behavior/format/style* gap after prompt+RAG | needs labeled data + evals; don't fine-tune for what belongs in retrieval; **RAFT** combines both |
| **+ Post-train (RL)** | *preference/safety/reasoning* gap after SFT | RLHF family: PPO / DPO (KTO/ORPO/SimPO) / GRPO; **RLVR** for verifiable reasoning → [ai-post-training](../ai-post-training/SKILL.md) |
| **Agent (separate axis)** | needs tools (via **MCP**), external actions, multi-step planning | orthogonal to the rungs; consider an SLM for narrow high-volume steps; keep each layer independently testable |

**AWS fork** — when "must run on AWS" binds, the lane logic still applies; only the hosting tier
maps onto AWS services (Bedrock managed → SageMaker custom/fine-tune serving → EC2/EKS full
self-host), plus managed-RAG and guardrail surfaces. Service mapping in
[decision-matrices.md](references/decision-matrices.md#single-call-vs-agent-vs-multi-agent).

(RAG-type selection lives in [ai-rag](../ai-rag/SKILL.md); model-tier routing and cascade economics in
[ai-api-cost-guide](../ops-cost-optimization/references/ai-api-cost-guide.md).)

## Model Architecture: Dense vs MoE vs SSM/Hybrid vs Diffusion

This axis is **orthogonal to the lane** and **invisible behind an API** — it only becomes a
decision when you *self-host weights or train from scratch*. **On an API, ignore this entire
axis** (the knobs that matter there are model tier and thinking budget). Self-hosting → **start
dense** unless a binding constraint forces otherwise: **MoE** (cost-per-token at scale — the
frontier default), **SSM/hybrid** (>100k-tok throughput; only the *hybrid* is competitive — pure
SSM fails in-context learning), or **diffusion-LM** (raw tokens/sec for code/structured text).
Then pick the MoE granularity and attention variant against that constraint. The full
architecture-comparison + sub-axes tables are in
[decision-matrices.md](references/decision-matrices.md#model-architecture-dense-vs-moe-vs-ssm-vs-diffusion);
hand off to [ai-llm-inference](../ai-llm-inference/SKILL.md) (serving) and
[ai-distributed-training](../ai-distributed-training/SKILL.md) (training).

**"What limits this component and how do I work around it?"** The advisor routes; the
[limitation → workaround → owner](references/decision-matrices.md#architecture-limitation--workaround--owning-skill)
and [encoder vs decoder](references/decision-matrices.md#transformer-family-encoder-vs-decoder-vs-encoder-decoder)
tables map each one to build-time depth ([ai-pretraining](../ai-pretraining/references/architecture-limitations-and-workarounds.md))
or serve-time depth ([ai-llm-inference](../ai-llm-inference/references/architecture-and-attention-serving.md)).

## Multimodal: Omni Model vs Specialist Pipeline

For images/audio/video alongside text, the choice is *one unified model* vs *a specialist
perceptual layer feeding an LLM*.

- **Omni / VLM (single model)** — default to **validate** a product fast; one API, broad
  coverage. Good enough for general visual Q&A, light OCR, casual audio.
- **Specialist per modality -> LLM reasoning** — switch when accuracy is the KPI, cost at
  volume binds, or you need non-hallucinating outputs (medical imaging, high-volume OCR,
  real-time/streaming ASR). The modality gap does **not** close with frontier scale alone.
  Signal table and OCR/IDP routing in
  [decision-matrices.md](references/decision-matrices.md#multimodal-omni-vs-specialist-pipeline).

Hand off to [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md) (multimodal
prompting) and [ai-ml-data-science](../ai-ml-data-science/SKILL.md) (training a specialist).

## Embeddings & Retrieval Model (a decision with lock-in)

The embedding/retrieval model is a *first-order* choice, not "RAG config": **swapping it forces
a full re-index.** Decide deliberately on five axes (modality → hosting → language → domain fit
→ retrieval architecture), and add a **cross-encoder reranker** by default (skip only under a
hard p99 budget). Five-axis selection tree in
[decision-matrices.md](references/decision-matrices.md#embedding--retrieval-model-selection);
depth in [ai-rag](../ai-rag/SKILL.md), concrete brains in
[ai-vector-brain](../ai-vector-brain/SKILL.md).

## Recommendation / Ranking (a distinct lane, not RAG)

**Implicit behavioral signals** (clicks/dwell/skips) + **<50ms** + a **dynamic catalog of
millions** = a recommender, *not* RAG — even though both "retrieve then rank." Don't model it as
vector-RAG; the default shape is **two-tower retrieval → ranking model**. RAG-vs-recsys
property table in
[decision-matrices.md](references/decision-matrices.md#recsys--ranking-vs-rag); depth in
[ai-ml-data-science](../ai-ml-data-science/SKILL.md) plus RecSys literature.

## How to Transfer Knowledge

"Transfer knowledge to a new task" has several distinct mechanisms — pick by what's stable and
what changes: new *facts* → RAG (no training); new domain with labels → fine-tune/LoRA; shrink
to a cheap model → distillation (reasoning distillation to keep CoT), **only after confirming the
teacher's terms permit training a competing model — record the licence**; new downstream task on a
vision/audio backbone → freeze + train a head; related tabular task → retrain trees or let a
tabular FM transfer via in-context learning. Situation-by-mechanism table in
[decision-matrices.md](references/decision-matrices.md#transferring-knowledge-to-a-new-task).

## How to Scale a Model

"Scale" is ambiguous — **clarify which axis first**, because the answer differs: (a) better
quality from more data/params (scaling laws), (b) better quality without retraining (**test-time
compute** — now a primary lever, not an afterthought: thinking budget / best-of-N + verifier,
traded against latency and cost per query class), (c) train a model too big for one GPU
(FSDP/ZeRO), (d) serve more traffic / lower latency (batching, quantization, routing), (e) more
data in the pipeline (data-lake/streaming). Axis → move → deep-skill routing table in
[decision-matrices.md](references/decision-matrices.md#how-to-scale-which-axis).

## How to Find & Vet New Architectures

When the right approach might be newer than what's catalogued, **discover and vet
deliberately** — don't adopt on hype or reject on unfamiliarity: *scout a fixed signal set →
eliminate on public benchmarks → confirm on your own 50–200-example golden set → hold the problem
constant → let it settle.* Leaderboard rank is a **filter, not a verdict**; the output is often a
**routing policy** (which approach per task class), not a single winner. Scouting →
[research-arxiv-scout](../research-arxiv-scout/SKILL.md) / [research-scout](../research-scout/SKILL.md);
eval methodology → [ai-evals](../ai-evals/SKILL.md); full process and emerging classes ("named but
not yet load-bearing") in [discovering-architectures.md](references/discovering-architectures.md).

## Decision Record Gate

Do not finish with a model name alone. The decision record must state the task and prediction point, hard constraints, eligible candidates, one-line elimination reason for every rejected candidate, the simplest baseline, the evidence used to compare survivors, and the measurable trigger for reconsidering the choice. If a hard constraint or success bar is unknown, return a provisional experiment plan rather than a production architecture verdict. For a model or provider pick, the record also states the licence terms (commercial use, fine-tuning, use of outputs to train other models, data retention and residency), the fallback model with its switch trigger, and a re-evaluation date; compare candidates with the same-harness rule in [decision-matrices.md](references/decision-matrices.md#vetting-a-new-architecture).

## Known Traps (Top Six)

The failure mode behind all of these: reaching for the familiar approach before classifying the
problem. Full trap + anti-pattern catalog in
[traps-and-anti-patterns.md](references/traps-and-anti-patterns.md).

- **fine-tuning the wrong gap** — fine-tune fixes *behavior/format*; missing knowledge → RAG, weak reasoning → a reasoning model / more thinking. Match the fix to the gap type.
- **"trees always win on tabular"** — false within a tabular FM's limits; but quoting a remembered size limit is its own trap — read the current model card, and check the licence before a commercial bake-off.
- **reflexive RAG / unchecked long-context** — a static corpus may just fit in long context; but *multi-fact* long-context recall degrades **silently** (needle tests pass, real recall fails) — eval multi-fact, and price the cost cliff at volume.
- **jumping to multi-agent** when a single agent or linear tool-use workflow would do — multi-agent can *lower* quality on sequential tasks via coordination overhead.
- **architecture-axis theatre** — debating dense/MoE/SSM/diffusion for a builder who only calls a hosted API (it's invisible there); or treating embedding choice as throwaway config (it has re-index lock-in).
- **silently dropping a candidate** instead of eliminating it with a stated reason.

## Navigation: Core References

- **[AI Skill Map](references/ai-skill-map.md)** — the `ai-*` supporting deep skills grouped by decision lane; the handoff index
- **[Decision Matrices](references/decision-matrices.md)** — cross-paradigm selection tables (classical ML vs DL vs LLM vs RAG vs fine-tune vs agent); also holds the transfer-knowledge, scale-axis, and emerging-classes tables
- **[When To Use What](references/when-to-use-what.md)** — per-approach "use it when / avoid it when" cheat sheet, including the GBDT family
- **[Discovering Architectures](references/discovering-architectures.md)** — discover → vet → reframe process for approaches newer than this skill catalogs
- **[Traps & Anti-Patterns](references/traps-and-anti-patterns.md)** — full trap + anti-pattern catalog (the negative knowledge)

## External Sources

See **[data/sources.json](data/sources.json)** for primary references on model selection,
the GBDT family, the prompt/RAG/fine-tune decision, and agent build-vs-not.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
