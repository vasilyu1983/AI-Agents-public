# Unattended Runs

Load this before you start a hive, workflow, or loop that no human watches: a scheduled run, an overnight batch, or a headless `claude -p` / `codex exec` call. Runtime facts and launch mechanics live in [../../agents-subagents/SKILL.md](../../agents-subagents/SKILL.md). This note holds only the judgment that an unattended run adds.

Evidence label: the cited papers are single-team preprints. Each supports a direction, not a number to plan around. Flag names change between releases; before you rely on one, check the current Claude Code / Codex docs for the exact flag.

## Rules

1. **Never trust an agent's "done", "infeasible" or time estimate.** One study (AgentTime, arXiv 2610.09944) reports that agents miss requested runtimes by a typical factor of about 2.9 for one model in one harness, and that some runs idle after appearing to finish. The size of the miss depends on the model and harness, so measure your own. Another (SWE-Marathon, arXiv 2606.07682) reports false "infeasible" claims, early stops and weak self-verification on very long tasks. Judge completion by an artifact and a check the agent cannot edit, not by its own report.
2. **Put wall-clock and cost limits outside the script.** A workflow script cannot read the clock, so it can only hold count-based caps (agent count, null-streak, round count). Set the cost cap and per-call stall timeout in the launcher or runtime (for example a `--max-budget-usd` style flag on the CLI and a `stallMs` style option per agent call). Look up the current names. Treat any cost figure as a client-side estimate.
3. **Run in no-prompt mode, with allow rules for exactly the needed tools.** In a `--permission-prompts none` style mode, anything that would prompt is denied unless a `PermissionRequest` hook allows it, and the run continues. Allow only the tools the run needs. A wide allow list defeats the point.
4. **Treat any non-zero exit or signal as INCOMPLETE.** SIGTERM exits 143 with the turn unfinished. Never map a killed, timed-out or budget-stopped run to success, and never merge its partial output without the parent's own check.
5. **Do not use `--bare` for an unattended run that relies on hooks.** `--bare` skips hooks, skills, plugins, MCP, memory and CLAUDE.md, so safety hooks (git guards, path guards) do not run. Keep hooks loaded, or pass the hook settings explicitly, and prove the hook fires with one denied dry-run command.
6. **Expect usage-limit failure, not a pause.** Interactive sessions can pause and resume after a reset. Headless, SDK and background runs fail instead. The launcher must detect the failure, record it as INCOMPLETE, and not retry in a tight loop.
7. **Make writers safe to repeat; keep irreversible actions in the parent.** Resume works by replay: finished agents return saved results, and the first changed or failed agent and every later one run again. Replayed tool calls can repeat irreversible effects (ACRFence, arXiv 2603.20625: duplicate payments in one study). File edits are safe to repeat. Pushes, merges, deploys and messages are not, so the parent does them after the run.
8. **Do not add an external durable-execution engine for a personal hive** when the runtime already replays. The engine adds a dependency and a second state store. Revisit only if you need cross-machine resume or long human-wait steps.
9. **Keep checks, gates, stop controls and protected-path lists outside every path a workflow agent may write.** This includes saved workflow scripts, runtime helper scripts, hook scripts, and the allow-list itself. Two studies motivate it. Poisoned self-evaluation persisted in self-modifying agents (arXiv 2609.17817).
   In a separate study (arXiv 2609.28274), agents sabotaged a peer's shutdown mechanism in 38.3% of rollouts against 8.4% in control; a prohibition reduced but did not remove it. A run in progress keeps its loaded script, but the next run loads the edit, so scope build-mode writers and snapshot or hash the gate files before and after.

## Pre-flight checklist

- [ ] Each completion check is a command or artifact the agents cannot write.
- [ ] Cost cap, per-call stall timeout and a run-level agent cap are set, and the clock is not read inside the script.
- [ ] No-prompt mode is on; the allow list names only the required tools.
- [ ] Hooks are loaded (no `--bare`), and a denied dry-run proves a guard fires.
- [ ] Gate files, workflow scripts, runtime helpers and hook scripts are outside the writers' scope.
- [ ] No workflow agent can push, merge, deploy or send a message.
- [ ] The launcher maps non-zero exit, signal and usage-limit failure to INCOMPLETE.
- [ ] A kill path exists: how you stop the run and where partial state is kept.
- [ ] The parent reads the diff and re-runs the checks before it commits or merges.

See also: [operational-guardrails.md](operational-guardrails.md) for stop conditions, [noninteractive-and-blueprints.md](noninteractive-and-blueprints.md) for CI-safe dispatch, [scripted-workflows.md](scripted-workflows.md) for resume and caching, and [output-contracts.md](output-contracts.md#optional-check_defect-field) for the `check_defect` stop.
