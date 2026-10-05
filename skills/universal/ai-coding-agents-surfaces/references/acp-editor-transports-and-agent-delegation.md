# ACP, Editor Transports, and Agent Delegation

Moved from the former remote-runtime skill. Editor-spawned agents speak a stdio protocol and reconnect by session ID, so "remote" does not always mean "across the internet". Covers ACP as a local stdio transport, schema-driven protocol codegen, and the agent-delegating mode.

Editor-spawned agents speak a stdio protocol, and reconnecting re-attaches by session ID. This shifts the default assumption that "remote" means "across the internet."

### ACP (Agent Client Protocol) as local stdio transport

ACP is a line-delimited JSON-RPC stdio protocol for editor ↔ agent. Editors spawn the agent process and drive it. Reconnect is session-ID re-attach; whether history is replayed depends on the method used (see [`references/recipe-reconnect-with-sequence.md`](recipe-reconnect-with-sequence.md#step-6--acp-stdio-variant)).

- **Pattern:** treat ACP as a first-class remote transport class alongside WebSocket. The `local UI ↔ remote agent` split still holds — the editor is the UI, the agent process is the executor — but the wire is a spawned subprocess, not a socket.
- **Anti-pattern:** building "IDE integration" as an in-process SDK embed. That couples editor lifecycle to agent lifecycle and makes crashes, upgrades, and custom distros impossible to isolate.
- **Recipe:** separate ACP server plumbing from the agent core. Generating method-routing code from the ACP schema (Goose's `goose-acp-macros` is one example) is the right level of indirection — your protocol-method set should be code-generated from the schema, not hand-written and drifting.

### Codegen for protocol methods

When the wire is typed (ACP, MCP, your own bridge protocol), hand-written method dispatch drifts from the schema as protocols evolve.

- **Pattern:** treat the protocol schema as source-of-truth; generate server method dispatch, client stubs, and message validators from it.
- **Anti-pattern:** copy-pasting message type definitions into handwritten `match` arms. Every protocol bump becomes a multi-file change with nothing to verify against.
- **Recipe:** commit `acp-schema.json` (or equivalent) to the repo. CI regenerates dispatch code and fails the build if handwritten code diverges.

### Agent-as-ACP-client delegation

ACP is bidirectional in practice: an agent can *also* act as an ACP client and delegate work to other coding agents running as ACP servers. This is the mirror image of the transport discussed above, and the skill's existing Viewer-only / SSH-proxy / Full-control mode taxonomy needs a fourth mode: **agent-delegating**, where the local runtime is neither UI nor executor — it is orchestrator.

- **Pattern:** add `agent-delegating` as a named mode; its control messages and approval routing follow the same typed-message discipline as the others.
- **Anti-pattern:** implementing delegation inside the provider layer (see `ai-coding-agents-provider-runtime` — agent-as-provider belongs there) *and* as a surfaces (remote-runtime) mode. Pick one; they interact but are not duplicates. Provider-level delegation is turn-scoped; remote-runtime delegation is session-scoped.
