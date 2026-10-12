"""
AI Coding Agent — Python Agent SDK Scaffolding

Minimal but production-ready scaffolding for building a coding agent
with the Claude Agent SDK. Customize the tools, hooks, and system prompt
for your specific coding task.

API shapes checked 2026-10-10 against
https://code.claude.com/docs/en/agent-sdk/python and .../agent-sdk/hooks.
Not executed: re-check the pages for your SDK version.

Usage:
    pip install claude-agent-sdk
    python sdk-agent-py.py "Review src/auth/ for security issues"
"""

import asyncio
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

# Resolve the current default model alias/ID via the claude-api skill or
# your provider config — do not hardcode a dated model snapshot here.
DEFAULT_CODING_MODEL = "sonnet"


# ─── Custom Tools ─────────────────────────────────────────────
# @tool(name, description, input_schema) wraps an async function that takes an
# args dict and returns an MCP-style content dict. Tools are served through
# create_sdk_mcp_server() and exposed as mcp__<server key>__<tool name>.

def _text(body: str) -> dict:
    return {"content": [{"type": "text", "text": body}]}


@tool(
    "run_tests",
    "Run the test suite and return results. Pass a specific test file path to run a subset.",
    {"test_path": str},
)
async def run_tests(args: dict) -> dict:
    """Run tests and return structured results."""
    import subprocess

    cmd = ["pytest", "--tb=short", "-q"]
    if args.get("test_path"):
        cmd.append(args["test_path"])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(Path.cwd()),
    )
    return _text(f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")


@tool(
    "run_linter",
    "Run the linter on a file or directory and return findings as structured text.",
    {"path": str},
)
async def run_linter(args: dict) -> dict:
    """Run linter and return findings."""
    import subprocess

    result = subprocess.run(
        ["ruff", "check", "--output-format", "json", args["path"]],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(Path.cwd()),
    )
    return _text(result.stdout or result.stderr or "No issues found.")


# ─── Hooks ────────────────────────────────────────────────────
# Hooks intercept tool calls for safety guardrails.
# Use PreToolUse to block dangerous operations.

PROTECTED_PATHS = [".env", "credentials", "secrets", "node_modules", ".git"]


async def pre_tool_hook(input_data, tool_use_id, context):
    """Deny writes to protected paths; an empty dict allows the call."""
    file_path = input_data["tool_input"].get("file_path", "")
    for protected in PROTECTED_PATHS:
        if protected in file_path:
            return {
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Cannot modify protected path containing '{protected}'",
                }
            }
    return {}


# ─── Agent Configuration ─────────────────────────────────────

SYSTEM_PROMPT = """You are a coding agent that reviews and improves code quality.

## Constraints

- Do not modify files outside the specified scope
- Do not delete files unless explicitly asked
- Run tests after every change to verify behavior preservation

## Workflow

1. Read the target files and understand the current code
2. Identify issues or improvements
3. Make targeted changes
4. Run tests to verify
5. Report findings and changes

## Output Contract

Produce a structured report with:
- Summary of changes made
- Test results (before and after)
- Any remaining issues or recommendations
"""


async def main():
    if len(sys.argv) < 2:
        print("Usage: python sdk-agent-py.py '<task description>'")
        sys.exit(1)

    task = sys.argv[1]

    options = ClaudeAgentOptions(
        model=DEFAULT_CODING_MODEL,  # resolve current alias/ID via the claude-api skill; avoid pinning a dated snapshot
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"dev": create_sdk_mcp_server(name="dev", tools=[run_tests, run_linter])},
        allowed_tools=["Read", "Grep", "Glob", "Edit", "mcp__dev__run_tests", "mcp__dev__run_linter"],
        max_turns=15,
        # Matchers match tool names, not paths; the callback checks the path.
        hooks={"PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[pre_tool_hook])]},
        # External MCP servers: see the mcp_servers entry in the Python SDK reference.
    )

    # Stream the agent's work
    async for message in query(prompt=task, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
                elif isinstance(block, ToolUseBlock):
                    print(f"\n[Tool: {block.name}]", flush=True)
        elif isinstance(message, ResultMessage) and message.is_error:
            print(f"\n[Error: {message.subtype}]", file=sys.stderr)

    print("\n\nAgent completed.")


if __name__ == "__main__":
    asyncio.run(main())
