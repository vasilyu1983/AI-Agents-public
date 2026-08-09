#!/usr/bin/env python3
"""
Query a knowledge graph by node neighborhood, paths, type listing, impact analysis, rank, PPR, search, or filtered diagram export.

Usage:
  python3 query_graph.py <graph.json> --node <id> [--hops N] [--format json|mermaid|table]
  python3 query_graph.py <graph.json> --from <id> --to <id> [--max-hops N] [--format ...]
  python3 query_graph.py <graph.json> --type <node_type> [--format ...]
  python3 query_graph.py <graph.json> --impact <id> [--hops N] [--format ...]
  python3 query_graph.py <graph.json> --rank [--top N] [--filter-type TYPE] [--format table|json]
  python3 query_graph.py <graph.json> --ppr --seed <id> [--top N] [--filter-type TYPE1,TYPE2] [--weights static|calibrated]
  python3 query_graph.py <graph.json> --search "query terms" [--types repo,process] [--limit N] [--format ...]
  python3 query_graph.py <graph.json> --diagram [--include-types repo,provider] [--exclude-relations documents] [--format mermaid] [--output graph.mmd]
"""
import argparse
import json
import re
import sys
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path


MERMAID_DIRECTIONS = ("LR", "RL", "TD", "TB", "BT")
MERMAID_GROUP_BY = ("none", "type", "domain")
MERMAID_TYPE_STYLES = {
    "repo": "fill:#dbeafe,stroke:#1d4ed8,color:#0f172a",
    "domain": "fill:#ede9fe,stroke:#7c3aed,color:#1f2937",
    "provider": "fill:#fef3c7,stroke:#d97706,color:#1f2937",
    "process": "fill:#dcfce7,stroke:#15803d,color:#14532d",
    "api_endpoint": "fill:#fee2e2,stroke:#dc2626,color:#7f1d1d",
    "message_topic": "fill:#cffafe,stroke:#0891b2,color:#164e63",
    "storage": "fill:#e5e7eb,stroke:#4b5563,color:#111827",
    "artifact": "fill:#f3f4f6,stroke:#6b7280,color:#111827",
    "service": "fill:#fde68a,stroke:#ca8a04,color:#78350f",
    "library": "fill:#fce7f3,stroke:#db2777,color:#831843",
    "package": "fill:#fce7f3,stroke:#db2777,color:#831843",
    "entity": "fill:#ecfccb,stroke:#65a30d,color:#365314",
}

# ---------------------------------------------------------------------------
# Graph loading and adjacency list construction
# ---------------------------------------------------------------------------

_TEMPORAL_AS_OF: datetime | None = None
_TEMPORAL_KNOWN_AT: datetime | None = None


def set_temporal_window(*, as_of: datetime | None, known_at: datetime | None) -> None:
    """Configure the bitemporal slice every load_graph call honors."""
    global _TEMPORAL_AS_OF, _TEMPORAL_KNOWN_AT
    _TEMPORAL_AS_OF = as_of
    _TEMPORAL_KNOWN_AT = known_at


