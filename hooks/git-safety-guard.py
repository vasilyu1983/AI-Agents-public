#!/usr/bin/env python3
"""PreToolUse guard: stop agents from destroying uncommitted work in a shared tree.

Why this exists: parallel subagents running `git stash` or `git checkout` in
the shared working tree have already clobbered a peer's uncommitted edit here.
`git stash` is the worst offender:
- it silently removes every agent's changes, not just the caller's;
- the stash ref is shared across all worktrees of a repository, so a
  `git stash pop` in one worktree can apply another agent's stash.

Runtimes: Claude Code and Codex both send PreToolUse JSON on stdin with
`tool_name: "Bash"` and `tool_input.command`. Codex may send the command as
an argv array. Both runtimes treat exit code 2 as "block" and show stderr to
the model, so this one script serves both. Claude Code's `Monitor` tool and
Desktop Commander's `start_process` also run shell text and are checked the
same way; input sent to a running process (`interact_with_process`) cannot be
parsed, so it blocks when it mentions git.

The command text is read the way the shell reads it: backslash-newline
continuations are joined, `#` comments end at the newline (not at the end of
the whole payload), and `$(...)` or backtick substitutions inside double
quotes are parsed as commands. A literal `cd`/`pushd` moves the directory
later calls are checked in. A `cd` can only remove the linked-worktree
exemption: it applies after a `cd` only when the session already runs in a
linked worktree, and never after `popd`, `cd -` or a `cd` to an expansion. Long options are matched by the
shortest prefix git accepts (`reset --h` is `reset --hard`); `--autostash` on
pull, merge and rebase counts as a stash.

Policy: the protected branches (`vcs.protected_branches`), the merge base (`vcs.default_base`) and the
push allowlist (`vcs.remotes_allowed`) come from the policy file that hooks/policy.py loads (AGENTS_POLICY,
then ~/.agents/policy.json, then config/policy.json), once at import. "The branches the policy protects"
below means that list; no branch name is built into the guard. If the policy cannot be loaded, the guard
fails closed: a payload that mentions git or a floor command (gh, rm, curl, wget, dd, mkfs) exits 2 with
"git-safety-guard: policy unreadable (<reason>): git blocked"; other payloads pass.

Tiers:
- ALWAYS blocked (parent and subagents): commands that discard working-tree
  changes nobody committed.
- STASH: `git stash list/show/create` pass (read-only). Every other stash form
  is blocked for subagents and asks the human in the parent session: exit 0
  with PreToolUse JSON `permissionDecision: "ask"`. Claude Code prompts, even
  in auto mode. Codex parses "ask" but does not support it yet, so there the
  prompt comes from the `git stash` prompt rule in codex/safety.rules.
- SUBAGENT-ONLY blocked: commands that are safe for a single operator but move
  the shared tree or index under peers (branch switches, rebases, commits,
  bulk staging). A subagent inside its own linked worktree is exempt from
  this tier, since nobody else shares that index.
- HOOK BYPASS and FORCE PUSH, blocked for everyone: `--no-verify` and its
  unambiguous prefixes (plus `-n` for commit and am, alone or in a short
  cluster); a `core.hooksPath` override through `-c`, `--config-env`,
  GIT_CONFIG_KEY_<n> / GIT_CONFIG_PARAMETERS or `git config`; and a force push
  (`-f`, `--force`, `--force-with-lease`, `--mirror`, `+ref`) or delete that
  targets a branch the policy protects. A force push without a refspec counts as protected,
  because a hook cannot know the current branch. A `git push` with no refspec
  and no force flag reads `remote.<name>.push` and `remote.<name>.mirror` in
  the target repository, and a `+` refspec or a mirror that reaches a protected branch
  counts as a force push; so does the same setting passed with `git -c`. The
  minimum prefixes were measured with `git <sub> <prefix> -h` on git 2.51.0.
- PUSH ALLOWLIST, blocked for everyone: a `git push` (any form above, including `-c`, `-C` and refspecs)
  whose remote URL is outside `vcs.remotes_allowed` ("push to a remote outside the policy allowlist"). The
  remote name is resolved with `git remote get-url --push --all <name>` in the target directory (no remote
  named: `remote.pushDefault`, the branch's remote, then `origin`). https://, ssh:// and git@host:path URLs
  become `host/path` without credentials, port or trailing `.git`, and match with fnmatch (case folded)
  against each pattern. A literal URL as the target is matched directly. A remote that cannot be resolved
  (no such remote, not a repository, a name from an expansion) is outside the allowlist. A push that sets
  `remote.<name>.url`, `remote.<name>.pushurl`, `url.<base>.insteadOf` or `url.<base>.pushInsteadOf` through
  `-c`, `--config-env` or GIT_CONFIG_* is blocked, because the override changes where the name resolves
  after the check; so is `include.path`/`includeIf.*.path`, or GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM, GIT_CONFIG,
  GIT_DIR or GIT_COMMON_DIR set in the same segment, since they load the same keys from another file. A variable
  exported in an earlier segment is not followed (known gap). An absent or empty `remotes_allowed` list turns this rule off.
- UNQUOTED EXPANSIONS, blocked for everyone: for commit, am, push, merge, rebase,
  reset, restore, switch, rm, gc and repack, an argument that is wholly an unquoted
  `$X`, `${X}`, `$(...)` or backtick expansion, unless it is the value of an option
  that takes one (`-F $f`, `-m $m`). The shell splits it into words, so it can carry
  `--no-verify`, `--force` or `--hard`. Words that `xargs` appends count the same
  way (`echo --hard | xargs git reset`); put paths after `--` and they pass. A quoted
  expansion is one word and keeps the existing rules: `git push origin "$branch"`
  passes, as before.
- GIT IN A VARIABLE: a command word that is `$g`, `${g}` or `"$g"`, where the same
  command line assigns `g=git` (or a path ending in `/git`, `export g=git`), is read as
  `git`. A variable that is not assigned in the command line stays unknown and passes,
  like any unknown wrapper; one assigned from text that mentions git but is not plainly
  `git` (`g=$(command -v git)`) fails closed, like other output the guard cannot see.

- NON-GIT FLOOR, blocked for everyone (a human at the `!` prompt can still run these): recursive `rm` of `/`,
  `~` or `$HOME` (also `/*`, `~/*`); recursive `rm` of a `.git` directory (`rm -rf .git`, `./.git/`,
  `$PWD/.git`, `.git/*`, `.*`; single files such as `rm .git/index.lock` pass); `curl|wget` piped into a shell, `sh -c "$(curl ...)"` and `bash <(curl ...)`;
  `gh repo delete` and `gh api` with DELETE; `gh pr merge` with `--admin`, without a 40-hex `--match-head-commit`,
  without one explicit `-R <owner/repo>` and PR number, or into a base other than the policy's merge base (read with
  `gh pr view <n> --repo <r>`, 10 s timeout; no answer blocks); a PUT to `gh api .../pulls/<n>/merge` and a
  `mergePullRequest` GraphQL call; a `gh pr merge` that shares its command line with another gh call; a gh
  command word, or any text in a `gh pr merge` or `gh api` call, from a `$` or backtick expansion; a gh alias,
  expanded from `gh alias list` and checked as that command, and blocked when it is a `!` shell alias, nests
  or cannot be read; a command word `$g` assigned gh, rm or dd on the same line is read as that command,
  and one assigned from other text that names them blocks; `mkfs*`; `dd of=/dev/...` (not null, stdout, stderr). It reuses the
  wrapper unwrapping above. A stage before the shell other than the fetcher (`curl x | tee f | sh`) is not seen.

A subagent is detected by the `agent_id` field, which both Claude Code and
Codex send for subagent tool calls, or by GIT_SAFETY_STRICT=1 in the
environment, which forces subagent rules for a whole session (teammates and
harnesses that run as top-level sessions).

Aliases are resolved: inline `git -c alias.x=stash x` and persistent aliases
from git config (looked up only for non-builtin subcommands, because git
ignores aliases that shadow builtins).

`git checkout <x>` is treated as a path checkout unless `x` resolves to a
commit in the target repository (after `cd` and `-C`), so `checkout feature`
passes and `checkout rules/x.md` is blocked. Heredoc bodies are data and are
not parsed, except command substitutions inside an unquoted heredoc, which the
shell would run.

A heredoc fed to a shell (`bash <<EOF`) is code, so its body is parsed.
Text that a shell reads on stdin is parsed too: a here-string
(`bash <<<"..."`), and a pipe from a literal `echo` or `printf`
(`echo 'git stash' | bash`). A pipe from any other producer into a shell
that reads stdin fails closed when the pipeline mentions git. `git rebase
-x/--exec <cmd>` bodies are parsed. The command name `git` matches in any
case (`GIT`, `/usr/bin/Git`), because a case-insensitive macOS filesystem
runs it.

Interpreter inline code (`python3 -c`, `node -e`, `perl -e`, `ruby -e`, and
a heredoc, here-string or literal pipe that python or node reads as its
script) is checked when it mentions git: every string literal, and every
list of string literals joined as argv (`["git", "stash"]`), is parsed as a
command. If the code shells out (`os.system`, `subprocess`, `exec`, `spawn`,
`system(`, backticks) and no literal gives a complete git command, it fails
closed. Code with no git word passes untouched.

Literal find/fd execution actions and env split strings are parsed as argv. An escaped or
quoted lone `;` or parenthesis stays a word, so a grouped find predicate or a second `-exec`
after a first one keeps every action. A command that git builds from the shell
(`--no-verify$IFS-m`, `${E}--no-verify`, `$'--no-verify'`, `{commit,--no-verify}`) is blocked
like an unquoted expansion.
Non-preview clean, reflog deletion/expiry, and explicit gc pruning are blocked.
Dry-run recovery inspection and gc --prune=never remain available.

Known blind spots, by design: scripts on disk (`bash x.sh`, `python3 x.py`,
`bash < x.sh`, `cat x.sh | bash` with no git word in the pipeline);
interpreter code that builds the git command at runtime and does not shell
out in a form listed above (for example a helper module), or that also holds
a complete literal git command; a quoted expansion in a flag position
(`git commit "$FLAGS"`) or a `+` inside a quoted refspec variable; push
settings from GIT_CONFIG_* variables; a `cd` inside a subshell, which the
guard applies to later commands too (so a branch name may be resolved in the
wrong repository); `--git-dir`/`--work-tree`; hooksPath values that come from config
files; config keys that run a command or prune (`-c core.editor=...`, `-c gc.pruneExpire=now gc`);
a shell, wrapper or package runner that is not in SHELLS or WRAPPERS; an unquoted
`bash -c $(...)`; and other git features that run commands (`bisect run`, `submodule
foreach`, `filter-branch`). This is a seatbelt against habitual commands, not
a sandbox; worktree isolation is the structural fix.

Failure policy: input that is not a JSON object, a shell payload with no
command, or an internal error blocks (exit 2) when the raw stdin contains a
`git` word, and allows (exit 0) otherwise, so a guard bug never blocks every
non-git command. A git call the parser reaches but cannot classify
(subcommand from a shell expansion or from xargs stdin) fails closed. There
is no switch that turns the guard off. Humans who need a blocked command run
it in their own terminal.
"""

