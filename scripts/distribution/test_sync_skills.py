#!/usr/bin/env python3
"""Regression tests for scripts/distribution/sync-skills.sh: it must never remove or replace an entry it does not own.

Each test copies the live script into a throwaway repo layout under a temp dir and runs it with
HOME pointed at a fake home, so the real ~/.claude, ~/.agents and repo .claude/workflows are never touched.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("sync-skills.sh")
SKILLS = ("alpha", "beta", "gamma", "delta", "epsilon")
WORKFLOWS = ("wf-own.js", "wf-foreign.js", "wf-file.js", "wf-dir.js", "wf-new.js")


class SyncSkillsOwnership(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sync-skills-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "repo"
        (self.repo / "scripts/distribution").mkdir(parents=True)
        shutil.copy(SCRIPT, self.repo / "scripts/distribution/sync-skills.sh")
        # Group layout: skills/universal/<name>, skills/project/<name>, skills/client/<c>/<name>.
        self.src = self.repo / "skills/universal"
        for name in SKILLS + ("agents-subagents",):
            (self.src / name).mkdir(parents=True)
            (self.src / name / "SKILL.md").write_text(f"# {name}\n")
        self.project = self.repo / "skills/project/project-zeta"
        self.client = self.repo / "skills/client/acme/acme-eta"
        for d in (self.project, self.client):
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(f"# {d.name}\n")
        self.wf_src = self.repo / "agents/workflows"
        self.wf_src.mkdir(parents=True)
        self.legacy = self.repo / "frameworks/shared-skills/skills"
        for wf in WORKFLOWS:
            (self.wf_src / wf).write_text("// workflow\n")
        self.src_real = Path(os.path.realpath(self.src))
        self.wf_real = Path(os.path.realpath(self.wf_src))
        self.home = self.tmp / "fakehome"
        self.elsewhere = self.tmp / "elsewhere"
        self.elsewhere.mkdir()

    def run_sync(self, *targets):
        env = dict(os.environ, HOME=str(self.home))
        proc = subprocess.run(["bash", str(self.repo / "scripts/distribution/sync-skills.sh"), *targets],
                              env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return proc.stdout

    def test_normal_case_links_everything(self):
        out = self.run_sync()
        for target in (self.home / ".claude/skills", self.home / ".agents/skills"):
            for name in SKILLS + ("agents-subagents",):
                self.assertEqual(os.readlink(target / name), str(self.src_real / name))
            self.assertEqual(os.readlink(target / "project-zeta"), os.path.realpath(self.project))
            self.assertEqual(os.readlink(target / "acme-eta"), os.path.realpath(self.client))
        for wf in WORKFLOWS:
            self.assertEqual(os.readlink(self.home / ".claude/workflows" / wf), str(self.wf_real / wf))
            self.assertTrue((self.repo / ".claude/workflows" / wf).exists())
        self.assertIn("Linked: 8 | External skipped: 0 | Stale removed: 0", out)
        self.assertIn("Linked: 5 | External skipped: 0 | Stale removed: 0", out)
        self.assertNotIn("SKIP", out)

    def test_skills_target_keeps_foreign_entries(self):
        t = self.home / ".claude/skills"
        t.mkdir(parents=True)
        # Owned link in a relative (non-canonical) form: must be replaced by the canonical absolute link.
        os.symlink(os.path.relpath(self.src / "alpha", t), t / "alpha")
        (self.elsewhere / "beta").mkdir()
        os.symlink(self.elsewhere / "beta", t / "beta")          # foreign same-name link
        (t / "gamma").write_text("user file\n")                     # same-name plain file
        (t / "delta").mkdir()                                       # same-name real dir
        (t / "delta" / "SKILL.md").write_text("# external delta\n")
        os.symlink("/nonexistent/other-tool/thing", t / "other-broken")  # foreign broken, non-library name
        os.symlink(self.src_real / "removed-skill", t / "removed-skill")  # repo-owned stale link

        out = self.run_sync("claude")

        with self.subTest('self.assertEqual(os.readlink(t / "alpha"), str(self.src_real / "alpha"))'):
            self.assertEqual(os.readlink(t / "alpha"), str(self.src_real / "alpha"))
        with self.subTest('self.assertEqual(os.readlink(t / "beta"), str(self.elsewhere / "beta"))'):
            self.assertEqual(os.readlink(t / "beta"), str(self.elsewhere / "beta"))
        with self.subTest('self.assertFalse((t / "gamma").is_symlink())'):
            self.assertFalse((t / "gamma").is_symlink())
        with self.subTest('self.assertEqual((t / "gamma").read_text(), "user file\\n")'):
            self.assertEqual((t / "gamma").read_text(), "user file\n")
        with self.subTest('self.assertFalse((t / "delta").is_symlink())'):
            self.assertFalse((t / "delta").is_symlink())
        with self.subTest('self.assertEqual((t / "delta" / "SKILL.md").read_text(), "# external delta\\n")'):
            self.assertEqual((t / "delta" / "SKILL.md").read_text(), "# external delta\n")
        with self.subTest('self.assertTrue((t / "other-broken").is_symlink())'):
            self.assertTrue((t / "other-broken").is_symlink())
        with self.subTest('self.assertFalse(os.path.lexists(t / "removed-skill"))'):
            self.assertFalse(os.path.lexists(t / "removed-skill"))
        with self.subTest('self.assertEqual(os.readlink(t / "epsilon"), str(self.src_real / "epsilon"))'):
            self.assertEqual(os.readlink(t / "epsilon"), str(self.src_real / "epsilon"))
        with self.subTest('self.assertIn("SKIP (foreign symlink): beta", out)'):
            self.assertIn("SKIP (foreign symlink): beta", out)
        with self.subTest('self.assertIn("SKIP (foreign file): gamma", out)'):
            self.assertIn("SKIP (foreign file): gamma", out)
        with self.subTest('self.assertIn("SKIP (foreign directory): delta", out)'):
            self.assertIn("SKIP (foreign directory): delta", out)
        with self.subTest('self.assertIn("External skipped: 3 | Stale removed: 1", out)'):
            self.assertIn("External skipped: 3 | Stale removed: 1", out)

    def test_workflows_keep_foreign_entries(self):
        t = self.home / ".claude/workflows"
        t.mkdir(parents=True)
        os.symlink(self.wf_src / "wf-own.js", t / "wf-own.js")  # owned, unresolved-prefix form
        (self.elsewhere / "wf-foreign.js").write_text("// other tool\n")
        os.symlink(self.elsewhere / "wf-foreign.js", t / "wf-foreign.js")
        (t / "wf-file.js").write_text("// user file\n")
        (t / "wf-dir.js").mkdir()
        os.symlink("/nonexistent/other-tool/x.js", t / "other-broken.js")
        os.symlink(self.wf_real / "wf-gone.js", t / "wf-gone.js")  # repo-owned stale link
        repo_wf = self.repo / ".claude/workflows"
        repo_wf.mkdir(parents=True)
        os.symlink(self.elsewhere / "wf-foreign.js", repo_wf / "wf-foreign.js")
        os.symlink("/nonexistent/other-tool/y.js", repo_wf / "other-broken.js")

        out = self.run_sync("claude")

        with self.subTest('self.assertEqual(os.readlink(t / "wf-own.js"), str(self.wf_real / "wf-own.js"))'):
            self.assertEqual(os.readlink(t / "wf-own.js"), str(self.wf_real / "wf-own.js"))
        with self.subTest('self.assertEqual(os.readlink(t / "wf-foreign.js"), str(self.elsewhere / "wf-foreign.js"))'):
            self.assertEqual(os.readlink(t / "wf-foreign.js"), str(self.elsewhere / "wf-foreign.js"))
        with self.subTest('self.assertEqual((t / "wf-file.js").read_text(), "// user file\\n")'):
            self.assertEqual((t / "wf-file.js").read_text(), "// user file\n")
        with self.subTest('self.assertTrue((t / "wf-dir.js").is_dir() and not (t / "wf-dir.js").is_symlink())'):
            self.assertTrue((t / "wf-dir.js").is_dir() and not (t / "wf-dir.js").is_symlink())
        with self.subTest('self.assertTrue((t / "other-broken.js").is_symlink())'):
            self.assertTrue((t / "other-broken.js").is_symlink())
        with self.subTest('self.assertFalse(os.path.lexists(t / "wf-gone.js"))'):
            self.assertFalse(os.path.lexists(t / "wf-gone.js"))
        with self.subTest('self.assertEqual(os.readlink(t / "wf-new.js"), str(self.wf_real / "wf-new.js"))'):
            self.assertEqual(os.readlink(t / "wf-new.js"), str(self.wf_real / "wf-new.js"))
        with self.subTest('self.assertEqual(os.readlink(repo_wf / "wf-foreign.js"), str(self.elsewhere / "wf-foreign.'):
            self.assertEqual(os.readlink(repo_wf / "wf-foreign.js"), str(self.elsewhere / "wf-foreign.js"))
        with self.subTest('self.assertTrue((repo_wf / "other-broken.js").is_symlink())'):
            self.assertTrue((repo_wf / "other-broken.js").is_symlink())
        with self.subTest('self.assertIn("SKIP (foreign symlink): wf-foreign.js", out)'):
            self.assertIn("SKIP (foreign symlink): wf-foreign.js", out)
        with self.subTest('self.assertIn("SKIP (foreign file): wf-file.js", out)'):
            self.assertIn("SKIP (foreign file): wf-file.js", out)
        with self.subTest('self.assertIn("SKIP (foreign directory): wf-dir.js", out)'):
            self.assertIn("SKIP (foreign directory): wf-dir.js", out)
        with self.subTest('self.assertIn("Linked: 2 | External skipped: 3 | Stale removed: 1", out)'):
            self.assertIn("Linked: 2 | External skipped: 3 | Stale removed: 1", out)

    def test_legacy_location_links_are_replaced(self):
        # Links made before the 2026-10-03 re-layout point into frameworks/shared-skills/skills
        # (now gone). They are ours: a re-sync must re-point them, not skip them as foreign.
        t = self.home / ".claude/skills"
        t.mkdir(parents=True)
        os.symlink(self.legacy / "alpha", t / "alpha")
        os.symlink(self.legacy / "old-removed", t / "old-removed")
        w = self.home / ".claude/workflows"
        w.mkdir(parents=True)
        os.symlink(self.legacy / "agents-subagents/assets/workflows/wf-own.js", w / "wf-own.js")
        repo_wf = self.repo / ".claude/workflows"
        repo_wf.mkdir(parents=True)
        os.symlink("../../frameworks/shared-skills/skills/agents-subagents/assets/workflows/wf-own.js",
                   repo_wf / "wf-own.js")

        out = self.run_sync("claude")

        self.assertEqual(os.readlink(t / "alpha"), str(self.src_real / "alpha"))
        self.assertFalse(os.path.lexists(t / "old-removed"))
        self.assertEqual(os.readlink(w / "wf-own.js"), str(self.wf_real / "wf-own.js"))
        self.assertEqual(os.readlink(repo_wf / "wf-own.js"), "../../agents/workflows/wf-own.js")
        self.assertNotIn("SKIP", out)

    def test_duplicate_name_across_groups_fails(self):
        # Runtime folders are flat, so one name in two groups would make one skill vanish.
        (self.repo / "skills/project/alpha").mkdir(parents=True)
        (self.repo / "skills/project/alpha/SKILL.md").write_text("# alpha again\n")
        env = dict(os.environ, HOME=str(self.home))
        proc = subprocess.run(["bash", str(self.repo / "scripts/distribution/sync-skills.sh")],
                              env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("exists in more than one group", proc.stderr)
        self.assertFalse((self.home / ".claude/skills").exists())


if __name__ == "__main__":
    unittest.main()
