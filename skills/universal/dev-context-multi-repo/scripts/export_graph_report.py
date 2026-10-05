#!/usr/bin/env python3
"""
Generate static HTML and Markdown reports from a knowledge graph.

Usage:
  python3 export_graph_report.py graphs/knowledge-graph.json
  python3 export_graph_report.py graphs/knowledge-graph.json --output-dir reports/
  python3 export_graph_report.py graphs/knowledge-graph.json --title "Platform Graph"
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def load_module(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


query_graph = load_module("query_graph.py", "dev_context_multi_repo_query_graph_report")

DEFAULT_DIAGRAM_SPECS = (
    {
        "title": "Platform Overview",
        "description": "Domains, repositories, providers, and processes.",
        "include_types": "domain,repo,provider,process",
        "exclude_relations": "documents",
        "group_by": "domain",
    },
    {
        "title": "Data Topology",
        "description": "Repositories and storage relationships.",
        "include_types": "domain,repo,database,table,entity",
        "include_relations": "contains,reads_from,writes_to,owns_data_in",
        "group_by": "domain",
    },
    {
        "title": "Documentation Coverage",
        "description": "Artifacts and the nodes they document.",
        "include_types": "artifact,domain,repo,provider,process",
        "include_relations": "documents,contains,implements_process,uses_provider",
        "group_by": "type",
    },
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path | None) -> dict | None:
    if not path or not path.exists():
        return None
    try:
        return load_json(path)
    except json.JSONDecodeError:
        return None


def default_reports_dir(graph_path: Path) -> Path:
    if graph_path.parent.name == "graphs":
        return graph_path.parent.parent / "reports"
    return graph_path.parent / "reports"


def default_title(graph_path: Path, graph: dict) -> str:
    meta = graph.get("meta", {})
    for key in ("portfolio", "build_source"):
        value = meta.get(key)
        if isinstance(value, str) and value.strip():
            return f"{value.strip().replace('-', ' ').title()} Graph Report"
    return f"{graph_path.stem.replace('-', ' ').title()} Report"


def relative_display_path(path: Path, base_dir: Path) -> str:
    try:
        return os.path.relpath(path.resolve(), base_dir.resolve())
    except ValueError:
        return str(path.resolve())


def safe_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def truncate(value: object, max_len: int = 120) -> str:
    text = safe_text(value)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def html_escape(value: object) -> str:
    return html.escape(safe_text(value), quote=True)


def markdown_escape(value: object) -> str:
    return safe_text(value).replace("|", "\\|").replace("\n", "<br>")


def format_markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(cell) for cell in row) + " |")
    return "\n".join(lines)


def slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-") or "section"


def build_node_index(nodes: list[dict]) -> dict[str, dict]:
    return {node["id"]: node for node in nodes if "id" in node}


def count_nodes_by_type(nodes: list[dict]) -> list[tuple[str, int]]:
    counts = Counter(node.get("type", "unknown") for node in nodes)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def count_edges_by_relation(edges: list[dict]) -> list[tuple[str, int]]:
    counts = Counter(edge.get("relation", "unknown") for edge in edges)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def top_ranked_nodes(nodes: list[dict], edges: list[dict], limit: int = 15) -> list[dict]:
    fan_in_count: dict[str, int] = {}
    fan_in_weight: dict[str, float] = {}
    node_index = build_node_index(nodes)
    for edge in edges:
        target = edge.get("target")
        if not target:
            continue
        fan_in_count[target] = fan_in_count.get(target, 0) + 1
        fan_in_weight[target] = fan_in_weight.get(target, 0.0) + float(edge.get("weight", 0.5))

    ranked = []
    for node_id, node in node_index.items():
        ranked.append(
            {
                "id": node_id,
                "label": node.get("label", node_id),
                "type": node.get("type", "unknown"),
                "fan_in": fan_in_count.get(node_id, 0),
                "weighted_fan_in": round(fan_in_weight.get(node_id, 0.0), 2),
                "domain": node.get("domain", ""),
            }
        )
    ranked.sort(key=lambda item: (-item["weighted_fan_in"], -item["fan_in"], item["label"]))
    return ranked[:limit]


def build_relation_rows(
    *,
    edges: list[dict],
    node_index: dict[str, dict],
    relation: str,
    source_types: set[str] | None = None,
    target_types: set[str] | None = None,
    limit: int = 50,
) -> list[dict]:
    rows = []
    for edge in edges:
        if edge.get("relation") != relation:
            continue
        source = node_index.get(edge.get("source", ""))
        target = node_index.get(edge.get("target", ""))
        if not source or not target:
            continue
        if source_types and source.get("type") not in source_types:
            continue
        if target_types and target.get("type") not in target_types:
            continue
        rows.append(
            {
                "source_id": source.get("id", ""),
                "source_label": source.get("label", source.get("id", "")),
                "source_type": source.get("type", ""),
                "source_domain": source.get("domain", ""),
                "target_id": target.get("id", ""),
                "target_label": target.get("label", target.get("id", "")),
                "target_type": target.get("type", ""),
                "target_domain": target.get("domain", ""),
                "relation": relation,
            }
        )
    rows.sort(
        key=lambda row: (
            row["source_domain"],
            row["source_label"],
            row["target_label"],
            row["target_id"],
        )
    )
    return rows[:limit] if limit > 0 else rows


def grouped_node_rows(nodes: list[dict]) -> list[tuple[str, list[dict]]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for node in nodes:
        groups[node.get("type", "unknown")].append(node)
    grouped = []
    for node_type in sorted(groups):
        rows = sorted(
            groups[node_type],
            key=lambda node: (
                str(node.get("domain", "")),
                str(node.get("label", node.get("id", ""))),
                str(node.get("id", "")),
            ),
        )
        grouped.append((node_type, rows))
    return grouped


def render_diagrams(nodes: list[dict], edges: list[dict], *, include_diagrams: bool) -> list[dict]:
    if not include_diagrams:
        return []

    diagrams: list[dict] = []
    for spec in DEFAULT_DIAGRAM_SPECS:
        result = query_graph.build_diagram_result(
            nodes,
            edges,
            include_types=spec.get("include_types", ""),
            exclude_types=spec.get("exclude_types", ""),
            include_relations=spec.get("include_relations", ""),
            exclude_relations=spec.get("exclude_relations", ""),
            diagram_limit=0,
        )
        if result.get("node_count", 0) == 0 or result.get("edge_count", 0) == 0:
            continue
        mermaid = query_graph.render_output(
            result,
            "mermaid",
            query_label=spec["title"],
            mermaid_direction="LR",
            mermaid_group_by=spec.get("group_by", "none"),
        )
        diagrams.append(
            {
                "title": spec["title"],
                "description": spec["description"],
                "mermaid": mermaid,
            }
        )
    return diagrams


def build_status_rows(
    validation_report: dict | None,
    consistency_report: dict | None,
    incremental_report: dict | None,
) -> list[dict]:
    rows = []
    if validation_report is not None:
        rows.append(
            {
                "artifact": "Graph Validation",
                "status": (
                    f"{validation_report.get('checks_passed', 0)}/"
                    f"{validation_report.get('checks_total', 0)} checks passed"
                ),
                "details": truncate([item.get("check") for item in validation_report.get("results", [])], 180),
            }
        )
    else:
        rows.append({"artifact": "Graph Validation", "status": "missing", "details": "graph-validation.json not found"})

    if consistency_report is not None:
        rows.append(
            {
                "artifact": "Consistency",
                "status": consistency_report.get("status", "unknown"),
                "details": f"{len(consistency_report.get('mismatches', []))} mismatches",
            }
        )
    else:
        rows.append({"artifact": "Consistency", "status": "missing", "details": "consistency-report.json not found"})

    if incremental_report is not None:
        rows.append(
            {
                "artifact": "Incremental Update",
                "status": (
                    f"checked {incremental_report.get('repos_checked', 0)} repos; "
                    f"changed {len(incremental_report.get('repos_changed', []))}; "
                    f"unchanged {len(incremental_report.get('repos_unchanged', []))}"
                ),
                "details": (
                    f"bootstrapped {len(incremental_report.get('repos_bootstrapped', []))}; "
                    f"missing {len(incremental_report.get('repos_not_found', []))}; "
                    f"invalid git {len(incremental_report.get('repos_invalid_git', []))}"
                ),
            }
        )
    else:
        rows.append({"artifact": "Incremental Update", "status": "missing", "details": "incremental-update.json not found"})

    return rows


def metadata_rows(graph_display_path: str, graph: dict, title: str) -> list[list[object]]:
    meta = graph.get("meta", {})
    return [
        ["Title", title],
        ["Graph File", graph_display_path],
        ["Generated At", meta.get("generated_at", "")],
        ["Graph Contract", meta.get("graph_contract_version", "")],
        ["Build Source", meta.get("build_source", "")],
        ["Node Count", len(graph.get("nodes", []))],
        ["Edge Count", len(graph.get("edges", []))],
        ["Base Commit SHAs", len(meta.get("base_commit_shas", {}) or {})],
        ["Portfolio Metrics", truncate(meta.get("portfolio_metrics", {}), 180)],
    ]


def report_payload(
    *,
    graph_path: Path,
    graph: dict,
    graph_display_path: str,
    title: str,
    validation_report: dict | None,
    consistency_report: dict | None,
    incremental_report: dict | None,
    include_diagrams: bool,
) -> dict:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    node_index = build_node_index(nodes)
    return {
        "title": title,
        "graph_path": graph_display_path,
        "metadata_rows": metadata_rows(graph_display_path, graph, title),
        "status_rows": build_status_rows(validation_report, consistency_report, incremental_report),
        "node_counts": count_nodes_by_type(nodes),
        "edge_counts": count_edges_by_relation(edges),
        "top_ranked": top_ranked_nodes(nodes, edges),
        "domain_repo_rows": build_relation_rows(
            edges=edges,
            node_index=node_index,
            relation="contains",
            source_types={"domain"},
            target_types={"repo"},
        ),
        "repo_provider_rows": build_relation_rows(
            edges=edges,
            node_index=node_index,
            relation="uses_provider",
            source_types={"repo"},
            target_types={"provider"},
        ),
        "repo_process_rows": build_relation_rows(
            edges=edges,
            node_index=node_index,
            relation="implements_process",
            source_types={"repo"},
            target_types={"process"},
        ),
        "repo_storage_rows": [
            *build_relation_rows(
                edges=edges,
                node_index=node_index,
                relation="reads_from",
                source_types={"repo"},
            ),
            *build_relation_rows(
                edges=edges,
                node_index=node_index,
                relation="writes_to",
                source_types={"repo"},
            ),
            *build_relation_rows(
                edges=edges,
                node_index=node_index,
                relation="owns_data_in",
                source_types={"repo"},
            ),
        ],
        "diagrams": render_diagrams(nodes, edges, include_diagrams=include_diagrams),
        "grouped_nodes": grouped_node_rows(nodes),
    }


def render_markdown(payload: dict) -> str:
    lines = [f"# {payload['title']}", ""]

    lines.extend(["## Build Metadata", "", format_markdown_table(["Field", "Value"], payload["metadata_rows"]), ""])

    status_rows = [[row["artifact"], row["status"], row["details"]] for row in payload["status_rows"]]
    lines.extend(["## Validation And Freshness", "", format_markdown_table(["Artifact", "Status", "Details"], status_rows), ""])

    node_rows = [[node_type, count] for node_type, count in payload["node_counts"]]
    edge_rows = [[relation, count] for relation, count in payload["edge_counts"]]
    lines.extend(["## Graph Inventory", "", "### Nodes By Type", "", format_markdown_table(["Type", "Count"], node_rows), ""])
    lines.extend(["### Edges By Relation", "", format_markdown_table(["Relation", "Count"], edge_rows), ""])

    ranked_rows = [
        [item["label"], item["type"], item["domain"], item["fan_in"], item["weighted_fan_in"], item["id"]]
        for item in payload["top_ranked"]
    ]
    lines.extend(["## Top Connected Nodes", "", format_markdown_table(["Label", "Type", "Domain", "Fan-In", "Weighted", "ID"], ranked_rows), ""])

    for title, rows in (
        ("Domains To Repositories", payload["domain_repo_rows"]),
        ("Repositories To Providers", payload["repo_provider_rows"]),
        ("Repositories To Processes", payload["repo_process_rows"]),
        ("Repositories To Storage", payload["repo_storage_rows"]),
    ):
        lines.extend([f"## {title}", ""])
        if rows:
            table_rows = [[row["source_label"], row["relation"], row["target_label"], row["target_type"]] for row in rows]
            lines.append(format_markdown_table(["Source", "Relation", "Target", "Target Type"], table_rows))
        else:
            lines.append("_No matching relationships found._")
        lines.append("")

    if payload["diagrams"]:
        lines.extend(["## Diagram Exports", ""])
        for diagram in payload["diagrams"]:
            lines.extend([f"### {diagram['title']}", "", diagram["description"], "", "```mermaid", diagram["mermaid"], "```", ""])

    lines.extend(["## Node Index", ""])
    for node_type, rows in payload["grouped_nodes"]:
        lines.extend([f"<details>", f"<summary>{html_escape(node_type)} ({len(rows)})</summary>", ""])
        table_rows = []
        for node in rows:
            table_rows.append(
                [
                    node.get("label", node.get("id", "")),
                    node.get("id", ""),
                    node.get("domain", ""),
                    truncate(node.get("summary", "")),
                    truncate(node.get("tags", []), 80),
                ]
            )
        lines.append(format_markdown_table(["Label", "ID", "Domain", "Summary", "Tags"], table_rows))
        lines.extend(["", "</details>", ""])

    return "\n".join(lines).rstrip() + "\n"


def render_html(payload: dict) -> str:
    node_type_options = "\n".join(
        f'<option value="{html_escape(node_type)}">{html_escape(node_type)} ({count})</option>'
        for node_type, count in payload["node_counts"]
    )
    node_rows = "\n".join(
        (
            "<tr "
            f'data-type="{html_escape(node.get("type", ""))}" '
            f'data-search="{html_escape(" ".join(filter(None, [safe_text(node.get("id")), safe_text(node.get("label")), safe_text(node.get("summary")), safe_text(node.get("domain")), safe_text(node.get("tags"))])).lower())}">'
            f"<td>{html_escape(node.get('label', node.get('id', '')))}</td>"
            f"<td><code>{html_escape(node.get('id', ''))}</code></td>"
            f"<td>{html_escape(node.get('type', ''))}</td>"
            f"<td>{html_escape(node.get('domain', ''))}</td>"
            f"<td>{html_escape(truncate(node.get('summary', ''), 160))}</td>"
            f"<td>{html_escape(truncate(node.get('tags', []), 120))}</td>"
            "</tr>"
        )
        for _node_type, rows in payload["grouped_nodes"]
        for node in rows
    )

    def rows_html(rows: list[list[object]]) -> str:
        return "\n".join(
            "<tr>" + "".join(f"<td>{html_escape(cell)}</td>" for cell in row) + "</tr>"
            for row in rows
        )

    diagram_sections = []
    for diagram in payload["diagrams"]:
        diagram_sections.append(
            f"""
            <section class="section">
              <h3>{html_escape(diagram['title'])}</h3>
              <p>{html_escape(diagram['description'])}</p>
              <pre class="mermaid-source"><code>{html_escape(diagram['mermaid'])}</code></pre>
            </section>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_escape(payload['title'])}</title>
  <style>
    :root {{
      --bg: #f7f7f3;
      --panel: #ffffff;
      --ink: #172121;
      --muted: #5b6464;
      --line: #d5dddb;
      --accent: #0f766e;
      --accent-soft: #d8f0ee;
      --warning: #92400e;
      --warning-soft: #fef3c7;
      --code-bg: #eff4f3;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #f7f7f3 0%, #edf5f3 100%);
      color: var(--ink);
    }}
    main {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 32px 24px 64px;
    }}
    .hero {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 28px;
      box-shadow: 0 18px 50px rgba(15, 23, 42, 0.06);
      margin-bottom: 24px;
    }}
    h1, h2, h3 {{ margin: 0 0 12px; line-height: 1.1; }}
    p {{ color: var(--muted); }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 20px;
    }}
    .card {{
      background: var(--accent-soft);
      border: 1px solid rgba(15, 118, 110, 0.16);
      border-radius: 16px;
      padding: 16px;
    }}
    .card strong {{
      display: block;
      font-size: 24px;
      margin-top: 6px;
    }}
    .section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 22px;
      margin-bottom: 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
    }}
    code {{
      background: var(--code-bg);
      padding: 2px 6px;
      border-radius: 6px;
    }}
    .controls {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }}
    .controls input, .controls select {{
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      font: inherit;
      min-width: 220px;
      background: white;
    }}
    .mermaid-source {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 16px;
      border-radius: 14px;
      overflow-x: auto;
      white-space: pre-wrap;
    }}
    .badge {{
      display: inline-block;
      background: var(--warning-soft);
      color: var(--warning);
      padding: 4px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      margin-right: 8px;
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <span class="badge">Static report</span>
      <h1>{html_escape(payload['title'])}</h1>
      <p>Generated from <code>{html_escape(payload['graph_path'])}</code>. This report keeps the skill headless while making the graph easy to review locally.</p>
      <div class="cards">
        <div class="card"><span>Node types</span><strong>{len(payload['node_counts'])}</strong></div>
        <div class="card"><span>Edge relations</span><strong>{len(payload['edge_counts'])}</strong></div>
        <div class="card"><span>Total nodes</span><strong>{sum(count for _, count in payload['node_counts'])}</strong></div>
        <div class="card"><span>Total edges</span><strong>{sum(count for _, count in payload['edge_counts'])}</strong></div>
      </div>
    </section>

    <section class="section">
      <h2>Build Metadata</h2>
      <table>
        <thead><tr><th>Field</th><th>Value</th></tr></thead>
        <tbody>{rows_html(payload['metadata_rows'])}</tbody>
      </table>
    </section>

    <section class="section">
      <h2>Validation And Freshness</h2>
      <table>
        <thead><tr><th>Artifact</th><th>Status</th><th>Details</th></tr></thead>
        <tbody>{rows_html([[row['artifact'], row['status'], row['details']] for row in payload['status_rows']])}</tbody>
      </table>
    </section>

    <section class="section">
      <h2>Graph Inventory</h2>
      <div class="cards">
        <div>
          <h3>Nodes By Type</h3>
          <table>
            <thead><tr><th>Type</th><th>Count</th></tr></thead>
            <tbody>{rows_html([[node_type, count] for node_type, count in payload['node_counts']])}</tbody>
          </table>
        </div>
        <div>
          <h3>Edges By Relation</h3>
          <table>
            <thead><tr><th>Relation</th><th>Count</th></tr></thead>
            <tbody>{rows_html([[relation, count] for relation, count in payload['edge_counts']])}</tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Top Connected Nodes</h2>
      <table>
        <thead><tr><th>Label</th><th>Type</th><th>Domain</th><th>Fan-In</th><th>Weighted</th><th>ID</th></tr></thead>
        <tbody>{rows_html([[item['label'], item['type'], item['domain'], item['fan_in'], item['weighted_fan_in'], item['id']] for item in payload['top_ranked']])}</tbody>
      </table>
    </section>

    <section class="section">
      <h2>High-Signal Relationship Slices</h2>
      <h3>Domains To Repositories</h3>
      <table>
        <thead><tr><th>Source</th><th>Relation</th><th>Target</th><th>Target Type</th></tr></thead>
        <tbody>{rows_html([[row['source_label'], row['relation'], row['target_label'], row['target_type']] for row in payload['domain_repo_rows']])}</tbody>
      </table>
      <h3>Repositories To Providers</h3>
      <table>
        <thead><tr><th>Source</th><th>Relation</th><th>Target</th><th>Target Type</th></tr></thead>
        <tbody>{rows_html([[row['source_label'], row['relation'], row['target_label'], row['target_type']] for row in payload['repo_provider_rows']])}</tbody>
      </table>
      <h3>Repositories To Processes</h3>
      <table>
        <thead><tr><th>Source</th><th>Relation</th><th>Target</th><th>Target Type</th></tr></thead>
        <tbody>{rows_html([[row['source_label'], row['relation'], row['target_label'], row['target_type']] for row in payload['repo_process_rows']])}</tbody>
      </table>
    </section>

    {''.join(diagram_sections)}

    <section class="section">
      <h2>Node Index</h2>
      <div class="controls">
        <input id="nodeSearch" type="search" placeholder="Search labels, ids, summaries, domains, tags">
        <select id="nodeTypeFilter">
          <option value="">All node types</option>
          {node_type_options}
        </select>
      </div>
      <table id="nodeTable">
        <thead>
          <tr>
            <th>Label</th>
            <th>ID</th>
            <th>Type</th>
            <th>Domain</th>
            <th>Summary</th>
            <th>Tags</th>
          </tr>
        </thead>
        <tbody>
          {node_rows}
        </tbody>
      </table>
    </section>
  </main>
  <script>
    const searchInput = document.getElementById('nodeSearch');
    const typeFilter = document.getElementById('nodeTypeFilter');
    const rows = Array.from(document.querySelectorAll('#nodeTable tbody tr'));

    function applyFilters() {{
      const query = (searchInput.value || '').trim().toLowerCase();
      const type = typeFilter.value;
      for (const row of rows) {{
        const matchesQuery = !query || row.dataset.search.includes(query);
        const matchesType = !type || row.dataset.type === type;
        row.style.display = matchesQuery && matchesType ? '' : 'none';
      }}
    }}

    searchInput.addEventListener('input', applyFilters);
    typeFilter.addEventListener('change', applyFilters);
  </script>
</body>
</html>
"""


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate static HTML and Markdown reports from a knowledge graph.")
    parser.add_argument("graph", help="Path to knowledge-graph.json")
    parser.add_argument("--output-dir", help="Directory for generated report files (default: sibling reports/ directory)")
    parser.add_argument("--title", help="Optional report title override")
    parser.add_argument("--validation", help="Optional path to graph-validation.json")
    parser.add_argument("--consistency", help="Optional path to consistency-report.json")
    parser.add_argument("--incremental", help="Optional path to incremental-update.json")
    parser.add_argument("--skip-diagrams", action="store_true", help="Skip Mermaid diagram sections")

    args = parser.parse_args()

    graph_path = Path(args.graph).resolve()
    if not graph_path.exists():
        print(f"Error: graph not found: {graph_path}", file=sys.stderr)
        return 1

    graph = load_json(graph_path)
    reports_dir = default_reports_dir(graph_path)
    output_dir = Path(args.output_dir).resolve() if args.output_dir else reports_dir.resolve()

    validation_path = Path(args.validation).resolve() if args.validation else (reports_dir / "graph-validation.json").resolve()
    consistency_path = Path(args.consistency).resolve() if args.consistency else (reports_dir / "consistency-report.json").resolve()
    incremental_path = Path(args.incremental).resolve() if args.incremental else (reports_dir / "incremental-update.json").resolve()

    validation_report = load_optional_json(validation_path)
    consistency_report = load_optional_json(consistency_path)
    incremental_report = load_optional_json(incremental_path)

    title = args.title or default_title(graph_path, graph)
    graph_display_path = Path("..") / "graphs" / graph_path.name if output_dir.name == "reports" and graph_path.parent.name == "graphs" else Path(relative_display_path(graph_path, output_dir))
    payload = report_payload(
        graph_path=graph_path,
        graph=graph,
        graph_display_path=str(graph_display_path),
        title=title,
        validation_report=validation_report,
        consistency_report=consistency_report,
        incremental_report=incremental_report,
        include_diagrams=not args.skip_diagrams,
    )

    html_path = output_dir / "graph-report.html"
    markdown_path = output_dir / "graph-report.md"
    write_output(html_path, render_html(payload))
    write_output(markdown_path, render_markdown(payload))

    print(json.dumps(
        {
            "graph": str(graph_path),
            "html": str(html_path),
            "markdown": str(markdown_path),
            "diagrams_included": not args.skip_diagrams,
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