def load_graph(graph_path: str) -> tuple[list[dict], list[dict], dict[str, dict]]:
    """Load graph JSON and return (nodes, edges, node_index).

    Edges are filtered through the active bitemporal window when one is set
    via set_temporal_window(); otherwise only currently-valid edges are
    returned (i.e. valid_until and ingested_until are absent).
    """
    path = Path(graph_path)
    if not path.exists():
        print(f"Error: file not found: {graph_path}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: JSON parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    if _has_temporal_metadata(edges):
        edges = filter_edges_temporal(edges, as_of=_TEMPORAL_AS_OF, known_at=_TEMPORAL_KNOWN_AT)

    node_index = {n["id"]: n for n in nodes if "id" in n}
    return nodes, edges, node_index


def _has_temporal_metadata(edges: list[dict]) -> bool:
    """Detect whether the graph carries any bitemporal fields at all.

    Graphs that have not yet adopted the bitemporal schema should not be
    silently filtered to empty results when the user passes neither flag.
    """
    if _TEMPORAL_AS_OF is not None or _TEMPORAL_KNOWN_AT is not None:
        return True
    for edge in edges:
        if any(_has_value(edge.get(field)) for field in ("valid_at", "valid_until", "ingested_at", "ingested_until")):
            return True
    return False


# ---------------------------------------------------------------------------
# Bitemporal filtering
# ---------------------------------------------------------------------------

def _parse_iso(value) -> datetime | None:
    """Parse an ISO-8601 string into an aware datetime. Returns None on failure."""
    if not value or not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        # Tolerate plain dates: 2026-04-01
        try:
            dt = datetime.strptime(raw[:10], "%Y-%m-%d")
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def filter_edges_temporal(
    edges: list[dict],
    *,
    as_of: datetime | None = None,
    known_at: datetime | None = None,
) -> list[dict]:
    """
    Apply bitemporal filtering to edges.

    Default (no filters): return only edges currently valid in both timelines —
    valid_until is null/missing AND ingested_until is null/missing.

    --as-of T (event time): keep edges where valid_at <= T < valid_until
    (or no event-time fields are set).

    --known-at T (transaction/ingest time): keep edges where ingested_at <= T <
    ingested_until (or no transaction-time fields are set).

    Both can be combined to answer "what did the system on date Y believe was
    true on date X" — the canonical bitemporal question.
    """
    if as_of is None and known_at is None:
        return [
            edge for edge in edges
            if not _has_value(edge.get("valid_until")) and not _has_value(edge.get("ingested_until"))
        ]

    selected: list[dict] = []
    for edge in edges:
        valid_at = _parse_iso(edge.get("valid_at"))
        valid_until = _parse_iso(edge.get("valid_until"))
        ingested_at = _parse_iso(edge.get("ingested_at"))
        ingested_until = _parse_iso(edge.get("ingested_until"))

        if as_of is not None:
            # Edge must have started by as_of (or have no valid_at fact)
            if valid_at is not None and valid_at > as_of:
                continue
            # Edge must not have ended before as_of
            if valid_until is not None and valid_until <= as_of:
                continue

        if known_at is not None:
            if ingested_at is not None and ingested_at > known_at:
                continue
            if ingested_until is not None and ingested_until <= known_at:
                continue

        selected.append(edge)

    return selected


def _has_value(field) -> bool:
    if field is None:
        return False
    if isinstance(field, str) and not field.strip():
        return False
    return True


def build_adjacency(edges: list[dict]) -> tuple[dict, dict]:
    """
    Build forward (outgoing) and backward (incoming) adjacency lists.
    Returns (fwd, bwd) where each maps node_id → list of (neighbor_id, edge_dict).
    """
    fwd: dict[str, list] = {}
    bwd: dict[str, list] = {}

    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        if not src or not tgt:
            continue
        fwd.setdefault(src, []).append((tgt, e))
        bwd.setdefault(tgt, []).append((src, e))

    return fwd, bwd


def active_edge_weight(edge: dict, weight_mode: str = "static") -> float:
    """Return the active edge weight for ranking and graph-walk retrieval."""
    if weight_mode == "calibrated":
        value = edge.get("weight_calibrated", edge.get("weight_static", edge.get("weight", 1.0)))
    else:
        value = edge.get("weight_static", edge.get("weight", 1.0))
    try:
        weight = float(value)
    except (TypeError, ValueError):
        weight = 1.0
    return max(weight, 0.0)


# ---------------------------------------------------------------------------
# BFS helpers
# ---------------------------------------------------------------------------

def bfs_neighborhood(start: str, fwd: dict, bwd: dict, hops: int) -> tuple[set[str], list[dict]]:
    """
    BFS in both directions from start, up to `hops` steps.
    Returns (visited_node_ids, traversed_edges).
    """
    visited_nodes: set[str] = {start}
    traversed_edges: list[dict] = []
    edge_keys_seen: set[tuple] = set()

    queue = deque([(start, 0)])
    visited_for_bfs = {start}

    while queue:
        node_id, depth = queue.popleft()
        if depth >= hops:
            continue

        # Outgoing
        for neighbor, edge in fwd.get(node_id, []):
            key = (edge.get("source"), edge.get("target"), edge.get("relation"))
            if key not in edge_keys_seen:
                edge_keys_seen.add(key)
                traversed_edges.append(edge)
            visited_nodes.add(neighbor)
            if neighbor not in visited_for_bfs:
                visited_for_bfs.add(neighbor)
                queue.append((neighbor, depth + 1))

        # Incoming
        for neighbor, edge in bwd.get(node_id, []):
            key = (edge.get("source"), edge.get("target"), edge.get("relation"))
            if key not in edge_keys_seen:
                edge_keys_seen.add(key)
                traversed_edges.append(edge)
            visited_nodes.add(neighbor)
            if neighbor not in visited_for_bfs:
                visited_for_bfs.add(neighbor)
                queue.append((neighbor, depth + 1))

    return visited_nodes, traversed_edges


def bfs_impact(start: str, fwd: dict, hops: int) -> tuple[set[str], list[dict]]:
    """
    Downstream BFS — only OUTGOING edges.
    Returns (visited_node_ids, traversed_edges).
    """
    visited_nodes: set[str] = {start}
    traversed_edges: list[dict] = []
    edge_keys_seen: set[tuple] = set()

    queue = deque([(start, 0)])
    visited_for_bfs = {start}

    while queue:
        node_id, depth = queue.popleft()
        if depth >= hops:
            continue

        for neighbor, edge in fwd.get(node_id, []):
            key = (edge.get("source"), edge.get("target"), edge.get("relation"))
            if key not in edge_keys_seen:
                edge_keys_seen.add(key)
                traversed_edges.append(edge)
            visited_nodes.add(neighbor)
            if neighbor not in visited_for_bfs:
                visited_for_bfs.add(neighbor)
                queue.append((neighbor, depth + 1))

    return visited_nodes, traversed_edges


def bfs_all_paths(start: str, end: str, fwd: dict, max_hops: int) -> list[list[str]]:
    """
    BFS to find all shortest paths from start to end using only outgoing edges.
    Paths are lists of node IDs. Returns empty list if no path within max_hops.
    """
    if start == end:
        return [[start]]

    # Queue: (current_node, path_so_far)
    queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
    found_paths: list[list[str]] = []
    # Track minimum path length found (only collect paths of this length)
    min_len = None
    visited_at_depth: dict[str, int] = {start: 0}

    while queue:
        node_id, path = queue.popleft()
        depth = len(path) - 1

        if min_len is not None and depth >= min_len:
            continue
        if depth >= max_hops:
            continue

        for neighbor, _edge in fwd.get(node_id, []):
            new_path = path + [neighbor]
            new_depth = len(new_path) - 1

            if neighbor == end:
                if min_len is None or new_depth <= min_len:
                    min_len = new_depth
                    found_paths.append(new_path)
                continue

            # Allow revisiting at same or shallower depth for all-paths
            prev_depth = visited_at_depth.get(neighbor)
            if prev_depth is None or new_depth <= prev_depth:
                visited_at_depth[neighbor] = new_depth
                queue.append((neighbor, new_path))

    return found_paths


def personalized_pagerank(
    nodes: list[dict],
    edges: list[dict],
    seeds: list[str],
    *,
    alpha: float = 0.15,
    weight_mode: str = "static",
    max_iter: int = 100,
    tol: float = 1e-9,
) -> dict[str, float]:
    """
    Compute weighted Personalized PageRank over outgoing graph edges.

    The implementation stays dependency-free so this skill works in bare Python
    environments. Dangling-node mass is redistributed through the seed vector.
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
        weight = active_edge_weight(edge, weight_mode)
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


# ---------------------------------------------------------------------------
# Community detection (Louvain)
# ---------------------------------------------------------------------------

def _undirected_adjacency(
    nodes: list[dict],
    edges: list[dict],
    weight_mode: str,
) -> tuple[dict[str, dict[str, float]], dict[str, float], float]:
    """
    Build symmetric weighted adjacency for community detection.

    Returns (adjacency, node_strength, total_weight). For each undirected pair
    (u, v) we sum forward and backward edge weights, so a single directed
    edge contributes its weight once and a reciprocal pair contributes the sum.
    """
    node_ids = [node["id"] for node in nodes if "id" in node]
    node_set = set(node_ids)
    adjacency: dict[str, dict[str, float]] = {node_id: {} for node_id in node_ids}

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_set or target not in node_set or source == target:
            continue
        weight = active_edge_weight(edge, weight_mode)
        if weight <= 0:
            continue
        adjacency[source][target] = adjacency[source].get(target, 0.0) + weight
        adjacency[target][source] = adjacency[target].get(source, 0.0) + weight

    node_strength = {node_id: sum(neighbours.values()) for node_id, neighbours in adjacency.items()}
    total_weight = sum(node_strength.values()) / 2.0
    return adjacency, node_strength, total_weight


def _louvain_pass(
    adjacency: dict[str, dict[str, float]],
    node_strength: dict[str, float],
    total_weight: float,
    resolution: float,
    seed: int,
) -> dict[str, str]:
    """One greedy Louvain modularity-improvement pass."""
    if total_weight <= 0:
        return {node_id: node_id for node_id in adjacency}

    community = {node_id: node_id for node_id in adjacency}
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
        for node_id in nodes_in_order:
            current_community = community[node_id]
            ki = node_strength[node_id]
            if ki <= 0:
                continue

            # Sum edge weight from this node to each neighboring community
            community_links: dict[str, float] = {}
            self_loop = 0.0
            for neighbour, weight in adjacency[node_id].items():
                if neighbour == node_id:
                    self_loop += weight
                    continue
                community_links[community[neighbour]] = (
                    community_links.get(community[neighbour], 0.0) + weight
                )

            # Remove node from current community
            community_strength[current_community] -= ki
            ki_in_current = community_links.get(current_community, 0.0)

            best_community = current_community
            best_gain = 0.0
            for candidate, ki_in_candidate in community_links.items():
                sigma_tot = community_strength.get(candidate, 0.0)
                # ΔQ for moving node to candidate community
                gain = (ki_in_candidate / total_weight) - resolution * (sigma_tot * ki) / (two_m * total_weight)
                if gain > best_gain + 1e-12:
                    best_gain = gain
                    best_community = candidate

            # Empty-community option: stay alone if no positive gain found
            if best_gain <= 0:
                best_community = current_community

            community_strength[best_community] = community_strength.get(best_community, 0.0) + ki
            if best_community != current_community:
                community[node_id] = best_community
                improved = True

    return community


class _DeterministicShuffler:
    """Tiny LCG-based shuffler so community detection stays reproducible."""

    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF or 1

    def _next(self) -> int:
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state

    def shuffle(self, items: list) -> None:
        for i in range(len(items) - 1, 0, -1):
            j = self._next() % (i + 1)
            items[i], items[j] = items[j], items[i]


def detect_communities(
    nodes: list[dict],
    edges: list[dict],
    *,
    resolution: float = 1.0,
    weight_mode: str = "static",
    seed: int = 42,
    max_levels: int = 5,
) -> dict[str, str]:
    """
    Run a Louvain-style community detection over the graph.

    Returns a mapping of node_id -> community_id.

    The algorithm runs greedy modularity passes followed by community
    aggregation, repeating until modularity stops improving (Louvain). It is
    intentionally pure-python so the skill stays dependency-free; for very
    large graphs (>50k edges), prefer a native implementation.
    """
    adjacency, node_strength, total_weight = _undirected_adjacency(nodes, edges, weight_mode)
    if total_weight <= 0:
        return {node_id: node_id for node_id in adjacency}

    # Level 0: each node is its own community
    membership = _louvain_pass(adjacency, node_strength, total_weight, resolution, seed)

    for level in range(max_levels):
        # Aggregate to super-nodes per community
        super_adjacency: dict[str, dict[str, float]] = {}
        super_strength: dict[str, float] = {}

        for node_id, neighbours in adjacency.items():
            community = membership[node_id]
            super_adjacency.setdefault(community, {})
            super_strength[community] = super_strength.get(community, 0.0)
            for neighbour, weight in neighbours.items():
                neighbour_community = membership[neighbour]
                super_adjacency[community][neighbour_community] = (
                    super_adjacency[community].get(neighbour_community, 0.0) + weight
                )
                super_strength[community] += weight

        # Strength is double-counted via symmetric adjacency
        super_strength = {community: total / 2.0 + total / 2.0 for community, total in super_strength.items()}

        super_membership = _louvain_pass(
            super_adjacency,
            super_strength,
            total_weight,
            resolution,
            seed + level + 1,
        )

        # Stop if no merges happened at this level
        if all(super_membership[community] == community for community in super_adjacency):
            break

        # Project super-community labels back down to original nodes
        membership = {
            node_id: super_membership[membership[node_id]]
            for node_id in adjacency
        }

        adjacency = super_adjacency
        node_strength = super_strength

    # Normalize community labels to community_0, community_1, ... ordered by size
    counts: dict[str, int] = {}
    for community in membership.values():
        counts[community] = counts.get(community, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    label_map = {community: f"community_{index}" for index, (community, _count) in enumerate(ordered)}

    return {node_id: label_map[community] for node_id, community in membership.items()}


def compute_modularity(
    edges: list[dict],
    membership: dict[str, str],
    *,
    weight_mode: str = "static",
) -> float:
    """Compute weighted modularity Q for a community assignment."""
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
        weight = active_edge_weight(edge, weight_mode)
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
    for node_id, community in membership.items():
        community_strength[community] = community_strength.get(community, 0.0) + strength.get(node_id, 0.0)

    modularity = 0.0
    for community, intra_weight in intra.items():
        sigma_tot = community_strength.get(community, 0.0)
        modularity += (intra_weight / two_m) - (sigma_tot / two_m) ** 2
    return modularity


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_json(result: dict) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False)


def format_mermaid(
    result: dict,
    query_label: str = "",
    *,
    direction: str = "LR",
    group_by: str = "none",
) -> str:
    nodes = sorted(
        result.get("nodes", []),
        key=lambda node: (
            str(node.get("domain", "")),
            str(node.get("type", "")),
            str(node.get("label", node.get("id", ""))),
            str(node.get("id", "")),
        ),
    )
    edges = sorted(
        result.get("edges", []),
        key=lambda edge: (
            str(edge.get("source", "")),
            str(edge.get("relation", "")),
            str(edge.get("target", "")),
        ),
    )

    lines = [f"flowchart {direction}"]
    if query_label:
        lines.append(f"  %% {_mermaid_comment(query_label)}")

    if not nodes:
        lines.append('  EMPTY["No nodes matched the query"]')
        return "\n".join(lines)

    if group_by == "none":
        for node in nodes:
            lines.append(_render_mermaid_node(node, indent="  "))
    else:
        grouped_nodes: dict[str, list[dict]] = defaultdict(list)
        group_labels: dict[str, str] = {}
        for node in nodes:
            group_key, group_label = _mermaid_group(node, group_by)
            grouped_nodes[group_key].append(node)
            group_labels[group_key] = group_label

        for group_key in sorted(grouped_nodes):
            subgraph_id = f"group_{_mermaid_safe_id(group_key)}"
            lines.append(f'  subgraph {subgraph_id}["{_mermaid_escape_label(group_labels[group_key])}"]')
            for node in grouped_nodes[group_key]:
                lines.append(_render_mermaid_node(node, indent="    "))
            lines.append("  end")

    for edge in edges:
        src = _mermaid_safe_id(edge.get("source", "?"))
        tgt = _mermaid_safe_id(edge.get("target", "?"))
        rel = _mermaid_escape_edge_label(edge.get("relation", ""))
        lines.append(f"  {src} -->|{rel}| {tgt}")

    for node_type, style in sorted(_mermaid_styles_for_nodes(nodes).items()):
        class_name = _mermaid_class_name(node_type)
        lines.append(f"  classDef {class_name} {style};")

    for node in nodes:
        lines.append(f"  class {_mermaid_safe_id(node['id'])} {_mermaid_class_name(node.get('type', 'unknown'))};")

    return "\n".join(lines)


def _mermaid_safe_id(node_id: str) -> str:
    """Replace characters that break Mermaid node IDs."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", node_id) if node_id else "UNKNOWN"


