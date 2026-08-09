"""
toolsearch_schema_loader_example.py

Demonstrates the ToolSearch schema-load pattern used in coding-agent runtimes.

ToolSearch is a two-phase mechanism:
  Phase 1 — Discovery: the model calls ToolSearch with a query.
             The runtime finds matching deferred tools and returns their schemas.
  Phase 2 — Execution: the model calls the loaded tool with the schema it just received.

This example shows how a runtime should implement Phase 1: receiving a ToolSearch
call, resolving matching deferred tools, loading their schemas, and returning
the schema payload to the model.

Requirements: Python 3.9+ stdlib only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class ToolSchema:
    """Minimal representation of a tool's JSON schema."""

    name: str
    description: str
    parameters: dict  # JSON Schema object
    origin: str = "builtin"  # "builtin" | "mcp" | "acp_delegated"
    always_load: bool = False
    should_defer: bool = False


@dataclass
class DeferredPool:
    """Registry of tools whose schemas are withheld from the initial tool list."""

    _tools: dict[str, ToolSchema] = field(default_factory=dict)

    def register(self, tool: ToolSchema) -> None:
        if tool.always_load:
            raise ValueError(
                f"Tool '{tool.name}' is marked always_load and must not be "
                "added to the deferred pool."
            )
        self._tools[tool.name] = tool

    def search(self, query: str) -> list[ToolSchema]:
        """
        Naive substring search over tool name and description.
        In production, replace with a vector-similarity or BM25 search.
        """
        q = query.lower()
        return [
            t
            for t in self._tools.values()
            if q in t.name.lower() or q in t.description.lower()
        ]

    def get(self, name: str) -> Optional[ToolSchema]:
        return self._tools.get(name)


# ---------------------------------------------------------------------------
# ToolSearch handler
# ---------------------------------------------------------------------------


def handle_toolsearch(
    query: str,
    deferred_pool: DeferredPool,
    toolsearch_enabled: bool = True,
    toolsearch_scope: str = "all",  # "all" | "mcp_only" | "builtins_only" | "none"
) -> dict:
    """
    Implements the ToolSearch tool call handler.

    Returns a dict that the runtime serialises as the ToolSearch tool result
    and sends back to the model.

    The model uses the returned schemas to construct its next tool call.
    """
    if not toolsearch_enabled or toolsearch_scope == "none":
        return {
            "tools_loaded": [],
            "error": "ToolSearch is disabled by policy.",
        }

    matches = deferred_pool.search(query)

    # Apply scope filter
    if toolsearch_scope == "mcp_only":
        matches = [t for t in matches if t.origin == "mcp"]
    elif toolsearch_scope == "builtins_only":
        matches = [t for t in matches if t.origin == "builtin"]

    if not matches:
        return {
            "tools_loaded": [],
            "message": f"No tools found for query: '{query}'",
        }

    # Return schemas the model can use to construct its next call
    return {
        "tools_loaded": [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
            for t in matches
        ]
    }


# ---------------------------------------------------------------------------
# Example: simulated agent turn
# ---------------------------------------------------------------------------


def simulate_toolsearch_turn() -> None:
    """
    Simulate a two-turn ToolSearch sequence:
      Turn 1: model calls ToolSearch → runtime loads schema
      Turn 2: model calls the loaded tool → runtime executes it
    """

    # --- Build a deferred pool with a few example tools ---

    pool = DeferredPool()

    pool.register(
        ToolSchema(
            name="mcp__slack__send_message",
            description="Send a message to a Slack channel",
            origin="mcp",
            should_defer=True,
            parameters={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel name, e.g. #general"},
                    "text": {"type": "string", "description": "Message text"},
                },
                "required": ["channel", "text"],
            },
        )
    )

    pool.register(
        ToolSchema(
            name="mcp__github__create_pull_request",
            description="Create a GitHub pull request for the current branch",
            origin="mcp",
            should_defer=True,
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                    "base": {"type": "string", "default": "main"},
                },
                "required": ["title"],
            },
        )
    )

    pool.register(
        ToolSchema(
            name="builtin__deep_codebase_index",
            description="Build a semantic index of the entire codebase",
            origin="builtin",
            should_defer=True,
            parameters={
                "type": "object",
                "properties": {
                    "root": {"type": "string", "description": "Repository root path"},
                },
                "required": ["root"],
            },
        )
    )

    # --- Turn 1: model calls ToolSearch ---

    print("=== Turn 1: Model calls ToolSearch ===")
    toolsearch_call = {"tool_name": "ToolSearch", "input": {"query": "slack send"}}
    print(f"Model → {json.dumps(toolsearch_call, indent=2)}\n")

    result = handle_toolsearch(
        query=toolsearch_call["input"]["query"],
        deferred_pool=pool,
        toolsearch_enabled=True,
        toolsearch_scope="all",
    )
    print(f"Runtime → ToolSearch result:\n{json.dumps(result, indent=2)}\n")

    # --- Turn 2: model calls the loaded tool ---

    print("=== Turn 2: Model calls loaded tool ===")
    tool_call = {
        "tool_name": "mcp__slack__send_message",
        "input": {"channel": "#general", "text": "Deployment complete."},
    }
    print(f"Model → {json.dumps(tool_call, indent=2)}\n")

    # Verify the tool is in the deferred pool (runtime would execute it here)
    loaded_tool = pool.get(tool_call["tool_name"])
    if loaded_tool is None:
        print("ERROR: Tool not found in deferred pool. This should not happen after ToolSearch.")
        return

    print(
        f"Runtime → executing '{loaded_tool.name}' "
        f"(origin: {loaded_tool.origin})\n"
        f"[in production: forward to MCP server, await result, return to model]\n"
    )


def simulate_toolsearch_not_found() -> None:
    """Simulate a ToolSearch call that returns no results."""
    pool = DeferredPool()  # empty pool

    print("=== ToolSearch: no results ===")
    result = handle_toolsearch(query="jira create ticket", deferred_pool=pool)
    print(json.dumps(result, indent=2))
    print()


def simulate_policy_disabled() -> None:
    """Simulate a session where ToolSearch is disabled by managed policy."""
    pool = DeferredPool()

    print("=== ToolSearch: disabled by policy ===")
    result = handle_toolsearch(
        query="slack send",
        deferred_pool=pool,
        toolsearch_enabled=False,
    )
    print(json.dumps(result, indent=2))
    print()


def simulate_scope_filter() -> None:
    """Simulate ToolSearch with scope restricted to MCP tools only."""
    pool = DeferredPool()
    pool.register(
        ToolSchema(
            name="builtin__deep_codebase_index",
            description="Semantic codebase indexer",
            origin="builtin",
            should_defer=True,
            parameters={"type": "object", "properties": {}, "required": []},
        )
    )
    pool.register(
        ToolSchema(
            name="mcp__search__web",
            description="Search the web",
            origin="mcp",
            should_defer=True,
            parameters={
                "type": "object",
                "properties": {"q": {"type": "string"}},
                "required": ["q"],
            },
        )
    )

    print("=== ToolSearch: scope=mcp_only (built-in excluded) ===")
    result = handle_toolsearch(
        query="search",
        deferred_pool=pool,
        toolsearch_scope="mcp_only",
    )
    print(json.dumps(result, indent=2))
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    simulate_toolsearch_turn()
    simulate_toolsearch_not_found()
    simulate_policy_disabled()
    simulate_scope_filter()
