"""consolidate.py --queue: routing-log lessons that wait too long fail; deferred ones do not.

Run: python3 test_consolidate_queue.py (stdlib unittest; no pytest needed).
"""
import datetime as dt
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("consolidate.py")
TODAY = dt.date.today().isoformat()
# Shape of a real lesson that stayed open on purpose: a STALL bullet line whose fix
# needs a user decision. Synthetic names; this skill is public.
OLD_STALL = "- 2020-01-10 STALL example-metrics — canonical revenue recipe is wrong; waiting for the owner"
HEADER = "# Routing log\n\nFormat: `YYYY-MM-DD WIN|STALL|MISROUTE <router> — <what>`\n\n## Log\n\n"


def run(log_text=None, *args):
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(SCRIPT), "--queue", *args]
        if log_text is not None:
            log = Path(tmp) / "routing-log.md"
            log.write_text(HEADER + log_text + "\n")
            cmd += ["--log", str(log)]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


class QueueTests(unittest.TestCase):
    def test_aged_lesson_without_state_fails(self):
        r = run(OLD_STALL)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("OPEN (1)", r.stdout)
        self.assertIn("example-metrics", r.stdout)

    def test_deferred_marker_keeps_lesson_visible_without_alarm(self):
        r = run(OLD_STALL + " {deferred: user-decision 2026-10-03}")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("DEFERRED (1)", r.stdout)
        self.assertNotIn("OPEN", r.stdout)

    def test_malformed_deferred_marker_does_not_defer(self):
        r = run(OLD_STALL + " {deferred: later}")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_legacy_fixes_and_pending_results_remain_visible_and_fail(self):
        log = "\n".join([
            "2020-01-02 MISROUTE router-x — old form [→ fix applied: trigger moved]",
            "- 2020-01-03 STALL skill-y — receipt form → fix 0123456ab → result pending",
            "- 2020-01-04 STALL skill-z — closed → fix 0123456ac → result WIN 2020-02-01",
        ])
        r = run(log)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("AWAITING RESULT (2)", r.stdout)
        self.assertIn("skill-y", r.stdout)
        self.assertIn("router-x", r.stdout)

    def test_planned_malformed_and_failed_fixes_cannot_close_a_lesson(self):
        for result in ("→ fix is planned", "FIXED abcdef123", "→ fix 0123456ab → result verifier failed",
                       "→ fix 0123456ab → result verifier passed but still broken",
                       "→ fix xyz → result verifier passed"):
            with self.subTest(result=result):
                r = run(OLD_STALL + " " + result)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("example-metrics", r.stdout)

    def test_successful_result_closes_only_the_syntax_queue(self):
        for result in ("verifier passed", "WIN 2020-02-01"):
            r = run(OLD_STALL + " → fix 0123456ab → result " + result)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("0 open, 0 deferred, 0 awaiting result", r.stdout)

    def test_failed_fresh_lesson_is_open_immediately(self):
        r = run(f"{TODAY} STALL sample — failed → fix 0123456ab → result verifier failed")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("OPEN (1)", r.stdout)

    def test_invalid_dates_fail_closed_in_every_state(self):
        for line in (OLD_STALL.replace("2020-01-10", "2020-02-30"),
                     OLD_STALL + " {deferred: user-decision 2020-02-30}",
                     OLD_STALL + " → fix 0123456ab → result WIN 2020-02-30",
                     OLD_STALL + " → fix 0123456ab → result WIN 2019-01-01",
                     OLD_STALL + " → fix 0123456ab → result WIN 9999-01-01"):
            with self.subTest(line=line):
                r = run(line)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("invalid date", r.stderr)

    def test_negative_age_threshold_fails_closed(self):
        self.assertEqual(run(OLD_STALL, "--days", "-1").returncode, 2)

    def test_malformed_date_shape_cannot_hide_among_valid_lines(self):
        for date in ("2020-2-30", "20200110", "not-a-date"):
            r = run("2020-01-01 WIN sample — control\n" + OLD_STALL.replace("2020-01-10", date))
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        for state in ("{deferred: user-decision 2020-2-30}",
                      "→ fix 0123456ab → result WIN 20200111"):
            r = run(OLD_STALL + " " + state)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_fresh_lesson_and_non_failure_lines_do_not_fail(self):
        log = "\n".join([f"- {TODAY} STALL skill-new — just logged",
                         "2020-01-05 MISS find-skill / undefined class",
                         "2020-01-06 WIN router-x — fine"])
        r = run(log)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("0 open", r.stdout)

    def test_days_threshold_is_respected(self):
        recent = (dt.date.today() - dt.timedelta(days=10)).isoformat()
        line = f"{recent} STALL skill-ten — ten days old"
        self.assertEqual(run(line).returncode, 0)
        self.assertEqual(run(line, "--days", "7").returncode, 1)

    def test_missing_or_empty_log_fails_closed(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--queue", "--log", "/nonexistent/routing-log.md"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(run("no dated lines here").returncode, 2)

    def test_skill_dir_still_required_without_queue(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, timeout=60)
        self.assertNotEqual(r.returncode, 0)

    def test_shipped_routing_log_is_read_by_default(self):
        # Shipped default, no --log: the library's own routing-log.md must parse (exit 0 or 1, never 2).
        r = run()
        self.assertIn(r.returncode, (0, 1), r.stdout + r.stderr)
        self.assertRegex(r.stdout, r"\d+ open")


if __name__ == "__main__":
    unittest.main()
