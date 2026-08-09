# Recipe: ToolSearch Deferred-Tool Results in the REPL

How ToolSearch tool calls and their results render in the terminal REPL. ToolSearch is a two-step flow: the model calls `ToolSearch` to get schemas, then calls the loaded tool. Both steps produce REPL events that must be rendered distinctly.

## Table of Contents

- [Overview of the two-step flow](#overview-of-the-two-step-flow)
- [Step 1 — Rendering the ToolSearch call](#step-1--rendering-the-toolsearch-call)
- [Step 2 — Rendering the loaded tool's execution](#step-2--rendering-the-loaded-tools-execution)
- [Step 3 — Handling ToolSearch with no results](#step-3--handling-toolsearch-with-no-results)
- [Step 4 — Permission prompt for a deferred tool](#step-4--permission-prompt-for-a-deferred-tool)
- [Step 5 — Scroll and focus behavior](#step-5--scroll-and-focus-behavior)
- [Component structure (pseudocode)](#component-structure-pseudocode)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

## Overview of the two-step flow

```
Turn N:
  Model → ToolSearch({query: "slack send"})
  Runtime → loads schema for mcp__slack__send_message
  Runtime → returns schema JSON as tool result

Turn N (same turn, second tool call):
  Model → mcp__slack__send_message({channel: "#general", text: "..."})
  Runtime → executes tool, returns result
  REPL → renders tool-use + tool-result as normal
```

The REPL must render the ToolSearch call itself (turn N, step 1) differently from a normal tool call, because the "result" is not a user-visible action — it is a schema document the model consumes.

## Step 1 — Rendering the ToolSearch call

ToolSearch tool-use events should render as a **discovery annotation**, not as a tool-result block:

```
┌─────────────────────────────────────────────────────────────────┐
│ ⟳ Loading tool: mcp__slack__send_message                        │
│   query: "slack send"                                           │
└─────────────────────────────────────────────────────────────────┘
```

Rules:
- Use a spinner or "loading" icon (not a checkmark) — discovery is not an action.
- Show the matched tool name(s), not the raw schema JSON.
- If ToolSearch returned multiple schemas, show a collapsed count: "2 tools loaded."
- Do not show the full schema JSON in the main REPL stream; that is model-internal.
- After the subsequent tool call completes, collapse the ToolSearch annotation to a single line: `⟳ Loaded mcp__slack__send_message`.

## Step 2 — Rendering the loaded tool's execution

Once ToolSearch has loaded the schema and the model calls the tool, render it identically to any other tool call. No special treatment for "this was deferred":

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙ mcp__slack__send_message                                       │
│   channel: "#general"                                           │
│   text: "Deployment complete"                                   │
├─────────────────────────────────────────────────────────────────┤
│ ✓ Message sent (ts: 1714204800.123456)                          │
└─────────────────────────────────────────────────────────────────┘
```

## Step 3 — Handling ToolSearch with no results

When ToolSearch finds no matching tools, render a distinct "not found" annotation:

```
┌─────────────────────────────────────────────────────────────────┐
│ ⊘ ToolSearch: no tools found for "jira create ticket"           │
│   Tip: check that the MCP server is connected                   │
└─────────────────────────────────────────────────────────────────┘
```

Rules:
- Do not render a tool-result block with an empty schema. That leaks model-internal state.
- Provide a brief diagnostic hint if the reason is likely actionable (MCP server disconnected, tool disabled by policy).
- If `toolsearch_enabled = false` in settings, ToolSearch should not appear in the tool list at all. This state should never reach the REPL renderer.

## Step 4 — Permission prompt for a deferred tool

If the loaded tool requires a permission prompt (e.g., network access, file write), the approval dialog appears after ToolSearch loads the schema — not before. The ToolSearch annotation and the approval dialog are sequential renders:

```
1. ⟳ Loading tool: mcp__filesystem__write_file
2. [Approval dialog: "mcp__filesystem__write_file wants to write to /tmp/output.txt. Allow?"]
3. ✓ File written: /tmp/output.txt
```

The ToolSearch annotation must be collapsed or dimmed before the approval dialog gains focus so the user is not reading schema text when they should be making an approval decision.

## Step 5 — Scroll and focus behavior

- The ToolSearch annotation must not steal scroll focus. If the user has scrolled up to read earlier history, a ToolSearch annotation appearing at the bottom must not jump the scroll position.
- If `auto_scroll` is enabled (the user is at the bottom of history), the annotation does auto-scroll — standard behavior.
- ToolSearch annotations are part of the transcript model; they must be included in virtual scroll range calculations. Do not skip them in the height estimation step.

## Component structure (pseudocode)

```typescript
function renderToolUse(event: ToolUseEvent): RenderedBlock {
  if (event.tool_name === "ToolSearch") {
    return renderToolSearchAnnotation(event);
  }
  return renderStandardToolUse(event);
}

function renderToolSearchAnnotation(event: ToolUseEvent): RenderedBlock {
  const query = event.input?.query ?? "";
  const loaded = event.result?.tools_loaded ?? [];
  const notFound = loaded.length === 0;

  if (notFound) {
    return {
      icon: "⊘",
      text: `ToolSearch: no tools found for "${query}"`,
      hint: inferHint(event),
      collapsed: false,
    };
  }

  return {
    icon: "⟳",
    text: `Loading tool: ${loaded.map(t => t.name).join(", ")}`,
    query,
    collapsed: false,          // expand during loading
    onComplete: (block) => {   // collapse after the real tool call lands
      block.icon = "⟳";
      block.text = `Loaded ${loaded.map(t => t.name).join(", ")}`;
      block.collapsed = true;
    },
  };
}
```

## Anti-patterns

- Rendering ToolSearch the same as a regular tool call (with a ✓ checkmark and a "result" section). It misleads users into thinking an action was taken when only a schema was loaded.
- Showing raw JSON schema output in the REPL stream. The model consumes that; users should not have to scroll past 200-line schema dumps.
- Not collapsing the ToolSearch annotation after the real tool call completes. In long sessions with many deferred tool loads, uncollapsed annotations accumulate and bury the actual work.
- Blocking the approval dialog behind the ToolSearch annotation. Approval is the safety-critical event; it must be the most salient render in the viewport when it appears.

## Related

- [`input-state-machine.md`](input-state-machine.md) — Input states and overlay behavior
- [`repl-message-input-and-history.md`](repl-message-input-and-history.md) — REPL ownership and message rendering
- [`../../ai-coding-agents-tools/references/deferral-eligibility-decision-tree.md`](../../ai-coding-agents-tools/references/deferral-eligibility-decision-tree.md) — When a tool should be deferred
- [`../../ai-coding-agents-settings-policy/references/deferred-tool-policy-layer.md`](../../ai-coding-agents-settings-policy/references/deferred-tool-policy-layer.md) — How ToolSearch is settings-gated
