# Frequent subgraphs and statistically enriched motifs

Load when the question concerns recurring **small structures**, rather than a node partition. Default to counting a declared pattern. Use discovery only when the pattern vocabulary is unknown and a bounded search is feasible; community detection does not answer this question.

## Select the counting problem

1. Define the collection unit: separate molecules, sessions or dependency snapshots, versus one large network. Declare node/edge labels, direction, multiedges, induced versus non-induced matching, pattern-size bounds and overlap handling. Duplicate snapshots can inflate support without independent evidence.
2. For a collection of graphs, use **transaction support**: the number (or fraction) of collection members containing at least one isomorphic copy. Count each member once, even if it contains many embeddings. Under matching rules where every superpattern occurrence contains its subpatterns, this support is anti-monotone and permits pruning infrequent extensions.
3. For a single network, declare occurrence semantics separately: distinct vertex sets, embeddings, or an explicit overlap-restricted measure. Automorphisms can multiply embeddings. Do not reuse transaction-support thresholds or anti-monotone pruning assumptions for raw occurrence counts.
4. When discovering frequent connected labeled patterns in a graph collection, consider **gSpan**: depth-first pattern growth with minimum DFS codes for canonical representation. The original paper establishes this search mechanism, not universal runtime superiority. Verify a chosen implementation's direction, label, multigraph and match semantics before use. Bound nodes/edges and minimum support; report incomplete searches when the time or memory budget ends.

For example, a triangle appearing ten times in one session and once in a second has transaction support two. A two-edge path can match within a triangle under non-induced matching, but cannot match its full three-node induced graph. Preserve that distinction in both gold cases and mining configuration.

## Frequency is not motif significance

A frequent subgraph is not automatically a statistically enriched motif. For a motif claim, compare the declared count with an explicit randomized-network ensemble preserving the relevant constraints, such as directed degree sequences, relation types or bipartite membership. State the null, randomization diagnostics, effect size, number of null samples and treatment of multiple tested patterns. A degree-preserving null answers a different question from an independent-edge null. If the null variance is zero, do not divide by it or manufacture a z-score.

Use planted positives, pattern-free negatives and node-ID relabeling controls before a large search. Labels with domain meaning must stay fixed during ID relabeling. Include a graph with extra edges to distinguish induced from non-induced matching, duplicate embeddings to check transaction support, and a reversed directed pattern where relevant. These tests establish counting semantics, not significance or downstream predictive value.

## Executable small-pattern control

Run with Python 3. This exhaustive oracle handles only simple, undirected, unlabeled graphs and three-node patterns; it does not implement gSpan or estimate motif significance. It counts each vertex set once, avoiding permutation multiplicity.

```python
from itertools import combinations, permutations

def graph(edges):
    return {frozenset(e) for e in edges}

def occurrences(edges, pattern, induced=False):
    vertices = set().union(*edges) if edges else set()
    n = len(set().union(*pattern))
    count = 0
    for group in combinations(sorted(vertices), n):
        inside = {e for e in edges if e <= set(group)}
        for order in permutations(group):
            mapped = {frozenset(order[i] for i in e) for e in pattern}
            if mapped <= inside and (not induced or mapped == inside):
                count += 1
                break
    return count

def support(collection, pattern, induced=False):
    return sum(occurrences(g, pattern, induced) > 0 for g in collection)

triangle = graph([(0, 1), (1, 2), (0, 2)])
path = graph([(0, 1), (1, 2)])
two_triangles = triangle | graph([(3, 4), (4, 5), (3, 5)])
collection = [two_triangles, triangle, path]
assert occurrences(two_triangles, triangle) == 2
assert support(collection, triangle) == 2  # graphs, not embeddings
assert support(collection, path) == 3      # non-induced
assert support(collection, path, induced=True) == 1
assert support([path], triangle) == 0      # pattern-free negative
rename = {i: 20 - i for i in range(6)}
relabeled = {frozenset(rename[i] for i in e) for e in two_triangles}
assert occurrences(relabeled, triangle) == 2
assert support(collection, triangle) <= support(collection, path)
print('planted, negative, relabeling and support controls passed')
```

## Sources and boundary

- Bhattacharya et al. (eds.), *Graph Mining*, ch. 5 §§5.2–5.3, printed pp. 57–60 (PDF 68–71), supplied the topic lead. Its algorithm comparisons are not a reproducible benchmark contract; do not inherit numerical performance claims.
- Yan & Han (2002), *gSpan: Graph-Based Substructure Pattern Mining*, ICDM, pp. 721–724, [original author-hosted paper](https://sites.cs.ucsb.edu/~xyan/papers/gSpan-short.pdf), §§1–3: graph-collection support, connected-pattern search and canonical minimum DFS codes.
- Milo et al. (2002), *Network Motifs: Simple Building Blocks of Complex Networks*, Science 298, pp. 824–827, [author-lab publication record and abstract](https://www.weizmann.ac.il/plants/milo/publications): motifs require enrichment relative to randomized networks.

Training graph classifiers from mined patterns belongs to `ai-ml-data-science`; discover patterns on training data only before assessing held-out predictive value.