import fnmatch
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SHELL_SPLIT = re.compile(r"&&|\|\||;|\||\n")
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "mksh", "ash", "fish", "csh", "tcsh"}

SAFE_ALTERNATIVE = (
    "Safe alternatives: snapshot with `git diff > \"$TMPDIR/snap.patch\"` "
    "(add `git diff --cached` for staged work), isolate with "
    "`git worktree add ../wt-<task> -b <task>`, or ask the parent agent or "
    "human to run it. See docs/hooks-and-safety.md."
)


# shlex glues adjacent punctuation (`);`, `()`, `|&`), so any all-punctuation token
# ends a simple command. Redirections are dropped with their target and fd.
OPERATOR = re.compile(r"[();<>|&]+")
REDIRECT = re.compile(r"(?:>>?|<<?<?|>&|<&|&>>?|>\|)-?")
# Commands that exec a later argv element. The first `git` token after one of
# these is the real command, whatever options or durations sit in between.
WRAPPERS = {"command", "exec", "nohup", "time", "env", "sudo", "doas", "timeout", "gtimeout",
            "nice", "ionice", "stdbuf", "caffeinate", "chronic", "unbuffer", "setsid", "xargs",
            "xcrun", "arch", "flock", "uv", "watch", "parallel", "script", "mise", "direnv", "poetry",
            "pipenv", "pnpm", "npx", "bunx", "yarn"}
# Git never lets an alias shadow these, so no alias lookup is needed for them.
BUILTINS = {"add", "am", "apply", "bisect", "blame", "branch", "checkout", "checkout-index",
            "cherry-pick", "clean", "clone", "commit", "config", "diff", "fetch", "grep", "init",
            "log", "merge", "mv", "pull", "push", "read-tree", "rebase", "reflog", "remote",
            "reset", "restore", "revert", "rm", "show", "stash", "status", "switch",
            "symbolic-ref", "tag", "update-ref", "worktree", "ls-files", "ls-tree", "rev-parse",
            "rev-list", "cat-file", "describe", "shortlog", "merge-base", "for-each-ref",
            "show-ref", "diff-tree", "check-ignore", "submodule", "notes", "format-patch", "help",
            "version", "gc", "fsck"}
UNVERIFIABLE = "__unverifiable__"  # [UNVERIFIABLE] or [UNVERIFIABLE, reason]
HOOKS_OVERRIDE = "__hooks_override__"
FORCE_CONFIG = "__force_config__"
REDIRECT_CONFIG = "__redirect_config__"
MARKERS = {UNVERIFIABLE, HOOKS_OVERRIDE, FORCE_CONFIG, REDIRECT_CONFIG}
GUARDED = {"commit", "am", "push", "merge", "rebase", "pull", "reset", "clean", "checkout", "restore", "rm",
           "switch", "gc", "reflog", "prune", "repack"}  # subcommands where a flag built by the shell matters
# Subcommands where an argument that starts with an unquoted expansion (or is appended by xargs) can carry a
# hook-skip, force or discard flag. Others keep the flag-name check only: git rejects or ignores a stray word.
EXPANSION_SUBS = {"commit", "am", "push", "merge", "rebase", "reset", "restore", "switch", "rm", "gc", "repack"}
STASH_READ_ONLY = {"list", "show", "create"}  # `create` writes a dangling commit, never the tree or refs/stash
SHELL_TOOLS = {"Bash", "shell", "local_shell", "exec_command", "Monitor"}
# Desktop Commander runs shell text in `start_process` and types `input` into a live process.
PROCESS_TOOLS = re.compile(r"mcp__.*desktop-commander.*__(start_process|interact_with_process)")
GIT_WORD = re.compile(r"(?<![\w.-])git(?![\w./-])", re.I)  # `GIT` runs git on macOS


def load_policy():
    """(protected branches, merge base, allowed remotes, error). Any failure returns an error text."""
    here = Path(__file__)
    try:
        for folder in (here.resolve().parent, here.parent):  # the installed guard is a symlink into the repo
            module = folder / "policy.py"
            if module.is_file():
                break
        else:
            raise RuntimeError("hooks/policy.py not found next to the guard")
        spec = importlib.util.spec_from_file_location("agents_policy", module)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        vcs = mod.load()["vcs"]
        allowed = vcs.get("remotes_allowed") or []
        if not (isinstance(allowed, list) and all(isinstance(a, str) for a in allowed)):
            raise RuntimeError("vcs.remotes_allowed must be a list of strings")
        return set(vcs["protected_branches"]), vcs["default_base"], allowed, None
    except Exception as exc:  # PolicyError, a missing loader or a broken one: all fail closed
        return set(), None, [], " ".join(str(exc).split())


PROTECTED, MERGE_BASE, REMOTES_ALLOWED, POLICY_ERROR = load_policy()
# Subcommand -> (shortest unambiguous prefix of --no-verify, `-n` also skips hooks).
# Measured on git 2.51.0; for merge and pull every shorter prefix is ambiguous.
NO_VERIFY = {"commit": ("--no-veri", True), "am": ("--no-v", True), "push": ("--no-veri", False),
             "rebase": ("--no-veri", False), "merge": ("--no-verify", False), "pull": ("--no-verify", False)}
# Subcommand -> (short options with a value, short options with an optional attached value,
# long options whose value may be the next argument).
OPTION_VALUES = {
    "commit": ("mFcCtU", "uS", {"--message", "--file", "--author", "--date", "--reedit-message",
                                "--reuse-message", "--fixup", "--squash", "--trailer", "--template",
                                "--cleanup", "--pathspec-from-file", "--unified"}),
    "am": ("Cp", "S", {"--whitespace", "--directory", "--exclude", "--include", "--patch-format",
                       "--resolvemsg"}),
    "push": ("o", "", {"--repo", "--receive-pack", "--exec", "--push-option", "--recurse-submodules"}),
}
# Value-taking options for the unquoted-expansion rule. merge and rebase are kept out of
# OPTION_VALUES so that the --no-verify parsing of those subcommands does not change.
EXPANSION_VALUES = dict(OPTION_VALUES, **{
    "merge": ("mFsX", "S", {"--message", "--file", "--strategy", "--strategy-option", "--into-name",
                            "--cleanup"}),
    "rebase": ("sXxC", "S", {"--onto", "--strategy", "--strategy-option", "--exec", "--empty",
                             "--whitespace"}),
})
# Subcommand -> {flag: shortest unambiguous prefix}. git accepts any unique prefix of a long
# option, so `reset --h` is `reset --hard`. Measured on git 2.51.0.
DESTRUCTIVE_PREFIX = {"reset": {"--hard": "--h", "--merge": "--me", "--keep": "--k"},
                      "clean": {"--force": "--f"}, "rm": {"--force": "--f"},
                      "switch": {"--discard-changes": "--di", "--force": "--fo"},
                      "restore": {"--worktree": "--w"},
                      "checkout": {"--pathspec-from-file": "--pathspec-fr"}}
AUTOSTASH_PREFIX = {"pull": "--au", "merge": "--au", "rebase": "--autost"}
CONFIG_READS = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "-l", "--list"}
# Marks a `$` or backtick that the shell would expand unquoted; tokenize() adds it.
MARK = "\x01"
SHELL_QUOTING = re.compile(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"|\\.|[$`]", re.S)
# An escaped or quoted lone `;`, `(`, `)`, `&`, `|`, `<` or `>` is a word, not an operator. mark_expansions() swaps
# it for a control character that shlex keeps inside the word; segments() swaps it back.
LITERAL_PUNCT = dict(zip(";()&|<>", map(chr, range(16, 23))))
UNLITERAL = str.maketrans({v: k for k, v in LITERAL_PUNCT.items()})
LONE_PUNCT = re.compile(r"\\[;()&|<>]|'[;()&|<>]'|\"[;()&|<>]\"")
BRACE = re.compile(r"(?<!\$)\{[^{}]*,[^{}]*\}")  # unquoted `{a,b}`: the shell builds several words from one
INTERPRETER = re.compile(r"(?:python|pypy)[\d.]*|node(?:js)?|perl[\d.]*|ruby[\d.]*")
# A string literal in python, node, perl or ruby code; backticks run a shell in perl and ruby.
LITERAL = re.compile(r'"""(.*?)"""|\'\'\'(.*?)\'\'\'|"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\'|`((?:[^`\\]|\\.)*)`',
                     re.S)
INTERPOLATION = re.compile(r"\$?\{[^{}]*\}|#\{[^{}]*\}|%\(\w+\)[sdr]|%[sdr]")
# Checked on code with its string literals removed, so prose inside strings does not count.
SHELLS_OUT = re.compile(r"%x\W|\b(?:system|popen\w*|subprocess|exec\w*|spawn\w*|qx|check_output|check_call"
                        r"|getoutput|Open3|child_process|pty)\b")
GROUP_END = {"}", "done", "fi", "esac"}
# Commands whose `NAME=value` arguments set environment variables for what they run.
ASSIGNERS = {"export", "declare", "typeset", "readonly", "local"}


class Ask(str):
    """A reason that prompts the human instead of blocking."""


class Rule(str):
    """A block reason that carries its own remedy (no stash/worktree advice)."""


# Shell syntax that can precede a command in the same simple-command segment.
KEYWORDS = {"!", "{", "}", "if", "then", "else", "elif", "do", "while", "until"}
SHELL_C = re.compile(r"-[a-z]*c[a-z]*")  # `-c`, `-lc`, `-ec`
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*", re.S)
HEREDOC = re.compile(r"(?<!<)<<-?(?!<)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")


FLOOR_WORD = re.compile(r"\b(?:rm|curl|wget|gh|dd|mkfs\S*)\b")  # words the non-git floor watches
DOWNLOAD_SHELL = "__download_to_shell__"  # synthetic segment: a shell runs what curl or wget fetched
FETCHERS = {"curl", "wget"}
FLOOR_COMMANDS = {"rm", "gh", "dd"}