def _mermaid_class_name(node_type: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]", "_", node_type or "unknown")
    return f"type_{normalized}"


def _mermaid_escape_label(value: object) -> str:
    text = str(value or "")
    text = text.replace("\\", "\\\\").replace('"', '\\"')
    return text.replace("\n", "<br/>")


def _mermaid_escape_edge_label(value: object) -> str:
    return _mermaid_escape_label(value).replace("|", "/")


def _mermaid_comment(value: str) -> str:
    return str(value).replace("\n", " ").replace("%", "")


def _render_mermaid_node(node: dict, *, indent: str) -> str:
    node_id = _mermaid_safe_id(node["id"])
    label = node.get("label", node["id"])
    return f'{indent}{node_id}["{_mermaid_escape_label(label)}"]'


def _mermaid_group(node: dict, group_by: str) -> tuple[str, str]:
    if group_by == "type":
        node_type = node.get("type", "unknown") or "unknown"
        return node_type, f"Type: {node_type}"

    if group_by == "domain":
        domain = (
            node.get("domain")
            or node.get("properties", {}).get("domain")
            or node.get("type", "ungrouped")
            or "ungrouped"
        )
        return str(domain), f"Domain: {domain}"

    return "all", "All Nodes"


def _mermaid_styles_for_nodes(nodes: list[dict]) -> dict[str, str]:
    styles = {"unknown": "fill:#ffffff,stroke:#64748b,color:#0f172a"}
    for node in nodes:
        node_type = node.get("type", "unknown") or "unknown"
        styles[node_type] = MERMAID_TYPE_STYLES.get(node_type, styles["unknown"])
    return styles


