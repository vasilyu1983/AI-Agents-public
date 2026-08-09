# Permission Routing: Local, Remote, And Worker Flows

## Table Of Contents

- [Design Goal](#design-goal)
- [Local Interactive Flow](#local-interactive-flow)
- [Remote Session Flow](#remote-session-flow)
- [Swarm Worker Flow](#swarm-worker-flow)
- [Unknown Tool And Synthetic Request Handling](#unknown-tool-and-synthetic-request-handling)

## Design Goal

Approval semantics should stay the same across execution topologies, but transport should differ. The `claude_code` source shows three distinct routing paths:

- local REPL approval
- remote session approval
- worker-to-leader approval

## Local Interactive Flow

Local interactive approval is the simplest path:

- tool requests enter the host permission system
- automated checks can run before dialog display
- the user approves, rejects, or updates input
- the host returns a structured result to the tool executor

This is the baseline all other approval paths should emulate semantically.

## Remote Session Flow

`RemoteSessionManager.ts` handles a remote approval path:

- the remote server sends a control request for `can_use_tool`
- the local client stores the pending request by request ID
- the client surfaces the approval UI locally
- the approval result is sent back as a structured remote permission response

This means the UI and the tool execution can live on different machines while sharing one approval contract.

## Swarm Worker Flow

`useSwarmPermissionPoller.ts` shows the worker flow:

- a worker registers a pending callback keyed by request ID
- the worker polls for a leader response
- mailbox or disk-backed updates are validated before callbacks fire
- sandbox permission responses use a parallel callback registry

The architectural lesson:

- worker approvals need durable identifiers
- leader responses should survive process or render boundaries
- malformed external approval updates must be filtered before execution resumes

## Unknown Tool And Synthetic Request Handling

`remotePermissionBridge.ts` adds two useful fallback patterns:

- create a synthetic assistant message when remote tool use has no local message object
- create a stub tool object when the remote server exposes a tool the local client does not know

Copy these rules:

- remote approval should not fail just because the local client lacks the full tool implementation
- the host should be able to render and decide on a request using normalized synthetic wrappers
- provenance should remain explicit so users know the tool originated remotely