# Block log: one JSON line per block, never the command text, paths or cwd (they can carry secrets).
# GUARD_BLOCK_LOG overrides the path (tests). Logging never changes the exit code.
BLOCK_RULES = [  # (text in the block reason, stable rule id); first match wins
    ("core.hooksPath", "git:hooks-path"), ("--no-verify", "git:no-verify"), ("remote.<name>.push", "git:force-config"),
    ("Deleting the remote branch", "git:push-delete"), ("Force-pushing", "git:force-push"),
    ("expands unquoted", "git:unquoted-expansion"), ("Subagents must not run `git stash`", "git:stash-subagent"),
    ("--autostash", "git:autostash-subagent"), ("reset --hard", "git:reset-hard"), ("git checkout <path>", "git:checkout-paths"),
    ("`git restore`", "git:restore"), ("`git rm -f`", "git:rm-force"), ("`git clean`", "git:clean"),
    ("Reflog expiry", "git:reflog-expire"), ("`git prune`", "git:prune"), ("`git repack", "git:repack"),
    ("garbage collection", "git:gc-prune"), ("`git switch", "git:switch-discard"), ("worktree remove", "git:worktree-remove-force"),
    ("refs/stash", "git:stash-ref"), ("read-tree", "git:read-tree-u"), ("checkout-index", "git:checkout-index-force"),
    ("cannot be checked", "git:unverifiable"), ("switch branches", "git:subagent-switch"),
    ("Subagents must not run `git", "git:subagent-integrate"), ("rewrite the shared index", "git:subagent-index"),
    ("Subagents commit only", "git:subagent-commit"), ("Subagents must stage", "git:subagent-add-bulk"),
    ("force-delete", "git:subagent-branch-force"),
]
FLOOR_RULES = {"recursive rm of a .git directory": "floor:rm-git-dir", "a shell runs a script that curl or wget downloads": "floor:download-shell", "mkfs formats a filesystem": "floor:mkfs",
               "dd writes to a device": "floor:dd-device", "gh repo delete removes a repository": "floor:gh-repo-delete",
               "gh api with the DELETE method": "floor:gh-api-delete", "recursive rm of / or the home directory": "floor:rm-root",
               "gh pr merge --admin bypasses branch protection": "floor:gh-merge-admin",
               "gh pr merge without --match-head-commit <the 40-character head_sha from adversarial-review>": "floor:gh-merge-unpinned",
               "gh api merges a pull request without the reviewed-commit pin": "floor:gh-api-merge",
               "gh pr merge into a base other than the policy's merge base, or a base gh could not read": "floor:gh-merge-base",
               "gh pr merge without one -R <owner/repo> and the PR number": "floor:gh-merge-repo",
               "gh pr merge shares its command line with another gh call": "floor:gh-merge-shared",
               "a gh command word comes from a shell expansion, so it cannot be checked": "floor:gh-expansion",
               "a gh pr merge or gh api call takes text from a shell expansion, so it cannot be checked": "floor:gh-expansion",
               "a gh alias that the guard could not resolve": "floor:gh-alias"}


def log_block(rule, event=None, agent=None):
    """Append one JSON line for a block; on any failure print one short line and carry on."""
    try:
        runtime = None
        if isinstance(event, dict):
            tool_input = event.get("tool_input")
            argv = isinstance(tool_input, dict) and isinstance(tool_input.get("command") or tool_input.get("cmd"), list)
            name = event.get("tool_name")
            runtime = "codex" if argv or name in {"shell", "local_shell", "exec_command"} else "claude" if name in {"Bash", "Monitor"} else None
        entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "hook": "git-safety-guard", "rule": rule}
        if runtime:
            entry["runtime"] = runtime
        if agent:
            entry["agent"] = agent
        path = Path(os.environ.get("GUARD_BLOCK_LOG") or Path(__file__).resolve().parent.parent / "telemetry" / "guard-blocks.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as exc:
        print(f"git-safety-guard: block log failed ({type(exc).__name__})", file=sys.stderr)


def reason_rule(reason):
    return next((rid for text, rid in BLOCK_RULES if text in reason), "git:other")


def base(token):
    """Command name of a token, lowercased: macOS runs `GIT` and `/usr/bin/Git` as git."""
    return os.path.basename(token).lower()


def truthy(value):
    return value.strip().lower() in {"", "true", "yes", "on", "1"}


def forced_protected(spec):
    """True if a `+src:dst` push refspec force-updates a protected branch."""
    spec = spec.strip()
    if not spec.startswith("+"):
        return False
    src, sep, dst = spec[1:].partition(":")
    return protected_ref(dst if sep else src)


REDIRECT_KEY = re.compile(r"remote\..+\.(url|pushurl)|url\..+\.(insteadof|pushinsteadof)|include\.path|includeif\..+\.path", re.S)
# Environment variables that point git at another config or repository, so the same keys can arrive indirectly.
REDIRECT_ENV = {"GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM", "GIT_CONFIG", "GIT_DIR", "GIT_COMMON_DIR"}


def redirects_remote(key):
    """True if a config key changes where a remote name resolves, or includes a file that can (include.path)."""
    return bool(REDIRECT_KEY.fullmatch(key.lower()))


def forces_by_config(pair):
    """True if `-c remote.<name>.push=+...` or `remote.<name>.mirror` makes a push force a protected branch."""
    key, _, value = pair.partition("=")
    key = key.lower()
    if re.fullmatch(r"remote\..+\.mirror", key, re.S):
        return truthy(value)
    return bool(re.fullmatch(r"remote\..+\.push", key, re.S)) and forced_protected(value)


def git_args(tokens):
    """Return (subcommand argv, inline aliases, -C dir) for a git call, or None."""
    i = 0
    while i < len(tokens) and (tokens[i] in KEYWORDS or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[i])):
        i += 1  # `then git ...`, `! git ...`, env assignments: FOO=1 git ...
    via_xargs = False
    if i < len(tokens) and base(tokens[i]) in WRAPPERS:
        j = next((k for k in range(i, len(tokens)) if base(tokens[k]) == "git"), None)
        if j is None:
            return None
        via_xargs = "xargs" in (base(t) for t in tokens[i:j])
        i = j
    if i >= len(tokens) or base(tokens[i]) != "git":
        return None
    i += 1
    aliases, cdir, hooks, force, redirect = {}, "", False, False, False
    while i < len(tokens) and tokens[i].startswith("-"):
        # global options: -C <dir>, -c <k=v>, --config-env <k=VAR>, --git-dir=..., --no-pager
        if tokens[i] in {"-c", "--config-env"} and i + 1 < len(tokens):
            m = re.fullmatch(r"alias\.([^=]+)=(.*)", tokens[i + 1], re.S)
            if m and tokens[i] == "-c":
                aliases[m.group(1).lower()] = m.group(2)
            hooks = hooks or tokens[i + 1].split("=", 1)[0].lower() == "core.hookspath"
            force = force or (tokens[i] == "-c" and forces_by_config(tokens[i + 1]))
            redirect = redirect or redirects_remote(tokens[i + 1].split("=", 1)[0])
        if tokens[i].startswith("--config-env="):
            hooks = hooks or tokens[i][len("--config-env="):].split("=", 1)[0].lower() == "core.hookspath"
            redirect = redirect or redirects_remote(tokens[i][len("--config-env="):].split("=", 1)[0])
        if tokens[i] == "-C" and i + 1 < len(tokens):
            cdir = os.path.join(cdir, tokens[i + 1])
        i += 2 if tokens[i] in {"-C", "-c", "--config-env", "--git-dir", "--work-tree", "--namespace",
                                "--attr-source"} else 1
    if hooks:
        return [HOOKS_OVERRIDE], aliases, cdir
    if force:
        return [FORCE_CONFIG], aliases, cdir
    args = tokens[i:]
    if redirect and REMOTES_ALLOWED and args and (args[0] == "push" or aliases.get(args[0], "").split()[:1] == ["push"]):
        return [REDIRECT_CONFIG], aliases, cdir
    if (via_xargs and not args) or (args and (re.search(r"[$`]", args[0]) or BRACE.search(args[0]))):
        return [UNVERIFIABLE], aliases, cdir  # subcommand comes from stdin, an expansion or a brace expansion
    if via_xargs and args[:1] == ["checkout"]:
        args = args + ["--"]  # xargs appends paths read from stdin
    elif via_xargs and args[:1] and args[0] in EXPANSION_SUBS:
        args = args + [MARK + "$"]  # xargs appends words read from stdin, as an unquoted expansion would
    return args, aliases, cdir


def git_ok(cwd, *argv):
    """Run a read-only git query; return stdout lines, or None on failure."""
    try:
        out = subprocess.run(["git", "-C", cwd, *argv], capture_output=True, text=True, timeout=2)
        return out.stdout.splitlines() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def is_ref(name, cwd):
    return git_ok(cwd, "rev-parse", "--verify", "-q", "--end-of-options", name + "^{commit}") is not None


def in_linked_worktree(cwd):
    """A linked worktree's git dir differs from the common dir; the main tree's does not."""
    dirs = git_ok(cwd, "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir")
    return bool(dirs) and len(dirs) == 2 and dirs[0] != dirs[1]


def config_alias(name, cwd):
    """Persistent alias value from git config, or None."""
    lines = git_ok(cwd, "config", "--get", f"alias.{name}")
    return "\n".join(lines).strip() or None if lines is not None else None


def expand(args, aliases, cwd, depth=0):
    """Yield every git argv an invocation can run, expanding aliases."""
    if not args or depth > 3 or args[0] in BUILTINS or args[0] in MARKERS:
        yield args
        return
    value = aliases.get(args[0].lower()) or config_alias(args[0], cwd)
    if value is None:
        yield args
    elif value.startswith("!"):  # shell alias: check every git call inside it
        for tokens in segments(value[1:]):
            found = git_args(tokens)
            if found:
                yield from expand(found[0], aliases, os.path.join(cwd, found[2]), depth + 1)
    else:
        yield from expand(shlex.split(value) + args[1:], aliases, cwd, depth + 1)


def has_flag(args, *names, sub=None):
    """True if any flag in names is present, including inside combined short flags (-fd)
    and, given `sub`, a long-option prefix git accepts for it (`reset --h`)."""
    shorts = {n[1] for n in names if len(n) == 2 and n[0] == "-" and n[1] != "-"}
    prefixes = [v for k, v in DESTRUCTIVE_PREFIX.get(sub, {}).items() if k in names]
    for a in args:
        if a in names:
            return True
        word = a.split("=", 1)[0]
        if any(word.startswith(p) and n.startswith(word) for p in prefixes
               for n in names if n.startswith(p)):
            return True
        if shorts and re.fullmatch(r"-[a-zA-Z]{2,}", a) and shorts & set(a[1:]):
            return True
    return False


def overwrites_paths(rest, cwd):
    """`git checkout <ref> <path>`, or `git checkout <x>` where x is not a commit-ish."""
    if has_flag(rest, "-b", "-B", "--orphan"):
        return False
    positional = [a for a in rest if not a.startswith("-")]
    if len(positional) >= 2:
        return True
    return len(positional) == 1 and not is_ref(positional[0], cwd)


def walk(sub, rest, table=OPTION_VALUES):
    """Split args into (flags, positionals) as parse-options reads them.

    A short cluster becomes one flag per letter and stops at a letter that takes
    a value (`-anm x` -> -a -n -m; `-uno` -> -u). Option values are skipped.
    """
    short_val, short_opt, long_val = table.get(sub, ("", "", set()))
    flags, positional, i = [], [], 0
    while i < len(rest):
        a = rest[i]
        i += 1
        if a == "--":
            positional += rest[i:]
            break
        if a.startswith("--"):
            flags.append(a)
            i += a in long_val
        elif a.startswith("-") and len(a) > 1:
            for k, c in enumerate(a[1:], 2):
                flags.append("-" + c)
                if c in short_val or c in short_opt:
                    i += c in short_val and k == len(a)  # `-m x`: the value is the next argument
                    break
        else:
            positional.append(a)
    return flags, positional


def skips_hooks(sub, rest):
    """True if the invocation passes --no-verify (or a prefix git accepts) or commit/am `-n`."""
    if sub not in NO_VERIFY:
        return False
    minimum, short_n = NO_VERIFY[sub]
    return any((f.startswith(minimum) and "--no-verify".startswith(f)) or (short_n and f == "-n")
               for f in walk(sub, rest)[0])


