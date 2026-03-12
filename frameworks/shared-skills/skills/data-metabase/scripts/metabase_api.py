#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise SystemExit(f"Missing required env var: {key}")
    return value


def _base_url() -> str:
    url = _require_env("METABASE_URL").rstrip("/")
    return url


def _request(method: str, path: str, headers: dict[str, str], body: object | None = None) -> tuple[int, dict, bytes]:
    url = f"{_base_url()}{path}"
    data = None
    final_headers = {"Accept": "application/json", "User-Agent": "data-metabase-skill/1.0", **headers}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        final_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=final_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type and raw:
                try:
                    return resp.status, json.loads(raw.decode("utf-8")), raw
                except json.JSONDecodeError:
                    return resp.status, {}, raw
            return resp.status, {}, raw
    except urllib.error.HTTPError as e:
        raw = e.read() if hasattr(e, "read") else b""
        payload = {}
        if raw:
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                payload = {}
        return e.code, payload, raw


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
        status, payload, _ = _request("POST", "/api/session", {}, {"username": username, "password": password})
        if status == 200 and isinstance(payload, dict) and payload.get("id"):
            candidates.append(("session_login", {"X-Metabase-Session": str(payload["id"])}))

    return candidates


def _pick_auth_headers() -> tuple[str, dict[str, str]]:
    for name, headers in _auth_candidates():
        status, payload, _ = _request("GET", "/api/user/current", headers)
        if status == 200 and isinstance(payload, dict) and payload.get("id"):
            return name, headers
    raise SystemExit(
        "Authentication failed. Set METABASE_URL and either METABASE_API_KEY or METABASE_USERNAME+METABASE_PASSWORD."
    )


def cmd_whoami(_: argparse.Namespace) -> None:
    method, headers = _pick_auth_headers()
    status, payload, _ = _request("GET", "/api/user/current", headers)
    if status != 200:
        raise SystemExit(f"whoami failed with status {status}: {json.dumps(payload)[:500]}")
    print(json.dumps({"auth_method": method, "user": payload}, ensure_ascii=False, indent=2))


def cmd_health(_: argparse.Namespace) -> None:
    status, payload, raw = _request("GET", "/api/util/health", {})
    if status != 200:
        raise SystemExit(f"health failed with status {status}: {raw[:500]!r}")
    if payload:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(raw.decode("utf-8", errors="replace"))


def cmd_export_card(args: argparse.Namespace) -> None:
    _, headers = _pick_auth_headers()
    status, payload, raw = _request("GET", f"/api/card/{args.id}", headers)
    if status != 200:
        raise SystemExit(f"export-card failed with status {status}: {raw[:500]!r}")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(args.out)


def cmd_export_dashboard(args: argparse.Namespace) -> None:
    _, headers = _pick_auth_headers()
    status, payload, raw = _request("GET", f"/api/dashboard/{args.id}", headers)
    if status != 200:
        raise SystemExit(f"export-dashboard failed with status {status}: {raw[:500]!r}")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(args.out)


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise SystemExit(f"Spec must be a JSON object: {path}")
    return value


def cmd_upsert_card(args: argparse.Namespace) -> None:
    _, headers = _pick_auth_headers()
    spec = _load_json(args.spec)

    card_id = spec.get("id")
    if card_id:
        payload = {k: v for k, v in spec.items() if k != "id"}
        status, updated, raw = _request("PUT", f"/api/card/{card_id}", headers, payload)
        if status not in (200, 202):
            raise SystemExit(f"upsert-card update failed with status {status}: {raw[:500]!r}")
        print(json.dumps({"action": "updated", "id": card_id, "result": updated}, ensure_ascii=False))
        return

    status, created, raw = _request("POST", "/api/card", headers, spec)
    if status not in (200, 201):
        raise SystemExit(f"upsert-card create failed with status {status}: {raw[:500]!r}")
    print(json.dumps({"action": "created", "result": created}, ensure_ascii=False))


def cmd_upsert_dashboard(args: argparse.Namespace) -> None:
    _, headers = _pick_auth_headers()
    spec = _load_json(args.spec)

    dashboard_id = spec.get("id")
    if dashboard_id:
        payload = {k: v for k, v in spec.items() if k != "id"}
        status, updated, raw = _request("PUT", f"/api/dashboard/{dashboard_id}", headers, payload)
        if status not in (200, 202):
            raise SystemExit(f"upsert-dashboard update failed with status {status}: {raw[:500]!r}")
        print(json.dumps({"action": "updated", "id": dashboard_id, "result": updated}, ensure_ascii=False))
        return

    status, created, raw = _request("POST", "/api/dashboard", headers, spec)
    if status not in (200, 201):
        raise SystemExit(f"upsert-dashboard create failed with status {status}: {raw[:500]!r}")
    print(json.dumps({"action": "created", "result": created}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal Metabase API helper (health, auth, cards, dashboards).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    health = sub.add_parser("health", help="Check API health endpoint.")
    health.set_defaults(func=cmd_health)

    whoami = sub.add_parser("whoami", help="Print current authenticated user.")
    whoami.set_defaults(func=cmd_whoami)

    export_card = sub.add_parser("export-card", help="Export a card JSON by id.")
    export_card.add_argument("--id", type=int, required=True)
    export_card.add_argument("--out", required=True)
    export_card.set_defaults(func=cmd_export_card)

    export_dashboard = sub.add_parser("export-dashboard", help="Export a dashboard JSON by id.")
    export_dashboard.add_argument("--id", type=int, required=True)
    export_dashboard.add_argument("--out", required=True)
    export_dashboard.set_defaults(func=cmd_export_dashboard)

    upsert_card = sub.add_parser("upsert-card", help="Create/update a card from a JSON spec.")
    upsert_card.add_argument("--spec", required=True, help="Path to card JSON; include 'id' to update.")
    upsert_card.set_defaults(func=cmd_upsert_card)

    upsert_dashboard = sub.add_parser("upsert-dashboard", help="Create/update a dashboard from a JSON spec.")
    upsert_dashboard.add_argument("--spec", required=True, help="Path to dashboard JSON; include 'id' to update.")
    upsert_dashboard.set_defaults(func=cmd_upsert_dashboard)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
