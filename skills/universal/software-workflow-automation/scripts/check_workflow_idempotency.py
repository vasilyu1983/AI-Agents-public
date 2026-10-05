#!/usr/bin/env python3
"""
Workflow definition idempotency linter.

Reads a workflow definition (JSON) and checks for:
  - Missing idempotency keys on steps that perform side effects
  - n8n keys that are constant, or not stable per item across retries
  - Missing or under-specified retry policy
  - Synchronous side effects without a dead-letter queue (DLQ) reference
  - Non-idempotent HTTP methods (POST/PUT/PATCH/DELETE) and n8n write
    operations (create, update, send, charge, ...) without an idempotency key
  - Steps that send, create, update, delete, or notify without retry guards

n8n trigger nodes, Respond to Webhook, explicit reads, candidate idempotent database
writes (upsert or conflict clauses with simple replacement assignments) and DLQ targets are
not linted as side effects; other database writes get a warning, not a key error.

Returns a JSON object with "issues" (list) and "summary" (counts).
Exit code 0 = passed; 1 = an issue at or above --fail-on (default: warning,
so any issue fails); 2 = input error: not a workflow, or no steps to lint.

Usage:
    python3 check_workflow_idempotency.py workflow.json
    python3 check_workflow_idempotency.py workflow.json --strict
    python3 check_workflow_idempotency.py workflow.json --fail-on error
    python3 check_workflow_idempotency.py --help
    cat workflow.json | python3 check_workflow_idempotency.py -
"""

from __future__ import annotations

import argparse
import json
import re
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

# Tokens that start with a keyword but are not the verb ("postgres" is not "post").
SIDE_EFFECT_KEYWORD_EXCEPTIONS = frozenset({
    "postgres", "postgresql", "posthog", "postcode", "postal", "postpone", "postprocess",
    "postprocessing", "postfix", "postmortem", "posture",
})

# Name labels that mark an n8n node as a dead-letter store.
DLQ_NODE_LABELS = ("dlq", "dead letter", "error queue")

# n8n `parameters.operation` words (camelCase-split, exact) that change external state.
N8N_WRITE_VERBS = frozenset(
    {
        "create", "update", "delete", "upsert", "insert", "send", "charge", "post",
        "capture", "refund", "add", "remove", "cancel", "append", "upload", "reply",
        "publish", "push", "incr", "increment", "decr", "decrement", "move", "copy",
        "share", "invite", "archive",
    }
)
N8N_READ_OPERATIONS = frozenset({"select", "get", "getall", "find", "aggregate"})

# n8n database nodes: they cannot carry an idempotency key, so the write itself must be
# idempotent (upsert, or a conflict clause on a unique business key).
N8N_DB_NODES = frozenset(
    {
        "postgres", "mysql", "microsoftsql", "mongodb", "snowflake", "questdb", "timescaledb",
        "cratedb", "oracledb",
    }
)
SQL_IDEMPOTENT_WRITE = re.compile(
    r"\bon\s+conflict\b|\bmerge\b|\binsert\s+ignore\b|\bon\s+duplicate\s+key\b", re.IGNORECASE)
SQL_WRITE_KEYWORD = re.compile(
    r"\b(?:insert|update|delete|merge|upsert|replace|create|drop|alter|truncate|grant|revoke"
    r"|call|exec|execute|copy|into|lock|vacuum)\b", re.IGNORECASE)

# Core n8n nodes that transform or route items in the workflow; their `operation`
# (e.g. itemLists "removeDuplicates", dateTime "addToDate") is not an external write.
N8N_CORE_NODES = frozenset(
    {
        "aggregate", "code", "comparedatasets", "crypto", "datetime", "executeworkflow",
        "executiondata", "filter", "function", "functionitem", "html", "if", "itemlists",
        "limit", "markdown", "merge", "noop", "removeduplicates", "renamekeys",
        "respondtowebhook", "set", "sort", "splitinbatches", "splitout", "stickynote",
        "stopanderror", "summarize", "switch", "wait", "xml",
    }
)

