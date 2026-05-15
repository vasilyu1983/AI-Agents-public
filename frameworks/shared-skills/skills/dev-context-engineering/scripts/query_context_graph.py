#!/usr/bin/env python3
"""
Query a context-graph.json file.

Supports:
  --node <id> [--hops N]      BFS neighborhood
  --impact <id> [--hops N]    Downstream impact (outgoing only)
  --rank [--top N]            Rank by weighted incoming edges
  --ppr --seed <id>           Personalized PageRank around 1+ seeds
  --tier-budget               Show how token cost is distributed across loading tiers

Examples:
  python3 query_context_graph.py context-graph.json --node "agents_md:AGENTS.md" --hops 2
  python3 query_context_graph.py context-graph.json --ppr --seed "rule:.claude/rules/coding-behavior.md" --top 20
  python3 query_context_graph.py context-graph.json --tier-budget --format table
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path


def load_graph(graph_path: str) -> tuple[list[dict], list[dict], dict[str, dict]]:
    data = json.loads(Path(graph_path).read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    return nodes, edges, {node["id"]: node for node in nodes if "id" in node}


def edge_weight(edge: dict) -> float:
    """Pick the most informative weight available, preferring calibrated values."""
    for field in ("weight_calibrated", "weight_static", "weight"):
        value = edge.get(field)
        if value is not None:
            try:
                return max(float(value), 0.0)
            except (TypeError, ValueError):
                continue
    return 1.0


def build_adjacency(edges: list[dict]) -> tuple[dict, dict]:
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
    visited = {start}
    edge_keys: set[tuple[str, str, str]] = set()
    collected_edges: list[dict] = []
    queue = deque([(start, 0)])
    while queue:
        node_id, depth = queue.popleft()
        if depth >= hops:
            continue
        for neighbor, edge in forward.get(node_id, []):
            key = (edge["source"], edge["target"], edge.get("relation", ""))
            if key not in edge_keys:
                edge_keys.add(key)
                collected_edges.append(edge)
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))
        for neighbor, edge in backward.get(node_id, []):
            key = (edge["source"], edge["target"], edge.get("relation", ""))
            if key not in edge_keys:
                edge_keys.add(key)
                collected_edges.append(edge)
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))
    return visited, collected_edges


def bfs_impact(start: str, forward: dict, hops: int) -> tuple[set[str], list[dict]]:
    visited = {start}
    edge_keys: set[tuple[str, str, str]] = set()
    collected_edges: list[dict] = []
    queue = deque([(start, 0)])
    while queue:
        node_id, depth = queue.popleft()
        if depth >= hops:
            continue
        for neighbor, edge in forward.get(node_id, []):
            key = (edge["source"], edge["target"], edge.get("relation", ""))
            if key not in edge_keys:
                edge_keys.add(key)
                collected_edges.append(edge)
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))
    return visited, collected_edges


def personalized_pagerank(
    nodes: list[dict],
    edges: list[dict],
    seeds: list[str],
    *,
    alpha: float = 0.15,
    max_iter: int = 100,
    tol: float = 1e-9,
) -> dict[str, float]:
    """Weighted PPR for context-graph retrieval. Pure-python."""
    node_ids = [node["id"] for node in nodes if "id" in node]
    node_set = set(node_ids)
    if not node_ids:
        return {}

    seed_set = [seed for seed in seeds if seed in node_set]
    if not seed_set:
        raise ValueError("at least one seed must exist in the graph")

    personalization = {nid: 0.0 for nid in node_ids}
    for seed in seed_set:
        personalization[seed] = 1.0 / len(seed_set)

    outgoing: dict[str, list[tuple[str, float]]] = {nid: [] for nid in node_ids}
    for edge in edges:
        src = edge.get("source")
        tgt = edge.get("target")
        if src not in node_set or tgt not in node_set:
            continue
        weight = edge_weight(edge)
        if weight <= 0:
            continue
        outgoing[src].append((tgt, weight))

    scores = dict(personalization)
    for _ in range(max_iter):
        next_scores = {nid: alpha * personalization[nid] for nid in node_ids}
        dangling = 0.0
        for nid, score in scores.items():
            targets = outgoing.get(nid, [])
            if not targets:
                dangling += score
                continue
            total = sum(weight for _t, weight in targets)
            if total <= 0:
                dangling += score
                continue
            walk = (1.0 - alpha) * score
            for tgt, weight in targets:
                next_scores[tgt] += walk * (weight / total)
        if dangling:
            redistribution = (1.0 - alpha) * dangling
            for nid, seed_score in personalization.items():
                if seed_score:
                    next_scores[nid] += redistribution * seed_score
        delta = sum(abs(next_scores[nid] - scores.get(nid, 0.0)) for nid in node_ids)
        scores = next_scores
        if delta < tol:
            break

    total = sum(scores.values())
    if total > 0:
        scores = {nid: value / total for nid, value in scores.items()}
    return scores


def rank_nodes(nodes: list[dict], edges: list[dict], top: int) -> list[dict]:
    fan_in: dict[str, float] = {}
    for edge in edges:
        target = edge.get("target")
        if not target:
            continue
        fan_in[target] = fan_in.get(target, 0.0) + edge_weight(edge)
    ranked = []
    for node in nodes:
        nid = node.get("id")
        if not nid:
            continue
        ranked.append({
            "id": nid,
            "type": node.get("type"),
            "label": node.get("label"),
            "loading_tier": node.get("loading_tier"),
            "weighted_fan_in": round(fan_in.get(nid, 0.0), 4),
        })
    ranked.sort(key=lambda item: (-item["weighted_fan_in"], item.get("label") or item["id"]))
    return ranked if top == 0 else ranked[:top]


def tier_budget(nodes: list[dict]) -> dict:
    by_tier: dict[str, dict] = {}
    for node in nodes:
        tier = node.get("loading_tier") or "untiered"
        bucket = by_tier.setdefault(tier, {"node_count": 0, "token_cost_total": 0, "stale_count": 0})
        bucket["node_count"] += 1
        bucket["token_cost_total"] += int(node.get("token_cost") or 0)
        if node.get("stale"):
            bucket["stale_count"] += 1
    return by_tier


def format_table(payload: dict) -> str:
    if "tier_budget" in payload:
        budget = payload["tier_budget"]
        lines = [f"{'TIER':<20} {'NODES':<8} {'TOKENS':<10} STALE"]
        lines.append("-" * 50)
        for tier, bucket in sorted(budget.items()):
            lines.append(
                f"{tier:<20} {bucket['node_count']:<8} {bucket['token_cost_total']:<10} {bucket['stale_count']}"
            )
        return "\n".join(lines)

    rows = payload.get("results") or payload.get("nodes") or []
    if not rows:
        return "No results."
    headers = ["id", "type", "label", "loading_tier"]
    if "ppr_score" in rows[0]:
        headers.append("ppr_score")
    if "weighted_fan_in" in rows[0]:
        headers.append("weighted_fan_in")
    lines = [" | ".join(headers), " | ".join("---" for _ in headers)]
    for row in rows:
        lines.append(" | ".join(str(row.get(header, "")) for header in headers))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", help="Path to context-graph.json")
    cmd = parser.add_mutually_exclusive_group(required=True)
    cmd.add_argument("--node", help="BFS neighborhood around a node")
    cmd.add_argument("--impact", help="Downstream impact from a node")
    cmd.add_argument("--rank", action="store_true", help="Rank nodes by weighted fan-in")
    cmd.add_argument("--ppr", action="store_true", help="Personalized PageRank (use --seed)")
    cmd.add_argument("--tier-budget", action="store_true", dest="tier_budget", help="Show node and token distribution per loading tier")

    parser.add_argument("--seed", action="append", default=[], help="Seed node id for --ppr (repeatable)")
    parser.add_argument("--alpha", type=float, default=0.15, help="Teleport probability for --ppr (default: 0.15)")
    parser.add_argument("--include-seeds", action="store_true", help="Include seed nodes in --ppr results")
    parser.add_argument("--filter-type", help="Comma-separated node types to keep in --ppr results")
    parser.add_argument("--top", type=int, default=20, help="Top results for --rank or --ppr (0 = all)")
    parser.add_argument("--hops", type=int, default=1, help="Hops for --node and --impact (default: 1)")
    parser.add_argument("--format", choices=("json", "table"), default="json")
    parser.add_argument("--output", help="Optional output file")
    args = parser.parse_args()

    nodes, edges, node_index = load_graph(args.graph)
    forward, backward = build_adjacency(edges)

    result: dict
    if args.node:
        if args.node not in node_index:
            print(f"Error: node '{args.node}' not in graph", file=sys.stderr)
            return 1
        ids, edge_rows = bfs_neighborhood(args.node, forward, backward, args.hops)
        result = {
            "query": "node",
            "node": args.node,
            "hops": args.hops,
            "nodes": [node_index[i] for i in sorted(ids) if i in node_index],
            "edges": edge_rows,
        }
    elif args.impact:
        if args.impact not in node_index:
            print(f"Error: node '{args.impact}' not in graph", file=sys.stderr)
            return 1
        ids, edge_rows = bfs_impact(args.impact, forward, args.hops)
        result = {
            "query": "impact",
            "node": args.impact,
            "hops": args.hops,
            "nodes": [node_index[i] for i in sorted(ids) if i in node_index],
            "edges": edge_rows,
        }
    elif args.rank:
        result = {"query": "rank", "results": rank_nodes(nodes, edges, args.top)}
    elif args.ppr:
        if not args.seed:
            print("Error: --ppr requires at least one --seed", file=sys.stderr)
            return 1
        if not 0 < args.alpha < 1:
            print("Error: --alpha must be between 0 and 1", file=sys.stderr)
            return 1
        unknown = [seed for seed in args.seed if seed not in node_index]
        if unknown:
            print(f"Error: unknown seed(s): {', '.join(unknown)}", file=sys.stderr)
            return 1
        scores = personalized_pagerank(nodes, edges, args.seed, alpha=args.alpha)
        seed_set = set(args.seed)
        allowed_types = {value.strip() for value in args.filter_type.split(",")} if args.filter_type else None
        ranked = []
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
                "loading_tier": node.get("loading_tier"),
                "ppr_score": round(scores.get(nid, 0.0), 10),
            })
        ranked.sort(key=lambda item: (-item["ppr_score"], item.get("label") or item["id"]))
        if args.top > 0:
            ranked = ranked[:args.top]
        result = {
            "query": "ppr",
            "seeds": args.seed,
            "alpha": args.alpha,
            "results": ranked,
        }
    elif args.tier_budget:
        result = {"query": "tier_budget", "tier_budget": tier_budget(nodes)}
    else:
        print("Error: choose exactly one query mode", file=sys.stderr)
        return 1

    if args.format == "table":
        rendered = format_table(result)
    else:
        rendered = json.dumps(result, indent=2, default=str)

    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
