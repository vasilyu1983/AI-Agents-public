#!/usr/bin/env python3
"""
Build a knowledge graph JSON from either:
  --profiles <dir>  : a directory of repo-profile JSON files
  --hub <dir>       : a requirements-hub directory

Usage:
  python3 build_knowledge_graph.py --hub /path/to/hub [--output /path/to/output.json]
  python3 build_knowledge_graph.py --profiles /path/to/profiles/ [--output ...]
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

CANONICAL_ENGINE = {
    "sql server": "sqlserver",
    "sqlserver": "sqlserver",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "pg": "postgresql",
    "elasticsearch": "elasticsearch",
    "es": "elasticsearch",
    "kafka": "kafka",
    "rabbitmq": "rabbitmq",
    "redis": "redis",
    "dynamodb": "dynamodb",
    "s3": "s3",
}

GRAPH_CONTRACT_VERSION = "1.1"

# Edge weight convention (from Understand-Anything, adapted for service-level graphs)
EDGE_WEIGHTS = {
    "contains":          1.0,
    "exposes":           0.9,
    "owns_data_in":      0.9,
    "calls":             0.8,
    "publishes_to":      0.8,
    "subscribes_to":     0.8,
    "uses_provider":     0.8,
    "implements_process": 0.8,
    "imports":           0.7,
    "depends_on":        0.6,
    "shares_library_with": 0.5,
    "deploys_with":      0.5,
    "reads_from":        0.7,
    "writes_to":         0.7,
    "replaces":          0.4,
    "extends":           0.6,
    "documents":         0.4,
    "governed_by":       0.4,
    "related_to":        0.3,
    "similar_to":        0.3,
    "contradicts":       0.3,
    "co_occurs":         0.3,
}


def normalize_id(label: str) -> str:
    """Lowercase, strip, replace non-safe chars with hyphens."""
    result = re.sub(r"[^a-z0-9._-]", "-", label.lower().strip())
    return result.strip("-")


def normalize_engine(raw: str) -> str:
    key = raw.lower().strip()
    return CANONICAL_ENGINE.get(key, normalize_id(raw))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def strip_br(text: str) -> str:
    """Remove HTML <br/> and <br> tags, replacing with space."""
    return re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE).strip()


def normalize_profile_entity_type(raw: str) -> str:
    if not raw:
        return "entity"
    lowered = raw.strip().lower()
    if lowered == "nuget_package":
        return "package"
    return lowered


def parse_last_verified(content: str) -> str | None:
    match = re.search(r"<!--\s*last_verified:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*-->", content)
    if not match:
        return None
    return match.group(1)


def artifact_node_id(relative_path: str) -> str:
    return f"artifact-{normalize_id(relative_path)}"


def parse_int_maybe(raw: str) -> int | None:
    if not raw:
        return None
    cleaned = raw.replace(",", "")
    match = re.search(r"([0-9]+)", cleaned)
    if not match:
        return None
    return int(match.group(1))


def typed_node_id(g: "GraphBuilder", label: str, node_type: str) -> str:
    """
    Reserve a stable ID for a label within a node type.

    Different ontology types can legitimately share the same normalized token,
    for example a repo named `notifications` and a domain named `Notifications`.
    In that case keep the original ID for the first type and scope later types.
    """
    base_id = normalize_id(label)
    existing = g._nodes.get(base_id)
    if existing is None or existing.get("type") == node_type:
        return base_id
    return f"{node_type}-{base_id}"


# ---------------------------------------------------------------------------
# Node / Edge registry with deduplication
# ---------------------------------------------------------------------------

class GraphBuilder:
    def __init__(self):
        self._nodes: dict[str, dict] = {}   # id -> node dict
        self._edge_keys: set[tuple] = set()  # (source, target, relation) dedup
        self._edges: list[dict] = []

    # -- nodes --

    def add_node(self, node_id: str, node_type: str, label: str, **kwargs) -> str:
        """Add or merge a node. Returns the canonical id."""
        if node_id not in self._nodes:
            n = {"id": node_id, "type": node_type, "label": label}
            for k, v in kwargs.items():
                if v is not None:
                    n[k] = v
            self._nodes[node_id] = n
        else:
            # Merge: update empty fields, combine evidence
            existing = self._nodes[node_id]
            for k, v in kwargs.items():
                if v is None:
                    continue
                if k == "evidence":
                    existing.setdefault("evidence", [])
                    existing["evidence"].extend(v)
                elif k == "tags":
                    existing.setdefault("tags", [])
                    existing["tags"] = sorted(set(existing["tags"]) | set(v))
                elif k == "properties":
                    existing.setdefault("properties", {})
                    for prop_key, prop_value in v.items():
                        existing["properties"].setdefault(prop_key, prop_value)
                elif k not in existing:
                    existing[k] = v
        return node_id

    def add_edge(self, source: str, target: str, relation: str, group: str, **kwargs):
        key = (source, target, relation)
        if key in self._edge_keys:
            return
        self._edge_keys.add(key)
        e = {"source": source, "target": target, "relation": relation, "group": group}
        # Auto-set weight from convention if not explicitly provided
        if "weight" not in kwargs:
            e["weight"] = EDGE_WEIGHTS.get(relation, 0.5)
        for k, v in kwargs.items():
            if v is not None:
                e[k] = v
        self._edges.append(e)

    def to_dict(self, portfolio_name: str, build_source: str, portfolio_metrics: dict | None = None) -> dict:
        nodes = list(self._nodes.values())
        edges = self._edges
        return {
            "meta": {
                "portfolio_name": portfolio_name,
                "generated_at": now_iso(),
                "version": "1.0",
                "graph_contract_version": GRAPH_CONTRACT_VERSION,
                "build_source": build_source,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "portfolio_metrics": portfolio_metrics or {},
            },
            "nodes": nodes,
            "edges": edges,
        }


# ---------------------------------------------------------------------------
# Mode A: --profiles
# ---------------------------------------------------------------------------

def build_from_profiles(profiles_dir: Path, g: GraphBuilder):
    json_files = sorted(profiles_dir.glob("*.json"))
    if not json_files:
        print(f"[profiles] No JSON files found in {profiles_dir}", file=sys.stderr)
        return

    print(f"[profiles] Loading {len(json_files)} profile(s) from {profiles_dir}")

    for jf in json_files:
        try:
            profile = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"  [warn] Could not parse {jf.name}: {exc}", file=sys.stderr)
            continue

        repo_id = profile.get("repo_id") or normalize_id(jf.stem)
        repo_name = profile.get("repo_name", repo_id)
        domain = profile.get("repo_group")

        g.add_node(
            repo_id,
            "repo",
            repo_name,
            domain=domain,
            summary=profile.get("summary"),
            tags=profile.get("domain_tags"),
        )

        # Domain container node
        if domain:
            domain_id = normalize_id(domain)
            g.add_node(domain_id, "domain", domain)
            g.add_edge(domain_id, repo_id, "contains", "structural")

        # Sub-entities
        for sub in profile.get("sub_entities", []):
            sub_id = sub.get("id") or normalize_id(f"{repo_id}-{sub.get('label','?')}")
            sub_type = normalize_profile_entity_type(sub.get("type", "entity"))
            sub_label = sub.get("label", sub_id)
            g.add_node(sub_id, sub_type, sub_label, parent_id=repo_id)
            g.add_edge(repo_id, sub_id, "contains", "structural")

        # Direct dependencies
        for dep in profile.get("dependencies_direct", []):
            dep_id = normalize_id(dep)
            g.add_node(dep_id, "library", dep)
            g.add_edge(repo_id, dep_id, "depends_on", "dependency")

        print(f"  [ok] {repo_id} ({repo_name})")


# ---------------------------------------------------------------------------
# Mode B: --hub  (requirements-hub parsers)
# ---------------------------------------------------------------------------

def ensure_artifact_node(
    hub_dir: Path,
    g: GraphBuilder,
    relative_path: str,
    *,
    artifact_kind: str,
    summary: str | None = None,
    status: str | None = None,
) -> str:
    abs_path = hub_dir / relative_path
    if not abs_path.exists():
        return ""

    content = abs_path.read_text(encoding="utf-8", errors="replace")
    node_id = artifact_node_id(relative_path)
    g.add_node(
        node_id,
        "artifact",
        abs_path.name,
        properties={
            "artifact_kind": artifact_kind,
            "path": relative_path,
            "status": status,
            "last_verified": parse_last_verified(content),
        },
        summary=summary,
    )
    return node_id


def document_node(g: GraphBuilder, artifact_id: str, target_id: str):
    if artifact_id and target_id:
        g.add_edge(artifact_id, target_id, "documents", "semantic")


def dedupe_service_endpoints(service: dict) -> tuple[list[dict], int]:
    """
    Collapse duplicate endpoint rows to unique (method, path) routes.

    Hub source catalogs sometimes list the same route multiple times to distinguish
    public/private interfaces. The graph contract operates at the route level, so
    duplicates are merged while preserving interface and purpose metadata.
    """
    merged: dict[tuple[str, str], dict] = {}
    duplicate_rows = 0

    for endpoint in service.get("endpoints", []):
        method = str(endpoint.get("method", "GET")).upper()
        path = endpoint.get("path", "")
        key = (method, path)
        current = merged.get(key)
        if current is None:
            extras = {
                k: v for k, v in endpoint.items()
                if k not in {"method", "path", "type", "purpose"} and v is not None
            }
            merged[key] = {
                "method": method,
                "path": path,
                "interfaces": [endpoint["type"]] if endpoint.get("type") else [],
                "purposes": [endpoint["purpose"]] if endpoint.get("purpose") else [],
                "extras": extras,
            }
            continue

        duplicate_rows += 1
        if endpoint.get("type") and endpoint["type"] not in current["interfaces"]:
            current["interfaces"].append(endpoint["type"])
        if endpoint.get("purpose") and endpoint["purpose"] not in current["purposes"]:
            current["purposes"].append(endpoint["purpose"])
        for key_name, value in endpoint.items():
            if key_name in {"method", "path", "type", "purpose"} or value is None:
                continue
            current["extras"].setdefault(key_name, value)

    normalized: list[dict] = []
    for merged_endpoint in merged.values():
        record = {
            "method": merged_endpoint["method"],
            "path": merged_endpoint["path"],
            "interfaces": merged_endpoint["interfaces"],
            "purposes": merged_endpoint["purposes"],
        }
        record.update(merged_endpoint["extras"])
        normalized.append(record)

    return normalized, duplicate_rows


def parse_overview_readme(hub_dir: Path, g: GraphBuilder):
    readme_path = hub_dir / "overview" / "README.md"
    if not readme_path.exists():
        print(f"[hub] overview/README.md not found at {readme_path}", file=sys.stderr)
        return

    content = readme_path.read_text(encoding="utf-8")
    rows = _parse_markdown_tables(content)
    count = 0
    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        doc_val = _find_col(row_lower, ["document"])
        desc_val = _find_col(row_lower, ["description"])
        status_val = _find_col(row_lower, ["status"])
        match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", doc_val)
        if not match:
            continue
        relative = match.group(2).strip()
        if not relative.startswith("overview/"):
            relative = f"overview/{relative}"
        artifact_id = ensure_artifact_node(
            hub_dir,
            g,
            relative,
            artifact_kind="overview-document",
            summary=desc_val or None,
            status=status_val or None,
        )
        if artifact_id:
            count += 1
    print(f"[hub] overview/README: indexed {count} overview artifact(s)")

# ---- B1: api-catalog.json --------------------------------------------------

def parse_api_catalog(hub_dir: Path, g: GraphBuilder):
    catalog_path = hub_dir / "overview" / "api-catalog.json"
    if not catalog_path.exists():
        print(f"[hub] api-catalog.json not found at {catalog_path}", file=sys.stderr)
        return

    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[hub] Failed to parse api-catalog.json: {exc}", file=sys.stderr)
        return

    artifact_id = ensure_artifact_node(
        hub_dir,
        g,
        "overview/api-catalog.json",
        artifact_kind="api-catalog",
        summary="Structured API endpoint registry across the portfolio.",
    )

    domains = data.get("domains", [])
    total_unique_routes = 0
    duplicate_rows_collapsed = 0

    for domain in domains:
        domain_name = domain.get("name", "unknown")
        domain_key = domain.get("key") or normalize_id(domain_name)
        domain_id = normalize_id(domain_key)
        g.add_node(domain_id, "domain", domain_name)
        document_node(g, artifact_id, domain_id)

        for svc in domain.get("services", []):
            repo_slug = svc.get("repo", "")
            repo_title = svc.get("title", repo_slug)
            repo_id = typed_node_id(g, repo_slug or repo_title, "repo")
            if not repo_id:
                continue

            # Derive summary and tags from available catalog metadata
            svc_summary = svc.get("description") or svc.get("purpose") or None
            svc_tags = []
            if domain_key:
                svc_tags.append(normalize_id(domain_key))
            if svc.get("language"):
                svc_tags.append(normalize_id(svc["language"]))
            if svc.get("interfaces"):
                svc_tags.extend(normalize_id(i) for i in svc["interfaces"])
            g.add_node(repo_id, "repo", repo_title, domain=domain_key,
                       summary=svc_summary if svc_summary else None,
                       tags=svc_tags if svc_tags else None)
            g.add_edge(domain_id, repo_id, "contains", "structural")
            document_node(g, artifact_id, repo_id)

            unique_endpoints, duplicate_rows = dedupe_service_endpoints(svc)
            total_unique_routes += len(unique_endpoints)
            duplicate_rows_collapsed += duplicate_rows

            for ep in unique_endpoints:
                method = ep.get("method", "GET").upper()
                path = ep.get("path", "")
                ep_id = f"{repo_id}#{method}#{path}"
                ep_label = f"{method} {path}"
                ep_props = {}
                interfaces = ep.get("interfaces") or []
                purposes = ep.get("purposes") or []
                if interfaces:
                    ep_props["endpoint_interfaces"] = interfaces
                    if len(interfaces) == 1:
                        ep_props["endpoint_type"] = interfaces[0]
                if purposes:
                    ep_props["purpose"] = purposes[0] if len(purposes) == 1 else " / ".join(purposes)
                    if len(purposes) > 1:
                        ep_props["purposes"] = purposes
                for extra_key, extra_value in ep.items():
                    if extra_key in {"method", "path", "interfaces", "purposes"}:
                        continue
                    if extra_value is not None:
                        ep_props[extra_key] = extra_value
                g.add_node(ep_id, "api_endpoint", ep_label, parent_id=repo_id,
                           properties=ep_props if ep_props else None)
                g.add_edge(repo_id, ep_id, "exposes", "structural")
                document_node(g, artifact_id, ep_id)

    print(
        f"[hub] api-catalog: {len(domains)} domain(s), "
        f"{total_unique_routes} unique route(s), "
        f"{duplicate_rows_collapsed} duplicate row(s) collapsed"
    )


# ---- B2: messaging-topology.md  -------------------------------------------

def parse_messaging_topology(hub_dir: Path, g: GraphBuilder):
    topo_path = hub_dir / "overview" / "messaging-topology.md"
    if not topo_path.exists():
        print(f"[hub] messaging-topology.md not found at {topo_path}", file=sys.stderr)
        return

    content = topo_path.read_text(encoding="utf-8")
    artifact_id = ensure_artifact_node(
        hub_dir,
        g,
        "overview/messaging-topology.md",
        artifact_kind="messaging-topology",
        summary="Kafka and RabbitMQ topology registry across the portfolio.",
    )
    print("[hub] messaging-topology: parsing Mermaid blocks")

    # Find all graph LR blocks (Kafka section is usually first, RabbitMQ second)
    # We look for the Kafka section specifically
    kafka_section = _extract_kafka_section(content)
    if kafka_section:
        _parse_mermaid_graph(kafka_section, g, artifact_id, broker="kafka")
    else:
        print("[hub] messaging-topology: no Kafka section found", file=sys.stderr)

    rabbit_section = _extract_rabbitmq_section(content)
    if rabbit_section:
        _parse_mermaid_graph(rabbit_section, g, artifact_id, broker="rabbitmq")


def _extract_kafka_section(content: str) -> str:
    """Extract the first mermaid graph block after a Kafka heading."""
    # Find "Kafka" heading then nearest ```mermaid ... ``` block
    kafka_heading = re.search(r"(?i)#+\s*kafka", content)
    if not kafka_heading:
        # Try to find mermaid block anywhere
        return _extract_first_mermaid_block(content)
    after = content[kafka_heading.start():]
    return _extract_first_mermaid_block(after)


def _extract_rabbitmq_section(content: str) -> str:
    rabbit_heading = re.search(r"(?i)#+\s*rabbit", content)
    if not rabbit_heading:
        return ""
    # Find the SECOND mermaid block in content (skip Kafka's block)
    after = content[rabbit_heading.start():]
    return _extract_first_mermaid_block(after)


def _extract_first_mermaid_block(text: str) -> str:
    """Return the content inside the first ```mermaid ... ``` fence."""
    m = re.search(r"```mermaid\s*(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1)
    # Also handle indented mermaid blocks or raw graph LR
    m = re.search(r"(graph\s+(?:LR|TD|TB|RL)\b.*?)(?:\n```|\Z)", text, re.DOTALL)
    if m:
        return m.group(1)
    return ""


def _parse_mermaid_graph(block: str, g: GraphBuilder, artifact_id: str, broker: str = "kafka"):
    """
    Parse a Mermaid graph LR block:
      - Node definitions: ID["label"] or ID{{"label"}} or ID(["label"])
      - Subgraph sections: subgraph producers / kafka / consumers
      - Arrow lines: A --> B  or  A --> B & C  (multi-target)
    """
    lines = block.splitlines()

    # Track which subgraph we're in: producers | topics | consumers | other
    current_subgraph = None
    producers: dict[str, str] = {}   # short_id -> display label
    topics: dict[str, str] = {}      # short_id -> display label
    consumers: dict[str, str] = {}   # short_id -> display label
    node_labels: dict[str, str] = {} # all node id -> label

    # Regexes for node definitions
    re_node_bracket  = re.compile(r'^(\w+)\["([^"]+)"\]')         # ID["label"]
    re_node_dblbrace = re.compile(r'^(\w+)\{\{"([^"]+)"\}\}')     # ID{{"label"}}
    re_node_paren    = re.compile(r'^(\w+)\(\["([^"]+)"\]\)')     # ID(["label"])
    re_node_simple   = re.compile(r'^(\w+)\["([^"<]+)')           # partial
    re_subgraph      = re.compile(r'^\s*subgraph\s+(\S+)', re.IGNORECASE)
    re_end           = re.compile(r'^\s*end\s*$', re.IGNORECASE)
    # Arrow: SRC --> TGT  or  SRC --> TGT & TGT2
    re_arrow         = re.compile(r'^\s*(\w+)\s*-->\s*(.+)$')
    re_multi_target  = re.compile(r'(\w+)')

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("%%"):
            continue

        # Subgraph boundary
        m = re_subgraph.match(line)
        if m:
            sg_name = m.group(1).lower()
            if "producer" in sg_name:
                current_subgraph = "producers"
            elif "consumer" in sg_name:
                current_subgraph = "consumers"
            elif broker in sg_name or "topic" in sg_name or "kafka" in sg_name or "rabbit" in sg_name:
                current_subgraph = "topics"
            else:
                current_subgraph = "other"
            continue

        if re_end.match(line):
            current_subgraph = None
            continue

        # Node definition (try each pattern)
        node_id, node_label = None, None
        for pattern in [re_node_dblbrace, re_node_bracket, re_node_paren]:
            mm = pattern.match(line)
            if mm:
                node_id, node_label = mm.group(1), strip_br(mm.group(2))
                break

        if node_id and node_label:
            node_labels[node_id] = node_label
            if current_subgraph == "producers":
                producers[node_id] = node_label
            elif current_subgraph == "consumers":
                consumers[node_id] = node_label
            elif current_subgraph == "topics":
                topics[node_id] = node_label
            continue

        # Arrow
        m = re_arrow.match(line)
        if m:
            src_id = m.group(1)
            targets_raw = m.group(2)
            # Split on & for compound targets
            target_ids = [t.strip() for t in re.split(r"\s*&\s*", targets_raw)]
            for tgt_id in target_ids:
                # tgt_id may have trailing label like TOPIC["..."]
                tgt_clean = re_multi_target.match(tgt_id)
                if tgt_clean:
                    tgt_id = tgt_clean.group(1)
                # Determine relationship
                src_is_producer = src_id in producers
                tgt_is_topic    = tgt_id in topics
                src_is_topic    = src_id in topics
                tgt_is_consumer = tgt_id in consumers

                if src_is_producer and tgt_is_topic:
                    _add_broker_edge(g, artifact_id, src_id, tgt_id, "publishes_to",
                                     producers, topics, broker)
                elif src_is_topic and tgt_is_consumer:
                    _add_broker_edge(g, artifact_id, src_id, tgt_id, "subscribes_to",
                                     topics, consumers, broker)
                else:
                    # Unknown—still record as calls
                    src_label = node_labels.get(src_id, src_id)
                    tgt_label = node_labels.get(tgt_id, tgt_id)
                    src_node_id = _ensure_node(g, src_id, src_label, producers, topics, consumers, broker)
                    tgt_node_id = _ensure_node(g, tgt_id, tgt_label, producers, topics, consumers, broker)
                    document_node(g, artifact_id, src_node_id)
                    document_node(g, artifact_id, tgt_node_id)
                    g.add_edge(src_node_id, tgt_node_id, "calls", "behavioral")


def _ensure_node(g, short_id, label, producers, topics, consumers, broker):
    display = label or short_id
    if short_id in topics:
        nid = typed_node_id(g, display, "queue_topic")
        g.add_node(nid, "queue_topic", label or short_id,
                   properties={"broker": broker})
    else:
        nid = typed_node_id(g, display, "repo")
        g.add_node(nid, "repo", label or short_id)
    return nid


def _add_broker_edge(g, artifact_id, src_short, tgt_short, relation, src_map, tgt_map, broker):
    src_label = src_map.get(src_short, src_short)
    tgt_label = tgt_map.get(tgt_short, tgt_short)

    if relation == "publishes_to":
        src_id = typed_node_id(g, src_label, "repo")
        tgt_id = typed_node_id(g, tgt_label, "queue_topic")
        g.add_node(src_id, "repo", src_label)
        g.add_node(tgt_id, "queue_topic", tgt_label, properties={"broker": broker})
    else:
        src_id = typed_node_id(g, src_label, "queue_topic")
        tgt_id = typed_node_id(g, tgt_label, "repo")
        g.add_node(src_id, "queue_topic", src_label, properties={"broker": broker})
        g.add_node(tgt_id, "repo", tgt_label)

    document_node(g, artifact_id, src_id)
    document_node(g, artifact_id, tgt_id)
    g.add_edge(src_id, tgt_id, relation, "behavioral")


# ---- B3: database-schemas.md -----------------------------------------------

def parse_database_schemas(hub_dir: Path, g: GraphBuilder):
    db_path = hub_dir / "overview" / "database-schemas.md"
    if not db_path.exists():
        print(f"[hub] database-schemas.md not found at {db_path}", file=sys.stderr)
        return

    content = db_path.read_text(encoding="utf-8")
    artifact_id = ensure_artifact_node(
        hub_dir,
        g,
        "overview/database-schemas.md",
        artifact_kind="database-schema-summary",
        summary="Cross-domain database engines, key tables, and entity relationships.",
    )
    print("[hub] database-schemas: parsing markdown tables")

    rows = _parse_markdown_tables(content)
    # Expected columns (case-insensitive): Service | Engine | Key Tables/Collections | ...
    count = 0
    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        service_val  = _find_col(row_lower, ["service", "repo", "service/repo"])
        engine_val   = _find_col(row_lower, ["engine", "db engine", "database engine"])
        tables_val   = _find_col(row_lower, ["key tables/collections", "tables", "collections",
                                              "key tables", "table/collection"])

        if not service_val or not engine_val:
            continue

        repo_id = typed_node_id(g, service_val, "repo")
        engine_norm = normalize_engine(engine_val)
        db_id = f"{repo_id}#{engine_norm}"

        g.add_node(repo_id, "repo", service_val)
        g.add_node(db_id, "database", engine_val, parent_id=repo_id,
                   properties={"engine": engine_norm})
        g.add_edge(repo_id, db_id, "owns_data_in", "data_flow")
        document_node(g, artifact_id, repo_id)
        document_node(g, artifact_id, db_id)

        if tables_val:
            raw_tables = [t.strip() for t in tables_val.split(",") if t.strip()]
            for tname in raw_tables:
                # Remove markdown formatting
                tname_clean = re.sub(r"[`*_]", "", tname).strip()
                if not tname_clean or tname_clean in ("-", "—", "n/a", "N/A"):
                    continue
                tbl_id = f"{db_id}#{normalize_id(tname_clean)}"
                g.add_node(tbl_id, "table", tname_clean, parent_id=db_id)
                g.add_edge(db_id, tbl_id, "contains", "structural")
                document_node(g, artifact_id, tbl_id)

        count += 1

    print(f"  [ok] Parsed {count} database rows")


# ---- B4: integration-matrix.md ---------------------------------------------

def parse_integration_matrix(hub_dir: Path, g: GraphBuilder):
    int_path = hub_dir / "overview" / "integration-matrix.md"
    if not int_path.exists():
        print(f"[hub] integration-matrix.md not found at {int_path}", file=sys.stderr)
        return

    content = int_path.read_text(encoding="utf-8")
    artifact_id = ensure_artifact_node(
        hub_dir,
        g,
        "overview/integration-matrix.md",
        artifact_kind="integration-matrix",
        summary="Provider integration comparison across domains and services.",
    )
    print("[hub] integration-matrix: parsing markdown tables")

    rows = _parse_markdown_tables(content)
    count = 0
    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        provider_val  = _find_col(row_lower, ["provider", "integration", "external service"])
        repo_val      = _find_col(row_lower, ["repo", "service", "consuming service", "used by"])
        messaging_val = _find_col(row_lower, ["messaging", "kafka", "queue"])
        auth_val      = _find_col(row_lower, ["auth"])
        incoming_val  = _find_col(row_lower, ["incoming"])
        storage_val   = _find_col(row_lower, ["storage"])
        domain_val    = _find_col(row_lower, ["domain"])
        capabilities_val = _find_col(row_lower, ["capabilities", "purpose"])

        if not provider_val or not repo_val:
            continue

        provider_id = typed_node_id(g, provider_val, "provider")
        repo_id     = typed_node_id(g, repo_val, "repo")

        g.add_node(
            provider_id,
            "provider",
            provider_val,
            properties={
                "provider_category": None,
                "auth": auth_val or None,
                "incoming_pattern": incoming_val or None,
                "storage": storage_val or None,
                "messaging": messaging_val or None,
                "capabilities": capabilities_val or None,
                "domain": domain_val or None,
                "external": True,
            },
        )
        g.add_node(repo_id, "repo", repo_val)
        g.add_edge(repo_id, provider_id, "uses_provider", "behavioral")
        document_node(g, artifact_id, repo_id)
        document_node(g, artifact_id, provider_id)

        if messaging_val:
            msg_lower = messaging_val.lower()
            if "kafka" in msg_lower:
                g.add_edge(repo_id, provider_id, "calls", "behavioral",
                           notes="via Kafka messaging")

        count += 1

    print(f"  [ok] Parsed {count} integration rows")


# ---- B5: nuget-dependency-map.md -------------------------------------------

def parse_nuget_dependency_map(hub_dir: Path, g: GraphBuilder):
    nuget_path = hub_dir / "overview" / "nuget-dependency-map.md"
    if not nuget_path.exists():
        print(f"[hub] nuget-dependency-map.md not found at {nuget_path}", file=sys.stderr)
        return

    content = nuget_path.read_text(encoding="utf-8")
    artifact_id = ensure_artifact_node(
        hub_dir,
        g,
        "overview/nuget-dependency-map.md",
        artifact_kind="dependency-map",
        summary="Cross-repo package dependency map.",
    )
    print("[hub] nuget-dependency-map: parsing Mermaid graph")

    for block in _iter_mermaid_blocks(content):
        _parse_nuget_mermaid(block, g, artifact_id)


def _iter_mermaid_blocks(content: str):
    """Yield all mermaid block bodies from markdown."""
    for m in re.finditer(r"```mermaid\s*(.*?)```", content, re.DOTALL):
        yield m.group(1)


def _parse_nuget_mermaid(block: str, g: GraphBuilder, artifact_id: str):
    """
    Parse a Mermaid graph for NuGet dependencies.
    subgraph names are domain groups; node labels are package/repo names.

    Handles:
      - Standard arrows:       A --> B
      - Labeled arrows:        A -->|"label"| B
      - Compound targets:      A -->|"label"| B & C & D
      - Subgraph IDs as targets (domain-level references)
    """
    lines = block.splitlines()
    current_subgraph_id   = None
    current_domain_label  = None
    node_labels: dict[str, str] = {}   # short Mermaid ID → display label
    subgraph_labels: dict[str, str] = {}  # subgraph short ID → display label

    # subgraph identity["Identity & Risk"]  OR  subgraph infra["Infrastructure"]
    re_subgraph_labeled = re.compile(r'^\s*subgraph\s+(\w+)\s*\["([^"]+)"\]', re.IGNORECASE)
    re_subgraph_plain   = re.compile(r'^\s*subgraph\s+(\S+)\s*$', re.IGNORECASE)
    re_end              = re.compile(r'^\s*end\s*$', re.IGNORECASE)
    re_node_br          = re.compile(r'^(\w+)\["([^"]+)"\]')
    # Arrow: --> or ==> with optional |"label"| then targets (may be compound with &)
    re_arrow = re.compile(r'^\s*(\w+)\s*(?:-->|==>)(?:\|[^|]+\|)?\s*(.+)$')

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("%%") or line.startswith("graph "):
            continue

        # Subgraph start (labeled: subgraph id["Label"] or plain: subgraph id)
        m = re_subgraph_labeled.match(line)
        if m:
            current_subgraph_id  = m.group(1)
            current_domain_label = strip_br(m.group(2))
            subgraph_labels[current_subgraph_id] = current_domain_label
            continue

        m = re_subgraph_plain.match(line)
        if m:
            current_subgraph_id  = m.group(1)
            current_domain_label = current_subgraph_id
            subgraph_labels.setdefault(current_subgraph_id, current_subgraph_id)
            continue

        if re_end.match(line):
            current_subgraph_id  = None
            current_domain_label = None
            continue

        # Node definition
        m = re_node_br.match(line)
        if m:
            nid, nlabel = m.group(1), strip_br(m.group(2))
            node_labels[nid] = nlabel
            ntype = "package" if "." in nlabel and nlabel[0].isupper() else "repo"
            n_norm = typed_node_id(g, nlabel, ntype)
            g.add_node(n_norm, ntype, nlabel,
                       domain=current_domain_label if current_domain_label else None)
            document_node(g, artifact_id, n_norm)
            continue

        # Arrow (labeled or plain, single or compound targets)
        m = re_arrow.match(line)
        if m:
            src_short  = m.group(1)
            targets_raw = m.group(2)
            src_label  = node_labels.get(src_short, src_short)
            src_id     = typed_node_id(g, src_label, "repo")

            # Split compound targets on &; strip Mermaid style suffixes like ["..."]
            raw_targets = [t.strip() for t in re.split(r"\s*&\s*", targets_raw)]
            for raw_tgt in raw_targets:
                # Strip any trailing ["..."] label
                tgt_short = re.match(r'^(\w+)', raw_tgt)
                if not tgt_short:
                    continue
                tgt_short = tgt_short.group(1)

                # Target is a known node ID
                if tgt_short in node_labels:
                    tgt_label = node_labels[tgt_short]
                    ntype = "package" if "." in tgt_label and tgt_label[0].isupper() else "repo"
                    tgt_id    = typed_node_id(g, tgt_label, ntype)
                    g.add_node(src_id, "repo", src_label)
                    g.add_node(tgt_id, ntype, tgt_label)
                    document_node(g, artifact_id, src_id)
                    document_node(g, artifact_id, tgt_id)
                    g.add_edge(src_id, tgt_id, "depends_on", "dependency")
                # Target is a subgraph ID (domain reference)
                elif tgt_short in subgraph_labels:
                    domain_label = subgraph_labels[tgt_short]
                    domain_id    = normalize_id(domain_label)
                    g.add_node(src_id, "repo", src_label)
                    g.add_node(domain_id, "domain", domain_label)
                    document_node(g, artifact_id, src_id)
                    document_node(g, artifact_id, domain_id)
                    g.add_edge(src_id, domain_id, "depends_on", "dependency")
                else:
                    # Fallback: treat as a generic repo/package node
                    tgt_id = typed_node_id(g, tgt_short, "repo")
                    g.add_node(src_id, "repo", src_label)
                    g.add_node(tgt_id, "repo", tgt_short)
                    document_node(g, artifact_id, src_id)
                    document_node(g, artifact_id, tgt_id)
                    g.add_edge(src_id, tgt_id, "depends_on", "dependency")


# ---- B6: */as-is/cross-repo-dependencies.md --------------------------------

def parse_cross_repo_dependencies(hub_dir: Path, g: GraphBuilder):
    """Walk all as-is/cross-repo-dependencies.md files in the hub."""
    found = list(hub_dir.rglob("as-is/cross-repo-dependencies.md"))
    if not found:
        print("[hub] cross-repo-dependencies.md: no files found", file=sys.stderr)
        return

    print(f"[hub] cross-repo-dependencies: {len(found)} file(s)")
    count = 0

    for crp in found:
        # Infer the repo context from the path: hub/REPO_DIR/as-is/cross-repo-...
        repo_dir = crp.parent.parent.name
        repo_id  = typed_node_id(g, repo_dir, "repo")
        g.add_node(repo_id, "repo", repo_dir)
        rel_path = str(crp.relative_to(hub_dir))
        artifact_id = ensure_artifact_node(
            hub_dir,
            g,
            rel_path,
            artifact_kind="cross-repo-dependencies",
            summary=f"Cross-repo package dependency notes for {repo_dir}.",
        )
        document_node(g, artifact_id, repo_id)

        content = crp.read_text(encoding="utf-8")
        rows = _parse_markdown_tables(content)

        for row in rows:
            row_lower = {k.lower().strip(): v for k, v in row.items()}
            pkg_val      = _find_col(row_lower, ["package", "nuget package", "package name"])
            published_by = _find_col(row_lower, ["published by", "publisher", "owner"])
            consumed_by  = _find_col(row_lower, ["consumed by", "consumers", "used by"])

            if not pkg_val:
                continue

            pkg_id = typed_node_id(g, pkg_val, "package")
            g.add_node(pkg_id, "package", pkg_val)

            if published_by:
                pub_id = typed_node_id(g, published_by, "repo")
                g.add_node(pub_id, "repo", published_by)
                g.add_edge(pub_id, pkg_id, "exposes", "structural")
                document_node(g, artifact_id, pub_id)

            if consumed_by:
                for consumer in re.split(r"[,;]", consumed_by):
                    consumer = consumer.strip()
                    if not consumer or consumer in ("-", "—"):
                        continue
                    cons_id = typed_node_id(g, consumer, "repo")
                    g.add_node(cons_id, "repo", consumer)
                    g.add_edge(cons_id, pkg_id, "depends_on", "dependency")
                    document_node(g, artifact_id, cons_id)

            document_node(g, artifact_id, pkg_id)

            count += 1

    print(f"  [ok] Parsed {count} NuGet cross-repo rows")


def split_compound_values(raw: str) -> list[str]:
    if not raw:
        return []
    cleaned = raw.replace(";", ",")
    parts = [part.strip() for part in re.split(r"\s*\+\s*|\s*,\s*", cleaned) if part.strip()]
    return [part for part in parts if part not in {"-", "—", "N/A", "n/a"}]


def strip_ticks(raw: str) -> str:
    return raw.strip().strip("`").strip()


def parse_platform_summary(hub_dir: Path, g: GraphBuilder) -> dict:
    summary_path = hub_dir / "overview" / "platform-summary.md"
    if not summary_path.exists():
        print(f"[hub] platform-summary.md not found at {summary_path}", file=sys.stderr)
        return {}

    content = summary_path.read_text(encoding="utf-8")
    artifact_id = ensure_artifact_node(
        hub_dir,
        g,
        "overview/platform-summary.md",
        artifact_kind="platform-summary",
        summary="Portfolio-level summary of repositories, languages, providers, and gaps.",
    )

    metrics: dict[str, int] = {}
    rows = _parse_markdown_tables(content)
    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        metric_val = _find_col(row_lower, ["metric"])
        value_val = _find_col(row_lower, ["value"])
        repo_val = _find_col(row_lower, ["repository"])
        loc_val = _find_col(row_lower, ["loc"])
        lang_val = _find_col(row_lower, ["primary language"])
        type_val = _find_col(row_lower, ["type"])
        domain_val = _find_col(row_lower, ["domain"])

        if metric_val and value_val:
            metric_key = metric_val.lower()
            if "total repositories" in metric_key:
                metrics["repo_count"] = parse_int_maybe(value_val) or 0
            elif "services" in metric_key and "api" not in metric_key:
                metrics["service_count"] = parse_int_maybe(value_val) or 0
            elif "external providers" in metric_key:
                metrics["provider_count"] = parse_int_maybe(value_val) or 0
            elif "business processes" in metric_key:
                metrics["process_count"] = parse_int_maybe(value_val) or 0
            elif "documented gaps" in metric_key:
                metrics["gap_count"] = parse_int_maybe(value_val) or 0
            elif "total lines of code" in metric_key:
                metrics["loc_total"] = parse_int_maybe(value_val) or 0
            continue

        if repo_val:
            repo_name = strip_ticks(repo_val)
            if not repo_name or repo_name.startswith("|") or repo_name.startswith("**~"):
                continue
            repo_id = typed_node_id(g, repo_name, "repo")
            repo_props = {}
            loc_num = parse_int_maybe(loc_val)
            if loc_num is not None:
                repo_props["loc"] = loc_num
            if lang_val:
                repo_props["primary_language"] = strip_ticks(lang_val)
            if type_val:
                repo_props["repo_kind"] = strip_ticks(type_val)
            if domain_val:
                repo_props["domain"] = strip_ticks(domain_val)
            g.add_node(
                repo_id,
                "repo",
                repo_name,
                domain=strip_ticks(domain_val) if domain_val else None,
                properties=repo_props or None,
            )
            document_node(g, artifact_id, repo_id)

    print(f"[hub] platform-summary: captured portfolio metrics and repo enrichment")
    return metrics


def parse_infrastructure_matrix(hub_dir: Path, g: GraphBuilder):
    infra_path = hub_dir / "overview" / "infrastructure-matrix.md"
    if not infra_path.exists():
        print(f"[hub] infrastructure-matrix.md not found at {infra_path}", file=sys.stderr)
        return

    content = infra_path.read_text(encoding="utf-8")
    artifact_id = ensure_artifact_node(
        hub_dir,
        g,
        "overview/infrastructure-matrix.md",
        artifact_kind="infrastructure-matrix",
        summary="Per-service runtime, storage, messaging, and infrastructure version profile.",
    )

    rows = _parse_markdown_tables(content)
    count = 0
    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        service_val = _find_col(row_lower, ["service", "repo"])
        storage_val = _find_col(row_lower, ["storage"])
        messaging_val = _find_col(row_lower, ["messaging"])
        runtime_val = _find_col(row_lower, [".net / runtime", "runtime", ".net"])
        infra_val = _find_col(row_lower, ["infra"])

        if not service_val:
            continue
        repo_name = strip_ticks(service_val)
        if repo_name.startswith("**") or repo_name in {"Metric", "Service"}:
            continue

        repo_id = typed_node_id(g, repo_name, "repo")
        props = {
            "storage": split_compound_values(storage_val),
            "messaging": split_compound_values(messaging_val),
            "runtime": strip_ticks(runtime_val) if runtime_val else None,
            "sc_infrastructure_version": strip_ticks(infra_val) if infra_val else None,
        }
        g.add_node(repo_id, "repo", repo_name, properties=props)
        document_node(g, artifact_id, repo_id)
        count += 1

    print(f"[hub] infrastructure-matrix: enriched {count} repo node(s)")


def parse_process_catalog(hub_dir: Path, g: GraphBuilder):
    process_path = hub_dir / "overview" / "process-catalog.md"
    if not process_path.exists():
        print(f"[hub] process-catalog.md not found at {process_path}", file=sys.stderr)
        return

    content = process_path.read_text(encoding="utf-8")
    artifact_id = ensure_artifact_node(
        hub_dir,
        g,
        "overview/process-catalog.md",
        artifact_kind="process-catalog",
        summary="Business process inventory, criticality, regulatory tags, and service chains.",
    )

    inventory_match = re.search(
        r"^##\s+2\.\s+Process Inventory\s*(.*?)(?=^---\s*$|^##\s+3\.)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    inventory_section = inventory_match.group(1) if inventory_match else content
    rows = _parse_markdown_tables(inventory_section)
    created = 0
    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        process_id = row_lower.get("id", "")
        process_name = row_lower.get("process", "")
        category = row_lower.get("category", "")
        domain_owner = row_lower.get("domain owner", "")
        criticality = row_lower.get("criticality", "")
        regulatory = row_lower.get("regulatory tags", "")
        service_count = row_lower.get("services", "")
        status = row_lower.get("status", "")

        if not process_id or not re.fullmatch(r"PRO-\d+", process_id):
            continue

        g.add_node(
            process_id,
            "process",
            process_name or process_id,
            properties={
                "category": category or None,
                "criticality": criticality or None,
                "status": status or None,
                "domain_owner": domain_owner or None,
                "regulatory_tags": split_compound_values(regulatory),
                "service_count": parse_int_maybe(service_count) if service_count else None,
            },
        )
        document_node(g, artifact_id, process_id)
        if domain_owner:
            domain_id = normalize_id(domain_owner)
            g.add_node(domain_id, "domain", domain_owner)
            g.add_edge(domain_id, process_id, "contains", "structural")
        created += 1

    section_pattern = re.compile(
        r"^###\s+(PRO-\d+):\s+(.+?)\n(.*?)(?=^###\s+PRO-\d+:|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for match in section_pattern.finditer(content):
        process_id, process_name, section = match.groups()
        g.add_node(process_id, "process", process_name)
        detail_rows = _parse_markdown_tables(section)
        if not detail_rows:
            continue
        detail = {}
        for row in detail_rows:
            row_lower = {k.lower().strip(): v for k, v in row.items()}
            field_name = row_lower.get("field", "").strip().strip("*").lower()
            value = row_lower.get("value", "")
            if field_name:
                detail[field_name] = value

        service_chain = detail.get("service chain", "")
        external_providers = detail.get("external providers", "")
        regulatory = detail.get("regulatory", "")
        known_gaps = detail.get("known gaps", "")

        service_names = re.findall(r"`([^`]+)`", service_chain)
        for service_name in service_names:
            repo_name = strip_ticks(service_name)
            repo_id = typed_node_id(g, repo_name, "repo")
            g.add_node(repo_id, "repo", repo_name)
            g.add_edge(repo_id, process_id, "implements_process", "behavioral")
            document_node(g, artifact_id, repo_id)

        providers = [strip_ticks(p) for p in split_compound_values(external_providers)]
        for provider_name in providers:
            provider_id = typed_node_id(g, provider_name, "provider")
            g.add_node(provider_id, "provider", provider_name, properties={"external": True})
            g.add_edge(process_id, provider_id, "uses_provider", "behavioral")
            document_node(g, artifact_id, provider_id)

        process_props = {
            "regulatory_tags": split_compound_values(regulatory),
            "known_gaps": [gap.strip() for gap in re.split(r"[;,]", known_gaps) if gap.strip()],
            "service_chain": service_names,
        }
        g.add_node(process_id, "process", process_name, properties=process_props)

    print(f"[hub] process-catalog: parsed {created} process inventory row(s)")


# ---------------------------------------------------------------------------
# Markdown table parser
# ---------------------------------------------------------------------------

def _parse_markdown_tables(content: str) -> list[dict[str, str]]:
    """
    Parse all markdown tables in content.
    Returns list of dicts with header → cell value.
    Skips separator rows (those containing only dashes/colons/pipes).
    """
    rows = []
    current_headers: list[str] = []

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            current_headers = []
            continue

        cells = [c.strip() for c in stripped.strip("|").split("|")]

        # Separator row: cells look like "---", ":---:", "---:"
        if all(re.match(r"^:?-{1,}:?$", c) for c in cells if c):
            continue

        if not current_headers:
            current_headers = cells
            continue

        # Data row
        if len(cells) < len(current_headers):
            cells += [""] * (len(current_headers) - len(cells))
        row = {current_headers[i]: cells[i] for i in range(len(current_headers))}
        rows.append(row)

    return rows


def _find_col(row_lower: dict, candidates: list[str]) -> str:
    """Return first matching value from a dict keyed by lowercased column names."""
    for c in candidates:
        if c in row_lower:
            return row_lower[c]
    # Partial match
    for c in candidates:
        for k, v in row_lower.items():
            if c in k:
                return v
    return ""


# ---------------------------------------------------------------------------
# Hub entry point
# ---------------------------------------------------------------------------

def build_from_hub(hub_dir: Path, g: GraphBuilder) -> dict:
    print(f"[hub] Building knowledge graph from hub at {hub_dir}")
    parse_overview_readme(hub_dir, g)
    parse_api_catalog(hub_dir, g)
    parse_messaging_topology(hub_dir, g)
    parse_database_schemas(hub_dir, g)
    parse_integration_matrix(hub_dir, g)
    parse_nuget_dependency_map(hub_dir, g)
    parse_cross_repo_dependencies(hub_dir, g)
    metrics = parse_platform_summary(hub_dir, g)
    parse_infrastructure_matrix(hub_dir, g)
    parse_process_catalog(hub_dir, g)
    return metrics


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build a knowledge-graph.json from repo profiles or a requirements-hub."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--profiles", metavar="DIR",
                      help="Directory containing repo-profile JSON files")
    mode.add_argument("--hub", metavar="DIR",
                      help="requirements-hub directory")
    parser.add_argument("--output", metavar="FILE",
                        help="Output JSON file path (default: graphs/knowledge-graph.json)")
    args = parser.parse_args()

    g = GraphBuilder()

    if args.profiles:
        profiles_dir = Path(args.profiles).resolve()
        if not profiles_dir.is_dir():
            print(f"Error: profiles directory not found: {profiles_dir}", file=sys.stderr)
            sys.exit(1)
        build_from_profiles(profiles_dir, g)
        portfolio_name = profiles_dir.name
        default_output = profiles_dir.parent / "graphs" / "knowledge-graph.json"
        portfolio_metrics = {}

    else:  # --hub
        hub_dir = Path(args.hub).resolve()
        if not hub_dir.is_dir():
            print(f"Error: hub directory not found: {hub_dir}", file=sys.stderr)
            sys.exit(1)
        portfolio_metrics = build_from_hub(hub_dir, g)
        portfolio_name = hub_dir.name
        default_output = hub_dir / "graphs" / "knowledge-graph.json"

    output_path = Path(args.output).resolve() if args.output else default_output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    graph_dict = g.to_dict(portfolio_name, "profiles" if args.profiles else "hub", portfolio_metrics)
    output_path.write_text(json.dumps(graph_dict, indent=2, ensure_ascii=False), encoding="utf-8")

    meta = graph_dict["meta"]
    print(
        f"\n[done] Knowledge graph written to {output_path}\n"
        f"       nodes={meta['node_count']}  edges={meta['edge_count']}"
    )


if __name__ == "__main__":
    main()
