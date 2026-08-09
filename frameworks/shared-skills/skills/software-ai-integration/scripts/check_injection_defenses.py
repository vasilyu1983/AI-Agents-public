#!/usr/bin/env python3
"""
check_injection_defenses.py — Lint an agent config JSON for prompt-injection defenses.

Usage:
    python3 check_injection_defenses.py <config.json> [--verbose]
    python3 check_injection_defenses.py --help

Exit codes:
    0 — all required defenses present (warnings only, if any)
    1 — one or more required defenses missing

Checks performed:
    1. tool_allowlist present and non-empty
    2. retrieval_source_allowlist present and non-empty
    3. output_validation.structured present and truthy
    4. prompt_isolation.system_prompt_immutable present and truthy
    5. (advisory) logging.enabled present and truthy
    6. (advisory) human_review_tools declared when high-privilege tools exist
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

class CheckResult:
    def __init__(self, name: str, passed: bool, severity: str, detail: str) -> None:
        self.name = name
        self.passed = passed
        self.severity = severity  # "error" | "warning"
        self.detail = detail

    def __repr__(self) -> str:
        status = "PASS" if self.passed else ("FAIL" if self.severity == "error" else "WARN")
        return f"[{status}] {self.name}: {self.detail}"


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

HIGH_PRIVILEGE_TOOLS = {
    "send_email", "sendEmail", "email_send",
    "write_file", "writeFile", "file_write",
    "http_request", "httpRequest", "fetch_url", "fetchUrl",
    "execute_code", "run_code", "shell", "bash",
    "delete_file", "deleteFile",
    "db_write", "database_write",
}


def check_tool_allowlist(config: dict[str, Any]) -> CheckResult:
    """Tool allowlist must be present and contain at least one entry."""
    allowlist = config.get("tools_allowed") or config.get("tool_allowlist") or config.get("allowed_tools")
    if allowlist and isinstance(allowlist, list) and len(allowlist) > 0:
        return CheckResult(
            "tool_allowlist",
            True,
            "error",
            f"{len(allowlist)} tool(s) explicitly allowed: {allowlist}",
        )
    return CheckResult(
        "tool_allowlist",
        False,
        "error",
        "No tool allowlist found. Without an allowlist, injected instructions can invoke any tool. "
        "Add 'tools_allowed': [...] with only the tools needed for this agent's task.",
    )


def check_retrieval_source_allowlist(config: dict[str, Any]) -> CheckResult:
    """Retrieval source allowlist restricts which data sources can be queried."""
    allowlist = (
        config.get("retrieval_sources")
        or config.get("retrieval_source_allowlist")
        or config.get("allowed_retrieval_sources")
    )
    if allowlist and isinstance(allowlist, list) and len(allowlist) > 0:
        return CheckResult(
            "retrieval_source_allowlist",
            True,
            "error",
            f"{len(allowlist)} retrieval source(s) defined: {allowlist}",
        )
    # Check for a nested retrieval config
    retrieval = config.get("retrieval") or {}
    if isinstance(retrieval, dict):
        sources = retrieval.get("sources") or retrieval.get("allowed_sources")
        if sources and isinstance(sources, list) and len(sources) > 0:
            return CheckResult(
                "retrieval_source_allowlist",
                True,
                "error",
                f"{len(sources)} retrieval source(s) in retrieval.sources: {sources}",
            )
    return CheckResult(
        "retrieval_source_allowlist",
        False,
        "error",
        "No retrieval source allowlist found. Without source restrictions, indirect injection via "
        "arbitrary external documents is possible. Add 'retrieval_sources': [...] or "
        "'retrieval.allowed_sources': [...] listing only trusted data sources.",
    )


def check_output_structured_validation(config: dict[str, Any]) -> CheckResult:
    """Output must be validated against a schema, not accepted as free-form text."""
    output_cfg = config.get("output_validation") or config.get("output") or {}
    if isinstance(output_cfg, dict):
        structured = output_cfg.get("structured") or output_cfg.get("schema_validation")
        if structured:
            schema = output_cfg.get("schema") or output_cfg.get("schema_ref")
            schema_note = f" (schema: {schema})" if schema else ""
            return CheckResult(
                "output_structured_validation",
                True,
                "error",
                f"Structured output validation enabled{schema_note}.",
            )
    # Also accept a top-level output_schema
    if config.get("output_schema"):
        return CheckResult(
            "output_structured_validation",
            True,
            "error",
            f"output_schema defined: {config['output_schema']}",
        )
    return CheckResult(
        "output_structured_validation",
        False,
        "error",
        "No structured output validation found. Free-form LLM output used as instructions or data "
        "without schema validation enables injection via unexpected output shapes. "
        "Add 'output_validation.structured': true and reference a schema.",
    )


def check_prompt_isolation(config: dict[str, Any]) -> CheckResult:
    """System prompt must be immutable at runtime; user/tool content must not modify it."""
    isolation = config.get("prompt_isolation") or {}
    if isinstance(isolation, dict):
        immutable = isolation.get("system_prompt_immutable")
        if immutable is True:
            return CheckResult(
                "prompt_isolation",
                True,
                "error",
                "prompt_isolation.system_prompt_immutable is true.",
            )
        if immutable is False:
            return CheckResult(
                "prompt_isolation",
                False,
                "error",
                "prompt_isolation.system_prompt_immutable is explicitly false. "
                "A mutable system prompt allows user or tool content to override agent instructions.",
            )
    # Key missing entirely
    return CheckResult(
        "prompt_isolation",
        False,
        "error",
        "No prompt_isolation config found. Without explicit isolation, it is unclear whether "
        "user or tool content can modify the system prompt at runtime. "
        "Add 'prompt_isolation': {'system_prompt_immutable': true, 'user_turn_scope': 'user_only', "
        "'tool_turn_scope': 'tool_only'}.",
    )


def check_logging_enabled(config: dict[str, Any]) -> CheckResult:
    """Advisory: logging should be enabled for audit and incident investigation."""
    logging_cfg = config.get("logging") or {}
    if isinstance(logging_cfg, dict) and logging_cfg.get("enabled"):
        return CheckResult(
            "logging_enabled",
            True,
            "warning",
            "logging.enabled is true.",
        )
    return CheckResult(
        "logging_enabled",
        False,
        "warning",
        "Logging not explicitly enabled. Without audit logs, prompt injection incidents cannot "
        "be investigated or attributed. Add 'logging': {'enabled': true, 'include_tool_calls': true}.",
    )


def check_human_review_for_high_privilege_tools(config: dict[str, Any]) -> CheckResult:
    """Advisory: high-privilege tools should require human review before execution."""
    allowed_tools = set(
        config.get("tools_allowed")
        or config.get("tool_allowlist")
        or config.get("allowed_tools")
        or []
    )
    high_priv_in_use = allowed_tools & HIGH_PRIVILEGE_TOOLS
    if not high_priv_in_use:
        return CheckResult(
            "human_review_high_privilege",
            True,
            "warning",
            "No high-privilege tools detected in allowlist.",
        )
    # High-privilege tools present — check for human review config
    require_confirmation = (
        config.get("require_confirmation")
        or config.get("human_review_tools")
        or config.get("human_in_the_loop")
    )
    if require_confirmation:
        confirmed = set(require_confirmation) if isinstance(require_confirmation, list) else set()
        uncovered = high_priv_in_use - confirmed
        if not uncovered:
            return CheckResult(
                "human_review_high_privilege",
                True,
                "warning",
                f"High-privilege tools {sorted(high_priv_in_use)} all have human review configured.",
            )
        return CheckResult(
            "human_review_high_privilege",
            False,
            "warning",
            f"High-privilege tools {sorted(uncovered)} are in the allowlist but not in "
            f"require_confirmation. An injection that triggers these tools will execute without "
            f"human approval.",
        )
    return CheckResult(
        "human_review_high_privilege",
        False,
        "warning",
        f"High-privilege tools detected ({sorted(high_priv_in_use)}) but no human review config "
        f"found. Add 'require_confirmation': {sorted(high_priv_in_use)} to require approval "
        f"before executing these tools.",
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

CHECKS = [
    check_tool_allowlist,
    check_retrieval_source_allowlist,
    check_output_structured_validation,
    check_prompt_isolation,
    check_logging_enabled,
    check_human_review_for_high_privilege_tools,
]


def run_checks(config: dict[str, Any]) -> list[CheckResult]:
    return [check(config) for check in CHECKS]


def print_report(config_path: Path, results: list[CheckResult], verbose: bool) -> int:
    errors = [r for r in results if not r.passed and r.severity == "error"]
    warnings = [r for r in results if not r.passed and r.severity == "warning"]
    passes = [r for r in results if r.passed]

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")

    print(f"## Injection Defense Check — {config_path.name}")
    print()
    print(f"Status : {status}")
    print(f"Errors : {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Passed : {len(passes)}")
    print()

    if errors:
        print("### Errors (required defenses missing)")
        for r in errors:
            print(f"  FAIL  {r.name}")
            print(f"        {r.detail}")
            print()

    if warnings:
        print("### Warnings (advisory)")
        for r in warnings:
            print(f"  WARN  {r.name}")
            print(f"        {r.detail}")
            print()

    if verbose and passes:
        print("### Passed")
        for r in passes:
            print(f"  PASS  {r.name}: {r.detail}")
        print()

    return 1 if errors else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Lint an agent config JSON for prompt-injection defenses. "
            "Exits 0 if no errors, 1 if required defenses are missing."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Checks:
  tool_allowlist                 tools_allowed / tool_allowlist must be a non-empty list
  retrieval_source_allowlist     retrieval_sources / retrieval.allowed_sources must be present
  output_structured_validation   output_validation.structured or output_schema must be truthy
  prompt_isolation               prompt_isolation.system_prompt_immutable must be true
  logging_enabled                (advisory) logging.enabled should be true
  human_review_high_privilege    (advisory) high-privilege tools should require confirmation

Example config:
  {
    "task_type": "document_summarization",
    "tools_allowed": ["read_document", "extract_sections"],
    "retrieval_sources": ["internal-knowledge-base"],
    "output_validation": {"structured": true, "schema": "SummarySchema"},
    "prompt_isolation": {"system_prompt_immutable": true},
    "logging": {"enabled": true, "include_tool_calls": true},
    "require_confirmation": []
  }
""",
    )
    parser.add_argument("config", help="Path to agent config JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show passing checks too")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)

    if not config_path.exists():
        print(f"Error: file not found: {config_path}", file=sys.stderr)
        return 1

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {config_path}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(config, dict):
        print(f"Error: config must be a JSON object, got {type(config).__name__}", file=sys.stderr)
        return 1

    results = run_checks(config)
    return print_report(config_path, results, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
