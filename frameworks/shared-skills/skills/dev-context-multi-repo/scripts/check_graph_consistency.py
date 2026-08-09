#!/usr/bin/env python3
"""
Compare hub source documents against a knowledge graph build and emit a consistency report.

Usage:
  python3 check_graph_consistency.py --hub /path/to/hub --graph /path/to/knowledge-graph.json
  python3 check_graph_consistency.py --hub /path/to/hub --graph /path/to/knowledge-graph.json --output report.json
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def report_path_value(path_value: str | None, report_path: str | None) -> str | None:
    if not path_value:
        return path_value
    if not report_path:
        return str(Path(path_value))
    anchor = Path(report_path).resolve().parent
    try:
        return os.path.relpath(Path(path_value).resolve(), start=anchor)
    except ValueError:
        return str(Path(path_value).resolve())


def report_for_output(report: dict, output_path: str | None) -> dict:
    rendered = dict(report)
    rendered["hub"] = report_path_value(rendered.get("hub"), output_path)
    rendered["graph"] = report_path_value(rendered.get("graph"), output_path)
    rendered["missing_last_verified"] = [
        report_path_value(value, output_path) for value in rendered.get("missing_last_verified", [])
    ]
    facts = dict(rendered.get("facts", {}))
    source_files = facts.get("source_files_newer_than_graph")
    if isinstance(source_files, list):
        facts["source_files_newer_than_graph"] = [
            report_path_value(value, output_path) for value in source_files
        ]
    rendered["facts"] = facts
    return rendered


def normalize_id(label: str) -> str:
    return re.sub(r"[^a-z0-9._-]", "-", label.lower().strip()).strip("-")


def artifact_node_id(relative_path: str) -> str:
    return f"artifact-{normalize_id(relative_path)}"


def parse_markdown_tables(content: str) -> list[dict[str, str]]:
    rows = []
    headers: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            headers = []
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(re.match(r"^:?-{1,}:?$", cell) for cell in cells if cell):
            continue
        if not headers:
            headers = cells
            continue
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))
        rows.append({headers[i]: cells[i] for i in range(len(headers))})
    return rows


def find_col(row_lower: dict[str, str], candidates: list[str]) -> str:
    for candidate in candidates:
        if candidate in row_lower:
            return row_lower[candidate]
    for candidate in candidates:
        for key, value in row_lower.items():
            if candidate in key:
                return value
    return ""


def parse_int_maybe(raw: str) -> int | None:
    if not raw:
        return None
    match = re.search(r"([0-9]+)", raw.replace(",", ""))
    return int(match.group(1)) if match else None


def has_last_verified(path: Path) -> bool:
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8", errors="replace")
    return bool(re.search(r"<!--\s*last_verified:\s*[0-9]{4}-[0-9]{2}-[0-9]{2}\s*-->", content))


def parse_iso_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    normalized = raw.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_graph(graph_path: Path) -> tuple[dict, list[dict], list[dict], dict[str, dict]]:
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    node_index = {node["id"]: node for node in nodes if "id" in node}
    return data.get("meta", {}), nodes, edges, node_index


def count_api_catalog_json(path: Path) -> dict[str, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    services = 0
    endpoint_rows = 0
    unique_endpoint_keys: set[tuple[str, str, str]] = set()
    domains = len(data.get("domains", []))
    for domain in data.get("domains", []):
        for service in domain.get("services", []):
            services += 1
            repo = service.get("repo") or service.get("title") or service.get("name") or ""
            for endpoint in service.get("endpoints", []):
                endpoint_rows += 1
                unique_endpoint_keys.add((
                    repo,
                    str(endpoint.get("method", "")).upper(),
                    endpoint.get("path", ""),
                ))

    unique_endpoints = len(unique_endpoint_keys)
    return {
        "domains": domains,
        "services": services,
        "endpoints": unique_endpoints,
        "endpoint_rows": endpoint_rows,
        "unique_endpoints": unique_endpoints,
        "duplicate_endpoint_rows": max(0, endpoint_rows - unique_endpoints),
    }


def count_api_catalog_md(path: Path) -> dict[str, int]:
    rows = parse_markdown_tables(path.read_text(encoding="utf-8"))
    total_services = 0
    total_endpoints = 0
    domains = 0
    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        domain = find_col(row_lower, ["domain"])
        services = parse_int_maybe(find_col(row_lower, ["services"]))
        endpoints = parse_int_maybe(find_col(row_lower, ["endpoints"]))
        if domain and services is not None and endpoints is not None:
            if domain.strip("* ").lower() != "total":
                domains += 1
                total_services += services
                total_endpoints += endpoints
    return {"domains": domains, "services": total_services, "endpoints": total_endpoints}


def count_process_catalog(path: Path) -> dict[str, int]:
    content = path.read_text(encoding="utf-8")
    plain = content.replace("**", "")

    summary_scope_match = re.search(r"Scope:\s*([0-9]+)\s+processes", plain)
    executive_match = re.search(r"operates\s+([0-9]+)\s+business processes", plain)

    inventory_match = re.search(
        r"^##\s+2\.\s+Process Inventory\s*(.*?)(?=^---\s*$|^##\s+3\.)",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    inventory_section = inventory_match.group(1) if inventory_match else content
    inventory_rows = parse_markdown_tables(inventory_section)

    inventory_ids: list[str] = []
    for row in inventory_rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        process_id = row_lower.get("id", "")
        if re.fullmatch(r"PRO-\d+", process_id):
            inventory_ids.append(process_id)

    unique_inventory_ids = sorted(set(inventory_ids))
    summary_scope = parse_int_maybe(summary_scope_match.group(1)) if summary_scope_match else 0
    executive_count = parse_int_maybe(executive_match.group(1)) if executive_match else 0
    return {
        "inventory_rows": len(inventory_ids),
        "unique_process_ids": len(unique_inventory_ids),
        "summary_scope_processes": summary_scope or 0,
        "executive_processes": executive_count or 0,
    }


def count_platform_summary(path: Path) -> dict[str, int]:
    rows = parse_markdown_tables(path.read_text(encoding="utf-8"))
    metrics: dict[str, int] = {}
    repo_names: set[str] = set()

    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        metric = find_col(row_lower, ["metric"])
        value = find_col(row_lower, ["value"])

        if metric and value:
            key = metric.lower()
            if "total repositories" in key:
                metrics["repo_count"] = parse_int_maybe(value) or 0
            elif "services" in key and "api" not in key:
                metrics["service_count"] = parse_int_maybe(value) or 0
            elif "external providers" in key:
                metrics["provider_count"] = parse_int_maybe(value) or 0
            elif "business processes" in key:
                metrics["process_count"] = parse_int_maybe(value) or 0
            elif "documented gaps" in key:
                metrics["gap_count"] = parse_int_maybe(value) or 0
            continue

        repo = row_lower.get("repository", "").strip().strip("`")
        loc = row_lower.get("loc")
        primary_language = row_lower.get("primary language")
        repo_type = row_lower.get("type")
        domain = row_lower.get("domain")
        if repo and loc is not None and primary_language is not None and repo_type is not None and domain is not None:
            if not repo.startswith("**"):
                repo_names.add(repo)

    metrics["repository_rows"] = len(repo_names)
    return metrics


def count_integration_providers(path: Path) -> dict[str, int]:
    rows = parse_markdown_tables(path.read_text(encoding="utf-8"))
    provider_names: set[str] = set()
    row_count = 0
    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        provider = find_col(row_lower, ["provider"]).strip()
        repo = find_col(row_lower, ["repo", "used by"]).strip()
        if provider and repo and not provider.startswith("**"):
            provider_names.add(provider)
            row_count += 1
    return {"row_count": row_count, "unique_providers": len(provider_names)}


def count_readme_domains(path: Path) -> int:
    rows = parse_markdown_tables(path.read_text(encoding="utf-8"))
    count = 0
    for row in rows:
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        domain = find_col(row_lower, ["domain"])
        repos = find_col(row_lower, ["repos"])
        if domain and repos and domain.strip("* ").lower() != "total":
            count += 1
    return count


def build_document_index(node_index: dict[str, dict], edges: list[dict]) -> dict[str, set[str]]:
    documented_targets: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if edge.get("relation") != "documents":
            continue
        source_id = edge.get("source")
        target_id = edge.get("target")
        if not source_id or not target_id:
            continue
        source_node = node_index.get(source_id)
        if source_node and source_node.get("type") == "artifact":
            documented_targets[source_id].add(target_id)
    return documented_targets


def count_documented_targets(
    relative_artifact_path: str,
    node_type: str,
    node_index: dict[str, dict],
    documented_targets: dict[str, set[str]],
) -> int:
    artifact_id = artifact_node_id(relative_artifact_path)
    return sum(
        1
        for target_id in documented_targets.get(artifact_id, set())
        if node_index.get(target_id, {}).get("type") == node_type
    )


def artifact_paths_without_documents(
    node_index: dict[str, dict],
    documented_targets: dict[str, set[str]],
    edges: list[dict],
) -> list[str]:
    incoming_documents: set[str] = set()
    for edge in edges:
        if edge.get("relation") == "documents" and edge.get("target"):
            incoming_documents.add(edge["target"])

    missing = []
    for node in node_index.values():
        if node.get("type") != "artifact":
            continue
        if documented_targets.get(node["id"]) or node["id"] in incoming_documents:
            continue
        artifact_kind = node.get("properties", {}).get("artifact_kind")
        if artifact_kind == "overview-document":
            continue
        rel_path = node.get("properties", {}).get("path") or node.get("label")
        missing.append(rel_path)
    return sorted(missing)


def source_files_newer_than_graph(graph_generated_at: datetime | None, paths: list[Path]) -> list[str]:
    if not graph_generated_at:
        return []
    newer = []
    for path in paths:
        if not path.exists():
            continue
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if mtime > graph_generated_at:
            newer.append(str(path))
    return sorted(newer)


def ratio(numerator: int | None, denominator: int | None) -> float | None:
    if denominator in (None, 0) or numerator is None:
        return None
    return round(numerator / denominator, 3)


def main():
    parser = argparse.ArgumentParser(description="Check consistency between hub source docs and a knowledge graph build.")
    parser.add_argument("--hub", required=True, help="Path to the requirements-hub directory")
    parser.add_argument("--graph", required=True, help="Path to the knowledge-graph.json file")
    parser.add_argument("--output", help="Optional path to write the JSON report")
    args = parser.parse_args()

    hub_dir = Path(args.hub).resolve()
    graph_path = Path(args.graph).resolve()
    if not hub_dir.is_dir():
        print(f"Error: hub directory not found: {hub_dir}", file=sys.stderr)
        sys.exit(1)
    if not graph_path.exists():
        print(f"Error: graph not found: {graph_path}", file=sys.stderr)
        sys.exit(1)

    meta, nodes, edges, node_index = load_graph(graph_path)
    node_types = Counter(node.get("type", "unknown") for node in nodes)
    documented_targets = build_document_index(node_index, edges)

    overview_dir = hub_dir / "overview"
    readme = overview_dir / "README.md"
    api_json = overview_dir / "api-catalog.json"
    api_md = overview_dir / "api-catalog.md"
    process_md = overview_dir / "process-catalog.md"
    platform_summary = overview_dir / "platform-summary.md"
    integration_matrix = overview_dir / "integration-matrix.md"
    validation_report = hub_dir / "reports" / "graph-validation.json"

    tracked_source_files = [
        readme,
        api_json,
        api_md,
        overview_dir / "database-schemas.md",
        overview_dir / "data-catalog.md",
        overview_dir / "full-system-diagram.md",
        integration_matrix,
        overview_dir / "infrastructure-matrix.md",
        overview_dir / "messaging-topology.md",
        overview_dir / "nuget-dependency-map.md",
        platform_summary,
        process_md,
    ]

    graph_generated_at = parse_iso_datetime(meta.get("generated_at"))
    artifact_gaps = artifact_paths_without_documents(node_index, documented_targets, edges)

    graph_facts = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "repo_nodes": node_types.get("repo", 0),
        "domain_nodes": node_types.get("domain", 0),
        "provider_nodes": node_types.get("provider", 0),
        "process_nodes": node_types.get("process", 0),
        "artifact_nodes": node_types.get("artifact", 0),
        "api_endpoint_nodes": node_types.get("api_endpoint", 0),
        "documented_by_api_catalog": {
            "domains": count_documented_targets("overview/api-catalog.json", "domain", node_index, documented_targets),
            "repos": count_documented_targets("overview/api-catalog.json", "repo", node_index, documented_targets),
            "api_endpoints": count_documented_targets("overview/api-catalog.json", "api_endpoint", node_index, documented_targets),
        },
        "documented_by_platform_summary": {
            "repos": count_documented_targets("overview/platform-summary.md", "repo", node_index, documented_targets),
        },
        "documented_by_integration_matrix": {
            "providers": count_documented_targets("overview/integration-matrix.md", "provider", node_index, documented_targets),
            "repos": count_documented_targets("overview/integration-matrix.md", "repo", node_index, documented_targets),
        },
        "documented_by_process_catalog": {
            "processes": count_documented_targets("overview/process-catalog.md", "process", node_index, documented_targets),
            "repos": count_documented_targets("overview/process-catalog.md", "repo", node_index, documented_targets),
            "providers": count_documented_targets("overview/process-catalog.md", "provider", node_index, documented_targets),
        },
        "artifacts_without_documents": artifact_gaps,
    }

    api_catalog_json_counts = count_api_catalog_json(api_json) if api_json.exists() else {}
    api_catalog_md_counts = count_api_catalog_md(api_md) if api_md.exists() else {}
    process_catalog_counts = count_process_catalog(process_md) if process_md.exists() else {}
    platform_summary_counts = count_platform_summary(platform_summary) if platform_summary.exists() else {}
    integration_matrix_counts = count_integration_providers(integration_matrix) if integration_matrix.exists() else {}

    facts = {
        "overview_readme_domains": count_readme_domains(readme) if readme.exists() else None,
        "api_catalog_json": api_catalog_json_counts,
        "api_catalog_md": api_catalog_md_counts,
        "process_catalog": process_catalog_counts,
        "platform_summary": platform_summary_counts,
        "integration_matrix": integration_matrix_counts,
        "graph": graph_facts,
        "coverage": {
            "api_endpoint_ratio": ratio(
                graph_facts["documented_by_api_catalog"]["api_endpoints"],
                api_catalog_json_counts.get("unique_endpoints"),
            ),
            "process_ratio": ratio(
                graph_facts["documented_by_process_catalog"]["processes"],
                process_catalog_counts.get("unique_process_ids"),
            ),
            "provider_ratio": ratio(
                graph_facts["documented_by_integration_matrix"]["providers"],
                integration_matrix_counts.get("unique_providers"),
            ),
            "platform_summary_repo_ratio": ratio(
                graph_facts["documented_by_platform_summary"]["repos"],
                platform_summary_counts.get("repository_rows"),
            ),
        },
        "base_commit_shas_present": bool(meta.get("base_commit_shas")),
        "validation_report_present": validation_report.exists(),
        "source_files_newer_than_graph": source_files_newer_than_graph(graph_generated_at, tracked_source_files),
    }

    mismatches = []

    api_json_endpoints = facts["api_catalog_json"].get("unique_endpoints")
    api_json_rows = facts["api_catalog_json"].get("endpoint_rows")
    graph_api_endpoints = facts["graph"]["documented_by_api_catalog"]["api_endpoints"]
    if api_json_endpoints is not None and api_json_endpoints != graph_api_endpoints:
        mismatches.append({
            "check": "api_json_unique_vs_graph_endpoint_count",
            "expected": api_json_endpoints,
            "actual": graph_api_endpoints,
        })

    if api_json_rows is not None and api_json_endpoints is not None and api_json_rows != api_json_endpoints:
        mismatches.append({
            "check": "api_json_raw_vs_unique_endpoint_count",
            "expected": api_json_endpoints,
            "actual": api_json_rows,
        })

    api_md_endpoints = facts["api_catalog_md"].get("endpoints")
    if api_md_endpoints is not None and api_json_endpoints is not None and api_md_endpoints != api_json_endpoints:
        mismatches.append({
            "check": "api_markdown_vs_json_unique_endpoint_count",
            "expected": api_json_endpoints,
            "actual": api_md_endpoints,
        })

    readme_domains = facts.get("overview_readme_domains")
    if readme_domains is not None and readme_domains != facts["graph"]["domain_nodes"]:
        mismatches.append({
            "check": "overview_readme_vs_graph_domain_count",
            "expected": readme_domains,
            "actual": facts["graph"]["domain_nodes"],
        })

    process_unique = facts["process_catalog"].get("unique_process_ids")
    graph_processes = facts["graph"]["documented_by_process_catalog"]["processes"]
    if process_unique is not None and process_unique != graph_processes:
        mismatches.append({
            "check": "process_catalog_vs_graph_process_count",
            "expected": process_unique,
            "actual": graph_processes,
        })

    process_scope = facts["process_catalog"].get("summary_scope_processes")
    if process_scope is not None and process_unique is not None and process_scope != process_unique:
        mismatches.append({
            "check": "process_scope_vs_inventory_count",
            "expected": process_unique,
            "actual": process_scope,
        })

    process_exec = facts["process_catalog"].get("executive_processes")
    if process_exec is not None and process_unique is not None and process_exec != process_unique:
        mismatches.append({
            "check": "process_executive_vs_inventory_count",
            "expected": process_unique,
            "actual": process_exec,
        })

    integration_provider_count = facts["integration_matrix"].get("unique_providers")
    graph_provider_count = facts["graph"]["documented_by_integration_matrix"]["providers"]
    if integration_provider_count is not None and integration_provider_count != graph_provider_count:
        mismatches.append({
            "check": "integration_matrix_vs_graph_provider_count",
            "expected": integration_provider_count,
            "actual": graph_provider_count,
        })

    platform_summary_repo_metric = facts["platform_summary"].get("repo_count")
    platform_summary_repo_rows = facts["platform_summary"].get("repository_rows")
    if platform_summary_repo_metric is not None and platform_summary_repo_rows is not None and platform_summary_repo_metric != platform_summary_repo_rows:
        mismatches.append({
            "check": "platform_summary_metric_vs_repo_rows",
            "expected": platform_summary_repo_metric,
            "actual": platform_summary_repo_rows,
        })

    graph_platform_summary_repos = facts["graph"]["documented_by_platform_summary"]["repos"]
    if platform_summary_repo_rows is not None and platform_summary_repo_rows != graph_platform_summary_repos:
        mismatches.append({
            "check": "platform_summary_repo_rows_vs_graph_coverage",
            "expected": platform_summary_repo_rows,
            "actual": graph_platform_summary_repos,
        })

    summary_process_count = facts["platform_summary"].get("process_count")
    if summary_process_count is not None and process_unique is not None and summary_process_count != process_unique:
        mismatches.append({
            "check": "platform_summary_vs_process_catalog_count",
            "expected": process_unique,
            "actual": summary_process_count,
        })

    if not facts["base_commit_shas_present"]:
        mismatches.append({
            "check": "base_commit_shas_present",
            "expected": True,
            "actual": False,
        })

    if not facts["validation_report_present"]:
        mismatches.append({
            "check": "validation_report_present",
            "expected": True,
            "actual": False,
        })

    if artifact_gaps:
        mismatches.append({
            "check": "artifact_document_coverage",
            "expected": 0,
            "actual": len(artifact_gaps),
        })

    if facts["source_files_newer_than_graph"]:
        mismatches.append({
            "check": "source_files_newer_than_graph",
            "expected": 0,
            "actual": len(facts["source_files_newer_than_graph"]),
        })

    last_verified_markdown_files = [
        readme,
        api_md,
        overview_dir / "database-schemas.md",
        overview_dir / "data-catalog.md",
        overview_dir / "full-system-diagram.md",
        integration_matrix,
        overview_dir / "infrastructure-matrix.md",
        overview_dir / "messaging-topology.md",
        overview_dir / "nuget-dependency-map.md",
        platform_summary,
        process_md,
    ]

    missing_last_verified = []
    for path in last_verified_markdown_files:
        if path.exists() and not has_last_verified(path):
            missing_last_verified.append(str(path))

    report = {
        "hub": str(hub_dir),
        "graph": str(graph_path),
        "facts": facts,
        "missing_last_verified": missing_last_verified,
        "mismatches": mismatches,
        "status": "ok" if not mismatches and not missing_last_verified else "attention",
    }

    output_report = report_for_output(report, args.output)
    rendered = json.dumps(output_report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")

    sys.exit(0 if report["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
