"""Real disk/reopen lifecycle tests; no SDK, LLM, or external server required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

_RUNTIME = Path(__file__).resolve().parents[3] / "reference_app/runtime/sqlite_lifecycle.py"
_SPEC = importlib.util.spec_from_file_location("sqlite_lifecycle", _RUNTIME)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
SQLiteLifecycle, Conflict, InvalidSource = (_MODULE.SQLiteLifecycle, _MODULE.Conflict,
                                          _MODULE.InvalidSource)


def fact(identifier="f1", source="s1", expires=None):
    return dict(id=identifier, value="preferred answer", sources=[source], expires=expires)


class SQLiteLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "memory.sqlite"
        self.now = 100
        self.store = SQLiteLifecycle(self.path, clock=lambda: self.now)
        self.store.add_episode("a", "s1", "source content")

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def reopen(self):
        self.store.close()
        self.store = SQLiteLifecycle(self.path, clock=lambda: self.now)

    def stage(self, tenant, job, inserts=(), deletes=(), expected_revision=None):
        # Fixtures compute their small candidates synchronously at this revision.
        if expected_revision is None:
            expected_revision = self.store.snapshot(tenant)["revision"]
        return self.store.stage(tenant, job, inserts, deletes, expected_revision=expected_revision)

    def seed(self):
        self.stage("a", "seed", [fact()])
        return self.store.publish("a", "seed")

    def test_persistent_stage_reopen_publish_retry(self):
        base = self.stage("a", "dream", [fact()])
        self.assertEqual(self.store.read("a"), [])
        self.reopen()
        revision = self.store.publish("a", "dream")
        self.reopen()
        self.assertEqual(self.store.read("a"), [{"id": "f1", "value": "preferred answer"}])
        self.stage("a", "dream", [fact()], expected_revision=base)
        self.assertEqual(self.store.publish("a", "dream"), revision)
        self.assertEqual(self.store.revision("a"), revision)

    def test_conflicting_workers_use_revision_cas(self):
        self.stage("a", "worker1", [fact("f1")])
        self.stage("a", "worker2", [fact("f2")])
        other = SQLiteLifecycle(self.path, clock=lambda: self.now)
        try:
            other.publish("a", "worker1")
            with self.assertRaises(Conflict):
                self.store.publish("a", "worker2")
            self.assertEqual([f["id"] for f in self.store.read("a")], ["f1"])
        finally:
            other.close()

    def test_expiry_before_publication(self):
        self.stage("a", "dream", [fact(expires=101)])
        self.now = 101
        with self.assertRaises(InvalidSource):
            self.store.publish("a", "dream")
        self.assertEqual(self.store.read("a"), [])

    def test_source_expiry_before_publication(self):
        self.store.add_episode("a", "short", "source", expires=101)
        self.stage("a", "dream", [fact(source="short")])
        self.now = 101
        with self.assertRaises(InvalidSource):
            self.store.publish("a", "dream")

    def test_read_filters_fact_and_lineage_ttl_after_reopen(self):
        self.store.add_episode("a", "short", "source", expires=102)
        self.stage("a", "dream", [fact("f1", expires=101), fact("f2", "short")])
        self.store.publish("a", "dream")
        self.now = 101
        self.reopen()
        self.assertEqual([f["id"] for f in self.store.read("a")], ["f2"])
        self.now = 102
        self.assertEqual(self.store.read("a"), [])

    def test_erasure_during_dream_cannot_resurrect(self):
        self.seed()
        self.stage("a", "dream", [fact("f2")])
        self.store.erase_episode("a", "s1")
        self.reopen()
        self.assertEqual(self.store.read("a"), [])
        with self.assertRaises(Conflict):
            self.store.publish("a", "dream")
        with self.assertRaises(Conflict):
            self.store.add_episode("a", "s1", "source content")
        self.stage("a", "fresh-job", [fact("f3")])
        with self.assertRaises(InvalidSource):
            self.store.publish("a", "fresh-job")

    def test_identical_ids_are_tenant_scoped(self):
        self.seed()
        self.store.add_episode("b", "s1", "different source")
        self.stage("b", "seed", [fact()])
        self.store.publish("b", "seed")
        self.store.erase_episode("a", "s1")
        self.assertEqual(len(self.store.read("b")), 1)
        self.assertEqual(self.store.read("a"), [])

    def test_cross_tenant_source_is_rejected(self):
        self.store.add_episode("b", "secret", "other tenant")
        self.stage("a", "dream", [fact(source="secret")])
        with self.assertRaises(InvalidSource):
            self.store.publish("a", "dream")

    def test_staged_delete_rolls_back_with_failed_insert(self):
        revision = self.seed()
        self.stage("a", "dream", [fact("f2", "missing")], deletes=["f1"])
        self.assertEqual(len(self.store.read("a")), 1)
        with self.assertRaises(InvalidSource):
            self.store.publish("a", "dream")
        self.reopen()
        self.assertEqual(self.store.revision("a"), revision)
        self.assertEqual(len(self.store.read("a")), 1)
        self.assertFalse(self.store._tombstoned("a", "fact", "f1"))

    def test_successful_delete_and_retry_after_erasure(self):
        self.seed()
        self.stage("a", "delete", deletes=["f1"])
        self.store.publish("a", "delete")
        self.assertEqual(self.store.read("a"), [])
        revision = self.store.revision("a")
        self.store.publish("a", "seed")
        self.assertEqual(self.store.revision("a"), revision)
        self.stage("a", "resurrect", [fact()])
        with self.assertRaises(Conflict):
            self.store.publish("a", "resurrect")

    def test_episode_and_job_retry_payload_must_match(self):
        revision = self.store.revision("a")
        self.store.add_episode("a", "s1", "source content")
        self.assertEqual(self.store.revision("a"), revision)
        with self.assertRaises(Conflict):
            self.store.add_episode("a", "s1", "changed")
        self.stage("a", "dream", [fact()])
        with self.assertRaises(Conflict):
            self.stage("a", "dream", [fact("f2")])

    def test_malformed_identifiers_and_batch_are_rejected(self):
        for identifier in (None, "", "a/b", "a b", "x" * 129, 5):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                self.stage("a", identifier, [fact()])
            with self.subTest(source=identifier), self.assertRaises(ValueError):
                self.stage("a", "dream", [fact(source=identifier)])
        with self.assertRaises(ValueError):
            self.stage("a", "dream", [fact(), fact()])
        with self.assertRaises(ValueError):
            self.stage("a", "dream", [fact()], deletes=["f1"])
        with self.assertRaises(ValueError):
            self.stage("a", "dream", [fact(expires=float("nan"))])

    def test_malformed_collections_leave_state_and_jobs_unchanged(self):
        self.stage("a", "seed", [fact("a"), fact("b"), fact("c"), fact("abc")])
        self.store.publish("a", "seed")
        before = self.store.snapshot("a")
        for invalid in ("abc", {"abc": True}, None, {"abc"}):
            for field in ("inserts", "deletes"):
                with self.subTest(field=field, invalid=invalid), self.assertRaises(ValueError):
                    self.stage("a", "bad", **{field: invalid})
                self.assertEqual(self.store.snapshot("a"), before)
                self.assertIsNone(self.store.db.execute(
                    "SELECT 1 FROM jobs WHERE tenant='a' AND id='bad'").fetchone())

    def test_revision_is_required_and_strict(self):
        with self.assertRaises(TypeError):
            self.store.stage("a", "dream", [fact()])
        for invalid in (None, True, False, -1, 1.0, "1"):
            with self.subTest(revision=invalid), self.assertRaises(ValueError):
                self.store.stage("a", "dream", [fact()], expected_revision=invalid)

    def test_snapshot_revision_and_sources_stay_consistent_during_writer(self):
        self.store.db.execute("PRAGMA journal_mode=WAL")
        other = SQLiteLifecycle(self.path, clock=lambda: self.now)
        original_read = self.store._read
        base = self.store.revision("a")

        def concurrent_read(tenant, now):
            # A second connection commits between the snapshot's two SELECTs.
            other.add_episode("a", "new-source", "concurrent change")
            return original_read(tenant, now)

        self.store._read = concurrent_read
        try:
            observed = self.store.snapshot("a")
            self.assertEqual(observed["revision"], base)
            self.assertEqual([e["id"] for e in observed["episodes"]], ["s1"])
            self.assertEqual(other.revision("a"), base + 1)
        finally:
            self.store._read = original_read
            other.close()

    def test_snapshot_candidate_stale_before_staging_is_rejected(self):
        observed = self.store.snapshot("a")
        self.assertEqual(observed["episodes"][0]["id"], "s1")
        self.assertEqual(observed["facts"], [])
        self.store.add_episode("a", "new-source", "concurrent change")
        with self.assertRaises(Conflict):
            self.store.stage("a", "dream", [fact()], expected_revision=observed["revision"])
        self.assertEqual(self.store.read("a"), [])

    def test_invalid_clock_rejects_reads_and_publication_without_mutations(self):
        self.store.add_episode("a", "short", "expiring source", expires=101)
        self.stage("a", "seed", [fact("keep"), fact("expired", "short", expires=101)])
        self.store.publish("a", "seed")
        self.stage("a", "dream", [fact("replacement", "short")], deletes=["keep"])
        self.now = 101
        self.reopen()
        self.assertEqual([f["id"] for f in self.store.read("a")], ["keep"])
        self.assertEqual([f["id"] for f in self.store.snapshot("a")["facts"]], ["keep"])

        def disk_state():
            return {table: [tuple(row) for row in self.store.db.execute(
                "SELECT * FROM " + table + " ORDER BY 1,2")]
                for table in ("tenants", "episodes", "facts", "lineage", "tombstones", "jobs")}

        before = disk_state()
        for invalid in (None, True, False, float("nan"), float("inf"), -float("inf"), "101"):
            self.now = invalid
            for operation in (lambda: self.store.read("a"), lambda: self.store.snapshot("a"),
                              lambda: self.store.publish("a", "dream")):
                with self.subTest(clock=invalid), self.assertRaises(ValueError):
                    operation()
                self.assertEqual(disk_state(), before)
                self.assertFalse(self.store.db.in_transaction)
        self.now = 101
        with self.assertRaises(InvalidSource):
            self.store.publish("a", "dream")
        self.assertEqual(disk_state(), before)  # failed source validation also rolls back deletion
        self.now = 100.0
        self.store.publish("a", "dream")  # connection remains usable after all rejections
        self.assertEqual([f["id"] for f in self.store.read("a")], ["expired", "replacement"])

    def test_explicit_stale_revision_rejected(self):
        with self.assertRaises(Conflict):
            self.stage("a", "dream", [fact()], expected_revision=0)


if __name__ == "__main__":
    unittest.main()
