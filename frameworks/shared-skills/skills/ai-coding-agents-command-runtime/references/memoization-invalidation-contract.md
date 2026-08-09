# Memoization Invalidation Contract

Documents which events must invalidate the command-registry resolved cache. Apply this contract to any implementation that caches parsed prompt files, resolved tool lists, or evaluated command metadata.

---

## Why a Contract

A lazy-resolution cache improves startup time: prompt files are not parsed until first invocation. The cost is staleness. Without a clear invalidation contract, cached commands silently diverge from on-disk truth. This document lists every event that MUST trigger `invalidate(name)` or `invalidateAll()`.

---

## Event Table

| Event | Scope | Action | Notes |
|-------|-------|--------|-------|
| **Prompt file changed on disk** (`fs.watch` / `chokidar`) | Single command | `invalidate(name)` | Watch `.claude/commands/`, `~/.claude/commands/`, and any custom `commandsDir`. |
| **Session start** | All commands | `invalidateAll()` | User may have edited files between sessions. Cheap — cache is cold anyway. |
| **Plugin installed or updated** | All plugin-sourced commands | `invalidateAll()` | A plugin update may change prompt content, allowed tools, or argument schema. |
| **Plugin removed** | Removed command(s) | `deregister(name)` + `invalidate(name)` | Resolved cache entry must be deleted; registry entry removed. Trap: leaving a resolved cache hit for a deregistered command causes invocation errors. Resolution: deregister always calls invalidate internally. |
| **Settings reload** (`/settings reload`, file-watch on `settings.json`)  | Commands whose `allowedTools` derives from settings | `invalidate(name)` for each affected command | Tool lists are not re-evaluated until next `resolve()`. |
| **Project switch** (opening a different repo in the same process) | All project-scoped commands | `invalidateAll()` + re-register project commands | Built-in and user commands survive; project commands must be re-registered from the new project root. Claude Code's `/cd` (shipped v2.1.169) is the concrete instance of this event: it relocates a live session to a new working directory *without* rewriting the system prompt or breaking the prompt cache — the new directory's `CLAUDE.md` is appended as a message instead. The expert nuance: prompt-cache preservation and command-registry invalidation are separate concerns that this event forces apart. You can (and should) keep the cached system-prompt prefix warm across the directory switch while still fully invalidating and re-registering project-scoped commands, since the old project's `.claude/commands/` almost certainly do not exist, or mean something different, at the new root. Treat "preserve cache" and "invalidate registry" as independent axes, not one combined reset. |
| **User-scope commands dir changes** | User-scoped commands | `invalidate(name)` per changed file | Watch `~/.claude/commands/` and `~/.codex/commands/`. |
| **Git checkout / branch switch** (if watching `.claude/` in the worktree) | All project commands | `invalidateAll()` for project scope | The `.claude/commands/` directory may differ between branches. |
| **Process hot-reload in dev mode** | All commands | `invalidateAll()` | Dev servers that hot-patch modules must clear the registry and resolved cache; stale closures from the previous module version will otherwise persist. |
| **Manual `invalidate()` call from test harness** | Targeted | `invalidate(name)` | Test code must be able to inject fresh definitions between test cases without restarting the process. |

---

## Invariants

1. **Cache miss is always safe.** Resolving an uncached command must re-read the file from disk and re-populate the cache. No invocation should fail because the cache was empty.
2. **Cache hit must never serve a deregistered command.** Calling `registry.has(name)` before serving a cache hit is not required if `deregister` always calls `invalidate`. Enforce this in the registry implementation.
3. **Invalidation is not async.** The invalidation call itself only clears in-memory state. The next `resolve()` call performs the async file read. This separation avoids blocking file I/O on the hot path when a file-watch event fires.
4. **Bulk invalidation is O(1) (map clear).** Prefer `invalidateAll()` over iterating and calling `invalidate()` per-entry when multiple commands are affected.

---

## Common Traps

**Trap:** File-watch callback fires but invalidation is skipped because the command name does not exactly match the registry key (e.g. path-based lookup vs. name-based lookup).
**Resolution:** Build a reverse index from `promptPath → name` at registration time so file-watch callbacks can look up the exact registry key.

**Trap:** Hot-reload in development clears the resolved cache but not the registered definitions; the new module version re-registers commands, but old closed-over function references survive in the resolved cache.
**Resolution:** `invalidateAll()` must clear both the resolved cache and the registry, then reload all sources.

**Trap:** Plugin update triggers re-registration but not invalidation, leaving the old resolved entry served until process restart.
**Resolution:** The plugin loader must call `invalidateAll()` (or at minimum invalidate all plugin-sourced command names) before re-registering updated commands.

**Trap:** Session-start `invalidateAll()` is skipped for performance; user's edited prompt file is never picked up.
**Resolution:** Session-start invalidation is mandatory. The cache is cold at session start, so the cost is exactly zero resolved-cache misses — there is nothing to lose.

---

## Integration Checklist

- [ ] File-watcher registered for `.claude/commands/`, `~/.claude/commands/`, and plugin command dirs
- [ ] Session-start hook calls `invalidateAll()`
- [ ] Plugin install/update/remove lifecycle hooks call `invalidateAll()` or targeted `deregister` + `invalidate`
- [ ] Settings reload hook invalidates tool-list-dependent commands
- [ ] Project switch handler re-registers project commands and calls `invalidateAll()` first
- [ ] Reverse index (`promptPath → name`) built at registration time for file-watch callbacks
- [ ] Test harness can call `invalidate(name)` between test cases
