# Browser Execution

How to drive the app under test as the persona, capture evidence, and emulate the persona's environment.

> Tool names and capabilities below drift with MCP server releases. Verify against the current official docs (Playwright MCP, Chrome DevTools MCP) before prescribing exact calls — inspect the installed tool schema alongside the linked official docs.

## Table of Contents

- [Tooling Selection](#tooling-selection)
- [Task Design: Bounded, Verifiable Scenarios](#task-design-bounded-verifiable-scenarios)
- [Session Protocol](#session-protocol)
- [Perception: Accessibility Tree First](#perception-accessibility-tree-first)
- [Environment Emulation](#environment-emulation)
- [Evidence Capture](#evidence-capture)
- [Playwright Script Fallback](#playwright-script-fallback)

## Tooling Selection

| Situation | Tool | Why |
|---|---|---|
| Default interactive persona session | Playwright MCP (`browser_navigate`, `browser_snapshot`, `browser_find`, `browser_click`, `browser_type`, `browser_fill_form`, `browser_wait_for`, `browser_take_screenshot`, `browser_resize`, `browser_console_messages`) | Accessibility-tree snapshots give element refs to act on; matches Claude Code/Codex MCP setups |
| Need console/network/performance evidence alongside UX signal | Chrome DevTools MCP (`navigate_page`, `new_page`, `take_snapshot`, `click`, `list_console_messages`, `list_network_requests`, `performance_start_trace`, `emulate`, `resize_page`) | Same driving ability plus DevTools-grade evidence and richer emulation for the Observation channel |
| High-volume re-checks of confirmed friction, token-constrained runs | Playwright CLI (`@playwright/cli`) | Official Microsoft companion to Playwright MCP. The agent issues shell commands (`goto`, `click`, `snapshot`, `find`, ...) and `snapshot` writes a compact YAML file with element refs to disk, so the model reads it on demand instead of receiving the full accessibility tree inline every turn |
| Headless CI, scheduled re-runs, no MCP available | Playwright script (Node/Python) | Deterministic, versionable; loses in-the-loop persona judgment, so scope it to re-checking known friction points |

**MCP vs. CLI for persona work.** Microsoft's own positioning is CLI for coding agents in large codebases where token/context budget is the binding constraint, MCP for long-running exploratory workflows where continuous in-context browser state matters more than token cost. Persona *discovery* sessions are exploratory and judgment-heavy — the persona reacts to what it perceives at each step — so **MCP stays the default here**. Reach for the CLI on the regression end of the loop: re-running a confirmed persona path across many builds. Practitioner reports cite a large token reduction for the CLI, but the specific figures trace back to secondary blogs rather than a primary Microsoft benchmark; treat the direction as reliable and the magnitude as unverified.

Before using a tool or enabling a capability, check the installed server's schema and [Playwright MCP documentation](https://github.com/microsoft/playwright-mcp). Look up supported capability flags, snapshot-search parameters, and output-file options there; do not infer support from another server release. Use a targeted snapshot search when supported and a full snapshot when orienting on a new screen.

## Task Design: Bounded, Verifiable Scenarios

Follow web-agent benchmark task design (WebArena, WebVoyager): each scenario is a specific, completable task with a checkable outcome — not "explore the app and share thoughts."

- Good: "Find out how much the Pro plan costs per month and start a trial" (success: trial-confirmation screen reached).
- Bad: "Look around the pricing area."
- Phrase the task in the persona's words in the profile; keep the success criterion observable in the UI (URL, text, element present).
- 3-7 scenarios per persona; order them the way the real journey orders them (discover → evaluate → sign up → first value).

## Session Protocol

1. **Fresh context per session** (one persona x one scenario). Cookies, auth, and cart state must not leak between scenarios. Enforce this mechanically, not by convention:
   - Chrome DevTools MCP: `new_page` with `isolatedContext: "{{persona}}-{{scenario}}"` — pages in different named contexts are fully isolated, pages sharing a name share cookies and storage. This is the cheapest correct way to run a persona pack without cross-contamination.
   - Playwright MCP: start the server in `--isolated` mode and close the browser (`browser_close`) between scenarios; the official docs specify that closing an isolated browser clears its session storage state. Closing a persistent-profile browser does not clear stored cookies. Verify the context is clean before starting the next scenario.
   - A returning-user scenario is the deliberate exception: reuse the context on purpose and say so in the session log, since the persona's stored state is the thing under test.
2. **Start at the persona's true entry point** — the marketing page, a search-engine-style landing, or the shared link. Never a deep link the persona wouldn't have.
3. **Loop per step**: snapshot → decide as the persona (consult persona state: mood, remaining patience) → act → observe result → log both channels in the session log.
4. **Enforce budgets mechanically**: count failed attempts and waits against the profile's budgets; when exhausted, record the abandonment and end the session.
5. **Timebox**: cap sessions (e.g., 25 steps or 10 minutes) so a stuck agent fails loud instead of looping.

## Perception: Accessibility Tree First

Prefer accessibility-tree snapshots (`browser_snapshot` / `take_snapshot`) over screenshots as the primary perception channel for structured controls, then check the rendered page when visibility or visual layout affects the persona. Benefits for persona testing:

- An accessibility snapshot can expose controls that a sighted persona has not noticed or that are visually obscured. Confirm visibility and the persona's available interaction mode before acting; tree presence does not establish discoverability or reachability.
- Element refs make actions reliable and loggable.

Use screenshots as **evidence** (attach to friction events) and as a secondary check when the persona's reaction depends on visual layout (crowding, contrast, hierarchy) that the tree can't convey. Missing accessible names in the snapshot are themselves findings — feed them to `qa-testing-accessibility`.

## Environment Emulation

Match the environment to the persona profile before the first step. Inspect the installed `emulate` schema and [official tool reference](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md) for accepted values and required page targeting before applying these example settings:

| Persona attribute | Emulation | Notes |
|---|---|---|
| Device / viewport | `emulate` `viewport: "375x812x3,mobile,touch"` (example) or a Playwright device/context configuration | Resizing alone changes dimensions; it does not enable mobile or touch behavior |
| Bandwidth | `emulate` `networkConditions: "Slow 3G"` (also `Fast 3G`, `Slow 4G`, `Fast 4G`, `Offline`) | Slow loads are exactly where low-patience personas abandon; an unthrottled desktop run silently hides this whole finding class |
| Older / cheaper device | `emulate` `cpuThrottlingRate` (accepted range from installed schema) | Calibrate against a target device or label the slowdown an assumed stress condition; a CPU factor is not a validated device proxy |
| Region | `emulate` `geolocation: "<lat>,<lon>"` | Reveals geo-gated pricing, currency, and content the persona would actually see |
| Dark/light preference | `emulate` `colorScheme` | Contrast and legibility bugs frequently exist in only one scheme |
| Locale/language | Launch args or app-level settings | Note untranslated strings as friction; `software-localisation` handles deep i18n audits |

Use `Offline` deliberately as a resilience probe: a persona on a train losing connection mid-checkout is a real scenario, and how the app recovers is often a severity-3+ finding.

## Evidence Capture

Every friction event needs at least one artifact:

| Evidence | How |
|---|---|
| Screenshot at the friction moment | `browser_take_screenshot` / `take_screenshot`; name it `{{persona}}-{{scenario}}-{{step}}.png` |
| Console errors | `browser_console_messages` / `list_console_messages` — capture at session end and after any visible error |
| Failed/slow requests | `list_network_requests` (Chrome DevTools MCP) when delay or dead-end friction occurs |
| Latency | Timestamp before/after waits; compare against the persona's wait tolerance |

Keep evidence file paths in the session log's Evidence column so the report can cite them.

## Playwright Script Fallback

When no MCP browser is available (CI, sandboxes), degrade gracefully:

1. Generate a Playwright script per scenario that replays the persona's known path and asserts the success criterion plus previously-found friction points (regression mode).
2. Persona *judgment* (think-aloud, new-friction discovery) cannot run in a plain script — mark such runs `mechanical re-check`, not full persona sessions, in the report.
3. For durable regression coverage of confirmed findings, hand off to `qa-testing-playwright` instead of growing this fallback.
