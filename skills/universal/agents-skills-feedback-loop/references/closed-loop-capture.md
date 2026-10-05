# Closed-Loop Capture (Layer 1)

How to make the learnings loop *close itself* — automatic capture after every
session, on **any laptop**. Claude Code is supported; Codex registration is
opt-in and captures nothing until the parser reads Codex transcripts. This is the
runtime-hook upgrade the main SKILL.md gestures at under "Related Skills →
agents-hooks".

## Table of Contents

- [Why this exists](#why-this-exists)
- [The three-part model](#the-three-part-model)
- [One script, two registrations](#one-script-two-registrations)
- [Install on any laptop](#install-on-any-laptop)
- [Skills-root discovery (portability)](#skills-root-discovery-portability)
- [Guardrails (why this is safe machine-global)](#guardrails-why-this-is-safe-machine-global)
- [Verifying it works](#verifying-it-works)
- [Testing without burning model calls](#testing-without-burning-model-calls)
- [Anti-patterns](#anti-patterns)

## Why this exists

The base loop (the `## Learnings Loop` addendum + `append_learning.py`) is
**open**: it depends on an agent or human remembering to append, so capture is
uneven across skills. Layer 1 closes the
*capture* half: a session-end hook detects which wired skills were used, asks
one cheap model pass whether there was a durable learning, and appends it via
the existing `append_learning.py`. No new memory format; no `SKILL.md`
rewrite. Consolidation stays manual and is out of scope here. Moving a
consolidated rule into skill logic is a reviewed skill edit (SKILL.md →
Promotion Out), never part of this hook.

## The three-part model

| Closure | Mechanism | Status |
|---|---|---|
| **Capture** | session-end hook → reflect → `append_learning.py` | **this doc** |
| Consolidate | scheduled `consolidate.py` (dreaming-style) | manual |
| Promote out | reviewed skill edit (SKILL.md → Promotion Out) | manual |

Build capture first: without traces there is nothing to consolidate.

## One script, two registrations

The script reads `{session_id, transcript_path, cwd, …}` from stdin, which is
the shape both runtimes' hook docs describe. Only the registration differs:

| Runtime | Config file | Event | Notes |
|---|---|---|---|
| Claude Code | `$HOME/.claude/settings.json` | `SessionEnd` | fires once per session |
| Codex CLI (`--codex` only) | `$HOME/.codex/hooks.json` | `Stop` | may fire per turn; transcript not yet parsed (logs `wired_skills=0`) |

Before relying on either row, look up the runtime's hooks reference for: the
session-end event name, how often it fires, its time budget and per-hook
timeout cap, and whether the transcript format is documented. The script is
built so that none of these numbers matter: it detaches and exits at once.

Because a `Stop`-style event can fire per turn, the script keeps a per-`(session_id,
skill)` marker (`$HOME/.agents/hooks/.seen/`) with a bounded retry count
(`MAX_ATTEMPTS=3`): at most one reflection per skill per session, whether the
host fires once (Claude) or many times (Codex). Markers older than 7 days are
pruned automatically.

The script lives at `$HOME/.agents/hooks/learnings_capture.py` — a
runtime-neutral location both agents can share (the OpenClaw `~/.agents`
convention). Source of truth is `assets/learnings_capture.py` in this skill.

## Install on any laptop

```bash
# From this skill directory:
python3 scripts/install_capture_hook.py --dry-run   # preview
python3 scripts/install_capture_hook.py             # apply
```

The installer resolves every path from `Path.home()` at run time — **no
username is ever hardcoded**. It is idempotent and re-runnable: it copies the
script to `$HOME/.agents/hooks/`, registers Claude Code (`settings.json` is
created if absent), and registers Codex only when you pass `--codex` (it prints
a warning, because the parser does not read Codex transcripts yet).
`--uninstall` removes both registrations.
Unrelated keys and other hooks are preserved; a prior registration of this
script is replaced, not duplicated.

Uninstall: `python3 scripts/install_capture_hook.py --uninstall`.

## Skills-root discovery (portability)

The script must find the repo to know which skills are wired and where
`append_learning.py` is. Resolution order:

1. `LEARNINGS_SKILLS_ROOT` env var (explicit override — set this in CI or
   non-standard layouts).
2. Common `$HOME`-relative layouts (`Documents/Code/AI-Agents/…`,
   `Documents/AI-Agents/…`, `AI-Agents/…`, `projects/…`, `code/…`,
   `.agents/skills`).

A candidate counts only if it actually contains
`agents-skills-feedback-loop/scripts/append_learning.py`. If none match →
silent no-op + a log line telling you to set `LEARNINGS_SKILLS_ROOT`. On a
laptop with a non-standard checkout path, set that env var in your shell
profile.

## Guardrails (why this is safe machine-global)

- **Detached worker.** The hook process reads the payload, hands it to a
  background worker (`start_new_session=True`), and exits 0. Session-end hooks
  run under a short, runtime-capped budget; serial model calls inside that
  budget get cancelled. So the installer sets no per-hook `timeout`.
- **Untrusted transcript.** The reflection call reads session text, which may
  contain injected instructions. It runs `claude -p --tools ""
  --no-session-persistence`: no tools, and no new transcript for the hook to
  capture again.
- **Redaction.** Every entry goes through `append_learning.py`, which replaces
  API keys, bearer tokens, emails, and home-directory usernames before writing.
  Learnings files are committed and some are published.
- **Recursion guard.** The reflection call (`claude -p`) is itself an agent
  session whose end re-enters the hook. The script exits at line 1 if
  `CLOSED_LOOP_HOOK_ACTIVE=1`, which it sets before spawning the model. Without
  this, a machine-global hook is a fork bomb. Verify this first on any change.
- **Blast-radius limit.** These hooks run in *every* repo on the machine. The
  transcript parse is the gate: no wired skill used → silent `exit 0`, no
  model call, no cost. Most sessions hit this.
- **Fail-silent, fail-logged.** Always `exit 0` (session-end hooks must not
  block). Every decision is written to
  `$HOME/.agents/hooks/learnings_capture.log`. **That log is the
  capture-rate gauge** — `session=… wired=N appended=M` is the loop's only
  measurement. Read it to know the loop is alive.
- **Capability-agnostic.** No `claude` CLI / no hook runtime → no-op, never an
  error. The manual `append_learning.py` path always still works.

## Verifying it works

It is self-instrumenting by design because three things are **not** verifiable
without a real session: (1) live `claude -p` reflection quality, (2) that the
host actually fires the hook with `matcher:"*"`, (3) the real transcript JSONL
schema (both runtimes warn the format is *not* a stable interface). One log
line triages all three:

```bash
cat ~/.agents/hooks/learnings_capture.log
```

- no new line after a session that used a wired skill → hook/matcher didn't
  fire (#2), or the detached worker failed to start (look for `detach failed`)
- `wired=0` after such a session → transcript schema differs here (#3); the
  parser fails silent, so fix `skills_used()` against a real transcript sample
- `wired≥1 appended=0` repeatedly → live model step misbehaving (#1)

## Testing without burning model calls

Set `LEARNINGS_REFLECT_CMD` to a stub that reads the prompt on stdin and
prints `SECTION|||text` (or `SKIP`). Point `LEARNINGS_SKILLS_ROOT` at a temp
fixture. This exercises detection → dedupe → append deterministically with no
`claude` call — the recommended pre-deploy check on any new machine.
`scripts/test_capture_hook.py` does exactly this and also asserts the hook
returns before a slow reflection finishes and that the reflection call has no
tools.

## Anti-patterns

- Hardcoding an absolute home path in the repo (breaks on the next laptop) —
  always reinstall via the installer instead.
- Using Claude Code's `Stop` event for capture — it fires after *every*
  response, not at session end. Claude Code uses `SessionEnd`.
- Running model calls inside the hook process, or raising the per-hook
  `timeout` to fit them. The runtime clamps the timeout to its cap; detach
  instead.
- Auto-rewriting `SKILL.md` from captured learnings. Capture only appends raw
  bullets; promotion stays human-reviewed (see main SKILL.md Anti-Patterns).