def format_table(result: dict) -> str:
    nodes = result.get("nodes", [])
    edges = result.get("edges", [])
    communities = result.get("communities", [])

    lines = []

    if communities:
        modularity = result.get("modularity")
        if modularity is not None:
            lines.append(f"Modularity Q = {modularity}; communities = {result.get('community_count', len(communities))}")
            lines.append("")
        lines.append(f"{'COMMUNITY':<20} {'SIZE':<6} {'TOP TYPES':<35} SAMPLE LABELS")
        lines.append("-" * 110)
        for community in communities:
            type_breakdown = community.get("type_breakdown", {})
            type_summary = ", ".join(f"{t}:{c}" for t, c in list(type_breakdown.items())[:3])
            samples = ", ".join(community.get("sample_labels", [])[:4])
            lines.append(
                f"{community.get('community_id',''):<20} {community.get('size', 0):<6} "
                f"{type_summary:<35} {samples}"
            )
        return "\n".join(lines)

    if nodes:
        lines.append(f"{'ID':<50} {'TYPE':<20} LABEL")
        lines.append("-" * 90)
        for n in nodes:
            lines.append(f"{n.get('id',''):<50} {n.get('type',''):<20} {n.get('label','')}")

    if edges:
        lines.append("")
        lines.append(f"{'SOURCE':<40} {'RELATION':<25} {'TARGET':<40} GROUP")
        lines.append("-" * 115)
        for e in edges:
            lines.append(
                f"{e.get('source',''):<40} {e.get('relation',''):<25} "
                f"{e.get('target',''):<40} {e.get('group','')}"
            )

    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Query commands
# ---------------------------------------------------------------------------

def cmd_node(
    graph_path: str,
    node_id: str,
    hops: int,
    fmt: str,
    output_path: str | None,
    mermaid_direction: str,
    mermaid_group_by: str,
):
    nodes, edges, node_index = load_graph(graph_path)
    fwd, bwd = build_adjacency(edges)

    if node_id not in node_index:
        # Try case-insensitive match
        match = _fuzzy_find_node(node_id, node_index)
        if match:
            print(f"[info] Node '{node_id}' not found exactly; using '{match}'", file=sys.stderr)
            node_id = match
        else:
            print(f"Error: node '{node_id}' not found in graph", file=sys.stderr)
            sys.exit(1)

    visited_ids, subgraph_edges = bfs_neighborhood(node_id, fwd, bwd, hops)
    sub_nodes = [node_index[nid] for nid in visited_ids if nid in node_index]

    result = {
        "query": {"type": "neighborhood", "node": node_id, "hops": hops},
        "node_count": len(sub_nodes),
        "edge_count": len(subgraph_edges),
        "nodes": sub_nodes,
        "edges": subgraph_edges,
    }
    _output(
        result,
        fmt,
        query_label=f"Neighborhood of {node_id} (hops={hops})",
        output_path=output_path,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )


