// Tree snapshots: the enforcement behind the read-only and file-scope rules; the prompt rules are guidance only.
// A saved workflow has no host shell, so a separate snapshot agent with only Bash, never a writer, runs
// SNAPSHOT_COMMAND and returns its raw stdout. This code parses that text itself and trusts no summary.
// The output is plain ASCII; every path is hex-encoded, so no file name reaches the relay agent as readable text:
//   TOKEN\t<token>                                    this step's token (shell variable t), against replay
//   HEAD
//   INDEX\t<hash of git ls-files -s -z>                every index entry's mode, blob and path
//   CONFIG\t<hash of git config --list --show-origin>  with include.path and includeIf files
//   PROTECTED\t<hash>                                 one hash over the content hash and path of .git/config, every
//                                                     file under .git/hooks and .git/info, every file under the
//                                                     PROTECTED_DIRS and PROTECTED_ROOTS at the repo root, and the
//                                                     PROTECTED_FILES at the repo root, ignored or not; a symlink is
//                                                     hashed as its link text,
//                                                     never followed. One line keeps the relayed text short.
//   <content blob|deleted>\t<hex path>                every path that differs from HEAD in the worktree or the index,
//                                                     plus every untracked file that is not ignored
//   CKSUM\t<crc>\t<bytes>                             POSIX cksum of every line above
//   SNAPSHOT-END
// Listing against HEAD, not the index, means an edit followed by `git add` still shows; the index hash shows staging.
// Every git call is written out with a literal subcommand, so the user's git-safety hook can check it, and runs
// with core.fsmonitor=false, so a planted config cannot run code through the snapshot. None of
// these read-only commands runs a hook, so hooksPath needs no override (the user's git-safety hook blocks one). Every command only reads: `hash-object` without -w and GIT_OPTIONAL_LOCKS=0 write nothing to
// .git. `--no-filters` hashes the exact bytes on disk; pipefail means a failed listing never prints SNAPSHOT-END;
// stderr is dropped, so no error text names a file. Snapshots are compared with each other, never with a clean tree,
// so the user's own uncommitted or staged edits trip nothing. Ignored files outside the protected root folders and
// files are not watched, so test caches never trip a read-only step; a protected path deeper in the tree, tracked or
// untracked-not-ignored, shows in the content delta. The checksum and token catch a relay that edits, mangles or
// replays the output; a relay that runs the command on a forged tree or computes its own checksum is not caught.
// A missing, unparseable, edited or replayed snapshot is never a pass.
// The command is one JSON string literal so the generator can copy the same text into the Codex plans.
const SNAPSHOT_COMMAND = "( set -o pipefail; export GIT_OPTIONAL_LOCKS=0; snaphash() { if [ -L \"$1\" ]; then readlink \"$1\" | git -c core.fsmonitor=false -c core.quotePath=false hash-object --stdin; else git -c core.fsmonitor=false -c core.quotePath=false hash-object --no-filters -- \"$1\"; fi; }; snaphex() { printf '%s' \"$1\" | od -An -tx1 | tr -d ' \\n'; }; cd \"$(git -c core.fsmonitor=false -c core.quotePath=false rev-parse --show-toplevel)\" && b=$(printf 'TOKEN\\t%s\\n' \"$t\" && c=$(git -c core.fsmonitor=false -c core.quotePath=false rev-parse --path-format=absolute --git-common-dir) && w=$(git -c core.fsmonitor=false -c core.quotePath=false rev-parse --absolute-git-dir) && git -c core.fsmonitor=false -c core.quotePath=false rev-parse --verify HEAD && printf 'INDEX\\t%s\\n' \"$(git -c core.fsmonitor=false -c core.quotePath=false ls-files -s -z | git -c core.fsmonitor=false -c core.quotePath=false hash-object --stdin)\" && printf 'CONFIG\\t%s\\n' \"$(git -c core.fsmonitor=false -c core.quotePath=false config --list --show-origin | git -c core.fsmonitor=false -c core.quotePath=false hash-object --stdin)\" && pr=$(for p in \"$c/config\" \"$w/config.worktree\" \"$c/hooks\" \"$c/info\" .claude .codex .agents .github .husky .vscode .idea .devcontainer CLAUDE.md AGENTS.md .mcp.json .claude.json .envrc .gitattributes .gitmodules .pre-commit-config.yaml hooks scripts/git-hooks agents/workflows skills/universal/agents-subagents/scripts agents/claude agents/codex; do [ -e \"$p\" ] || [ -L \"$p\" ] || continue; find \"$p\" \\( -type f -o -type l \\) -print; done | LC_ALL=C sort -u | while IFS= read -r f; do h=$(snaphash \"$f\") || exit 1; printf '%s\\t%s\\n' \"$h\" \"$f\"; done | git -c core.fsmonitor=false -c core.quotePath=false hash-object --stdin) && printf 'PROTECTED\\t%s\\n' \"$pr\" && { git -c core.fsmonitor=false -c core.quotePath=false diff HEAD --no-renames --no-ext-diff --no-textconv --name-only -z && git -c core.fsmonitor=false -c core.quotePath=false ls-files -o --exclude-standard -z; } | tr '\\n\\0' '\\001\\n' | LC_ALL=C sort -u | while IFS= read -r f; do if [ -f \"$f\" ]; then h=$(git -c core.fsmonitor=false -c core.quotePath=false hash-object --no-filters -- \"$f\"); elif [ -e \"$f\" ]; then h=; else h=deleted; fi; printf '%s\\t%s\\n' \"$h\" \"$(snaphex \"$f\")\"; done) && printf '%s\\n' \"$b\" && printf 'CKSUM\\t%s\\t%s\\n' $(printf '%s\\n' \"$b\" | cksum) && echo SNAPSHOT-END ) 2>/dev/null";
const SNAPSHOT_SCHEMA = {
  type: 'object',
  required: ['stdout'],
  properties: { stdout: { type: 'string', description: 'The complete stdout of the command, verbatim' } },
};
const SNAPSHOT_HASH = /^[0-9a-f]{40}(?:[0-9a-f]{24})?$/;
const SNAPSHOT_LINE = /^([0-9a-f]{40}(?:[0-9a-f]{24})?|deleted)\t((?:[0-9a-f]{2})+)$/;

