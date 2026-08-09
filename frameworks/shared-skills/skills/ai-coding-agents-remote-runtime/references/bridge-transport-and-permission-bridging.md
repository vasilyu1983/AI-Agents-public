# Bridge Transport And Permission Bridging

## Table Of Contents

- [Design Goal](#design-goal)
- [Typed Control Messages](#typed-control-messages)
- [Permission Bridging](#permission-bridging)
- [SDK-To-REPL Message Adaptation](#sdk-to-repl-message-adaptation)
- [Reconnect Behavior](#reconnect-behavior)

## Design Goal

Remote coding-agent transport should not be “chat messages over WebSocket.” It should separate conversation messages from control-plane requests such as approvals, cancellations, reconnect notices, and plugin or server refresh.

## Typed Control Messages

`RemoteSessionManager.ts` uses separate SDK control requests and responses:

- normal SDK messages are forwarded to the UI
- control requests handle approval
- control-cancel requests clear pending approval state
- unsupported control types receive structured errors instead of hanging

That is the right baseline for a bridge protocol.

## Permission Bridging

Remote approval is bridged by:

- storing pending requests by request ID
- surfacing a local approval UI
- returning a structured allow or deny result

`remotePermissionBridge.ts` adds two practical fallbacks:

- synthetic assistant messages for remote tool use
- stub local tool objects when the remote tool does not exist locally

Those patterns let the local client render and decide on remote actions without implementing the full tool.

Concrete flow worth copying:

1. remote runtime emits a typed permission request with `request_id`
2. local bridge stores the pending request by ID
3. local UI renders an approval surface using request metadata, not backend internals
4. user allows or denies
5. bridge sends a structured success response
6. if the remote side cancels first, local state clears the pending prompt instead of leaving orphaned UI

Credential design worth copying (verified against `code.claude.com/docs/en/remote-control`, 2026-07-11): use multiple short-lived credentials, each scoped to a single purpose (e.g. one for registering the local process with the relay, a different one for each connecting viewer) and expiring independently, rather than one long-lived shared session secret. That way revoking a compromised viewer credential does not force the executing side to re-authenticate, and vice versa.

## SDK-To-REPL Message Adaptation

`sdkMessageAdapter.ts` exists because the remote backend speaks one message shape while the REPL expects another. That is a reusable lesson:

- keep the transport schema stable
- adapt it once at the client boundary
- do not make every UI component understand backend-native wire messages

## Reconnect Behavior

The remote manager also distinguishes:

- connected
- reconnecting
- disconnected
- viewer-only no-interrupt behavior

A coding-agent remote client should model these states explicitly. Reconnect is not the same as healthy; viewer-only is not the same as a full controller.

## Edge Cases And Workarounds

Important behaviors that are easy to miss in a scratch build:

- unsupported control subtype
  - respond with a structured error so the server does not hang waiting for a reply
- viewer-only client
  - do not send interrupts
  - do not behave like a full controller during reconnect or title-update flows
- missing local tool definition for a remote tool use
  - create a stub display model instead of crashing the transcript renderer
- reconnecting versus disconnected
  - these should be separate states in the local UI
  - "trying to recover" and "session is gone" are different operator experiences
- stale pending approvals on disconnect
  - clear or cancel them deterministically

Useful implementation tip:

- keep one adapter at the boundary that translates backend-native messages into the local REPL message model
- do not leak transport-native message shapes into every UI component
