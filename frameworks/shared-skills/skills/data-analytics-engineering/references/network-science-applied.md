---
description: Network-science patterns for analytics engineering. Covers customer-graph centrality, referral-cascade SIR, fraud-ring community detection, dbt-model PageRank criticality, temporal user-item analytics, sessionized event-graph clustering, embedding-based segmentation, and churn contagion — grounded in warehouse and dbt reality.
last_verified: 2026-05-02
status: stable
---

# Network Science Applied: From Warehouse Graphs to Actionable Analytics

> **Gate before invoking:** Check [`foundations-network-science` § When to Apply](../../foundations-network-science/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Framing Note](#framing-note)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Customer-Graph Centrality for Influencer Identification](#p1--customer-graph-centrality-for-influencer-identification)
  - [P2 — dbt-Model Dependency PageRank for Pipeline Criticality](#p2--dbt-model-dependency-pagerank-for-pipeline-criticality)
  - [P3 — Transactions-Graph Community Detection for Fraud Rings](#p3--transactions-graph-community-detection-for-fraud-rings)
  - [P4 — Referral-Cascade SIR Model for Viral Product Growth](#p4--referral-cascade-sir-model-for-viral-product-growth)
  - [P5 — Temporal User-Item Graph Analytics](#p5--temporal-user-item-graph-analytics)
  - [P6 — Sessionized Event-Graph Clustering](#p6--sessionized-event-graph-clustering)
  - [P7 — Embedding-Based Customer Segmentation](#p7--embedding-based-customer-segmentation)
  - [P8 — Churn Contagion in Social-Graph Datasets](#p8--churn-contagion-in-social-graph-datasets)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Treating Graph Degree as Influence](#a1--treating-graph-degree-as-influence)
  - [A2 — Running Community Detection Once on a Snapshot](#a2--running-community-detection-once-on-a-snapshot)
  - [A3 — Using Static-Graph SIR for Bursty Event Streams](#a3--using-static-graph-sir-for-bursty-event-streams)
  - [A4 — Applying Web-Default PageRank Damping to Pipeline Graphs](#a4--applying-web-default-pagerank-damping-to-pipeline-graphs)
  - [A5 — Embedding Nodes Without Anchoring to a Stable Vocabulary](#a5--embedding-nodes-without-anchoring-to-a-stable-vocabulary)
- [Recipes](#recipes)
  - [R1 — Referral-Cascade SIR for Growth Engineering](#r1--referral-cascade-sir-for-growth-engineering)
  - [R2 — Fraud-Ring Detection with Community Detection and Centrality](#r2--fraud-ring-detection-with-community-detection-and-centrality)
  - [R3 — dbt Dependency Graph PageRank for Release-Risk Scoring](#r3--dbt-dependency-graph-pagerank-for-release-risk-scoring)
- [Composition](#composition)
- [Primitive Links](#primitive-links)
- [Sources](#sources)

---

## Framing Note

Analytics engineers increasingly work with data that is graph-shaped: customer referral trees, transaction networks, dbt model dependency DAGs, user-item interaction bipartite graphs, and social graphs embedded in product-event streams. The marts they build are queried for decisions about which customers to activate, which pipeline models are blast-radius risks, and where fraud rings are clustering.

This file is the applied layer of the `foundations-network-science` skill. It translates the 11 primitives into patterns that arise inside dbt projects, warehouse SQL, and product-analytics pipelines. Every pattern names the primitive it relies on and links to the corresponding template. Assumed stack: Snowflake or BigQuery, dbt or SQLMesh, Python (NetworkX / graph-tool / PyTorch Geometric) for computation steps that go beyond SQL, with results written back as dbt models or seed tables.

---

## Pattern Catalog

### P1 — Customer-Graph Centrality for Influencer Identification

**Primitive**: #01 Centrality Measures → [`../../foundations-network-science/assets/templates/network-science/01-centrality-measures.md`](../../foundations-network-science/assets/templates/network-science/01-centrality-measures.md)

**When to use.** You have a customer referral graph, co-purchase graph, or co-usage network and want to rank customers by structural influence — not just by their own revenue, engagement, or number of direct referrals.

**The problem it solves.** Raw degree (referral count) misses the quality of connections: a customer who referred three enterprise accounts is more valuable than one who referred thirty trial accounts that never converted. Betweenness centrality finds structural bridges — customers who connect otherwise separate segments. Eigenvector centrality (and its directed variant, PageRank) propagates influence transitively: being connected to influential nodes elevates your own score.

**Choose the right measure.**

| Objective | Centrality Measure | Reason |
|-----------|-------------------|--------|
| Top referrers by conversion quality | Weighted degree (converted referrals) | Simple, interpretable |
| Network bridges between segments | Betweenness centrality | Finds connectors, not just hubs |
| Transitive influence propagation | Eigenvector centrality (undirected) or PageRank (directed referral DAG) | Reflects endorsed authority |
| Time-to-contact for onboarding nudges | Closeness centrality | Finds nodes close to everyone |

**dbt integration pattern.**

```sql
-- dbt: fct_referral_graph_edges
-- grain: one row per (referrer_account_id, referee_account_id)
-- weight = converted_within_90d flag
select
    r.referrer_account_id,
    r.referee_account_id,
    case when a.converted_at is not null then 1 else 0 end as edge_weight
from {{ ref('fct_referrals') }} r
left join {{ ref('dim_accounts') }} a
    on r.referee_account_id = a.account_id
    and a.converted_at <= dateadd(day, 90, r.referral_date)
```

```python
import networkx as nx
import pandas as pd

edges = pd.read_sql("select * from analytics.fct_referral_graph_edges", conn)
G = nx.DiGraph()
G.add_weighted_edges_from(
    edges[['referrer_account_id', 'referee_account_id', 'edge_weight']].itertuples(index=False)
)

betweenness = nx.betweenness_centrality(G, weight='weight', normalized=True)
pagerank    = nx.pagerank(G, weight='weight', alpha=0.85)
eigenvec    = nx.eigenvector_centrality_numpy(G.to_undirected(), weight='weight')

scores = pd.DataFrame({
    'account_id':   list(betweenness.keys()),
    'betweenness':  list(betweenness.values()),
    'pagerank':     [pagerank[n] for n in betweenness],
    'eigenvector':  [eigenvec.get(n, 0) for n in betweenness],
})
# Write back to warehouse as a seed or dbt Python model
scores.to_sql('fct_customer_centrality', conn, if_exists='replace', index=False)
```

**Worked example.** A B2B SaaS company has 8,400 customer accounts linked by 3,100 referral edges. Raw top-10 by referral count are all individual freelancers who invited trial users. Top-10 by betweenness centrality are seven agency partners who bridge SMB and enterprise segments. Top-10 by eigenvector centrality are Fortune-500 accounts whose referrals feed back into other enterprise accounts. The centrality-ranked list surfaces the correct target for a referral incentive program; the degree-ranked list does not.

---

### P2 — dbt-Model Dependency PageRank for Pipeline Criticality

**Primitive**: #02 PageRank → [`../../foundations-network-science/assets/templates/network-science/02-pagerank.md`](../../foundations-network-science/assets/templates/network-science/02-pagerank.md)

**When to use.** You have a dbt or SQLMesh project with a model dependency DAG and want to rank models by blast radius: which models, if they fail or change schema, will propagate the most downstream impact? Use this to prioritise contract placement, CI test coverage, and on-call escalation priority.

**The problem it solves.** A model deep in the dependency tree with many transitive descendants is more critical than a leaf model with zero dependents. Standard dependency counts only look one hop downstream; PageRank on the reversed dependency graph propagates transitivity — a model is critical if it feeds critical models.

**Reverse PageRank for blast radius.** Run PageRank on the reversed dependency graph: reverse all edges so that arrows point from dependent to dependency. A node with high reverse-PageRank has the most transitive dependents — it is the most critical model to protect.

```python
import networkx as nx
import json, subprocess

# Parse dbt manifest.json for model dependencies
manifest = json.load(open('target/manifest.json'))
nodes = manifest['nodes']

G = nx.DiGraph()
for node_id, node in nodes.items():
    if node['resource_type'] == 'model':
        for dep in node.get('depends_on', {}).get('nodes', []):
            if dep in nodes:
                G.add_edge(dep, node_id)   # dep → downstream model

# Reverse for blast-radius PageRank
G_rev = G.reverse(copy=True)

# Calibrate damping: dbt graphs are sparse and small vs. web graphs
# d=0.65 is more stable for typical dbt projects (50–500 nodes)
pr_blast = nx.pagerank(G_rev, alpha=0.65)

ranked = sorted(pr_blast.items(), key=lambda x: x[1], reverse=True)
print("Top 10 blast-radius models:")
for node_id, score in ranked[:10]:
    print(f"  {nodes[node_id]['name']:<50}  PR={score:.4f}")
```

**Contract placement heuristic.** Models in the top 20% by blast-radius PageRank are contract candidates. Add `config: contract: enforced: true` in their dbt YAML. Models in the top 5% should have freshness + schema contracts and CI gate checks.

**Worked example.** A dbt project with 280 models. Top-3 by blast-radius PageRank: `stg_orders` (feeds 214 downstream models transitively), `dim_accounts` (feeds 189), `fct_revenue` (feeds 97). The team had contracts on `fct_revenue` but not on `stg_orders`, which had no data contract despite being the highest-impact failure point. After adding the contract, a schema change on the source table was caught in CI before reaching production.

---

### P3 — Transactions-Graph Community Detection for Fraud Rings

**Primitive**: #03 Community Detection → [`../../foundations-network-science/assets/templates/network-science/03-community-detection.md`](../../foundations-network-science/assets/templates/network-science/03-community-detection.md)

**When to use.** You have a transactions or account-activity graph where edges represent shared identifiers (same device, same IP range, same email domain, same card BIN) and want to surface clusters of accounts that likely belong to coordinated fraud rings.

**The problem it solves.** Rule-based fraud detection flags individual accounts. Fraud rings operate as coordinated networks: individual accounts may look clean but share identifiers with fraudulent accounts two hops away. Community detection surfaces the entire ring, not just the caught node.

**Graph construction.** Build a bipartite graph from shared identifiers, then project onto the account layer:

```sql
-- dbt: fct_fraud_graph_edges
-- Accounts sharing the same device fingerprint or IP subnet get an edge
-- weight = number of shared identifiers (stronger edge = more shared signals)
select
    a1.account_id                          as account_a,
    a2.account_id                          as account_b,
    count(distinct s.identifier_value)     as shared_signals
from {{ ref('fct_account_signals') }} s
join {{ ref('fct_account_signals') }} s2
    on  s.identifier_type  = s2.identifier_type
    and s.identifier_value = s2.identifier_value
    and s.account_id       < s2.account_id
join {{ ref('dim_accounts') }} a1 on s.account_id  = a1.account_id
join {{ ref('dim_accounts') }} a2 on s2.account_id = a2.account_id
group by 1, 2
having count(distinct s.identifier_value) >= 2   -- require ≥2 shared signals
```

```python
import networkx as nx
from community import best_partition   # python-louvain

edges = pd.read_sql("select * from analytics.fct_fraud_graph_edges", conn)
G = nx.Graph()
G.add_weighted_edges_from(
    edges[['account_a', 'account_b', 'shared_signals']].itertuples(index=False)
)

# Run Louvain 20 times; take highest modularity result
best_q, best_partition_map = -1, None
for _ in range(20):
    part = best_partition(G, weight='weight', resolution=1.0)
    q = nx.community.modularity(G, [
        {n for n, c in part.items() if c == cid}
        for cid in set(part.values())
    ])
    if q > best_q:
        best_q, best_partition_map = q, part

community_df = pd.DataFrame(
    {'account_id': list(best_partition_map.keys()),
     'community_id': list(best_partition_map.values())}
)

# Join known-fraud labels to score community risk
fraud_labels = pd.read_sql("select account_id, is_confirmed_fraud from dim_accounts", conn)
community_risk = (
    community_df.merge(fraud_labels, on='account_id')
    .groupby('community_id')
    .agg(
        community_size=('account_id', 'count'),
        confirmed_fraud_count=('is_confirmed_fraud', 'sum')
    )
    .assign(fraud_density=lambda d: d.confirmed_fraud_count / d.community_size)
    .sort_values('fraud_density', ascending=False)
)
```

**Escalation logic.** Communities where `fraud_density >= 0.1` (10% confirmed fraud) are high-risk rings — flag all members for manual review. Communities where a single confirmed-fraud node exists and `community_size >= 5` are candidate rings — flag for automated hold pending review.

**Worked example.** A fintech's transaction graph has 42,000 accounts. Louvain (γ=1.0, 20 runs, Q=0.47) produces 380 communities. Joining to known-fraud labels: 12 communities have fraud density > 10%. The largest high-density community has 94 accounts, 18 confirmed fraudulent, sharing device fingerprints and IP subnets. Rule-based systems had flagged 18 of the 94; community detection surfaces the remaining 76 connected members for review.

---

### P4 — Referral-Cascade SIR Model for Viral Product Growth

**Primitive**: #07 Contagion / SIR → [`../../foundations-network-science/assets/templates/network-science/07-contagion-sir.md`](../../foundations-network-science/assets/templates/network-science/07-contagion-sir.md)

**When to use.** You have a product with a referral or invitation mechanism and want to model how virality spreads through the user graph: expected final reach from a seed campaign, time-to-peak, and sensitivity of growth to changes in the invitation conversion rate (β) or churn rate (γ).

**The problem it solves.** Standard viral coefficient (k-factor) models assume homogeneous mixing — every user can reach every other user. Real referral graphs are heterogeneous: power-law degree distributions mean a few super-connectors dominate spread while most users reach only a handful of neighbours. Using a network-aware SIR model produces materially different growth forecasts and identifies the right seed accounts.

**Calibrate β and γ from warehouse data.**

```sql
-- dbt: fct_referral_sir_calibration
-- Calibration window: last 90 days of referral activity
select
    date_trunc('week', referral_date)          as week,
    count(*)                                    as new_invitations_sent,
    countif(converted_within_14d)               as conversions,
    countif(converted_within_14d) / count(*)    as beta_weekly,   -- transmission rate
    countif(not active_at_week4)                as recoveries,
    countif(not active_at_week4) / count(*)     as gamma_weekly   -- recovery (churn) rate
from {{ ref('fct_referrals') }}
where referral_date >= dateadd(day, -90, current_date)
group by 1
order by 1
```

```python
import networkx as nx
import numpy as np
from collections import defaultdict

# Build referral graph from warehouse
edges = pd.read_sql("select referrer_id, referee_id from fct_referrals", conn)
G = nx.DiGraph()
G.add_edges_from(edges[['referrer_id', 'referee_id']].itertuples(index=False))

# Calibrated parameters (from SQL above, median over last 12 weeks)
beta  = 0.08   # weekly transmission rate per infected neighbour
gamma = 0.25   # weekly recovery rate

# Network-aware R₀ check (use undirected projection for degree moments)
G_u = G.to_undirected()
degrees = [d for _, d in G_u.degree()]
k_mean  = np.mean(degrees)
k2_mean = np.mean([d**2 for d in degrees])
R0_network = (beta / gamma) * (k2_mean / k_mean)
print(f"Network-aware R₀ = {R0_network:.2f}  ({'epidemic' if R0_network > 1 else 'subcritical'})")

# Monte Carlo SIR (1,000 realisations)
def sir_simulation(G, beta, gamma, seeds, n_steps=52):
    all_nodes = list(G.nodes())
    state = {n: 'S' for n in all_nodes}
    for s in seeds:
        state[s] = 'I'
    history = []
    for _ in range(n_steps):
        new_state = state.copy()
        for node in all_nodes:
            if state[node] == 'I':
                if np.random.rand() < gamma:
                    new_state[node] = 'R'
                    continue
                for nbr in G.successors(node):
                    if state[nbr] == 'S' and np.random.rand() < beta:
                        new_state[nbr] = 'I'
        state = new_state
        counts = {k: sum(1 for v in state.values() if v == k) for k in 'SIR'}
        history.append(counts)
        if counts['I'] == 0:
            break
    return history

# Seed selection: top-PageRank nodes (highest referral authority)
pr = nx.pagerank(G, alpha=0.75)
top_seeds = sorted(pr, key=pr.get, reverse=True)[:10]

n_runs = 1000
final_reach = []
for _ in range(n_runs):
    h = sir_simulation(G, beta, gamma, seeds=top_seeds[:5])
    final_reach.append(h[-1]['R'] + h[-1]['I'])

p5, p50, p95 = np.percentile(final_reach, [5, 50, 95])
print(f"Expected final reach: {p50:,} users  (90% CI: [{p5:,}, {p95:,}])")
```

**Worked example.** A PLG SaaS product calibrates β=0.08, γ=0.25 from 12 weeks of referral data. Mean-field R₀ = 0.32 (subcritical — would suggest no viral growth). Network-aware R₀ = 1.41 (epidemic — power-law degree distribution amplifies spread). Monte Carlo from top-5 PageRank seeds: median final reach = 2,340 users (5th–95th: 180–8,900). Growth team uses the model to size the referral incentive: increasing β from 0.08 to 0.12 (via a higher reward) pushes median reach to 6,100 users.

---

### P5 — Temporal User-Item Graph Analytics

**Primitive**: #11 Temporal Networks → [`../../foundations-network-science/assets/templates/network-science/11-temporal-networks.md`](../../foundations-network-science/assets/templates/network-science/11-temporal-networks.md)

**When to use.** You have a user-item interaction table (views, purchases, ratings, clicks) with timestamps and want to analyse how influence or co-engagement patterns evolve over time — not just what users interacted with, but when and in what sequence.

**The problem it solves.** A static bipartite graph of user-item interactions misrepresents temporal dynamics: users who engage with items in the same session (close timestamps) form tighter co-purchase or co-view clusters than users who engaged months apart. Temporal network analysis separates genuine co-engagement from coincidental statistical overlap. It also reveals decay: which items are losing relevance as temporal reachability declines.

**dbt mart for temporal interaction graph.**

```sql
-- dbt: fct_user_item_temporal_edges
-- grain: one row per (user_id, item_id, event_timestamp)
select
    e.user_id,
    e.item_id,
    e.event_timestamp,
    e.event_type,
    date_trunc('day', e.event_timestamp)   as event_day,
    -- Session window: events within 30 minutes of each other = same session
    sum(case
        when datediff(
            'minute',
            lag(e.event_timestamp) over (partition by e.user_id order by e.event_timestamp),
            e.event_timestamp
        ) > 30 then 1 else 0
    end) over (partition by e.user_id order by e.event_timestamp) as session_id
from {{ ref('fct_product_events') }} e
where e.event_type in ('view', 'purchase', 'add_to_cart')
  and e.event_timestamp >= dateadd(day, -{{ var('lookback_days', 90) }}, current_date)
```

```python
import pandas as pd
import numpy as np

events = pd.read_sql("select * from analytics.fct_user_item_temporal_edges", conn)
events['event_timestamp'] = pd.to_datetime(events['event_timestamp'])
events = events.sort_values('event_timestamp')

# Burstiness per user: are interactions clustered or evenly spaced?
def burstiness(inter_event_times):
    if len(inter_event_times) < 2:
        return np.nan
    mu, sigma = np.mean(inter_event_times), np.std(inter_event_times)
    return (sigma - mu) / (sigma + mu) if (sigma + mu) > 0 else 0

iet = (
    events.sort_values('event_timestamp')
    .groupby('user_id')['event_timestamp']
    .apply(lambda ts: ts.diff().dt.total_seconds().dropna().tolist())
)
burstiness_scores = iet.apply(burstiness).rename('burstiness')

# High-burstiness users (B > 0.5) have binge patterns
# Low-burstiness users (B near 0) have regular, scheduled engagement
# Use burstiness as a feature in churn models and segmentation
user_features = burstiness_scores.reset_index()
user_features['engagement_pattern'] = pd.cut(
    user_features['burstiness'],
    bins=[-1, -0.2, 0.2, 0.6, 1],
    labels=['regular', 'poisson', 'bursty', 'highly_bursty']
)
```

**Temporal reachability as item decay signal.** For each item, compute the fraction of users who engaged within a rolling 14-day window. Declining temporal reachability signals a trending item going cold — use as a feature in recommendation freshness scoring.

**Worked example.** An e-commerce platform with 120,000 users and 45,000 items. Static co-purchase graph suggests items A and B are strongly co-purchased (1,200 co-purchase pairs). Temporal analysis: 74% of those co-purchases occurred within the same 30-minute session; the rest are separated by weeks and likely coincidental. The session-filtered co-purchase graph produces tighter, more actionable product recommendation clusters. Burstiness analysis: 18% of users have B > 0.6 (binge shoppers); these users have 3.4× higher 90-day LTV than regular-pattern users.

---

### P6 — Sessionized Event-Graph Clustering

**Primitive**: #09 Graph Clustering → [`../../foundations-network-science/assets/templates/network-science/09-graph-clustering.md`](../../foundations-network-science/assets/templates/network-science/09-graph-clustering.md)

**When to use.** You have a product-event stream where users traverse screens, features, or pages, and want to cluster users by their navigation patterns — not by demographics or raw feature usage counts, but by structural similarity in the graph of transitions they make.

**The problem it solves.** Standard funnel analysis and cohort segmentation group users by whether they reached a step, not by how they navigated. Graph clustering on the session transition graph reveals behavioural archetypes: power users who use advanced features in non-linear patterns, onboarding users who follow a guided path, and confused users who ping-pong between the same two screens.

**Build the session transition graph.**

```sql
-- dbt: fct_session_transitions
-- grain: one row per (from_screen, to_screen, session_id, user_id)
select
    e1.user_id,
    e1.session_id,
    e1.screen_name                                          as from_screen,
    e2.screen_name                                          as to_screen,
    count(*)                                                as transition_count
from {{ ref('fct_product_events') }} e1
join {{ ref('fct_product_events') }} e2
    on  e1.user_id    = e2.user_id
    and e1.session_id = e2.session_id
    and e2.event_rank = e1.event_rank + 1
group by 1, 2, 3, 4
```

```python
import networkx as nx
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.cluster import SpectralClustering

# Aggregate to user-level transition vectors
transitions = pd.read_sql("select * from analytics.fct_session_transitions", conn)
screen_pairs = transitions.groupby(['from_screen', 'to_screen'])['transition_count'].sum()
all_pairs = list(screen_pairs.index)

# Build per-user transition-frequency vector
user_vectors = (
    transitions.groupby(['user_id', 'from_screen', 'to_screen'])['transition_count']
    .sum()
    .unstack(level=['from_screen', 'to_screen'], fill_value=0)
    .reindex(columns=pd.MultiIndex.from_tuples(all_pairs), fill_value=0)
)
X = normalize(user_vectors.values, norm='l1')   # row-normalize to relative frequencies

# Spectral clustering on user-similarity graph
# Build user similarity graph via cosine similarity
from sklearn.metrics.pairwise import cosine_similarity
sim_matrix = cosine_similarity(X)
np.fill_diagonal(sim_matrix, 0)

# k=5 behavioural archetypes (tune via eigengap heuristic)
sc = SpectralClustering(n_clusters=5, affinity='precomputed', assign_labels='kmeans', random_state=42)
labels = sc.fit_predict(sim_matrix)

user_clusters = pd.DataFrame({
    'user_id': user_vectors.index,
    'behavioural_cluster': labels
})
# Write back to warehouse; join to dim_users for downstream analysis
```

**Worked example.** A SaaS product with 28,000 active users and 14 distinct screens. Spectral clustering (k=5, eigengap confirms 5 clusters) produces: Cluster 0 — "power integrators" (42% of users, cycle through API docs and settings); Cluster 1 — "dashboard consumers" (31%, mostly homepage and reports); Cluster 2 — "onboarding stragglers" (14%, loop between getting-started screens); Cluster 3 — "explorers" (8%, wide coverage of all screens); Cluster 4 — "confused users" (5%, high ping-pong on the same 2–3 screens). The "confused" cluster has 4.2× higher 30-day churn than Cluster 0. The team adds targeted in-app guidance triggered on Cluster 4 membership.

---

### P7 — Embedding-Based Customer Segmentation

**Primitive**: #10 Graph Embeddings → [`../../foundations-network-science/assets/templates/network-science/10-graph-embeddings.md`](../../foundations-network-science/assets/templates/network-science/10-graph-embeddings.md)

**When to use.** You have a customer graph (referral, co-usage, support-interaction, or transaction network) with rich node attributes (industry, seat count, ARR tier) and want to produce a low-dimensional representation of each customer that captures both structural position in the graph and node attributes — for use in segmentation, lookalike modelling, and churn prediction.

**The problem it solves.** Traditional segmentation uses attribute tables only. Graph embeddings combine structural position (who a customer is connected to in the referral or interaction network) with node features. A customer who is structurally central in the enterprise segment behaves differently from one with identical attributes but isolated in the graph — the embedding captures this.

**Two embedding approaches.**

| Approach | When to Use | Library |
|----------|-------------|---------|
| Node2Vec (random walk) | Pure topology; no node attributes | `node2vec` Python package |
| GraphSAGE / GCN | Node attributes + topology combined | `PyTorch Geometric` |
| LINE | Large graphs (> 100k nodes); fast | `pecanpy` |

```python
from node2vec import Node2Vec
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

edges = pd.read_sql("select account_a, account_b, shared_signals from fct_fraud_graph_edges", conn)
G = nx.Graph()
G.add_weighted_edges_from(edges.itertuples(index=False))

# Node2Vec: p=1, q=0.5 → DFS-biased (community-aware embeddings)
node2vec = Node2Vec(G, dimensions=64, walk_length=30, num_walks=200, p=1, q=0.5, workers=4)
model = node2vec.fit(window=10, min_count=1, batch_words=4)

# Extract embeddings for all nodes
node_ids  = list(G.nodes())
embeddings = np.array([model.wv[str(n)] for n in node_ids])

# Combine with node attribute features
attributes = pd.read_sql(
    "select account_id, seat_count, arr_usd, account_age_days from dim_accounts", conn
).set_index('account_id')
attr_matrix = StandardScaler().fit_transform(attributes.reindex(node_ids).fillna(0))

# Concatenate graph embedding and attribute features
combined = np.hstack([embeddings, attr_matrix])

# KMeans segmentation (k=6; tune with elbow or silhouette)
kmeans = KMeans(n_clusters=6, random_state=42, n_init=20)
segment_labels = kmeans.fit_predict(combined)

segment_df = pd.DataFrame({'account_id': node_ids, 'graph_segment': segment_labels})
segment_df.to_sql('fct_customer_graph_segments', conn, if_exists='replace', index=False)
```

**Stability note.** Graph embeddings are sensitive to graph changes — adding or removing edges shifts the embedding space. Re-train on a fixed snapshot (e.g., monthly) and version the embedding model. Do not join embeddings from different training runs directly; re-embed both batches first.

**Worked example.** A marketplace platform embeds 18,000 seller accounts using Node2Vec on the co-purchase graph (sellers whose products are frequently bought together). KMeans (k=6) on embeddings + attributes produces segments with 3.1× higher silhouette score than attributes-only KMeans. Segment 2 (2,100 sellers) shows a high-centrality, high-ARR cluster that churn models using only attributes had grouped with mid-market accounts. Adding graph segment as a feature improves 90-day churn AUC from 0.71 to 0.79.

---

### P8 — Churn Contagion in Social-Graph Datasets

**Primitive**: #07 Contagion / SIR → [`../../foundations-network-science/assets/templates/network-science/07-contagion-sir.md`](../../foundations-network-science/assets/templates/network-science/07-contagion-sir.md); **supporting**: #11 Temporal Networks, #03 Community Detection

**When to use.** You have a product with a social or collaborative layer — teams, shared workspaces, referral networks, or community groups — and want to model whether churn is socially contagious: does the departure of one user or account raise the probability of departure for their connected neighbours?

**The problem it solves.** Standard churn models treat each customer independently. In products with network effects (team collaboration, shared dashboards, community content), churn can cascade: a key user leaving degrades value for their neighbours, increasing their churn probability. Modelling churn as a contagion on the social graph identifies at-risk clusters before individual-level signals appear.

**Test for churn contagion (before modelling).**

```sql
-- Contagion test: do accounts whose graph neighbours churned
-- have higher observed churn rates than accounts with no churned neighbours?
select
    case when n.churned_neighbour_count > 0 then 'exposed' else 'unexposed' end as exposure,
    count(*)                                               as account_count,
    countif(a.churned_within_90d)                          as churned_count,
    countif(a.churned_within_90d) / count(*)               as churn_rate
from {{ ref('dim_accounts') }} a
left join (
    select
        e.account_b                          as account_id,
        countif(a2.churned_before_date)      as churned_neighbour_count
    from {{ ref('fct_referral_graph_edges') }} e
    join {{ ref('dim_accounts') }} a2
        on e.account_a = a2.account_id
        and a2.churn_date < dateadd(day, -30, current_date)
    group by 1
) n on a.account_id = n.account_id
group by 1
```

If `churn_rate(exposed) > churn_rate(unexposed)` with sufficient sample size, contagion is present and the SIR model is appropriate.

```python
import networkx as nx
import numpy as np
import pandas as pd

# Calibrate β from observed churn contagion lift
# β ≈ (churn_rate_exposed - churn_rate_unexposed) / avg_infected_neighbours
beta  = 0.04   # weekly churn transmission probability per churned neighbour
gamma = 0.0    # churn is absorbing — no recovery (use SIS if reactivation is possible)

# Load social graph and churn seeds (accounts churned in last 30 days)
edges = pd.read_sql("select account_a, account_b from fct_referral_graph_edges", conn)
seeds = pd.read_sql("select account_id from dim_accounts where churned_in_last_30d", conn)

G = nx.Graph()
G.add_edges_from(edges.itertuples(index=False))
seed_set = set(seeds['account_id'].tolist())

# SI model (absorbing churn = no recovery)
# Monte Carlo 1,000 runs, horizon = 13 weeks
def si_simulation(G, beta, seeds, n_steps=13):
    state = {n: ('I' if n in seeds else 'S') for n in G.nodes()}
    infected_by_week = [sum(1 for v in state.values() if v == 'I')]
    for _ in range(n_steps):
        new_state = state.copy()
        for node in G.nodes():
            if state[node] == 'S':
                infected_nbrs = sum(1 for nbr in G.neighbors(node) if state[nbr] == 'I')
                if infected_nbrs > 0 and np.random.rand() < 1 - (1 - beta) ** infected_nbrs:
                    new_state[node] = 'I'
        state = new_state
        infected_by_week.append(sum(1 for v in state.values() if v == 'I'))
    return infected_by_week

n_runs = 1000
trajectories = [si_simulation(G, beta, seed_set) for _ in range(n_runs)]
median_trajectory = np.median(trajectories, axis=0)
p5_trajectory     = np.percentile(trajectories, 5, axis=0)
p95_trajectory    = np.percentile(trajectories, 95, axis=0)

# Identify highest-risk accounts: susceptible with most churned neighbours
at_risk = []
for node in G.nodes():
    if node not in seed_set:
        churned_nbrs = sum(1 for nbr in G.neighbors(node) if nbr in seed_set)
        if churned_nbrs >= 2:
            at_risk.append({'account_id': node, 'churned_neighbours': churned_nbrs})
at_risk_df = pd.DataFrame(at_risk).sort_values('churned_neighbours', ascending=False)
```

**Community-level early warning.** Use community detection (#03) to identify the communities with the highest fraction of already-churned accounts. Communities above a risk threshold get a proactive CSM outreach before individual churn signals fire.

**Worked example.** A team-collaboration SaaS product with 12,000 active accounts. Contagion test: exposed accounts (2+ churned neighbours in the prior month) churn at 18.4% in the next 90 days vs. 6.1% for unexposed (3× lift; p < 0.001). SI model calibrated to β=0.04. Starting from 340 churned seeds, the model predicts median +580 additional churns over 13 weeks (5th–95th: 210–1,140). Community detection surfaces 3 communities where churn density > 20% — CSM team intervenes with "save" campaigns targeted at 94 susceptible high-value accounts within those communities.

---

## Anti-Pattern Catalog

### A1 — Treating Graph Degree as Influence

**Primitives implicated**: #01 Centrality Measures, #02 PageRank

**Description.** Ranking customers, pipeline models, or content nodes by raw edge count (degree centrality) and reporting this as "influence" or "criticality."

**Why it fails.** Degree measures only the number of direct connections — not the quality of those connections or the transitive reach they enable. A node with 100 connections to low-degree nodes has lower real influence than a node with 10 connections to high-degree hubs. In a dbt dependency graph, a model with 20 direct dependents may have lower blast radius than a model with 3 dependents that each feed 50 downstream models.

**Concrete example.** A growth team ranks "influencer accounts" by number of direct referrals. Top 10 are freelancers who invited trial users; none converted. The enterprise partners who referred converting customers rank 40th–60th because they referred fewer but higher-value accounts. The degree-based list wastes the referral incentive budget.

**Fix.** Use PageRank or eigenvector centrality for undirected influence; reverse-PageRank for downstream blast radius. Weight edges by conversion quality, not raw count. Report centrality measure used and its limitations alongside results.

---

### A2 — Running Community Detection Once on a Snapshot

**Primitives implicated**: #03 Community Detection, #11 Temporal Networks

**Description.** Running Louvain or label propagation once on a single graph snapshot and treating the resulting community assignments as stable entity attributes — for example, storing `community_id` as a column in `dim_accounts` without a refresh schedule.

**Why it fails.** Graphs evolve. New edges are added, old edges decay, and the underlying community structure shifts. A fraud ring community from three months ago may have disbanded and reformed under different identifiers. A customer community used for churn modelling may be stale if account relationships have changed. Stale community labels fed into downstream models silently corrupt their signal.

**Fix.** Community detection results are time-bounded artefacts. Version them with a `community_snapshot_date`. Refresh on the same schedule as the underlying edge table. For fraud applications, refresh at least daily. Store the modularity score Q alongside the snapshot as a health indicator — a drop in Q signals structural graph change. Consider using a rolling temporal window (last 30 days of interactions) rather than all-time edges.

---

### A3 — Using Static-Graph SIR for Bursty Event Streams

**Primitives implicated**: #07 Contagion / SIR, #11 Temporal Networks

**Description.** Calibrating a referral or churn contagion model on the static aggregate graph (all-time edges, no timestamps) and reporting epidemic size or timeline forecasts as if they reflect the actual temporal dynamics of the event stream.

**Why it fails.** Static-graph SIR overestimates spread speed and epidemic size on bursty contact sequences. Referral invitations, support escalations, and churn events cluster in bursts with long inter-event gaps. Long gaps between contacts reduce the effective transmission rate. On the static graph, two accounts appear permanently connected; in reality, their interaction may have been a single event 18 months ago.

**Concrete example.** A growth team runs static-graph SIR on the all-time referral graph (β=0.05, γ=0.20). Predicted 90-day reach from a 10-seed campaign: 4,200 users. Temporal SIR on the past-90-day interaction window: 1,100 users. The team over-allocates referral incentives by 3.8× based on the static forecast.

**Fix.** Build the interaction graph with a recency window appropriate to the contagion dynamics (for referral models: last 90–180 days; for churn contagion: last 30 days). Use temporal SIR with actual event timestamps when the event stream is available. Always report: "graph built from interactions within [window]; static-graph upper bound is [value]."

---

### A4 — Applying Web-Default PageRank Damping to Pipeline Graphs

**Primitives implicated**: #02 PageRank

**Description.** Running `nx.pagerank(G)` with the default `alpha=0.85` damping factor on dbt model dependency graphs or small customer referral graphs — without calibrating the parameter to the graph's structure.

**Why it fails.** The default damping factor d=0.85 was calibrated on web-scale graphs with millions of nodes and a specific link-to-node ratio. On a dbt project with 50–500 models, or a referral graph with thousands of nodes, d=0.85 produces numerically unstable results or concentrates PageRank into dangling-node sinks in ways that misrepresent the true dependency structure. Small, sparse graphs need d in the range 0.55–0.75 for stable, meaningful output.

**Fix.** Sensitivity-test d before reporting: run PageRank at d ∈ {0.55, 0.65, 0.75, 0.85} and compare the rank ordering of the top 20 nodes. If the ordering is stable across d values, the default is fine. If the ranking changes substantially, report at d=0.65 and note the sensitivity. For dbt dependency graphs specifically, d=0.65 is a reasonable starting default; document the choice in the model YAML.

---

### A5 — Embedding Nodes Without Anchoring to a Stable Vocabulary

**Primitives implicated**: #10 Graph Embeddings

**Description.** Training Node2Vec or GraphSAGE embeddings on a graph snapshot and then comparing, joining, or using as features embeddings trained at different points in time — without re-training on a common snapshot.

**Why it fails.** Graph embedding methods produce arbitrary rotation/reflection of the embedding space. Two runs on the same graph with different random seeds produce embeddings that are not comparable — the same node may land in opposite regions of the embedding space across runs. Joining embeddings from a November training run with embeddings from a February training run to produce "segment evolution" is numerically meaningless.

**Fix.** Treat the embedding training run as a versioned model artefact: fix the training snapshot date, fix the random seed, and store the trained model alongside the embeddings. To compare over time, embed both the old and new node sets using the same trained model (transductive) or retrain from scratch and align embeddings with Procrustes alignment. Never concatenate embeddings from separate training runs without explicit alignment.

---

## Recipes

### R1 — Referral-Cascade SIR for Growth Engineering

**Scenario.** A PLG product is launching a referral incentive campaign. The growth team wants to estimate expected user reach from seeding 10 power users, forecast the campaign ROI, and identify whether increasing the reward (lifting β) produces a super-linear gain in reach.

**Stack**: #01 Centrality (seed selection) → #05 Scale-Free Networks (R₀ check) → #07 SIR (Monte Carlo forecast) → #11 Temporal Networks (recency window)

**Step 1: Build the temporal referral graph (last 90 days).**

```sql
-- fct_referral_temporal_edges: timestamped referral events within the recency window
select
    referrer_id,
    referee_id,
    referral_date,
    converted_within_14d
from {{ ref('fct_referrals') }}
where referral_date >= dateadd(day, -90, current_date)
```

**Step 2: Calibrate β and γ from observed data.**

From the SQL in P4, compute median weekly β (invitation-to-conversion rate) and γ (weekly deactivation rate). If calibration data is sparse, use a sensitivity range: β ∈ {low, mid, high} to bracket forecasts.

**Step 3: Check R₀ and network structure.**

```python
G_u = G.to_undirected()
degrees = [d for _, d in G_u.degree()]
k_mean  = np.mean(degrees)
k2_mean = np.mean([d**2 for d in degrees])
R0 = (beta / gamma) * (k2_mean / k_mean)
# If R₀ > 1: epidemic regime — campaign will spread beyond direct referrals
# If R₀ < 1: subcritical — reach is bounded; seed selection is critical
```

**Step 4: Select seeds via PageRank.**

```python
pr = nx.pagerank(G, alpha=0.70)
seed_candidates = sorted(pr, key=pr.get, reverse=True)[:20]
# Optionally: diversify by community membership to seed multiple clusters
```

**Step 5: Monte Carlo forecast for three β scenarios.**

Run 1,000 SIR simulations per β scenario (current rate, +25% reward, +50% reward). Plot 10th–90th percentile bands for cumulative reach over 13 weeks. Identify the β inflection point where R₀ crosses 1.0 — this is the minimum reward level needed for viral spread.

**Step 6: Write results to warehouse.**

```python
results = pd.DataFrame({
    'scenario':    ['current', 'plus_25pct', 'plus_50pct'],
    'beta':        [0.08, 0.10, 0.12],
    'R0_network':  [r0_current, r0_plus25, r0_plus50],
    'reach_p10':   [...],
    'reach_p50':   [...],
    'reach_p90':   [...],
})
results.to_sql('fct_referral_campaign_forecast', conn, if_exists='replace', index=False)
```

**Expected output.** A dbt model `fct_referral_campaign_forecast` with per-scenario reach distributions, R₀ by scenario, and seed account list. Growth team uses this to size the reward budget and set campaign KPIs with uncertainty bounds.

---

### R2 — Fraud-Ring Detection with Community Detection and Centrality

**Scenario.** A fintech risk team suspects coordinated account fraud. Transaction monitoring flags individual accounts but misses rings. The team wants to surface clusters of connected suspicious accounts and identify the highest-risk nodes within each ring for manual review prioritisation.

**Stack**: #03 Community Detection (ring surfacing) → #01 Centrality (within-ring prioritisation) → #08 Link Prediction (anticipate ring expansion)

**Step 1: Build the shared-signal graph (see P3 for SQL).**

Require ≥2 shared signals (device fingerprint, IP subnet, email domain, card BIN) as the edge criterion. Weight edges by number of shared signals.

**Step 2: Run Louvain with multiple resolutions.**

```python
# Run at γ=0.5, 1.0, 2.0 to find community structure at different granularities
# γ=0.5: larger communities (entire fraud networks)
# γ=2.0: tighter communities (specific fraud sub-rings)
results = {}
for gamma in [0.5, 1.0, 2.0]:
    best_q, best_part = -1, None
    for _ in range(20):
        part = best_partition(G, weight='weight', resolution=gamma)
        q = compute_modularity(G, part)
        if q > best_q:
            best_q, best_part = q, part
    results[gamma] = (best_q, best_part)

# Select resolution based on highest Q; report Q alongside results
```

**Step 3: Score community risk and flag high-density communities.**

Join community assignments to known-fraud labels. Flag communities where `fraud_density >= 0.10`.

**Step 4: Within flagged communities, rank by betweenness centrality.**

```python
for cid in high_risk_communities:
    subgraph_nodes = [n for n, c in partition.items() if c == cid]
    H = G.subgraph(subgraph_nodes)
    btw = nx.betweenness_centrality(H, weight='weight', normalized=True)
    # Top-betweenness nodes within the ring = coordinators / mule managers
    ring_leaders = sorted(btw.items(), key=lambda x: x[1], reverse=True)[:3]
```

**Step 5: Link prediction to anticipate ring growth.**

Use common neighbours or Jaccard coefficient on the current graph to predict which currently-clean accounts are most likely to be added to a flagged ring. Accounts in the top-10% of predicted link probability to a flagged community are candidates for proactive review.

**Expected output.** A dbt mart `fct_fraud_communities` with community_id, risk tier, member count, fraud density, and the top-3 betweenness-central accounts per high-risk community. Risk operations queue is populated with high-density community members ordered by betweenness rank within the ring.

---

### R3 — dbt Dependency Graph PageRank for Release-Risk Scoring

**Scenario.** A data engineering team wants to introduce release gates: before merging any dbt model change, automatically score the blast radius of that change and route high-risk changes to senior review. The scoring should be based on transitive downstream impact, not just direct dependencies.

**Stack**: #02 PageRank (blast-radius scoring) → #06 Percolation (failure cascade threshold) → #04 Small World (diameter check for impact propagation speed)

**Step 1: Parse the dbt manifest and build the dependency graph.**

```python
import json, networkx as nx

manifest = json.load(open('target/manifest.json'))
G = nx.DiGraph()
model_names = {}

for node_id, node in manifest['nodes'].items():
    if node['resource_type'] != 'model':
        continue
    model_names[node_id] = node['name']
    for dep in node.get('depends_on', {}).get('nodes', []):
        if dep in manifest['nodes']:
            G.add_edge(dep, node_id)
```

**Step 2: Compute reverse-PageRank (blast-radius score).**

```python
G_rev = G.reverse(copy=True)
pr_blast = nx.pagerank(G_rev, alpha=0.65)

blast_scores = pd.DataFrame([
    {'model_id': nid, 'model_name': model_names.get(nid, nid), 'blast_radius_pr': score}
    for nid, score in pr_blast.items()
]).sort_values('blast_radius_pr', ascending=False)
```

**Step 3: Assign risk tiers.**

```python
p80 = blast_scores['blast_radius_pr'].quantile(0.80)
p95 = blast_scores['blast_radius_pr'].quantile(0.95)

blast_scores['risk_tier'] = pd.cut(
    blast_scores['blast_radius_pr'],
    bins=[-np.inf, p80, p95, np.inf],
    labels=['standard', 'elevated', 'critical']
)
# Standard: merge with passing tests
# Elevated: senior review required
# Critical: requires contract validation + dual approval + backfill plan
```

**Step 4: Integrate with CI pipeline.**

```bash
# In CI (GitHub Actions / dbt Cloud job):
# 1. Run dbt compile to generate manifest
# 2. Run Python script to score changed models
# 3. Fail CI if any changed model is 'critical' and no senior-review label is present

python scripts/score_blast_radius.py \
    --manifest target/manifest.json \
    --changed-models "$(dbt ls --select state:modified)" \
    --output ci_blast_scores.json

# Exit code 1 if critical model changed without approval token
python scripts/gate_critical_changes.py --scores ci_blast_scores.json
```

**Step 5: Publish scores as a dbt seed.**

Write `blast_scores` to `seeds/model_blast_radius.csv`. Reference it in dbt documentation and in the ownership catalog (`assets/ownership-catalog-worksheet.md`). Refresh on every manifest rebuild (CI pass).

**Expected output.** A versioned `model_blast_radius` seed in the dbt project, a CI gate that blocks unreviewed critical-tier model changes, and a dashboard showing the top-20 highest-blast-radius models with their current contract and test coverage status. The risk tier becomes a field in the data catalog.

---

## Composition

| Workflow | Primary method | Supporting | Output artefact |
|----------|---------------|-----------|----------------|
| Influencer identification for growth campaign | P1 Centrality (betweenness + eigenvector) | P4 SIR seed selection | `fct_customer_centrality` |
| Viral product growth forecasting | P4 SIR Monte Carlo | P1 PageRank seeds, P5 Temporal window | `fct_referral_campaign_forecast` |
| Fraud ring detection | P3 Community Detection | P1 Betweenness (within ring), P7 Embeddings | `fct_fraud_communities` |
| dbt pipeline criticality | P2 Reverse-PageRank | — | `model_blast_radius` seed |
| Customer behavioural segmentation | P7 Graph Embeddings | P1 Centrality features, P6 Graph Clustering | `fct_customer_graph_segments` |
| Churn cascade early warning | P8 Churn SIR/SI | P3 Community risk, P1 Centrality | `fct_churn_contagion_risk` |
| Temporal co-engagement analytics | P5 Temporal User-Item | P6 Session Clustering | `fct_user_item_temporal_edges` |

**Do not stack graph and attribute features without normalisation.** Combining raw graph embedding dimensions with numeric attribute features (ARR, seat count) requires standardisation — raw attribute values dominate due to scale difference.

**Community detection and SIR are complementary, not interchangeable.** Use community detection to find the structure; use SIR to model dynamics within and across that structure. Communities define spread barriers; SIR measures how fast spread happens despite those barriers.

---

## Primitive Links

| Pattern / Anti-Pattern | Primitive | File |
|------------------------|-----------|------|
| Customer-graph centrality, influencer ranking | #01 Centrality Measures | [`../../foundations-network-science/assets/templates/network-science/01-centrality-measures.md`](../../foundations-network-science/assets/templates/network-science/01-centrality-measures.md) |
| dbt blast-radius scoring, pipeline criticality | #02 PageRank | [`../../foundations-network-science/assets/templates/network-science/02-pagerank.md`](../../foundations-network-science/assets/templates/network-science/02-pagerank.md) |
| Fraud ring detection, behavioural archetypes | #03 Community Detection | [`../../foundations-network-science/assets/templates/network-science/03-community-detection.md`](../../foundations-network-science/assets/templates/network-science/03-community-detection.md) |
| Temporal reachability baseline | #04 Small World | [`../../foundations-network-science/assets/templates/network-science/04-small-world.md`](../../foundations-network-science/assets/templates/network-science/04-small-world.md) |
| Network-aware R₀ for viral growth | #05 Scale-Free Networks | [`../../foundations-network-science/assets/templates/network-science/05-scale-free-networks.md`](../../foundations-network-science/assets/templates/network-science/05-scale-free-networks.md) |
| Failure cascade threshold for CI gates | #06 Percolation | [`../../foundations-network-science/assets/templates/network-science/06-percolation.md`](../../foundations-network-science/assets/templates/network-science/06-percolation.md) |
| Referral-cascade SIR, churn contagion | #07 Contagion / SIR | [`../../foundations-network-science/assets/templates/network-science/07-contagion-sir.md`](../../foundations-network-science/assets/templates/network-science/07-contagion-sir.md) |
| Fraud ring growth anticipation | #08 Link Prediction | [`../../foundations-network-science/assets/templates/network-science/08-link-prediction.md`](../../foundations-network-science/assets/templates/network-science/08-link-prediction.md) |
| Sessionized event-graph clustering | #09 Graph Clustering | [`../../foundations-network-science/assets/templates/network-science/09-graph-clustering.md`](../../foundations-network-science/assets/templates/network-science/09-graph-clustering.md) |
| Embedding-based customer segmentation | #10 Graph Embeddings | [`../../foundations-network-science/assets/templates/network-science/10-graph-embeddings.md`](../../foundations-network-science/assets/templates/network-science/10-graph-embeddings.md) |
| Temporal user-item graph, bursty event streams | #11 Temporal Networks | [`../../foundations-network-science/assets/templates/network-science/11-temporal-networks.md`](../../foundations-network-science/assets/templates/network-science/11-temporal-networks.md) |
| Degree ≠ influence (A1) | #01 Centrality, #02 PageRank | see above |
| Static community detection staleness (A2) | #03 Community Detection, #11 Temporal | see above |
| Static SIR on bursty events (A3) | #07 SIR, #11 Temporal | see above |
| Web-default damping on non-web graphs (A4) | #02 PageRank | see above |
| Embedding vocabulary drift (A5) | #10 Graph Embeddings | see above |

**Full primitive reference**: [`../../foundations-network-science/SKILL.md`](../../foundations-network-science/SKILL.md)

---

## Sources

- Newman, M.E.J. (2010). *Networks: An Introduction*. Oxford University Press. §11 (community detection), §17 (SIR/contagion), §18 (temporal networks). Canonical textbook reference for all structural graph algorithms.
- Barabási, A.-L. (2016). *Network Science*. Cambridge University Press. [networksciencebook.com](https://networksciencebook.com/). §10 (spreading phenomena), §9 (communities). Open-access.
- Blondel, V.D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics*. [doi:10.1088/1742-5468/2008/10/P10008](https://doi.org/10.1088/1742-5468/2008/10/P10008). Louvain algorithm; foundation for fraud-ring detection pattern.
- Pastor-Satorras, R., & Vespignani, A. (2001). Epidemic spreading in scale-free networks. *Physical Review Letters*, 86(14). [doi:10.1103/PhysRevLett.86.3200](https://doi.org/10.1103/PhysRevLett.86.3200). Network-aware R₀ formula; vanishing epidemic threshold used in P4.
- Holme, P., & Saramäki, J. (2012). Temporal networks. *Physics Reports*, 519(3). [doi:10.1016/j.physrep.2012.03.001](https://doi.org/10.1016/j.physrep.2012.03.001). Burstiness parameter, time-respecting paths; foundation for P5 and A3.
- Page, L., Brin, S., Motwani, R., & Winograd, T. (1999). The PageRank citation ranking: Bringing order to the web. Stanford Technical Report. [ilpubs.stanford.edu:8090/422/](http://ilpubs.stanford.edu:8090/422/). Original PageRank definition; damping factor calibration context for A4.
- Grover, A., & Leskovec, J. (2016). node2vec: Scalable feature learning for networks. *KDD 2016*. [doi:10.1145/2939672.2939754](https://doi.org/10.1145/2939672.2939754). Node2Vec embedding algorithm used in P7.
- Hamilton, W.L., Ying, R., & Leskovec, J. (2017). Inductive representation learning on large graphs. *NeurIPS 2017*. [arxiv:1706.02216](https://arxiv.org/abs/1706.02216). GraphSAGE; attribute-aware graph embeddings for P7.
- Fortunato, S. (2010). Community detection in graphs. *Physics Reports*, 486(3–5). [doi:10.1016/j.physrep.2009.11.002](https://doi.org/10.1016/j.physrep.2009.11.002). Resolution limit analysis; foundation for A2 (snapshot staleness).
- Bollen, J., Mao, H., & Zeng, X. (2011). Twitter mood predicts the stock market. *Journal of Computational Science*, 2(1). Social contagion measurement methodology referenced in P8 churn contagion calibration framing.
- NetworkX library: [networkx.org](https://networkx.org/). Python graph analysis library used throughout all code examples. Supports PageRank, betweenness centrality, Louvain, spectral clustering, and temporal path analysis.
