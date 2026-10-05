# Hooks and Safety

The harness ships 3 hooks. None is active until you register it. This page explains what each hook does, how to install it, and what to do when it blocks a command.

- [1. The hooks](#1-the-hooks)
- [2. Install the hooks](#2-install-the-hooks)
- [3. The git safety guard in detail](#3-the-git-safety-guard-in-detail)
- [4. When a command is blocked](#4-when-a-command-is-blocked)
- [5. If work was lost](#5-if-work-was-lost)
- [6. Several agents in one tree](#6-several-agents-in-one-tree)
- [7. Limits](#7-limits)

## 1. The hooks

| Hook | Runtime and event | What it does |
|---|---|---|
| `git-safety-guard.py` | Claude Code and Codex, before each shell command | Blocks git commands that can destroy uncommitted work, bypass git hooks, or force-push `main` or `dev` |
| `config-guard.py` | Claude Code, before each `Write` or `Edit` | Denies an edit to an existing lint or format config, so an agent cannot loosen a rule to pass a check |
| `notify-waiting.py` | Claude Code, on a permission or idle prompt | Shows a desktop notification when a session waits for you |

`hooks/hooks.json` is the registry. It lists each hook's event, matcher, timeout and command. Each hook has a test file: `hooks/test_git_safety_guard.py` and `hooks/test_config_guard.py`.

## 2. Install the hooks

The hook commands run the scripts from `~/.agents/hooks/`. This fixed path works for both runtimes and for any clone location.

1. Link the scripts. Run this in your clone:

   ```bash
   mkdir -p ~/.agents/hooks
   for f in git-safety-guard.py config-guard.py notify-waiting.py; do ln -sf "$PWD/hooks/$f" ~/.agents/hooks/$f; done
   ```

   - The links point into your clone. **If you move or delete the clone, run this step again from the new location.** Otherwise the git guard is missing and blocks every `git` command (see "Fail closed" below).
   - `ln -sf` replaces any file of the same name already in `~/.agents/hooks/`.

2. Add the Claude Code entries to `~/.claude/settings.json`. These settings apply to every project on this machine. To try the hooks in one project first, put them in that project's `.claude/settings.json` instead.

   1. Back up the file: `cp ~/.claude/settings.json ~/.claude/settings.json.bak`
   2. If the file has no `"hooks"` key, add the block below.
   3. If it already has `"hooks"`, add each entry to the existing list of the same event. For example, append the two `PreToolUse` entries to your `"PreToolUse": [...]` list. Do not add a second `"PreToolUse"` key, and do not replace your existing hooks.
   4. Leave out any entry you do not want.
   5. Check the JSON: `python3 -m json.tool ~/.claude/settings.json > /dev/null && echo valid`. If it is not valid, restore the backup.

   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Bash|Monitor|mcp__.*desktop-commander.*__(start_process|interact_with_process)",
           "hooks": [
             {
               "type": "command",
               "command": "sh -c 'f=\"$HOME/.agents/hooks/git-safety-guard.py\"; if [ -f \"$f\" ]; then exec python3 \"$f\"; fi; case \"$(cat)\" in *git\\ *) echo \"git-safety-guard missing at $f: git blocked\" >&2; exit 2;; esac; exit 0'",
               "timeout": 10,
               "statusMessage": "git-safety-guard"
             }
           ]
         },
         {
           "matcher": "Write|Edit",
           "hooks": [
             {
               "type": "command",
               "command": "sh -c 'f=\"$HOME/.agents/hooks/config-guard.py\"; [ -f \"$f\" ] || exit 0; exec python3 \"$f\"'",
               "timeout": 10,
               "statusMessage": "config-guard"
             }
           ]
         }
       ],
       "Notification": [
         {
           "matcher": "permission_prompt|idle_prompt",
           "hooks": [
             {
               "type": "command",
               "command": "sh -c 'f=\"$HOME/.agents/hooks/notify-waiting.py\"; [ -f \"$f\" ] || exit 0; python3 \"$f\"; exit 0'",
               "timeout": 10
             }
           ]
         }
       ]
     }
   }
   ```

3. For Codex, add the entry to `~/.codex/hooks.json`, merged the same way:

   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Bash",
           "hooks": [
             {
               "type": "command",
               "command": "sh -c 'f=\"$HOME/.agents/hooks/git-safety-guard.py\"; if [ -f \"$f\" ]; then exec python3 \"$f\"; fi; case \"$(cat)\" in *git\\ *) echo \"git-safety-guard missing at $f: git blocked\" >&2; exit 2;; esac; exit 0'",
               "timeout": 10,
               "statusMessage": "git-safety-guard"
             }
           ]
         }
       ]
     }
   }
   ```

   Codex asks you to trust a new or changed hook. Approve it under `/hooks`, then start a new Codex session.

4. Check the guard. In a new Claude Code session, ask the agent to run `git stash`. You should get a permission prompt. **Choose No.** Seeing the prompt is the pass; choosing Yes stashes your uncommitted work.

Notes on the commands:

- **Fail closed.** If `git-safety-guard.py` is missing from `~/.agents/hooks/`, the wrapper blocks every command that contains `git `. Remove the settings entry before you remove the script.
- **Fail open.** If `config-guard.py` or `notify-waiting.py` is missing, the wrapper allows the call.
- The notification uses `osascript` on macOS and `notify-send` on Linux. The text is fixed, so it never shows a file path or command on a lock screen.

## 3. The git safety guard in detail

Several agents can share one working tree. One agent's `git stash` or `git checkout -- .` can destroy another agent's uncommitted work. The guard prevents that.

| Tier | Applies to | Commands |
|---|---|---|
| Always blocked | Everyone | `reset --hard/--merge/--keep`; path checkout (`checkout --`, `-f`, `--ours`, `--theirs`, `-p`); working-tree `restore`; `rm -f` without `--cached`; `clean` unless it is a dry run; reflog expire or delete; `prune`; `gc --prune` (except `=never`); `switch --discard-changes/-f`; `worktree remove --force`; deleting `refs/stash`; `read-tree -u`; `checkout-index -f` |
| Stash | Main session: asks you. Subagent: blocked. | `git stash` and `--autostash`, except `stash list`, `show` and `create` |
| Subagent only | Subagents outside their own linked worktree | `checkout`, `switch`, `rebase`, `merge`, `cherry-pick`, `revert`, `pull`, `am`, `reset`, `restore`, `commit`, bulk `add` (`-A`, `-u`, `.`), `branch -D/-f/-M/-C`, `update-ref`, `symbolic-ref` |
| Hook bypass | Everyone | `--no-verify`, `commit -n`, and any `core.hooksPath` override |
| Force push | Everyone | A force push or delete that reaches `main` or `dev`. A force push with no refspec also counts. Other branch names, such as `master`, `develop` or `release/*`, are not protected; see section 7. |
| Unquoted expansion | Everyone | An argument to `commit`, `am`, `push`, `merge` or `rebase` that is only an unquoted `$X`, `$(...)` or backtick expansion |

- **Subagent detection.** The guard treats a call as a subagent's when the hook payload has an `agent_id` field. Set `GIT_SAFETY_STRICT=1` to apply subagent rules to a whole session.
- **What it reads.** Aliases, heredocs, `find -exec`, `env -S`, and inline `python3 -c` or `node -e` code that mentions git.
- **No off switch.** To disable it, remove its settings entry.
- **Codex and "ask".** Codex does not support the "ask" decision yet. In Codex, add a prompt rule for `git stash` to your Codex rules if you want a prompt instead of a silent pass.

## 4. When a command is blocked

1. Read the error. `BLOCKED by git-safety-guard` names the guard. A sandbox error, a deny rule or a Codex policy message comes from another layer.
2. Do not work around the block. Use the safe alternative:

   | You wanted to | Do this instead |
   |---|---|
   | Save work before a risky step | `git diff --binary > "$TMPDIR/task.patch"` and `git diff --cached --binary > "$TMPDIR/task.staged.patch"` |
   | Give a writer its own space | `git worktree add ../wt-<task> -b <task>` |
   | Restore one file from a commit | `git show <commit>:<path> > <path>` |
   | Switch branch | Run `git switch <branch>` yourself, after you check `git status` |
   | Commit as a subagent | Report the change; the main session commits |

3. If the command is really needed, run it yourself in a terminal.

## 5. If work was lost

| Situation | Recovery |
|---|---|
| A stash was dropped | `git fsck --unreachable \| grep commit`, then `git diff <sha>^1 <sha> \| git apply` |
| A reset or rebase went over commits | `git reflog`, then create a branch at the lost commit |
| The work was staged but never committed | `git fsck --lost-found` |
| The work was never staged | Git cannot recover it |

## 6. Several agents in one tree

When several agents write, the main session integrates once:

1. Give each writing agent its own files. Never put two writers on one file.
2. Run at most 3 writing agents at once.
3. Collect each agent's report. Each report states its branch, base commit, changed files and checks.
4. Run `git status --porcelain` and check that each changed path has one owner.
5. Run the generators once, then the checks.
6. Stage explicit paths with `git add -- <paths>`, then commit once.

## 7. Limits

The guard is a seatbelt, not a sandbox. It does not catch:

- scripts on disk (`bash cleanup.sh`);
- git commands built at runtime;
- `--git-dir` and `--work-tree`;
- git config keys that run commands;
- `ssh`, `su -c` and an unquoted `bash -c $(...)`;
- `bisect run`, `submodule foreach` and `filter-branch`;
- a force push to a branch other than `main` or `dev`. The protected names are the `PROTECTED` set in `hooks/git-safety-guard.py`. Add your own names there; glob patterns such as `release/*` work.

For real isolation, give each writer its own `git worktree`.

`config-guard.py` sees only `Write` and `Edit`. A shell edit such as `sed -i` on a config file passes it.
