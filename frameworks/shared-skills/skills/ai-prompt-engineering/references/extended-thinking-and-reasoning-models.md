# Extended Thinking and Reasoning Models

Patterns and configuration for Claude Opus 4.8/Fable 5 adaptive thinking, GPT-5 / o-series reasoning, and general reasoning-model prompting.

Last updated: 2026-07. Verify API parameters against current documentation before shipping.

## Table of Contents

- [Claude Opus 4.8](#claude-opus-48)
- [Claude Fable 5 (claude-fable-5)](#claude-fable-5-claude-fable-5)
- [Claude Adaptive Thinking (claude-opus-4-7)](#claude-adaptive-thinking-claude-opus-4-7)
- [OpenAI o-series Reasoning Models (o3, o4-mini, o1)](#openai-o-series-reasoning-models-o3-o4-mini-o1)
- [Prompting Patterns for Reasoning Models](#prompting-patterns-for-reasoning-models)
- [Cost and Latency Trade-offs](#cost-and-latency-trade-offs)
- [Evaluation Checklist](#evaluation-checklist)

---

## Claude Opus 4.8

Claude Opus 4.8 (`claude-opus-4-8`) is Anthropic's most capable Opus-tier model as of May 2026 ($5/$25 per MTok, 1M context, 128k output).

Source: https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8 (verified 2026-06-09)

### API surface vs Opus 4.7

The API contract is **identical** to Opus 4.7. Code that runs on Opus 4.7 requires no changes for Opus 4.8:

- `temperature`, `top_p`, `top_k` at non-default values still return a 400 error.
- `thinking: {"type": "enabled", "budget_tokens": N}` still returns a 400 error.
- Adaptive thinking (`thinking: {"type": "adaptive"}`) and the `effort` parameter are the only thinking-on controls.
- The effort default on Opus 4.8 is `high` on all surfaces (including Claude Code) — set explicitly if you need a different level.

### New in Opus 4.8

- **Mid-conversation system messages**: `role: "system"` is now accepted immediately after a user turn. Preserves prompt-cache hits on earlier turns during long agentic loops.
- **Refusal stop details**: `stop_details` object is now publicly documented; describes the refusal category so applications can route the user appropriately.
- **Lower prompt-cache minimum**: 1,024 tokens on Opus 4.8 (vs a higher threshold on Opus 4.7). Prompts too short to cache on 4.7 may now cache with no code changes.
- **Fast mode** (research preview): set `speed: "fast"` for up to 2.5x higher output tokens per second at premium pricing. Verify current access and pricing at the what's-new page before enabling.

### Capability improvements

Compared with Opus 4.7: fewer wasted thinking tokens on bimodal workloads (the model decides per-turn whether to think), better tool triggering, better long-context handling in agentic traces.

---

## Claude Fable 5 (claude-fable-5)

Claude Fable 5 (`claude-fable-5`) is Anthropic's most capable widely released model as of June 9, 2026 ($10/$50 per MTok, 1M context, 128k output, GA).

Source: https://www.anthropic.com/news/claude-fable-5-mythos-5 (verified 2026-06-09)

### Thinking and effort

Adaptive thinking is **always on** for Fable 5 — unlike Opus 4.7/4.8 where it is off by default. You cannot disable it. The same `effort` parameter controls thinking depth. Prompting patterns from Opus 4.7/4.8 carry over: outcome-first prompts, under-specify the method, omit CoT scaffolding.

### Context and output prompting implications

1M context and 128k output are operational at launch. Sizing implications:
- Token budgets from Opus 4.7/4.8 carry over unchanged — both use the same tokenizer (introduced with Opus 4.7).
- With 1M input available, KV-cache strategy matters for cost (see `ai-llm-inference: kv-cache-optimization.md`).
- At 128k output, max_tokens headroom is the same as Opus 4.8 — do not reuse Opus 4.6 output budget figures.

### Safety-classifier fallback — prompting contract implications

Fable 5 includes an inline safety classifier. When requests about cybersecurity exploits, biology/chemistry dual-use, or model distillation trigger it (<5% of sessions on average), the response is served by **Claude Opus 4.8** instead of Fable 5.

**Prompt contract requirements**:
- Your output schema, tool definitions, error handling, and downstream parsers must work correctly for both Fable 5 and Opus 4.8 responses.
- Do not write prompts that depend on Fable 5-specific capability improvements and assume they always apply — fallback sessions will receive Opus 4.8 responses.
- Test your full prompt suite against Opus 4.8 explicitly as part of Fable 5 deployment validation.
- In production, monitor `stop_details` (now documented since Opus 4.8) to detect and count fallback-triggered sessions as a separate behavioral slice.

### Claude Mythos 5

`claude-mythos-5` is the same underlying model as Fable 5 with cybersecurity safeguards removed, available only via Project Glasswing (invitation only, no self-serve, deployed in collaboration with the US government). Not applicable to most production prompt engineering work.

### Expert judgment: Mythos-class model availability is not a stable dependency

Fable 5 launched June 9, 2026, was suspended for all users on June 12 after the US government imposed export controls following a discovered jailbreak technique, and was redeployed globally on July 1 with a tightened safety classifier (source: [Redeploying Claude Fable 5](https://www.anthropic.com/news/redeploying-fable-5), verified 2026-07-11). Two prompting-contract implications follow from this, independent of the specific dates:

- **Do not build a prompt contract that assumes a frontier model family will stay continuously available.** For any workflow with real uptime requirements, define and test a fallback path to a prior-generation model (here, Opus 4.8) before shipping — not as an afterthought once an outage happens. The safety-classifier-fallback contract described above already forces this; treat full-family suspension as the same class of risk, one severity level up.
- **A tightened safety classifier after a jailbreak disclosure raises false-positive refusals on legitimate requests** — Anthropic's own post-incident note says the improved classifier "flags more benign requests during routine coding tasks." If your eval suite's refusal-rate metric was calibrated before a classifier update, re-baseline it; a refusal-rate regression right after a provider-side security patch is not necessarily your prompt's fault.

---

## Claude Adaptive Thinking (claude-opus-4-7)

### What changed from Opus 4.6

`thinking: {"type": "enabled", "budget_tokens": N}` — **removed**. Sending this on `claude-opus-4-7` returns a **400 error**. Adaptive thinking (`thinking: {"type": "adaptive"}`) is the only supported thinking-on mode.

Adaptive thinking is **off by default** — requests with no `thinking` field run without thinking. Enable it explicitly when needed.

### API usage

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "Prove that sqrt(2) is irrational."}],
)

for block in response.content:
    if block.type == "thinking":
        print("THINKING:", block.thinking[:200], "...")
    else:
        print("ANSWER:", block.text)
```

### Effort levels (Messages API only)

`effort` is set in `output_config`. Claude Managed Agents handles effort automatically — do not set it manually there.

| effort | Use when |
|--------|----------|
| (omit) | Low-stakes, latency-critical tasks |
| `"high"` | Minimum for intelligence-sensitive work |
| `"xhigh"` | Coding and agentic use cases — highest quality |

```python
output_config = {"effort": "xhigh"}
```

### Thinking display: opt in to see reasoning

By default, thinking content is **omitted silently** from responses (no error, just empty `thinking` fields). This can appear as a long pause before output in streaming. To restore visible thinking:

```python
thinking = {
    "type": "adaptive",
    "display": "summarized",  # or "omitted" (default)
}
```

Use `"summarized"` when streaming reasoning to users or debugging model behavior.

### task_budget (beta)

Advisory token budget across the full agentic loop. The model sees a running countdown and scopes its work accordingly. Requires beta header `task-budgets-2026-03-13`.

```python
response = client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=128000,
    output_config={
        "effort": "high",
        "task_budget": {"type": "tokens", "total": 128000},
    },
    messages=[
        {"role": "user", "content": "Review the codebase and propose a refactor plan."}
    ],
    betas=["task-budgets-2026-03-13"],
)
```

Key rules:
- Minimum `task_budget.total` is 20,000 tokens.
- `task_budget` is advisory (model-visible soft cap across the loop); `max_tokens` is a hard per-request cap (not model-visible). Use both together.
- Do not set `task_budget` for open-ended tasks where quality matters more than token scope.

### Sampling parameters removed

**`temperature`, `top_p`, and `top_k` at any non-default value → 400 error on `claude-opus-4-7`.**

Migration: omit these parameters entirely. Use prompting to steer output style. The old advice to set `temperature=0` for determinism is moot — the parameter cannot be set and never guaranteed identical outputs anyway.

### Token-count note: new tokenizer

Claude Opus 4.7 uses a new tokenizer that may use ~1.0–1.35× as many tokens vs Opus 4.6 (up to ~35% more, workload-dependent). `count_tokens` returns different numbers per model version. Recompute token budgets, `max_tokens` headroom, and cost estimates per model version — do not carry over Opus 4.6 figures without re-measuring.

Source: https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7

### Streaming with adaptive thinking

```python
with client.messages.stream(
    model="claude-opus-4-7",
    max_tokens=8000,
    thinking={"type": "adaptive", "display": "summarized"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "Design a rate limiter."}],
) as stream:
    for event in stream:
        if hasattr(event, "type") and event.type == "content_block_delta":
            pass  # handle delta events
```

### Anti-patterns for adaptive thinking

- Enabling thinking for simple, single-step prompts — pure cost waste.
- Setting `thinking: {"type": "enabled", "budget_tokens": N}` — 400 error on Opus 4.7.
- Sending `temperature`, `top_p`, or `top_k` — 400 error on Opus 4.7.
- Relying on thinking content in downstream logic — not deterministic and not guaranteed.
- Disabling thinking mid-conversation — can confuse multi-turn state; keep the setting consistent.

---

## OpenAI o-series Reasoning Models (o3, o4-mini, o1)

> **o3 retirement note**: o3 is scheduled to retire from ChatGPT on August 26, 2026. If your o-series selection discussion includes o3, note this retirement date. For new implementations, prefer o4-mini (or GPT-5.5 for high-effort work) over o3. Verify current model availability at platform.openai.com before recommending a specific o-series model.

### What it is

The o-series models have reasoning tokens baked into the generation process. Unlike Claude adaptive thinking, reasoning is not directly visible in the API response — you see only the final output plus a `usage.completion_tokens_details.reasoning_tokens` count.

### API usage

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="o3",
    messages=[{"role": "user", "content": "Write a proof that there are infinitely many primes."}],
    max_completion_tokens=4096,
    # reasoning_effort controls how hard the model tries; options: "low", "medium", "high"
    # Available in Responses API and some chat completion endpoints
)

print(response.choices[0].message.content)
print("Reasoning tokens:", response.usage.completion_tokens_details.reasoning_tokens)
```

### reasoning_effort parameter (o3 / o4-mini)

Available via the Responses API (`/v1/responses`):

```python
response = client.responses.create(
    model="o3",
    input=[{"role": "user", "content": "Optimize this SQL query: ..."}],
    reasoning={"effort": "high"},  # "low" | "medium" | "high"
)
```

| effort | Token budget | Use when |
|--------|-------------|----------|
| `none` | None | GPT-5.5 only. Latency/cost-critical tasks where reasoning adds no value |
| `minimal` | Very light | GPT-5-class only. Near-instant responses; simple formatting/lookup tasks that still benefit from a token of reasoning |
| `low` | Minimal | Fast turnaround; simple tasks; latency-sensitive flows with complex instructions |
| `medium` | Balanced | Default; most production use — confirm `medium` is actually insufficient before reaching for `high`/`xhigh` |
| `high` | Heavy | Hard math, complex code, research synthesis |
| `xhigh` | Maximum | GPT-5.5 only. Long, agentic, reasoning-heavy work that prioritizes intelligence over speed/cost |

### Reasoning token cost

Reasoning tokens are billed as output tokens. At `high` effort, a single complex request can use 10,000+ reasoning tokens before producing output. Budget accordingly.

### GPT-5.5 patterns (April 2026)

Source: [OpenAI GPT-5.5 prompting guide](https://developers.openai.com/api/docs/guides/prompt-guidance?model=gpt-5.5). Verify against current docs before shipping.

**Default style shift.** GPT-5.5 is "efficient, direct, and task-oriented." It self-selects efficient solution paths when given room. Process-heavy scaffolding that older models needed now adds noise, narrows the search space, and produces mechanical answers. Treat reasoning effort as last-mile tuning, not the primary quality lever — first try clearer success criteria, verification loops, and tool persistence rules.

**Outcome-first prompts.** Describe destination, not every step.

```
# Anti-pattern (legacy, process-first)
First inspect A, then inspect B, then compare every field, then think through
all possible exceptions, then decide which tool to call, then call the tool,
then explain the entire process to the user.

# Preferred (GPT-5.5, outcome-first)
Resolve the customer's issue end to end.

Success means:
- the eligibility decision is made from the available policy and account data
- any allowed action is completed before responding
- the final answer includes completed_actions, customer_message, and blockers
- if evidence is missing, ask for the smallest missing field
```

**Recommended prompt template:**

```
Role: [1-2 sentences defining function, context, job]

# Personality       (tone, warmth, directness, formality, humor)
# Goal              (user-visible outcome)
# Success criteria  (what must be true before final answer)
# Constraints       (policy, safety, evidence, side-effect limits)
# Output            (sections, length, tone)
# Stop rules        (when to retry, fallback, abstain, ask, or stop)
```

Keep each section short. Personality controls *sound*; collaboration style (when to ask, assume, check work, handle uncertainty) controls *task behavior*. Neither replaces clear goals, success criteria, tool rules, or stopping conditions.

**Word-choice rule.** Use `ALWAYS`, `NEVER`, `must`, `only` for true invariants — safety rules, required output fields, actions that must never happen. For judgment calls, prefer decision rules (`prefer X when Y; otherwise Z`). Convergent guidance with Anthropic 4.7 (positive examples > negative "don't" lists).

**Migration warning.** "Avoid carrying over every instruction from an older prompt stack." Switch model → pin `reasoning_effort` → run evals → iterate one change at a time. Do not wholesale-rewrite legacy prompts.

**`text.verbosity` parameter.** API default is `medium`. Set `low` for shorter, more concise responses. Independent of `reasoning_effort`: a high-effort model can still produce a low-verbosity answer.

**`phase` parameter (multi-step Responses).** When using `previous_response_id` or manual assistant-item replay:

- `phase: "commentary"` for intermediate user-visible updates
- `phase: "final_answer"` for the completed answer
- Preserve assistant `phase` values exactly when replaying
- Do not add `phase` to user messages

**Preamble pattern (tool-heavy workflows).** Before any tool call in a multi-step task, emit one or two sentences acknowledging the request and stating the first step. This shows the first visible token before tool latency lands and improves perceived responsiveness in streaming.

**Retrieval budget pattern.** Don't reflex-search.

```
For ordinary Q&A, start with one broad search. If top results contain enough
citable support, answer from those results.

Search again only when:
- top results don't answer the core question
- a required fact, parameter, owner, date, ID, or source is missing
- the user asked for exhaustive coverage
- a specific document/URL/record must be read
- the answer would otherwise contain an important unsupported claim

Do not search again to improve phrasing, add nonessential examples, or
support wording that can safely be made generic.
```

**Citation gating for creative drafting.** Use retrieved facts for concrete product/customer/metric/roadmap/capability claims and cite them. Never invent specific names, first-party metrics, customer outcomes, or capabilities to make a draft sound stronger.

### GPT-5 (pre-5.5, general)

GPT-5 follows the same o-series interface patterns. Use `reasoning_effort` or `max_completion_tokens` to control depth. The 5.5 guidance above is the more current reference.

---

## Prompting Patterns for Reasoning Models

### Do: under-specify, not over-specify

Reasoning models perform best when given the goal and constraints, not a step-by-step method. Over-specifying the approach interferes with the model's internal reasoning.

```
# Good — state the goal and constraints
"Implement a thread-safe LRU cache in Python. Constraints: stdlib only,
O(1) get/put, handle concurrent reads from multiple threads."

# Avoid — prescribing the algorithm
"Implement a thread-safe LRU cache using an OrderedDict with a threading.Lock.
Follow these steps: 1) Create the dict 2) Add a lock 3) ..."
```

### Do: use system prompts for constraints, not instructions

```python
messages = [
    {"role": "system", "content": "You are a security auditor. Flag all SQL injection risks. Be concise."},
    {"role": "user", "content": code_snippet},
]
```

### Do: ask for structured output with JSON schema (OpenAI)

```python
response = client.chat.completions.create(
    model="o4-mini",
    messages=[{"role": "user", "content": "Analyse this codebase..."}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "issues": {"type": "array", "items": {"type": "string"}},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                },
                "required": ["issues", "severity"],
            },
        },
    },
)
```

### Do: match effort to task difficulty

| Task type | Claude | OpenAI |
|-----------|--------|--------|
| Simple lookup / short answer | thinking off | `o4-mini` low effort |
| Code review, logic | adaptive thinking + effort high | `o3` medium effort |
| Architecture analysis | adaptive thinking + effort xhigh | `o3` high effort |
| Math proofs, novel research | adaptive thinking + effort xhigh | `o3` high effort |

### Avoid: chain-of-thought prompting (CoT instructions)

Reasoning models have CoT built in. Adding "think step by step" or few-shot CoT examples in the prompt typically wastes tokens and can degrade quality.

```
# Avoid for o-series / adaptive thinking models
"Let's think step by step. First, ..."

# For standard non-reasoning models (gpt-4o, claude-haiku), CoT prompting is still useful
```

### Avoid: excessive formatting instructions in the system prompt

Reasoning models follow formatting instructions, but heavy format guidance in the system prompt can shorten the reasoning budget. Use the `response_format` parameter for structured output instead.

---

## Cost and Latency Trade-offs

| Dimension | Adaptive thinking | o-series high effort |
|-----------|------------------|---------------------|
| Latency | +2–10s over base | +5–30s over base |
| Cost multiplier | 2–5x over no-thinking | 3–8x over non-reasoning |
| Quality uplift | Significant for multi-step | Significant for hard tasks |
| Streaming | Supported | Supported |
| Cacheable prefix | Input only | Input only |

Note: Token cost estimates are model-version-dependent. The Claude Opus 4.7 tokenizer produces ~1.0–1.35× the tokens of Opus 4.6 for the same content. Re-measure cost at your actual production volume after any model upgrade.

---

## Evaluation Checklist

Before enabling adaptive thinking or high reasoning effort in production:

- [ ] Measure quality delta on a real eval set (not vibe-checking).
- [ ] Measure p95 latency with thinking enabled at your target effort level.
- [ ] Estimate monthly cost at production volume — using the specific model version's tokenizer.
- [ ] Confirm the use case is genuinely reasoning-bound (multi-step, ambiguous, novel).
- [ ] Set a cost alert for unexpected reasoning-token spikes.
- [ ] Confirm `temperature`, `top_p`, `top_k` are omitted from requests to `claude-opus-4-7`.
- [ ] Decide whether `"display": "summarized"` is needed for your streaming UX.