def cmd_paths(
    graph_path: str,
    src: str,
    tgt: str,
    max_hops: int,
    fmt: str,
    output_path: str | None,
    mermaid_direction: str,
    mermaid_group_by: str,
):
    nodes, edges, node_index = load_graph(graph_path)
    fwd, _bwd = build_adjacency(edges)

    src = _resolve_node(src, node_index)
    tgt = _resolve_node(tgt, node_index)

    paths = bfs_all_paths(src, tgt, fwd, max_hops)

    if not paths:
        result = {
            "query": {"type": "paths", "from": src, "to": tgt, "max_hops": max_hops},
            "paths_found": 0,
            "paths": [],
        }
    else:
        # Reconstruct edge details for each path
        edge_lookup: dict[tuple, dict] = {}
        for e in edges:
            edge_lookup[(e.get("source"), e.get("target"))] = e

        path_details = []
        for path in paths:
            steps = []
            for i in range(len(path) - 1):
                edge = edge_lookup.get((path[i], path[i + 1]), {
                    "source": path[i], "target": path[i + 1], "relation": "unknown"
                })
                steps.append(edge)
            path_details.append({
                "nodes": path,
                "hops": len(path) - 1,
                "edges": steps,
            })

        # For flat output format, collect unique nodes/edges across all paths
        all_node_ids: set[str] = set()
        all_edge_keys: set[tuple] = set()
        all_edges_flat: list[dict] = []
        for pd in path_details:
            all_node_ids.update(pd["nodes"])
            for e in pd["edges"]:
                key = (e.get("source"), e.get("target"), e.get("relation"))
                if key not in all_edge_keys:
                    all_edge_keys.add(key)
                    all_edges_flat.append(e)

        result = {
            "query": {"type": "paths", "from": src, "to": tgt, "max_hops": max_hops},
            "paths_found": len(paths),
            "paths": path_details,
            "nodes": [node_index[nid] for nid in all_node_ids if nid in node_index],
            "edges": all_edges_flat,
        }

    _output(
        result,
        fmt,
        query_label=f"Paths from {src} to {tgt}",
        output_path=output_path,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )


def cmd_type(
    graph_path: str,
    node_type: str,
    fmt: str,
    output_path: str | None,
    mermaid_direction: str,
    mermaid_group_by: str,
):
    nodes, edges, node_index = load_graph(graph_path)

    matched = [n for n in nodes if n.get("type") == node_type]
    result = {
        "query": {"type": "by_type", "node_type": node_type},
        "node_count": len(matched),
        "nodes": matched,
        "edges": [],
    }
    _output(
        result,
        fmt,
        query_label=f"Nodes of type '{node_type}'",
        output_path=output_path,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )


def cmd_rank(
    graph_path: str,
    top: int,
    filter_type: str,
    fmt: str,
    output_path: str | None,
    mermaid_direction: str,
    mermaid_group_by: str,
    weight_mode: str = "static",
):
    """
    Rank nodes by fan-in (number of incoming edges).
    Optionally weight by edge weight (weighted fan-in = sum of incoming edge weights).
    Higher fan-in = more critical / more widely depended-on.
    """
    nodes, edges, node_index = load_graph(graph_path)

    # Count and weight incoming edges per node
    fan_in_count: dict[str, int] = {}
    fan_in_weight: dict[str, float] = {}
    for e in edges:
        tgt = e.get("target")
        if not tgt:
            continue
        fan_in_count[tgt] = fan_in_count.get(tgt, 0) + 1
        fan_in_weight[tgt] = fan_in_weight.get(tgt, 0.0) + active_edge_weight(e, weight_mode)

    # Build ranked list
    ranked = []
    for n in nodes:
        nid = n.get("id")
        if not nid:
            continue
        if filter_type and n.get("type") != filter_type:
            continue
        ranked.append({
            "id": nid,
            "type": n.get("type", "?"),
            "label": n.get("label", nid),
            "fan_in": fan_in_count.get(nid, 0),
            "weighted_fan_in": round(fan_in_weight.get(nid, 0.0), 2),
            "summary": n.get("summary"),
            "tags": n.get("tags"),
        })

    # Sort by weighted fan-in descending, then count descending
    ranked.sort(key=lambda x: (-x["weighted_fan_in"], -x["fan_in"]))
    if top > 0:
        ranked = ranked[:top]

    result = {
        "query": {"type": "rank", "filter_type": filter_type or "all", "top": top, "weights": weight_mode},
        "node_count": len(ranked),
        "nodes": ranked,
        "edges": [],
    }
    _output(
        result,
        fmt,
        query_label=f"Top {top} nodes by fan-in" if top else "All nodes by fan-in",
        output_path=output_path,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )


def cmd_ppr(
    graph_path: str,
    seeds: list[str],
    alpha: float,
    top: int,
    filter_type: str,
    include_seeds: bool,
    weight_mode: str,
    fmt: str,
    output_path: str | None,
    mermaid_direction: str,
    mermaid_group_by: str,
):
    nodes, edges, node_index = load_graph(graph_path)
    resolved_seeds = [_resolve_node(seed, node_index) for seed in seeds]
    scores = personalized_pagerank(nodes, edges, resolved_seeds, alpha=alpha, weight_mode=weight_mode)
    allowed_types = _parse_csv_set(filter_type)
    seed_set = set(resolved_seeds)

    ranked = []
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            continue
        if not include_seeds and node_id in seed_set:
            continue
        if allowed_types and node.get("type") not in allowed_types:
            continue
        ranked.append(
            {
                "id": node_id,
                "type": node.get("type"),
                "label": node.get("label", node_id),
                "ppr_score": round(scores.get(node_id, 0.0), 10),
                "summary": node.get("summary"),
                "tags": node.get("tags"),
            }
        )

    ranked.sort(key=lambda item: (-item["ppr_score"], item["type"] or "", item["label"] or "", item["id"]))
    if top > 0:
        ranked = ranked[:top]

    selected_ids = {node["id"] for node in ranked} | seed_set
    selected_edges = [
        edge
        for edge in edges
        if edge.get("source") in selected_ids and edge.get("target") in selected_ids
    ]

    result = {
        "query": {
            "type": "ppr",
            "seeds": resolved_seeds,
            "alpha": alpha,
            "top": top,
            "filter_type": sorted(allowed_types) if allowed_types else "all",
            "include_seeds": include_seeds,
            "weights": weight_mode,
        },
        "node_count": len(ranked),
        "edge_count": len(selected_edges),
        "nodes": ranked,
        "edges": selected_edges,
    }
    _output(
        result,
        fmt,
        query_label=f"PPR from {', '.join(resolved_seeds)}",
        output_path=output_path,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )


