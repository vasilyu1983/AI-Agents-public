/**
 * minimal-command-registry.ts
 *
 * TypeScript pseudo-code showing:
 *   1. Command precedence (built-in < project < user)
 *   2. Lazy-shim pattern — commands are not parsed until first invocation
 *
 * This is illustrative, not a production dependency. Adapt to your runtime.
 */

// ── Types ─────────────────────────────────────────────────────────────────────

type CommandSource = "builtin" | "project" | "user";

interface CommandDefinition {
  /** Slash-command name, e.g. "review" → invoked as /review */
  name: string;
  /** Human-readable description shown in /help output */
  description: string;
  /** Origin layer — determines precedence when names collide */
  source: CommandSource;
  /** Path to the .md prompt file — loaded lazily on first invocation */
  promptPath: string;
  /** Allowed tool names; undefined = inherit caller permissions */
  allowedTools?: string[];
}

/** Resolved command: prompt loaded, shim evaluated */
interface ResolvedCommand extends CommandDefinition {
  promptContent: string;
}

// ── Precedence constants ──────────────────────────────────────────────────────

/**
 * Higher number wins when two commands share the same name.
 * Trap: never flip user < project — user overrides are intentional.
 * Resolution: if you see a command disappear after upgrade, check that a new
 * builtin has not shadowed a user or project command (it cannot by this ordering,
 * but a misconfigured loader that ignores precedence can).
 */
const PRECEDENCE: Record<CommandSource, number> = {
  builtin: 0,
  project: 1,
  user: 2,
};

// ── Registry ──────────────────────────────────────────────────────────────────

export class CommandRegistry {
  /**
   * Internal store. Key = command name, value = winning definition.
   * Only the highest-precedence definition for each name is kept.
   */
  private registry = new Map<string, CommandDefinition>();

  /**
   * Lazy cache: stores fully-loaded commands after first invocation.
   * Prevents re-reading the prompt file on every call.
   */
  private resolvedCache = new Map<string, ResolvedCommand>();

  // ── Registration ─────────────────────────────────────────────────────────

  /**
   * Register a command. Call for each source in ascending precedence order
   * (builtin first, then project, then user) so the final state is correct.
   *
   * Trap: registering out of order (user before builtin) will cause user
   * commands to be overwritten by builtins.
   * Resolution: always call registerAll() which sorts by precedence internally.
   */
  register(cmd: CommandDefinition): void {
    const existing = this.registry.get(cmd.name);
    if (!existing || PRECEDENCE[cmd.source] >= PRECEDENCE[existing.source]) {
      this.registry.set(cmd.name, cmd);
      // Invalidate any cached resolution when definition changes
      this.resolvedCache.delete(cmd.name);
    }
  }

  /**
   * Bulk-register from all sources. Sorts by precedence so callers do not need
   * to worry about insertion order.
   */
  registerAll(definitions: CommandDefinition[]): void {
    const sorted = [...definitions].sort(
      (a, b) => PRECEDENCE[a.source] - PRECEDENCE[b.source]
    );
    for (const def of sorted) {
      this.register(def);
    }
  }

  // ── Resolution (lazy shim) ────────────────────────────────────────────────

  /**
   * Resolve a command by name. Returns the fully-loaded command (prompt file
   * read) on first call; subsequent calls return the cached result.
   *
   * Lazy-shim pattern: the prompt file is never touched until the command is
   * actually invoked. This keeps startup time O(1) regardless of registry size.
   *
   * Trap: if the prompt file changes on disk after the first invocation the
   * cache will return stale content.
   * Resolution: call invalidate(name) when a file-watch event fires, or call
   * invalidateAll() at the start of each session.
   */
  async resolve(name: string): Promise<ResolvedCommand> {
    if (this.resolvedCache.has(name)) {
      return this.resolvedCache.get(name)!;
    }

    const def = this.registry.get(name);
    if (!def) {
      throw new Error(`Command not found: /${name}. Run /help to list available commands.`);
    }

    const promptContent = await loadPromptFile(def.promptPath);
    const resolved: ResolvedCommand = { ...def, promptContent };
    this.resolvedCache.set(name, resolved);
    return resolved;
  }

  // ── Cache invalidation ────────────────────────────────────────────────────

  /** Invalidate the resolved cache for a single command (e.g. on file change). */
  invalidate(name: string): void {
    this.resolvedCache.delete(name);
  }

  /** Invalidate all cached resolutions (e.g. at session start). */
  invalidateAll(): void {
    this.resolvedCache.clear();
  }

  // ── Introspection ─────────────────────────────────────────────────────────

  /** List all registered commands, sorted for /help output. */
  list(): CommandDefinition[] {
    return [...this.registry.values()].sort((a, b) =>
      a.name.localeCompare(b.name)
    );
  }

  /** Check if a command name is registered. */
  has(name: string): boolean {
    return this.registry.has(name);
  }
}

// ── Stub helpers (replace with real I/O in your runtime) ─────────────────────

async function loadPromptFile(path: string): Promise<string> {
  // Replace with: fs.readFile, fetch, or your VFS abstraction.
  // Returning a stub here keeps this file runtime-agnostic.
  return `[prompt loaded from ${path}]`;
}

// ── Usage example ─────────────────────────────────────────────────────────────

/*
const registry = new CommandRegistry();

registry.registerAll([
  { name: "review",  source: "builtin", description: "Code review",     promptPath: "builtin/review.md" },
  { name: "review",  source: "project", description: "Project review",  promptPath: ".claude/commands/review.md" },
  { name: "deploy",  source: "user",    description: "My deploy helper", promptPath: "~/.claude/commands/deploy.md" },
]);

// /review resolves to the project-scoped version (precedence 1 > 0)
const cmd = await registry.resolve("review");
console.log(cmd.source);        // "project"
console.log(cmd.promptContent); // contents of .claude/commands/review.md

// File-watch event fires:
registry.invalidate("review");
*/
