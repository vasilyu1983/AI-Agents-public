# Cross-Paradigm Decision Matrices

*Purpose: side-by-side selection tables spanning classical ML, deep learning, LLM, RAG,
fine-tuning, and agents — the comparisons that normally live in separate skills. Use to
eliminate ineligible options with reasons, then hand off to the deep skill.*

## Table of Contents

- [Master: Which Paradigm](#master-which-paradigm)
- [GBDT vs Tabular Foundation Models](#gbdt-vs-tabular-foundation-models)
- [GBDT Library Selection](#gbdt-library-selection)
- [Trees vs Deep Learning (Tabular)](#trees-vs-deep-learning-tabular)
- [Thinking Budget: How Much Test-Time Compute](#thinking-budget-how-much-test-time-compute)
- [Prompt vs RAG vs Fine-tune vs Long-Context](#prompt-vs-rag-vs-fine-tune-vs-long-context)
- [Post-Training Method: SFT vs DPO vs PPO vs GRPO vs RLVR](#post-training-method-sft-vs-dpo-vs-ppo-vs-grpo-vs-rlvr)
- [Single Call vs Agent vs Multi-Agent](#single-call-vs-agent-vs-multi-agent)
- [Older / Foundational Net Family](#older--foundational-net-family)
- [Model Architecture: Dense vs MoE vs SSM vs Diffusion](#model-architecture-dense-vs-moe-vs-ssm-vs-diffusion)
- [Architecture Limitation → Workaround → Owning Skill](#architecture-limitation--workaround--owning-skill)
- [Transformer Family: Encoder vs Decoder vs Encoder-Decoder](#transformer-family-encoder-vs-decoder-vs-encoder-decoder)
- [Multimodal: Omni vs Specialist Pipeline](#multimodal-omni-vs-specialist-pipeline)
- [Embedding / Retrieval Model Selection](#embedding--retrieval-model-selection)
- [Recsys / Ranking vs RAG](#recsys--ranking-vs-rag)
- [Adapt vs Train From Scratch](#adapt-vs-train-from-scratch)
- [Transferring Knowledge to a New Task](#transferring-knowledge-to-a-new-task)
- [How to Scale (Which Axis)](#how-to-scale-which-axis)
- [Vetting a New Architecture](#vetting-a-new-architecture)
- [Emerging Architecture Classes (mid-2026)](#emerging-architecture-classes-mid-2026)

---

## Master: Which Paradigm

| Problem shape | First choice | Avoid because | Deep skill |
|---|---|---|---|
| Predict value/label from columns | Gradient-boosted trees | LLM is slower, costlier, less accurate on tabular | ai-ml-data-science |
| Understand/generate natural language | LLM (prompt-first) | Trees can't model language | ai-llm |
| Answer from a private/large corpus | RAG | Fine-tuning bakes in stale facts | ai-rag |
| Take actions / call tools / plan steps | Agent | A single call can't act or loop | ai-agents |
| Classify images / audio / raw signals | Deep net (CNN/Transformer) | Trees need hand-engineered features | ai-ml-data-science |
| Reason over images/audio/video + text | Omni/VLM (then specialist if accuracy/cost binds) | Text-only model can't perceive | ai-prompt-engineering |
| Similarity / semantic retrieval | Embedding model + reranker | Generative call is slower and costlier per match | ai-rag |
| Rank items for a user from behavior | Recsys (two-tower -> ranker) | RAG ignores implicit feedback + <50ms budget | ai-ml-data-science |

## GBDT vs Tabular Foundation Models

The "trees win on tabular" default (Grinsztajn 2022) is now broadly contested by in-context
tabular foundation models. Lineage: TabPFN v2 (Nature 2025, ~10k rows) → **TabPFN-2.5**
(arXiv 2511.08667, Nov 2025, ~50k rows / ~2k features, + distillation engine to compact
MLP/tree) → **TabPFN-3** (May 2026, ~1M rows — the current frontier). Open-source reference
alternative: **TabICL v2** (Feb 2026) when the non-commercial TabPFN license blocks you.
(Volatile — verify the current version's limits before quoting; names date faster than the rule.)

| Signal | Lean GBDT (XGBoost/LightGBM/CatBoost) | Lean tabular FM (TabPFN-3 / TabICL v2) |
|---|---|---|
| Table size | beyond the current FM envelope, or very wide (>~2k cols) | within the current FM envelope (TabPFN-3 ~1M rows; strongest on small/medium) |
| Goal | deployable, inspectable, low-latency model (or use the FM's distilled export) | max accuracy with no tuning, single forward pass |
| Tuning budget | have one, want headroom | none — FM beats tuned GBDTs out of the box on small/medium data |
| Ops constraint | CPU-friendly, mature ecosystem | needs the FM runtime (or its distilled MLP/tree export); license matters (TabPFN non-commercial) |

Rule: **try a tabular FM first whenever the table is within its (version-specific) envelope and
raw accuracy is the bar; GBDT stays the default for very wide tables, beyond the FM envelope,
and where a natively inspectable, CPU-cheap model with a mature ecosystem matters.**

## GBDT Library Selection

| Library | Deciding feature | Pick when | Skip when |
|---|---|---|---|
| Decision Tree | one readable tree | need a human-readable rule / baseline | accuracy matters (high variance) |
| Random Forest | bagging, low variance | robust baseline, little tuning budget | you need max accuracy and will tune |
| XGBoost | regularization + 2nd-order grads | general strong default, tuning budget | dataset too large to train fast |
| LightGBM | histogram + leaf-wise growth | large data, training speed matters | tiny data (can overfit leaf-wise) |
| CatBoost | ordered boosting + native categoricals | many categorical features, leakage risk | all-numeric and speed-critical |

## Trees vs Deep Learning (Tabular)

| Signal | Lean trees | Lean deep learning |
|---|---|---|
| Data size | small-to-medium rows | very large + raw modalities in row |
| Feature type | already structured columns | raw text/image/audio embedded |
| Interpretability | required | not required |
| Cost/latency | tight | flexible |

Default: **trees win on structured tabular data** for large/wide tables; for small/medium
tables see [GBDT vs Tabular Foundation Models](#gbdt-vs-tabular-foundation-models). Move to
deep learning only when raw unstructured signals are part of each row.

## Thinking Budget: How Much Test-Time Compute

By 2026 "reasoning model vs standard model" has largely collapsed into **one model with a
thinking-budget dial** (extended-thinking token budget / auto-routing on GPT-5-, Claude-,
Gemini-class models). So the decision is usually *how much* to think, not *which model*.
Test-time compute closes a *logic* gap — distinct from a knowledge gap (RAG) or a behavior
gap (fine-tune). Try raising the budget before fine-tuning when the failure is multi-step
reasoning. It's a first-class cost/latency knob: more thinking = more tokens = more $ + lag.

| Gap you observe | Mechanism | Not this |
|---|---|---|
| Multi-step logic / planning / math fails | Raise the thinking budget / extended thinking | fine-tune (won't add reasoning depth cheaply) |
| Right answer if it "thinks longer" | More test-time compute (higher budget; or best-of-N + a verifier) | bigger base model by default |
| Latency/cost-critical, shallow task | Low/no thinking (skip the overhead) | always-on max thinking (wastes tokens/latency) |
| Need a cheap model that keeps the reasoning | Reasoning distillation from the teacher's traces | full fine-tune from scratch |

## Prompt vs RAG vs Fine-tune vs Long-Context

| Gap you observe | Mechanism | Not this |
|---|---|---|
| Wrong/missing *facts*, large/fresh/cited corpus | RAG | fine-tune (bakes stale facts) |
| Small/static corpus that fits the window | Long-context prompt + prompt caching | RAG (unneeded retrieval complexity) |
| Wrong *behavior/format/style*, repeated & stable | Fine-tune (LoRA/SFT) | RAG (won't change behavior) |
| Domain-specific RAG, want both grounding + behavior | RAFT (retrieval-augmented fine-tuning) | choosing only one |
| Multi-step *logic* gap | Reasoning model (see table above) | fine-tune first |
| Just needs clearer instructions | Better prompt + examples | any heavier option |

Order of promotion: **prompt -> more thinking -> RAG/long-context -> fine-tune -> post-train**,
one rung at a time, on evidence; match the rung to the gap type rather than climbing blindly.

Two cautions when weighing long-context against RAG: (1) **cost cliff** — at high query
volume, re-sending a large context per call can cost orders of magnitude more than retrieving
a few chunks; prompt caching narrows this only when a large *static* prefix is reused.
(2) **silent recall failure** — single-fact "needle in a haystack" tests pass at 99%+, but
*multi-fact* recall across a big window degrades sharply and fails quietly. Eval multi-fact
recall on your own data before betting a design on long context. "Context engineering" (fill
the window with just the right tokens each step) is the broader 2026 framing; RAG is one
input channel within it. GraphRAG / agentic RAG earn their extra cost only for multi-hop or
entity-relational queries that flat vector RAG answers poorly.

## Post-Training Method: SFT vs DPO vs PPO vs GRPO vs RLVR

Post-training is the rung *after* SFT, reached only when a preference, safety, or reasoning gap
survives supervised fine-tuning. Pick by the reward signal you can actually produce. Full
depth (reward modeling, KL regularization, over-optimization) in
[ai-post-training](../../ai-post-training/SKILL.md).

| You have / want | Method | Why |
|---|---|---|
| Labeled demonstrations of the target behavior | **SFT** (the baseline; not "RL") | cheapest; do this first and exhaust it before any RL |
| Pairwise preferences, want simplicity + stability | **DPO** (or DAAs: KTO / ORPO / SimPO) | offline, no reward model or sampling loop; the default first preference method |
| Preferences + budget for a reward model + online RL | **PPO** (reward model + policy + value/critic) | the classic RLHF; highest ceiling, most moving parts and compute |
| Many samples scorable per prompt, want to drop the critic | **GRPO** (group-relative advantage) | DeepSeek-R1's lever; ~40–60% memory cut vs PPO by removing the value model |
| A *verifiable* checker (math/code/unit tests) as reward | **RLVR** (often via GRPO) | no human labels — ground-truth reward; the standard 2026 reasoning recipe |
| Scale preference labels cheaply | **RLAIF / Constitutional AI** | model-as-judge generates the preference/critique signal |
| A quick lift without an RL loop | **Rejection sampling (best-of-N → SFT)** | generate, score, SFT on the winners; simplest "RL-flavored" gain |

Trap: reaching for PPO/GRPO when DPO would do, or post-training at all when the gap is missing
*knowledge* (RAG) or *format* (SFT). Always pair with an eval harness — preference RL
over-optimizes (reward hacking / Goodhart) silently.

## Single Call vs Agent vs Multi-Agent

| Need | Choice |
|---|---|
| One transform, no tools | Single LLM call |
| Linear tool use (1-2 tools, fixed order) | Tool-use workflow |
| Planning + many tools + loops | Single agent (expose tools via MCP) |
| Narrow, high-volume, repetitive agent step | Small language model (SLM) for that step |
| Distinct specialized roles, *parallel & independent* work | Multi-agent (only if a single agent provably can't) |

Default to the lowest tier that meets the need (task → workflow → agent). Multi-agent helps
only when subtasks are genuinely parallel and independent or exceed one context window — on
sequential, write-heavy tasks coordination overhead can *lower* quality and multiply token
cost. Treat **autonomy** as a separate dial from architecture: a capable agent can be
constrained to require approval per action; the 2026 production norm is human-*on*-the-loop
(autonomous execution + monitoring + alert-based intervention), not pre-authorize-everything.
Build tool access to the stable MCP spec; plan a migration when a new spec version finalizes.

**AWS cloud fork** — if the constraint is AWS: **Bedrock** for managed inference (Claude /
Amazon Nova 2 / OpenAI GPT-5.x, 18+ providers / 110+ models); **SageMaker** for custom model
hosting / fine-tune serving; **EC2/EKS** for full OSS self-hosting. **Bedrock Knowledge
Bases** = managed RAG (S3 ingestion, built-in chunking + retrieval, zero-ops).

## Older / Foundational Net Family

Decoder-only LLMs dominate generation, but older families are still the right pick for
specific shapes — name and route them, never dismiss as obsolete. Depth:
[ai-ml-data-science](../../ai-ml-data-science/SKILL.md) (CNN/RNN/specialist training),
[ai-rag](../../ai-rag/SKILL.md) + [ai-vector-brain](../../ai-vector-brain/SKILL.md) (encoder-only).

| Family | Still the right call when | Modern replacement (and when to prefer it) |
|---|---|---|
| **RNN / LSTM / GRU** | strict streaming, tiny footprint, very long *cheap* sequence with no parallel train need | Transformer / SSM-hybrid when you can batch and want quality |
| **CNN** | spatial image features, edge/on-device vision, small data | Vision Transformer (ViT) at scale + lots of data |
| **Encoder-only (BERT-class)** | encode text for **classification / NER / retrieval embeddings** | still the default embedding/classification backbone — not replaced by decoder LLMs |
| **Encoder-decoder (T5-class seq2seq)** | fixed **text-to-text transforms** (translate, summarize, parse) with paired data | decoder-only LLM when you want one general model + few-shot flexibility |
| **GAN / VAE** | fast/light image or latent generation, anomaly detection (VAE) | image-diffusion (DiT / latent diffusion) for quality at the cost of speed |

Rule: match the family to the *signal shape and deployment budget*, not to recency. An
encoder-only embedder behind a reranker is a 2026-correct choice, not a legacy one.

## Model Architecture: Dense vs MoE vs SSM vs Diffusion

Orthogonal to the lane and **invisible behind an API** — only a decision when self-hosting or
training. For an API caller, the knobs are model tier and thinking budget, not this.

| Architecture | Choose when (self-host/train) | Watch out |
|---|---|---|
| Dense Transformer | tight VRAM; simplest to fine-tune/reason about | priciest FLOPs/quality at frontier scale |
| Mixture-of-Experts (MoE) | cost-per-token at scale; frontier default (DeepSeek-V3/V4, Llama 4, Qwen3) | saves FLOPs not VRAM (all experts resident); routing/serving complexity |
| SSM / **hybrid** (Mamba-2/3, Jamba, Granite-4, Nemotron-H) | >100k-token sequences at high throughput; KV-cache memory binds | *pure* SSM trails + fails in-context learning — only the hybrid (SSM + a few attention layers) is competitive |
| Diffusion-LM (Mercury 2, LLaDA, DiffusionGemma) | raw tokens/sec dominates; code/structured text (~1000+ tok/s, usually AR-init + block diffusion) | autoregressive still leads deep reasoning; young ecosystem |

Sub-axes once self-hosting frontier-class weights:

| Sub-axis | Options | Default / when to move |
|---|---|---|
| MoE granularity | coarse (few large experts) · fine-grained (many small + low activation ratio) · shared-expert yes/no | fine-grained + shared expert (DeepSeek pattern) is the 2026 cost/quality lever at scale; Qwen3 drops the shared expert |
| Attention variant | MHA · **GQA** · MLA · NSA/DSA / sliding-window | GQA is the universal default; **MLA** for ~90%+ KV-cache compression (DeepSeek); **NSA**/sliding-window when long-context $/token or KV memory binds (NSA ~11× at 64k) — note NSA is the research precursor, not what shipped: DeepSeek-V3.2 runs the distinct, finer-grained **DSA** (DeepSeek Sparse Attention, via a lightning indexer) in production |

## Architecture Limitation → Workaround → Owning Skill

When the question is "what *limits* this component and how do I work around it?", the advisor
routes; the mechanics live in the deep catalogues — **build-time**
([ai-pretraining architecture-limitations-and-workarounds.md](../../ai-pretraining/references/architecture-limitations-and-workarounds.md))
and **serve-time**
([ai-llm-inference architecture-and-attention-serving.md](../../ai-llm-inference/references/architecture-and-attention-serving.md)).

| Limitation | Primary workaround | Owner |
|---|---|---|
| Attention O(n²) compute/memory | FlashAttention (exact), sparse/sliding/NSA, linear/SSM hybrids | build (mechanics) · serve (kernels) |
| Softmax attention sinks / massive activations / logit blow-up | QK-Norm, logit soft-capping, z-loss, off-by-one/gated softmax | build |
| KV-cache too large (long ctx / big batch) | MHA→GQA→MLA, KV quantization, PagedAttention | serve (GQA/MLA chosen at build) |
| RoPE can't extrapolate past trained length | train-short + extend with YaRN / NTK-aware / linear PI | build (train) · serve (apply, must match) |
| Dense FFN too expensive at scale | Mixture-of-Experts + load-balancing (router collapse is the trap) | build · ai-distributed-training |
| Training instability / loss spikes at depth/precision | pre-norm + RMSNorm, DeepNorm/T-Fixup, fp8 blockwise scaling, fp32 reductions | build |
| Lost-in-the-middle / long-context degradation | StreamingLLM + sinks, sliding window, ring attention, position-stratified eval | serve |
| W8A8 activation outliers break quantization | SmoothQuant (migrate scale to weights); or weight-only AWQ/GPTQ | serve |

## Transformer Family: Encoder vs Decoder vs Encoder-Decoder

Which *family* — not just which size — is a decision with hard limits. Decoder-only is the
default for general generation; switch when the limitation binds. Mechanics + contrast detail
in the build-time catalogue linked above.

| Family | Best at | Limitation | Switch / workaround |
|---|---|---|---|
| Encoder-only (BERT) | classification, dense embeddings (bidirectional) | cannot generate; MLM trains on ~15% of tokens (sample-inefficient) | ELECTRA (replaced-token-detection) for efficiency; switch families to generate |
| Decoder-only (GPT) | generation, in-context learning, scales simplest | causal mask wastes bidirectional context; no native fixed-length embedding | prefix-LM (bidirectional prompt); pooling/last-token for embeddings |
| Encoder-decoder (T5) | seq2seq with paired data (translation, summarization) | ~2× params; weaker few-shot ICL; needs paired data | use only for clean input→output transforms; else decoder-only generalizes better |

## Multimodal: Omni vs Specialist Pipeline

| Signal | Lean omni / VLM | Lean specialist -> LLM reasoning |
|---|---|---|
| Stage | validating a product, broad coverage | accuracy is the KPI, or scaling a proven flow |
| Cost at volume | acceptable | specialist often far cheaper per item |
| Hallucination tolerance | okay | must avoid (medical/legal/finance; non-AR ASR is structurally resistant) |
| Modalities | text + image (+ audio/video on omni) | one demanding modality (OCR, streaming ASR, imaging) |

Enterprises commonly run many specialists behind one reasoning LLM rather than a single omni
model. The modality gap does not close with frontier scale alone. IDP / OCR specialist routing
(AWS): **default** → Amazon Bedrock Data Automation (BDA — FM classify + extract, flat
per-doc pricing; Bedrock Pipeline mode wraps Textract as the OCR layer, March 2026);
**Textract standalone** for high-volume standardized docs (forms, tables, handwriting) or
95%+ compliance SLAs; **self-hosted OSS** → paperless-ngx (REST API, IMAP/consume-folder,
built-in OCR).

## Embedding / Retrieval Model Selection

A first-order choice with **lock-in: swapping the embedder forces a full re-index.** Decide on
five axes, in order:

| Axis | Question |
|---|---|
| Modality | text only, or image/code/multilingual? |
| Hosting | managed API vs self-hosted (open-weight embedders now lead public benchmarks); **AWS managed default → Amazon Nova 2 Multimodal Embeddings** (supersedes Titan, 2026; Matryoshka-tunable dims: 3072 / 1024 / 384 / 256) |
| Language scope | English-centric vs broad multilingual |
| Domain fit | general vs domain-tuned (legal/medical/code) |
| Retrieval architecture | dense · hybrid (sparse+dense) · late-interaction (multi-vector) |

Add a **cross-encoder reranker** by default (bi-encoder top-k → rerank top-n); it lifts
precision materially for tens of ms — skip only under a hard p99 budget. **AWS native
reranking**: Bedrock Rerank API (Cohere Rerank 3.5 / Amazon Rerank) — the managed quality
lever before building a custom reranker. Reserve late-interaction (ColBERT-style) for
demanding domain search where its storage cost pays off.

**AWS managed RAG surface fork** (choose by ownership scope):

- **Bedrock Knowledge Bases** — zero-ops S3 ingestion + retrieval component; the default when building a custom RAG stack on AWS
- **Amazon Kendra GenAI Index** — managed retriever reusable across Q Business + Bedrock KB; prefer when one index must serve multiple surfaces
- **Amazon Q Business** — fully managed end-to-end assistant; prefer when building an enterprise Q&A product, not a retrieval component
- **Amazon Bedrock Guardrails** — governance layer for regulated/safety-critical deployments: contextual grounding check (RAG faithfulness gate), PII redaction, denied topics, prompt-attack detection, Automated Reasoning; model-independent via ApplyGuardrail API

## Recsys / Ranking vs RAG

Both "retrieve then rank," but they are different lanes.

| Property | RAG | Recsys / ranking |
|---|---|---|
| Query | natural-language question | a user + context (no text query needed) |
| Signal | document relevance | implicit feedback (clicks, dwell, skips) |
| Latency budget | ~0.5–2s | <50ms |
| Catalog | document corpus | dynamic, millions of items |
| Success metric | answer quality / citations | A/B-tested business metric |
| Default shape | embed -> retrieve -> (rerank) -> generate | two-tower retrieve -> ranking model |

If it has implicit feedback + <50ms + a dynamic million-item catalog, build a recommender,
not RAG — even though the retrieval step looks similar.

## Adapt vs Train From Scratch

| Situation | Choice |
|---|---|
| A suitable base model exists | Adapt (prompt/RAG/fine-tune) |
| Research goal *is* pre-training, or no base fits | Train from scratch (ai-pretraining) |
| Need a cheaper model with same behavior | Distill from a larger model |

## Transferring Knowledge to a New Task

Several distinct mechanisms — pick by what's stable and what changes:

| Situation | Mechanism |
|---|---|
| Same model, new *facts* | RAG (retrieval) — no training |
| Same task family, new domain, have labels | Fine-tune / adapter (LoRA) on the base |
| Big model -> small cheap model, same behavior | Distillation (teacher -> student) |
| Reasoning model -> small model, keep reasoning | Reasoning distillation (train on teacher traces, e.g. R1-style) |
| Vision/audio backbone -> new downstream task | Transfer learning: freeze backbone, train head |
| Tabular model -> related tabular task | Retrain trees; or a tabular foundation model (TabPFN) transfers via in-context learning |

## How to Scale (Which Axis)

"Scale" is ambiguous — clarify which axis, because the answer differs:

| Axis the user means | Move | Deep skill |
|---|---|---|
| Better quality from more data/params | Scaling-law sizing (Chinchilla) | [ai-scaling-laws](../../ai-scaling-laws/SKILL.md) |
| Better quality without retraining | **Test-time compute**: thinking budget, best-of-N, verifier/reward-model selection | [ai-llm](../../ai-llm/SKILL.md) / [ai-evals](../../ai-evals/SKILL.md) |
| Train a model too big for one GPU | FSDP / ZeRO / parallelism | [ai-distributed-training](../../ai-distributed-training/SKILL.md) |
| Serve more traffic / lower latency | Batching, quantization, routing | [ai-llm-inference](../../ai-llm-inference/SKILL.md) |
| Handle more data in the pipeline | Data-lake / streaming infra | [data-lake-platform](../../data-lake-platform/SKILL.md) |

Test-time compute is a primary lever, not an afterthought: spending more at inference (longer
reasoning, parallel samples + a verifier) lifts quality without retraining — but trades directly
against latency and cost, so budget it per query class.

## Vetting a New Architecture

Leaderboard rank is a *filter, not a verdict*. Adopt deliberately:

| Step | Do |
|---|---|
| Filter | use public benchmarks only to eliminate; prefer contamination-resistant, unsaturated ones |
| Golden set | score 50–200 real examples from *your* task (deterministic + LLM-judge + some human) |
| Hold constant | same eval, same inputs across candidates — or you're measuring the harness |
| Settle | wait a couple weeks post-release; verify version-specific claims against primary sources |
| Output | often a **routing policy** (which approach per task class), not a single winner |

Scout with [research-arxiv-scout](../../research-arxiv-scout/SKILL.md) /
[research-scout](../../research-scout/SKILL.md); grade with
[ai-evals](../../ai-evals/SKILL.md).

## Emerging Architecture Classes (mid-2026)

Know they exist; don't bet a build on them yet. Most are research-to-early-production — flag
them so you neither miss nor over-adopt. These move monthly; verify status against primary
sources before recommending, and default to "named but not yet load-bearing" unless your own
golden-set eval says otherwise.

| Class | Examples | Status / where it matters |
|---|---|---|
| Tokenizer-free / byte-level | BLT (Byte Latent Transformer), ByteFlow | Research-strong; removes the tokenizer, robust to noisy/multilingual bytes |
| JEPA / latent-predictive | V-JEPA 2 | Early production for robotics/video & world understanding (not text gen) |
| World models | Genie 3, Marble/World Labs | Commercial beta; relevant to agents/embodied/sim, not chat |
| Looped / recurrent-depth | Ouro, latent-reasoning transformers | Research; reasoning without emitting explicit CoT tokens |
| Diffusion-LM | Mercury 2, DiffusionGemma, LLaDA | Production in speed-critical code/structured-text niches; DiffusionGemma (Jun 2026, open) vs the closed Gemini Diffusion research demo — name the one actually available (see model-architecture axis) |
