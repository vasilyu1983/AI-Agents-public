# Identification and GNN Pitfalls

Load this reference before you make a causal peer-effect claim from network data, trust statistics from a sampled or partial graph, or report a GNN or link-prediction result as evidence that one model is better than another. It owns what can and cannot be identified. The SKILL anti-patterns table owns the one-line traps.

## Contents

- [Identification in observational network data](#identification-in-observational-network-data)
- [Sampling and missing edges](#sampling-and-missing-edges)
- [GNN failure modes](#gnn-failure-modes)
- [Evaluation leakage and split design](#evaluation-leakage-and-split-design)
- [Decision checklist](#decision-checklist)
- [Sources](#sources)

## Identification in observational network data

| Problem | What goes wrong | What changes the decision |
|---------|-----------------|---------------------------|
| Homophily vs contagion | Connected people behave alike because they chose each other, share an environment, or influence each other. In observational data these three explanations are generically confounded. The asymmetries people read from regression coefficients (such as "ego adopts after alter") do not identify a causal effect without strong extra assumptions (Shalizi & Thomas). | Do not size a referral or seeding budget on an observed "influence" coefficient. Use a randomized or encouragement design, or state the assumption that makes the estimate causal. If you cannot, report the result as association. |
| Size of the bias | In one large product-adoption network, matched-sample estimation found that earlier methods overstated peer influence several-fold, and that homophily explained more than half of the apparent contagion (Aral, Muchnik & Sundararajan). The magnitude belongs to that network. | Treat any unadjusted "network lift" as an upper bound. Do not carry the multiplier over to your own network. |
| Reflection problem | When you regress an individual's outcome on the average outcome of their reference group, you cannot separate endogenous peer effects from contextual effects or from shared (correlated) effects. Identification needs prior knowledge of who belongs to each reference group, plus exclusion restrictions (Manski). | Before interpreting "peer effect" coefficients, write down the reference group and the variable that shifts peers but not ego. If neither exists, the coefficient is not a peer effect. |
| Adjacency built from outcomes | You create edges from the behaviour you later explain, such as co-purchase or co-citation. Structure and outcome are then mechanically linked. | Build the graph from a window before the outcome, or from a relation that is independent of it. |

## Sampling and missing edges

| Mechanism | Direction of bias | Handling |
|-----------|-------------------|----------|
| Boundary specification (who counts as a node) | Can change network statistics sharply. Omitting affiliations tends to overestimate clustering and assortativity (Kossinets). | State the inclusion rule. Rerun key metrics under a wider and a narrower boundary. |
| Fixed-choice designs ("name up to k friends") | Cap degree and censor high-degree nodes. Clustering and assortativity tend to be overestimated (Kossinets). | Do not read the degree tail or hub rankings from capped data. |
| Actor non-response | Missing nodes take their edges with them. Clustering and assortativity tend to be underestimated (Kossinets). | Model or bound the missing ties. Compare rankings with and without imputed edges. |
| BFS, snowball, forest-fire and respondent-driven crawls | An incomplete crawl oversamples high-degree nodes. The observed mean degree and degree distribution are biased upward (Kurant, Markopoulou & Thiran). | Correct with the sampling design (re-weight by inclusion probability), or use a random-walk sampler with a known stationary distribution. Label uncorrected crawl statistics as crawl statistics. |
| API or log truncation | Rate limits, retention windows, or top-k exports drop low-activity edges non-randomly. | Record what the source drops before computing centrality. The ranking inherits that filter. |

Rule of thumb: every metric computed on an observed graph is a metric of the observation process plus the network. If you cannot name the sampling mechanism, give rankings as scenario ranges rather than point answers (see [decision-and-validation.md](decision-and-validation.md)).

## GNN failure modes

| Failure | Mechanism | Diagnostic and response |
|---------|-----------|-------------------------|
| Over-smoothing | GCN-style propagation is a form of Laplacian smoothing, so with enough layers node representations converge and lose discriminative signal (Li, Han & Wu). | Plot validation accuracy against depth. Prefer a shallow model, residual or jumping connections, or decoupled propagation over simply stacking more layers. |
| Over-squashing | Information from an exponentially growing receptive field is compressed into a fixed-size vector through bottleneck edges. The effect is worse on tasks that need long-range interactions (Alon & Yahav). Negatively curved edges mark the bottlenecks (Topping et al.). | If the task needs signal from many hops away, test rewiring or a fully adjacent final layer before adding depth. More depth makes squashing worse. |
| Heterophily | When linked nodes tend to have different labels, popular homophily-assuming GNNs can underperform a feature-only MLP (Zhu et al., H2GCN). | Measure label homophily on the training graph before choosing an architecture. Always report an MLP baseline. |
| Benchmark artefacts under heterophily | Some widely used heterophily benchmarks contain duplicate nodes that leak between train and test. On cleaned benchmarks, standard GNNs almost always beat heterophily-specific models (Platonov et al.). | Deduplicate before you trust a heterophily result. Do not pick a specialized architecture because of old leaderboard gaps. |

For choosing the number of layers from the problem radius and the per-architecture ordering, see [10-graph-embeddings.md](../assets/templates/network-science/10-graph-embeddings.md) (Failure Mode 3).

## Evaluation leakage and split design

| Pitfall | Why it misleads | Fix |
|---------|-----------------|-----|
| One fixed split | Different train/validation/test splits can reverse model rankings. With equal tuning, simpler models often match or beat complex ones (Shchur et al.). | Report mean and spread over several random splits and seeds, with the same tuning budget for every model. |
| Transductive leakage | In transductive node classification the test nodes' features and edges are visible during training. Features computed on the full graph, such as degree, PageRank, embeddings, or normalization statistics, can encode test labels. | Compute structural features only on the edges available at training time, or evaluate inductively on held-out nodes or subgraphs. |
| Random edge splits for link prediction | Random negatives are easy. Without hard negatives and unified splits, reported gains inflate and rankings are unstable (Li et al., HeaRT). | Use hard or heuristic-matched negatives and a shared split. Report which negatives you used. |
| Target-link inclusion | Leaving the target edges in the message-passing graph during training causes overfitting, a train/test distribution shift, and implicit test leakage. The effect is largest for low-degree nodes (Zhu et al., SpotTarget). | Exclude the target edges from the graph during training, and the test edges at test time. Break results down by node degree. |
| Temporal edges split at random | Future edges inform the prediction of past ones. | Split by time. See [08-link-prediction.md](../assets/templates/network-science/08-link-prediction.md) and the TGB historical-negative guidance in [patterns-scenarios-traps.md](patterns-scenarios-traps.md). |

## Decision checklist

Before shipping a network-derived causal claim or a GNN comparison, write down:

1. The causal claim, if any, and the design or assumption that identifies it (randomization, a valid instrument, or a known reference group).
2. The sampling or crawl mechanism, and whether degree-dependent inclusion was corrected.
3. The measured homophily, and the MLP baseline result.
4. The split protocol: seeds, inductive or transductive, time-respecting or random, and target edges excluded or not.
5. The negative-sampling scheme for link prediction.

If any item is unknown, report the result as descriptive and say which item blocks a stronger claim.

## Sources

- Shalizi, C. R. & Thomas, A. C. (2011). Homophily and contagion are generically confounded in observational social network studies. *Sociological Methods & Research* 40:211–239. arXiv:1004.4704.
- Aral, S., Muchnik, L. & Sundararajan, A. (2009). Distinguishing influence-based contagion from homophily-driven diffusion in dynamic networks. *PNAS* 106(51):21544–21549.
- Manski, C. F. (1993). Identification of endogenous social effects: the reflection problem. *Review of Economic Studies* 60(3):531–542.
- Kossinets, G. (2006). Effects of missing data in social networks. *Social Networks* 28:247–268. arXiv:cond-mat/0306335.
- Kurant, M., Markopoulou, A. & Thiran, P. Towards unbiased BFS sampling. arXiv:1102.4599.
- Li, Q., Han, Z. & Wu, X.-M. (2018). Deeper insights into graph convolutional networks for semi-supervised learning. AAAI. arXiv:1801.07606.
- Alon, U. & Yahav, E. (2021). On the bottleneck of graph neural networks and its practical implications. ICLR. arXiv:2006.05205.
- Topping, J., Di Giovanni, F., Chamberlain, B. P., Dong, X. & Bronstein, M. M. (2022). Understanding over-squashing and bottlenecks on graphs via curvature. ICLR. arXiv:2111.14522.
- Zhu, J. et al. (2020). Beyond homophily in graph neural networks: current limitations and effective designs. NeurIPS. arXiv:2006.11468.
- Platonov, O. et al. (2023). A critical look at the evaluation of GNNs under heterophily: are we really making progress? arXiv:2302.11640.
- Shchur, O., Mumme, M., Bojchevski, A. & Günnemann, S. (2018). Pitfalls of graph neural network evaluation. arXiv:1811.05868.
- Li, J. et al. Evaluating graph neural networks for link prediction: current pitfalls and new benchmarking. arXiv:2306.10453.
- Zhu, J. et al. Pitfalls in link prediction with graph neural networks: understanding the impact of target-link inclusion and better practices. WSDM. arXiv:2306.00899.