// POSIX cksum: CRC-32, polynomial 0x04C11DB7, MSB first, then the length in bytes, then the complement.
// `text` must be ASCII, so each character is one byte.
const CKSUM_TABLE = [];
for (let i = 0; i < 256; i++) {
  let c = i << 24;
  for (let k = 0; k < 8; k++) c = c & 0x80000000 ? (c << 1) ^ 0x04c11db7 : c << 1;
  CKSUM_TABLE.push(c >>> 0);
}
function cksum(text) {
  let crc = 0;
  const add = (byte) => { crc = ((crc << 8) ^ CKSUM_TABLE[((crc >>> 24) ^ byte) & 0xff]) >>> 0; };
  for (let i = 0; i < text.length; i++) add(text.charCodeAt(i));
  for (let n = text.length; n > 0; n = Math.floor(n / 256)) add(n % 256);
  return ~crc >>> 0;
}

// A hex-encoded UTF-8 path, or null. A control character (a newline arrives as \u0001) fails.
function unhex(hex) {
  let path;
  try { path = decodeURIComponent(hex.replace(/../g, '%$&')); } catch (error) { return null; }
  return /[\u0000-\u001f\u007f]/.test(path) ? null : path;
}

// Returns { head, index, protected, files } or { broken: stop_reason, problem }.
function parseSnapshot(out, token) {
  const fail = (problem) => ({ broken: 'snapshot_failed', problem });
  if (!out || typeof out.stdout !== 'string') return fail('the snapshot agent returned no stdout');
  const lines = out.stdout.split('\n');
  while (lines.length && lines[lines.length - 1] === '') lines.pop();
  if (lines.length < 7 || lines[lines.length - 1] !== 'SNAPSHOT-END') return fail('the snapshot is cut short');
  const sum = /^CKSUM\t(\d+)\t(\d+)$/.exec(lines[lines.length - 2]);
  if (!sum) return fail('the snapshot has no checksum line');
  const body = lines.slice(0, -2).join('\n') + '\n';
  if (/[^\t\n -~]/.test(body) || cksum(body) !== Number(sum[1]) || body.length !== Number(sum[2])) {
    return { broken: 'snapshot_tampered', problem: 'the snapshot body does not match its checksum' };
  }
  if (lines[0] !== 'TOKEN\t' + token) return { broken: 'snapshot_tampered', problem: "the snapshot token is not this step's token" };
  const field = (line, name) => (line.startsWith(name + '\t') ? line.slice(name.length + 1) : '');
  const [index, config, guard] = [field(lines[2], 'INDEX'), field(lines[3], 'CONFIG'), field(lines[4], 'PROTECTED')];
  if (![lines[1], index, config, guard].every((hash) => SNAPSHOT_HASH.test(hash))) return fail('a bad HEAD, INDEX, CONFIG or PROTECTED line');
  const files = Object.create(null);
  for (const line of lines.slice(5, -2)) {
    const m = SNAPSHOT_LINE.exec(line);
    const path = m ? unhex(m[2]) : null;
    if (!path || path in files) return fail('a malformed path line');
    files[path] = m[1];
  }
  return { head: lines[1], index, protected: { 'git config': config, 'protected files': guard }, files };
}

