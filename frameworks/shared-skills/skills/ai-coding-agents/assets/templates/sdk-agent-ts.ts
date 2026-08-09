/**
 * AI Coding Agent — TypeScript Agent SDK Scaffolding
 *
 * Minimal but production-ready scaffolding for building a coding agent
 * with the Claude Agent SDK. Customize the tools, hooks, and system prompt
 * for your specific coding task.
 *
 * Usage:
 *     npm install @anthropic-ai/claude-agent-sdk
 *     npx tsx sdk-agent-ts.ts "Review src/auth/ for security issues"
 */

import {
  Agent,
  type AgentOptions,
  type HookEvent,
  createTool,
} from "@anthropic-ai/claude-agent-sdk";
import { execFileSync } from "child_process";
import { z } from "zod";

// Resolve the current default model alias/ID via the claude-api skill or
// your provider config — do not hardcode a dated model snapshot here.
const DEFAULT_CODING_MODEL = "sonnet";

// ─── Custom Tools ─────────────────────────────────────────────
// Wrap development tools as typed Agent SDK tools using Zod schemas.

const runTests = createTool({
  name: "run_tests",
  description:
    "Run the test suite and return results. Pass a specific test file path to run a subset.",
  inputSchema: z.object({
    testPath: z
      .string()
      .optional()
      .describe("Specific test file to run. Omit for full suite."),
  }),
  execute: async ({ testPath }) => {
    try {
      const args = ["jest", "--json"];
      if (testPath) args.push(testPath);
      const output = execFileSync("npx", args, {
        timeout: 120_000,
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "pipe"],
      });
      return output;
    } catch (error: any) {
      return `Exit code: ${error.status}\n\nSTDOUT:\n${error.stdout}\n\nSTDERR:\n${error.stderr}`;
    }
  },
});

const runLinter = createTool({
  name: "run_linter",
  description:
    "Run ESLint on a file or directory and return findings as JSON.",
  inputSchema: z.object({
    path: z.string().describe("File or directory path to lint."),
  }),
  execute: async ({ path }) => {
    try {
      const output = execFileSync("npx", ["eslint", "--format", "json", path], {
        timeout: 60_000,
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "pipe"],
      });
      return output;
    } catch (error: any) {
      return error.stdout || error.stderr || "No issues found.";
    }
  },
});

// ─── Hooks ────────────────────────────────────────────────────
// Intercept tool calls for safety guardrails.

const PROTECTED_PATHS = [".env", "credentials", "secrets", "node_modules", ".git"];

function preToolHook(event: HookEvent): HookEvent {
  if (
    (event.toolName === "Write" || event.toolName === "Edit") &&
    event.toolInput
  ) {
    const filePath = (event.toolInput as Record<string, string>).file_path ?? "";
    for (const protectedPath of PROTECTED_PATHS) {
      if (filePath.includes(protectedPath)) {
        event.block(
          `Blocked: cannot modify protected path containing '${protectedPath}'`
        );
        return event;
      }
    }
  }
  return event;
}

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

  const options: AgentOptions = {
    model: DEFAULT_CODING_MODEL, // resolve current alias/ID via the claude-api skill; avoid pinning a dated snapshot
    systemPrompt: SYSTEM_PROMPT,
    tools: [runTests, runLinter],
    maxTurns: 15,
    hooks: { preToolUse: preToolHook },
    // Uncomment for additional configuration:
    // mcpServers: [{ name: "eslint", command: "npx", args: ["@anthropic/eslint-mcp-server"] }],
    // allowedTools: ["Read", "Grep", "Glob", "Bash", "Edit", "Write"],
  };

  const agent = new Agent(options);

  for await (const event of agent.run(task)) {
    switch (event.type) {
      case "text":
        process.stdout.write(event.text);
        break;
      case "tool_use":
        console.log(`\n[Tool: ${event.toolName}]`);
        break;
      case "error":
        console.error(`\n[Error: ${event.error}]`);
        break;
    }
  }

  console.log("\n\nAgent completed.");
}

main().catch(console.error);
