---
description: Network-science decision rules for multi-agent systems: when a call-graph analysis is worth running, betweenness over degree for bottlenecks, time-respecting paths for debugging, and checkpoint placement.
last_verified: 2026-09-24
status: stable
---

# Network Science Applied to Multi-Agent Systems

> **Gate before invoking:** Check [`foundations-network-science` § When to Apply](../../foundations-network-science/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

Centrality, PageRank, community detection, small-world, scale-free, percolation, SIR, embeddings and temporal networks are covered in the foundation. Most agent teams are too small for graph statistics. Read the trace directly unless the rules below apply.

## Decision rules

1. **Run graph analysis only once there is a graph.** That starts at roughly ten or more agents or tools, with ten or more session traces to build edges from. Below that, centrality, community and embedding scores are noise. Inspect the trace by hand.
2. **Find bottlenecks with betweenness, not call volume.** An agent many others call (high in-degree) is not a broker if its callers have other paths. Only high betweenness marks an agent whose slowdown or failure cuts work streams. For that agent, decide between splitting it, replicating it, or re-routing callers straight to its targets. Before merging specialists into one hub, simulate removing the hub and compare how many agents can still complete work before and after.
3. **Debug along time-respecting paths.** A call at t = 200 ms cannot have caused an error seen at t = 180 ms, even when the static graph has the edge. Build the timestamped call graph for the failing session and trace only paths that arrive before the error. A static graph overstates reach.
4. **Put validation checkpoints where errors cross boundaries:** on the receiving side of calls between clusters, and on the highest-betweenness agents. On hub-heavy graphs, `R₀ = (β/γ)·⟨k²⟩/⟨k⟩` lets an error spread even when the per-call pass-on rate β is low. Estimate β and γ from your own error logs. A default range is a guess, not a measurement.

## Worked recipe — bottleneck audit from traces

```python
import networkx as nx
G = nx.DiGraph()
for t in traces:                                  # ≥10 sessions (rule 1)
    for c in t["calls"]:
        w = G.get_edge_data(c["from"], c["to"], {"weight": 0})["weight"]
        G.add_edge(c["from"], c["to"], weight=w + 1)
# betweenness treats weight as distance, so give frequent edges short distances
for u, v, d in G.edges(data=True):
    d["dist"] = 1 / d["weight"]
btw = nx.betweenness_centrality(G, normalized=True, weight="dist")
indeg = dict(G.in_degree(weight="weight"))
for a in sorted(btw, key=btw.get, reverse=True)[:3]:
    H = G.copy(); H.remove_node(a)
    frac = max(len(c) for c in nx.weakly_connected_components(H)) / len(H)
    print(a, round(btw[a], 2), indeg[a], f"largest component after removal {frac:.0%}")
```

An agent with high betweenness whose removal leaves the largest component well below the whole graph is a single point of failure. Give it a circuit breaker ([control-theory-applied.md](control-theory-applied.md)) and a replica before scaling the team. An agent with high in-degree but low betweenness only needs capacity. That is a queueing question ([queueing-theory-applied.md](queueing-theory-applied.md)).

## Related

- [team-selection-guide.md](team-selection-guide.md): picking members. Past co-occurrence in traces is a weak signal that doesn't replace role fit.
- Primary sources: Freeman (1977); Watts & Strogatz (1998); Barabási & Albert (1999); Holme & Saramäki (2012), all cited in the foundation.