// A stop for a missing or broken snapshot, or null.
function snapshotStop(snap, stepName) {
  if (snap && !snap.broken) return null;
  const why = snap ? snap : { broken: 'snapshot_failed', problem: 'the tree snapshot is missing' };
  return { verdict: 'INCOMPLETE', stop_reason: why.broken, open: { step: stepName, problem: why.problem } };
}

// Each snapshot gets its own token from the step label, a counter and the args, so a relay cannot hand back an
// earlier step's output. The counter is deterministic, so a resumed run asks for the same tokens.
let SNAPSHOT_COUNT = 0;
function snapshotToken(label) {
  SNAPSHOT_COUNT += 1;
  const seed = encodeURIComponent(JSON.stringify([label, SNAPSHOT_COUNT, typeof args === 'undefined' ? null : args]));
  return SNAPSHOT_COUNT.toString(16).padStart(4, '0') + cksum(seed).toString(16).padStart(8, '0');
}

// Cheap caps for every agent call of one run. The outermost copy of this code wraps the host agent(); a nested engine
// gets a wrapper that carries the state in .guard, and reuses it. A cap or a null streak stops later work;
// reserved snapshots still verify a writer's changes. stopOverride() names the stop without hiding a safety block.
const guarded = agent && agent.guard ? agent : (() => {
  const given = args && args.maxAgents !== undefined ? args.maxAgents : typeof WORKFLOW_MANIFEST === 'undefined' ? undefined : WORKFLOW_MANIFEST.max_agents;
  if (given !== undefined && given !== null && (!Number.isInteger(given) || given < 1)) throw new Error('maxAgents must be a positive integer');
  const g = { used: 0, nulls: 0, stopped: null, max: given || null, streak: 3, reserved: 0 };
  const run = async (prompt, options) => {
    const validation = g.reserved > 0 && /(^|:)snapshot:/.test(options.label);
    if (!validation && !g.stopped && g.max && g.used + g.reserved >= g.max) { g.stopped = 'agent_cap'; log('Agent cap ' + g.max + ' reached: no further agent runs'); }
    if (g.stopped && !validation) return null;
    if (validation) g.reserved -= 1;
    g.used += 1;
    let out = null;
    try {
      out = await agent(prompt, options);
      return out;
    } finally {
      g.nulls = out === null || out === undefined ? g.nulls + 1 : 0;
      if (!g.stopped && g.nulls >= g.streak) { g.stopped = 'null_streak'; log(g.streak + ' agent results in a row failed: no further agent runs'); }
    }
  };
  run.guard = g;
  return run;
})();
const stopOverride = (verdict, reason) => (verdict !== 'BLOCKED' && guarded.guard.stopped ? ['INCOMPLETE', guarded.guard.stopped] : [verdict, reason]);

// Admit a writing step only when its writers and both possible validation calls fit the shared hard cap.
// Reserved snapshots still run if the writer trips the null streak; later work remains stopped.
function reserveVerification(writers = 1) {
  const g = guarded.guard;
  if (g.stopped) return false;
  if (g.max && g.used + writers + 2 > g.max) {
    g.stopped = 'agent_cap';
    log('Agent cap ' + g.max + ': insufficient capacity for the writer and snapshot retry');
    return false;
  }
  g.reserved = 2;
  return true;
}

// An LLM relays about 4 KB of hex verbatim and can drop characters; the checksum catches that. One retry with a fresh
// token and label absorbs a copy slip without weakening the check: the retry must pass the same checksum and token.
async function takeSnapshot(label, phaseTitle) {
  try {
    const first = await relaySnapshot(label, phaseTitle);
    if (!first.broken) return first;
    log('Snapshot ' + label + ' unusable (' + first.broken + '); taking it once more');
    return await relaySnapshot(label + ':retry', phaseTitle);
  } finally {
    guarded.guard.reserved = 0;
  }
}

