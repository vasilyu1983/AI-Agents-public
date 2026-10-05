# Learning-to-Rank Pipeline

The six-step shape of a production learning-to-rank (LTR) system: how a judgment list becomes a deployed ranking model, and which parts of that shape survive changes in engine and algorithm.

Pipeline structure follows Grainger, Turnbull & Irwin, *AI-Powered Search* (Manning, 2025), ch. 10. **Read the [Algorithm Choice](#algorithm-choice-what-not-to-port) section before implementing** — the book's teaching algorithm is not the 2026 production recommendation.

---
## Table of Contents

- [When LTR Is Worth It](#when-ltr-is-worth-it)
- [The Six Steps](#the-six-steps)
- [Step 1: Gather Judgments](#step-1-gather-judgments)
- [Step 2: Feature Logging](#step-2-feature-logging)
  - [What counts as a feature](#what-counts-as-a-feature)
  - [The train/serve consistency rule](#the-trainserve-consistency-rule)
  - [Feature stores: what transfers and what doesn't](#feature-stores-what-transfers-and-what-doesnt)
- [Step 3: Transform to a Traditional ML Problem](#step-3-transform-to-a-traditional-ml-problem)
- [Step 4: Train and Evaluate](#step-4-train-and-evaluate)
- [Algorithm Choice: What Not to Port](#algorithm-choice-what-not-to-port)
- [Step 5: Store the Model](#step-5-store-the-model)
- [Step 6: Search Using the Model](#step-6-search-using-the-model)
- [Making It Automatic](#making-it-automatic)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

---

## When LTR Is Worth It

LTR replaces hand-tuned boost weights with a model learned from data about what users actually consider relevant. Reach for it when:

- Manual relevance tuning has plateaued — every boost adjustment that helps one query class hurts another.
- You have enough traffic to derive judgments from behaviour (see [`click-models-and-bias-correction.md`](click-models-and-bias-correction.md)), or budget for human judgments.
- Relevance depends on several signals interacting (text match across fields, recency, popularity, personalisation) rather than one dominant one.

Skip it when a cross-encoder reranker over a good hybrid candidate set already meets your quality bar — that path needs no feature store and no per-engine plumbing. See [`ranking-pipeline-guide.md`](../../ai-rag/references/ranking-pipeline-guide.md).

---

## The Six Steps

| Step | Name | Output |
|---|---|---|
| 1 | Gather judgments | Judgment list — grade, query, doc |
| 2 | Feature logging | Logged judgments — the same rows with feature values attached |
| 3 | Transform to a traditional ML problem | A training set an ordinary ML library can consume |
| 4 | Train and evaluate the model | A scoring function, checked for generalisation |
| 5 | Store the model | Model uploaded to the search infrastructure and enabled |
| 6 | Search using the model | Live ranking |

The value of this list is that it names where things go wrong. Most failed LTR projects fail at Step 1 (bad judgments) or Step 2 (train/serve feature skew), not at Step 4 where the interesting mathematics lives.

---

## Step 1: Gather Judgments

A **judgment list** is a list of relevance labels or grades, each indicating the relevance of a document to a query. The simplest form is binary — 0 for irrelevant, 1 for relevant — and graded scales (0–4, or continuous) work the same way structurally.

```python
# grade, query, doc
Judgment(grade=1, keywords="social network", doc_id=37799)
```

Two sources:

- **Human judgments** — accurate, expensive, and they go stale. Viable for a bounded head-query set.
- **Behavioural judgments** — derived from click logs. This is what makes retraining automatic, and it is where the biases live. Do not use raw click-through rate; see [`click-models-and-bias-correction.md`](click-models-and-bias-correction.md) for SDBN grading and beta-prior confidence damping.

The rest of the pipeline is only as good as this step. A judgment list that encodes position bias trains a model to reproduce your current ranking.

---

## Step 2: Feature Logging

Feature logging takes a judgment list and computes feature values for each labelled query-document pair. The judgment list goes in; the same rows come out with a feature vector attached.

### What counts as a feature

A feature is a numerical attribute of the document, the query, or the query-document relationship — the mathematical building blocks of a ranking function. Typical starting set:

- Per-field text relevance scores (BM25 on title, on body, on description)
- Document-only values (recency, popularity, price, rating, stock status)
- Query-document relationship values (commute distance in job search, category match, a knowledge-graph relationship between query and document)

The practical constraint the book names: **anything you can compute relatively quickly at query time might be a reasonable feature.** A feature that takes 400ms to compute is not a feature, however predictive it is — it is a reranking stage with a latency budget of its own.

### The train/serve consistency rule

The single most important line in this step: *it's crucial that we log features for training in a manner consistent with how the search engine will execute the model.*

If `title_bm25` at training time is computed with different analysis, different field boosts, or a different similarity than the engine uses at query time, the model learns weights for a feature that does not exist in production. This is train/serve skew, and it is silent — the model trains fine, evaluates fine offline, and underperforms in production for reasons no metric explains.

Guard it structurally: define each feature once, in one place, and have both the logging path and the serving path read that definition. Never reimplement a feature for logging.

### Feature stores: what transfers and what doesn't

Engines with native LTR support (Solr, Elasticsearch, OpenSearch) track features in a **feature store** — a named, versioned list of feature definitions, typically parameterised queries that accept the user's keywords:

```python
feature_set = [
    ltr.generate_query_feature(feature_name="title_bm25", field_name="title"),
    ltr.generate_query_feature(feature_name="overview_bm25", field_name="overview"),
    ltr.generate_field_value_feature(feature_name="release_year",
                                     field_name="release_year")]
ltr.upload_features(features=feature_set, model_name="movie_model")
```

Two of these are parameterised (they take the keywords and search a field); the third is a document-only field value.

**Portability caveat.** The book's feature-store mechanics assume a search engine with an LTR plugin — the Solr `SolrFeature` class, the Elasticsearch/OpenSearch LTR plugins (which implement nearly identical concepts, the OpenSearch plugin being derived from the same lineage). Vespa instead implements phased ranking with model invocation per phase; Weaviate exposes reranking capabilities of its own.

**The pipeline shape transfers. The storage mechanics do not.** If you are on a vector database, a managed retrieval service, or a custom stack, you will implement Step 2 yourself: a feature-computation service both paths call, plus your own versioned feature definitions. Port the *discipline* — named features, one definition, logged consistently with serving — not the plugin API.

---

## Step 3: Transform to a Traditional ML Problem

Most of LTR is translating a ranking task into something an ordinary ML library can optimise. The distinction the book draws:

- **Pointwise ML** (stock price prediction) tries to predict each individual value accurately.
- **LTR** is about placing each query's result set in the ideal *order*. The absolute scores are irrelevant; only their ordering within a query matters.

That mismatch is why LTR needs a transformation step at all. The three standard formulations:

- **Pointwise** — predict each grade directly, ignore query grouping. Simplest, weakest.
- **Pairwise** — reduce to "is document A more relevant than document B for this query?" Turns ranking into binary classification over difference vectors, minimising out-of-order pairs.
- **Listwise** — optimise a rank-aware metric (NDCG) over the whole result list for a query. Strongest, and what modern implementations use.

The output of this step is a training set carrying a query-group identifier alongside labels and features. Preserving that grouping is non-negotiable: without it the learner cannot know which comparisons are meaningful, and it will happily learn to compare documents from unrelated queries.

---

## Step 4: Train and Evaluate

Construct the model and confirm it generalises — that it will perform well on queries it has not seen.

Evaluation discipline specific to LTR:

- **Split by query, never by row.** Rows from the same query landing on both sides of the split leaks the answer.
- **Hold out whole queries**, and keep head/torso/tail proportions realistic in both splits. A model that only ever sees head queries in training will not generalise to the tail, which is where LTR earns its keep.
- **Score with a rank-aware metric** (NDCG@k, MRR) — not accuracy, not RMSE.
- **Compare against the incumbent ranker**, not against zero. A model that beats random is not news.
- Offline gains do not imply online gains. Gate the deployment on an online test ([`user-feedback-learning.md`](user-feedback-learning.md) Pattern 3).

---

## Algorithm Choice: What Not to Port

*AI-Powered Search* teaches Step 3 and Step 4 through **SVMrank**, which transforms ranking into binary classification over pairwise feature differences and fits a linear SVM. This is a **pedagogical choice, and a good one** — the pairwise transformation is visible in two dimensions, the resulting model is a readable linear weighting, and the whole mechanism can be followed by hand.

**Do not port it to production.** SVMrank in the book is a teaching device, not a recommendation for a new system.

For a production system, use:

- **Gradient-boosted decision trees with a ranking objective** — LambdaMART, in practice via LightGBM (`lambdarank`) or XGBoost (`rank:ndcg`, `rank:pairwise`). This is the default for feature-based LTR. It handles unnormalised and non-linear features, mixed feature scales, and missing values without the preprocessing an SVM demands; it optimises NDCG directly rather than a pairwise proxy; and it trains fast enough for frequent retraining.
- **Neural cross-encoders** — when the ranking signal is primarily semantic rather than feature-engineered, a cross-encoder over query-document text usually beats any feature-based model, at higher inference cost and over a smaller candidate set. See [`ranking-pipeline-guide.md`](../../ai-rag/references/ranking-pipeline-guide.md).

The two are not exclusive: a common shape is a cross-encoder producing a semantic score that becomes one feature among many in a LambdaMART model alongside behavioural and business features.

Note also SVM-specific frictions the book raises that simply vanish with GBDTs: SVMs are sensitive to feature range and require normalisation to a consistent scale before the separating hyperplane is meaningful. Tree-based rankers are invariant to monotonic feature scaling, so that entire preprocessing stage — and the train/serve skew it can introduce — disappears.

**What to port from ch. 10:** the six-step shape, the judgment-list-first ordering, and the feature-logging consistency discipline. Those are engine-agnostic and durable. The algorithm is not.

---

## Step 5: Store the Model

Upload the model to the search infrastructure, declare which features feed it, and enable it.

Operationally this is a deployment, so treat it as one:

- Version the model and the feature set together — a model is only valid against the feature definitions it was trained on. Deploying a model against a changed feature set is the second flavour of train/serve skew.
- Keep the previous model loaded and switchable so rollback does not require a retrain or reindex.
- Record the training judgment-list version alongside the model, so a regression can be traced back to the judgments that caused it.

---

## Step 6: Search Using the Model

Execute searches with the model in the ranking path.

Practical shape: LTR runs as a **reranking phase over a candidate set**, not as the primary retrieval scorer. Retrieve top-N with a cheap query (BM25, ANN, or hybrid), then apply the model to those N. Scoring the whole index with a feature-heavy model is not affordable, and it is not necessary — the recall work belongs to candidate generation.

Log at serve time what you will need at the next Step 1: query, the ranks shown, the model version, the feature-set version. Without the ranks shown, the next round of click models cannot compute examines.

---

## Making It Automatic

The six steps run once as a project. The value comes from running them on a loop, so the model tracks what users currently consider relevant rather than what they considered relevant at launch.

The loop, and where each piece lives:

1. **Input new destination** — regenerate the judgment list from recent signals ([`click-models-and-bias-correction.md`](click-models-and-bias-correction.md)).
2. **Drive to destination** — rerun Steps 2–5 to retrain and deploy.
3. **Are we there yet?** — confirm the new model actually helps users, via an online test ([`user-feedback-learning.md`](user-feedback-learning.md) Pattern 3), and explore so the next cycle's judgments cover documents this model never showed ([`click-models-and-bias-correction.md`](click-models-and-bias-correction.md) Pattern CM-3).

Around that loop sits maintenance: the search team monitors performance and intervenes — opening the hood to explore new features and model adjustments, or revisiting Step 1 to correct a mistaken understanding of user behaviour. Automation removes the retraining toil, not the judgment.

---

## Validation Checklist

- [ ] Judgment list debiased before training (position + confidence), not raw CTR
- [ ] Judgment list version recorded alongside the model it trained
- [ ] Each feature defined once; logging and serving read the same definition
- [ ] Feature values spot-checked for train/serve agreement on live queries
- [ ] Feature compute cost fits the query latency budget
- [ ] Train/test split by whole query, with realistic head/torso/tail mix
- [ ] Evaluated with a rank-aware metric against the incumbent ranker
- [ ] Ranking objective used (LambdaMART / `rank:ndcg`), not a plain classifier or regressor
- [ ] Model + feature set versioned together; previous version switchable for rollback
- [ ] Model applied as reranking over a candidate set, not index-wide scoring
- [ ] Serve-time logs capture ranks shown, model version, feature-set version
- [ ] Online test gates rollout; offline gain alone does not ship

---

## Cross-References

- [`click-models-and-bias-correction.md`](click-models-and-bias-correction.md) — how Step 1's judgment list gets built from clicks without inheriting position, confidence, and presentation bias.
- [`user-feedback-learning.md`](user-feedback-learning.md) — signal capture (upstream of Step 1), interleaving and guardrails (gating Step 5), monitoring.
- [`ranking-pipeline-guide.md`](../../ai-rag/references/ranking-pipeline-guide.md) — where the trained model sits among candidate generation (ACL pre-filtered), fusion, and cross-encoder reranking.
- [`search-evaluation-guide.md`](search-evaluation-guide.md) — offline metric definitions for Step 4.