def config_sets_hookspath(rest):
    """`git config` that sets or unsets core.hooksPath; plain reads pass."""
    low = [a.lower() for a in rest]
    if not any(a == "core.hookspath" or a.startswith("core.hookspath=") for a in low):
        return False
    if low[:1] in (["get"], ["list"]) or CONFIG_READS & set(low):
        return False
    writes = any(a.startswith(("--unset", "--add", "--replace-all")) for a in low)
    return writes or [a for a in low if not a.startswith("-")] != ["core.hookspath"]  # `git config <key>` reads


def protected_ref(dst):
    """True if a push destination is a protected branch, a glob that matches one, or unknown (HEAD)."""
    name = dst[len("refs/heads/"):] if dst.startswith("refs/heads/") else dst
    if name in {"", "HEAD", "@"} or re.search(r"[$`]", name):  # unknown: current branch or an expansion
        return True
    return any(fnmatch.fnmatchcase(b, name) for b in PROTECTED)


def config_force(cwd, remote):
    """The `remote.<name>.push` or `.mirror` setting that makes a bare `git push` force a protected branch, or None."""
    for line in git_ok(cwd, "config", "--get-regexp", r"^remote\..*\.(push|mirror)$") or []:
        key, _, value = line.partition(" ")
        name, _, kind = key[len("remote."):].rpartition(".")
        if remote and name != remote:
            continue
        if (kind == "mirror" and truthy(value)) or (kind == "push" and forced_protected(value)):
            return f"{key} {value}"
    return None


def push_reason(rest, cwd="."):
    """Block reason for a force push or delete that reaches a protected branch, else None."""
    flags, positional = walk("push", rest)
    names = [f.split("=", 1)[0] for f in flags]
    force = any(n in {"-f", "--force"} or (n.startswith("--force-w") and "--force-with-lease".startswith(n))
                or (n.startswith("--m") and "--mirror".startswith(n)) for n in names)
    delete = any(n == "-d" or (n.startswith("--de") and "--delete".startswith(n)) for n in names)
    refspecs = positional[1:]
    what = "Force-pushing to a protected branch rewrites shared history."
    if force and not refspecs:
        return f"{what} A force push without an explicit refspec may target a protected branch. Name a feature branch."
    if not refspecs:  # git falls back to the configured push refspecs only when none is given
        found = config_force(cwd, positional[0] if positional else None)
        if found:
            return (f"{what} This push has no refspec, so git uses the configured `{found}`, which force-pushes "
                    "to a protected branch. Name a feature branch: `git push origin <branch>`.")
    for spec in refspecs:
        plus = spec.startswith("+")
        src, sep, dst = spec[plus:].partition(":")
        dst = dst if sep else src
        removing = delete or (sep and not src)
        if (force or plus or removing) and protected_ref(dst):
            if removing:
                return f"Deleting the remote branch `{dst}` is blocked; the policy protects it."
            return f"{what} Push to a feature branch and open a PR, or ask the human to run it."
    return None


SCHEME_URL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
SCP_URL = re.compile(r"^(?:[^@/:]+@)?([^@/:]+):(?!//)(.*)$")


def is_url(text):
    return bool(SCHEME_URL.match(text) or SCP_URL.match(text))


def normalise_url(url):
    """`host/path` for an https://, ssh:// or git@host:path URL (no credentials, port or .git), else None."""
    url = url.strip()
    if SCHEME_URL.match(url):
        rest = SCHEME_URL.sub("", url, count=1)
        authority, slash, path = rest.partition("/")
        host = authority.rpartition("@")[2]
        host = re.sub(r":\d*$", "", host)
    else:
        m = SCP_URL.match(url)
        if not m:
            return None  # a local path or a bare name
        host, path = m.group(1), m.group(2)
    path = path.lstrip("/").rstrip("/")
    path = path[:-4] if path.endswith(".git") else path
    return f"{host}/{path}".lower() if host else None


def allowed_url(url):
    norm = normalise_url(url)
    return norm is not None and any(fnmatch.fnmatchcase(norm, pat.lower()) for pat in REMOTES_ALLOWED)


def push_target(rest, positional, cwd):
    """The remote name or URL a `git push` sends to, or None when no remote can be named."""
    for i, a in enumerate(rest):
        if a == "--":
            break
        if a.startswith("--repo="):
            return a.partition("=")[2]
        if a == "--repo" and i + 1 < len(rest):
            return rest[i + 1]
    if positional:
        return positional[0]
    found = git_ok(cwd, "config", "--get", "remote.pushDefault")
    if found:
        return found[0]
    branch = git_ok(cwd, "symbolic-ref", "--short", "-q", "HEAD")
    if branch:
        for kind in ("pushremote", "remote"):
            found = git_ok(cwd, "config", "--get", f"branch.{branch[0]}.{kind}")
            if found:
                return found[0]
    return "origin"


def remote_reason(rest, cwd="."):
    """Block reason when a push goes to a remote outside vcs.remotes_allowed, else None. An empty list turns it off."""
    if not REMOTES_ALLOWED:
        return None
    _, positional = walk("push", rest)
    target = push_target(rest, positional, cwd)
    outside = "push to a remote outside the policy allowlist"
    if re.search(r"[$`]", target) or MARK in target:
        return f"{outside}: the remote comes from a shell expansion, so it cannot be checked."
    if is_url(target):
        urls = [target]
    else:
        urls = git_ok(cwd, "remote", "get-url", "--push", "--all", target)
        if not urls:
            return f"{outside}: remote `{target}` does not resolve to a URL here."
    for url in urls:
        if not allowed_url(url):
            return f"{outside}: `{target}` is not listed in vcs.remotes_allowed. Ask the human to run the push."
    return None


def loose_expansion(sub, rest):
    """True if the shell can build a hook-skip or force flag from the arguments of a guarded call.

    A flag whose name holds an expansion or a brace expansion (`--no-verify$IFS-m`, `--for${E}ce`,
    `reset --$'hard'`) is blocked for the subcommands in GUARDED. For commit, am, push, merge and
    rebase, so is an argument that starts with an unquoted expansion or holds a brace expansion
    (`${E}--no-verify`, `{--no-verify,-m}`) unless it is the value of an option that takes one;
    reset, restore, switch, rm, gc and repack are checked the same way (`git reset $(echo --hard)`).
    The shell splits such an argument into words, so an unquoted `$FLAGS` can carry --no-verify.
    Paths after `--` cannot become options, so they pass.
    """
    if sub not in GUARDED:
        return False
    before = rest[:rest.index("--")] if "--" in rest else rest
    flags, positional = walk(sub, before, EXPANSION_VALUES)
    if any(re.search(r"[$`]", name) or BRACE.search(name) for name in (f.split("=", 1)[0] for f in flags)):
        return True
    return sub in EXPANSION_SUBS and any(a.startswith(MARK) or BRACE.search(a) for a in positional)


def rebase_execs(rest):
    """Shell commands that `git rebase -x/--exec <cmd>` runs after each commit."""
    i = 0
    while i < len(rest):
        a = rest[i]
        i += 1
        if a == "--":
            return
        name, eq, value = a.partition("=")
        if a.startswith("--"):
            if len(name) >= 4 and "--exec".startswith(name):
                if eq:
                    yield value
                elif i < len(rest):
                    yield rest[i]
                    i += 1
            elif name in EXPANSION_VALUES["rebase"][2] and not eq:
                i += 1
        elif a.startswith("-") and len(a) > 1:
            for k, c in enumerate(a[1:], 2):
                if c == "x":
                    if a[k:]:
                        yield a[k:]
                    elif i < len(rest):
                        yield rest[i]
                        i += 1
                    break
                if c in "sXC":  # these take a value, so the rest of the cluster is that value
                    i += k == len(a)
                    break


def env_overrides_hooks(tokens):
    """True if a segment sets GIT_CONFIG_KEY_<n> or GIT_CONFIG_PARAMETERS to core.hooksPath."""
    i = 0
    while i < len(tokens) and (tokens[i] in KEYWORDS or ASSIGNMENT.fullmatch(tokens[i])):
        i += 1
    head = base(tokens[i]) if i < len(tokens) else ""
    scope = tokens if head in WRAPPERS | ASSIGNERS else tokens[:i]  # `env K=V git`, `export K=V`
    for t in scope:
        if base(t) == "git":
            break
        m = re.fullmatch(r"(GIT_CONFIG_KEY_\d+|GIT_CONFIG_PARAMETERS)=(.*)", t, re.S)
        if m and "core.hookspath" in m.group(2).lower():
            return True
    return False


def env_redirects_push(tokens):
    """True if a segment sets a remote/url config through GIT_CONFIG_* and then runs `git push`."""
    if not REMOTES_ALLOWED:
        return False
    i = 0
    while i < len(tokens) and (tokens[i] in KEYWORDS or ASSIGNMENT.fullmatch(tokens[i])):
        i += 1
    head = base(tokens[i]) if i < len(tokens) else ""
    scope = tokens if head in WRAPPERS | ASSIGNERS else tokens[:i]
    hit = False
    for t in scope:
        if base(t) == "git":
            break
        m = re.fullmatch(r"(GIT_CONFIG_KEY_\d+|GIT_CONFIG_PARAMETERS)=(.*)", t, re.S)
        if (m and REDIRECT_KEY.search(m.group(2).lower())) or t.partition("=")[0] in REDIRECT_ENV:
            hit = True
    return hit and "push" in tokens


def dry_run_requested(flags):
    """Respect option order: a negated dry-run option cancels an earlier preview."""
    preview = False
    for flag in flags:
        if flag == "-n" or (flag.startswith("--d") and "--dry-run".startswith(flag)):
            preview = True
        elif flag.startswith("--no-d"):
            preview = False
    return preview