async function relaySnapshot(label, phaseTitle) {
  const token = snapshotToken(label);
  let out = null;
  try {
    out = await guarded(
      [
        'You take a tree snapshot. Run exactly this one command with the Bash tool, and no other command:',
        '',
        't=' + token + '; ' + SNAPSHOT_COMMAND,
        '',
        'Do not create, edit or delete any file. Return {"stdout": "<the complete stdout>"} verbatim:',
        'do not summarise, reorder, trim, decode or explain it.',
      ].join('\n'),
      { label, phase: phaseTitle, effort: 'low', model: 'haiku', tools: ['Bash'], schema: SNAPSHOT_SCHEMA }
    );
  } catch (error) {
    log('Snapshot ' + label + ' failed: ' + String((error && error.message) || error));
  }
  return parseSnapshot(out, token);
}

// A pinned command (a test command, an acceptance command) run by a Bash-only agent that relays raw output, like the
// snapshot: the runtime reads the exit code from output it parses itself and trusts no agent's pass/fail report.
//   TOKEN\t<token>                   this step's token, against replay
//   EXIT\t<n>                        exit code of `bash -c <command>` from the repo root, stdin closed, stderr merged
//   TAIL\t<hex>                      the last 400 bytes of the output, as evidence only
//   CKSUM\t<crc>\t<bytes>            POSIX cksum of the three lines above
//   COMMAND-END
// The command comes from the approved plan, never from an agent's report. A relay that runs another command, or
// invents a checksum, is not caught: the same limit as the snapshot. A missing, unparseable, edited or replayed
// result is never a pass. The command has no time limit here beyond the host's Bash tool. Callers snapshot the tree
// around it, so a command that writes a tracked or unignored file stops the run. A command that is blank or spans
// several lines is refused.
const COMMAND_SCHEMA = SNAPSHOT_SCHEMA;
function commandBrief(command, token) {
  const quoted = "'" + command.split("'").join("'\\''") + "'";
  return 't=' + token + '; c=' + quoted + '; ( cd "$(git -c core.fsmonitor=false rev-parse --show-toplevel)" || exit 1; o=$(PYTHONDONTWRITEBYTECODE=1 bash -c "$c" </dev/null 2>&1); rc=$?; '
    + "b=$(printf 'TOKEN\\t%s\\nEXIT\\t%s\\nTAIL\\t%s\\n' \"$t\" \"$rc\" \"$(printf '%s' \"$o\" | tail -c 400 | od -An -tx1 | tr -d ' \\n')\"); "
    + "printf '%s\\n' \"$b\"; printf 'CKSUM\\t%s\\t%s\\n' $(printf '%s\\n' \"$b\" | cksum); echo COMMAND-END )";
}

// Returns { exit, tail } or { broken: stop_reason, problem }.
function parseCommand(out, token) {
  const fail = (problem) => ({ broken: 'command_failed', problem });
  if (!out || typeof out.stdout !== 'string') return fail('the command agent returned no stdout');
  const lines = out.stdout.split('\n');
  while (lines.length && lines[lines.length - 1] === '') lines.pop();
  if (lines.length !== 5 || lines[4] !== 'COMMAND-END') return fail('the command result is cut short');
  const sum = /^CKSUM\t(\d+)\t(\d+)$/.exec(lines[3]);
  if (!sum) return fail('the command result has no checksum line');
  const body = lines.slice(0, 3).join('\n') + '\n';
  if (/[^\t\n -~]/.test(body) || cksum(body) !== Number(sum[1]) || body.length !== Number(sum[2])) {
    return { broken: 'command_tampered', problem: 'the command result does not match its checksum' };
  }
  if (lines[0] !== 'TOKEN\t' + token) return { broken: 'command_tampered', problem: "the command result token is not this step's token" };
  const code = /^EXIT\t(\d{1,3})$/.exec(lines[1]);
  const tail = /^TAIL\t((?:[0-9a-f]{2})*)$/.exec(lines[2]);
  if (!code || !tail) return fail('a bad EXIT or TAIL line');
  const text = tail[1].replace(/../g, (h) => { const n = parseInt(h, 16); return n === 10 ? '\n' : n >= 32 && n < 127 ? String.fromCharCode(n) : '.'; });
  return { exit: Number(code[1]), tail: text };
}

