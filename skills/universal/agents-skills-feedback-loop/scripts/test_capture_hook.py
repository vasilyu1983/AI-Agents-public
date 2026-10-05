"""Regression coverage for the Layer 1 capture hook (assets/learnings_capture.py).

Why these tests exist:
- A session-end hook runs under the runtime's hook time budget. Model calls made
  inside that budget get cancelled, so the hook must hand the work to a detached
  worker and return at once.
- The reflection call reads untrusted transcript text. It must run with no tools
  and must not persist a new session transcript.

Run: python3 -m unittest scripts/test_capture_hook.py  (from the skill root)
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
HOOK = SKILL / "assets" / "learnings_capture.py"
APPEND = SKILL / "scripts" / "append_learning.py"


def wait_for(predicate, seconds=15.0):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.1)
    return False


class CaptureHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        root = self.tmp / "skills"
        loop_scripts = root / "agents-skills-feedback-loop" / "scripts"
        loop_scripts.mkdir(parents=True)
        shutil.copy2(APPEND, loop_scripts / "append_learning.py")
        self.demo = root / "demo"
        self.demo.mkdir()
        (self.demo / "SKILL.md").write_text("# Demo\n\n## Learnings Loop\nWired.\n")
        (self.demo / "learnings.md").write_text("# demo — Learnings\n\n## Mistakes to Avoid\n\n")
        self.transcript = self.tmp / "session.jsonl"
        lines = [
            {"message": {"role": "user", "content": "use the demo skill"}},
            {"message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": "demo"}}]}},
        ]
        self.transcript.write_text("\n".join(json.dumps(x) for x in lines) + "\n")
        self.env = dict(os.environ)
        self.env.pop("CLOSED_LOOP_HOOK_ACTIVE", None)
        self.env.update({"HOME": str(self.tmp / "home"), "LEARNINGS_SKILLS_ROOT": str(root)})
        (self.tmp / "home").mkdir()

    def run_hook(self, env):
        payload = {"session_id": "s1", "transcript_path": str(self.transcript), "cwd": str(self.tmp)}
        start = time.time()
        proc = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                              capture_output=True, text=True, env=env, timeout=60)
        return proc, time.time() - start

    def test_hook_returns_before_slow_reflection_finishes(self):
        env = dict(self.env, LEARNINGS_REFLECT_CMD="sleep 3; echo 'Mistakes to Avoid|||Detached capture still appends'")
        proc, elapsed = self.run_hook(env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertLess(elapsed, 2.0, "hook blocked on the model call; the runtime budget would cancel it")
        learnings = self.demo / "learnings.md"
        self.assertTrue(wait_for(lambda: "Detached capture still appends" in learnings.read_text()),
                        "detached worker never appended the learning")

    def test_reflection_runs_without_tools_or_session_persistence(self):
        bindir = self.tmp / "bin"
        bindir.mkdir()
        argv_file = self.tmp / "claude-argv.json"
        stub = bindir / "claude"
        stub.write_text(
            f"#!{sys.executable}\nimport json, sys\n"
            f"open({str(argv_file)!r}, 'w').write(json.dumps(sys.argv[1:]))\nprint('SKIP')\n")
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        env = dict(self.env, PATH=f"{bindir}:{self.env.get('PATH', '')}")
        env.pop("LEARNINGS_REFLECT_CMD", None)
        proc, _ = self.run_hook(env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(wait_for(lambda: argv_file.exists() and argv_file.read_text()), "claude was never called")
        argv = json.loads(argv_file.read_text())
        self.assertIn("--no-session-persistence", argv)
        self.assertIn("--tools", argv)
        self.assertEqual(argv[argv.index("--tools") + 1], "", "reflection call must disable all tools")


if __name__ == "__main__":
    unittest.main()
