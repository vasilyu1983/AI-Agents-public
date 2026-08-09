#!/usr/bin/env python3
"""
Workflow definition idempotency linter.

Reads a workflow definition (JSON) and checks for:
  - Missing idempotency keys on steps that perform side effects
  - Missing or under-specified retry policy
  - Synchronous side effects without a dead-letter queue (DLQ) reference
  - Non-idempotent HTTP methods (POST/PUT/PATCH/DELETE) without idempotency annotation
  - Steps that send, create, update, delete, or notify without retry guards

Returns a JSON object with "issues" (list) and "summary" (counts).
Exit code 0 = no issues found; 1 = issues found; 2 = input error.

Usage:
    python3 check_workflow_idempotency.py workflow.json
    python3 check_workflow_idempotency.py workflow.json --strict
    python3 check_workflow_idempotency.py --help
    cat workflow.json | python3 check_workflow_idempotency.py -
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Heuristics: keywords that indicate side-effect operations
# ---------------------------------------------------------------------------

SIDE_EFFECT_KEYWORDS = frozenset(
    {
        "send", "create", "update", "delete", "notify", "publish", "emit",
        "write", "insert", "upsert", "patch", "post", "charge", "bill",
        "email", "sms", "webhook", "http", "request", "call", "invoke",
        "dispatch", "trigger", "push", "enqueue",
    }
)

NON_IDEMPOTENT_HTTP_METHODS = frozenset({"post", "put", "patch", "delete"})

IDEMPOTENCY_KEY_NAMES = frozenset(
    {
        "idempotency_key", "idempotencyKey", "idempotency-key",
        "idempotency_id", "idempotencyId", "idempotent_key",
        "deduplication_key", "deduplicationKey", "dedupe_key",
        "request_id", "requestId", "request-id",
    }
)

RETRY_POLICY_NAMES = frozenset(
    {"retry", "retryPolicy", "retry_policy", "retries", "retry_config", "retryConfig"}
)

DLQ_NAMES = frozenset(
    {
        "dlq", "dead_letter_queue", "deadLetterQueue", "dead-letter-queue",
        "dlq_topic", "dlqTopic", "error_queue", "errorQueue",
        "fallback_queue", "fallbackQueue",
    }
)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Workflow definition idempotency linter.\n\n"
            "Reads a JSON workflow definition and reports missing idempotency keys,\n"
            "missing retry policies, and synchronous side effects without DLQ guards.\n\n"
            "Expected JSON shape (any of the following are accepted):\n"
            "  { \"steps\": [ { \"id\": \"...\", \"type\": \"...\", ... } ] }\n"
            "  { \"tasks\": [ ... ] }\n"
            "  { \"nodes\": [ ... ] }\n"
            "  [ { \"id\": \"...\", ... } ]   (bare step array)\n\n"
            "Each step/task/node is inspected for idempotency and retry patterns."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Path to the workflow JSON file, or '-' to read from stdin (default: -).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Strict mode: treat any step with a recognized side-effect keyword "
            "in its name or type as requiring an idempotency key, even if it "
            "is not an HTTP step."
        ),
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json).",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has_key(obj: dict, key_set: frozenset) -> bool:
    """Return True if any key in the object (case-insensitive) matches key_set."""
    lower_keys = {k.lower() for k in obj}
    return bool(lower_keys & {k.lower() for k in key_set})


def _flatten_string_values(obj: Any, depth: int = 0) -> list[str]:
    """Collect all string values from a nested dict/list (limited depth)."""
    if depth > 4:
        return []
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        out: list[str] = []
        for v in obj.values():
            out.extend(_flatten_string_values(v, depth + 1))
        return out
    if isinstance(obj, list):
        out = []
        for item in obj:
            out.extend(_flatten_string_values(item, depth + 1))
        return out
    return []


def _looks_like_side_effect(step: dict) -> bool:
    """Heuristic: does this step look like it performs a side effect?"""
    candidates = [
        str(step.get("id", "")),
        str(step.get("name", "")),
        str(step.get("type", "")),
        str(step.get("action", "")),
        str(step.get("operation", "")),
    ]
    combined = " ".join(candidates).lower()
    return any(kw in combined for kw in SIDE_EFFECT_KEYWORDS)


def _get_http_method(step: dict) -> str | None:
    """Extract HTTP method from a step definition if present."""
    for key in ("method", "http_method", "httpMethod", "verb"):
        val = step.get(key)
        if isinstance(val, str):
            return val.lower()
    # Check nested under 'request', 'config', 'parameters'
    for nested_key in ("request", "config", "parameters", "options"):
        nested = step.get(nested_key)
        if isinstance(nested, dict):
            for key in ("method", "http_method", "httpMethod"):
                val = nested.get(key)
                if isinstance(val, str):
                    return val.lower()
    return None


def _get_retry_policy(step: dict) -> dict | None:
    """Return the retry policy dict/value if present."""
    for key in RETRY_POLICY_NAMES:
        val = step.get(key)
        if val is not None:
            return val
    return None


def _has_dlq(step: dict) -> bool:
    """Return True if the step references a DLQ."""
    if _has_key(step, DLQ_NAMES):
        return True
    # Check nested
    for nested_key in ("on_failure", "onFailure", "failure", "error", "fallback"):
        nested = step.get(nested_key)
        if isinstance(nested, dict) and _has_key(nested, DLQ_NAMES):
            return True
    return False


def _has_idempotency_key(step: dict) -> bool:
    """Return True if the step or its parameters carry an idempotency key."""
    if _has_key(step, IDEMPOTENCY_KEY_NAMES):
        return True
    for nested_key in ("parameters", "params", "headers", "config", "options", "metadata"):
        nested = step.get(nested_key)
        if isinstance(nested, dict) and _has_key(nested, IDEMPOTENCY_KEY_NAMES):
            return True
    return False


# ---------------------------------------------------------------------------
# Linting
# ---------------------------------------------------------------------------

def lint_step(step: dict, strict: bool) -> list[dict]:
    """
    Lint a single step. Returns a list of issue dicts with keys:
      step_id, rule, severity, message
    """
    issues: list[dict] = []
    step_id = step.get("id") or step.get("name") or "<unnamed>"

    is_side_effect = _looks_like_side_effect(step)
    http_method = _get_http_method(step)
    retry_policy = _get_retry_policy(step)
    has_dlq = _has_dlq(step)
    has_idem_key = _has_idempotency_key(step)

    # Rule 1: Non-idempotent HTTP method without idempotency key
    if http_method and http_method in NON_IDEMPOTENT_HTTP_METHODS and not has_idem_key:
        issues.append({
            "step_id": step_id,
            "rule": "missing-idempotency-key",
            "severity": "error",
            "message": (
                f"Step performs a {http_method.upper()} request but has no idempotency key. "
                "Add an 'idempotency_key' or 'request_id' field to prevent duplicate side effects on retry."
            ),
        })

    # Rule 2: Side-effect step without retry policy (strict mode or HTTP)
    if is_side_effect and retry_policy is None:
        sev = "error" if http_method or strict else "warning"
        issues.append({
            "step_id": step_id,
            "rule": "missing-retry-policy",
            "severity": sev,
            "message": (
                "Step appears to perform a side effect but has no retry policy. "
                "Add a 'retry_policy' with max_attempts, backoff, and jitter to handle transient failures."
            ),
        })

    # Rule 3: Under-specified retry policy (has retry key but no max_attempts)
    if retry_policy is not None and isinstance(retry_policy, dict):
        has_limit = any(
            k in retry_policy
            for k in ("max_attempts", "maxAttempts", "max_retries", "maxRetries", "attempts", "limit")
        )
        if not has_limit:
            issues.append({
                "step_id": step_id,
                "rule": "unbounded-retry-policy",
                "severity": "warning",
                "message": (
                    "Retry policy is present but does not specify a maximum attempt count. "
                    "An unbounded retry can cause infinite loops. Add 'max_attempts'."
                ),
            })

    # Rule 4: Non-idempotent side effect without DLQ
    if is_side_effect and (http_method in NON_IDEMPOTENT_HTTP_METHODS or strict):
        if retry_policy is not None and not has_dlq:
            issues.append({
                "step_id": step_id,
                "rule": "sync-side-effect-without-dlq",
                "severity": "warning",
                "message": (
                    "Step has a retry policy and performs a side effect but references no dead-letter queue. "
                    "Exhausted retries will silently drop the event. Add a 'dlq' or 'dead_letter_queue' reference."
                ),
            })

    # Rule 5: Strict — side-effect step with no idempotency key at all
    if strict and is_side_effect and not has_idem_key and http_method not in NON_IDEMPOTENT_HTTP_METHODS:
        issues.append({
            "step_id": step_id,
            "rule": "missing-idempotency-key-strict",
            "severity": "warning",
            "message": (
                "Step name or type suggests a side effect. In strict mode, all side-effect steps "
                "should carry an idempotency key or dedupe ID."
            ),
        })

    return issues


def extract_steps(workflow: Any) -> list[dict]:
    """Extract the list of steps from various workflow JSON shapes."""
    if isinstance(workflow, list):
        return [s for s in workflow if isinstance(s, dict)]
    if isinstance(workflow, dict):
        for key in ("steps", "tasks", "nodes", "activities", "jobs"):
            val = workflow.get(key)
            if isinstance(val, list):
                return [s for s in val if isinstance(s, dict)]
    return []


def lint_workflow(workflow: Any, strict: bool) -> list[dict]:
    steps = extract_steps(workflow)
    if not steps:
        return [{
            "step_id": None,
            "rule": "no-steps-found",
            "severity": "warning",
            "message": (
                "No steps found in workflow definition. Expected a list or an object with "
                "a 'steps', 'tasks', 'nodes', 'activities', or 'jobs' key."
            ),
        }]
    all_issues: list[dict] = []
    for step in steps:
        all_issues.extend(lint_step(step, strict))
    return all_issues


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()

    # Read input
    try:
        if args.file == "-":
            raw = sys.stdin.read()
        else:
            with open(args.file, "r", encoding="utf-8") as fh:
                raw = fh.read()
    except OSError as exc:
        print(json.dumps({"error": str(exc), "issues": [], "summary": {}}))
        return 2

    # Parse JSON
    try:
        workflow = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"Invalid JSON: {exc}", "issues": [], "summary": {}}))
        return 2

    issues = lint_workflow(workflow, strict=args.strict)

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    summary = {
        "total_issues": len(issues),
        "errors": len(errors),
        "warnings": len(warnings),
    }

    result = {"issues": issues, "summary": summary}

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if not issues:
            print("No issues found.")
        for issue in issues:
            sid = issue.get("step_id") or "<workflow>"
            sev = issue["severity"].upper()
            rule = issue["rule"]
            msg = issue["message"]
            print(f"[{sev}] step={sid} rule={rule}")
            print(f"       {msg}")
        print(f"\nSummary: {summary['errors']} error(s), {summary['warnings']} warning(s)")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
