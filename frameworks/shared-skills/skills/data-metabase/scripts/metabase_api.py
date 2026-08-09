#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any


USER_AGENT = "data-metabase-skill/1.2"


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise SystemExit(f"Missing required env var: {key}")
    return value


def _base_url() -> str:
    return _require_env("METABASE_URL").rstrip("/")


def _parse_json(raw: bytes) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _request_with_retry(
    method: str, url: str, headers: dict[str, str], data: bytes | None
) -> tuple[int, Any, bytes, str]:
    """Send one HTTP request, retrying on 429 and 5xx up to 3 times with exponential backoff."""
    max_retries = 3
    delay = 1.0
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                payload = _parse_json(raw) if "json" in content_type else None
                return resp.status, payload, raw, content_type
        except urllib.error.HTTPError as err:
            raw = err.read() if hasattr(err, "read") else b""
            content_type = err.headers.get("Content-Type", "") if err.headers else ""
            payload = _parse_json(raw) if "json" in content_type else None
            if err.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                retry_after = err.headers.get("Retry-After") if err.headers else None
                wait = float(retry_after) if retry_after and retry_after.isdigit() else delay
                time.sleep(wait)
                delay *= 2
                continue
            return err.code, payload, raw, content_type
        except urllib.error.URLError as err:
            raise SystemExit(f"Request failed for {method} {url}: {err}") from err
    # unreachable, but satisfies type checkers
    raise SystemExit(f"Request failed after {max_retries} retries: {method} {url}")


def _request(
    method: str, path: str, headers: dict[str, str], body: Any | None = None
) -> tuple[int, Any, bytes, str]:
    url = f"{_base_url()}{path}"
    data = None
    final_headers = {"Accept": "application/json", "User-Agent": USER_AGENT, **headers}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        final_headers["Content-Type"] = "application/json"
    return _request_with_retry(method, url, final_headers, data)


def _error_detail(payload: Any, raw: bytes) -> str:
    if payload is not None:
        return json.dumps(payload, ensure_ascii=False)[:1000]
    return raw[:500].decode("utf-8", errors="replace")


def _ensure_status(context: str, status: int, payload: Any, raw: bytes, expected: tuple[int, ...]) -> None:
    if status not in expected:
        raise SystemExit(f"{context} failed with status {status}: {_error_detail(payload, raw)}")


def _write_bytes(path: str, raw: bytes) -> None:
    with open(path, "wb") as handle:
        handle.write(raw)


def _write_json(path: str, value: Any) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def _emit(value: Any, *, out: str | None = None, raw: bytes | None = None) -> None:
    if out:
        if raw is not None:
            _write_bytes(out, raw)
        else:
            _write_json(out, value)
        print(out)
        return
    if raw is not None and value is None:
        sys.stdout.write(raw.decode("utf-8", errors="replace"))
        return
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _auth_candidates() -> list[tuple[str, dict[str, str]]]:
    candidates: list[tuple[str, dict[str, str]]] = []

    api_key = os.getenv("METABASE_API_KEY")
    if api_key:
        candidates.append(("api_key_x_api_key", {"X-API-KEY": api_key}))
        candidates.append(("api_key_bearer", {"Authorization": f"Bearer {api_key}"}))

    session = os.getenv("METABASE_SESSION")
    if session:
        candidates.append(("session_env", {"X-Metabase-Session": session}))

    username = os.getenv("METABASE_USERNAME")
    password = os.getenv("METABASE_PASSWORD")
    if username and password:
        status, payload, _, _ = _request("POST", "/api/session", {}, {"username": username, "password": password})
        if status == 200 and isinstance(payload, dict) and payload.get("id"):
            candidates.append(("session_login", {"X-Metabase-Session": str(payload["id"])}))

    return candidates


def _pick_auth_headers() -> tuple[str, dict[str, str]]:
    for name, headers in _auth_candidates():
        status, payload, _, _ = _request("GET", "/api/user/current", headers)
        if status == 200 and isinstance(payload, dict) and payload.get("id"):
            return name, headers
    raise SystemExit(
        "Authentication failed. Set METABASE_URL and either METABASE_API_KEY, METABASE_SESSION, "
        "or METABASE_USERNAME+METABASE_PASSWORD."
    )


def _authed_request(method: str, path: str, body: Any | None = None) -> tuple[str, int, Any, bytes, str]:
    auth_method, headers = _pick_auth_headers()
    status, payload, raw, content_type = _request(method, path, headers, body)
    if status == 401:
        auth_method, headers = _pick_auth_headers()
        status, payload, raw, content_type = _request(method, path, headers, body)
    return auth_method, status, payload, raw, content_type


