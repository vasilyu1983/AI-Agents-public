# Hostile-Path Test Checklist

Scenarios to exercise before shipping any permission subsystem. Cover denied paths, user cancellations, remote-unknown-tool calls, and bypass-mode invariants. Each row includes a Resolution to make this a generative toolkit, not just a list.

---

## How to Use

Mark each row `pass`, `fail`, or `skip+reason` before release. A permission subsystem is not shippable until all non-skipped rows are `pass`. Re-run after changes to policy rules, approval UI, or tool-registration logic.

---

## Section 1 — Denied Requests

| ID | Scenario | Setup | Expected Behavior | Resolution if Failing |
|----|----------|-------|-------------------|-----------------------|
| DENY-01 | Tool in explicit deny list | Policy has `Bash` → `deny` | Tool call returns `PermissionDenied` immediately; no approval prompt shown | Check that `deny` rules are evaluated before `ask` rules in the policy evaluation order |
| DENY-02 | Subagent requests tool denied by managed policy | Managed policy denies `file_delete` for all subagents | `PermissionDenied` returned; parent agent is notified via `permission.denied` event | Managed policy must be applied at the outermost decision point, not just the agent-level check |
| DENY-03 | Destructive Bash command without explicit allow | `rm -rf` issued without a prior `allow` rule | Tool call blocked; approval prompt shown (or denied if `ask` not in policy) | Classify destructive patterns at argument-parse time; do not rely on model self-assessment |
| DENY-04 | Network tool call when network is disabled | Agent calls an MCP network tool with `allow_network = false` | Denied before the tool handler fires | Network-disabled flag must be checked in the permission layer, not in the tool handler |
| DENY-05 | Deny rule overrides a broader allow rule | `allow: Bash(*)` + `deny: Bash(rm *)` | `rm` variant denied; all other Bash calls allowed | Rule evaluation must be: specific deny > specific allow > broad allow > default |

---

## Section 2 — User Cancellation

| ID | Scenario | Setup | Expected Behavior | Resolution if Failing |
|----|----------|-------|-------------------|-----------------------|
| CANCEL-01 | User dismisses approval prompt without choosing | Approval prompt appears; user closes it | Tool call treated as `deny`; no side effects; agent notified of cancellation | Timeout or close event on the approval UI must resolve the pending promise as `deny`, never as `allow` |
| CANCEL-02 | User cancels mid-session while approval prompt is open | User presses Ctrl+C while an `ask` prompt is pending | Session cancelled; pending approval resolved as `deny`; `task.cancelled` event emitted | Cancellation signal must drain the approval queue with `deny` before shutting down |
| CANCEL-03 | User cancels a previously-allowed tool before execution | User allowed a Bash command; then cancels before the process forks | Process never started; `task.cancelled` event emitted | Allow decisions must not be considered irrevocable until the tool handler receives control; insert a cancellation checkpoint between allow and exec |
| CANCEL-04 | Repeated cancellations do not leave zombie approvals | User cancels 5 times in a row | Each cancellation results in a clean `deny`; no leaked approval state | Approval queue must be fully drained and reset on each cancellation |

---

## Section 3 — Remote / Unknown Tool

| ID | Scenario | Setup | Expected Behavior | Resolution if Failing |
|----|----------|-------|-------------------|-----------------------|
| REM-01 | Agent requests a tool not in the local registry | Remote agent calls `mcp__unknown_server__do_thing` | Permission layer returns `ToolNotRegistered`; agent shown an informative error | Unknown-tool check must fire before policy evaluation; do not evaluate policy for unregistered tools |
| REM-02 | MCP server registers a tool whose name collides with a builtin | Plugin registers a tool named `Bash` | Rejected at registration time; existing `Bash` binding preserved | Tool registration must check for name collisions and reject or namespace the new entry |
| REM-03 | Remote-runtime tool call arrives with no session context | Tool call received over WebSocket with no `session_id` | Rejected with `AuthRequired`; not evaluated against policy | Session context must be validated before policy evaluation; unauthenticated requests never reach the policy layer |
| REM-04 | ACP-delegated subagent requests a tool outside its declared scope | Subagent's manifest lists `allowed_tools: [Read, Grep]`; it calls `Bash` | Denied at the orchestrator's permission layer; `permission.denied` event forwarded over ACP | Orchestrator must re-apply its own policy to all ACP-delegated tool calls; the delegated agent's allow-list is an upper bound, not a bypass |
| REM-05 | Tool response arrives after session expires | Tool was dispatched, session expired before response | Response discarded; `session.expired` event emitted; no state mutation applied | Implement a session-validity check on tool-response ingestion, not only on tool dispatch |

---

## Section 4 — Bypass Mode

| ID | Scenario | Setup | Expected Behavior | Resolution if Failing |
|----|----------|-------|-------------------|-----------------------|
| BYP-01 | Bypass mode enabled allows all non-destructive calls | `bypassPermissions: true` in dev config | Non-destructive tool calls proceed without approval prompt | Bypass mode must only suppress the prompt, never mutate policy state; destructive-class tools must still be blocked unless explicitly added to the allow list |
| BYP-02 | Bypass mode does NOT bypass deny rules | `bypassPermissions: true` + `deny: file_delete` | `file_delete` still denied despite bypass mode | `deny` rules are unconditional; bypass mode only affects `ask` behavior, not `deny` behavior |
| BYP-03 | Bypass mode is never active in production config | Managed policy sets `bypass_mode: prohibited` | Dev flag ignored when managed policy is present | Managed policy enforcement must gate on the full policy chain, including a `bypass_mode: prohibited` check |
| BYP-04 | Audit log entries are not suppressed in bypass mode | Bypass mode active; agent makes 10 tool calls | All 10 calls appear in the audit log with `bypass_mode: true` annotation | Bypass mode suppresses approval prompts, never audit events; verify the audit pipeline is independent of the approval path |
| BYP-05 | Subagents do not inherit parent bypass mode | Parent session has bypass mode; spawns a subagent | Subagent evaluates its own policy; bypass mode does not propagate | Session-scope flags must not be inherited by child sessions unless the child's own config explicitly sets them |

---

## Pass Criteria

A permission subsystem passes this checklist when:
- All `DENY-*` rows produce the documented `PermissionDenied` result with no side effects.
- All `CANCEL-*` rows produce clean `deny` outcomes with no leaked state.
- All `REM-*` rows reject or error before any side-effecting code runs.
- All `BYP-*` rows confirm that bypass mode is scoped, audited, and cannot override `deny` rules.