def verdict(args, subagent, cwd=".", blind=False):
    """Return a block reason (or an Ask) for one git invocation, or None to allow.

    `blind` means a `cd` before this call had an unreadable target, so the directory is unknown
    and the linked-worktree exemption does not apply."""
    if not args:
        return None
    sub, rest = args[0], args[1:]

    if sub == HOOKS_OVERRIDE or (sub == "config" and config_sets_hookspath(rest)):
        return Rule("Overriding `core.hooksPath` turns off the repository's git hooks. "
                    "Fix what the hook reports instead.")
    if skips_hooks(sub, rest):
        return Rule(f"`git {sub} --no-verify` (or `-n`) skips the git hooks. Fix what the hook reports instead.")
    if sub == FORCE_CONFIG:
        return Rule("`git -c remote.<name>.push=+...` or `remote.<name>.mirror` makes the push force a protected "
                    "branch. Push a feature branch without that setting.")
    if sub == REDIRECT_CONFIG:
        return Rule("`remote.<name>.url`, `remote.<name>.pushurl`, `url.<base>.insteadOf` or `include.path` set through "
                    "`-c`, `--config-env` or GIT_CONFIG_*, or GIT_CONFIG_GLOBAL/GIT_CONFIG_SYSTEM/GIT_DIR, redirects the "
                    "push to a URL the allowlist check cannot see. "
                    "Push without that setting.")
    if sub == "push":
        reason = push_reason(rest, cwd) or remote_reason(rest, cwd)
        if reason:
            return Rule(reason)
    if loose_expansion(sub, rest):
        return Rule(f"`git {sub}` has an argument that the shell expands unquoted ($X, $(...), backticks, "
                    "$'...' or {a,b}). The shell turns it into words, so it can carry --no-verify, --force or --hard. "
                    "Quote it, write the options out, or put paths after `--`.")

    if sub == "stash":
        if rest[:1] and rest[0] in STASH_READ_ONLY:
            return None
        if subagent:  # refs/stash is shared by every worktree, so a linked worktree does not exempt it
            return "Subagents must not run `git stash`: it moves every agent's uncommitted changes. Use `git diff` snapshots."
        return Ask("`git stash` moves every session's uncommitted changes into refs/stash, which all worktrees "
                   "share. Approve only if no other agent or session is editing this tree.")
    autostash = AUTOSTASH_PREFIX.get(sub)
    if autostash and any(a.startswith(autostash) and "--autostash".startswith(a) for a in rest):
        if subagent:
            return f"Subagents must not run `git {sub} --autostash`: it stashes every agent's uncommitted changes."
        return Ask(f"`git {sub} --autostash` stashes and re-applies every session's uncommitted changes. "
                   "Approve only if no other agent or session is editing this tree.")
    if sub == "reset" and has_flag(rest, "--hard", "--merge", "--keep", sub=sub):
        return "`git reset --hard/--merge/--keep` discards uncommitted working-tree changes."
    if sub == "checkout":
        if ("--" in rest or has_flag(rest, "-f", "--force", "--ours", "--theirs", "-p", "--patch")
                or has_flag(rest, "--pathspec-from-file", sub=sub) or overwrites_paths(rest, cwd)):
            return ("`git checkout <path>` / `checkout <ref> <path>` / `checkout -f` overwrites uncommitted files "
                    "(to change branches, use `git switch <branch>`).")
    if sub == "restore" and not (has_flag(rest, "--staged", "-S") and not has_flag(rest, "--worktree", "-W", sub=sub)):
        return "`git restore` on the working tree discards uncommitted edits."
    if sub == "rm" and has_flag(rest, "-f", "--force", sub=sub) and not has_flag(rest, "--cached"):
        return "`git rm -f` deletes files even when they have uncommitted edits."
    if sub == "clean":
        excludes = {"--exclude"[:n] for n in range(3, len("--exclude") + 1)}
        flags, _ = walk(sub, rest, {"clean": ("e", "", excludes)})
        if has_flag(flags, "-f", "--force", sub=sub) or not dry_run_requested(flags):
            return "`git clean` can delete other agents' untracked files when clean.requireForce is false. Use --dry-run."
    if sub == "reflog" and rest[:1] in (["expire"], ["delete"]) and not dry_run_requested(walk(sub, rest[1:])[0]):
        return "Reflog expiry or deletion removes recovery records shared by all sessions."
    if sub == "prune" and not dry_run_requested(walk(sub, rest)[0]):
        return "`git prune` deletes unreachable objects that recovery needs. Use --dry-run."
    if sub == "repack" and has_flag(rest, "-a") and has_flag(rest, "-d"):
        return "`git repack -a -d` drops unreachable objects that recovery needs. Use -A or skip -d."
    if sub == "gc" and any(
        a.split("=", 1)[0].startswith("--pr")
        and "--prune".startswith(a.split("=", 1)[0])
        and a.partition("=")[2].lower() != "never"
        for a in rest
    ):
        return "Explicit garbage collection pruning can delete unreachable work needed for recovery."
    if sub == "switch" and has_flag(rest, "--discard-changes", "-f", "--force", sub=sub):
        return "`git switch --discard-changes` discards uncommitted work."
    if sub == "worktree" and rest[:1] == ["remove"] and has_flag(rest[1:], "-f", "--force"):
        return "`git worktree remove --force` deletes a worktree with uncommitted work."
    if sub in {"update-ref", "reflog"} and any("stash" in a for a in rest) and (sub == "update-ref" or rest[:1] in (["expire"], ["delete"])):
        return "Deleting or rewriting refs/stash destroys stashed work shared by every worktree."
    if sub == "read-tree" and has_flag(rest, "-u"):
        return "`git read-tree -u` rewrites working-tree files from a tree."
    if sub == "checkout-index" and has_flag(rest, "-f", "--force"):
        return "`git checkout-index -f` overwrites working-tree files from the index."
    if sub == UNVERIFIABLE:
        if rest:
            return Rule(rest[0])
        return "The git subcommand comes from a shell expansion or stdin, so it cannot be checked."

    if not subagent or (not blind and in_linked_worktree(cwd)):
        return None  # a subagent's own linked worktree is its to manage

    if sub in {"checkout", "switch"}:
        return "Subagents must not switch branches in the shared tree; the parent integrates. Use a worktree."
    if sub in {"rebase", "merge", "cherry-pick", "revert", "pull", "am"}:
        return f"Subagents must not run `git {sub}` in the shared tree; hand the change to the parent."
    if sub in {"reset", "restore", "read-tree", "checkout-index", "update-ref", "symbolic-ref"}:
        return "Subagents must not rewrite the shared index or refs; the parent owns staging and integration."
    if sub == "commit":
        return "Subagents commit only in their own worktree; in the shared tree the parent commits once per batch."
    bulk = [a for a in rest if not a.startswith("-") and (a in {".", "./", "..", "*"} or a.startswith(":"))]
    if sub == "add" and (has_flag(rest, "-A", "--all", "-u", "--update") or bulk):
        return "Subagents must stage explicit paths they own, never `git add -A/./-u/*/:/`."
    if sub == "branch" and has_flag(rest, "-D", "-f", "--force", "-M", "-C"):
        return "Subagents must not force-delete, force-move or overwrite branches."
    return None


def mark_expansions(command):
    """Prefix each unquoted `$` and backtick with MARK, so tokens keep whether the shell splits them.

    An escaped or quoted lone `;`, `(`, `)`, `&`, `|`, `<` or `>` (`find ... -exec x \\;`) becomes a word
    character, so it does not end the command."""
    def mark(m):
        text = m.group(0)
        if text in ("$", "`"):
            return MARK + text
        return LITERAL_PUNCT[text[1]] if LONE_PUNCT.fullmatch(text) else text
    return SHELL_QUOTING.sub(mark, command.translate({ord(c): None for c in [MARK, *LITERAL_PUNCT.values()]}))


def substitution_end(text, i):
    """Index of the `)` or backtick that closes the substitution starting at text[i], or len(text)."""
    if text[i] == "`":
        j = i + 1
        while j < len(text) and text[j] != "`":
            j += 2 if text[j] == "\\" else 1
        return min(j, len(text))
    depth, j, quote = 0, i + 1, None
    while j < len(text):
        c = text[j]
        if c == "\\" and quote != "'":
            j += 2
            continue
        if quote:
            quote = None if c == quote else quote
        elif c in "'\"":
            quote = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return len(text)


def shell_text(command):
    """Read text as the shell does before splitting words: join backslash-newline
    continuations, drop `#` comments, and collect the `$(...)` and backtick bodies inside
    double quotes, which the shell runs. Returns (text, substitution bodies)."""
    out, bodies, i, quote, word_start = [], [], 0, None, True
    while i < len(command):
        c, nxt = command[i], command[i + 1:i + 2]
        if quote == "'":
            out.append(c)
            quote = None if c == "'" else quote
            i += 1
            continue
        if c == "\\":
            if nxt != "\n":  # a continuation joins lines; any other escape is kept
                out.append(command[i:i + 2])
                word_start = False
            i += 2
            continue
        if quote == '"' and (c == "`" or (c == "$" and nxt == "(")):
            end = substitution_end(command, i)
            bodies.append(command[i + (1 if c == "`" else 2):end])
            out.append(command[i:end + 1])
            i = end + 1
            continue
        if quote is None and c == "#" and word_start:
            while i < len(command) and command[i] != "\n":
                i += 1
            continue
        if c in "'\"" and quote in (None, c):
            quote = None if quote else c
        out.append(c)
        word_start = quote is None and (c.isspace() or c in ";&|()<>")
        i += 1
    return "".join(out), bodies


def tokenize(command):
    """Quote-aware tokens with shell operators as separate tokens."""
    command = mark_expansions(command)
    try:
        lex = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        lex.commenters = ""  # shell_text() already dropped comments line by line
        return list(lex)
    except ValueError:  # unbalanced quotes: fall back to a plain operator split
        return [t for part in SHELL_SPLIT.split(command) for t in (part.split() + [";"])]


def feeds_shell(line):
    """True if a heredoc on this line is read by a shell as code (`bash <<EOF`, `cat <<EOF | sh`)."""
    for part in re.split(r"[|;&]", line):
        words = [w for w in part.split() if not ASSIGNMENT.fullmatch(w)]
        if words and base(words[0]) in SHELLS and not any(SHELL_C.fullmatch(w) for w in words[1:]):
            return True
    return False


def feeds_interpreter(line):
    """The interpreter whose script is a heredoc on this line (`python3 - <<EOF`, `cat <<EOF | node`)."""
    for part in re.split(r"[|;&]", line):
        words, skip = [], False
        for w in part.split():
            if skip or re.match(r"\d*[<>]", w):  # drop redirections and a detached target
                skip = not skip and bool(re.fullmatch(r"\d*(?:<<-?|<<<|<|>>?|>&|<&)", w))
                continue
            words.append(w)
        k = launcher_at(words, is_interpreter)
        if k is not None and interpreter_code(words, k) == ([], True):
            return base(words[k])
    return None


