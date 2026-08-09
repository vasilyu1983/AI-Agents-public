# Provider Abstraction And Stream Normalization

The runtime should present one internal model interface even when upstream providers differ sharply.

## Normalize at these boundaries

- request shape
- streaming event types
- tool-call emission
- structured-output parsing
- usage accounting
- error classification

## Stable internal event model

A good internal stream model usually includes:

- assistant text delta
- reasoning or analysis delta when supported
- tool-call start
- tool-call argument delta
- tool-call end
- usage update
- provider warning
- terminal completion or failure

Keep provider-specific raw payloads available for debugging, but do not let the rest of the runtime depend on them directly.

## Tool-call normalization rules

- Normalize tool names before dispatch.
- Normalize argument payloads into one parsed structure.
- Distinguish malformed tool output from model refusal or transport failure.
- Keep direct tool-call semantics separate from transparent wrapper tools or server-mediated tools.

## Edge cases

- **Partial tool arguments**: some providers stream arguments incrementally; downstream dispatch should only see a complete normalized payload.
- **Provider-specific reasoning streams**: keep them optional so unsupported providers do not break the local event contract.
- **Usage late arrival**: some providers report token or cost data after completion; the runtime should merge rather than overwrite.
- **Cache-aware behavior**: prompt-cache and ordering constraints may affect the tool list and prompt shape even before the request is sent.

## Practical tip

If your tool runtime or UI needs to branch on raw provider response shapes, the provider boundary is too leaky.
