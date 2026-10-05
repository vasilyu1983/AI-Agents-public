# Playwright Test Agents, MCP & AI-Powered Testing

Current Playwright AI workflows have three adjacent pieces:
- **Playwright Test Agents** for planning, generation, and healing inside the Playwright ecosystem.
- **Playwright MCP** for structured browser control through accessibility snapshots.
- **Chrome DevTools MCP** for performance tracing, network debugging, console inspection, and Lighthouse audits via Chrome DevTools Protocol.

---
## Table of Contents

- [Overview](#overview)
- [Initialize Playwright Test Agents in a project](#initialize-playwright-test-agents-in-a-project)
- [MCP server package](#mcp-server-package)
- [How MCP Works](#how-mcp-works)
- [Accessibility Tree Approach](#accessibility-tree-approach)
- [Architecture](#architecture)
- [Agent Roles (Playwright Test Agents)](#agent-roles-playwright-test-agents)
- [1. Planner](#1-planner)
- [2. Generator](#2-generator)
- [3. Healer](#3-healer)
- [Integration with AI Tools](#integration-with-ai-tools)
- [Claude Desktop](#claude-desktop)
- [IDE Agents (MCP-Capable)](#ide-agents-mcp-capable)
- [Cursor IDE (Example)](#cursor-ide-example)
- [Self-Healing and Natural-Language Authoring](#self-healing-and-natural-language-authoring)
- [Best Practices](#best-practices)
- [Do](#do)
- [Avoid](#avoid)
- [Browser Installation](#browser-installation)
- [Manual installation if needed](#manual-installation-if-needed)
- [Configuration Options](#configuration-options)
- [Limitations](#limitations)
- [Agent Evidence Artifacts (Playwright 1.59+)](#agent-evidence-artifacts-playwright-159)
- [Action annotations](#action-annotations)
- [Video receipt](#video-receipt)
- [Bound browser session](#bound-browser-session)
- [Dashboard review pattern](#dashboard-review-pattern)
- [Review checklist for agent-authored tests](#review-checklist-for-agent-authored-tests)
- [Related Resources](#related-resources)


## Overview

Use official Playwright Test Agents first when you want Playwright-native planning / generation / healing workflows. Use Playwright MCP when your coding agent or IDE needs a structured browser tool interface.

Official docs:
- Playwright Test Agents: https://playwright.dev/docs/test-agents
- Playwright MCP repo: https://github.com/microsoft/playwright-mcp

Quick start:

```bash
# Initialize Playwright Test Agents in a project
npx playwright init-agents

# With IDE-specific loop (regenerate when Playwright updates)
npx playwright init-agents --loop=claude    # Claude Code
npx playwright init-agents --loop=vscode    # VS Code / Copilot
npx playwright init-agents --loop=opencode  # OpenCode
npx playwright init-agents --loop=codex     # Codex

# Playwright MCP server
npx -y @playwright/mcp@latest

# Chrome DevTools MCP server
npx -y chrome-devtools-mcp@latest
```

Playwright MCP bridges Large Language Models (LLMs) with Playwright-managed browsers. It enables AI agents to control web interactions through structured accessibility snapshots rather than screenshots.

**Key characteristics:**
- Fast and lightweight (uses accessibility tree, not pixels)
- LLM-friendly (no vision models required)
- Deterministic tool application (structured data, not ambiguous screenshots)

Official repository: https://github.com/microsoft/playwright-mcp (package: `@playwright/mcp`)

---

## How MCP Works

### Accessibility Tree Approach

MCP operates on the browser's accessibility tree - a semantic, hierarchical representation of UI elements:

```text
Snapshot mode includes:
- Roles (button, textbox, link, heading)
- Labels ("Submit", "Email address")
- States (disabled, checked, expanded)
- Hierarchy (parent-child relationships)
```

This approach is more reliable than screenshot-based automation because:
- No visual noise or rendering differences
- Consistent across browsers and platforms
- Faster processing (no image analysis)
- Deterministic element identification

### Architecture

```text
LLM/agent <-> MCP server <-> Playwright (browser control)
```

---

## Agent Roles (Playwright Test Agents)

These roles are now documented in Playwright Test Agents. Treat outputs as suggestions and always review diffs and assertions.

### 1. Planner

Explores the application and produces a Markdown test plan:

```text
Input: "Test the checkout flow"
Output: Markdown plan with:
- User journey steps
- Expected assertions
- Edge cases to cover
- Data requirements
```

### 2. Generator

Transforms Markdown plans into Playwright Test files:

```typescript
// Generated from plan
import { test, expect } from '@playwright/test';

test('checkout flow - happy path', async ({ page }) => {
  await page.goto('/cart');
  await page.getByRole('button', { name: 'Checkout' }).click();
  // ... generated steps
});
```

### 3. Healer

Executes test suites and automatically repairs failing tests:

- Identifies broken locators
- Suggests updated selectors
- Fixes timing issues
- Adapts to UI changes

---

## Integration with AI Tools

### Claude Desktop

Configure in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

### IDE Agents (MCP-Capable)

For IDE agents that support MCP, configure the Playwright MCP server and ask the agent to use structured snapshots to explore flows, then convert the plan into hardened Playwright tests.

### Cursor IDE (Example)

Add to Cursor's MCP configuration:

```json
{
  "playwright": {
    "command": "npx",
    "args": ["-y", "@playwright/mcp@latest"],
    "env": {
      "PLAYWRIGHT_MCP_HEADLESS": "true"
    }
  }
}
```

---

## Self-Healing and Natural-Language Authoring

MCP lets an agent inspect the accessibility tree, propose updated locators when a UI refactor breaks a test, and turn a plain-language request into Playwright code. Treat AI-authored or AI-healed locators as a draft: require the semantic priority order (`getByRole` → `getByLabel`/`getByText` → `getByTestId`) and a human or second-agent review before merge (see the review checklist below).

## Best Practices

### Do

- Use Playwright Test Agents or MCP for scaffolding, then review and harden
- Leverage accessibility tree for stable locators
- Combine with human review for critical tests
- Use healer workflows for maintenance, not blind trust

### Avoid

- Auto-healing that weakens assertions
- Generating tests without understanding the flow
- Skipping code review of AI-generated tests
- Using MCP for security-sensitive test creation

---

## Chrome DevTools MCP (Complementary)

Chrome DevTools MCP is a separate MCP server from Google that connects AI agents directly to Chrome's DevTools Protocol. Use it alongside Playwright MCP when you need Chrome-specific debugging and performance analysis.

Official repo: https://github.com/ChromeDevTools/chrome-devtools-mcp
Blog: https://developer.chrome.com/blog/chrome-devtools-mcp

### When to Use Which

| Need | Use | Why |
|------|-----|-----|
| Test generation & scaffolding | Playwright MCP | Accessibility tree + test code output |
| Cross-browser testing | Playwright MCP | Chromium, Firefox, WebKit support |
| Performance tracing & analysis | Chrome DevTools MCP | CrUX integration, trace insights |
| Network request debugging | Chrome DevTools MCP | Full request/response inspection |
| Console inspection (source-mapped) | Chrome DevTools MCP | Source-mapped stack traces |
| Lighthouse audits | Chrome DevTools MCP | Built-in `lighthouse_audit` tool |
| Memory profiling | Chrome DevTools MCP | `take_heapsnapshot` tool (Memory category) |
| Form filling & navigation | Either | Both support input automation |

### Tools

Chrome DevTools MCP's tool count and categories change between releases; verify against [`docs/tool-reference.md`](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md) before quoting a number. Check tool names and `--slim` availability against that reference and the installed CLI help; `--headless` and `--isolated` (see Security below) are the two flags worth setting explicitly for CI/agent use.

### Security: Profile Isolation

The blast radius of these flags depends on which browser the agent is attached to. Connecting to an existing Chrome instance via `--browserUrl` (or an equivalent `--autoConnect`-style flag in other MCP browser tools) attaches the agent to that browser's default profile — with access to **all open windows** of that profile: logged-in email, banking, GitHub sessions, saved cookies. A page with injected instructions, opened in any tab of that profile, combined with an agent holding your authenticated browser, is the worst-case combination for prompt injection.

Default to `--isolated` (or a dedicated, non-default profile with no connect flags). Testing localhost almost never needs your real logged-in sessions. Use `--browserUrl` / connect-to-existing-Chrome only when the test genuinely needs real authenticated state, and close unrelated tabs first.

This is **not** the same "isolation" discussed elsewhere in this skill set — persona/test-state isolation (see `qa-persona-testing`) is about preventing state bleed between simulated users in the same test run. This section is about the operator's real browser profile and its live sessions being reachable by the automation tool. Knowing one does not mean you're covered on the other.

Source: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), skill `browser-testing-with-devtools`, commit `7676817c12a1317454ae3898a0c5c1eacf5dd3d5` (MIT).

### Requirements

- Chrome: current stable or newer (auto-downloads via Puppeteer if missing)
- Node.js: v20.19+ or latest LTS
- Platforms: macOS, Linux, Windows 11

### Connection Modes

- **Automatic** (default): Chrome launches on first tool use
- **Manual**: Connect to existing Chrome via `--browserUrl http://127.0.0.1:9222`

---

## `@playwright/cli` vs MCP: Decision Table

Both tools are maintained by Microsoft. Choose based on your agentic loop's priorities.

| Criterion | `@playwright/cli` | Playwright MCP (`@playwright/mcp`) |
|-----------|------------------|-------------------------------------|
| Token cost | Lower (shell commands) | Higher (persistent MCP protocol overhead) — the official docs describe the difference only qualitatively; measure token use in your own loop before quoting a figure |
| Interface | Shell commands (Bash tool) | MCP protocol (JSON tool calls) |
| Context persistence | Commands operate on a reusable browser session | Persistent browser session |
| Best for | High-throughput coding agents; CI debugging; large codebases | Exploratory automation; self-healing; long-running agent loops |
| Schema loading | None | Requires loading tool schemas each session |
| Setup | `npx @playwright/cli` (no config) | MCP server config in client |

When in doubt for Claude Code or Cursor: start with `@playwright/cli` for most E2E authoring; switch to MCP when you need iterative page inspection or self-healing loops.

---

## v1.59 Agentic APIs

Three new APIs in v1.59 are specifically useful for agent-driven test workflows:

**`browser.bind(name, opts)`** — makes a launched browser available to `playwright-cli`, `@playwright/mcp`, and other clients without re-launching. It returns a named-pipe endpoint by default, or a `ws://` URL when you pass `host`/`port`:
```typescript
const browser = await chromium.launch();
const { endpoint } = await browser.bind('my-session', { workspaceDir: '/my/project' });
// playwright-cli attach my-session
// @playwright/mcp --endpoint=my-session
await browser.unbind(); // stop accepting new connections
```

**`page.screencast`** — programmatic video recording with precise start/stop, frame capture, and action annotations (`page.screencast.start({ path })` / `page.screencast.stop()`). Replaces the need to rely on `video: 'on'` for agent evidence:
```typescript
await page.screencast.start({ path: 'recording.webm' });
// ... perform agent actions ...
await page.screencast.stop();
```

**`npx playwright trace`** — CLI-based trace analysis (no browser UI needed); pipe into agent output for failure reasoning. Subcommands: `open <trace.zip>`, `actions [--grep=...]`, `action <n>`, `snapshot <n> --name <before|after>`, `close`:
```bash
npx playwright trace open test-results/example-trace.zip
npx playwright trace actions --grep="expect"
npx playwright trace action 9
```

---

## Browser Installation

Since Playwright v1.57, Playwright runs on Chrome for Testing builds (not plain Chromium). Headed mode uses `chrome`, headless uses `chrome-headless-shell` — pass `--only-shell` during install if you only run headless (common in CI) to skip downloading the full headed browser.

```bash
# Manual installation if needed
npx playwright install chromium
npx playwright install firefox
npx playwright install webkit
```

---

## Configuration Options

```json
{
  "playwright": {
    "command": "npx",
    "args": ["-y", "@playwright/mcp@latest"],
    "env": {
      "PLAYWRIGHT_MCP_HEADLESS": "true",
      "PLAYWRIGHT_MCP_BROWSER": "chromium",
      "PLAYWRIGHT_MCP_VIEWPORT_SIZE": "1280x720"
    }
  }
}
```

---

## Limitations

- Native mobile apps not supported (DOM-based only)
- Complex visual assertions require human verification
- AI suggestions need code review
- Not a replacement for test strategy thinking

---

## Agent Evidence Artifacts (Playwright 1.59+)

Playwright 1.59 added three patterns that make agent-driven test runs reviewable without re-executing them. Use them as **review artifacts** for any test step authored or healed by an agent — they are the receipt that lets a human (or a second agent) verify what actually happened.

### Action annotations

Wrap agent-generated logical actions in `test.step('...', async () => { ... })`. The trace viewer treats each `test.step` as a collapsible segment with its own snapshots and console output. For agents, this is the equivalent of a commit message on a single physical action — it makes traces self-documenting.

`test.step` also accepts an options object — `test.step('name', fn, { timeout, box: true })`. Set a per-step `timeout` (ms) on agent-generated steps that call slow external services, instead of raising the whole test's timeout; `box: true` points errors thrown inside the step at the step's call site rather than its internals, which keeps agent-authored failure output readable.

```typescript
test('signup flow', async ({ page }) => {
  await test.step('navigate to landing', async () => { /* … */ });
  await test.step('submit email form (agent-generated)', async () => { /* … */ });
});
```

### Video receipt

Always enable video capture for any test an agent authored, healed, or modified — even when the test passes. The video is the artifact a human reviews before merging an agent-generated PR.

```typescript
// playwright.config.ts
use: {
  video: { mode: 'retain-on-failure', size: { width: 1280, height: 720 } },
}

// Per-test override for agent-authored work — keep video on success too:
test.use({ video: 'on' });
```

Pair with `trace: 'on'` for agent-authored tests so the reviewer has both a click-by-click DOM trace and a literal screen recording.

### Bound browser session

For long-running agent loops (planner → generator → healer), bind the browser once (`browser.bind(name)`, above) and reuse it across iterations via `playwright-cli attach <name>` or an MCP `--endpoint` connection, instead of re-launching per step. This cuts startup overhead and lets the agent observe state changes incrementally.

```typescript
import { chromium } from '@playwright/test';

const browser = await chromium.launch();
const { endpoint } = await browser.bind('agent-loop', { workspaceDir: 'agent-evidence/' });
const context = await browser.newContext({
  recordVideo: { dir: 'agent-evidence/' },
});
const page = await context.newPage();
// agent loop here — other tools attach via `endpoint` while this context stays open…
await context.close();   // flushes video file for the reviewer
await browser.unbind();
```

### Dashboard review pattern

For PRs that include agent-authored or agent-healed tests, post the HTML report (`npx playwright show-report`) and per-step trace links as a PR comment. This gives the reviewer a single dashboard URL instead of asking them to clone-and-run. CI snippet:

```yaml
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: agent-evidence-${{ github.run_id }}
    path: |
      playwright-report/
      test-results/**/trace.zip
      test-results/**/video.webm
```

### Review checklist for agent-authored tests

Before merging any test scaffolded or healed by an agent, the reviewer should confirm:

1. Each logical action is wrapped in `test.step` with a description matching what the action does (no boilerplate "step 1 / step 2").
2. Locators use the semantic priority (`getByRole` → `getByLabel` → `getByText` → `getByTestId`) — not generated CSS or XPath.
3. Video and trace artifacts exist and the reviewer has watched the failing path or the modified path.
4. No `page.waitForTimeout` was reintroduced by self-healing.
5. Auth state and storage state are explicit, not inferred from agent context.

---

## Related Resources

- [Microsoft Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Playwright CLI (`@playwright/cli`)](https://www.npmjs.com/package/@playwright/cli) — official token-efficient CLI alternative to MCP; use shell commands instead of MCP protocol (the docs describe it as token-efficient without a number; measure your own token usage before citing a specific comparison figure)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Chrome DevTools MCP Blog](https://developer.chrome.com/blog/chrome-devtools-mcp)
- [Playwright test.step API](https://playwright.dev/docs/api/class-test#test-step)
- [Playwright video API](https://playwright.dev/docs/videos)
