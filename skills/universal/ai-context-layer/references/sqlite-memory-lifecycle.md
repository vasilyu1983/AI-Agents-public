# SQLite lifecycle runtime evidence

Load when implementing or reviewing local memory publication, deletion during consolidation, or retry safety. This reference runs real SQLite transactions against a disk database; the existing state-maintenance reducer fixtures measure a separate contract.

## Execute

From the repository root, with Python 3.11 or later and no installed packages:

```bash
python3 skills/universal/ai-context-layer/builds/evals/suites/state_maintenance/test_sqlite_lifecycle.py
```

The [runtime](../builds/reference_app/runtime/sqlite_lifecycle.py) is exercised by [disk lifecycle tests](../builds/evals/suites/state_maintenance/test_sqlite_lifecycle.py). The clock is injected in epoch seconds, making expiration at the exact boundary deterministic. A single clock reader requires a finite integer or float and rejects booleans, missing values, NaN and infinities before read, snapshot or publication SQL; invalid clock input cannot bypass TTL or partially apply deletes. The suite uses temporary disk files, reopens databases, and publishes through a second connection to exercise stale worker rejection.

## Contracts demonstrated

- Episodes and facts have composite tenant/ID keys. Every public operation validates identifiers, and every source lookup includes tenant scope. The caller must derive the authorized tenant from its application identity; supplying a tenant string is not authentication.
- `snapshot` returns the tenant revision, visible facts and visible source episodes inside one read transaction. Compute a candidate from that snapshot, then pass its revision explicitly to `stage`; capturing a new revision after computation could admit stale candidates. The required revision is a nonnegative integer (booleans are rejected).
- `stage` persists the entire insert/delete candidate batch without changing live facts. Insert/delete collections must be lists or tuples; strings and mappings are rejected before staging. Candidate generation occurs outside the transaction; no model or reflection quality is implied.
- `publish` starts `BEGIN IMMEDIATE`, compares the staged tenant revision, validates each source and expiration, applies inserts and deletes, increments the revision, and marks the job published in one transaction. A failed insert rolls back earlier candidate deletes and tombstones. Any successful tenant mutation invalidates stale jobs; expiration is checked even without a revision change.
- Source erasure deletes every directly dependent fact, cascades lineage deletion, writes permanent tenant-scoped tombstones, increments the revision, and clears pending candidate payloads for that tenant. A stale dream cannot reinsert its result. Facts reference raw episodes only, so this implementation needs no recursive fact-to-fact cascade.
- Source IDs are immutable. Fact replacement uses a new ID plus deletion of the old ID in the same batch; erased IDs cannot be reused. A normalized payload fingerprint rejects an idempotency key retried with different mutations. Delivery retries return the recorded publication revision without applying mutations again, including after later erasure.
- `read` uses one SQL snapshot and excludes expired facts and facts with expired or missing sources. Expiration is a visibility rule; it does not physically delete rows. Publication clears candidate content after success while retaining the fingerprint and revision needed for retries.

A caller supplies the candidate generator; the publication pattern is:

```python
observed = store.snapshot("tenant-a")
# Build proposed inserts/deletes using observed["facts"] and observed["episodes"].
store.stage("tenant-a", "dream-1", inserts=proposed_inserts, deletes=proposed_deletes,
            expected_revision=observed["revision"])
store.publish("tenant-a", "dream-1")
```

Retain the original revision with a job retry. Recompute a stale job from a fresh snapshot and use a new job ID.

## Evidence limits

The suite demonstrates lifecycle behavior in the bundled SQLite implementation. It does not measure retrieval quality, model reflection, clustering, ANN indexes, production load, authenticated access, backup erasure, or managed-engine behavior. Tombstones and job fingerprints are durable metadata: operators must define their retention and collision/reuse policy. The database file, SQLite journals, filesystem snapshots and backups require their own erasure policy; SQL deletion does not guarantee physical sanitization.

This is a bounded reference, not a migration framework or unattended dream scheduler. Failed or stale jobs remain stored until an operator discards them; retry requires a newly computed batch and job ID after reading the new revision. Source erasure clears all pending jobs in its tenant conservatively. No queue leasing, distributed locks, schema upgrades, tenant authorization, encryption, quotas, automatic retention sweeper, provenance authority ranking, or fact-level history is implemented. Use the memory architecture's contracts to supply those controls before deployment.
