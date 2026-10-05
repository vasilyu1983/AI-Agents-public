#!/usr/bin/env python3
"""Regression tests for git-safety-guard.py.

Run: python3 hooks/test_git_safety_guard.py

Each case runs the hook as a subprocess with a real PreToolUse payload, so the
tests cover stdin parsing and exit codes exactly as Claude Code and Codex see
them. GIT_* variables are removed from the environment first, so neither the
hook nor the fixture repos can reach the caller's repository. The bypass table
lives in tests/bypass_vectors.json.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
# SAFETY_GUARD_PATH runs the suite against a working copy, so the live guard is replaced only after it passes.
HOOK = os.environ.get("SAFETY_GUARD_PATH") or os.path.join(HERE, "git-safety-guard.py")
VECTORS = os.path.join(HERE, "tests", "bypass_vectors.json")
for _key in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_key]  # GIT_DIR and friends would point the hook and fixtures at the real repo
GIT_ID = ["-c", "user.email=t@example.invalid", "-c", "user.name=t"]


def make_repo(d):
    """A repo with one commit and a `feature` branch; returns its path."""
    subprocess.run(["git", "init", "-q", d], check=True)
    subprocess.run(["git", "-C", d, *GIT_ID, "commit", "-q", "--allow-empty", "-m", "init"], check=True)
    subprocess.run(["git", "-C", d, "branch", "feature"], check=True)
    return d


def run_proc(command, agent_id=None, tool_name="Bash", cwd=None, raw=None, env_extra=None):
    event = {"tool_name": tool_name, "tool_input": {"command": command}}
    if agent_id:
        event["agent_id"] = agent_id
    if cwd:
        event["cwd"] = cwd
    env = {k: v for k, v in os.environ.items() if k != "GIT_SAFETY_STRICT"}
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, HOOK],
        input=raw if raw is not None else json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
    )


def run(command, **kw):
    proc = run_proc(command, **kw)
    return proc.returncode, proc.stderr


def decision(command, **kw):
    """'block' (exit 2), 'ask' (exit 0 + PreToolUse ask JSON) or 'allow'."""
    proc = run_proc(command, **kw)
    if proc.returncode == 2:
        return "block"
    try:
        out = json.loads(proc.stdout or "{}").get("hookSpecificOutput", {})
    except ValueError:
        return "allow"
    return out.get("permissionDecision", "allow")


class AlwaysBlocked(unittest.TestCase):
    """Destructive commands block everyone; stash writes ask the parent and block subagents."""

    def assertBlocked(self, command, **kw):
        code, err = run(command, **kw)
        self.assertEqual(code, 2, f"expected block: {command!r}")
        self.assertIn("BLOCKED by git-safety-guard", err)

    def assertGated(self, command, **kw):
        """Never silently allowed: the parent is asked or blocked, a subagent is blocked."""
        self.assertIn(decision(command, **kw), {"ask", "block"}, f"parent not gated: {command!r}")
        self.assertEqual(decision(command, agent_id="sub-1", **kw), "block", f"subagent not blocked: {command!r}")

    def test_stash_writes_ask_parent_and_block_subagents(self):
        for cmd in ["git stash", "git stash push -m wip", "git stash -u", "git stash pop",
                    "git stash apply", "git stash drop", "git stash clear", "git stash store abc",
                    "git -C . stash pop", "git -c alias.s=stash s"]:
            with self.subTest(command=cmd):
                self.assertEqual(decision(cmd), "ask")
                self.assertEqual(decision(cmd, agent_id="sub-1"), "block")
                self.assertEqual(decision(cmd, env_extra={"GIT_SAFETY_STRICT": "1"}), "block")

    def test_ask_payload_shape(self):
        proc = run_proc("git stash")
        out = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual((proc.returncode, out["hookEventName"], out["permissionDecision"]), (0, "PreToolUse", "ask"))
        self.assertIn("refs/stash", out["permissionDecisionReason"])

    def test_block_wins_over_ask(self):
        self.assertEqual(decision("git stash && git reset --hard"), "block")

    def test_stash_hidden_in_chains_and_wrappers(self):
        for cmd in ["cd sub && git stash", "ls; git stash", "true || git stash", "(cd x; git stash)",
                    "sleep 1 & git stash", "echo ok\ngit stash", "bash -lc 'git stash'",
                    "sh -c \"cd x && git stash pop\"", "git -C ../other stash",
                    "git -c core.pager=cat stash", "GIT_DIR=.git git stash", "env git stash",
                    "command git stash", "/usr/bin/git stash", "echo $(git stash)",
                    "eval \"git stash\"", "eval git reset --hard", "xargs git stash < /dev/null",
                    "find . -name x | xargs -0 git checkout --"]:
            self.assertGated(cmd)

    def test_wrapper_and_plumbing_bypasses(self):
        for cmd in ["timeout 5 git stash", "env -i git stash", "env -i timeout 5 git stash",
                    "nice -n 10 git reset --hard", "stdbuf -oL git stash pop",
                    "git update-ref -d refs/stash", "git reflog expire --expire=now refs/stash",
                    "git read-tree -u --reset HEAD", "git read-tree -m -u HEAD",
                    "git checkout-index -f -a", "git checkout-index --force --all"]:
            self.assertGated(cmd)

    def test_inline_and_persistent_aliases(self):
        for cmd in ["git -c alias.s=stash s", "git -c alias.s='stash pop' s",
                    "git -c alias.x='!git reset --hard' x", "git -c alias.X=stash x"]:
            self.assertGated(cmd)
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q", d], check=True)
            subprocess.run(["git", "-C", d, "config", "alias.st", "stash"], check=True)
            subprocess.run(["git", "-C", d, "config", "alias.wipe", "!git clean -fd"], check=True)
            self.assertGated("git st", cwd=d)
            self.assertGated("git wipe", cwd=d)

    def test_unverifiable_subcommand_fails_closed(self):
        for cmd in ["git $SUB", "git \"$SUB\" pop", "git ${OP}", "echo stash | xargs git",
                    "git $(echo stash)"]:
            self.assertBlocked(cmd)

    def test_shell_keywords_and_functions(self):
        for cmd in ["if ! git diff --quiet; then git stash; fi", "for f in a b; do git checkout -- \"$f\"; done",
                    "{ git stash; }", "! git stash", "f() { git reset --hard; }; f",
                    "while true; do git stash pop; done", "git diff --name-only | xargs git checkout",
                    "(git status);git stash", "git status|&git stash", "git stash 2>/dev/null",
                    "git reset --hard >/dev/null 2>&1"]:
            self.assertGated(cmd)

    def test_checkout_of_non_ref_is_a_path(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d)
            for cmd in ["git checkout rules/x.md", "git checkout 'src/*.py'", "git -C sub checkout x.md",
                        "cd sub && git checkout x.md"]:
                self.assertBlocked(cmd, cwd=d)

    def test_heredoc_substitution_still_runs(self):
        self.assertGated("cat <<EOF\n$(git stash)\nEOF")
        self.assertGated("cat <<'EOF' > notes.md\ngit status\nEOF\ngit stash")

    def test_argv_array_command(self):
        self.assertGated(["git", "stash"])
        self.assertGated(["bash", "-lc", "git stash pop"])

    def test_destructive_non_stash(self):
        for cmd in ["git reset --hard", "git reset --hard HEAD~1", "git reset --keep",
                    "git checkout -- file.py", "git checkout -f main", "git checkout HEAD file.py",
                    "git restore file.py", "git restore --worktree --staged file.py",
                    "git clean -f", "git clean -fd", "git clean -xfd", "git clean --force",
                    "git switch --discard-changes main", "git switch -f main",
                    "git worktree remove --force ../wt"]:
            self.assertBlocked(cmd)

    def test_checkout_of_existing_path(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "notes.md"), "w").close()
            self.assertBlocked("git checkout notes.md", cwd=d)
            self.assertBlocked("git checkout .", cwd=d)

    def test_codex_tool_names(self):
        self.assertGated("git stash", tool_name="shell")
        self.assertGated("git stash", tool_name="exec_command")


class ParentAllowed(unittest.TestCase):
    """The human-driven parent keeps normal git; stash writes ask (see AlwaysBlocked)."""

    def assertAllowed(self, command, **kw):
        code, err = run(command, **kw)
        self.assertEqual(code, 0, f"expected allow: {command!r}\n{err}")

    def test_read_only_and_safe(self):
        for cmd in ["git status", "git diff", "git log --oneline -5", "git restore --staged file.py",
                    "git restore -S file.py", "git reset HEAD file.py", "git checkout -b feature",
                    "git switch main", "git worktree add ../wt-x -b x", "git worktree remove ../wt",
                    "git clean -n", "git add -A", "git commit -am msg", "git rebase main",
                    "git rm -- owned.py", "rm -f owned.tmp", "git push origin main"]:
            self.assertAllowed(cmd)

    def test_wrappers_and_plumbing_that_keep_work(self):
        for cmd in ["timeout 5 git status", "env -i git diff", "git read-tree HEAD",
                    "git checkout-index -a", "git update-ref refs/heads/x HEAD",
                    "git reflog show refs/stash", "sudo -u git ls", "git -c alias.l=log l",
                    "xargs git add < files.txt"]:
            self.assertAllowed(cmd)
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q", d], check=True)
            subprocess.run(["git", "-C", d, "config", "alias.st", "status"], check=True)
            self.assertAllowed("git st", cwd=d)
            self.assertAllowed("git unknown-cmd", cwd=d)

    def test_branch_checkout_without_path(self):
        with tempfile.TemporaryDirectory() as d:
            make_repo(d)
            self.assertAllowed("git checkout feature", cwd=d)
            self.assertAllowed("git checkout --detach HEAD", cwd=d)
            self.assertAllowed("git checkout feature 2>/dev/null", cwd=d)
            self.assertAllowed("git log --oneline > commits.txt 2>&1", cwd=d)

    def test_heredoc_bodies_are_data(self):
        for cmd in ["cat <<'EOF' > notes.md\ngit stash\ngit reset --hard\nEOF",
                    "cat <<-EOF\n\tgit clean -fd\n\tEOF", "python3 - <<'PY'\ngit checkout -- x\nPY",
                    "grep x <<< foo\ngit status"]:
            self.assertAllowed(cmd)

    def test_mentions_are_not_commands(self):
        for cmd in ["echo 'never run git stash'", "grep -rn 'git stash' docs/",
                    "rg 'reset --hard' -g '!**/.archive/**'", "# git stash"]:
            self.assertAllowed(cmd)

    def test_stash_inspection_is_read_only(self):
        for cmd in ["git stash list", "git stash show -p stash@{0}", "git stash create",
                    "git -C . stash create", "git -C . stash list", "git -C . stash show",
                    "git -c core.pager=cat stash list", "bash -lc 'git -C . stash create'",
                    "git -c alias.inspect='stash list' inspect",
                    "git stash list > stashes.txt 2>&1"]:
            for agent_id in [None, "sub-1"]:
                with self.subTest(command=cmd, agent_id=agent_id):
                    self.assertEqual(decision(cmd, agent_id=agent_id), "allow")

    def test_non_shell_tools_ignored(self):
        self.assertAllowed("git stash", tool_name="Read")


class SubagentTier(unittest.TestCase):
    """Commands that are safe for one operator but move the shared tree under peers."""

    def test_blocked_for_subagents(self):
        for cmd in ["git checkout main", "git switch main", "git rebase main", "git merge x",
                    "git pull", "git cherry-pick abc", "git reset HEAD file.py",
                    "git restore --staged file.py", "git add -A", "git add .", "git add -u",
                    "git commit -a -m x", "git commit -am x", "git branch -D x",
                    "git update-ref refs/heads/x HEAD", "git read-tree HEAD",
                    "git symbolic-ref HEAD refs/heads/x", "git commit -m x", "git commit --amend",
                    "git add ./", "git add '*'", "git add :/", "git branch -f x", "git branch -d -f x"]:
            code, _ = run(cmd, agent_id="sub-1")
            self.assertEqual(code, 2, f"expected subagent block: {cmd!r}")

    def test_allowed_for_subagents(self):
        for cmd in ["git status", "git diff", "git add path/owned.md", "git log",
                    "git worktree add ../wt-x -b x"]:
            code, err = run(cmd, agent_id="sub-1")
            self.assertEqual(code, 0, f"expected subagent allow: {cmd!r}\n{err}")

    def test_own_linked_worktree_is_exempt(self):
        with tempfile.TemporaryDirectory() as d:
            main = make_repo(os.path.join(d, "main"))
            wt = os.path.join(d, "wt")
            subprocess.run(["git", "-C", main, "worktree", "add", "-q", wt, "-b", "task"], check=True)
            for cmd in ["git commit -m x", "git add -A", "git rebase feature", "git switch feature"]:
                code, err = run(cmd, agent_id="sub-1", cwd=wt)
                self.assertEqual(code, 0, f"expected allow in own worktree: {cmd!r}\n{err}")
            code, _ = run("git commit -m x", agent_id="sub-1", cwd=main)
            self.assertEqual(code, 2, "commit in the main tree stays blocked")
            code, _ = run("git stash", agent_id="sub-1", cwd=wt)
            self.assertEqual(code, 2, "always-tier still applies in a worktree")

    def test_strict_env_forces_subagent_tier(self):
        code, _ = run("git switch main", env_extra={"GIT_SAFETY_STRICT": "1"})
        self.assertEqual(code, 2)


class BypassTable(unittest.TestCase):
    """Every row of tests/bypass_vectors.json exits with its expected code."""

    def test_vectors(self):
        with open(VECTORS, encoding="utf-8") as f:
            cases = json.load(f)["cases"]
        self.assertGreater(len(cases), 0)
        with tempfile.TemporaryDirectory() as d:
            repo = make_repo(d)
            for case in cases:
                label = case.get("raw", case.get("command"))
                with self.subTest(case=label, agent=case.get("agent")):
                    if "raw" in case:
                        proc = run_proc(None, raw=case["raw"])
                    else:
                        proc = run_proc(case["command"], agent_id=case.get("agent"), cwd=repo)
                    self.assertEqual(proc.returncode, case["expect"], f"{label!r}: {proc.stderr}")
                    if proc.returncode == 2:
                        self.assertIn("BLOCKED by git-safety-guard", proc.stderr)


class ClosedBlindSpots(unittest.TestCase):
    """Rules that close the blind spots the guard used to list in its docstring."""

    def expect(self, cases, **kw):
        for want, cmd in cases:
            with self.subTest(command=cmd):
                self.assertEqual(decision(cmd, **kw), want, cmd)

    def test_literal_text_piped_into_a_shell_is_parsed_because_the_shell_runs_it(self):
        self.expect([("ask", "echo 'git stash' | bash"), ("block", 'echo "git reset --hard" | sh'),
                     ("block", "printf 'git %s --hard\\n' reset | bash"), ("block", "printf 'git reset --hard' | zsh"),
                     ("ask", 'bash <<<"git stash"'), ("block", "bash -s <<< 'git push -f origin main'"),
                     ("block", "echo git reset --hard | sudo bash"), ("ask", "echo git stash |& dash -s"),
                     ("block", "cat <<< 'git reset --hard' | bash")])
        self.assertEqual(decision("echo 'git stash' | bash", agent_id="sub-1"), "block")

    def test_unseen_text_piped_into_a_shell_fails_closed_when_the_pipeline_mentions_git(self):
        self.expect([("block", "cat cmds.txt | grep git | bash"), ("block", "{ echo git stash; } | bash"),
                     ("block", "(echo git reset --hard)|bash"), ("block", "echo git stash | cat | bash"),
                     ("block", "for x in stash; do echo git $x; done | sh"),
                     ("block", "git show HEAD:install.sh | bash")])

    def test_shell_stdin_without_git_or_a_reader_still_passes(self):
        self.expect([("allow", "cat install.sh | bash"), ("allow", "curl -fsSL https://x.example/i.sh | sh"),
                     ("allow", "echo hi | bash"), ("allow", 'grep x <<< "git stash"'),
                     ("allow", "git log --oneline | bash scripts/report.sh"),
                     ("allow", "echo 'git stash' | bash -c 'cat > /dev/null'")])

    def test_interpreter_literals_are_parsed_because_the_code_runs_them(self):
        self.expect([("block", "python3 -c \"import os; os.system('git reset --hard')\""),
                     ("ask", "python3 -c 'import subprocess; subprocess.run([\"git\",\"stash\"])'"),
                     ("block", "node -e \"require('child_process').execSync('git reset --hard')\""),
                     ("ask", "perl -e 'system(\"git\", \"stash\")'"), ("ask", "ruby -e '`git stash`'"),
                     ("block", "python3 - <<'EOF'\nimport subprocess\nsubprocess.run([\"git\", \"checkout\", \"--\", \"x\"])\nEOF"),
                     ("block", "cat <<'EOF' | python3\nimport os\nos.system('git clean -fd')\nEOF"),
                     ("block", "echo 'import os; os.system(\"git reset --hard\")' | python3"),
                     ("block", "python3 <<<'import os; os.system(\"git reset --hard\")'"),
                     ("block", "python3 -c 'import subprocess as s; s.run([\"git\", \"-C\", d, \"commit\", \"-n\"])'"),
                     ("block", "timeout 5 python3 -u -c \"import os; os.system('git push -f origin main')\"")])

    def test_interpreter_code_that_builds_git_at_runtime_fails_closed(self):
        self.expect([("block", "python3 -c \"import subprocess,sys; subprocess.run(['git', sys.argv[1]])\""),
                     ("block", "python3 -c \"import os; os.system('git ' + 'stash')\""),
                     ("block", "python3 -c 'import subprocess; subprocess.run([\"git\"] + [\"stash\"])'"),
                     ("block", "python3 -c 'import os; os.system(f\"git {op} --hard\")'"),
                     ("block", "node -e 'require(\"child_process\").execSync(`git ${op}`)'"),
                     # Prose and a command fragment look the same, so shell-out code that names git
                     # in a literal that is not a whole git command cannot be checked.
                     ("block", "python3 - <<'EOF'\nimport subprocess\ns = 'Never run git stash here.'\n"
                               "subprocess.run(['ls'])\nEOF")])

    def test_interpreter_code_without_a_git_command_passes_untouched(self):
        self.expect([("allow", "python3 -c 'print(1)'"), ("allow", "python3 -c 'print(\"git\")'"),
                     ("allow", 'git status --short | python3 -c "import sys; print(sys.stdin.read())"'),
                     ("allow", "perl -pi -e 's/git stash/git diff/g' notes.md"),
                     ("allow", "python3 - <<'EOF'\nimport subprocess\nsubprocess.run([\"ls\"])\nEOF"),
                     ("allow", "python3 - <<'EOF'\nimport subprocess\ns = 'Never run `rm -rf` here.'\n"
                               "subprocess.run(['ls'])\nEOF"),
                     ("allow", "python3 - <<'EOF'\nimport os, subprocess\nfor r in ['a', 'b']:\n"
                               "    subprocess.run(['git', '-C', os.path.join('/x', r), 'diff', '--quiet'])\nEOF")])

    def test_unquoted_expansion_arguments_fail_closed_because_they_can_carry_flags(self):
        self.expect([("block", "git commit $FLAGS"), ("block", "git commit -m x $(echo --no-verify)"),
                     ("block", "git push origin $BRANCH"), ("block", "git merge ${BR}"), ("block", "git rebase $BASE"),
                     ("block", "git am $PATCHES"), ("block", "git -C . commit -m x `cat flags`"),
                     ("block", "bash -c 'git commit $FLAGS'"), ("block", "eval git commit \"$X\"")])

    def test_quoted_and_option_value_expansions_pass(self):
        self.expect([("allow", "git -c gc.auto=0 commit -q -F $S/c8.txt"), ("allow", 'git commit -F "$f"'),
                     ("allow", 'git commit -m "$msg"'), ("allow", 'git push origin "$branch"'),
                     ("allow", "git commit -m $msg"), ("allow", "git commit -- $FILES"), ("allow", "git add $FILES"),
                     ("allow", 'git commit -m "$(cat <<\'EOF\'\nSubject\n\nBody with $(git log -1)\nEOF\n)"'),
                     ("allow", "git commit --file=$MSG"), ("allow", "git rebase --onto $NEW main")])

    def test_rebase_exec_bodies_are_commands(self):
        self.expect([("block", "git rebase -x 'git reset --hard' main"),
                     ("block", "git rebase --exec 'git push -f origin main' main"),
                     ("block", "git rebase --exec='git commit --no-verify --amend' main"),
                     ("ask", 'git rebase -i -x "git stash" main'), ("block", 'git rebase -x "$CMD" main'),
                     ("block", "git -c alias.r='rebase -x \"git clean -fd\"' r main"),
                     ("allow", "git rebase -x 'make test' main")])

    def test_uppercase_git_is_git_on_a_case_insensitive_filesystem(self):
        self.expect([("block", "GIT reset --hard"), ("ask", "Git stash drop"), ("block", "/usr/bin/GIT reset --hard"),
                     ("block", "ENV git reset --hard"), ("block", "BASH -c 'git reset --hard'"),
                     ("block", "GIT commit --no-verify -m x")])

    def test_configured_force_refspec_counts_as_a_force_push(self):
        with tempfile.TemporaryDirectory() as d:
            repo = make_repo(d)
            for args in [["remote", "add", "origin", "https://example.invalid/o.git"],
                         ["remote", "add", "up", "https://example.invalid/u.git"],
                         ["remote", "add", "mir", "https://example.invalid/m.git"],
                         ["config", "remote.origin.push", "+HEAD:refs/heads/main"],
                         ["config", "remote.up.push", "refs/heads/feature:refs/heads/dev"],
                         ["config", "remote.mir.mirror", "true"]]:
                subprocess.run(["git", "-C", repo, *args], check=True)
            self.expect([("block", "git push"), ("block", "git push origin"), ("block", "git push -n origin"),
                         ("block", "git push mir"), ("block", f"git -C {repo} push origin"),
                         ("allow", "git push up"), ("allow", "git push origin feature")], cwd=repo)
        self.expect([("block", "git -c remote.origin.push=+HEAD:refs/heads/main push origin"),
                     ("block", "git -c remote.origin.mirror=true push origin"),
                     ("allow", "git -c remote.origin.push=+feature:feature push origin")])

    def test_parent_session_commands_still_pass(self):
        self.expect([("allow", c) for c in [
            "git -c gc.auto=0 commit -q -F $S/c8.txt", "git add -A hooks skills scripts", "git push origin dev",
            "git log --oneline -1", "git diff --cached -M --stat",
            "python3 - <<'EOF'\nimport subprocess\nsubprocess.run([\"git\",\"ls-files\",\"*learnings*.md\"])\nEOF",
            "for t in a b; do python3 $t; done", "git status --short | grep -v x",
            "bash scripts/git-hooks/validate-snapshot.sh HEAD full"]])


class ShellReadingGaps(unittest.TestCase):
    """Shapes from the 2026-10-03 guard review: text the shell runs but the guard did not read."""

    def expect(self, cases, **kw):
        for want, cmd in cases:
            with self.subTest(command=cmd):
                self.assertEqual(decision(cmd, **kw), want, cmd)

    def test_execution_actions_preserve_stash_permission(self):
        commands = [
            r"find . -exec git stash clear \;",
            r"find . -execdir git stash pop {} +",
            r"find . -ok git stash clear \;",
            "fd -x git stash clear", "fd --exec git stash clear",
            "fdfind -X git stash clear", 'env -S "git stash clear"',
            'env -S"git stash clear"', 'env --split-string="git stash clear"',
            'fd --exec-batch env -S "git stash clear"',
            r"env -i find . -exec git stash clear \;",
        ]
        for cmd in commands:
            with self.subTest(command=cmd):
                self.assertEqual(decision(cmd), "ask")
                self.assertEqual(decision(cmd, agent_id="sub-1"), "block")

    def test_execution_actions_keep_data_and_safe_commands_allowed(self):
        self.expect([
            ("allow", "find . -name git -print"),
            ("allow", "find . -name -exec -print"),
            ("allow", r"find . -exec echo git stash clear \;"),
            ("allow", r"find . -exec git status \;"),
            ("allow", "fd -- -x git"), ("allow", "fd -x git diff"),
            ("allow", 'env -S "git status"'),
            ("allow", 'env -S "printf ; git stash clear"'),
            ("allow", 'env -u -S printf git'),
            ("allow", 'env printf -S "git stash clear"'),
            ("block", 'env -S "sh -c \'git reset --hard\'"'),
        ])

    def test_cleanup_cannot_remove_shared_recovery_or_untracked_work(self):
        self.expect([
            ("block", "git reflog expire --expire=now --all"),
            ("block", "git reflog expire --expire-unreachable=now --all"),
            ("block", "git reflog delete HEAD@{1}"),
            ("block", "git reflog expire -n --no-dry-run --expire=now --all"),
            ("block", "git gc --prune=now"), ("block", "git gc --prune"),
            ("block", "git -c clean.requireForce=false clean -d"),
            ("block", "git clean -d"), ("block", "git clean -i"),
            ("allow", "git clean -n -d"),
            ("allow", "git -c clean.requireForce=false clean --dry-run -d"),
            ("allow", "git reflog show"),
            ("allow", "git reflog expire --dry-run --all"),
            ("allow", "git gc --auto"), ("allow", "git gc --prune=never"),
        ])

    def test_clean_preview_requires_an_active_option_not_a_path_or_pattern(self):
        self.expect([
            ("block", "git -c clean.requireForce=false clean -- -n"),
            ("block", "git -c clean.requireForce=false clean -- --dry-run"),
            ("block", "git -c clean.requireForce=false clean -e -n"),
            ("block", "git -c clean.requireForce=false clean -en"),
            ("block", "git -c clean.requireForce=false clean --exclude -n"),
            ("block", "git -c clean.requireForce=false clean --excl -n"),
            ("block", "git -c clean.requireForce=false clean -n --no-dry-run"),
            ("allow", "git clean -n -- -f"),
            ("allow", "git clean --dry-run --exclude -f"),
        ])

    def test_a_comment_line_does_not_hide_the_lines_after_it(self):
        self.expect([("block", "# tidy up\ngit reset --hard"), ("block", "echo hi # note\ngit clean -fd"),
                     ("block", "n=${#arr[@]}\ngit clean -fd"), ("allow", "# show state\ngit status"),
                     ("allow", "git log --format='%h #%s'")])

    def test_a_backslash_continuation_joins_the_flag_to_its_command(self):
        self.expect([("block", "git reset \\\n  --hard"), ("block", "git commit \\\n  --no-verify -m x"),
                     ("allow", "git commit -q \\\n  -m x")])

    def test_a_substitution_inside_double_quotes_runs(self):
        self.expect([("ask", 'X="$(git stash)"'), ("block", 'echo "now: $(git reset --hard)"'),
                     ("block", 'echo "`git clean -fd`"'),
                     ("allow", "git commit -m \"$(cat <<'EOF'\nmention git reset --hard here\nEOF\n)\"")])

    def test_shell_text_in_other_tools_is_checked(self):
        self.assertEqual(decision("git reset --hard", tool_name="Monitor"), "block")
        dc = "mcp__plugin_desktop-commander_desktop-commander__"
        self.assertEqual(decision("git stash", tool_name=dc + "start_process"), "ask")
        raw = json.dumps({"tool_name": dc + "interact_with_process",
                          "tool_input": {"pid": 1, "input": "os.system('git reset --hard')"}})
        self.assertEqual(run(None, raw=raw)[0], 2)
        raw = json.dumps({"tool_name": dc + "interact_with_process", "tool_input": {"pid": 1, "input": "1+1"}})
        self.assertEqual(run(None, raw=raw)[0], 0)

    def test_cd_moves_the_worktree_exemption(self):
        with tempfile.TemporaryDirectory() as d:
            main = make_repo(os.path.join(d, "main"))
            wt = os.path.join(d, "wt")
            subprocess.run(["git", "-C", main, "worktree", "add", "-q", wt, "-b", "task"], check=True)
            for want, cmd in [(2, f"cd {main} && git commit -m x"), (2, 'cd "$MAIN" && git commit -m x'),
                              (2, f"pushd {main}; popd; git commit -m x"),
                              (0, f"cd {wt} && git commit -m x"), (0, "cd . && git add -A")]:
                with self.subTest(command=cmd):
                    self.assertEqual(run(cmd, agent_id="sub-1", cwd=wt)[0], want, cmd)
            # A cd in a subshell does not move the commit; it must not earn the exemption.
            for cmd in [f"(cd {wt}); git commit -m x", f"pushd {wt}; popd; git commit -m x",
                        f'echo "$(cd {wt})"; git commit -m x', f"cd {wt} && git commit -m x"]:
                with self.subTest(command=cmd, cwd="main"):
                    self.assertEqual(run(cmd, agent_id="sub-1", cwd=main)[0], 2, cmd)
            self.assertEqual(run(f"git -C {wt} commit -m x", agent_id="sub-1", cwd=main)[0], 0)

    def test_long_option_prefixes_and_autostash(self):
        self.expect([("block", "git reset --h"), ("block", "git reset --ha HEAD"), ("block", "git clean --fo -d"),
                     ("block", "git switch --disc main"), ("block", "git restore --w f.py"),
                     ("block", "git rm -rf dir"), ("allow", "git rm -r --cached dir"),
                     ("ask", "git pull --rebase --autostash"), ("ask", "git rebase --autost main"),
                     ("allow", "git pull --rebase"), ("allow", "git reset --soft HEAD~1"),
                     ("block", "xcrun git reset --hard"), ("block", "flock /tmp/l git clean -fd")])
        self.assertEqual(decision("git pull --autostash", agent_id="sub-1"), "block")


class ReviewGaps(unittest.TestCase):
    """Shapes from the 2026-10-04 review: the documented parser limits and their sibling forms."""

    def expect(self, cases, **kw):
        for want, cmd in cases:
            with self.subTest(command=cmd):
                self.assertEqual(decision(cmd, **kw), want, cmd)

    def test_grouped_find_predicates_and_repeated_actions_keep_every_exec(self):
        self.expect([
            ("block", r"find . \( -name x \) -exec git commit --no-verify -m m \;"),
            ("block", r"find . -exec true \; -exec git reset --hard \;"),
            ("block", r"find . -exec true \; -o -exec git commit --no-verify -m m \;"),
            ("block", "find . '(' -name x ')' -exec git reset --hard ';'"),
            ("allow", r"find . \( -name x \) -exec git status \;"),
            ("allow", r"find . -exec echo git reset --hard \;"),
            ("allow", "git commit -m ';' -q"),
        ])

    def test_env_short_clusters_keep_the_split_string(self):
        self.expect([
            ("block", "env -iS 'git commit --no-verify -m m'"),
            ("block", "env -vS 'git reset --hard'"),
            ("block", r"env -iSgit\ reset\ --hard"),
            ("block", "env -iu FOO -S 'git reset --hard'"),
            ("allow", "env -iS 'git status'"),
            ("allow", "env -iu FOO printf git"),
        ])

    def test_fd_attached_and_clustered_exec_forms(self):
        self.expect([
            ("block", "fd -e py --exec=git commit --no-verify -m m"),
            ("block", "fd --exec-batch=git reset --hard"),
            ("block", "fd -xgit reset --hard"),
            ("block", "fd -Hx git reset --hard"),
            ("allow", "fd --exec=git status"), ("allow", "fd -Hx git status"),
        ])

    def test_the_shell_cannot_build_a_flag_the_guard_does_not_see(self):
        self.expect([
            ("block", "git commit --no-verify$IFS-m$IFSx"), ("block", "git commit --no-verif${E}y -m x"),
            ("block", "git commit ${E}--no-verify -m x"), ("block", 'git commit --no-verify"$E" -m x'),
            ("block", "git reset --hard$E"), ("block", "git push --for${E}ce origin main"),
            ("block", "git commit $'--no-verify' -m x"), ("block", "git reset --$'hard'"),
            ("block", "git {commit,--no-verify} -m x"), ("block", "git commit {--no-verify,-m} x"),
            ("allow", 'git commit -m "$msg" --author="$A"'), ("allow", "git commit -m $m -F \"$f\""),
            ("allow", 'git push origin "$branch"'), ("allow", 'git commit -m x -- "$f"'),
            ("allow", "git add {a,b}.py"), ("allow", "git commit -m 'x {a,b}'"),
            ("allow", "git log HEAD@{1}"), ("allow", "git diff -U$N"),
        ])

    def test_global_option_values_do_not_become_the_subcommand(self):
        self.expect([("block", "git --attr-source HEAD commit --no-verify -m x"),
                     ("allow", "git --attr-source HEAD status")])

    def test_function_and_dash_dash_wrappers_are_unwrapped(self):
        self.expect([("block", "function f { git reset --hard; }; f"), ("block", "bash -c -- 'git reset --hard'"),
                     ("allow", "bash -c -- 'git status'")])

    def test_an_alias_defined_in_the_same_command_is_checked(self):
        self.expect([("block", "git config alias.zz 'commit --no-verify' && git zz -m m"),
                     ("block", "git config alias.zz '!git reset --hard' && git zz"),
                     ("allow", "git config alias.zz status && git zz")])

    def test_text_a_shell_reads_from_a_substitution_fails_closed(self):
        self.expect([("block", "bash <(echo 'git reset --hard')"), ("block", "source <(echo git reset --hard)"),
                     ("block", 'bash -c "$(echo git reset --hard)"'),
                     ("block", "eval \"$(printf 'git reset --hard')\""),
                     ("allow", 'eval "$(ssh-agent -s)"'), ("allow", "bash <(echo ok)")])

    def test_sibling_shells_and_wrappers_are_unwrapped(self):
        self.expect([("block", f"{w} git reset --hard") for w in
                     ["watch", "parallel", "mise exec --", "pnpm exec", "script -q /dev/null"]] +
                    [("block", f"{sh} -c 'git reset --hard'") for sh in ["ksh", "fish", "tcsh", "csh"]] +
                    [("allow", "watch git status"), ("allow", "fish -c 'git status'")])

    def test_prune_and_repack_cannot_drop_unreachable_objects(self):
        self.expect([("block", "git prune --expire now"), ("block", "git prune"), ("block", "git repack -ad"),
                     ("block", "git repack -a -d"), ("allow", "git prune -n"), ("allow", "git prune --dry-run"),
                     ("allow", "git repack -Ad"), ("allow", "git repack -a")])

    def test_checkout_from_a_pathspec_file_overwrites_paths(self):
        with tempfile.TemporaryDirectory() as d:
            repo = make_repo(os.path.join(d, "repo"))
            self.expect([("block", "git checkout HEAD --pathspec-from-file=list"),
                         ("block", "git checkout --pathspec-from-file=list"),
                         ("block", "git checkout feature --pathspec-from-file list"),
                         ("allow", "git checkout feature"), ("allow", "git restore --staged --pathspec-from-file=l")],
                        cwd=repo)


class FailOpen(unittest.TestCase):
    def test_malformed_json_allows(self):
        code, _ = run(None, raw="{not json")
        self.assertEqual(code, 0)

    def test_empty_input_allows(self):
        code, _ = run(None, raw="")
        self.assertEqual(code, 0)

    def test_unbalanced_quotes_still_guarded(self):
        self.assertEqual(decision("git stash; echo 'oops"), "ask")
        self.assertEqual(decision("git reset --hard; echo 'oops"), "block")


if __name__ == "__main__":
    unittest.main(verbosity=1)
