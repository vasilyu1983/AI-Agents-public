# Text Clustering and Topic Modeling

Use this reference when a corpus of unlabeled documents needs structure: exploratory grouping, discovering themes, sanity-checking a proposed label taxonomy before annotation, finding mislabeled or outlier documents, or building a topic view over support tickets, reviews, abstracts, or logs. The center of gravity is a modular pipeline — embed, reduce, cluster, represent — where each stage is a replaceable component rather than a monolithic algorithm.

Prompting, generation quality, and RAG retrieval design belong in `ai-llm` and `ai-rag`. Serving and monitoring a topic model in production belongs in `ai-mlops`.

## Contents

- [The four-stage pipeline](#the-four-stage-pipeline)
- [Stage 1: embed the documents](#stage-1-embed-the-documents)
- [Stage 2: reduce dimensionality](#stage-2-reduce-dimensionality)
- [Stage 3: cluster the reduced embeddings](#stage-3-cluster-the-reduced-embeddings)
- [Stage 4: represent the topics with c-TF-IDF](#stage-4-represent-the-topics-with-c-tf-idf)
- [Optional stage: representation-model reranking](#optional-stage-representation-model-reranking)
- [Why modularity is the design point](#why-modularity-is-the-design-point)
- [Choosing this pipeline vs plain k-means over embeddings](#choosing-this-pipeline-vs-plain-k-means-over-embeddings)
- [Evaluation and interpretation](#evaluation-and-interpretation)
- [Known traps](#known-traps)
- [Design checklist](#design-checklist)

## The four-stage pipeline

```text
documents
  |
  v  embedding model (semantic-similarity-optimized encoder)
high-dimensional document vectors
  |
  v  dimensionality reduction (UMAP)
low-dimensional vectors (typically 5-10 dims)
  |
  v  density clustering (HDBSCAN) -> clusters + explicit outlier label
document groups
  |
  v  c-TF-IDF over the cluster's bag-of-words
ranked keywords per cluster (= topic)
  |
  v  optional representation model (KeyBERT-style, MMR, or LLM label)
refined keywords or a single human-readable topic label
```

Stages 1-3 are text *clustering*. Stage 4 turns clusters into *topics* by attaching an interpretable representation. This split — clustering and representation being largely independent of each other — is what makes the pipeline swappable end to end. BERTopic (Grootendorst, arXiv 2203.05794) is the framework that packages these stages; the pipeline shape is usable without the library.

## Stage 1: embed the documents

Encode each document with an embedding model chosen for semantic similarity, not for generation. Clustering quality is bounded here: if the encoder does not place semantically similar documents near each other, no downstream stage recovers it.

Practical selection notes:

- Pick from a benchmark that scores *clustering* tasks specifically (MTEB reports clustering as its own task family). A model that ranks well on retrieval is not automatically good at clustering.
- Smaller encoders are often the right call. Embedding a full corpus is a one-pass cost over every document, so encoder size directly sets the wall-clock floor of the whole pipeline.
- `sentence-transformers` is the usual entry point and is BERTopic's default embedding backend, but any encoder that yields a fixed-length vector per document works.
- Cache embeddings. Every later stage is cheap to re-run; re-embedding is not. Both the clustering step and the topic model should accept precomputed embeddings.

Long documents need a chunking decision before this stage — decide whether the unit of analysis is a document, a section, or a paragraph, because that unit is what gets clustered.

## Stage 2: reduce dimensionality

Raw embedding dimensionality is hostile to density-based clustering: as dimensions grow, the number of possible subspaces grows exponentially and distance contrasts flatten, so density becomes hard to estimate. Reducing first gives the cluster model a space where local density is meaningful.

- UMAP is the usual choice over PCA here because it handles nonlinear structure better; PCA remains a reasonable fast baseline. Both are compression, not dimension deletion — information is lost either way, and the trade-off between aggressive reduction and information retention is a tuning decision, not a solved one.
- Target a small number of components — roughly 5-10 dimensions is the commonly used band for preserving global structure while making clustering tractable.
- Use a cosine metric rather than Euclidean when working from normalized text embeddings; Euclidean distance degrades in high-dimensional embedding spaces.
- Setting a `min_dist` near zero produces tighter, more separated clusters, which is what the downstream density model wants. This is a different setting than you would use for a pretty 2D picture.
- Fixing a random seed in UMAP makes results reproducible across sessions but disables parallelism and slows fitting. Take that trade knowingly.

Keep two reductions separate: the **clustering reduction** (5-10 dims, tuned for cluster quality) and the **visualization reduction** (2 dims, tuned for a readable plot). Do not cluster on the 2D projection — a 2D map exaggerates and compresses distances, so clusters it shows apart may not be apart and vice versa.

Libraries: `umap-learn`, or scikit-learn's PCA.

## Stage 3: cluster the reduced embeddings

HDBSCAN is the default because of two properties that matter for exploratory text work:

1. **It does not require the number of clusters up front.** In genuinely exploratory work you do not know how many themes exist, and guessing k biases the result toward the guess.
2. **It does not force every document into a cluster.** Documents in sparse regions are assigned an explicit outlier label (conventionally `-1`) rather than being pulled into the nearest group.

Outlier handling is the operationally significant part. A centroid method assigns every niche or off-topic document to *some* cluster, silently contaminating that cluster's representation. HDBSCAN quarantines them instead. The consequence: expect a large outlier bucket on a heterogeneous corpus, and treat its size as a diagnostic, not a defect. Options when the outlier share is too large for the use case:

- Lower the minimum cluster size to allow smaller, denser groups to form.
- Reassign outliers after the fact to their nearest topic (BERTopic exposes an outlier-reduction step for this), accepting that reassignment reintroduces the contamination HDBSCAN avoided.
- Swap in k-means if the application genuinely requires every document to have a label.

The minimum-cluster-size parameter is the main lever on granularity: it sets the smallest group the model will call a cluster, so lowering it yields more, finer topics.

Libraries: `hdbscan`, or scikit-learn's HDBSCAN implementation.

## Stage 4: represent the topics with c-TF-IDF

A cluster is a set of document IDs; it is not yet a topic. The representation stage attaches interpretable keywords.

Standard TF-IDF weights terms within a *document*. The cluster-level analogue, **c-TF-IDF** (class-based TF-IDF), does the same at the *cluster* level:

1. Concatenate all documents in a cluster and build one bag-of-words per cluster, giving a term frequency per cluster rather than per document (the "c-TF" term). A `CountVectorizer` produces this.
2. Weight each term by an inverse-document-frequency factor computed across clusters — the log of the average term frequency across all clusters divided by that term's total frequency — so terms common to every cluster are downweighted and terms distinctive to one cluster are upweighted.
3. Multiply c-TF by IDF. Rank the vocabulary by the product; the top terms are the topic representation, with higher weight meaning more representative.

Two things follow from this construction:

- It is a classical bag-of-words method — fast, deterministic, no model call, and it does not use the semantics of the embedding space. That is both its speed advantage and its weakness.
- It is computed from cluster membership alone and does not depend on which embedding, reduction, or cluster model produced the membership. This independence is what makes the whole pipeline modular.

Because c-TF-IDF ignores semantics, stop words can survive into representations and near-duplicate word forms (e.g. singular/plural variants of the same stem) crowd out distinct terms. Both are addressed in the next stage rather than by abandoning c-TF-IDF.

## Optional stage: representation-model reranking

The c-TF-IDF output is a cheap first-pass representation. A reranking or "representation" model takes that candidate set and improves it with a slower, more powerful technique — the same rerank-a-cheap-candidate-set pattern used in neural search.

Three families, stackable:

| Approach | Mechanism | What it fixes | Cost it adds |
|---|---|---|---|
| Embedding-based keyword reranking (KeyBERT-style) | compare candidate keyword embeddings against the topic's average document embedding, rerank by cosine similarity | removes stop words, favors semantically central terms | one embedding pass over candidates per topic; can drop informative domain abbreviations the encoder represents poorly |
| Maximal marginal relevance (MMR) | iteratively pick the next keyword that is relevant to the topic but dissimilar to already-chosen keywords, controlled by a diversity parameter | redundancy — collapses near-duplicate word forms, widens coverage | trims a larger candidate set (say 30) down to a diverse smaller set (say 10) |
| Generative LLM labeling | prompt an LLM with the topic's keywords plus a few representative documents, ask for a short label | produces a single human-readable topic name instead of a keyword list | one model call per topic |

### The cost pattern that makes LLM labeling viable

This is the key operational point of the whole pipeline. Naively, using an LLM to characterize topics means calling it once per *document* — millions of calls on a large corpus. In this architecture the LLM is called once per *topic*: hundreds of calls, not millions, regardless of corpus size. The prompt carries the c-TF-IDF keywords plus a small subset of the most representative documents (selected by cosine similarity of their c-TF-IDF values against the topic's), typically a handful.

The economics invert as a result. Corpus size drives the embedding cost (linear in documents) but not the labeling cost (linear in topics). A pipeline that would be prohibitive as per-document LLM classification becomes routine.

Two consequences worth stating plainly: label quality tracks model capability — small instruction-tuned models produce labels that are correct but too generic to be useful, while larger models produce labels specific enough to act on — and the keyword representations remain worth keeping alongside the generated label. No labeler is perfect, keywords stay directly traceable to the corpus, and a topic can carry several representations at once (keyword-reranked, MMR-diversified, LLM-labeled) as different views on the same cluster.

## Why modularity is the design point

Each stage consumes the previous stage's output and nothing else, so any stage can be replaced without touching the others:

- A better encoder ships — swap stage 1, keep everything downstream.
- Outliers are unacceptable for the application — swap HDBSCAN for k-means in stage 3, c-TF-IDF is unaffected.
- Representations need improving — re-run stage 4 and the representation model alone, with no re-embedding, no re-reduction, and no re-clustering. That last property is what makes representation iteration cheap enough to do interactively.

The same seam supports variant workflows on one base pipeline — guided or seeded topics, semi-supervised topics, hierarchical topics, topics over time, online/incremental fitting, and zero-shot topic assignment are all changes to one or two stages rather than different algorithms.

Treat this as an architectural property to preserve in your own implementation, not just a library feature: keep embeddings, cluster assignments, and representations as separate persisted artifacts, and the pipeline stays cheap to iterate.

## Choosing this pipeline vs plain k-means over embeddings

| Situation | Use |
|---|---|
| Number of themes unknown; corpus genuinely exploratory | UMAP + HDBSCAN |
| Corpus is heterogeneous with real off-topic or niche documents you want isolated | UMAP + HDBSCAN (outliers are the feature) |
| Every document must receive a label — routing, assignment, exhaustive coverage | k-means (or HDBSCAN plus outlier reassignment) |
| Cluster count is fixed by an external constraint (a known taxonomy, a fixed number of queues) | k-means |
| Clusters need to be stable and cheaply re-derivable at fixed k across refreshes | k-means |
| Corpus is small enough that density estimation is unreliable | k-means, and treat the result as provisional |
| Interpretable topic labels are the deliverable | either — the c-TF-IDF and representation stages work on any cluster assignment |

k-means is not a fallback for the unsophisticated; it is the right answer when full coverage or a fixed k is a real requirement. The reverse also holds — forcing k on an exploratory corpus manufactures topic boundaries that the data does not contain.

## Evaluation and interpretation

Topic models have no ground truth by construction, so evidence has to be assembled deliberately:

- **Read documents from each cluster.** Sample several documents from a cluster and check that the c-TF-IDF keywords actually describe them. This manual pass is not optional overhead; it is the primary validity check, and any visualization is only an approximation of the embedding space.
- **Search for topics you expect.** Query the model with a known theme and confirm a coherent topic ranks highly for it. A known document that should belong to a theme should land in that theme's topic.
- **Inspect the outlier bucket.** If it is dominated by one recognizable theme, the clustering parameters are too strict.
- **Check topic count against use.** Hundreds of fine-grained topics are useful for exploration and useless as a routing taxonomy. Tune the minimum cluster size to the consumer, not to an abstract quality score.
- **Compare representations side by side.** Running c-TF-IDF, MMR, and an LLM label together for the same topic surfaces disagreement, and disagreement is where the interpretation is fragile.
- Standard cluster-validity indices and coherence scores can supplement this, but do not let a single aggregate number substitute for reading the documents.

## Known traps

- Clustering on the 2D visualization projection instead of the 5-10 dim clustering projection. The 2D map distorts distance for legibility.
- Treating the outlier bucket as a bug and reassigning it by default, which reintroduces exactly the contamination HDBSCAN was chosen to avoid.
- Calling an LLM once per document to label topics. The architecture exists specifically to make this once per topic.
- Reporting an LLM-generated topic label without the keyword representation behind it, leaving no traceable path from the label back to the corpus.
- Re-running the full pipeline (re-embedding included) to change a topic representation, when only the representation stage needed to change.
- Judging the pipeline by cluster geometry while never reading a document from any cluster.
- Choosing an embedding model by general leaderboard rank rather than by its clustering-task performance.
- Failing to fix or record the reduction seed, then being unable to reproduce a topic set that a stakeholder is already referring to by number. Topic IDs are not stable across refits.
- Treating stop words surviving into c-TF-IDF output as a flaw in the pipeline rather than the expected behavior of a bag-of-words stage that a representation model is meant to correct.

## Design checklist

- [ ] Unit of analysis fixed (document, section, chunk) before embedding
- [ ] Embedding model chosen against clustering-task evidence, embeddings cached
- [ ] Clustering reduction and visualization reduction kept as separate artifacts
- [ ] Cosine metric used for reduction over normalized text embeddings
- [ ] Cluster granularity tuned to the downstream consumer, not to a score
- [ ] Outlier share measured and an explicit decision recorded (keep / reassign / switch to k-means)
- [ ] c-TF-IDF representation stored alongside any generated label
- [ ] LLM labeling budgeted per topic, not per document
- [ ] Clusters manually inspected by reading sampled documents
- [ ] Seeds, parameters, and the embedding model identity recorded — topic IDs are not stable across refits

## Sources

- Alammar, J. and Grootendorst, M., *Hands-On Large Language Models*, O'Reilly, 2024 — Chapter 5, "Text Clustering and Topic Modeling."
- Grootendorst, M., "BERTopic: Neural topic modeling with a class-based TF-IDF procedure," arXiv:2203.05794 (2022).
- McInnes, L., Healy, J., and Melville, J., "UMAP: Uniform Manifold Approximation and Projection for dimension reduction," arXiv:1802.03426 (2018).
- McInnes, L., Healy, J., and Astels, S., "hdbscan: Hierarchical density based clustering," *Journal of Open Source Software* 2.11 (2017): 205.
