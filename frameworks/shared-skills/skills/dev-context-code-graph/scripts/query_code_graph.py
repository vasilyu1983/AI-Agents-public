#!/usr/bin/env python3
"""Query a code graph by neighborhood, impact, path, type, rank, structural risk, search, or diagram export."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path


MERMAID_DIRECTIONS = ("LR", "RL", "TD", "TB", "BT")
MERMAID_TYPE_STYLES = {
    "repo": "fill:#dbeafe,stroke:#1d4ed8,color:#0f172a",
    "file": "fill:#f3f4f6,stroke:#4b5563,color:#111827",
    "class": "fill:#ede9fe,stroke:#7c3aed,color:#1f2937",
    "function": "fill:#dcfce7,stroke:#15803d,color:#14532d",
    "method": "fill:#ccfbf1,stroke:#0f766e,color:#134e4a",
    "test": "fill:#fee2e2,stroke:#dc2626,color:#7f1d1d",
    "external_symbol": "fill:#fde68a,stroke:#d97706,color:#78350f",
}


def load_graph(graph_path: str) -> tuple[list[dict], list[dict], dict[str, dict]]:
    data = json.loads(Path(graph_path).read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    return nodes, edges, {node["id"]: node for node in nodes if "id" in node}


def build_adjacency(edges: list[dict]) -> tuple[dict[str, list[tuple[str, dict]]], dict[str, list[tuple[str, dict]]]]:
    forward: dict[str, list[tuple[str, dict]]] = {}
    backward: dict[str, list[tuple[str, dict]]] = {}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if not source or not target:
            continue
        forward.setdefault(source, []).append((target, edge))
        backward.setdefault(target, []).append((source, edge))
    return forward, backward


def bfs_neighborhood(start: str, forward: dict, backward: dict, hops: int) -> tuple[set[str], list[dict]]:
    visited_nodes = {start}
    visited_edges: list[dict] = []
    edge_keys: set[tuple[str, str, str]] = set()
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        node_id, depth = queue.popleft()
        if depth >= hops:
            continue
        for neighbor, edge in forward.get(node_id, []):
            key = (edge["source"], edge["target"], edge["relation"])
            if key not in edge_keys:
                edge_keys.add(key)
                visited_edges.append(edge)
            visited_nodes.add(neighbor)
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, depth + 1))
        for neighbor, edge in backward.get(node_id, []):
            key = (edge["source"], edge["target"], edge["relation"])
            if key not in edge_keys:
                edge_keys.add(key)
                visited_edges.append(edge)
            visited_nodes.add(neighbor)
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, depth + 1))
    return visited_nodes, visited_edges


def bfs_impact(start: str, forward: dict, hops: int) -> tuple[set[str], list[dict]]:
    visited_nodes = {start}
    visited_edges: list[dict] = []
    edge_keys: set[tuple[str, str, str]] = set()
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        node_id, depth = queue.popleft()
        if depth >= hops:
            continue
        for neighbor, edge in forward.get(node_id, []):
            key = (edge["source"], edge["target"], edge["relation"])
            if key not in edge_keys:
                edge_keys.add(key)
                visited_edges.append(edge)
            visited_nodes.add(neighbor)
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, depth + 1))
    return visited_nodes, visited_edges


def bfs_paths(start: str, end: str, forward: dict, max_hops: int) -> list[list[str]]:
    if start == end:
        return [[start]]
    queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
    found: list[list[str]] = []
    shortest = None
    while queue:
        node_id, path = queue.popleft()
        if shortest is not None and len(path) - 1 >= shortest:
            continue
        if len(path) - 1 >= max_hops:
            continue
        for neighbor, _edge in forward.get(node_id, []):
            if neighbor in path:
                continue
            new_path = path + [neighbor]
            if neighbor == end:
                shortest = len(new_path) - 1
                found.append(new_path)
                continue
            queue.append((neighbor, new_path))
    return found


def k_node_disjoint_paths(start: str, end: str, forward: dict, max_hops: int, k: int) -> list[list[str]]:
    """Return up to k shortest paths, avoiding intermediate nodes from prior paths."""
    if k <= 1:
        return bfs_paths(start, end, forward, max_hops)

    blocked: set[str] = set()
    paths: list[list[str]] = []
    for _ in range(k):
        queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
        found_path: list[str] | None = None
        while queue:
            node_id, path = queue.popleft()
            if len(path) - 1 >= max_hops:
                continue
            for neighbor, _edge in forward.get(node_id, []):
                if neighbor in path:
                    continue
                if neighbor in blocked and neighbor not in {start, end}:
                    continue
                next_path = path + [neighbor]
                if neighbor == end:
                    found_path = next_path
                    queue.clear()
                    break
                queue.append((neighbor, next_path))
        if not found_path:
            break
        paths.append(found_path)
        blocked.update(found_path[1:-1])
    return paths


def relation_set(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {item.strip() for item in raw.split(",") if item.strip()}


def filtered_edges(edges: list[dict], relations: set[str]) -> list[dict]:
    if not relations:
        return edges
    return [edge for edge in edges if edge.get("relation") in relations]


def undirected_neighbors(edges: list[dict]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if not source or not target:
            continue
        graph[source].add(target)
        graph[target].add(source)
    return graph


def articulation_points(edges: list[dict], top: int = 20) -> list[dict]:
    graph = undirected_neighbors(edges)
    timer = 0
    discovery: dict[str, int] = {}
    low: dict[str, int] = {}
    parent: dict[str, str | None] = {}
    points: dict[str, int] = {}

    def dfs(node: str) -> None:
        nonlocal timer
        discovery[node] = low[node] = timer
        timer += 1
        children = 0
        separated = 0
        for neighbor in sorted(graph[node]):
            if neighbor not in discovery:
                parent[neighbor] = node
                children += 1
                dfs(neighbor)
                low[node] = min(low[node], low[neighbor])
                if parent.get(node) is None:
                    continue
                if low[neighbor] >= discovery[node]:
                    separated += 1
            elif neighbor != parent.get(node):
                low[node] = min(low[node], discovery[neighbor])
        if parent.get(node) is None and children > 1:
            points[node] = children
        elif parent.get(node) is not None and separated:
            points[node] = separated + 1

    for node in sorted(graph):
        if node not in discovery:
            parent[node] = None
            dfs(node)

    rows = [
        {"node_id": node, "components_disconnected_if_removed": count}
        for node, count in points.items()
    ]
    rows.sort(key=lambda item: (-item["components_disconnected_if_removed"], item["node_id"]))
    return rows if top == 0 else rows[:top]


def bridge_edges(edges: list[dict], top: int = 20) -> list[dict]:
    graph = undirected_neighbors(edges)
    timer = 0
    discovery: dict[str, int] = {}
    low: dict[str, int] = {}
    parent: dict[str, str | None] = {}
    bridges: list[dict] = []

    def dfs(node: str) -> None:
        nonlocal timer
        discovery[node] = low[node] = timer
        timer += 1
        for neighbor in sorted(graph[node]):
            if neighbor not in discovery:
                parent[neighbor] = node
                dfs(neighbor)
                low[node] = min(low[node], low[neighbor])
                if low[neighbor] > discovery[node]:
                    bridges.append({"source": node, "target": neighbor})
            elif neighbor != parent.get(node):
                low[node] = min(low[node], discovery[neighbor])

    for node in sorted(graph):
        if node not in discovery:
            parent[node] = None
            dfs(node)

    bridges.sort(key=lambda item: (item["source"], item["target"]))
    return bridges if top == 0 else bridges[:top]


def cycles_by_relation(edges: list[dict], relations: set[str]) -> list[dict]:
    selected_relations = relations or {str(edge.get("relation")) for edge in edges if edge.get("relation")}
    rows: list[dict] = []
    for relation in sorted(selected_relations):
        forward = defaultdict(list)
        for edge in edges:
            if edge.get("relation") == relation:
                forward[edge.get("source")].append(edge.get("target"))
        visited: set[str] = set()
        stack: list[str] = []
        in_stack: set[str] = set()
        seen_cycles: set[tuple[str, ...]] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            stack.append(node)
            in_stack.add(node)
            for neighbor in sorted(item for item in forward.get(node, []) if item):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in in_stack:
                    idx = stack.index(neighbor)
                    cycle = stack[idx:] + [neighbor]
                    canonical = tuple(sorted(cycle[:-1]))
                    if canonical not in seen_cycles:
                        seen_cycles.add(canonical)
                        rows.append({"relation": relation, "cycle": cycle, "length": len(cycle) - 1})
            stack.pop()
            in_stack.remove(node)

        for node in sorted(forward):
            if node not in visited:
                dfs(node)
    rows.sort(key=lambda item: (item["relation"], item["length"], item["cycle"]))
    return rows


def topological_sort(edges: list[dict], relation: str) -> tuple[list[str], list[dict]]:
    relation_edges = [edge for edge in edges if edge.get("relation") == relation]
    cycles = cycles_by_relation(relation_edges, {relation})
    if cycles:
        return [], cycles
    nodes: set[str] = set()
    indegree: dict[str, int] = defaultdict(int)
    forward: dict[str, list[str]] = defaultdict(list)
    for edge in relation_edges:
        source = edge.get("source")
        target = edge.get("target")
        if not source or not target:
            continue
        nodes.update([source, target])
        forward[source].append(target)
        indegree[target] += 1
        indegree.setdefault(source, 0)
    queue = deque(sorted(node for node in nodes if indegree[node] == 0))
    ordered: list[str] = []
    while queue:
        node = queue.popleft()
        ordered.append(node)
        for neighbor in sorted(forward.get(node, [])):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    return ordered, []


def query_search(nodes: list[dict], query: str, types: set[str] | None = None, limit: int = 20) -> list[dict]:
    terms = [term for term in re.split(r"\s+", query.lower().strip()) if term]
    matches: list[tuple[int, dict]] = []
    for node in nodes:
        if types and node.get("type") not in types:
            continue
        haystack = " ".join(
            [
                str(node.get("id", "")),
                str(node.get("label", "")),
                str(node.get("path", "")),
                str(node.get("summary", "")),
                " ".join(str(tag) for tag in node.get("tags", [])),
                " ".join(f"{key} {value}" for key, value in (node.get("properties") or {}).items()),
            ]
        ).lower()
        score = sum(term in haystack for term in terms)
        if score:
            matches.append((score, node))
    matches.sort(key=lambda item: (-item[0], item[1].get("label", item[1]["id"])))
    limited = matches if limit == 0 else matches[:limit]
    return [node for _score, node in limited]


def personalized_pagerank(
    nodes: list[dict],
    edges: list[dict],
    seeds: list[str],
    *,
    alpha: float = 0.15,
    max_iter: int = 100,
    tol: float = 1e-9,
) -> dict[str, float]:
    """
    Weighted Personalized PageRank for hot-symbol blast-radius retrieval.

    Mirrors the multi-repo implementation: dependency-free, dangling mass
    redistributed through the seed vector, weights honoured per-edge.
    """
    node_ids = [node["id"] for node in nodes if "id" in node]
    if not node_ids:
        return {}

    node_set = set(node_ids)
    seed_set = [seed for seed in seeds if seed in node_set]
    if not seed_set:
        raise ValueError("at least one seed must exist in the graph")

    personalization = {node_id: 0.0 for node_id in node_ids}
    seed_weight = 1.0 / len(seed_set)
    for seed in seed_set:
        personalization[seed] = seed_weight

    outgoing: dict[str, list[tuple[str, float]]] = {node_id: [] for node_id in node_ids}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_set or target not in node_set:
            continue
        try:
            weight = float(edge.get("weight", 1.0))
        except (TypeError, ValueError):
            weight = 1.0
        if weight <= 0:
            continue
        outgoing[source].append((target, weight))

    scores = dict(personalization)
    for _ in range(max_iter):
        next_scores = {node_id: alpha * personalization[node_id] for node_id in node_ids}
        dangling_mass = 0.0

        for node_id, score in scores.items():
            weighted_targets = outgoing.get(node_id, [])
            if not weighted_targets:
                dangling_mass += score
                continue
            total_weight = sum(weight for _target, weight in weighted_targets)
            if total_weight <= 0:
                dangling_mass += score
                continue
            walk_mass = (1.0 - alpha) * score
            for target, weight in weighted_targets:
                next_scores[target] += walk_mass * (weight / total_weight)

        if dangling_mass:
            redistributed = (1.0 - alpha) * dangling_mass
            for node_id, seed_score in personalization.items():
                if seed_score:
                    next_scores[node_id] += redistributed * seed_score

        delta = sum(abs(next_scores[node_id] - scores.get(node_id, 0.0)) for node_id in node_ids)
        scores = next_scores
        if delta < tol:
            break

    total = sum(scores.values())
    if total > 0:
        scores = {node_id: value / total for node_id, value in scores.items()}
    return scores


def _undirected_adjacency(
    nodes: list[dict],
    edges: list[dict],
) -> tuple[dict[str, dict[str, float]], dict[str, float], float]:
    """Symmetric weighted adjacency for community detection."""
    node_ids = [node["id"] for node in nodes if "id" in node]
    node_set = set(node_ids)
    adjacency: dict[str, dict[str, float]] = {nid: {} for nid in node_ids}

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_set or target not in node_set or source == target:
            continue
        try:
            weight = float(edge.get("weight", 1.0))
        except (TypeError, ValueError):
            weight = 1.0
        if weight <= 0:
            continue
        adjacency[source][target] = adjacency[source].get(target, 0.0) + weight
        adjacency[target][source] = adjacency[target].get(source, 0.0) + weight

    node_strength = {nid: sum(neighbours.values()) for nid, neighbours in adjacency.items()}
    total_weight = sum(node_strength.values()) / 2.0
    return adjacency, node_strength, total_weight


class _DeterministicShuffler:
    """LCG-based shuffler so community detection stays reproducible."""

    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF or 1

    def _next(self) -> int:
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state

    def shuffle(self, items: list) -> None:
        for i in range(len(items) - 1, 0, -1):
            j = self._next() % (i + 1)
            items[i], items[j] = items[j], items[i]


def _louvain_pass(
    adjacency: dict[str, dict[str, float]],
    node_strength: dict[str, float],
    total_weight: float,
    resolution: float,
    seed: int,
) -> dict[str, str]:
    if total_weight <= 0:
        return {nid: nid for nid in adjacency}

    community = {nid: nid for nid in adjacency}
    community_strength: dict[str, float] = dict(node_strength)
    two_m = 2.0 * total_weight

    rng = _DeterministicShuffler(seed)
    nodes_in_order = list(adjacency.keys())

    improved = True
    iterations = 0
    max_iterations = 20
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        rng.shuffle(nodes_in_order)
        for nid in nodes_in_order:
            current = community[nid]
            ki = node_strength[nid]
            if ki <= 0:
                continue

            community_links: dict[str, float] = {}
            for neighbour, weight in adjacency[nid].items():
                if neighbour == nid:
                    continue
                community_links[community[neighbour]] = (
                    community_links.get(community[neighbour], 0.0) + weight
                )

            community_strength[current] -= ki

            best = current
            best_gain = 0.0
            for candidate, ki_in_candidate in community_links.items():
                sigma_tot = community_strength.get(candidate, 0.0)
                gain = (ki_in_candidate / total_weight) - resolution * (sigma_tot * ki) / (two_m * total_weight)
                if gain > best_gain + 1e-12:
                    best_gain = gain
                    best = candidate

            if best_gain <= 0:
                best = current

            community_strength[best] = community_strength.get(best, 0.0) + ki
            if best != current:
                community[nid] = best
                improved = True

    return community


def detect_communities(
    nodes: list[dict],
    edges: list[dict],
    *,
    resolution: float = 1.0,
    seed: int = 42,
    max_levels: int = 5,
) -> dict[str, str]:
    """
    Louvain-style community detection over the code graph.

    Returns node_id -> community_id mapping. Pure-python; for very large graphs
    (>50k edges), prefer a native Leiden implementation.
    """
    adjacency, node_strength, total_weight = _undirected_adjacency(nodes, edges)
    if total_weight <= 0:
        return {nid: nid for nid in adjacency}

    membership = _louvain_pass(adjacency, node_strength, total_weight, resolution, seed)

    for level in range(max_levels):
        super_adjacency: dict[str, dict[str, float]] = {}
        super_strength: dict[str, float] = {}

        for nid, neighbours in adjacency.items():
            community = membership[nid]
            super_adjacency.setdefault(community, {})
            super_strength[community] = super_strength.get(community, 0.0)
            for neighbour, weight in neighbours.items():
                neighbour_community = membership[neighbour]
                super_adjacency[community][neighbour_community] = (
                    super_adjacency[community].get(neighbour_community, 0.0) + weight
                )
                super_strength[community] += weight

        super_strength = {c: total / 2.0 + total / 2.0 for c, total in super_strength.items()}

        super_membership = _louvain_pass(
            super_adjacency,
            super_strength,
            total_weight,
            resolution,
            seed + level + 1,
        )

        if all(super_membership[c] == c for c in super_adjacency):
            break

        membership = {nid: super_membership[membership[nid]] for nid in adjacency}
        adjacency = super_adjacency
        node_strength = super_strength

    counts: dict[str, int] = {}
    for community in membership.values():
        counts[community] = counts.get(community, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    label_map = {c: f"community_{i}" for i, (c, _n) in enumerate(ordered)}

    return {nid: label_map[c] for nid, c in membership.items()}


def compute_modularity(edges: list[dict], membership: dict[str, str]) -> float:
    if not membership:
        return 0.0
    strength: dict[str, float] = {}
    intra: dict[str, float] = {}
    total_weight = 0.0

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source is None or target is None or source == target:
            continue
        if source not in membership or target not in membership:
            continue
        try:
            weight = float(edge.get("weight", 1.0))
        except (TypeError, ValueError):
            weight = 1.0
        if weight <= 0:
            continue
        strength[source] = strength.get(source, 0.0) + weight
        strength[target] = strength.get(target, 0.0) + weight
        total_weight += weight
        if membership[source] == membership[target]:
            intra[membership[source]] = intra.get(membership[source], 0.0) + 2 * weight

    if total_weight <= 0:
        return 0.0

    two_m = 2.0 * total_weight
    community_strength: dict[str, float] = {}
    for nid, community in membership.items():
        community_strength[community] = community_strength.get(community, 0.0) + strength.get(nid, 0.0)

    modularity = 0.0
    for community, intra_weight in intra.items():
        sigma_tot = community_strength.get(community, 0.0)
        modularity += (intra_weight / two_m) - (sigma_tot / two_m) ** 2
    return modularity


def summarize_communities(nodes: list[dict], membership: dict[str, str], top: int) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for node in nodes:
        nid = node.get("id")
        if not nid or nid not in membership:
            continue
        grouped.setdefault(membership[nid], []).append(node)

    summaries = []
    for community, members in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        types: dict[str, int] = {}
        files: dict[str, int] = {}
        sample_labels = []
        for node in members:
            type_key = node.get("type", "?")
            types[type_key] = types.get(type_key, 0) + 1
            path_key = node.get("path") or "?"
            files[path_key] = files.get(path_key, 0) + 1
            if len(sample_labels) < 5:
                sample_labels.append(node.get("label") or node.get("id"))
        summaries.append({
            "community_id": community,
            "size": len(members),
            "type_breakdown": dict(sorted(types.items(), key=lambda item: -item[1])),
            "top_files": dict(sorted(files.items(), key=lambda item: -item[1])[:5]),
            "sample_labels": sample_labels,
        })

    return summaries if top == 0 else summaries[:top]


def rank_nodes(nodes: list[dict], edges: list[dict], filter_type: str | None, top: int) -> list[dict]:
    incoming = defaultdict(float)
    for edge in edges:
        incoming[edge["target"]] += float(edge.get("weight", 1.0))
    ranked = []
    for node in nodes:
        if filter_type and node.get("type") != filter_type:
            continue
        ranked.append(
            {
                "id": node["id"],
                "type": node.get("type"),
                "label": node.get("label"),
                "importance": round(incoming.get(node["id"], 0.0), 3),
                "path": node.get("path"),
            }
        )
    ranked.sort(key=lambda item: (-item["importance"], item["label"]))
    return ranked if top == 0 else ranked[:top]


def format_json(payload: dict) -> str:
    return json.dumps(payload, indent=2)


def format_table(payload: dict) -> str:
    if "communities" in payload and payload.get("query") == "communities":
        summaries = payload["communities"]
        modularity = payload.get("modularity", 0.0)
        count = payload.get("community_count", len(summaries))
        if not summaries:
            return f"No communities (modularity={modularity}, count={count})."
        lines = [
            f"# Communities (modularity={modularity}, count={count})",
            "",
            "community_id | size | top_types | sample_labels",
            "--- | --- | --- | ---",
        ]
        for entry in summaries:
            top_types = ", ".join(f"{k}:{v}" for k, v in entry.get("type_breakdown", {}).items())
            samples = ", ".join(entry.get("sample_labels", [])[:3])
            lines.append(f"{entry['community_id']} | {entry['size']} | {top_types} | {samples}")
        return "\n".join(lines)
    rows = payload.get("results") or payload.get("nodes") or payload.get("paths") or []
    if not rows:
        return "No results."
    if isinstance(rows[0], list):
        return "\n".join(" -> ".join(item) for item in rows)
    headers = sorted({key for row in rows for key in row.keys()})
    lines = [" | ".join(headers), " | ".join("---" for _ in headers)]
    for row in rows:
        lines.append(" | ".join(str(row.get(header, "")) for header in headers))
    return "\n".join(lines)


def mermaid_safe_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not cleaned:
        return "node"
    if cleaned[0].isdigit():
        return f"n_{cleaned}"
    return cleaned


def mermaid_escape(value: str) -> str:
    return value.replace('"', '\\"')


def format_mermaid(payload: dict, direction: str) -> str:
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])
    lines = [f"flowchart {direction}"]
    for node in nodes:
        node_id = mermaid_safe_id(node["id"])
        label = mermaid_escape(node.get("label", node["id"]))
        lines.append(f'  {node_id}["{label}"]')
    for edge in edges:
        source = mermaid_safe_id(edge["source"])
        target = mermaid_safe_id(edge["target"])
        label = mermaid_escape(edge.get("relation", ""))
        lines.append(f"  {source} -->|{label}| {target}")
    for node_type, style in MERMAID_TYPE_STYLES.items():
        class_name = mermaid_safe_id(f"class_{node_type}")
        lines.append(f"  classDef {class_name} {style}")
        for node in nodes:
            if node.get("type") == node_type:
                lines.append(f"  class {mermaid_safe_id(node['id'])} {class_name}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", help="Path to code-graph.json")
    parser.add_argument("--node", help="Neighborhood around a node")
    parser.add_argument("--from", dest="from_id", help="Path search source node")
    parser.add_argument("--to", help="Path search target node")
    parser.add_argument("--type", dest="node_type", help="List all nodes of a given type")
    parser.add_argument("--impact", help="Downstream impact from a node")
    parser.add_argument("--rank", action="store_true", help="Rank nodes by weighted incoming edges")
    parser.add_argument("--ppr", action="store_true", help="Personalized PageRank from one or more --seed nodes")
    parser.add_argument("--seed", action="append", default=[], help="Seed node id for --ppr (repeatable)")
    parser.add_argument("--alpha", type=float, default=0.15, help="Teleport probability for --ppr (default: 0.15)")
    parser.add_argument("--include-seeds", action="store_true", help="Include seed nodes in --ppr results")
    parser.add_argument("--search", help="Lexical search query")
    parser.add_argument("--diagram", action="store_true", help="Export full graph or filtered subgraph as Mermaid")
    parser.add_argument("--articulation-points", action="store_true", help="List articulation points in the selected graph")
    parser.add_argument("--bridges", action="store_true", help="List bridge edges in the selected graph")
    parser.add_argument("--cycles", action="store_true", help="List directed cycles grouped by relation")
    parser.add_argument("--topo-sort", metavar="RELATION", help="Topologically sort the selected relation if it is acyclic")
    parser.add_argument("--communities", action="store_true", help="Detect modules via Louvain communities")
    parser.add_argument("--resolution", type=float, default=1.0, help="Resolution γ for --communities (default: 1.0; >1 favours smaller, <1 favours larger)")
    parser.add_argument("--community-seed", type=int, default=42, help="Deterministic seed for --communities (default: 42)")
    parser.add_argument("--hops", type=int, default=1, help="Hop depth for neighborhood and impact")
    parser.add_argument("--max-hops", type=int, default=3, help="Maximum path-finding depth")
    parser.add_argument("--k", type=int, default=1, help="Number of node-disjoint shortest paths for --from/--to")
    parser.add_argument("--top", type=int, default=20, help="Top rows for --rank")
    parser.add_argument("--filter-type", help="Optional node type filter for --rank")
    parser.add_argument("--types", help="Comma-separated node types for --search")
    parser.add_argument("--relations", help="Comma-separated relations for structural graph queries")
    parser.add_argument("--limit", type=int, default=20, help="Result limit for --search")
    parser.add_argument("--format", choices=("json", "table", "mermaid"), default="json")
    parser.add_argument("--output", help="Optional output file")
    parser.add_argument("--mermaid-direction", choices=MERMAID_DIRECTIONS, default="LR")
    args = parser.parse_args()

    nodes, edges, node_index = load_graph(args.graph)
    forward, backward = build_adjacency(edges)

    if sum(bool(value) for value in (args.node, args.from_id, args.node_type, args.impact, args.rank, args.ppr, args.search, args.diagram, args.articulation_points, args.bridges, args.cycles, args.topo_sort, args.communities)) != 1:
        print("Error: choose exactly one query mode", file=sys.stderr)
        return 1

    result: dict
    if args.node:
        node_ids, edge_rows = bfs_neighborhood(args.node, forward, backward, args.hops)
        result = {"query": "node", "nodes": [node_index[node_id] for node_id in sorted(node_ids) if node_id in node_index], "edges": edge_rows}
    elif args.impact:
        node_ids, edge_rows = bfs_impact(args.impact, forward, args.hops)
        result = {"query": "impact", "nodes": [node_index[node_id] for node_id in sorted(node_ids) if node_id in node_index], "edges": edge_rows}
    elif args.from_id:
        if not args.to:
            print("Error: --from requires --to", file=sys.stderr)
            return 1
        result = {"query": "path", "paths": k_node_disjoint_paths(args.from_id, args.to, forward, args.max_hops, args.k)}
    elif args.node_type:
        result = {"query": "type", "results": [node for node in nodes if node.get("type") == args.node_type]}
    elif args.rank:
        result = {"query": "rank", "results": rank_nodes(nodes, edges, args.filter_type, args.top)}
    elif args.ppr:
        if not args.seed:
            print("Error: --ppr requires at least one --seed", file=sys.stderr)
            return 1
        if not 0 < args.alpha < 1:
            print("Error: --alpha must be between 0 and 1", file=sys.stderr)
            return 1
        unknown_seeds = [seed for seed in args.seed if seed not in node_index]
        if unknown_seeds:
            print(f"Error: unknown seed(s): {', '.join(unknown_seeds)}", file=sys.stderr)
            return 1
        scores = personalized_pagerank(nodes, edges, args.seed, alpha=args.alpha)
        ranked = []
        seed_set = set(args.seed)
        allowed_types = {value.strip() for value in args.filter_type.split(",")} if args.filter_type else None
        for node in nodes:
            nid = node.get("id")
            if not nid:
                continue
            if not args.include_seeds and nid in seed_set:
                continue
            if allowed_types and node.get("type") not in allowed_types:
                continue
            ranked.append({
                "id": nid,
                "type": node.get("type"),
                "label": node.get("label"),
                "path": node.get("path"),
                "ppr_score": round(scores.get(nid, 0.0), 10),
            })
        ranked.sort(key=lambda item: (-item["ppr_score"], item.get("type") or "", item.get("label") or "", item["id"]))
        if args.top > 0:
            ranked = ranked[:args.top]
        result = {
            "query": "ppr",
            "seeds": args.seed,
            "alpha": args.alpha,
            "include_seeds": args.include_seeds,
            "results": ranked,
        }
    elif args.search:
        requested_types = {value.strip() for value in args.types.split(",")} if args.types else None
        result = {"query": "search", "results": query_search(nodes, args.search, requested_types, args.limit)}
    elif args.articulation_points:
        selected_edges = filtered_edges(edges, relation_set(args.relations))
        rows = articulation_points(selected_edges, args.top)
        for row in rows:
            node = node_index.get(row["node_id"], {})
            row["type"] = node.get("type")
            row["label"] = node.get("label")
            row["path"] = node.get("path")
        result = {"query": "articulation_points", "results": rows}
    elif args.bridges:
        selected_edges = filtered_edges(edges, relation_set(args.relations))
        result = {"query": "bridges", "results": bridge_edges(selected_edges, args.top)}
    elif args.cycles:
        result = {"query": "cycles", "results": cycles_by_relation(edges, relation_set(args.relations))}
    elif args.communities:
        if args.resolution <= 0:
            print("Error: --resolution must be > 0", file=sys.stderr)
            return 1
        membership = detect_communities(
            nodes,
            edges,
            resolution=args.resolution,
            seed=args.community_seed,
        )
        modularity = compute_modularity(edges, membership)
        summaries = summarize_communities(nodes, membership, args.top)
        result = {
            "query": "communities",
            "resolution": args.resolution,
            "seed": args.community_seed,
            "modularity": round(modularity, 6),
            "community_count": len({c for c in membership.values()}),
            "communities": summaries,
        }
    elif args.topo_sort:
        ordered, cycles = topological_sort(edges, args.topo_sort)
        if cycles:
            result = {"query": "topo_sort", "relation": args.topo_sort, "error": "cycles_detected", "results": cycles}
        else:
            result = {"query": "topo_sort", "relation": args.topo_sort, "results": [{"order": index + 1, "node_id": node_id, "label": node_index.get(node_id, {}).get("label")} for index, node_id in enumerate(ordered)]}
    else:
        result = {"query": "diagram", "nodes": nodes, "edges": edges}

    if args.format == "json":
        rendered = format_json(result)
    elif args.format == "table":
        rendered = format_table(result)
    else:
        if "nodes" not in result:
            print("Error: Mermaid output requires nodes and edges", file=sys.stderr)
            return 1
        rendered = format_mermaid(result, args.mermaid_direction)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