def _load_json_value(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_json_object(path: str) -> dict[str, Any]:
    value = _load_json_value(path)
    if not isinstance(value, dict):
        raise SystemExit(f"Expected a JSON object in {path}")
    return value


def _validate_card_spec(spec: dict[str, Any]) -> None:
    is_update = bool(spec.get("id"))
    if is_update:
        return
    required = ("name", "dataset_query")
    missing = [key for key in required if key not in spec]
    if missing:
        raise SystemExit(f"Card create spec is missing required keys: {', '.join(missing)}")


def _validate_dashboard_spec(spec: dict[str, Any]) -> None:
    is_update = bool(spec.get("id"))
    if is_update:
        return
    if "name" not in spec:
        raise SystemExit("Dashboard create spec is missing required key: name")


def _print_dry_run(action: str, endpoint: str, payload: Any) -> None:
    print(
        json.dumps(
            {"dry_run": True, "action": action, "endpoint": endpoint, "payload": payload},
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_health(_: argparse.Namespace) -> None:
    status, payload, raw, _ = _request("GET", "/api/util/health", {})
    _ensure_status("health", status, payload, raw, (200,))
    if payload is not None:
        _emit(payload)
        return
    _emit(None, raw=raw)


def cmd_whoami(_: argparse.Namespace) -> None:
    auth_method, status, payload, raw, _ = _authed_request("GET", "/api/user/current")
    _ensure_status("whoami", status, payload, raw, (200,))
    _emit({"auth_method": auth_method, "user": payload})


def cmd_export_card(args: argparse.Namespace) -> None:
    _, status, payload, raw, _ = _authed_request("GET", f"/api/card/{args.id}")
    _ensure_status("export-card", status, payload, raw, (200,))
    _emit(payload, out=args.out)


def cmd_export_dashboard(args: argparse.Namespace) -> None:
    _, status, payload, raw, _ = _authed_request("GET", f"/api/dashboard/{args.id}")
    _ensure_status("export-dashboard", status, payload, raw, (200,))
    _emit(payload, out=args.out)


def cmd_list_collections(args: argparse.Namespace) -> None:
    path = "/api/collection/tree" if args.tree else "/api/collection"
    _, status, payload, raw, _ = _authed_request("GET", path)
    _ensure_status("list-collections", status, payload, raw, (200,))
    _emit(payload)


def cmd_list_databases(_: argparse.Namespace) -> None:
    _, status, payload, raw, _ = _authed_request("GET", "/api/database")
    _ensure_status("list-databases", status, payload, raw, (200,))
    _emit(payload)


def cmd_database_metadata(args: argparse.Namespace) -> None:
    _, status, payload, raw, _ = _authed_request("GET", f"/api/database/{args.id}/metadata")
    _ensure_status("database-metadata", status, payload, raw, (200,))
    _emit(payload)


def cmd_list_fields(args: argparse.Namespace) -> None:
    _, status, payload, raw, _ = _authed_request("GET", f"/api/database/{args.database_id}/metadata")
    _ensure_status("list-fields", status, payload, raw, (200,))
    if not isinstance(payload, dict):
        raise SystemExit("list-fields expected a metadata object response")

    rows: list[dict[str, Any]] = []
    for table in payload.get("tables", []) or []:
        if args.table_id and table.get("id") != args.table_id:
            continue
        for field in table.get("fields", []) or []:
            rows.append(
                {
                    "table_id": table.get("id"),
                    "table_name": table.get("name"),
                    "schema": table.get("schema"),
                    "field_id": field.get("id"),
                    "field_name": field.get("name"),
                    "display_name": field.get("display_name"),
                    "base_type": field.get("base_type"),
                    "semantic_type": field.get("semantic_type"),
                }
            )
    _emit(rows)


def cmd_upsert_card(args: argparse.Namespace) -> None:
    spec = _load_json_object(args.spec)
    _validate_card_spec(spec)

    card_id = spec.get("id")
    if card_id:
        payload = {key: value for key, value in spec.items() if key != "id"}
        if args.dry_run:
            _print_dry_run("update_card", f"/api/card/{card_id}", payload)
            return
        _, status, result, raw, _ = _authed_request("PUT", f"/api/card/{card_id}", payload)
        _ensure_status("upsert-card update", status, result, raw, (200, 202))
        _emit({"action": "updated", "id": card_id, "result": result})
        return

    if args.dry_run:
        _print_dry_run("create_card", "/api/card", spec)
        return
    _, status, result, raw, _ = _authed_request("POST", "/api/card", spec)
    _ensure_status("upsert-card create", status, result, raw, (200, 201))
    _emit({"action": "created", "result": result})


def cmd_upsert_dashboard(args: argparse.Namespace) -> None:
    spec = _load_json_object(args.spec)
    _validate_dashboard_spec(spec)

    dashboard_id = spec.get("id")
    if dashboard_id:
        payload = {key: value for key, value in spec.items() if key != "id"}
        if args.dry_run:
            _print_dry_run("update_dashboard", f"/api/dashboard/{dashboard_id}", payload)
            return
        _, status, result, raw, _ = _authed_request("PUT", f"/api/dashboard/{dashboard_id}", payload)
        _ensure_status("upsert-dashboard update", status, result, raw, (200, 202))
        _emit({"action": "updated", "id": dashboard_id, "result": result})
        return

    if args.dry_run:
        _print_dry_run("create_dashboard", "/api/dashboard", spec)
        return
    _, status, result, raw, _ = _authed_request("POST", "/api/dashboard", spec)
    _ensure_status("upsert-dashboard create", status, result, raw, (200, 201))
    _emit({"action": "created", "result": result})


def cmd_add_dashcard(args: argparse.Namespace) -> None:
    spec = _load_json_object(args.spec)
    endpoint = f"/api/dashboard/{args.dashboard_id}/cards"
    if args.dry_run:
        _print_dry_run("add_dashcard", endpoint, spec)
        return
    _, status, result, raw, _ = _authed_request("POST", endpoint, spec)
    _ensure_status("add-dashcard", status, result, raw, (200, 201, 202))
    _emit(result)


def cmd_update_dashcards(args: argparse.Namespace) -> None:
    payload = _load_json_value(args.spec)
    if isinstance(payload, list):
        payload = {"cards": payload}
    if not isinstance(payload, dict):
        raise SystemExit("update-dashcards spec must be a JSON object or array")
    endpoint = f"/api/dashboard/{args.dashboard_id}/cards"
    if args.dry_run:
        _print_dry_run("update_dashcards", endpoint, payload)
        return
    _, status, result, raw, _ = _authed_request("PUT", endpoint, payload)
    _ensure_status("update-dashcards", status, result, raw, (200, 202))
    _emit(result)


def cmd_remove_dashcard(args: argparse.Namespace) -> None:
    endpoint = f"/api/dashboard/{args.dashboard_id}/cards/{args.dashcard_id}"
    if args.dry_run:
        _print_dry_run("remove_dashcard", endpoint, None)
        return
    _, status, result, raw, _ = _authed_request("DELETE", endpoint)
    _ensure_status("remove-dashcard", status, result, raw, (200, 202, 204))
    _emit({"removed": True, "dashboard_id": args.dashboard_id, "dashcard_id": args.dashcard_id, "result": result})


def cmd_run_query(args: argparse.Namespace) -> None:
    spec = _load_json_object(args.spec)
    if args.dry_run:
        _print_dry_run("run_query", "/api/dataset", spec)
        return
    _, status, payload, raw, _ = _authed_request("POST", "/api/dataset", spec)
    _ensure_status("run-query", status, payload, raw, (200, 202))
    _emit(payload, out=args.out, raw=None if args.out is None else raw)


def cmd_export_card_query(args: argparse.Namespace) -> None:
    body: Any = {}
    if args.parameters:
        params = _load_json_value(args.parameters)
        body = params if isinstance(params, dict) else {"parameters": params}
    endpoint = f"/api/card/{args.id}/query/{args.format}"
    if args.dry_run:
        _print_dry_run("export_card_query", endpoint, body)
        return
    _, status, payload, raw, content_type = _authed_request("POST", endpoint, body)
    _ensure_status("export-card-query", status, payload, raw, (200, 202))
    if args.out:
        _emit(payload, out=args.out, raw=raw)
        return
    if "json" in content_type and payload is not None:
        _emit(payload)
        return
    _emit(None, raw=raw)


def cmd_sync_schema(args: argparse.Namespace) -> None:
    endpoint = f"/api/database/{args.id}/sync_schema"
    if args.dry_run:
        _print_dry_run("sync_schema", endpoint, {})
        return
    _, status, payload, raw, _ = _authed_request("POST", endpoint, {})
    _ensure_status("sync-schema", status, payload, raw, (200, 202))
    _emit(payload if payload is not None else {"queued": True, "database_id": args.id})


def cmd_rescan_values(args: argparse.Namespace) -> None:
    endpoint = f"/api/database/{args.id}/rescan_values"
    if args.dry_run:
        _print_dry_run("rescan_values", endpoint, {})
        return
    _, status, payload, raw, _ = _authed_request("POST", endpoint, {})
    _ensure_status("rescan-values", status, payload, raw, (200, 202))
    _emit(payload if payload is not None else {"queued": True, "database_id": args.id})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Metabase helper for auth, discovery, cards, dashboards, query execution, and schema refresh."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    health = sub.add_parser("health", help="Check the Metabase health endpoint.")
    health.set_defaults(func=cmd_health)

    whoami = sub.add_parser("whoami", help="Print the current authenticated user and chosen auth method.")
    whoami.set_defaults(func=cmd_whoami)

    export_card = sub.add_parser("export-card", help="Export a card JSON by ID.")
    export_card.add_argument("--id", type=int, required=True)
    export_card.add_argument("--out", required=True)
    export_card.set_defaults(func=cmd_export_card)

    export_dashboard = sub.add_parser("export-dashboard", help="Export a dashboard JSON by ID.")
    export_dashboard.add_argument("--id", type=int, required=True)
    export_dashboard.add_argument("--out", required=True)
    export_dashboard.set_defaults(func=cmd_export_dashboard)

    list_collections = sub.add_parser("list-collections", help="List collections or the collection tree.")
    list_collections.add_argument("--tree", action="store_true", help="Use /api/collection/tree.")
    list_collections.set_defaults(func=cmd_list_collections)

    list_databases = sub.add_parser("list-databases", help="List databases visible to the authenticated user.")
    list_databases.set_defaults(func=cmd_list_databases)

    database_metadata = sub.add_parser("database-metadata", help="Fetch database metadata by database ID.")
    database_metadata.add_argument("--id", type=int, required=True)
    database_metadata.set_defaults(func=cmd_database_metadata)

    list_fields = sub.add_parser("list-fields", help="Flatten fields from database metadata.")
    list_fields.add_argument("--database-id", type=int, required=True)
    list_fields.add_argument("--table-id", type=int, help="Filter to a single table ID.")
    list_fields.set_defaults(func=cmd_list_fields)

    upsert_card = sub.add_parser("upsert-card", help="Create or update a card from a JSON spec.")
    upsert_card.add_argument("--spec", required=True, help="Path to card JSON; include 'id' to update.")
    upsert_card.add_argument("--dry-run", action="store_true")
    upsert_card.set_defaults(func=cmd_upsert_card)

    upsert_dashboard = sub.add_parser("upsert-dashboard", help="Create or update a dashboard from a JSON spec.")
    upsert_dashboard.add_argument("--spec", required=True, help="Path to dashboard JSON; include 'id' to update.")
    upsert_dashboard.add_argument("--dry-run", action="store_true")
    upsert_dashboard.set_defaults(func=cmd_upsert_dashboard)

    add_dashcard = sub.add_parser("add-dashcard", help="Add a card or text block to a dashboard.")
    add_dashcard.add_argument("--dashboard-id", type=int, required=True)
    add_dashcard.add_argument("--spec", required=True, help="Path to dashcard placement JSON.")
    add_dashcard.add_argument("--dry-run", action="store_true")
    add_dashcard.set_defaults(func=cmd_add_dashcard)

    update_dashcards = sub.add_parser("update-dashcards", help="Update dashboard card layout using /cards endpoint.")
    update_dashcards.add_argument("--dashboard-id", type=int, required=True)
    update_dashcards.add_argument("--spec", required=True, help="Path to JSON object or array of dashcards.")
    update_dashcards.add_argument("--dry-run", action="store_true")
    update_dashcards.set_defaults(func=cmd_update_dashcards)

    remove_dashcard = sub.add_parser("remove-dashcard", help="Remove a dashcard from a dashboard.")
    remove_dashcard.add_argument("--dashboard-id", type=int, required=True)
    remove_dashcard.add_argument("--dashcard-id", type=int, required=True)
    remove_dashcard.add_argument("--dry-run", action="store_true")
    remove_dashcard.set_defaults(func=cmd_remove_dashcard)

    run_query = sub.add_parser("run-query", help="Execute a dataset query spec via /api/dataset.")
    run_query.add_argument("--spec", required=True, help="Path to dataset query JSON.")
    run_query.add_argument("--out", help="Optional output file path.")
    run_query.add_argument("--dry-run", action="store_true")
    run_query.set_defaults(func=cmd_run_query)

    export_card_query = sub.add_parser("export-card-query", help="Run a saved card and export results.")
    export_card_query.add_argument("--id", type=int, required=True)
    export_card_query.add_argument("--format", choices=("json", "csv", "xlsx"), default="json")
    export_card_query.add_argument("--parameters", help="Optional path to parameters JSON.")
    export_card_query.add_argument("--out", help="Optional output file path.")
    export_card_query.add_argument("--dry-run", action="store_true")
    export_card_query.set_defaults(func=cmd_export_card_query)

    sync_schema = sub.add_parser("sync-schema", help="Request a database schema sync.")
    sync_schema.add_argument("--id", type=int, required=True, help="Database ID.")
    sync_schema.add_argument("--dry-run", action="store_true")
    sync_schema.set_defaults(func=cmd_sync_schema)

    rescan_values = sub.add_parser("rescan-values", help="Request a database field values rescan.")
    rescan_values.add_argument("--id", type=int, required=True, help="Database ID.")
    rescan_values.add_argument("--dry-run", action="store_true")
    rescan_values.set_defaults(func=cmd_rescan_values)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
