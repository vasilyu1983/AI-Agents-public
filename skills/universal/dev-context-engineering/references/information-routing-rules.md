# Information Routing Rules

> **Source**: Adapted from [garrytan/gbrain](https://github.com/garrytan/gbrain) at commit `adb02b7826a010700efc968b18df8aaf17d8ffa1`. License: MIT. Extracted 2026-04-13.

When new information enters the session — something the user says, something an agent discovers, a decision made in conversation — it belongs in exactly one layer. Get the routing wrong and three failure modes appear: things get re-asked (because the answer lived in the wrong layer), things are lost on reset (because durable knowledge was saved only to session memory), or the hot layer bloats (because everything ends up in `AGENTS.md`).

## The Three Layers and Their Purposes

| Layer | What it stores | Survives agent reset? | Cost to read |
|-------|---------------|----------------------|--------------|
| **Compiled knowledge** (docs hub, brain, wiki) | World facts: people, systems, decisions, concepts, architecture | Yes | One retrieval hop |
| **Agent memory** (operational state) | How the agent should behave: preferences, tool configs, defaults | Depends on platform | In always-on context |
| **Session context** (conversation window) | What was just said, current task, immediate state | No — ephemeral | Free |

## The Boundary Test

For any new piece of information, ask: **"Is this about the world, or about how to operate?"**

- *World* → compiled knowledge layer. Facts about entities that are external to the agent and would matter even if you swapped the agent for a different one.
- *Operations* → agent memory. Guidance that changes how the agent behaves but isn't a fact about anything outside the agent.
- *Current conversation* → session. What's already in the window. No storage action needed.

## Worked Examples

| New information | Layer | Why |
|-----------------|-------|-----|
| "Pedro is CEO of Acme Corp" | Compiled knowledge | World fact — still true if you swap the agent |
| "Acme raised Series D at $1.2B in March" | Compiled knowledge | World fact — dateable, citable |
| "User prefers concise formatting with no preamble" | Agent memory | Operational — how to respond, not a fact about the world |
| "Always run the lint check before committing" | Agent memory | Operational — enforces behavior, doesn't describe reality |
| "The file I just pasted" | Session | Ephemeral — already in the window |
| "User's take on the zero-to-one framework" | Compiled knowledge | The user's *original thinking* is world content worth preserving — goes in an originals/ area, not memory |
| "API key for Stripe goes in `.env`" | Agent memory | Operational — a rule for the agent, not a fact about Stripe |

## The Three Failure Modes

1. **People in agent memory**: "Pedro prefers email over Slack" feels like a preference, but it is a fact *about Pedro*. If you store it in agent memory and the memory wipes on reset, you've lost knowledge that should survive forever. Put it on Pedro's page in the compiled layer.
2. **Preferences in the compiled layer**: "User likes bullet points over paragraphs" is about agent behavior, not about the world. Parking it in the docs hub clutters pages that should be about entities and decisions. Put it in agent memory.
3. **Durable facts in session only**: "We decided to use PostgreSQL" said in a single conversation and never written down is lost the moment the window rolls. If it's a decision that will matter next week, write it to the compiled layer *in the same turn* it gets made.

## Lookup Routing

Reading follows the same rule with a safety net: always check the compiled knowledge layer *before* reaching for an external API or the web.

1. Search the compiled layer for the entity or topic.
2. If found: read the relevant page(s). Use that data as the first-pass answer. External sources only fill gaps.
3. If not found: then and only then reach for external lookup.

Quote from the source: "An agent that reaches for the web before checking its own brain is wasting money and giving worse answers."

## When to Apply This

- **New repo with durable knowledge needs**: apply from day one. Set up the compiled layer structure and the boundary test before the first session.
- **Existing repo with a bloated `AGENTS.md`**: audit each section. For every item, ask "world or operations?" Move world content out to docs, keep operations in the hot layer.
- **Multi-agent setup**: the compiled layer is the shared ground truth. Agent memory stays per-agent; the compiled layer is portable across agents.

## Related

- [fast-track-guide.md](fast-track-guide.md) — Setting up the initial layer structure in a new repo
- [multi-repo-strategy.md](multi-repo-strategy.md) — How the three layers distribute across repos when knowledge and behavior have different portability requirements
- [context-resolver-pattern.md](context-resolver-pattern.md) — The routing layer that connects "user asks X" to "load compiled-layer document Y"