def cmd_communities(
    graph_path: str,
    resolution: float,
    weight_mode: str,
    seed: int,
    top: int,
    fmt: str,
    output_path: str | None,
    mermaid_direction: str,
    mermaid_group_by: str,
) -> None:
    nodes, edges, _index = load_graph(graph_path)

    membership = detect_communities(
        nodes,
        edges,
        resolution=resolution,
        weight_mode=weight_mode,
        seed=seed,
    )
    modularity = compute_modularity(edges, membership, weight_mode=weight_mode)

    grouped: dict[str, list[dict]] = {}
    for node in nodes:
        nid = node.get("id")
        if not nid or nid not in membership:
            continue
        community = membership[nid]
        grouped.setdefault(community, []).append(node)

    summaries = []
    for community, members in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        types: dict[str, int] = {}
        domains: dict[str, int] = {}
        sample_labels = []
        for node in members:
            type_key = node.get("type", "?")
            types[type_key] = types.get(type_key, 0) + 1
            domain_key = node.get("domain") or "?"
            domains[domain_key] = domains.get(domain_key, 0) + 1
            if len(sample_labels) < 5:
                sample_labels.append(node.get("label") or node.get("id"))
        summaries.append({
            "community_id": community,
            "size": len(members),
            "type_breakdown": dict(sorted(types.items(), key=lambda item: -item[1])),
            "domain_breakdown": dict(sorted(domains.items(), key=lambda item: -item[1])),
            "sample_labels": sample_labels,
            "member_ids": [m.get("id") for m in members],
        })

    if top > 0:
        summaries = summaries[:top]

    result = {
        "query": {
            "type": "communities",
            "resolution": resolution,
            "weights": weight_mode,
            "seed": seed,
            "top": top,
        },
        "modularity": round(modularity, 6),
        "community_count": len(grouped),
        "communities": summaries,
        "nodes": [],
        "edges": [],
    }
    _output(
        result,
        fmt,
        query_label=f"Communities (γ={resolution})",
        output_path=output_path,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )


def cmd_impact(
    graph_path: str,
    node_id: str,
    hops: int,
    fmt: str,
    output_path: str | None,
    mermaid_direction: str,
    mermaid_group_by: str,
):
    nodes, edges, node_index = load_graph(graph_path)
    fwd, _bwd = build_adjacency(edges)

    node_id = _resolve_node(node_id, node_index)

    visited_ids, subgraph_edges = bfs_impact(node_id, fwd, hops)
    sub_nodes = [node_index[nid] for nid in visited_ids if nid in node_index]

    result = {
        "query": {"type": "impact", "node": node_id, "hops": hops},
        "node_count": len(sub_nodes),
        "edge_count": len(subgraph_edges),
        "nodes": sub_nodes,
        "edges": subgraph_edges,
    }
    _output(
        result,
        fmt,
        query_label=f"Impact of {node_id} (downstream, hops={hops})",
        output_path=output_path,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )


def _flatten_for_search(node: dict) -> str:
    parts = [
        node.get("id", ""),
        node.get("label", ""),
        node.get("summary", ""),
        " ".join(node.get("tags", []) or []),
        node.get("domain", ""),
        node.get("notes", ""),
    ]
    props = node.get("properties")
    if isinstance(props, dict):
        for value in props.values():
            if isinstance(value, list):
                parts.append(" ".join(str(item) for item in value))
            else:
                parts.append(str(value))
    return " ".join(part for part in parts if part).lower()


def _score_node(query: str, node: dict) -> float:
    query = query.strip().lower()
    if not query:
        return 0.0

    haystack = _flatten_for_search(node)
    label = node.get("label", "").lower()
    node_id = node.get("id", "").lower()
    tags = [tag.lower() for tag in node.get("tags", []) or []]
    tokens = [token for token in re.split(r"\s+", query) if token]

    score = 0.0
    if node_id == query:
        score += 12.0
    if label == query:
        score += 10.0
    if query in label:
        score += 6.0
    if query in node_id:
        score += 5.0
    if query in haystack:
        score += 3.0

    for token in tokens:
        if token in label:
            score += 2.0
        if token in node_id:
            score += 1.5
        if any(token == tag or token in tag for tag in tags):
            score += 1.5
        if token in haystack:
            score += 0.75

    return score


def cmd_search(
    graph_path: str,
    query: str,
    types: str,
    limit: int,
    fmt: str,
    output_path: str | None,
    mermaid_direction: str,
    mermaid_group_by: str,
):
    nodes, _edges, _node_index = load_graph(graph_path)

    allowed_types = {item.strip() for item in types.split(",") if item.strip()} if types else set()
    ranked = []
    for node in nodes:
        if allowed_types and node.get("type") not in allowed_types:
            continue
        score = _score_node(query, node)
        if score <= 0:
            continue
        ranked.append(
            {
                "score": round(score, 2),
                **node,
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item.get("label", ""), item.get("id", "")))
    if limit > 0:
        ranked = ranked[:limit]

    result = {
        "query": {
            "type": "search",
            "query": query,
            "types": sorted(allowed_types) if allowed_types else "all",
            "limit": limit,
        },
        "node_count": len(ranked),
        "nodes": ranked,
        "edges": [],
    }
    _output(
        result,
        fmt,
        query_label=f"Search '{query}'",
        output_path=output_path,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )


