# Authoring Evaluations for a Custom MCP Server

Use this when a custom MCP server is stable enough to ship and you need a repeatable way to check whether its tools actually work for an agent — not just that the server starts and the Inspector can list tools, but that a real agent using real tool descriptions can complete real tasks with them.

## Why a Separate Eval Set (Not Just the Minimum Acceptance Checks)

`references/mcp-custom.md`'s Minimum Acceptance Checks confirm the server *runs correctly* (tool list loads, one call succeeds, errors are clean, pagination works). They do not confirm the server is *usable by an agent* — that tool names and descriptions are precise enough for correct tool selection, that a multi-step task actually completes, and that the answer the agent produces is checkable. Eval questions test that second, harder property.

## The Spec: 10 Questions, 6 Criteria Each

Author exactly **10 evaluation questions** per server before considering it ready for broader use. Write questions before the server is "done," not after — writing them earlier surfaces missing tools and unclear descriptions while they're still cheap to fix.

Each question must meet all six criteria:

| Criterion | What it rules out |
|---|---|
| **Independent** | The question doesn't depend on state left behind by a previous question or a particular run order |
| **Read-only** | Answering it doesn't require a destructive or state-changing tool call — the eval set itself shouldn't need cleanup or a fresh environment between runs |
| **Complex** | Answering it requires more than one tool call — a single `get_x(id)` lookup doesn't exercise tool chaining or the agent's ability to plan a sequence |
| **Realistic** | The question resembles something a real user of this server would actually ask, not a synthetic edge case invented to be hard |
| **Verifiable** | The correct answer is a single value or short string checkable by exact or near-exact string comparison — not a paragraph a grader has to judge subjectively |
| **Stable** | The answer will not change over time (avoid "how many open tickets are there right now" against live data; prefer counts/facts anchored to fixed records or a frozen fixture) |

Verify each question yourself — solve it using only the server's tools before shipping it — rather than trusting that a question "looks answerable." A question you can't personally answer with the tools as described is a defect in either the question or the tool surface, and you want to find out which before an agent hits it.

## Output Format

Output the question set as machine-checkable blocks so a test harness can run them without a human reading each answer:

```xml
<qa_pair>
  <question>Which customer placed order #4821, and what is their account status?</question>
  <answer>jane.doe@example.com, active</answer>
</qa_pair>
```

One `<qa_pair>` per question, in the order authored. Keep `<answer>` to the exact string (or short delimited list) a harness can compare against the agent's final output — not a sentence.

## Worked Example

Bad (fails Complex + Verifiable):
> "Tell me about our top customers." — no single tool chain produces this, and "tell me about" has no checkable answer.

Good:
> "What is the shipping status of the most recent order placed by the customer with email `jane.doe@example.com`?" — requires `find_customer_by_email` → `list_orders(customer_id, sort=recent, limit=1)` → `get_order_status(order_id)` (Complex), the record is fixed in test fixtures (Stable), the answer is one word like `shipped` (Verifiable), no tool in the chain mutates data (Read-only), it doesn't depend on any other question having run first (Independent), and it's the kind of thing a support agent would actually ask (Realistic).

## Where This Fits the Workflow

Run eval authoring after the server passes `references/mcp-custom.md`'s Minimum Acceptance Checks and before Registry Publishing. A server with 10 verified qa_pairs that an agent can solve using only its tool descriptions is meaningfully more trustworthy than one that merely starts and responds — treat the eval set as part of the deliverable, not optional polish.

## Related

- [mcp-custom.md](mcp-custom.md) — Minimum Acceptance Checks and Production Checklist (run before this)
- [../SKILL.md](../SKILL.md) — Quick reference