async function relayCommand(command, label, phaseTitle) {
  const token = snapshotToken(label);
  let out = null;
  try {
    out = await guarded(
      [
        'You run one pinned command. Run exactly this one command with the Bash tool, and no other command:',
        '',
        commandBrief(command, token),
        '',
        'Do not create, edit or delete any file. Return {"stdout": "<the complete stdout>"} verbatim:',
        'do not summarise, reorder, trim, decode or explain it.',
      ].join('\n'),
      { label, phase: phaseTitle, effort: 'low', model: 'haiku', tools: ['Bash'], schema: COMMAND_SCHEMA }
    );
  } catch (error) {
    log('Command ' + label + ' failed: ' + String((error && error.message) || error));
  }
  return parseCommand(out, token);
}

// One retry with a fresh token and label absorbs a relay slip; the retry must pass the same checksum and token.
async function runCommand(command, label, phaseTitle) {
  if (typeof command !== 'string' || !command.trim() || /[\u0000-\u001f\u007f]/.test(command)) {
    return { broken: 'command_invalid', problem: 'the pinned command is blank or not one line' };
  }
  const first = await relayCommand(command, label, phaseTitle);
  if (!first.broken) return first;
  log('Command ' + label + ' unusable (' + first.broken + '); running it once more');
  return relayCommand(command, label + ':retry', phaseTitle);
}

// A stop for a command result that is not an exit code, or null.
const commandStop = (res, stepName) => (res.broken ? { verdict: 'INCOMPLETE', stop_reason: res.broken, open: { step: stepName, problem: res.problem } } : null);

// The paths whose content differs between two snapshots, sorted.
function snapshotDelta(before, after, part = 'files') {
  const paths = new Set([...Object.keys(before[part]), ...Object.keys(after[part])]);
  return [...paths].filter((p) => before[part][p] !== after[part][p]).sort();
}

// Checks one step against the snapshot before it. `step` is { name, writes, scope?, frozen? }: a read-only step may change
// nothing; a writing step may change only files in `scope` when a scope is given, and none in `frozen`. Returns null or a stop.
function treeStop(before, after, step) {
  const broken = snapshotStop(after, step.name);
  if (broken) return broken;
  if (after.head !== before.head) return { verdict: 'BLOCKED', stop_reason: 'head_moved', open: { step: step.name, head_before: before.head, head_after: after.head } };
  // Hooks, git config, agent instructions and settings, editor and CI config may change in no step, even inside a
  // writer's scope or with no scope: plan validation already keeps these paths out of every scope.
  const guarded = [...snapshotDelta(before, after, 'protected'), ...snapshotDelta(before, after).filter((file) => pathProblem(file))];
  if (guarded.length) return { verdict: 'BLOCKED', stop_reason: 'protected_changed', open: { step: step.name, changed: guarded } };
  // No member may stage: only the parent stages, after the run. Staging also changes the content delta below.
  if (after.index !== before.index) return { verdict: 'BLOCKED', stop_reason: 'index_changed', open: { step: step.name, changed: snapshotDelta(before, after) } };
  // Frozen files (the scripts and tests a build is judged by) change in no step of the run, in scope or not.
  const thawed = step.frozen ? snapshotDelta(before, after).filter((file) => step.frozen.includes(file)) : [];
  if (thawed.length) return { verdict: 'BLOCKED', stop_reason: 'frozen_changed', open: { step: step.name, changed: thawed } };
  const changed = snapshotDelta(before, after);
  if (!step.writes && changed.length) return { verdict: 'BLOCKED', stop_reason: 'read_only_wrote', open: { step: step.name, changed } };
  const outside = step.scope ? changed.filter((file) => !step.scope.includes(file)) : [];
  if (outside.length) return { verdict: 'BLOCKED', stop_reason: 'out_of_scope', open: { step: step.name, outside, allowed: step.scope } };
  return null;
}

// A writer's reported files must equal the observed changes, both ways.
function reportStop(changed, reported, stepName) {
  const said = [...new Set(reported)];
  const unreported = changed.filter((file) => !said.includes(file));
  const unchanged = said.filter((file) => !changed.includes(file));
  if (!unreported.length && !unchanged.length) return null;
  return { verdict: 'BLOCKED', stop_reason: 'report_mismatch', open: { step: stepName, observed: changed, reported: said, unreported, unchanged } };
}