def cmd_diagram(
    graph_path: str,
    include_types: str,
    exclude_types: str,
    include_relations: str,
    exclude_relations: str,
    diagram_limit: int,
    fmt: str,
    output_path: str | None,
    mermaid_direction: str,
    mermaid_group_by: str,
):
    nodes, edges, _node_index = load_graph(graph_path)

    result = build_diagram_result(
        nodes,
        edges,
        include_types=include_types,
        exclude_types=exclude_types,
        include_relations=include_relations,
        exclude_relations=exclude_relations,
        diagram_limit=diagram_limit,
    )
    _output(
        result,
        fmt,
        query_label="Filtered diagram export",
        output_path=output_path,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )


def build_diagram_result(
    nodes: list[dict],
    edges: list[dict],
    *,
    include_types: str = "",
    exclude_types: str = "",
    include_relations: str = "",
    exclude_relations: str = "",
    diagram_limit: int = 200,
) -> dict:
    """Build a filtered diagram result without writing output."""

    include_type_set = _parse_csv_set(include_types)
    exclude_type_set = _parse_csv_set(exclude_types)
    include_relation_set = _parse_csv_set(include_relations)
    exclude_relation_set = _parse_csv_set(exclude_relations)

    selected_nodes = []
    selected_ids: set[str] = set()
    for node in nodes:
        node_type = node.get("type", "")
        if include_type_set and node_type not in include_type_set:
            continue
        if exclude_type_set and node_type in exclude_type_set:
            continue
        node_id = node.get("id")
        if not node_id:
            continue
        selected_nodes.append(node)
        selected_ids.add(node_id)

    selected_edges = []
    connected_ids: set[str] = set()
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        relation = edge.get("relation", "")
        if not source or not target:
            continue
        if source not in selected_ids or target not in selected_ids:
            continue
        if include_relation_set and relation not in include_relation_set:
            continue
        if exclude_relation_set and relation in exclude_relation_set:
            continue
        selected_edges.append(edge)
        connected_ids.add(source)
        connected_ids.add(target)

    if connected_ids and (include_relation_set or exclude_relation_set):
        selected_nodes = [node for node in selected_nodes if node.get("id") in connected_ids]

    if diagram_limit > 0 and len(selected_nodes) > diagram_limit:
        print(
            (
                f"Error: diagram selection has {len(selected_nodes)} nodes, which exceeds "
                f"--diagram-limit={diagram_limit}. Narrow the filters or set --diagram-limit 0."
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    return {
        "query": {
            "type": "diagram",
            "include_types": sorted(include_type_set) if include_type_set else "all",
            "exclude_types": sorted(exclude_type_set),
            "include_relations": sorted(include_relation_set) if include_relation_set else "all",
            "exclude_relations": sorted(exclude_relation_set),
            "diagram_limit": diagram_limit,
        },
        "node_count": len(selected_nodes),
        "edge_count": len(selected_edges),
        "nodes": selected_nodes,
        "edges": selected_edges,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_csv_set(raw: str) -> set[str]:
    if not raw:
        return set()
    return {item.strip() for item in raw.split(",") if item.strip()}

def _resolve_node(node_id: str, node_index: dict[str, dict]) -> str:
    if node_id in node_index:
        return node_id
    match = _fuzzy_find_node(node_id, node_index)
    if match:
        print(f"[info] Node '{node_id}' not found exactly; using '{match}'", file=sys.stderr)
        return match
    print(f"Error: node '{node_id}' not found in graph", file=sys.stderr)
    sys.exit(1)


def _fuzzy_find_node(node_id: str, node_index: dict[str, dict]) -> str:
    """Case-insensitive ID lookup."""
    lower = node_id.lower()
    for nid in node_index:
        if nid.lower() == lower:
            return nid
    return ""


def render_output(
    result: dict,
    fmt: str,
    *,
    query_label: str = "",
    mermaid_direction: str = "LR",
    mermaid_group_by: str = "none",
) -> str:
    if fmt == "json":
        return format_json(result)
    if fmt == "mermaid":
        return format_mermaid(
            result,
            query_label,
            direction=mermaid_direction,
            group_by=mermaid_group_by,
        )
    if fmt == "table":
        return format_table(result)
    return format_json(result)


def _output(
    result: dict,
    fmt: str,
    *,
    query_label: str = "",
    output_path: str | None = None,
    mermaid_direction: str = "LR",
    mermaid_group_by: str = "none",
):
    rendered = render_output(
        result,
        fmt,
        query_label=query_label,
        mermaid_direction=mermaid_direction,
        mermaid_group_by=mermaid_group_by,
    )
    if output_path:
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + ("\n" if not rendered.endswith("\n") else ""), encoding="utf-8")
        print(f"[ok] Wrote {fmt} output to {path}", file=sys.stderr)
        return
    print(rendered)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Query a knowledge graph JSON file."
    )
    parser.add_argument("graph", help="Path to knowledge-graph.json")

    # Commands (mutually exclusive)
    cmd_group = parser.add_mutually_exclusive_group(required=True)
    cmd_group.add_argument("--node", metavar="ID",
                           help="BFS neighborhood around a node (both directions)")
    cmd_group.add_argument("--from", dest="path_from", metavar="ID",
                           help="Source node for path-finding (use with --to)")
    cmd_group.add_argument("--type", metavar="NODE_TYPE",
                           help="List all nodes of a given type")
    cmd_group.add_argument("--impact", metavar="ID",
                           help="Downstream impact analysis (outgoing only)")
    cmd_group.add_argument("--rank", action="store_true",
                           help="Rank all nodes by fan-in (most-depended-on first)")
    cmd_group.add_argument("--ppr", action="store_true",
                           help="Personalized PageRank retrieval from one or more --seed nodes")
    cmd_group.add_argument("--communities", action="store_true",
                           help="Detect communities (Louvain). Use --resolution to control granularity")
    cmd_group.add_argument("--search", metavar="QUERY",
                           help="Lexical search across node ids, labels, summaries, tags, and properties")
    cmd_group.add_argument("--diagram", action="store_true",
                           help="Create a filtered diagram export from the whole graph")

    # Options
    parser.add_argument("--to", metavar="ID",
                        help="Target node for path-finding")
    parser.add_argument("--hops", type=int, default=1, metavar="N",
                        help="BFS hop depth for --node and --impact (default: 1)")
    parser.add_argument("--max-hops", type=int, default=3, metavar="N",
                        help="Maximum hops for path-finding (default: 3)")
    parser.add_argument("--top", type=int, default=20, metavar="N",
                        help="Number of top nodes for --rank or --ppr (default: 20; 0 = all)")
    parser.add_argument("--filter-type", dest="filter_type", metavar="TYPE",
                        help="Filter --rank to a specific node type, or --ppr to comma-separated node types")
    parser.add_argument("--seed", action="append", default=[],
                        help="Seed node for --ppr. May be passed multiple times")
    parser.add_argument("--alpha", type=float, default=0.15,
                        help="Teleport probability for --ppr (default: 0.15)")
    parser.add_argument("--weights", choices=["static", "calibrated"], default="static",
                        help="Edge weights for --rank and --ppr (default: static)")
    parser.add_argument("--include-seeds", action="store_true",
                        help="Include seed nodes in --ppr results")
    parser.add_argument("--resolution", type=float, default=1.0,
                        help="Resolution γ for --communities (default: 1.0; <1 = fewer/larger, >1 = more/smaller)")
    parser.add_argument("--community-seed", type=int, default=42,
                        help="RNG seed for --communities reproducibility (default: 42)")
    parser.add_argument("--types", metavar="TYPE1,TYPE2",
                        help="Comma-separated node types to include for --search")
    parser.add_argument("--limit", type=int, default=20, metavar="N",
                        help="Result limit for --search (default: 20; 0 = all)")
    parser.add_argument("--include-types", metavar="TYPE1,TYPE2",
                        help="Comma-separated node types to include for --diagram")
    parser.add_argument("--exclude-types", metavar="TYPE1,TYPE2",
                        help="Comma-separated node types to exclude from --diagram")
    parser.add_argument("--include-relations", metavar="REL1,REL2",
                        help="Comma-separated relations to include for --diagram")
    parser.add_argument("--exclude-relations", metavar="REL1,REL2",
                        help="Comma-separated relations to exclude from --diagram")
    parser.add_argument("--diagram-limit", type=int, default=200, metavar="N",
                        help="Maximum nodes allowed for --diagram output (default: 200; 0 = all)")
    parser.add_argument("--format", dest="fmt",
                        choices=["json", "mermaid", "table"], default=None,
                        help="Output format (default: json; --diagram defaults to mermaid)")
    parser.add_argument("--output", metavar="FILE",
                        help="Optional path to write the rendered output instead of stdout")
    parser.add_argument("--mermaid-direction", choices=MERMAID_DIRECTIONS, default="LR",
                        help="Flow direction for Mermaid output (default: LR)")
    parser.add_argument("--mermaid-group-by", choices=MERMAID_GROUP_BY, default="none",
                        help="Group Mermaid nodes by domain or type (default: none)")
    parser.add_argument("--as-of", dest="as_of", metavar="ISO_DATE",
                        help="Bitemporal event-time slice. Filter edges to those that were true in the world at this date")
    parser.add_argument("--known-at", dest="known_at", metavar="ISO_DATE",
                        help="Bitemporal transaction-time slice. Filter edges to those the system believed at this date")

    args = parser.parse_args()
    fmt = args.fmt or ("mermaid" if args.diagram else "json")

    as_of = _parse_iso(args.as_of) if args.as_of else None
    known_at = _parse_iso(args.known_at) if args.known_at else None
    if args.as_of and as_of is None:
        parser.error(f"--as-of: could not parse '{args.as_of}' as ISO date")
    if args.known_at and known_at is None:
        parser.error(f"--known-at: could not parse '{args.known_at}' as ISO date")
    set_temporal_window(as_of=as_of, known_at=known_at)

    if args.node:
        cmd_node(args.graph, args.node, args.hops, fmt, args.output, args.mermaid_direction, args.mermaid_group_by)

    elif args.path_from:
        if not args.to:
            parser.error("--from requires --to")
        cmd_paths(
            args.graph,
            args.path_from,
            args.to,
            args.max_hops,
            fmt,
            args.output,
            args.mermaid_direction,
            args.mermaid_group_by,
        )

    elif args.type:
        cmd_type(args.graph, args.type, fmt, args.output, args.mermaid_direction, args.mermaid_group_by)

    elif args.impact:
        cmd_impact(args.graph, args.impact, args.hops, fmt, args.output, args.mermaid_direction, args.mermaid_group_by)

    elif args.rank:
        cmd_rank(
            args.graph,
            args.top,
            args.filter_type or "",
            fmt,
            args.output,
            args.mermaid_direction,
            args.mermaid_group_by,
            args.weights,
        )

    elif args.ppr:
        if not args.seed:
            parser.error("--ppr requires at least one --seed")
        if not 0 < args.alpha < 1:
            parser.error("--alpha must be greater than 0 and less than 1")
        cmd_ppr(
            args.graph,
            args.seed,
            args.alpha,
            args.top,
            args.filter_type or "",
            args.include_seeds,
            args.weights,
            fmt,
            args.output,
            args.mermaid_direction,
            args.mermaid_group_by,
        )

    elif args.communities:
        if args.resolution <= 0:
            parser.error("--resolution must be positive")
        cmd_communities(
            args.graph,
            args.resolution,
            args.weights,
            args.community_seed,
            args.top,
            fmt,
            args.output,
            args.mermaid_direction,
            args.mermaid_group_by,
        )

    elif args.search:
        cmd_search(
            args.graph,
            args.search,
            args.types or "",
            args.limit,
            fmt,
            args.output,
            args.mermaid_direction,
            args.mermaid_group_by,
        )

    elif args.diagram:
        cmd_diagram(
            args.graph,
            args.include_types or "",
            args.exclude_types or "",
            args.include_relations or "",
            args.exclude_relations or "",
            args.diagram_limit,
            fmt,
            args.output,
            args.mermaid_direction,
            args.mermaid_group_by,
        )


if __name__ == "__main__":
    main()
