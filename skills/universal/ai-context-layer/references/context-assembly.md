# Context Assembly

## Table of Contents

- [Inputs](#inputs)
- [Outputs](#outputs)
- [Surface Rules](#surface-rules)
- [Emotional Context and Tone Modulation](#emotional-context-and-tone-modulation)
- [Memory Injection Site](#memory-injection-site)
- [Projection Rules](#projection-rules)
- [Context Compression](#context-compression)
- [Token Budget Management](#token-budget-management)

Context assembly is the layer that turns many sources into a usable per-surface bundle.

## Inputs

- actor and owner scope
- target surface
- task or intent
- latency budget
- trust requirement
- entitlement or policy state

## Outputs

- `live_facts`
- `memory`
- `domain_evidence`
- `relationship_context`
- `guardrails`
- `projection`

## Surface Rules

Different surfaces need different bundles:

- dashboard: more deterministic summaries, less prose
- chat: evidence-bearing derived prompt context
- workflow or automation: action-oriented structured context
- email or push: compact, derived, policy-safe context only

## Emotional Context and Tone Modulation

Context assembly should influence not just *what* the AI says, but *how* it says it. This is especially important for consumer-facing products where emotional resonance drives retention.

### Emotional signals as assembly inputs

- **Mood signal**: capture user's current emotional state as an explicit input to context assembly. This can come from a dedicated mood picker, a journaling/tracking surface, or inferred from interaction patterns.
- **Emotional frame**: generate a warm, human-readable narrative from the same data that produces raw context metadata. Example: instead of "Trust: high, Coverage: 0.87, Signals: natal_chart, transits", produce "I drew on your Scorpio rising and your recent questions about career shifts." This is a presentation-layer transform of existing context metadata.
- **Tone modulation**: the mood signal should influence the AI's response register. When a user is low/frustrated, the AI should lead with empathy. When the user is energized, the AI can match that energy.

### Cross-surface signal flow

Signals captured on one surface should be available as assembly inputs on other surfaces:

- Mood/energy captured in a journaling surface should flow into a chat/ask surface's context.
- Decision signals from a dashboard should deep-link into an ask surface with pre-filled context.
- Feedback reactions from chat should update memory confidence scores that affect all surfaces.

This requires either a shared signal store (backend) or explicit client-side signal passing (e.g., passing last-known mood with ask submissions).

### Anti-patterns

- Treating tone as a static brand voice instead of a dynamic response to user state.
- Exposing raw context metadata (trust levels, coverage scores) to end users — present the emotional frame instead, collapse technical details for power users.
- Assuming the same tone works across emotional states — a 200-word evidence-rich answer to a frustrated user will feel cold.

## Memory Injection Site

Where a retrieved memory lands in the window is a design decision with real
consequences — it changes the authority the model assigns the memory, the cost of
the call, and which retrieval architectures remain available. Two placements, and a
hybrid.

### System-prompt placement

Append retrieved memories to the system instructions, framed as foundational
context for the whole interaction.

- **Gains**: high authority; clean separation between context and dialogue; the
  right home for stable global facts such as a user profile.
- **Risk — over-influence**: the agent starts relating every topic back to the
  memories in its core instructions, even where they are irrelevant.
- **Constraint — dynamic construction**: the system prompt must be rebuilt per call
  from the current retrieval result. Not every agent framework supports this.
- **Constraint — incompatible with memory-as-a-tool**: the system prompt is finalized
  before the model can decide to call a retrieval tool, so the two patterns cannot
  both drive the same slot.
- **Constraint — poor for multimodal**: most models accept text-only system
  instructions, so images and audio cannot be embedded there.

### Dialogue-history placement

Inject memories into the turn-by-turn conversation, either before the full history
or immediately before the latest user turn. Retrieving memories via a tool call is a
special case of this — the memories arrive as tool output inside the dialogue.

- **Noisier**: raises token cost and can confuse the model when the retrieved
  memories turn out to be irrelevant to the turn.
- **Risk — dialogue injection**: the model may treat an injected memory as something
  that was actually said in the conversation.
- **Perspective rule**: memories injected under the `user` role must be written in
  the first person, or the perspective mismatch itself becomes a confusion source.

### Recommended hybrid

Use the system prompt for the stable profile — facts that should always be present —
and dialogue injection or memory-as-a-tool for transient episodic memories relevant
only to the immediate context. This keeps persistent context persistent without
paying its cost on every turn for facts that are only situationally useful.

<!-- Source: Milam & Gulli, "Context Engineering: Sessions, Memory" (Google, Nov 2025), pp. 61-63 -->

## Projection Rules

- send derived and bounded fields to the model
- keep secrets and internal raw state out of the prompt
- use per-surface allowlists
- cap token budgets aggressively

## Context Compression

Not all context needs full fidelity. Use compression to fit more value into bounded budgets:

- **Progressive disclosure**: load a summary first, fetch full detail only when the task requires it.
- **Sliding-window summarization**: for conversation history, summarize older turns and keep recent turns verbatim. The window size depends on the surface and task.
- **Compression before retrieval**: summarize or classify the query intent before choosing which retrieval sources to call. Reduces wasted retrieval budget on irrelevant sources.
- **Tiered context**: separate always-present context (guardrails, actor identity) from on-demand context (deep domain evidence, relationship graphs). Load tiers lazily.

Compression is a context assembly concern, not a retrieval concern. The assembly layer decides what to compress and when.

## Token Budget Management

Every context bundle should have an explicit token budget per surface:

- **Priority ordering**: guardrails > live_facts > memory > domain_evidence > relationship_context. When the budget is tight, drop the lowest-priority slices first.
- **Hard caps per surface**: dashboard (2K-4K tokens), chat (4K-8K), workflow (2K-6K), email/push (1K-2K). Tune to your model and latency target. **Tokenizers change between model releases**, so the same text can cost noticeably more tokens on a newer model. Re-measure caps on the production model after every model change; do not reuse ratios from another model. Where the provider offers an advisory task or effort budget across a full agentic loop (distinct from `max_tokens`), use it alongside hard per-surface caps for long-horizon agents.
- **Truncation policy**: never truncate mid-evidence or mid-memory. Drop entire slices rather than producing partial context that could mislead the model.
- **Budget monitoring**: track actual bundle sizes against budgets. Alert when bundles consistently exceed 80% of budget, which signals context creep.
