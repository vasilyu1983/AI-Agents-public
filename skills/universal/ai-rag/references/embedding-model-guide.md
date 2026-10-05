# Embedding Model Selection Guide

Choose embedding models by fit, not by leaderboard screenshots.

---
## Table of Contents

- [Selection Criteria](#selection-criteria)
- [Durable Heuristics](#durable-heuristics)
- [Model Families To Check Live](#model-families-to-check-live)
- [Evaluation Workflow](#evaluation-workflow)
- [Matryoshka / Reduced Dimensions](#matryoshka--reduced-dimensions)
- [Anti-Patterns](#anti-patterns)
- [Checking Live Standings](#checking-live-standings)
- [Training and Domain Adaptation: The Escalation Ladder](#training-and-domain-adaptation-the-escalation-ladder)
  - [Rung 0: Prove the Rest of the Pipeline First](#rung-0-prove-the-rest-of-the-pipeline-first)
  - [Contrastive Training Fundamentals](#contrastive-training-fundamentals)
  - [Negative-Example Taxonomy](#negative-example-taxonomy)
  - [MNR Loss and In-Batch Negatives](#mnr-loss-and-in-batch-negatives)
  - [Rung 1: Fine-Tune an Existing Model, Not From Scratch](#rung-1-fine-tune-an-existing-model-not-from-scratch)
  - [Rung 2: Augment Scarce Labels](#rung-2-augment-scarce-labels)
  - [Rung 3: Adaptive Pretraining for Domain Shift](#rung-3-adaptive-pretraining-for-domain-shift)
  - [Escalation Ladder Summary](#escalation-ladder-summary)
- [Adjacent Task Routing](#adjacent-task-routing)

---

## Selection Criteria

| Criterion | Questions to answer |
|-----------|---------------------|
| Domain fit | Is the corpus general, multilingual, code-heavy, legal, medical, or product-specific? |
| Latency | Is query-time embedding on the critical path? |
| Cost | Can you afford managed APIs for indexing and query traffic? |
| Deployment | Do you need self-hosting, residency, or air-gapped operation? |
| Context length | Do your chunks or queries exceed short-token embedders? |
| Dimensionality | Does storage or index memory pressure require lower dimensions? |

## Durable Heuristics

- Use one document embedding family and one query embedding family unless the provider explicitly supports asymmetric retrieval.
- Reindex whenever embedding model, dimension, or normalization changes.
- Do not choose by benchmark average alone; test on your own retrieval set.
- If storage is tight, use lower dimensions only after measuring recall loss.

## Model Families To Check Live

- Bedrock-hosted (AWS-native): Amazon multimodal and text embedding families (check the current Bedrock embeddings catalog for dimensions, context length, languages, and which models are legacy)
- Managed APIs: OpenAI, Cohere, Voyage AI, Jina
- Open-weight or self-hosted: BGE, GTE, E5, NV-Embed, Sentence Transformers families
- Multilingual: BGE-M3, multilingual E5, provider multilingual offerings
- Code retrieval: code-specialized embedders or hybrid lexical + semantic retrieval

## Evaluation Workflow

1. Pick 2-4 candidate embedding families.
2. Keep chunking, filtering, and reranking constant.
3. Reindex a representative slice.
4. Measure recall@k, MRR, nDCG, latency, and cost.
5. Keep the simplest option that meets product targets.

## Matryoshka / Reduced Dimensions

Use dimension reduction only when index size or memory is a real bottleneck. Keep a baseline at full dimension and compare retrieval quality before adopting a smaller shape.

## Anti-Patterns

- Mixing embeddings from different model versions in one index
- Assuming higher dimensions always win
- Hard-coding volatile prices or leaderboard scores into durable docs
- Fine-tuning before proving that chunking, filters, and reranking are already well-tuned

## Checking Live Standings

Provider features, prices, context limits, and benchmark standing change with every model release, and different tracking sites disagree on exact scores. This guide names no leader. Before selecting an embedding model:

1. Check the current MTEB leaderboard at [huggingface.co/spaces/mteb/leaderboard](https://huggingface.co/spaces/mteb/leaderboard) for both the API tier and the open-weight tier, and treat any single-source ranking claim as provisional.
2. Verify license, context length, dimensions, and pricing from the provider's primary docs.
3. Shortlist two or three candidates and run them on your own retrieval eval set.

**Judgment call, not just a ranking lookup:** the top MTEB score is rarely the right selection criterion in isolation. Weight it against license (Apache-2.0 vs. proprietary API vs. non-commercial), context length fit for your chunk size, multilingual coverage if the corpus needs it, and reindex cost if you might need to switch later — a Matryoshka-capable model that lets you shrink dimensions without a full reindex is often worth more than 1-2 MTEB points.

## Training and Domain Adaptation: The Escalation Ladder

Everything above assumes an off-the-shelf model will do. This section is for when it will not: domain retrieval where the corpus vocabulary, entity names, or notion of "relevant" diverges from what general-purpose embedders were trained on. Climb this ladder one rung at a time and re-measure at each step — every rung costs more data, more compute, and more maintenance surface than the one below it.

Concepts and terminology in this section follow Alammar & Grootendorst, *Hands-On Large Language Models* (O'Reilly, 2024), Ch. 10.

### Rung 0: Prove the Rest of the Pipeline First

Do not train anything until chunking, metadata filters, hybrid retrieval, and reranking are already tuned and their failures characterized. This is the existing anti-pattern in this file, restated because it is the most common reason a training project wastes a quarter: a reranker fixes many of the same symptoms as a fine-tuned embedder, at a fraction of the operational cost and with no reindex.

Escalate past Rung 0 only when you can name the failure in retrieval terms — e.g. "recall@20 is fine but the correct chunk never ranks top-3, and the near-misses are lexically similar in-domain documents the model cannot separate."

### Contrastive Training Fundamentals

Embedding models are trained so that similar documents land closer in vector space and dissimilar ones land further apart. The mechanism is **contrastive learning**: feed the model pairs (or triplets) of similar and dissimilar documents so it learns what makes them similar or different, rather than trying to learn a definition of similarity in isolation.

The pedagogical framing is worth keeping, because it drives every data decision downstream: teaching a model what a dog is by listing "tail, nose, four legs" is underdetermined — a cat matches too. Contrast supplies the missing information by asking "why is this a dog *and not* a cat?" Applied to retrieval: your training data must encode not just what a correct answer looks like, but what a plausible-but-wrong answer looks like in your domain.

Two things are required to run contrastive learning:

1. **Data** constituting similar/dissimilar pairs.
2. **A loss function** defining how the model measures and optimizes similarity.

The dominant framework is `sentence-transformers`, whose **bi-encoder** (SBERT) architecture embeds each text independently through a shared-weight Siamese network with a pooling layer, so embeddings can be precomputed and compared with cosine similarity. Contrast with a **cross-encoder**, which takes two texts jointly and outputs a similarity score. Cross-encoders generally achieve better accuracy but do not produce embeddings — which is exactly the reranker-vs-retriever split already used elsewhere in this skill. That is also why a cross-encoder reranker is the cheaper first move at Rung 0: it buys cross-encoder accuracy on a shortlist without needing bi-encoder training.

### Negative-Example Taxonomy

Positives are usually easy to collect (question/answer, title/abstract, query/clicked-doc). Negatives are where retrieval quality is won or lost. Three tiers, in increasing order of both value and cost to produce:

| Tier | How it is produced | What the model learns |
|------|--------------------|-----------------------|
| **Easy negatives** | Randomly sample other documents | Coarse topical separation; the discrimination task is trivially easy |
| **Semi-hard negatives** | Use a pretrained embedding model, take high cosine-similarity neighbours | Topical similarity, but these are similar *sentences*, not plausible wrong *answers* |
| **Hard negatives** | Manual labelling, or filtering/generating with an LLM judge | Fine-grained distinctions — the nuance that actually decides top-3 ranking |

**Why hard negatives matter most.** A hard negative is very similar to the query but is the wrong answer. The book's worked example: for the question "How many people live in Amsterdam?", the correct answer is "Almost a million people live in Amsterdam." A good hard negative mentions both Amsterdam *and* a population figure while still being wrong — "More than a million people live in Utrecht, which is more than Amsterdam." It is related to the question but is not the answer.

Because hard negatives make the task harder, the model must learn more nuanced representations, and the book reports that performance "generally improves quite a bit." Direction only — treat any specific magnitude as corpus-dependent and measure it on your own retrieval set.

The practical consequence for data budgeting: building positive pairs is generally straightforward, but adding hard negative pairs significantly increases the difficulty of creating quality data. Budget the majority of your labelling effort there, not on collecting more positives.

**Retrieval-specific note:** a semi-hard negative mined by cosine similarity can accidentally be a *true* positive your labels missed (an unlabelled correct answer). Training on it teaches the model to push a correct document away. Screen mined negatives against known positives before training.

### MNR Loss and In-Batch Negatives

**Multiple negatives ranking (MNR) loss** — also known as InfoNCE or NTXentLoss — is the standard choice for retrieval-style training. It takes positive pairs, or triplets of a positive pair plus an unrelated sentence. Negative pairs are constructed by mixing one positive pair with another: pair a paper title with a completely different abstract. These are **in-batch negatives**. Embeddings are computed, cosine similarity applied, and the result optimized as a classification task with cross-entropy loss.

**The batch-size interaction is the operationally important part.** Larger batch sizes tend to work better with MNR loss, because a larger batch makes the task more difficult — the model must find the best matching sentence from a larger set of candidate pairs. Batch size is therefore not just a memory/throughput knob under MNR: it directly controls task difficulty and hence embedding quality. Tune it as a quality hyperparameter, and note the tension — MNR wants large batches, while memory-hungry losses force them down.

Note the relationship to the taxonomy above: in-batch negatives are *easy* negatives, since they are sampled from unrelated pairs and may be completely unrelated to the query. Large batches make easy negatives harder in aggregate, but they do not manufacture hard negatives. Explicitly mined hard negatives and a large batch are complementary, not substitutes.

### Rung 1: Fine-Tune an Existing Model, Not From Scratch

Training from scratch is possible but costly and time-consuming, and it is almost never the right first move for a retrieval project. `sentence-transformers` allows nearly any existing embedding model to be used as a base for fine-tuning — start from a model already trained on large general data and adapt it to your domain.

Mechanically, the change is small: swap the base model for a pretrained sentence-transformers checkpoint and keep the same MNR-loss training loop. The book's own comparison makes the case for reading benchmark deltas carefully rather than as a clean win — its fine-tuned pretrained model scored highest of its examples, but the authors immediately caveat that the pretrained base had already seen the full dataset while their from-scratch run used a 50,000-example subset. Do not port their numbers into your decision; the transferable lesson is that fine-tuning generally needs less data than creating a model and is the practical way to adapt an existing model to your domain.

Two data cautions that apply at this rung:

- Smaller datasets make training and fine-tuning less stable. Prefer larger datasets, assuming the data stays high quality.
- Freezing layers is possible but generally not advised — performance is often better with all layers unfrozen.

### Rung 2: Augment Scarce Labels

If you have only a few thousand labelled pairs — the common case — **Augmented SBERT** bridges the gap. It uses a slow, accurate cross-encoder to label a larger set of pairs, then trains the fast bi-encoder on the result:

1. Fine-tune a cross-encoder on the small annotated **gold** dataset (ground truth).
2. Create new sentence pairs.
3. Label them with the fine-tuned cross-encoder, producing a **silver** dataset (fully annotated, but predicted rather than ground truth).
4. Train the bi-encoder on gold + silver combined.

To test whether the silver data is actually earning its place, also train on gold alone; the performance difference indicates how much the silver set contributes.

### Rung 3: Adaptive Pretraining for Domain Shift

Use this rung when the target domain contains words and subjects absent from the source domain — the out-domain/in-domain gap that makes general embedders underperform on specialist corpora regardless of how many pairs you label.

Unsupervised techniques let you exploit an unlabelled domain corpus. Several exist (SimCSE, Contrastive Tension, TSDAE, GPL); **TSDAE** (Transformer-based Sequential Denoising Auto-Encoder) is the one the book focuses on for domain adaptation. It removes a percentage of words from an input sentence, encodes the damaged sentence with a pooling layer into an embedding, and has a decoder reconstruct the original sentence from that embedding — the more accurate the embedding, the more accurate the reconstruction. Conceptually similar to masked language modelling, but reconstructing the whole sentence rather than masked tokens. After training, keep the encoder; the decoder existed only to judge the embeddings. TSDAE pools on the `[CLS]` token rather than mean pooling — per the TSDAE paper this was more effective, because mean pooling loses position information.

**Adaptive pretraining** is the two-stage recipe that makes this useful:

1. Pretrain on your domain-specific corpus with an unsupervised technique (TSDAE, or masked language modelling on the base BERT model).
2. Fine-tune the result with a supervised training set — general supervised training or Augmented SBERT.

The property that makes this worth the extra stage: the supervised data in step 2 can be **out-of-domain**. Target-domain data is preferred, but out-domain data also works, because step 1 already grounded the model in the target domain. That is the escape hatch for a specialist corpus with no labelled pairs at all — unlabelled domain text plus a public supervised set.

Set expectations honestly: unsupervised techniques are generally outperformed by supervised ones and have difficulty learning domain-specific concepts on their own. Adaptive pretraining is a way to combine them, not a replacement for labels.

### Escalation Ladder Summary

| Rung | Move | Use when | Cost |
|------|------|----------|------|
| 0 | Chunking, filters, hybrid, reranker | Always — before any training | Lowest; no reindex |
| 1 | Fine-tune a pretrained embedder (MNR loss + hard negatives) | You have labelled in-domain pairs | Reindex + training loop |
| 2 | Augmented SBERT (gold + cross-encoder-labelled silver) | Only a few thousand labelled pairs | Adds a cross-encoder training stage |
| 3 | Adaptive pretraining (TSDAE/MLM, then supervised) | Target vocabulary and subjects diverge from source domain; little or no labelled data | Highest; two training stages |

Every rung at or above 1 changes the embedding space and therefore requires a full reindex — the reindex rule at the top of this file applies to your own fine-tunes exactly as it applies to swapping vendors. Version the model artifact alongside the index and keep the retrieval eval set fixed across rungs, or the comparisons are meaningless.

## Adjacent Task Routing

Embedding models built or tuned here are also the input to unsupervised corpus analysis. For clustering or thematically labelling a corpus rather than retrieving against it — topic discovery, taxonomy bootstrapping, exploring what a corpus actually contains before designing retrieval — route to [`../../ai-ml-data-science/references/text-clustering-topic-modeling.md`](../../ai-ml-data-science/references/text-clustering-topic-modeling.md).
