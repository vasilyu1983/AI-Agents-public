# Goose Session and Task Patterns

Moved from the former sessions and tasks skills: cross-process session re-attach over ACP, recipe-as-session-seed, typed recipe blueprints, capability-narrowed subagents, and sub-recipes.

## Goose Session Patterns

Goose adds two session patterns not covered by the Claude Code-derived core: **cross-process session re-attach over ACP**, and **recipe-as-session-seed** for deterministic resume.

### Cross-process session re-attach (ACP)

Goose runs as an ACP stdio server. When an editor (Zed, JetBrains, etc.) disconnects and reconnects, the session ID is passed back on the new stdin pipe and the agent re-attaches in-place. This is different from in-process resume (already covered by rewind/checkpoint) and different from same-machine file-watch continuation — the process may have restarted, but the session object persists.

- **Pattern:** session identity must survive the parent process it was spawned by. Persist session state server-side; require the re-attaching client to prove it holds the session ID.
- **Anti-pattern:** binding session lifetime to the stdin FD or parent PID. That collapses editor restarts, agent upgrades, and sleep/resume into session loss.
- **Recipe:** on ACP connect, the agent looks up the session ID in its session store; if found and auth proof matches, resume from persisted transcript + checkpoint. If not, create new. Log whether a resume hit or missed so operators can distinguish session loss from client-side amnesia.

### Recipe-as-session-seed

A resumed session is usually rehydrated from the transcript. Goose's recipe model offers an alternative: a session can be re-seeded from the *recipe* that spawned it plus its parameters — a typed, versioned, much smaller artifact than a raw transcript. This is stronger than transcript replay because inputs are structured and the recipe version pins extension set and instructions.

- **Pattern:** for recipe-spawned sessions, persist `(recipe ref, recipe version, parameter values, output checkpoints)` alongside the transcript. Resume can choose: replay transcript (high fidelity, large) or re-spawn from recipe + parameters + last checkpoint (deterministic, small).
- **Anti-pattern:** storing only the transcript for recipe-spawned sessions. On cross-version resume, the transcript may reference tools or extensions no longer in the envelope.
- **Recipe:** add a `seed_ref: Option<RecipeSeed>` field to session metadata. When present, resume UI should offer "replay transcript" and "re-run recipe from last checkpoint" as named modes.


## Goose Task Patterns

Goose models task creation around **recipes**: declarative YAML units that replace ad-hoc free-text task spawning. Three patterns worth importing into the task runtime model.

### Recipes as typed task blueprints

A Goose recipe is a validated YAML file with `version / title / description / instructions / author / extensions / activities / prompt / parameters` (typed: `{key, input_type, requirement, description, default}`). Tasks spawn *from* a recipe, not from a free-form user string. Parameters are declared, activities are listed, required extensions are pinned.

- **Pattern:** when a task type is well-defined and reusable, promote it to a typed blueprint. Runtime validates the blueprint at load time (see `recipe-scanner`-style static checks), binds typed parameters, and spawns the task with a pinned extension manifest.
- **Anti-pattern:** treating every task as a free-text prompt and relying on prompt craft to make them repeatable. That collapses reuse, versioning, and validation into transcript memory.
- **Recipe:** ship a validator that checks YAML syntax, required fields, extension references (do the declared extensions actually exist?), and security gates (is this recipe allowed to spawn network-touching tools?). Goose's `recipe-scanner/` crate is a working reference.

### Capability-narrowed subagents

When a lead session spawns parallel subagents (code review lane, docs lane, file-processing lane), each subagent should carry its *own* extension manifest — typically a subset of the lead's. Goose models this explicitly; the subagent inherits no more capability than its recipe declares.

- **Pattern:** subagent spawn = recipe + parameters + capability-narrowed extension list. The narrower capability envelope is enforced at task-creation time, not at tool-call time.
- **Anti-pattern:** subagents inheriting the lead's full tool belt by default. That turns "delegate code review" into "let a sub-process touch anything the lead could touch" and defeats parallel-lane isolation.
- **Recipe:** in your task typing, add an `extensions: Vec<ExtensionRef>` field to the subagent-task family. Refuse to spawn if the subagent's declared extensions are not a subset of the lead's envelope.

### Sub-recipes — composable task blueprints

A Goose recipe can invoke another recipe as a step, not just call a tool. Sub-recipes let complex workflows compose from validated pieces instead of giant monolithic prompts.

- **Pattern:** model sub-recipe calls as a distinct task relationship ("spawned-by-recipe-step"), separate from lead→worker (delegation) and from tool calls (invocation). Ownership, cancellation, and blocker semantics follow the recipe tree.
- **Anti-pattern:** inlining sub-recipes into the parent's prompt text. That loses the validation, capability-narrowing, and telemetry attribution benefits of the recipe boundary.
- **Recipe:** give sub-recipe tasks a distinct lifecycle state (`pending-subrecipe`, `running-subrecipe`, `completed-subrecipe`) and a parent-recipe pointer. Cancellation of the parent should cascade; a failed sub-recipe should be a first-class blocker on the parent.

