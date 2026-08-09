# When To Use What — Per-Approach Cheat Sheet

*Purpose: a fast "use it when / avoid it when" lookup for each major approach. For the
comparative tables, see [decision-matrices.md](decision-matrices.md). For depth, hand off to
the named deep skill.*

## Table of Contents

- [Classical ML / Trees](#classical-ml--trees)
- [Tabular Foundation Models](#tabular-foundation-models)
- [Deep Learning (Foundational Net Families)](#deep-learning-foundational-net-families)
- [Transformer / LLM](#transformer--llm)
- [Thinking Budget (Reasoning / Test-Time Compute)](#thinking-budget-reasoning--test-time-compute)
- [RAG](#rag)
- [Fine-tuning](#fine-tuning)
- [Post-Training / Alignment (RLHF, DPO, GRPO, RLVR)](#post-training--alignment-rlhf-dpo-grpo-rlvr)
- [AI Agents](#ai-agents)
- [Multimodal (Omni vs Specialist)](#multimodal-omni-vs-specialist)
- [Embedding / Retrieval Models](#embedding--retrieval-models)
- [Recsys / Ranking](#recsys--ranking)
- [Model Architecture (Dense / MoE / SSM / Diffusion)](#model-architecture-dense--moe--ssm--diffusion)
- [Finding & Vetting New Architectures](#finding--vetting-new-architectures)

---

## Classical ML / Trees

- **Decision Tree** — use for an interpretable baseline or a readable rule; avoid when
  accuracy matters (single trees are high-variance).
- **Random Forest** — use for a robust low-tuning baseline; avoid when you need the last
  few points of accuracy and have a tuning budget (boosting beats it).
- **XGBoost** — use as the general strong tabular default with regularization and tuning;
  avoid when data is too large to train comfortably (go LightGBM).
- **LightGBM** — use for large datasets where training speed matters (histogram + leaf-wise
  growth); avoid on tiny data (leaf-wise overfits).
- **CatBoost** — use when many categorical features and minimal preprocessing are wanted, or
  target-leakage is a risk (ordered boosting); avoid when all-numeric and speed-critical.

Why boosting beats one deep tree: sequential residual-fitting reduces bias. Why random
forest reduces variance: decorrelated bagging.

## Tabular Foundation Models

- **Tabular foundation models (TabPFN-3 / TabICL v2)** — use within the current version's size
  envelope (TabPFN-3 ~1M rows as of May 2026; strongest on small/medium) when raw accuracy
  matters and you have no tuning budget: it beats tuned GBDTs in a single in-context forward
  pass and can be distilled to a compact MLP/tree for low-latency serving. **TabICL v2** is the
  open-source alternative when TabPFN's non-commercial license blocks you. Avoid beyond the
  FM envelope or on very wide tables, where GBDTs still win. (Limits/licenses are volatile and
  version-specific — verify before quoting.)
- Deep skill: [ai-ml-data-science](../../ai-ml-data-science/SKILL.md).

## Deep Learning (Foundational Net Families)

Match the net family to the *signal shape*, not to recency — these are not obsolete:

- **CNN** — use for spatial image features, edge/on-device vision, small image data; move to
  **Vision Transformer (ViT)** at scale with lots of data.
- **RNN / LSTM / GRU** — use for strict streaming or tiny-footprint sequence models; otherwise
  Transformers (or SSM-hybrids) win once you can batch and parallelize training.
- **Encoder-only (BERT-class)** — the default backbone for text **classification / NER /
  retrieval embeddings**; not replaced by decoder-only LLMs (it's what sits behind RAG/rankers).
- **Encoder-decoder (T5-class seq2seq)** — use for fixed **text-to-text transforms**
  (translate, summarize, parse) with paired data; a decoder-only LLM wins when you want one
  general few-shot model.
- **GAN / VAE** — use for fast/light image or latent generation and anomaly detection (VAE);
  move to **image diffusion (DiT / latent diffusion)** for generation quality at a speed cost.
- Avoid all of these on small structured/tabular data — gradient-boosted trees win with less
  data and cost.
- Deep skill: [ai-ml-data-science](../../ai-ml-data-science/SKILL.md) (CNN/RNN/specialist
  training); encoder-only embedders → [ai-rag](../../ai-rag/SKILL.md) +
  [ai-vector-brain](../../ai-vector-brain/SKILL.md).

## Transformer / LLM

- Use for natural-language understanding/generation, few-shot tasks, and flexible
  instruction-following.
- Avoid for tabular prediction (trees), for deterministic logic a plain function handles,
  and for routing/retry decisions an `if` statement already knows.
- Deep skill: [ai-llm](../../ai-llm/SKILL.md).

## Thinking Budget (Reasoning / Test-Time Compute)

- By 2026 this is a **dial on one model** (extended-thinking budget / auto-routing), not a
  separate "reasoning model" you switch to — raise the budget rather than the product.
- Use more thinking when the failure is *multi-step logic, planning, or math*; it closes a
  reasoning gap cheaply and is worth trying *before* fine-tuning. For harder cases add
  best-of-N sampling with a verifier.
- Avoid on shallow, latency- or cost-critical tasks where the overhead is wasted, and when
  the real gap is knowledge (use RAG) or behavior (fine-tune), not reasoning. Budget it: more
  thinking = more tokens = more $ + latency.
- To keep reasoning in a cheaper model, distill from the teacher's reasoning traces.
- Deep skill: [ai-llm](../../ai-llm/SKILL.md).

## RAG

- Use when answers need *current or private* knowledge, or citations/grounding, especially
  for large/fresh corpora.
- Avoid as a fix for weak instructions or for *behavior* problems (RAG changes knowledge,
  not behavior); also reconsider when a small/static corpus fits affordably in a
  long-context window with prompt caching — long context can obviate RAG there.
- For domain-specific RAG that also needs behavior shaping, combine via RAFT
  (retrieval-augmented fine-tuning).
- Watch long-context's silent failure (multi-fact recall degrades quietly) and its cost cliff
  at volume; reserve GraphRAG / agentic RAG for multi-hop or entity-relational queries that
  flat vector RAG answers poorly. Think "context engineering" — RAG is one input channel.
- Pick the embedder + reranker deliberately (see below) — it's a lock-in decision, not config.
- **AWS managed RAG path**: fork by scope — **Bedrock Knowledge Bases** (zero-ops S3
  ingestion + retrieval component, default for custom RAG stacks on AWS); **Amazon Kendra
  GenAI Index** (managed retriever reusable across Q Business + KB, prefer when one index
  serves multiple surfaces); **Amazon Q Business** (fully managed assistant end-to-end, prefer
  when building an enterprise Q&A product rather than a retrieval component). For
  regulated/safety-critical deployments add **Amazon Bedrock Guardrails** as the governance
  layer (contextual grounding check for RAG faithfulness, PII redaction, Automated Reasoning).
- Deep skill: [ai-rag](../../ai-rag/SKILL.md).

## Fine-tuning

- Use when a *stable, repeated* behavior/format/style gap survives prompt + RAG fixes, and
  you have quality data + eval coverage. This is **SFT** — the supervised baseline, do it first.
- Avoid for information that should live in retrieval, and as a first resort.
- Deep skill: [ai-llm](../../ai-llm/SKILL.md).

## Post-Training / Alignment (RLHF, DPO, GRPO, RLVR)

- Use the rung *after* SFT, when a **preference, safety, or reasoning** gap survives supervised
  fine-tuning and you can produce a reward signal. Pick by the signal you have:
  **DPO** (or KTO/ORPO/SimPO) for pairwise preferences with the least machinery; **PPO** for
  classic reward-model RLHF; **GRPO** when you can score many samples per prompt (drops the
  critic); **RLVR** when a verifiable checker (math/code/tests) is the reward — the standard
  2026 reasoning recipe. **RLAIF / Constitutional AI** scales preference labels via model-as-judge.
- Avoid post-training when the gap is missing *knowledge* (RAG) or *format* (SFT); avoid PPO/GRPO
  when DPO suffices. Always pair with an eval harness — preference RL over-optimizes (reward
  hacking / Goodhart) silently.
- Deep skill: [ai-post-training](../../ai-post-training/SKILL.md).

## AI Agents

- Use when the task needs tools, external actions, or multi-step planning. Standardize tool
  access via MCP rather than bespoke per-tool glue.
- Avoid when a single LLM call or a linear tool-use workflow suffices; avoid multi-agent
  until a single agent provably can't — on sequential, write-heavy tasks the coordination
  overhead can *lower* quality and multiply cost. Multi-agent earns its keep only for
  genuinely parallel, independent subtasks or work exceeding one context window.
- For narrow, high-volume, repetitive agent steps, a small language model (SLM) is often
  cheaper and fast enough — reserve the frontier model for the hard planning steps.
- Set **autonomy** as a separate dial from architecture (per-action approval ↔ human-on-the-
  loop monitoring). Default to the lowest tier (task → workflow → agent) that meets the need.
- Deep skill: [ai-agents](../../ai-agents/SKILL.md).

## Multimodal (Omni vs Specialist)

- Use a unified **omni / VLM** model to validate fast and for broad, light coverage (visual
  Q&A, casual OCR/audio).
- Switch to a **specialist per modality → LLM reasoning** when accuracy is the KPI, cost at
  volume binds, or hallucination is unacceptable (medical imaging, high-volume OCR,
  real-time/streaming ASR — non-autoregressive ASR is structurally hallucination-resistant).
  IDP / OCR routing (AWS): **default** → Amazon Bedrock Data Automation (BDA — FM classify
  and extract, flat per-doc pricing; Bedrock Pipeline mode wraps Textract as the OCR layer,
  March 2026); **Textract standalone** for high-volume standardized docs (forms, tables,
  handwriting) or 95%+ compliance SLAs; **self-hosted OSS** → paperless-ngx (REST API,
  IMAP/consume-folder, built-in OCR).
- Avoid assuming one omni model covers everything; enterprises run many specialists behind a
  reasoning LLM. The modality gap does not close with frontier scale alone.
- Deep skills: [ai-prompt-engineering](../../ai-prompt-engineering/SKILL.md),
  [ai-ml-data-science](../../ai-ml-data-science/SKILL.md).

## Embedding / Retrieval Models

- Use a strong general embedder + a cross-encoder reranker as the default retrieval stack;
  open-weight embedders now lead public benchmarks.
- Decide on five axes — modality → hosting → language scope → domain fit → retrieval
  architecture (dense / hybrid / late-interaction) — because **swapping the embedder forces a
  full re-index**. This is architecture, not config.
- **AWS-native managed default**: Amazon Nova 2 Multimodal Embeddings (supersedes Titan,
  2026) — reach for it when staying within managed Bedrock and multimodal or text embeddings
  are both needed.
- Avoid skipping the reranker except under a hard p99 budget; reserve late-interaction
  (ColBERT-style) for demanding domain search where its storage cost pays off.
- Deep skills: [ai-rag](../../ai-rag/SKILL.md), [ai-vector-brain](../../ai-vector-brain/SKILL.md).

## Recsys / Ranking

- Use a recommender (two-tower retrieve → ranking model) when the system ingests implicit
  feedback (clicks, dwell, skips), must return in <50ms, and ranks a dynamic million-item
  catalog — even though it "retrieves then ranks" like RAG.
- Avoid modeling this as vector-RAG: the latency budget, implicit-feedback training, and
  business-metric coupling make it a distinct lane.
- Deep skill: [ai-ml-data-science](../../ai-ml-data-science/SKILL.md) + RecSys literature.

## Model Architecture (Dense / MoE / SSM / Diffusion)

- **Ignore this axis when calling a hosted API** — the architecture is invisible; tune model
  tier and thinking budget instead.
- When self-hosting or training: dense for tight VRAM and simplicity; **MoE** for cost-per-
  token at scale (saves FLOPs not VRAM; fine-grained + shared-expert is the 2026 design lever);
  **SSM/hybrid** (Mamba-2/3, Jamba, Granite-4) for very long sequences at high throughput —
  note *pure* SSM isn't competitive, only the hybrid; **diffusion-LM** (Mercury 2, Gemini
  Diffusion, LLaDA) when raw tokens/sec dominates on code/structured text (AR still leads deep
  reasoning).
- Attention variant: **GQA** is the universal default; **MLA** for ~90%+ KV-cache compression
  (DeepSeek); **NSA**/sliding-window when long-context $/token or KV memory binds.
- Deep skills: [ai-llm-inference](../../ai-llm-inference/SKILL.md) (serving),
  [ai-distributed-training](../../ai-distributed-training/SKILL.md) (training).

## Finding & Vetting New Architectures

- Use when the right approach may be newer than what's catalogued here. Scout release feeds,
  preference leaderboards, and one synthesis newsletter; delegate scouting to
  [research-arxiv-scout](../../research-arxiv-scout/SKILL.md) /
  [research-scout](../../research-scout/SKILL.md).
- Treat leaderboards as an *elimination filter only*; vet on a 50–200-example golden set from
  your own task with the problem held constant, and let a release settle before betting on it.
- Avoid adopting on hype or rejecting on unfamiliarity; the output is often a routing policy,
  not a single winner. Grade with [ai-evals](../../ai-evals/SKILL.md).
- **Mid-2026 emerging classes to name but not yet bet on:** tokenizer-free / byte-level (BLT),
  JEPA / latent-predictive (V-JEPA 2, for robotics/video), world models (Genie 3), looped /
  recurrent-depth transformers (Ouro, latent reasoning), and diffusion-LMs (covered above).
  Know they exist; default to "named, not load-bearing" until your own golden set says otherwise.
  These move monthly — verify status against primary sources.
