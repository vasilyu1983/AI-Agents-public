/**
 * AI Coding Agent — TypeScript Agent SDK Scaffolding
 *
 * Minimal but production-ready scaffolding for building a coding agent
 * with the Claude Agent SDK. Customize the tools, hooks, and system prompt
 * for your specific coding task.
 *
 * API shapes checked 2026-10-10 against
 * https://code.claude.com/docs/en/agent-sdk/typescript and .../agent-sdk/hooks.
 * Not executed: re-check the pages for your SDK version.
 *
 * Usage:
 *     npm install @anthropic-ai/claude-agent-sdk
 *     npx tsx sdk-agent-ts.ts "Review src/auth/ for security issues"
 */

import {
  query,
  tool,
  createSdkMcpServer,
  type HookCallback,
  type Options,
  type PreToolUseHookInput,
} from "@anthropic-ai/claude-agent-sdk";
import { execFileSync } from "child_process";
import { z } from "zod";

// Resolve the current default model alias/ID via the claude-api skill or
// your provider config — do not hardcode a dated model snapshot here.
const DEFAULT_CODING_MODEL = "sonnet";

// ─── Custom Tools ─────────────────────────────────────────────
// tool(name, description, zodShape, handler) returns an MCP-style content result.
// Tools are served through createSdkMcpServer() and exposed as
// mcp__<server key>__<tool name>.

const text = (body: string) => ({ content: [{ type: "text" as const, text: body }] });

const runTests = tool(
  "run_tests",
  "Run the test suite and return results. Pass a specific test file path to run a subset.",
  { testPath: z.string().optional().describe("Specific test file to run. Omit for full suite.") },
  async ({ testPath }) => {
    try {
      const args = ["jest", "--json"];
      if (testPath) args.push(testPath);
      const output = execFileSync("npx", args, {
        timeout: 120_000,
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "pipe"],
      });
      return text(output);
    } catch (error: any) {
      return text(`Exit code: ${error.status}\n\nSTDOUT:\n${error.stdout}\n\nSTDERR:\n${error.stderr}`);
    }
  },
);

const runLinter = tool(
  "run_linter",
  "Run ESLint on a file or directory and return findings as JSON.",
  { path: z.string().describe("File or directory path to lint.") },
  async ({ path }) => {
    try {
      const output = execFileSync("npx", ["eslint", "--format", "json", path], {
        timeout: 60_000,
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "pipe"],
      });
      return text(output);
    } catch (error: any) {
      return text(error.stdout || error.stderr || "No issues found.");
    }
  },
);

// ─── Hooks ────────────────────────────────────────────────────
// Intercept tool calls for safety guardrails.

const PROTECTED_PATHS = [".env", "credentials", "secrets", "node_modules", ".git"];

// A hook returns {} to allow, or a deny decision inside hookSpecificOutput.
// Matchers match tool names, not paths; the callback checks the path.
const preToolHook: HookCallback = async (input) => {
  const pre = input as PreToolUseHookInput;
  const filePath = ((pre.tool_input as Record<string, unknown>)?.file_path as string) ?? "";
  for (const protectedPath of PROTECTED_PATHS) {
    if (filePath.includes(protectedPath)) {
      return {
        hookSpecificOutput: {
          hookEventName: pre.hook_event_name,
          permissionDecision: "deny" as const,
          permissionDecisionReason: `Cannot modify protected path containing '${protectedPath}'`,
        },
      };
    }
  }
  return {};
};

// ─── Agent Configuration ─────────────────────────────────────

const SYSTEM_PROMPT = `You are a coding agent that reviews and improves code quality.

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
`;

// ─── Main ────────────────────────────────────────────────────

async function main() {
  const task = process.argv[2];
  if (!task) {
    console.error('Usage: npx tsx sdk-agent-ts.ts "<task description>"');
    process.exit(1);
  }

  const options: Options = {
    model: DEFAULT_CODING_MODEL, // resolve current alias/ID via the claude-api skill; avoid pinning a dated snapshot
    systemPrompt: SYSTEM_PROMPT,
    mcpServers: { dev: createSdkMcpServer({ name: "dev", tools: [runTests, runLinter] }) }, // a record, not an array
    allowedTools: ["Read", "Grep", "Glob", "Edit", "mcp__dev__run_tests", "mcp__dev__run_linter"],
    maxTurns: 15,
    hooks: { PreToolUse: [{ matcher: "Write|Edit", hooks: [preToolHook] }] },
    // External MCP servers: see mcpServers in the TypeScript SDK reference.
  };

  for await (const message of query({ prompt: task, options })) {
    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if (block.type === "text") process.stdout.write(block.text);
        else if (block.type === "tool_use") console.log(`\n[Tool: ${block.name}]`);
      }
    } else if (message.type === "result" && message.subtype !== "success") {
      console.error(`\n[Error: ${message.subtype}]`);
    }
  }

  console.log("\n\nAgent completed.");
}

main().catch(console.error);
