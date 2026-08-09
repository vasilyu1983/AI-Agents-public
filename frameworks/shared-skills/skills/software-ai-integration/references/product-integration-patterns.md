# Product Integration Patterns

Use this file when the request is about product UX and systems behavior around AI features rather than raw model choice.

## Streaming UX

- Stream from the first token unless the task is explicitly batch/offline.
- Preserve user context when retries happen; do not wipe the composer or draft.
- Expose `stop`, `retry`, and `undo/apply` controls for any user-visible generation.
- Distinguish loading, generating, validating, and failed states in the UI.

## Structured Output

- Prefer tool calling or schema-constrained generation over regex parsing.
- Validate before persisting or triggering side effects.
- Keep a degraded path: partial parse, human review, or explicit retry.
- Version output schemas like public API contracts.

## Persistence

- Store conversations and AI actions server-side with timestamps, model ID, prompt version, and feedback markers.
- Treat system prompts, tools, and post-processors as deployable product logic.
- Keep an audit trail when generations can affect business records, user content, or support workflows.

## Degraded Mode

- Define what the product does when the model is unavailable: fallback provider, simpler model, or non-AI path.
- Make degraded mode explicit in the UI when user expectations would otherwise be violated.
- Prefer keeping the core product usable without AI rather than blocking the entire journey.