// One spelling per path: no leading ./, no . segments, no doubled or trailing slash.
function normalPath(file) {
  return String(file).split('/').filter((part) => part !== '' && part !== '.').join('/');
}

// Agents often report absolute paths, and the run knows only repo-relative ones (a live run reported
// /Users/.../scripts/x.py). An absolute path that ends in '/' + a known path is that path, the longest match first.
// This only matches a report to the tree: the snapshots, not the report, decide what changed.
function repoPath(file, known) {
  const path = normalPath(file);
  if (!String(file).startsWith('/')) return path;
  const hit = known.filter((rel) => path.endsWith('/' + rel)).sort((a, b) => b.length - a.length)[0];
  return hit || path;
}

// Paths no workflow may plan or change: git state, agent instructions and settings, hooks, editor and CI config.
// A directory matches as any path segment and a file as the basename, at any depth (a nested repo has its own),
// case-insensitively because macOS volumes usually are. Build files such as package.json stay allowed: they reach
// review as ordinary diffs. PROTECTED_ROOTS match only from the repo root, because their names are ordinary code
// deeper down (src/hooks stays allowed; a root hooks/ is refused in every repo): hooks holds the live agent safety
// hooks that ~/.agents/hooks links to, scripts/git-hooks is the git core.hooksPath, agents/workflows holds the saved workflow
// scripts that ~/.claude/workflows links to, skills/universal/agents-subagents/scripts holds the shared runtime and its gates, and agents/claude and agents/codex hold the reviewer, judge and refuter definitions that ~/.claude/agents links to: a writer must not rewrite the code that judges it (the next run would load the edit); the parent edits these by hand. Ignored files under them, such
// as a stale __pycache__ that a hook test rewrites, are hashed too, so such a run stops once as protected_changed. Each list is one JSON array on one line: the generator copies all three into the Codex rule.
const PROTECTED_DIRS = [".git", ".claude", ".codex", ".agents", ".github", ".husky", ".vscode", ".idea", ".devcontainer"];
const PROTECTED_FILES = ["CLAUDE.md", "AGENTS.md", ".mcp.json", ".claude.json", ".envrc", ".gitattributes", ".gitmodules", ".pre-commit-config.yaml"];
const PROTECTED_ROOTS = ["hooks", "scripts/git-hooks", "agents/workflows", "skills/universal/agents-subagents/scripts", "agents/claude", "agents/codex"];

// Why a planned path may not be used, or null.
function pathProblem(file) {
  if (typeof file !== 'string' || !file.trim()) return 'is blank';
  if (/[\u0000-\u001f\u007f\\]/.test(file)) return 'has a backslash or a control character';
  if (file.startsWith('/') || /^[A-Za-z]:/.test(file) || file.startsWith('~')) return 'is absolute';
  const path = normalPath(file);
  if (!path || path.split('/').includes('..')) return 'has a .. segment';
  const parts = path.toLowerCase().split('/');
  const name = parts[parts.length - 1];
  if (parts.some((part) => PROTECTED_DIRS.some((dir) => dir.toLowerCase() === part))) return 'is under a protected directory';
  if (PROTECTED_FILES.some((file) => file.toLowerCase() === name)) return 'is a protected file';
  if (PROTECTED_ROOTS.some((root) => (parts.join('/') + '/').startsWith(root.toLowerCase() + '/'))) return 'is under a protected repo-root folder';
  if (/^settings[^/]*\.json$/.test(name)) return 'is a settings file';
  return null;
}

// check_defect: a builder or fixer that believes a check it is judged by is itself wrong must not edit that check.
// It fills the optional check_defect string instead; a nonblank value stops the run as BLOCKED, stop reason
// check_defect, with the text in the escalation. Empty or absent means no defect.
const CHECK_DEFECT_RULE = 'If a check you are judged by is wrong, do not edit it; fill check_defect with the check name and why.';
const withCheckDefect = (schema) => (schema && schema.type === 'object'
  ? { ...schema, properties: { ...schema.properties, check_defect: { type: 'string', description: 'Empty unless a check you are judged by is wrong: its name and why. Never edit that check.' } } }
  : schema);
const checkDefectOf = (out) => (out && typeof out.check_defect === 'string' && out.check_defect.trim() ? out.check_defect.trim() : null);