IDEMPOTENCY_KEY_NAMES = frozenset(
    {
        "idempotency_key", "idempotencyKey", "idempotency-key",
        "idempotency_id", "idempotencyId", "idempotent_key",
        "deduplication_key", "deduplicationKey", "dedupe_key",
        "request_id", "requestId", "request-id",
    }
)

# Header names (from name/value header lists) that carry an idempotency key, beyond
# IDEMPOTENCY_KEY_NAMES: any name containing "idempotency" (Idempotency-Key,
# X-Idempotency-Key) plus these provider headers. Add other providers' key headers here.
IDEMPOTENCY_HEADER_NAMES = frozenset({"paypal-request-id"})

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
            "  [ { \"id\": \"...\", ... } ]   (bare step array)\n"
            "  [ { \"nodes\": [ ... ] }, ... ]   (array of workflows, linted one by one)\n\n"
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
        "--fail-on",
        choices=["error", "warning"],
        default="warning",
        help=(
            "Lowest severity that makes the exit code 1 (default: warning, so any issue fails). "
            "'error' reports warnings but lets them pass. Independent of --strict, which "
            "changes what is found and at which severity."
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


def _words(text: str) -> set[str]:
    """Split identifiers on non-alphanumerics and camelCase: "sendEmail" -> {send, email}."""
    return {w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", text)}


def _has_keyword(text: str) -> bool:
    """A token that starts with a side-effect keyword ("sendgrid", "createorder", "charges"),
    except known non-verbs such as "postgres"."""
    return any(word.startswith(kw) for word in _words(text) - SIDE_EFFECT_KEYWORD_EXCEPTIONS
               for kw in SIDE_EFFECT_KEYWORDS)


def _n8n_node_kind(step: dict) -> str:
    """The node's own type name, lower-cased: "n8n-nodes-base.postgres" -> "postgres"."""
    return str(step.get("type", "")).rsplit(".", 1)[-1].lower()


def _is_n8n_trigger(step: dict) -> bool:
    """Trigger nodes (Webhook, Form, Manual, Schedule, app triggers) receive, they do not act;
    Respond to Webhook only answers the inbound request."""
    return (_n8n_node_kind(step).endswith("trigger") or _n8n_node_kind(step) == "respondtowebhook"
            or step.get("type") == "n8n-nodes-base.webhook")


def _n8n_operation(step: dict) -> str:
    params = step.get("parameters")
    op = params.get("operation") if isinstance(params, dict) else None
    return op if isinstance(op, str) else ""


def _sql_read_only(query: str) -> bool:
    """Every statement is a SELECT or WITH ... SELECT, and none contains a write keyword."""
    statements = [part.strip() for part in query.lstrip("=").split(";") if part.strip()]
    return bool(statements) and all(
        re.match(r"(?:select|with)\b", st, re.IGNORECASE) and not SQL_WRITE_KEYWORD.search(st)
        for st in statements)


def _n8n_read_only(step: dict) -> bool:
    """An explicit read: select/get/getAll/find/aggregate, or a read-only executeQuery."""
    op = _n8n_operation(step)
    if op.lower() in N8N_READ_OPERATIONS:
        return True
    if op == "executeQuery":
        query = step["parameters"].get("query")
        return isinstance(query, str) and _sql_read_only(query)
    return False


def _n8n_db_write(step: dict) -> str | None:
    """For an n8n database node: "idempotent" (a static candidate, not a proof)
    or "write" (insert, update, delete, other or default operations).
    None for reads and for nodes that are not database nodes."""
    if _n8n_node_kind(step) not in N8N_DB_NODES or _n8n_read_only(step):
        return None
    op = _n8n_operation(step)
    if op.lower() == "upsert":
        return "idempotent"
    if op == "executeQuery":
        query = step["parameters"].get("query")
        if isinstance(query, str) and _sql_idempotent_candidate(query):
            return "idempotent"
    return "write"


def _sql_idempotent_candidate(query: str) -> bool:
    """Allow only simple conflict writes; unfamiliar SET expressions fail closed.

    A conflict clause alone does not make `n = n + 1` replay-safe. This is a
    deliberately small SQL subset, not a SQL parser: multiple statements,
    comments and complex assignments need review. Keys, triggers and stable
    input/source rows remain manual checks even for accepted candidates.
    """
    if not SQL_IDEMPOTENT_WRITE.search(query) or "--" in query or "/*" in query:
        return False
    statements = [part.strip() for part in query.lstrip("=").split(";") if part.strip()]
    if len(statements) != 1:
        return False
    # MERGE's incoming row may have an arbitrary source alias; only direct reads
    # from that source qualify. Target references, arithmetic and function calls don't.
    source = re.search(r"\busing\s+([\w.]+)(?:\s+(?:as\s+)?(\w+))?\s+on\b", query, re.I)
    incoming = {"excluded"}
    if source:
        incoming.add((source.group(2) or source.group(1).rsplit(".", 1)[-1]).lower())
    updates = list(re.finditer(r"\bupdate\s+(?:set\s+)?(.+?)(?=\bwhere\b|\bwhen\b|\breturning\b|;|$)",
                               query, re.I | re.S))
    for update in updates:
        for assignment in update.group(1).split(","):
            match = re.fullmatch(r'\s*(?:\w+\.)?(?:\w+|"\w+"|`\w+`|\[\w+\])\s*=\s*(.+?)\s*', assignment, re.S)
            if not match:
                return False
            rhs = match.group(1)
            literal = re.fullmatch(r"(?:[+-]?\d+(?:\.\d+)?|'(?:[^']|'')*'|true|false|null|\$\d+|\?)", rhs, re.I)
            reference = re.fullmatch(r'(\w+)\.(?:\w+|"\w+"|`\w+`|\[\w+\])', rhs)
            # MySQL's VALUES(col) refers to the incoming insert value.
            values = re.fullmatch(r"values\(\w+\)", rhs, re.I)
            if not (literal or values or (reference and reference.group(1).lower() in incoming)):
                return False
    return True


def _n8n_write_operation(step: dict) -> str | None:
    """Return the write operation of an n8n app node (Stripe charge/create, Slack post, ...)."""
    if (_n8n_node_kind(step) in N8N_CORE_NODES | N8N_DB_NODES) or _is_n8n_trigger(step):
        return None
    op = _n8n_operation(step)
    return op if _words(op) & N8N_WRITE_VERBS else None


def _is_dlq_named(node: dict) -> bool:
    return any(label in str(node.get("name", "")).lower() for label in DLQ_NODE_LABELS)


def _n8n_dlq_sinks(workflow: Any) -> set[str]:
    """DLQ-named nodes reached only through error outputs. They store failed items; a
    duplicate DLQ record is harmless, so they are not linted (check their own durability
    by hand). Any other error-path node, such as a fallback charge, is still linted."""
    if not _is_n8n_workflow(workflow) or not isinstance(workflow.get("connections"), dict):
        return set()
    error_targets: set[str] = set()
    for node in workflow["nodes"]:
        if isinstance(node, dict) and node.get("onError") == "continueErrorOutput":
            error_targets |= {t["name"] for t in _n8n_error_destinations(node, workflow)}
    other_targets: set[str] = set()
    for source, route in workflow["connections"].items():
        outputs = route.get("main", []) if isinstance(route, dict) else []
        for index, edges in enumerate(outputs if isinstance(outputs, list) else []):
            source_node = next((n for n in workflow["nodes"] if isinstance(n, dict) and n.get("name") == source), {})
            if index == 1 and source_node.get("onError") == "continueErrorOutput":
                continue
            other_targets |= {e["node"] for e in edges or [] if isinstance(e, dict) and isinstance(e.get("node"), str)}
    names = {n.get("name") for n in workflow["nodes"] if isinstance(n, dict) and _is_dlq_named(n)}
    return (error_targets - other_targets) & names


def _looks_like_side_effect(step: dict, workflow: Any = None) -> bool:
    """Heuristic: does this step look like it performs a side effect?"""
    if _is_n8n_workflow(workflow):
        if _is_n8n_trigger(step) or _n8n_read_only(step):
            return False
        db = _n8n_db_write(step)
        if db:
            return db == "write"
        if _n8n_write_operation(step):
            return True
    candidates = [
        str(step.get("id", "")),
        str(step.get("name", "")),
        str(step.get("type", "")),
        str(step.get("action", "")),
        str(step.get("operation", "")),
    ]
    return _has_keyword(" ".join(candidates))


def _get_http_method(step: dict, workflow: Any = None) -> str | None:
    """Extract the outbound HTTP method from a step definition if present."""
    if _is_n8n_workflow(workflow) and _is_n8n_trigger(step):
        return None  # a Webhook's httpMethod is the inbound request it accepts
    # `requestMethod` is the n8n HTTP Request node's typeVersion-1 field.
    for key in ("method", "http_method", "httpMethod", "requestMethod", "verb"):
        val = step.get(key)
        if isinstance(val, str):
            return val.lower()
    # Check nested under 'request', 'config', 'parameters'
    for nested_key in ("request", "config", "parameters", "options"):
        nested = step.get(nested_key)
        if isinstance(nested, dict):
            for key in ("method", "http_method", "httpMethod", "requestMethod"):
                val = nested.get(key)
                if isinstance(val, str):
                    return val.lower()
    return None


N8N_DEFAULT_MAX_TRIES = 3


def _get_retry_policy(step: dict) -> dict | None:
    """Return the retry policy dict/value if present."""
    for key in RETRY_POLICY_NAMES:
        val = step.get(key)
        if val is not None:
            return val
    # n8n node settings: retryOnFail + maxTries (n8n defaults maxTries to 3).
    if step.get("retryOnFail") is True:
        return {
            "max_attempts": step.get("maxTries", N8N_DEFAULT_MAX_TRIES),
            "wait_ms": step.get("waitBetweenTries"),
        }
    return None


def _named_params(obj: Any, depth: int = 0) -> list[str]:
    """Collect 'name' fields from list-of-{name, value} parameter shapes (n8n headers/query)."""
    if depth > 5:
        return []
    names: list[str] = []
    if isinstance(obj, dict):
        name = obj.get("name")
        if isinstance(name, str) and "value" in obj:
            names.append(name)
        for v in obj.values():
            names.extend(_named_params(v, depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            names.extend(_named_params(item, depth + 1))
    return names


def _n8n_error_destinations(step: dict, workflow: Any) -> list[dict]:
    """Read the error output's target nodes from an exported n8n graph."""
    if not isinstance(workflow, dict):
        return []
    connections = workflow.get("connections", {})
    node_name = step.get("name")
    route = connections.get(node_name, {}) if isinstance(connections, dict) and isinstance(node_name, str) else {}
    main = route.get("main", []) if isinstance(route, dict) else []
    if not isinstance(main, list) or len(main) < 2 or not isinstance(main[1], list):
        return []
    destinations = {node["name"]: node for node in workflow.get("nodes", [])
                    if isinstance(node, dict) and isinstance(node.get("name"), str)}
    return [destinations[edge["node"]] for edge in main[1]
            if isinstance(edge, dict) and isinstance(edge.get("node"), str)
            and edge["node"] in destinations]


# Core (`n8n-nodes-base.*`), scoped packages (`@n8n/n8n-nodes-langchain.*`,
# `@acme/n8n-nodes-x.*`) and locally loaded custom nodes (`CUSTOM.*`).
N8N_NODE_TYPE = re.compile(r"(?:@[^/\s]+/)?n8n-nodes-|CUSTOM\.")


def _is_n8n_workflow(workflow: Any) -> bool:
    """Distinguish an n8n export from the supported generic `nodes` shape."""
    if not isinstance(workflow, dict) or not isinstance(workflow.get("nodes"), list):
        return False
    return any(isinstance(node, dict) and isinstance(node.get("type"), str)
               and N8N_NODE_TYPE.match(node["type"]) for node in workflow["nodes"])


def _has_dlq(step: dict, workflow: Any = None) -> bool:
    """Return True if the step references a DLQ."""
    if _is_n8n_workflow(workflow):
        # A configured but unconnected error output silently drops failed items.
        if step.get("onError") != "continueErrorOutput":
            return False
        # A disabled node or a sticky note never receives the failed item.
        targets = [node for node in _n8n_error_destinations(step, workflow)
                   if node.get("disabled") is not True
                   and node.get("type") != "n8n-nodes-base.stickyNote"]
        if not targets:
            return False
        # Only the connected error output counts in n8n; a stray `dlq` field routes nothing.
        return any(
            _is_dlq_named(node)
            and node.get("type") != "n8n-nodes-base.noOp"
            for node in targets
        )
    if _has_key(step, DLQ_NAMES):
        return True
    # Check nested
    for nested_key in ("on_failure", "onFailure", "failure", "error", "fallback"):
        nested = step.get(nested_key)
        if isinstance(nested, dict) and _has_key(nested, DLQ_NAMES):
            return True
    return False


def _literal_expression(value: str) -> bool:
    """Recognize only a quoted constant in an n8n expression, not general JS."""
    return bool(re.fullmatch(r"=\s*\{\{\s*(['\"])(?:\\.|(?!\1).)*\1\s*\}\}", value.strip()))


# Run-time item data followed by a property or method access; a bare `$json` renders
# as "[object Object]". `$workflow` and `$node[...]` metadata are constant per workflow;
# `$execution` is constant per execution and changes when a webhook is redelivered.
N8N_RUNTIME_REFERENCE = re.compile(
    r"(?:\$(?:json|binary|input|item|items|prevNode)\b|\$\([^)]*\)"
    r"|\$node\s*\[[^\]]*\]\s*\.\s*(?:json|binary)\b)\s*(?:\?\.|\.|\[)")

# Batch-level accessors return the same item for every item in the run.
N8N_BATCH_ACCESSOR = re.compile(
    r"(?:\$input|\$\([^)]*\))\s*\.\s*(?:first|last|all)\s*\("
    r"|\$items\s*\([^)]*\)\s*\[\s*\d+\s*\]")

# Components that differ per execution, run or attempt: a key containing one is new on
# every retry or redelivery, so it never deduplicates anything.
N8N_VOLATILE_PATTERNS = (
    r"\$(?:execution|runIndex|now|today)\b",       # n8n execution, run and clock variables
    r"\bDate\s*\(",                               # Date() and new Date()
    r"\bDate\s*\.\s*now\s*\(",                    # Date.now()
    r"\bDateTime\s*\.\s*(?:now|local|utc)\s*\(",   # Luxon clock
    r"\bperformance\s*\.\s*now\s*\(",
    r"\bMath\s*\.\s*random\s*\(",
    r"\brandomUUID\s*\(",                         # crypto.randomUUID()
)
N8N_VOLATILE_REFERENCE = re.compile("|".join(N8N_VOLATILE_PATTERNS))


def _n8n_expression_code(body: str) -> list[str] | None:
    """Split an n8n template into `{{ }}` segments with literals and comments removed.

    Quote-aware, so `}}` inside a string does not end a segment; template-literal
    `${...}` parts are kept as code. Returns None for anything unterminated or a
    stray `}}`, so callers fail closed.
    """
    segments: list[str] = []
    i, n = 0, len(body)
    while i < n:
        if body.startswith("}}", i):
            return None
        if not body.startswith("{{", i):
            i += 1
            continue
        i += 2
        code: list[str] = []
        while not body.startswith("}}", i):
            if i >= n:
                return None
            c = body[i]
            if c in "'\"`":
                j = i + 1
                while j < n and body[j] != c:
                    if c == "`" and body.startswith("${", j):
                        k = body.find("}", j)
                        if k < 0:
                            return None
                        code.append(" " + body[j + 2:k] + " ")
                        j = k + 1
                    else:
                        j += 2 if body[j] == "\\" else 1
                if j >= n:
                    return None
                code.append(" ")
                i = j + 1
            elif body.startswith("/*", i):
                j = body.find("*/", i + 2)
                if j < 0:
                    return None
                code.append(" ")
                i = j + 2
            elif body.startswith("//", i):
                ends = [k for k in (body.find("\n", i), body.find("}}", i)) if k >= 0]
                if not ends:
                    return None
                code.append(" ")
                i = min(ends)
            else:
                code.append(c)
                i += 1
        segments.append("".join(code))
        i += 2
    return segments or None


def _n8n_key_problem(value: str) -> str | None:
    """Classify an n8n key expression: None if it is stable per item, else "static" or "unstable".

    "static": not a well-formed `={{ ... }}` expression reading the current item's data
    (no `=` prefix, an empty or unterminated `{{ }}`, only literals, comments, bare
    objects, workflow or execution metadata, or batch-level accessors). Fails closed.
    "unstable": reads item data but mixes in a per-execution, per-run, per-attempt or
    batch-level component, so retries and redeliveries get a new key.
    A key that passes can still have the wrong business scope; that stays a review item.
    """
    stripped = value.strip()
    if not stripped.startswith("="):
        return "static"
    segments = _n8n_expression_code(stripped[1:])
    if not segments:
        return "static"
    if not any(N8N_RUNTIME_REFERENCE.search(N8N_BATCH_ACCESSOR.sub(" ", code)) for code in segments):
        return "static"
    if any(N8N_VOLATILE_REFERENCE.search(code) or N8N_BATCH_ACCESSOR.search(code) for code in segments):
        return "unstable"
    return None


def _is_key_header(name: str) -> bool:
    lower = name.lower()
    return (lower in {k.lower() for k in IDEMPOTENCY_KEY_NAMES} or "idempotency" in lower
            or lower in IDEMPOTENCY_HEADER_NAMES)


def _n8n_key_problems(step: dict, workflow: Any = None) -> set[str]:
    """Problems ("static", "unstable") of the n8n idempotency keys this step sets."""
    if not _is_n8n_workflow(workflow):
        return set()  # `={{ }}` expression semantics exist only in n8n; other engines template differently
    wanted = {k.lower() for k in IDEMPOTENCY_KEY_NAMES}
    problems: set[str] = set()

    def check(value: Any) -> None:
        if isinstance(value, str) and value.strip():
            problem = _n8n_key_problem(value)
            if problem:
                problems.add(problem)

    def visit(obj: Any) -> None:
        if isinstance(obj, dict):
            name = obj.get("name")
            if isinstance(name, str) and _is_key_header(name):
                check(obj.get("value"))
            # In n8n, a key-named parameter is also an n8n expression field.
            for k, v in obj.items():
                if k.lower() in wanted:
                    check(v)
                visit(v)
        elif isinstance(obj, list):
            for v in obj:
                visit(v)

    visit(step.get("parameters", {}))
    return problems


def _has_idempotency_key(step: dict, workflow: Any = None) -> bool:
    """Return True if the step or its parameters carry an idempotency key."""
    wanted = {k.lower() for k in IDEMPOTENCY_KEY_NAMES}
    n8n = _is_n8n_workflow(workflow)

    def valid(value: Any) -> bool:
        if not n8n:
            # Generic engines: a declared key is the contract, but it must be a non-empty
            # string or a structured reference such as {"path": "order.id"}.
            return (isinstance(value, str) and bool(value.strip())) or (isinstance(value, dict) and bool(value))
        return (isinstance(value, str) and bool(value.strip()) and value.strip() != "="
                and not _literal_expression(value))

    if any(k.lower() in wanted and valid(v) for k, v in step.items()):
        return True
    for nested_key in ("parameters", "params", "headers", "config", "options", "metadata"):
        nested = step.get(nested_key)
        if isinstance(nested, dict) and any(k.lower() in wanted and valid(v)
                                            for k, v in nested.items()):
            return True
    # Header/query parameters expressed as [{"name": ..., "value": ...}] (n8n HTTP Request node).
    def named_valid(obj: Any) -> bool:
        if isinstance(obj, dict):
            name = obj.get("name")
            if isinstance(name, str) and _is_key_header(name) and "value" in obj and valid(obj["value"]):
                return True
            # n8n nests key-named fields (e.g. parameters.options.idempotencyKey).
            if n8n and any(k.lower() in wanted and valid(v) for k, v in obj.items()):
                return True
            return any(named_valid(v) for v in obj.values())
        if isinstance(obj, list):
            return any(named_valid(v) for v in obj)
        return False

    for nested_key in ("parameters", "params", "headers"):
        if named_valid(step.get(nested_key)):
            return True
    return False


# ---------------------------------------------------------------------------
# Linting
# ---------------------------------------------------------------------------

def lint_step(step: dict, strict: bool, workflow: Any = None) -> list[dict]:
    """
    Lint a single step. Returns a list of issue dicts with keys:
      step_id, rule, severity, message
    """
    issues: list[dict] = []
    step_id = step.get("id") or step.get("name") or "<unnamed>"

    is_side_effect = _looks_like_side_effect(step, workflow)
    http_method = _get_http_method(step, workflow)
    write_op = _n8n_write_operation(step) if _is_n8n_workflow(workflow) else None
    db_write = _n8n_db_write(step) if _is_n8n_workflow(workflow) else None
    non_idempotent = http_method in NON_IDEMPOTENT_HTTP_METHODS or bool(write_op)
    retry_policy = _get_retry_policy(step)
    has_dlq = _has_dlq(step, workflow)
    has_idem_key = _has_idempotency_key(step, workflow)
    key_problems = _n8n_key_problems(step, workflow)

    if "static" in key_problems:
        issues.append({
            "step_id": step_id,
            "rule": "static-idempotency-key",
            "severity": "error",
            "message": "Idempotency key is a constant or not a well-formed expression reading the current item's data; derive it from the item's upstream business ID so distinct operations do not collide. To read another node's data for the current item, use .item (e.g. $('Webhook').item.json.id), not .first(), .last() or .all().",
        })
    if "unstable" in key_problems:
        issues.append({
            "step_id": step_id,
            "rule": "unstable-idempotency-key",
            "severity": "error",
            "message": "Idempotency key mixes item data with a per-execution, per-run, per-attempt or batch-level value ($execution, $runIndex, $now, $today, Date(), DateTime.now(), performance.now(), Math.random(), randomUUID(), .first()/.last()/.all(), $items(...)[n]); a retry or redelivery then sends a new key. Use only the item's upstream business ID, reading other nodes with .item.",
        })

    # Rule 1: Non-idempotent HTTP method or n8n write operation without idempotency key
    if non_idempotent and not has_idem_key:
        what = f"a {http_method.upper()} request" if http_method in NON_IDEMPOTENT_HTTP_METHODS else f"a '{write_op}' operation"
        issues.append({
            "step_id": step_id,
            "rule": "missing-idempotency-key",
            "severity": "error",
            "message": (
                f"Step performs {what} but has no idempotency key. "
                "Add an 'idempotency_key' or 'request_id' field (or an Idempotency-Key header) to prevent "
                "duplicate side effects on retry. If the node cannot carry a key, call the API through an "
                "HTTP Request node that can, or check the item's business ID against a dedupe store first."
            ),
        })

    # Rule 1b: n8n database write that is not idempotent by construction (DB nodes carry no key)
    if db_write == "write":
        issues.append({
            "step_id": step_id,
            "rule": "non-idempotent-db-write",
            "severity": "warning",
            "message": (
                f"Database write ('{_n8n_operation(step) or 'default operation'}') is not idempotent by "
                "construction or needs SQL review. Use a unique business key and stable replacement "
                "values; a conflict clause with an increment is not replay-safe."
            ),
        })

    # Rule 2: Side-effect step without retry policy (strict mode or HTTP)
    if is_side_effect and retry_policy is None:
        sev = "error" if http_method or write_op or strict else "warning"
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
    if is_side_effect and (non_idempotent or db_write or strict):
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
    if strict and is_side_effect and not has_idem_key and not non_idempotent and not db_write:
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


STEP_LIST_KEYS = ("steps", "tasks", "nodes", "activities", "jobs")


def _is_workflow_object(obj: Any) -> bool:
    return isinstance(obj, dict) and any(isinstance(obj.get(k), list) for k in STEP_LIST_KEYS)


def extract_steps(workflow: Any) -> list[dict]:
    """Extract the list of steps from various workflow JSON shapes."""
    if isinstance(workflow, list):
        return [s for s in workflow if isinstance(s, dict)]
    if isinstance(workflow, dict):
        for key in STEP_LIST_KEYS:
            val = workflow.get(key)
            if isinstance(val, list):
                return [s for s in val if isinstance(s, dict)]
    return []


def load_workflows(data: Any) -> list[tuple[str | None, Any]]:
    """Return (label, workflow) pairs to lint, or raise ValueError for non-workflow input.

    A top-level array made only of workflow objects (e.g. an n8n multi-workflow export)
    is linted workflow by workflow; any other array is a bare step array. Input with no
    steps at all is an error; one empty workflow inside a batch gets a no-steps warning.
    """
    if isinstance(data, dict):
        if not _is_workflow_object(data):
            raise ValueError("Not a workflow: expected an object with a 'steps', 'tasks', 'nodes', "
                             "'activities', or 'jobs' list, an array of such objects, or a bare step array.")
        pairs = [(None, data)]
    elif isinstance(data, list):
        if not data:
            raise ValueError("Empty array: nothing to lint.")
        if all(_is_workflow_object(item) for item in data):
            pairs = [(str(wf.get("name") or wf.get("id") or index), wf) for index, wf in enumerate(data)]
        else:
            pairs = [(None, data)]  # a bare step array; group steps with their own `steps` stay steps
    else:
        raise ValueError("Not a workflow: expected a JSON object or array.")
    if not any(extract_steps(wf) for _, wf in pairs):
        raise ValueError("No steps to lint: every workflow in the input is empty.")
    return pairs


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
    dlq_sinks = _n8n_dlq_sinks(workflow)
    for step in steps:
        if _is_n8n_workflow(workflow) and step.get("disabled") is True:
            continue  # a disabled n8n node never executes
        if step.get("name") in dlq_sinks:
            continue  # a DLQ target: see _n8n_dlq_sinks
        all_issues.extend(lint_step(step, strict, workflow))
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

    try:
        workflows = load_workflows(workflow)
    except ValueError as exc:
        print(json.dumps({"error": str(exc), "issues": [], "summary": {}}))
        return 2

    issues = []
    for label, wf in workflows:
        found = lint_workflow(wf, strict=args.strict)
        if label is not None:
            found = [dict(issue, workflow=label) for issue in found]
        issues.extend(found)

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
            where = f"workflow={issue['workflow']} " if "workflow" in issue else ""
            print(f"[{sev}] {where}step={sid} rule={rule}")
            print(f"       {msg}")
        print(f"\nSummary: {summary['errors']} error(s), {summary['warnings']} warning(s)")

    failing = errors if args.fail_on == "error" else issues
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
