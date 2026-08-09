# Trace And Telemetry Model

Use a layered telemetry model for coding agents:

1. **Session layer**
   Session id, repo or workspace, runtime mode, provider config, settings snapshot, and user-visible start or stop metadata.
2. **Turn layer**
   Prompt input, selected context, command mode, agent identity, and final answer summary.
3. **Execution layer**
   Tool calls, approvals, subprocess boundaries, file edits, retries, worker spawning, and verification passes.
4. **Outcome layer**
   Success or failure category, latency, token usage, cost, and any regression score outputs.

## Minimum replay-safe payload

Persist enough state to explain a bad run without depending on transient UI events:

- user input
- resolved context or file list
- tool-call sequence
- tool inputs and outputs after redaction
- diffs or write summaries
- approval requests and decisions
- worker or teammate handoffs
- verifier findings
- final answer

## Good design rules

- Use one canonical trace or session id across local UI, remote bridge, and worker tasks.
- Give every tool call a stable id and parent turn id.
- Keep UI rendering metadata separate from semantic execution metadata.
- Store redacted but structured payloads so search and replay remain useful.
- Emit event timestamps in causal order and preserve monotonic ordering when clocks differ.

## Edge cases

- **Background tasks**: They should emit progress events against the same session while preserving their own task ids.
- **Remote sessions**: Bridge control messages belong in the trace even when the local UI never re-renders them directly.
- **Resume flows**: A resumed session should continue the same semantic session lineage while marking the restore boundary explicitly.
- **Verifier passes**: Record them separately from implementation attempts so regressions can distinguish “wrong fix” from “missing verification.”

## Practical tip

If a user reports “the agent made the wrong change,” the trace should answer four questions quickly:

1. what context it loaded
2. which tool sequence it chose
3. whether any approval or policy boundary changed the plan
4. whether a verifier saw the defect and failed to block it
