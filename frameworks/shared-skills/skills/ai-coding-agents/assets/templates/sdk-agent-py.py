"""
AI Coding Agent — Python Agent SDK Scaffolding

Minimal but production-ready scaffolding for building a coding agent
with the Claude Agent SDK. Customize the tools, hooks, and system prompt
for your specific coding task.

Usage:
    pip install claude-agent-sdk
    python sdk-agent-py.py "Review src/auth/ for security issues"
"""

import asyncio
import sys
from pathlib import Path

from claude_agent_sdk import (
    Agent,
    AgentOptions,
    Tool,
    tool,
    HookEvent,
)

# Resolve the current default model alias/ID via the claude-api skill or
# your provider config — do not hardcode a dated model snapshot here.
DEFAULT_CODING_MODEL = "sonnet"


# ─── Custom Tools ─────────────────────────────────────────────
# Wrap development tools as typed Agent SDK tools.
# The @tool decorator registers the function as an agent-callable tool.

@tool(
    name="run_tests",
    description="Run the test suite and return results. Pass a specific test file path to run a subset.",
)
async def run_tests(test_path: str = "") -> str:
    """Run tests and return structured results."""
    import subprocess

    cmd = ["pytest", "--tb=short", "-q"]
    if test_path:
        cmd.append(test_path)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(Path.cwd()),
    )
    return f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"


@tool(
    name="run_linter",
    description="Run the linter on a file or directory and return findings as structured text.",
)
async def run_linter(path: str) -> str:
    """Run linter and return findings."""
    import subprocess

    result = subprocess.run(
        ["ruff", "check", "--output-format", "json", path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(Path.cwd()),
    )
    return result.stdout or result.stderr or "No issues found."


# ─── Hooks ────────────────────────────────────────────────────
# Hooks intercept tool calls for safety guardrails.
# Use PreToolUse to block dangerous operations.

PROTECTED_PATHS = [".env", "credentials", "secrets", "node_modules", ".git"]


def pre_tool_hook(event: HookEvent) -> HookEvent:
    """Block writes to protected paths."""
    if event.tool_name in ("Write", "Edit") and event.tool_input:
        file_path = event.tool_input.get("file_path", "")
        for protected in PROTECTED_PATHS:
            if protected in file_path:
                event.block(f"Blocked: cannot modify protected path containing '{protected}'")
                return event
    return event


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

    agent = Agent(
        AgentOptions(
            model=DEFAULT_CODING_MODEL,  # resolve current alias/ID via the claude-api skill; avoid pinning a dated snapshot
            system_prompt=SYSTEM_PROMPT,
            tools=[run_tests, run_linter],
            max_turns=15,
            hooks={"pre_tool_use": pre_tool_hook},
            # Uncomment for additional configuration:
            # mcp_servers=[{"name": "eslint", "command": "npx", "args": ["@anthropic/eslint-mcp-server"]}],
            # allowed_tools=["Read", "Grep", "Glob", "Bash", "Edit", "Write"],
        )
    )

    # Stream the agent's work
    async for event in agent.run(task):
        if event.type == "text":
            print(event.text, end="", flush=True)
        elif event.type == "tool_use":
            print(f"\n[Tool: {event.tool_name}]", flush=True)
        elif event.type == "error":
            print(f"\n[Error: {event.error}]", file=sys.stderr)

    print("\n\nAgent completed.")


if __name__ == "__main__":
    asyncio.run(main())