def strip_heredocs(command):
    """Drop heredoc bodies (data, not commands), keeping `$(...)` from unquoted ones
    and the whole body when a shell reads it. Returns (text, interpreter script bodies)."""
    lines, out, bodies, i = command.split("\n"), [], [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        for m in HEREDOC.finditer(line):
            quoted, tag = m.group(1), m.group(2)
            code = feeds_shell(line)
            script = not code and feeds_interpreter(line)
            body = []
            while i < len(lines) and lines[i].lstrip("\t") != tag:
                if code:
                    out.append(lines[i])
                else:
                    if script:
                        body.append(lines[i])
                    if not quoted:  # unquoted bodies still run command substitutions
                        out.extend(a or b for a, b in re.findall(r"\$\(([^()]*)\)|`([^`]*)`", lines[i]))
                i += 1
            i += 1  # the delimiter line
            if script:
                bodies.append((script, "\n".join(body)))
    return "\n".join(out), bodies


def launcher_at(tokens, match):
    """Index of the command `match` accepts in `X=1 cmd`, `timeout 5 env cmd`, or None."""
    i = 0
    while i < len(tokens) and (tokens[i] in KEYWORDS or ASSIGNMENT.fullmatch(tokens[i])):
        i += 1
    if i >= len(tokens) or not (match(base(tokens[i])) or base(tokens[i]) in WRAPPERS):
        return None
    for k in range(i, len(tokens)):
        name = base(tokens[k])
        if name == "git":
            return None
        if match(name):
            return k
    return None


def shell_at(tokens):
    """Index of the shell in `bash -c`, `X=1 sh -c`, `timeout 5 env bash -c`, or None."""
    return launcher_at(tokens, SHELLS.__contains__)


def is_interpreter(name):
    return bool(INTERPRETER.fullmatch(name))


def shell_reads_stdin(args):
    """True if a shell given these arguments (and no -c) reads its script from stdin."""
    j = 0
    while j < len(args):
        t = args[j]
        if t in {"-o", "+o", "-O", "+O", "--rcfile", "--init-file"}:
            j += 2
            continue
        if re.fullmatch(r"[-+][A-Za-z]*s[A-Za-z]*", t):
            return True
        if not t.startswith(("-", "+")):
            return False  # a script file on disk
        j += 1
    return True


def interpreter_code(tokens, k):
    """(inline code strings, reads its script from stdin) for the interpreter at tokens[k]."""
    name, codes, j = base(tokens[k]), [], k + 1
    family = "py" if name.startswith(("python", "pypy")) else "node" if name.startswith("node") else "pe"
    while j < len(tokens):
        t = tokens[j]
        j += 1
        if family == "py":
            if re.fullmatch(r"-[A-Za-z]*c", t):
                return tokens[j:j + 1], False
            if t in {"-W", "-X"}:
                j += 1
            elif t == "-":
                return [], True
            elif not t.startswith("-") or re.fullmatch(r"-[A-Za-z]*m", t):
                return [], False  # a script file or -m module
        elif family == "node":
            if t in {"-e", "--eval", "-p", "--print", "-pe"}:
                return tokens[j:j + 1], False
            if t.startswith(("--eval=", "--print=")):
                return [t.split("=", 1)[1]], False
            if t in {"-r", "--require", "--import", "--loader"}:
                j += 1
            elif t == "-":
                return [], True
            elif not t.startswith("-"):
                return [], False
        else:  # perl and ruby take several -e
            m = re.fullmatch(r"-[A-Za-z]*?[eE](.*)", t, re.S)
            if m and t != "--":
                if m.group(1):
                    codes.append(m.group(1))
                else:
                    codes.extend(tokens[j:j + 1])
                    j += 1
            elif t == "--" or not t.startswith("-"):
                return codes, False
    return codes, not codes


def unescape(text):
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t", "r": "\n"}.get(m.group(1), m.group(1)), text)


def printf_text(fmt, args):
    """What `printf FMT ARGS` prints, close enough to parse: directives take arguments in order."""
    args, out = list(args), []
    for _ in range(50):
        out.append(re.sub(r"%%|%[-+ #0-9.]*[A-Za-z]",
                          lambda m: "%" if m.group(0) == "%%" else (args.pop(0) if args else ""), fmt))
        if not args or not re.search(r"%[-+ #0-9.]*[A-Za-z]", fmt):
            break
    return unescape("".join(out))


def literal_output(tokens, here, heredoc):
    """Texts a pipeline producer writes when they are visible in the command, or None if unknown."""
    i = 0
    while i < len(tokens) and (tokens[i] in KEYWORDS or ASSIGNMENT.fullmatch(tokens[i])):
        i += 1
    if i >= len(tokens):
        return None
    head, args = base(tokens[i]), tokens[i + 1:]
    if head == "echo":
        while args and re.fullmatch(r"-[neE]+", args[0]):
            args = args[1:]
        return [" ".join(args), unescape(" ".join(args))]
    if head == "printf":
        args = args[1:] if args[:1] == ["--"] else args
        if not args or args[0].startswith("-v"):
            return [] if args else None
        return [printf_text(args[0], args[1:]), unescape(" ".join(args))]
    if head == "cat" and all(a.startswith("-") for a in args) and (here or heredoc):
        return here  # a heredoc body that a later shell reads is already part of the command text
    return None


def opaque(reason):
    """A synthetic git call that verdict() blocks with `reason`."""
    return ["git", UNVERIFIABLE, reason]


def piped_code(parse, here, heredoc, producer, pipeline, text):
    """Segments of the script a shell or interpreter reads on stdin."""
    if here:
        for h in here:
            yield from parse(h)
        return
    if heredoc or producer is None:
        return  # heredoc bodies were handled by strip_heredocs; `< file` is a script on disk
    tokens, p_here, p_heredoc, op = producer
    lit = literal_output(tokens, p_here, p_heredoc) if op in ("|", "|&") else None
    if lit is not None:
        for t in lit:
            yield from parse(t)
        return
    group = op not in ("|", "|&") or tokens[:1] and tokens[0] in GROUP_END
    scope = text if group else " ".join(pipeline)
    if GIT_WORD.search(scope.replace(MARK, "")):
        yield opaque("Text piped into a shell or interpreter comes from a command whose output the guard cannot "
                     "see, and the command mentions git. Run the git commands directly.")


def code_candidates(code):
    """Shell texts that string literals in interpreter code can run.

    Literals separated by commas form one argv list (`["git", "-C", d, "stash"]`,
    `spawn("git", ["stash"])`). Any other expression in the list becomes a quoted
    `"$X"`, including literals nested in a call (`os.path.join(d, "x")`). A list
    ends at a bracket it did not open, `;`, `=` or `:`, or two literals with no
    comma between them. A list of one literal is a shell string. Interpolation
    (`{x}`, `#{x}`, `%s`) becomes `$X`.
    """
    runs, run, stack, pending = [], [], [], False
    matches = list(LITERAL.finditer(code))
    for n in range(len(matches) + 1):
        start = matches[n - 1].end() if n else 0
        gap = code[start:matches[n].start() if n < len(matches) else len(code)]
        broke, comma, prev = not run, False, '"'
        for ch in gap if run else "":
            if ch in "([{":
                stack.append(prev.isalnum() or prev in "_)]")  # True: a call or subscript, not a list
            elif ch in ")]}":
                if not stack:
                    broke = True
                    break
                stack.pop()
            elif ch == ";" or (ch in "=:" and not any(stack)):
                broke = True
                break
            elif ch == "," and not any(stack):
                if pending:
                    run.append(None)
                pending, comma = False, True
            elif not ch.isspace() and not any(stack):
                pending = True
            if not ch.isspace():
                prev = ch
        broke = broke or not (comma or pending or any(stack))
        if (broke or n == len(matches)) and run:
            runs.append(run + [None] * (pending and comma))  # `["git", "add", path]`
            run, stack, pending = [], [], False
        if n == len(matches):
            break
        if run and (pending or any(stack)):
            pending = True  # a literal inside a larger expression: that expression is one argument
            continue
        m = matches[n]
        run.append(unescape(INTERPOLATION.sub("$X", next((g for g in m.groups() if g is not None), ""))))
    for r in runs:
        if len(r) == 1:
            yield r[0]
            continue
        yield " ".join('"$X"' if v is None else shlex.quote(v) for v in r)
        for v in r:
            if v is not None and re.search(r"\s", v.strip()):
                yield v


def code_segments(code, name="python3"):
    """Segments for interpreter code: its string literals, or a fail-closed call if it shells out opaquely."""
    code = code.replace(MARK, "")
    if not GIT_WORD.search(code):
        return
    out, complete, partial = [], False, False
    for text in code_candidates(code):
        if not GIT_WORD.search(text):
            continue
        for tokens in segments(text):
            out.append(tokens)
            found = git_args(tokens)
            if found:
                complete = complete or bool(found[0])
                partial = partial or not found[0]
    yield from out
    shells_out = SHELLS_OUT.search(LITERAL.sub(" ", code)) or (name.startswith(("perl", "ruby")) and "`" in code)
    if shells_out and (partial or not complete):
        yield opaque("Interpreter code runs a command and mentions git, but no string literal in it is a "
                     "complete git command, so it cannot be checked. Write the git call as one literal "
                     "command or argv list, or run it directly.")


def launched_argv(current):
    """Unwrap execution actions, without treating command mentions as commands."""
    k = launcher_at(current, {"find", "fd", "fdfind", "env"}.__contains__)
    if k is None:
        return
    name, args = base(current[k]), current[k + 1:]
    if name == "env":
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--":
                return
            if arg in {"-u", "--unset", "-C", "--chdir"}:
                i += 2
                continue
            if not arg.startswith("-") and not ASSIGNMENT.fullmatch(arg):
                yield args[i:]
                return
            value, end = None, i + 1
            if arg in {"-S", "--split-string"}:
                if end >= len(args):
                    return
                value, end = args[end], end + 1
            elif arg.startswith("--split-string="):
                value = arg.split("=", 1)[1]
            elif re.fullmatch(r"-[A-Za-z].*", arg, re.S):  # a short cluster: `-iS cmd`, `-vSgit\\ x`, `-iu NAME`
                for k, c in enumerate(arg[1:], 2):
                    if c == "S":
                        if arg[k:]:
                            value = arg[k:]
                        elif end < len(args):
                            value, end = args[end], end + 1
                        else:
                            return
                        break
                    if c in "uCP":  # these take a value: the rest of the cluster, or the next argument
                        end += not arg[k:]
                        break
            if value is None:
                i = end
                continue
            # env -S has expansion and escape rules that differ from shell syntax.
            if re.search(r"[$\\]", value):
                if mentions_git(value):
                    yield opaque("The env split string uses expansion or escapes, so it cannot be checked.")
                return
            try:
                yield shlex.split(value) + args[end:]
            except ValueError:
                if mentions_git(value):
                    yield opaque("The env split string has invalid quotes, so it cannot be checked.")
            return
        return
    actions = {"-exec", "-execdir", "-ok", "-okdir"} if name == "find" else {
        "-x", "-X", "--exec", "--exec-batch"
    }
    # Predicate values can look like actions but remain data.
    values = {"-name", "-iname", "-path", "-ipath", "-regex", "-iregex", "-type",
              "-user", "-group", "-size", "-mtime", "-atime", "-ctime", "-newer",
              "-maxdepth", "-mindepth", "-printf", "-fprint", "-lname", "-ilname",
              "-perm", "-inum", "-links"}
    i = 0
    while i < len(args):
        arg = args[i]
        if name != "find" and arg == "--":
            return
        if name == "find" and arg in values:
            i += 2
            continue
        attached = None if name == "find" else re.fullmatch(r"(?:--exec(?:-batch)?=|-[xX](?=.))(.*)", arg, re.S)
        if arg in actions or attached or (name != "find" and re.fullmatch(r"-[HIiasLguFp0]+[xX]", arg)):
            end = i + 1
            if name == "find":
                while end < len(args) and args[end] not in {";", "+"}:
                    end += 1
            else:
                end = len(args)
            yield ([attached.group(1)] if attached else []) + args[i + 1:end]
            i = end + 1
        else:
            i += 1


def dynamic_code(code):
    """Fail closed on shell code that is wholly a quoted substitution mentioning git (`bash -c "$(echo git ...)"`)."""
    if re.match(r"\s*(?:\$\(|`)", code) and GIT_WORD.search(code):
        yield opaque("Shell code comes from a command substitution that mentions git, so the guard cannot see "
                     "it. Write the git command out.")


def download_substitution(code):
    """A shell's code starts with a fetcher's substitution, including known wrappers."""
    code = code.lstrip().removeprefix(MARK)
    if not code.startswith(("$(", "`")):
        return False
    start = 2 if code.startswith("$(") else 1
    body = code[start:substitution_end(code, 0)]
    return launcher_at(tokenize(body), FETCHERS.__contains__) is not None


def simple_command(current, here, heredoc, producer, pipeline, text):
    """Segments for one simple command, unwrapping shells and interpreters."""
    if current[:1] == ["function"]:
        current = current[2:]  # `function f { git ...`: the body runs when f is called
    for argv in launched_argv(current):
        yield from simple_command(argv, [], False, None, argv, text)
    shell = shell_at(current)
    if shell is not None:
        args = current[shell + 1:]
        for j, t in enumerate(args):
            if SHELL_C.fullmatch(t):
                j += args[j + 1:j + 2] == ["--"]  # `bash -c -- 'cmd'`
                if j + 1 < len(args):
                    if download_substitution(args[j + 1]):
                        yield [DOWNLOAD_SHELL]
                    yield from dynamic_code(args[j + 1])
                    yield from segments(args[j + 1])
                return
        if shell_reads_stdin(args):
            if producer and producer[3] in ("|", "|&") and launcher_at(producer[0], FETCHERS.__contains__) is not None:
                yield [DOWNLOAD_SHELL]
            yield from piped_code(segments, here, heredoc, producer, pipeline, text)
        return
    if current and current[0] == "eval":
        yield from dynamic_code(" ".join(current[1:]))
        yield from segments(" ".join(current[1:]))
        return
    if not current:
        return
    k = launcher_at(current, is_interpreter)
    if k is not None:
        codes, stdin = interpreter_code(current, k)
        name = base(current[k])
        for code in codes:
            yield from code_segments(code, name)
        if stdin:
            yield from piped_code(lambda t: code_segments(t, name), here, heredoc, producer, pipeline, text)
    yield current


def segments(command):
    """Yield token lists for each simple command, unwrapping `bash -c '...'`, interpreter
    code, and text that a shell or interpreter reads from a here-string or a pipe."""
    text, bodies = strip_heredocs(command or "")
    for name, body in bodies:
        yield from code_segments(body, name)
    text, substitutions = shell_text(text)
    for body in substitutions:
        yield from segments(body)
    current, skip, here, heredoc = [], False, [], False
    producer, pipeline, fetch_input = None, [], False
    for tok in tokenize(text) + [";"]:
        if skip:
            if skip == "<<<":
                here.append(tok)
            skip = False
            continue
        if REDIRECT.fullmatch(tok):
            if current and current[-1].isdigit():
                current.pop()  # the fd in `2>/dev/null`
            skip = "<<<" if tok.startswith("<<<") else True  # the redirect target
            heredoc = heredoc or (tok.startswith("<<") and not tok.startswith("<<<"))
            continue
        if not OPERATOR.fullmatch(tok):
            current.append(tok.translate(UNLITERAL))
            continue
        if fetch_input and launcher_at(current, FETCHERS.__contains__) is not None:
            yield [DOWNLOAD_SHELL]  # classify the whole launcher, including env/absolute paths
        fetch_input = tok == "<(" and shell_at(current) is not None
        if tok == "<(" and GIT_WORD.search(text.replace(MARK, "")) and (
                shell_at(current) is not None or current[:1] in (["source"], ["."])):
            yield opaque("A shell reads text from a process substitution whose output the guard cannot see, "
                         "and the command mentions git. Run the git commands directly.")
        yield from simple_command(current, here, heredoc, producer, pipeline + current, text)
        piped = "|" in tok and "||" not in tok
        producer = (current, here, heredoc, tok) if piped else None
        pipeline = pipeline + current if piped else []
        current, here, heredoc = [], [], False


def root_wipe_target(target):
    """Recognize root/home spellings without treating cwd globs as root.

    Only collapse dot-only components. Resolving a named directory followed by `..`
    lexically would misread symlink traversal, which this parser does not resolve.
    """
    if target.endswith("/*"):
        target = target[:-1]
    if target.startswith("/"):
        return all(part in ("", ".", "..") for part in target.split("/"))
    for home in ("~", "$HOME", "${HOME}"):
        if target == home or target.startswith(home + "/"):
            return all(part in ("", ".") for part in target[len(home):].split("/"))
    return False


def git_dir_target(target):
    """True if an rm target is a `.git` directory (`.git`, `./.git/`, `$PWD/.git`, `.git/*`) or a glob that matches it.

    Only the last path component counts, so `.git/index.lock` and `.gitignore` pass."""
    if target.endswith("/*"):
        target = target[:-1]
    name = os.path.basename(os.path.normpath(target)).lower()
    if name == ".git":
        return True
    return name.startswith(".") and bool(re.search(r"[*?\[]", name)) and fnmatch.fnmatchcase(".git", name)


# gh pr merge options that take a value. Skipping each with its value finds `pr merge` in any order gh accepts
# (`gh -R o/r pr merge`, `gh pr -R o/r merge`).
GH_MERGE_VALUES = {"-b", "--body", "-F", "--body-file", "-t", "--subject", "-A", "--author-email", "--match-head-commit", "-R", "--repo"}


def gh_positionals(args):
    """gh's positional words: every option is skipped, and an option in GH_MERGE_VALUES with its value."""
    out, i = [], 0
    while i < len(args):
        if args[i] in GH_MERGE_VALUES:
            i += 2
            continue
        if not args[i].startswith("-"):
            out.append(args[i])
        i += 1
    return out


# gh's own top-level commands. gh refuses an alias that shadows one, so only another first word needs `gh alias list`.
GH_COMMANDS = {"agent-task", "alias", "api", "attestation", "auth", "browse", "cache", "codespace", "completion", "config",
               "copilot", "discussion", "extension", "gist", "gpg-key", "help", "issue", "label", "licenses", "org", "pr",
               "preview", "project", "release", "repo", "ruleset", "run", "search", "secret", "skill", "ssh-key", "status",
               "variable", "workflow"}
EXPANSION = re.compile(r"[$`]")


def gh_aliases(cwd):
    """`gh alias list` as {name: expansion}, or None when gh cannot tell within 10 seconds."""
    try:
        out = subprocess.run(["gh", "alias", "list"], cwd=cwd, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return {} if "no aliases" in out.stderr else None
    return dict(line.split(": ", 1) for line in out.stdout.splitlines() if ": " in line)


def merge_base(selector, repo, cwd):
    """The base branch of PR `selector` in `repo`, or None when gh cannot tell within 10 seconds."""
    try:
        out = subprocess.run(["gh", "pr", "view", selector, "--repo", repo, "--json", "baseRefName", "-q", ".baseRefName"],
                             cwd=cwd, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else None


def floor_rule(tokens, cwd=".", alone=True, alias=False):
    """The non-git floor: the rule a simple command breaks, or None. Applies to every caller, not only subagents.

    `alone` is False when the command line runs gh more than once; `alias` is True for an expanded gh alias."""
    if tokens == [DOWNLOAD_SHELL]:
        return "a shell runs a script that curl or wget downloads"
    k = launcher_at(tokens, lambda n: n in FLOOR_COMMANDS or n.startswith("mkfs"))
    if k is None:
        return None
    name, args = base(tokens[k]), [a.replace(MARK, "") for a in tokens[k + 1:]]
    if name.startswith("mkfs"):
        return "mkfs formats a filesystem"
    if name == "dd":
        return "dd writes to a device" if any(
            a.startswith("of=/dev/") and a not in ("of=/dev/null", "of=/dev/stdout", "of=/dev/stderr") for a in args) else None
    if name == "gh":
        words = [a for a in args if not a.startswith("-")]
        methods = [args[i + 1] if a in ("-X", "--method") and i + 1 < len(args) else a.split("=")[-1] if a.startswith("--method=")
                   else a[2:] for i, a in enumerate(args) if a in ("-X", "--method") or a.startswith(("--method=", "-X"))]
        # The shell fills in `$X` and `` `...` `` after the hook ran, so a gh command word built that way is unknown.
        # An alias expands to a different command, so the guard reads its expansion; gh runs a `!` alias in a shell.
        head = gh_positionals(args)[:2]
        if any(EXPANSION.search(w) for w in head):
            return "a gh command word comes from a shell expansion, so it cannot be checked"
        if head and head[0] not in GH_COMMANDS:
            aliases = None if alias else gh_aliases(cwd)
            expansion = (aliases or {}).get(head[0])
            if expansion and not expansion.startswith("!"):
                rest, extra = args[:], []
                rest.remove(head[0])
                for i, a in enumerate(rest, 1):  # gh fills $1, $2 ... and appends the arguments it did not use
                    if f"${i}" in expansion:
                        expansion = expansion.replace(f"${i}", a)
                    else:
                        extra.append(a)
                return floor_rule(["gh", *shlex.split(expansion), *extra], cwd, alone, alias=True)
            if aliases is None or expansion:
                return "a gh alias that the guard could not resolve"
        # A merge or an API call is checked by its text, and `$A` could hold `--admin`, `-X "$M"` a PUT.
        if (head == ["pr", "merge"] or words[:1] == ["api"]) and any(EXPANSION.search(a) for a in args):
            return "a gh pr merge or gh api call takes text from a shell expansion, so it cannot be checked"
        if words[:2] == ["repo", "delete"]:
            return "gh repo delete removes a repository"
        # An agent merge must pin the commit adversarial-review returned as head_sha, so GitHub refuses it if the
        # PR head moved after the review, and must target dev. The base is not in the command and a private repo on
        # the free plan has no branch protection, so the guard asks gh for it and blocks when gh cannot say. An
        # explicit -R makes the lookup read the merged repository whatever the cwd, a `cd` or GH_REPO says.
        merge = gh_positionals(args)
        if merge[:2] == ["pr", "merge"]:
            if not alone:  # another gh call on the line (`gh pr edit --base main && ...`) could move the base after the check
                return "gh pr merge shares its command line with another gh call"
            if any(a == "--admin" or a.startswith("--admin=") for a in args):
                return "gh pr merge --admin bypasses branch protection"
            pins = [args[i + 1] if a == "--match-head-commit" and i + 1 < len(args) else a.partition("=")[2]
                    for i, a in enumerate(args) if a == "--match-head-commit" or a.startswith("--match-head-commit=")]
            if not any(re.fullmatch(r"[0-9a-f]{40}", pin) for pin in pins):
                return "gh pr merge without --match-head-commit <the 40-character head_sha from adversarial-review>"
            repos = {args[i + 1] if a in ("-R", "--repo") and i + 1 < len(args) else a.split("=", 1)[1] if "=" in a else a[2:]
                     for i, a in enumerate(args) if a in ("-R", "--repo") or a.startswith(("--repo=", "-R"))}
            if len(repos) != 1 or len(merge) < 3 or not all(repos):
                return "gh pr merge without one -R <owner/repo> and the PR number"
            if merge_base(merge[2], repos.pop(), cwd) != MERGE_BASE:
                return "gh pr merge into a base other than the policy's merge base, or a base gh could not read"
        upper = set(map(str.upper, methods))
        if words[:1] == ["api"] and ("PUT" in upper and any(re.search(r"pulls/[^/?#]+/merge/?(?:[?#].*)?$", w) for w in words)
                                     or any("mergePullRequest" in a for a in args)):
            return "gh api merges a pull request without the reviewed-commit pin"
        return "gh api with the DELETE method" if words[:1] == ["api"] and "DELETE" in upper else None
    ddash = args.index("--") if "--" in args else len(args)
    recursive = any(a in ("-r", "-R") or re.fullmatch(r"-[A-Za-z]*[rR][A-Za-z]*", a) or (len(a) > 2 and "--recursive".startswith(a))
                    for a in args[:ddash])
    targets = [a for a in args[:ddash] if not a.startswith("-")] + args[ddash + 1:]
    if recursive and any(git_dir_target(t) for t in targets):
        return "recursive rm of a .git directory"
    wipes = any(root_wipe_target(t) for t in targets)
    return "recursive rm of / or the home directory" if recursive and wipes else None


def mentions_git(raw):
    """True if raw hook input contains `git` as a word (JSON escapes such as \\n count as spaces)."""
    return bool(GIT_WORD.search(re.sub(r"\\[ntr\"]", " ", raw or "")))


def watched(raw):
    """True if raw hook input mentions git or a floor command, so a guard failure must block it."""
    return mentions_git(raw) or bool(FLOOR_WORD.search(re.sub(r"\\[ntr\"]", " ", raw or "")))


def unreadable(raw, why):
    """Block input the guard cannot read if it mentions git; allow it otherwise."""
    if not watched(raw):
        return 0
    log_block("input:unreadable")
    print(f"BLOCKED by git-safety-guard: {why}, and the input mentions git, so it cannot be checked.",
          file=sys.stderr)
    return 2


VAR_WORD = re.compile(MARK + r"?\$(?:(\w+)|\{(\w+)\})")  # `$g` or `${g}`; a quoted "$g" has no MARK


def track_assignments(tokens, assigned):
    """Record `NAME=value` from a bare assignment segment or `export`/`declare`. A prefix assignment
    (`g=git cmd`) only reaches cmd's environment, not the words of cmd, so it is not recorded."""
    i = 0
    while i < len(tokens) and (tokens[i] in KEYWORDS or ASSIGNMENT.fullmatch(tokens[i])):
        i += 1
    if i < len(tokens) and base(tokens[i]) in ASSIGNERS:
        names = [t for t in tokens[i + 1:] if ASSIGNMENT.fullmatch(t)]
    elif i == len(tokens):
        names = [t for t in tokens if ASSIGNMENT.fullmatch(t)]
    else:  # `g=\`which git\`; ...` tokenizes as a prefix assignment, but the backticks run first
        names = [t for t in tokens[:i] if ASSIGNMENT.fullmatch(t) and t.partition("=")[2].startswith(MARK + "`")]
    for t in names:
        name, _, value = t.partition("=")
        assigned[name] = value


def git_var_words(token, assigned, mentions):
    """Words a `$g`/`${g}` command word expands to when the command line assigned it git, else None.

    An assignment that is not plainly git comes back as an opaque call when its text mentions git, or when
    it is a substitution (`g=$(command -v git)`) and `mentions` says the command line mentions git."""
    m = VAR_WORD.fullmatch(token)
    value = assigned.get(m.group(1) or m.group(2)) if m else None
    if value is None:
        return None
    try:
        words = shlex.split(value)
    except ValueError:
        words = []
    if words and base(words[0]) == "git" and MARK not in value:
        return words
    if GIT_WORD.search(value.replace(MARK, "")) or (MARK in value and mentions):
        return opaque("A command word is a variable assigned from text that mentions git, so the git command "
                      "cannot be checked. Write `git` out.")
    return None


def resolve_git_vars(tokens, assigned, mentions):
    """Replace a command word that is a variable assigned git (`g=git; $g reset --hard`).

    Behind a wrapper (`env $g`, `xargs $g`) any later word counts, as for a literal git."""
    if not assigned:
        return tokens
    i = 0
    while i < len(tokens) and (tokens[i] in KEYWORDS or ASSIGNMENT.fullmatch(tokens[i])):
        i += 1
    wrapped = i < len(tokens) and base(tokens[i]) in WRAPPERS
    out = tokens[:i]
    for k in range(i, len(tokens)):
        out += (git_var_words(tokens[k], assigned, mentions) if k == i or wrapped else None) or [tokens[k]]
    return out


FLOOR_VAR = re.compile(r"\b(?:gh|rm|dd)\b")


def resolve_floor_vars(parts, mentions):
    """The segments with a command word that is a variable assigned gh, rm or dd read as that command
    (`G=gh; $G pr merge`), as resolve_git_vars does for git. None when one is assigned from other text
    that names them, or from a substitution (`G=$(command -v gh)`) on a line that `mentions` them."""
    assigned, out = {}, []
    for tokens in parts:
        i = 0
        while i < len(tokens) and (tokens[i] in KEYWORDS or ASSIGNMENT.fullmatch(tokens[i])):
            i += 1
        wrapped = i < len(tokens) and base(tokens[i]) in WRAPPERS
        new = tokens[:i]
        for k in range(i, len(tokens)):
            m = VAR_WORD.fullmatch(tokens[k]) if k == i or wrapped else None
            value = assigned.get(m.group(1) or m.group(2)) if m else None
            if value is None or not (FLOOR_VAR.search(value.replace(MARK, "")) or (MARK in value and mentions)):
                new.append(tokens[k])
                continue
            try:
                words = [] if MARK in value else shlex.split(value)
            except ValueError:
                words = []
            if not words or base(words[0]) not in FLOOR_COMMANDS:
                return None
            new += words
        track_assignments(new, assigned)
        out.append(new)
    return out


def calls(command, cwd, depth=0):
    """Yield (git argv, repo dir) for every git call a command can run.

    The argv is None for a segment that sets core.hooksPath through GIT_CONFIG_* variables.
    `git rebase -x <cmd>` bodies are commands too, so they are parsed in the same repo.
    """
    # A `cd` inside a subshell, `$(...)` or before `popd` does not move later commands, but the
    # guard cannot tell, so a `cd` may only take the worktree exemption away, never grant it.
    blind, start, defined, assigned = False, cwd, {}, {}
    mentions = bool(GIT_WORD.search(command.replace(MARK, "")))
    for tokens in segments(command):
        tokens = resolve_git_vars(tokens, assigned, mentions)
        track_assignments(tokens, assigned)
        if env_overrides_hooks(tokens):
            yield None, cwd, blind
            return
        if env_redirects_push(tokens):
            yield [REDIRECT_CONFIG], cwd, blind
            return
        k = launcher_at(tokens, {"cd", "pushd", "popd"}.__contains__)
        if k is not None:
            target = next((t for t in tokens[k + 1:] if not t.startswith("-") or t == "-"), "~")
            if base(tokens[k]) == "popd" or MARK in target or target == "-":
                blind = True  # `popd`, `cd "$D"` or `cd -`: the directory is unknown from here on
            else:
                cwd = os.path.join(cwd, os.path.expanduser(target))
                blind = blind or not in_linked_worktree(start)
            continue
        found = git_args(tokens)
        if found is None:
            continue
        here = os.path.join(cwd, found[2])  # honour `git -C <dir>`
        if found[0][:1] == ["config"]:  # `git config alias.x '...' && git x` runs the alias this command defines
            for n, a in enumerate(found[0][:-1]):
                if a.lower().startswith("alias."):
                    defined[a[6:].lower()] = found[0][n + 1]
        for args in expand(found[0], {**defined, **found[1]}, here):
            yield args, here, blind
            if args[:1] != ["rebase"] or depth > 3:
                continue
            for body in rebase_execs(args[1:]):
                if re.match(r"\s*" + MARK + r"?[$`]", body):
                    yield [UNVERIFIABLE, "The `git rebase --exec` command comes from a shell expansion, so it "
                                         "cannot be checked. Write the command out."], here, blind
                else:
                    yield from calls(body, here, depth + 1)


def check(raw):
    """Exit code for one PreToolUse payload."""
    try:
        event = json.loads(raw)
    except ValueError:
        event = None
    if not isinstance(event, dict):
        return unreadable(raw, "the hook input is not a JSON object")
    tool_name = event.get("tool_name")
    process = PROCESS_TOOLS.fullmatch(tool_name or "")
    if tool_name is not None and tool_name not in SHELL_TOOLS and not process:
        return 0
    tool_input = event.get("tool_input")
    if process and process.group(1) == "interact_with_process":  # input to a REPL, not shell text
        text = tool_input.get("input") if isinstance(tool_input, dict) else None
        return unreadable(text if isinstance(text, str) else raw, "input sent to a running process cannot be checked")
    command = (tool_input.get("command") or tool_input.get("cmd")) if isinstance(tool_input, dict) else None
    if isinstance(command, list) and command:  # Codex argv form
        command = shlex.join(str(c) for c in command)
    if not isinstance(command, str) or not command.strip():
        return unreadable(raw, "the shell payload has no command")
    if POLICY_ERROR and watched(raw):
        log_block("policy:unreadable", event)
        print(f"git-safety-guard: policy unreadable ({POLICY_ERROR}): git blocked", file=sys.stderr)
        return 2
    subagent = bool(event.get("agent_id")) or os.environ.get("GIT_SAFETY_STRICT") == "1"
    who = "subagent" if subagent else "parent"
    parts = resolve_floor_vars(list(segments(command)), bool(FLOOR_VAR.search(command.replace(MARK, ""))))
    if parts is None:
        log_block("floor:var", event, who)
        print("BLOCKED by git-safety-guard: A command word is a variable assigned from text that names gh, rm or dd, "
              "so the command cannot be checked. Write the command out, or ask the user to run it at the `!` prompt.",
              file=sys.stderr)
        return 2
    alone =sum(launcher_at(t, lambda n: n == "gh") is not None for t in parts) <= 1
    for tokens in parts:
        rule = floor_rule(tokens, event.get("cwd") or os.getcwd(), alone)
        if rule:
            log_block(FLOOR_RULES.get(rule, "floor:other"), event, who)
            print(f"BLOCKED by git-safety-guard: {rule}. "
                  "If you intend it, ask the user to run it themselves at the `!` prompt.", file=sys.stderr)
            return 2
    cwd = event.get("cwd") or os.getcwd()
    asks = []
    for args, here, blind in calls(command, cwd):
        if args is None:
            log_block("git:hooks-env", event, who)
            print("BLOCKED by git-safety-guard: Setting core.hooksPath through GIT_CONFIG_KEY_<n> or "
                  "GIT_CONFIG_PARAMETERS turns off the repository's git hooks.", file=sys.stderr)
            return 2
        reason = verdict(args, subagent, here, blind)
        if isinstance(reason, Ask):
            asks.append(reason)
        elif reason:
            log_block(reason_rule(reason), event, who)
            advice = "" if isinstance(reason, Rule) else f" {SAFE_ALTERNATIVE}"
            print(f"BLOCKED by git-safety-guard: {reason.replace(MARK, '')}{advice}", file=sys.stderr)
            return 2
    if asks:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                                 "permissionDecisionReason": f"git-safety-guard: {asks[0]}"}}))
    return 0


def main():
    raw = ""
    try:
        raw = sys.stdin.read()
        return check(raw)
    except Exception as exc:  # a guard bug blocks git commands only, never every command
        if watched(raw):
            log_block("git:internal-error")
            print(f"BLOCKED by git-safety-guard: internal error on a git or floor command ({exc!r}).", file=sys.stderr)
            return 2
        print(f"git-safety-guard: internal error, allowing a command with no git in it ({exc!r})")
        return 0


if __name__ == "__main__":
    sys.exit(main())
