# Production Readiness Checklist

Deployment gate for coding agents and coding agent teams. Complete before sharing with team or deploying in CI.

## Functional Validation

- [ ] Runs successfully on 3+ representative tasks
- [ ] Handles edge cases: empty files, missing files, large files (1000+ lines)
- [ ] Produces correct output format matching the output contract
- [ ] Self-verification step validates output correctly
- [ ] No scope creep observed (agent stays within assigned files/directories)

## Token Budget

- [ ] Token usage within acceptable limits across test runs
- [ ] No context exhaustion (agent doesn't lose track in large codebases)
- [ ] Progressive disclosure working (agent doesn't read unnecessary files)
- [ ] Cost per invocation acceptable for intended usage frequency

## Safety

- [ ] Permission mode appropriate for the operations performed
- [ ] Read-only agents cannot write (disallowedTools enforced)
- [ ] Protected paths excluded (.env, credentials, secrets, node_modules)
- [ ] Destructive git operations blocked (push, force, reset --hard)
- [ ] No prompt injection vulnerability via code content

## Reliability

- [ ] maxTurns set to prevent infinite loops
- [ ] Failure behavior defined and tested ("if stuck, report and stop")
- [ ] Error handling: agent reports errors clearly, doesn't silently fail
- [ ] Idempotent: running twice on same input produces consistent results

## Runtime Substrate

- [ ] Command registry load order documented and deterministic
- [ ] Dynamic commands or skills have explicit cache invalidation rules
- [ ] Tool pool ordering stable enough for prompt-cache-sensitive providers
- [ ] Permission context has one canonical owner in the runtime
- [ ] Background or headless workers never block forever on approval UI
- [ ] Settings reload path is centralized and re-applies derived state cleanly
- [ ] Remote bridge distinguishes normal messages from control-plane requests
- [ ] Resume flow restores trusted state and recomputes environment-dependent state
- [ ] Long-session TUI tested for virtualization, resize, and scroll stability
- [ ] Background task claiming, release, and cancellation semantics tested under contention

## Multi-Agent (if applicable)

- [ ] All workers complete within expected time
- [ ] No merge conflicts between workers (owned_files exclusive)
- [ ] Coordinator synthesis produces coherent implementation specs
- [ ] Verification worker independently validates implementation
- [ ] Escalation path tested (what happens when a worker fails)
- [ ] Task graph persisted and recoverable

## Integration

- [ ] Agent definition committed to repo (.claude/agents/ or .codex/agents/)
- [ ] Description triggers correctly for intended use cases
- [ ] Description does NOT trigger for unrelated tasks
- [ ] Documentation updated (README, AGENTS.md if applicable)
- [ ] Team members briefed on how to use and when to invoke

## Monitoring

- [ ] Know how to check agent token usage after invocation
- [ ] Know how to read agent transcripts for debugging
- [ ] Feedback loop: how will you learn about agent failures in real use?
- [ ] Plan for iterating: when and how to update the agent based on usage
