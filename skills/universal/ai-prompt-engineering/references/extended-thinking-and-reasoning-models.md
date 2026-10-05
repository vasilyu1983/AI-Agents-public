# Extended Thinking and Reasoning Models

Provider-neutral rules for prompting and configuring reasoning models (models with native thinking, reasoning tokens, or an effort control).

This file holds judgment, not a model roster. Model names, prices, parameter names, beta flags, defaults and availability change often. Look them up in the provider's current model page, parameter reference and migration guide each time you write code.

## Table of Contents

- [Lookup Step Before Configuring](#lookup-step-before-configuring)
- [Configuration Rules](#configuration-rules)
- [Prompting Patterns for Reasoning Models](#prompting-patterns-for-reasoning-models)
- [Availability and Fallback](#availability-and-fallback)
- [Cost and Latency](#cost-and-latency)
- [Evaluation Checklist](#evaluation-checklist)

---

## Lookup Step Before Configuring

Before you set any reasoning or sampling parameter for a specific model, check these in the provider's current documentation:

1. **Sampling parameters.** Does the model accept `temperature`, `top_p`, `top_k` at non-default values? Some reasoning models reject them with an error; others ignore them silently.
2. **Reasoning control.** What is the model's thinking or effort control called, what levels does it take, is it on or off by default, and can it be disabled?
3. **Reasoning visibility.** Is thinking content returned, summarized, or omitted by default? Omitted thinking can look like a long pause before the first streamed token.
4. **Budgets.** Is there a hard output cap only, or also a model-visible advisory budget for a multi-step loop?
5. **Tokenizer.** Did the tokenizer change from the model you are replacing? Token counts, cost and `max_tokens` headroom then change for the same text.
6. **Structured output.** Which native schema-output mode does the model support, and which schema features does that mode accept?

Record what you looked up (date, doc URL) next to the config, so the next person knows what to re-check.

## Configuration Rules

- **Set reasoning depth through the provider's effort or thinking control, not through prompt text.** Look the control up per model; do not copy levels or defaults from another model or provider.
- **Omit sampling parameters on models that reject or ignore them.** Steer style with the prompt instead.
- **Temperature 0 is not a determinism strategy.** It is not available on every model, and where it is available it does not guarantee identical outputs. Get determinism from explicit schemas, closed-set output vocabularies, null-fallback rules and post-generation validation. For evaluation, see the repeated-runs rule in [prompt-testing-ci-cd.md](prompt-testing-ci-cd.md#evaluate-on-production-settings-with-repeats).
- **Pair an advisory budget with a hard cap.** If the provider offers a model-visible budget for a whole agentic loop, use it together with the per-request hard output cap. Do not set an advisory budget on open-ended tasks where quality matters more than token scope.
- **Keep the thinking setting constant within a conversation.** Switching it mid-conversation can confuse multi-turn state, and on some providers it invalidates the cached message prefix.
- **Never put thinking content into downstream logic.** It is not deterministic, not guaranteed to be returned, and may be summarized. Parse only the final answer.
- **Opt in to visible or summarized thinking only for debugging or a deliberate UX need**, and look up the display option per model.

## Prompting Patterns for Reasoning Models

### Do: state the outcome, not the method

Reasoning models do best with the goal, the success criteria and the constraints. A prescribed step-by-step method narrows the model's search and produces mechanical answers.

```
# Avoid — process-first
First inspect A, then inspect B, then compare every field, then think through
all possible exceptions, then decide which tool to call, then call the tool,
then explain the entire process to the user.

# Prefer — outcome-first
Resolve the customer's issue end to end.

Success means:
- the eligibility decision is made from the available policy and account data
- any allowed action is completed before responding
- the final answer includes completed_actions, customer_message, and blockers
- if evidence is missing, ask for the smallest missing field
```

```
# Good — goal and constraints
"Implement a thread-safe LRU cache in Python. Constraints: stdlib only,
O(1) get/put, handle concurrent reads from multiple threads."

# Avoid — prescribing the algorithm
"Implement a thread-safe LRU cache using an OrderedDict with a threading.Lock.
Follow these steps: 1) Create the dict 2) Add a lock 3) ..."
```

A compact section order that works across providers:

```
Role: [1-2 sentences defining function, context, job]

# Goal              (user-visible outcome)
# Success criteria  (what must be true before the final answer)
# Constraints       (policy, safety, evidence, side-effect limits)
# Output            (sections, length, tone)
# Stop rules        (when to retry, fall back, abstain, ask, or stop)
```

Keep each section short. Tone guidance controls how the answer sounds; stop rules and success criteria control task behavior. Neither replaces the other.

### Do: use the system prompt for constraints, not procedures

```python
messages = [
    {"role": "system", "content": "You are a security auditor. Flag all SQL injection risks. Be concise."},
    {"role": "user", "content": code_snippet},
]
```

### Do: reserve absolute words for true invariants

Use `ALWAYS`, `NEVER`, `must` and `only` for invariants: safety rules, required output fields, actions that must never happen. For judgment calls, write decision rules ("prefer X when Y; otherwise Z"). Positive examples work better than long "don't" lists.

### Do: use native schema output instead of heavy format instructions

Heavy formatting instructions in the system prompt can shorten the model's reasoning. When you need structured output, use the provider's native schema-output mode (look up its name and supported schema subset) and keep the prompt about the task. Schema design rules (field order, enums, nullables, repair loop) are in [core-patterns.md](core-patterns.md#schema-design-for-llm-output).

### Do: match reasoning depth to task difficulty

| Task type | Reasoning setting |
|-----------|-------------------|
| Simple lookup, short answer, formatting | thinking off or the lowest effort level |
| Code review, logic, most production work | the provider's default or medium level; confirm it is insufficient before raising it |
| Architecture analysis, hard debugging | high effort |
| Proofs, novel research, long agentic work | the highest level, after a cost check |

Treat effort as last-mile tuning. Clearer success criteria, verification loops and tool-persistence rules usually move quality more.

### Do: budget retrieval and gate citations

```
For ordinary Q&A, start with one broad search. If top results contain enough
citable support, answer from those results.

Search again only when:
- top results don't answer the core question
- a required fact, parameter, owner, date, ID, or source is missing
- the user asked for exhaustive coverage
- a specific document/URL/record must be read
- the answer would otherwise contain an important unsupported claim
```

In drafting tasks, use retrieved facts for concrete product, customer, metric, roadmap and capability claims and cite them. Never invent names, first-party metrics or customer outcomes to make a draft sound stronger.

### Do: send a short preamble before the first tool call

In tool-heavy streaming flows, emit one or two sentences that acknowledge the request and state the first step before any tool call. The user sees a first token before tool latency lands.

### Avoid: chain-of-thought instructions

Reasoning models reason natively. "Think step by step" or few-shot chain-of-thought examples usually waste tokens and can lower quality. Do not ask for visible chain of thought; ask for the final answer plus a short justification or checks if you need an audit trail. Explicit chain-of-thought prompting is still useful on non-reasoning models.

### Avoid: carrying every instruction over from an older prompt stack

When migrating to a new model: switch the model, fix the reasoning setting, run the evals, then change one thing at a time. Do not rewrite a legacy prompt wholesale, and do not keep process scaffolding the new model no longer needs.

---

## Availability and Fallback

- **Do not assume a frontier model family stays continuously available.** Safety incidents, export controls and capacity limits can suspend a model or route requests to a different model with no notice. For any workflow with uptime requirements, define and test a fallback model path before shipping.
- **Some providers serve a flagged request from a different model** (for example, when an inline safety classifier fires). The output schema, tool definitions, error handling and parsers must work for every model that can answer. Run the full prompt suite against the fallback model, and track fallback-served sessions as a separate slice using the provider's stop or refusal metadata.
- **Re-baseline refusal metrics after a provider safety update.** A tightened classifier raises false-positive refusals on benign requests. A refusal-rate jump right after a provider-side change is not evidence that your prompt got worse.

## Cost and Latency

- Reasoning tokens are normally billed as output tokens; check the provider's pricing page. A hard request at high effort can spend thousands of reasoning tokens before any output.
- Latency and cost multipliers depend on model, effort level and workload. Measure them on your own traffic; do not reuse figures from another model or from a blog post.
- Caching discounts apply to a repeated input prefix, not to the reasoning tokens a request generates.
- After any model change, re-measure token counts with the new model's tokenizer before reusing budgets or cost estimates.

---

## Evaluation Checklist

Before enabling thinking or a higher effort level in production:

- [ ] Measure the quality delta on a real eval set, with repeated runs (not vibe-checking).
- [ ] Measure p95 latency at the target effort level.
- [ ] Estimate monthly cost at production volume with the target model's tokenizer.
- [ ] Confirm the use case is reasoning-bound (multi-step, ambiguous, novel).
- [ ] Set a cost alert for reasoning-token spikes.
- [ ] Confirm sampling parameters are omitted for models that reject or ignore them (from the lookup step).
- [ ] Decide whether visible or summarized thinking is needed for the streaming UX.
- [ ] Run the suite against every fallback model that can serve the same request.
