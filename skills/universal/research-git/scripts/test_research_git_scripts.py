"""Fail-closed contracts for the research-git scripts, using a stub `gh`. No network.

Run: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEARCH = HERE / "search_repos.sh"
FETCH = HERE / "fetch_repo_assets.sh"
DIFF = HERE / "diff_against_local.sh"

# The stub reads STUB_MODE to pick a behaviour. It never touches the network.
STUB_GH = r'''#!/usr/bin/env python3
import base64, json, os, sys
mode = os.environ.get("STUB_MODE", "")
args = sys.argv[1:]
if args[:2] == ["auth", "status"]:
    sys.exit(0)
log = os.environ.get("STUB_LOG")
if log:
    with open(log, "a") as fh:
        fh.write("\n".join(sorted(os.listdir(os.environ.get("TMPDIR", "")))) + "\n")
if args[:2] == ["search", "repos"]:
    if mode == "ratelimit":
        sys.stderr.write("HTTP 403: API rate limit exceeded for user ID 1.\n")
        sys.exit(1)
    if mode == "empty":
        print("[]")
        sys.exit(0)
    print(json.dumps([{"fullName": "o/r", "description": "d", "stargazersCount": 900,
                       "updatedAt": "2026-01-01T00:00:00Z", "language": "Go"}]))
    sys.exit(0)
if args[0] == "api":
    path = args[1]
    if mode == "ratelimit":
        sys.stderr.write("HTTP 403: API rate limit exceeded\n")
        sys.exit(1)
    if path == "repos/example/repo":
        print(json.dumps(dict(license=dict(spdx_id="MIT"), stargazers_count=0,
                              updated_at="2026-09-11", description="", default_branch="main",
                              archived=False, fork=False)))
        sys.exit(0)
    if "/commits/" in path:
        if mode == "nosha":
            sys.stderr.write("HTTP 404: No commit found for SHA: main\n")
            sys.exit(1)
        print("abc123")
        sys.exit(0)
    if path == "repos/example/repo/git/trees/abc123?recursive=1":
        print(json.dumps({"truncated": True, "tree": [{"path": "README.md", "type": "blob"}]}))
        sys.exit(0)
    if path == "repos/example/repo/git/trees/abc123":
        print(json.dumps({"truncated": False, "tree": [
            {"path": "README.md", "type": "blob", "sha": "b0"},
            {"path": "skills", "type": "tree", "sha": "t1"}]}))
        sys.exit(0)
    if path == "repos/example/repo/git/trees/t1?recursive=1":
        print(json.dumps({"truncated": False, "tree": [{"path": "demo/SKILL.md", "type": "blob"}]}))
        sys.exit(0)
    if path.startswith("repos/example/repo/contents/") and mode == "ratelimit_contents":
        sys.stderr.write("HTTP 403: API rate limit exceeded for user ID 1.\n")
        sys.exit(1)
    if path.startswith("repos/example/repo/contents/docs?"):
        print(json.dumps([{"type": "dir", "name": "sub"}]))
        sys.exit(0)
    if path.startswith("repos/example/repo/contents/docs/sub?"):
        print(json.dumps([{"type": "file", "name": "a.md"}]))
        sys.exit(0)
    if path.startswith("repos/example/repo/contents/docs/sub/a.md?") and mode == "ratelimit_nested":
        sys.stderr.write("HTTP 403: API rate limit exceeded for user ID 1.\n")
        sys.exit(1)
    if path.startswith("repos/example/repo/contents/skills/demo/SKILL.md"):
        print(json.dumps({"encoding": "base64",
                          "content": base64.b64encode(b"# demo skill\n").decode()}))
        sys.exit(0)
    sys.exit(1)
sys.exit(2)
'''

# Stub curl for the Scorecard lookup. STUB_CURL picks: ok (200 + score), notfound
# (404, the project is not published), fail (network error, nothing written).
STUB_CURL = r'''#!/usr/bin/env python3
import os, sys
mode = os.environ.get("STUB_CURL", "ok")
args = sys.argv[1:]
out = args[args.index("-o") + 1] if "-o" in args else None
if mode == "fail":
    sys.exit(7)
body, code = ('{"score": 7.5}', "200") if mode == "ok" else ('{"code":404,"message":"not found"}', "404")
if out:
    open(out, "w").write(body)
else:
    sys.stdout.write(body)
if "-w" in args:
    sys.stdout.write(code)
'''


class StubbedGh(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        bins = self.root / "bin"
        bins.mkdir()
        gh = bins / "gh"
        gh.write_text(STUB_GH)
        gh.chmod(0o755)
        curl = bins / "curl"
        curl.write_text(STUB_CURL)
        curl.chmod(0o755)
        self.path = str(bins) + os.pathsep + os.environ["PATH"]

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, script, *args, mode="", extra_env=None):
        env = dict(os.environ, PATH=self.path, STUB_MODE=mode, **(extra_env or {}))
        return subprocess.run(["bash", str(script), *args], env=env,
                              capture_output=True, text=True)


class SearchReposTests(StubbedGh):
    # G1: a rate-limited search must fail, not print "(no results)" and exit 0.
    def test_rate_limit_fails_loud(self):
        run = self.run_script(SEARCH, "--kind", "practice", "monorepo", mode="ratelimit")
        self.assertEqual(run.returncode, 1)
        self.assertIn("rate limit exceeded", run.stderr)
        self.assertIn("gh api rate_limit", run.stderr)
        self.assertNotIn("(no results)", run.stdout)

    def test_missing_kind_exits_1(self):
        run = self.run_script(SEARCH)
        self.assertEqual(run.returncode, 1)
        self.assertIn("--kind is required", run.stderr)

    def test_help_exits_0_without_calling_gh(self):
        run = self.run_script(SEARCH, "--help", mode="ratelimit")
        self.assertEqual(run.returncode, 0)
        self.assertIn("four modes", run.stdout)

    def test_empty_result_is_reported_not_failed(self):
        run = self.run_script(SEARCH, "--kind", "code", "react", mode="empty")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("(no results)", run.stdout)

    def test_results_render(self):
        run = self.run_script(SEARCH, "--kind", "practice", "monorepo")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("o/r", run.stdout)

    # mktemp must honour TMPDIR: bare `mktemp` on macOS writes to the system temp
    # dir, which sandboxed runs cannot write, so the script aborted before searching.
    def test_temp_file_lands_in_tmpdir(self):
        tmpdir = self.root / "tmp"
        tmpdir.mkdir()
        log = self.root / "stub.log"
        run = self.run_script(SEARCH, "--kind", "practice", "monorepo",
                              extra_env={"TMPDIR": str(tmpdir), "STUB_LOG": str(log)})
        self.assertEqual(run.returncode, 0, run.stderr)
        seen = log.read_text().split()
        self.assertTrue(any(n.startswith("search_repos.") for n in seen), seen)

    def test_awesome_mode_fails_loud(self):
        run = self.run_script(SEARCH, "--awesome", mode="ratelimit")
        self.assertEqual(run.returncode, 1)
        self.assertNotIn("★ ?", run.stdout)


class FetchAndDiffTests(StubbedGh):
    # G4: --help is not an error.
    def test_help_exits_0(self):
        for script in (FETCH, DIFF):
            run = self.run_script(script, "--help")
            self.assertEqual(run.returncode, 0, script.name)
            self.assertIn("Usage", run.stdout)

    def test_no_args_exit_1(self):
        for script in (FETCH, DIFF):
            self.assertEqual(self.run_script(script).returncode, 1, script.name)

    def test_unresolvable_sha_fails_loud(self):
        run = self.run_script(FETCH, "example/repo", str(self.root / "out"), "--kind", "skill",
                              mode="nosha")
        self.assertEqual(run.returncode, 1)
        self.assertIn("cannot resolve the commit SHA", run.stderr)

    # G2: a truncated recursive tree is walked, and the listing says so.
    def test_truncated_tree_is_walked(self):
        run = self.run_script(FETCH, "example/repo", str(self.root / "out"), "--kind", "skill")
        self.assertEqual(run.returncode, 0, run.stderr)
        out = self.root / "out" / "example__repo"
        self.assertEqual((out / "SKILL.md").read_text(), "# demo skill\n")
        meta = json.loads((out / "_metadata.json").read_text())
        self.assertEqual(meta["tree_listing"], "complete-after-truncation")
        manifest = (out / "_fetch-manifest.jsonl").read_text()
        self.assertIn("truncated; walked subtrees", manifest)

    # A throttled contents call is not a missing optional path: the fetch must stop,
    # not record "unavailable" and exit 0 with fetch_status "partial".
    def test_rate_limited_contents_fails_loud(self):
        run = self.run_script(FETCH, "example/repo", str(self.root / "out"), "--kind", "code",
                              mode="ratelimit_contents")
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn("rate limit exceeded", run.stderr)
        self.assertFalse((self.root / "out" / "example__repo" / "_metadata.json").exists())

    # The same abort must work for a file inside a directory listing, where the
    # old pipe-into-while loop ran fetch_file in a subshell.
    def test_rate_limited_nested_file_fails_loud(self):
        run = self.run_script(FETCH, "example/repo", str(self.root / "out"),
                              "--kind", "killer-feature", mode="ratelimit_nested")
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn("rate limit exceeded", run.stderr)
        self.assertFalse((self.root / "out" / "example__repo" / "_metadata.json").exists())

    def test_fetch_temp_files_land_in_tmpdir(self):
        tmpdir = self.root / "tmp"
        tmpdir.mkdir()
        log = self.root / "stub.log"
        run = self.run_script(FETCH, "example/repo", str(self.root / "out"), "--kind", "skill",
                              extra_env={"TMPDIR": str(tmpdir), "STUB_LOG": str(log)})
        self.assertEqual(run.returncode, 0, run.stderr)
        seen = log.read_text().split()
        self.assertTrue(any(n.startswith("fetch_repo_assets.") for n in seen), seen)

    # A SKILL.md with no "## " headings made grep exit 1; under pipefail + set -e
    # the script died silently instead of reporting "no new section headings".
    def test_diff_survives_skill_without_headings(self):
        ext = self.root / "ext"
        loc = self.root / "loc"
        ext.mkdir()
        loc.mkdir()
        (ext / "SKILL.md").write_text("# only a title\n")
        (loc / "SKILL.md").write_text("# title\n\n## Section\n")
        run = self.run_script(DIFF, str(ext), str(loc))
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("no new section headings", run.stdout)
        self.assertIn("Next Steps", run.stdout)

    # A Scorecard lookup that fails (network, DNS, proxy) must not be recorded the
    # same way as a project Scorecard has never scored: "n/a" hid the difference.
    def test_scorecard_fetch_failure_is_distinct_from_not_published(self):
        cases = {"ok": "7.5", "notfound": "not published (404)",
                 "fail": "unavailable (fetch failed)"}
        for stub_mode, expected in cases.items():
            with self.subTest(stub_mode=stub_mode):
                out = self.root / f"out-{stub_mode}"
                run = self.run_script(FETCH, "example/repo", str(out), "--kind", "code",
                                      extra_env={"STUB_CURL": stub_mode})
                self.assertEqual(run.returncode, 0, run.stderr)
                meta = json.loads((out / "example__repo" / "_metadata.json").read_text())
                self.assertEqual(meta["scorecard"], expected)
                self.assertNotEqual(meta["scorecard"], "n/a")

    # An input with no SKILL.md is not a skill bundle; a soft note and exit 0 let a
    # wrong path (raw/ parent, a practice extract) pass as "nothing new".
    def test_diff_rejects_non_skill_bundle_with_exit_2(self):
        skill = self.root / "skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# title\n\n## Section\n")
        for label, ext, loc in (("external", self.root / "raw", skill),
                                ("local", skill, self.root / "notskill")):
            with self.subTest(side=label):
                (self.root / "raw").mkdir(exist_ok=True)
                (self.root / "notskill").mkdir(exist_ok=True)
                run = self.run_script(DIFF, str(ext), str(loc))
                self.assertEqual(run.returncode, 2, run.stdout)
                self.assertIn("SKILL.md", run.stderr)
                self.assertNotIn("Next Steps", run.stdout)

    def test_capped_tree_walk_is_partial(self):
        run = self.run_script(FETCH, "example/repo", str(self.root / "out"), "--kind", "skill",
                              extra_env={"MAX_TREE_CALLS": "1"})
        self.assertEqual(run.returncode, 0, run.stderr)
        meta = json.loads((self.root / "out" / "example__repo" / "_metadata.json").read_text())
        self.assertEqual(meta["tree_listing"], "capped")
        self.assertEqual(meta["fetch_status"], "partial")
        self.assertIn("capped", run.stderr)


if __name__ == "__main__":
    unittest.main()
