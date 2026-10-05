"""Disk-backed lifecycle reference; consolidation candidates are supplied by the caller.

Identifiers are tenant-local. Tombstones prohibit reusing erased IDs. Publication
serializes SQLite writers and compares the entire tenant revision before mutation.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import math
import re
import sqlite3
import time


class Conflict(ValueError):
    """Stale snapshot, reused ID, or changed retry payload."""


class InvalidSource(ValueError):
    """Missing, expired, or erased lineage."""


def _identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value):
        raise ValueError("identifier must be 1-128 ASCII letters/digits or _.:-")
    return value


def _expiry(value):
    if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                              or not math.isfinite(value)):
        raise ValueError("expiry must be finite epoch seconds or None")
    return value


class SQLiteLifecycle:
    """Small synchronous reference, with an injected epoch-seconds clock."""

    def __init__(self, path, clock=time.time):
        self.clock = clock
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS tenants(tenant TEXT PRIMARY KEY, revision INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS episodes(
                tenant TEXT, id TEXT, content TEXT NOT NULL, expires REAL,
                PRIMARY KEY(tenant,id));
            CREATE TABLE IF NOT EXISTS facts(
                tenant TEXT, id TEXT, value TEXT NOT NULL, expires REAL,
                PRIMARY KEY(tenant,id));
            CREATE TABLE IF NOT EXISTS lineage(
                tenant TEXT, fact TEXT, source TEXT, PRIMARY KEY(tenant,fact,source),
                FOREIGN KEY(tenant,fact) REFERENCES facts(tenant,id) ON DELETE CASCADE,
                FOREIGN KEY(tenant,source) REFERENCES episodes(tenant,id));
            CREATE TABLE IF NOT EXISTS tombstones(
                tenant TEXT, kind TEXT, id TEXT, PRIMARY KEY(tenant,kind,id));
            CREATE TABLE IF NOT EXISTS jobs(
                tenant TEXT, id TEXT, payload TEXT NOT NULL, base INTEGER NOT NULL,
                published INTEGER, fingerprint TEXT NOT NULL, PRIMARY KEY(tenant,id));
        """)

    def _now(self):
        """Fail closed before TTL SQL or publication on an invalid clock value."""
        now = self.clock()
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise ValueError("clock must return finite epoch seconds")
        try:
            finite = math.isfinite(now)
        except OverflowError:
            finite = False
        if not finite:
            raise ValueError("clock must return finite epoch seconds")
        return now

    def close(self):
        self.db.close()

    @contextmanager
    def _transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def revision(self, tenant):
        _identifier(tenant)
        row = self.db.execute("SELECT revision FROM tenants WHERE tenant=?", (tenant,)).fetchone()
        return row[0] if row else 0

    def _bump(self, tenant):
        self.db.execute("INSERT INTO tenants VALUES (?,1) ON CONFLICT(tenant) DO UPDATE "
                        "SET revision=revision+1", (tenant,))
        return self.revision(tenant)

    def _tombstoned(self, tenant, kind, identifier):
        return self.db.execute("SELECT 1 FROM tombstones WHERE tenant=? AND kind=? AND id=?",
                               (tenant, kind, identifier)).fetchone() is not None

    def add_episode(self, tenant, identifier, content, expires=None):
        _identifier(tenant), _identifier(identifier), _expiry(expires)
        if not isinstance(content, str):
            raise ValueError("episode content must be text")
        with self._transaction():
            if self._tombstoned(tenant, "episode", identifier):
                raise Conflict("episode ID erased")
            old = self.db.execute("SELECT content,expires FROM episodes WHERE tenant=? AND id=?",
                                  (tenant, identifier)).fetchone()
            if old:
                if tuple(old) != (content, expires):
                    raise Conflict("episode ID reused with different content")
                return self.revision(tenant)
            self.db.execute("INSERT INTO episodes VALUES (?,?,?,?)",
                            (tenant, identifier, content, expires))
            return self._bump(tenant)

    def erase_episode(self, tenant, identifier):
        _identifier(tenant), _identifier(identifier)
        with self._transaction():
            if self._tombstoned(tenant, "episode", identifier):
                return self.revision(tenant)
            dependents = self.db.execute("SELECT fact FROM lineage WHERE tenant=? AND source=?",
                                         (tenant, identifier)).fetchall()
            for row in dependents:
                self._delete_fact(tenant, row[0])
            self.db.execute("DELETE FROM episodes WHERE tenant=? AND id=?", (tenant, identifier))
            self.db.execute("INSERT INTO tombstones VALUES (?,'episode',?)", (tenant, identifier))
            self.db.execute("UPDATE jobs SET payload='{}' WHERE tenant=? AND published IS NULL", (tenant,))
            return self._bump(tenant)

    def _delete_fact(self, tenant, identifier):
        self.db.execute("DELETE FROM facts WHERE tenant=? AND id=?", (tenant, identifier))
        self.db.execute("INSERT OR IGNORE INTO tombstones VALUES (?,'fact',?)", (tenant, identifier))

    def _normalize(self, inserts, deletes):
        if not isinstance(inserts, (list, tuple)) or not isinstance(deletes, (list, tuple)):
            raise ValueError("inserts and deletes must be lists or tuples")
        normalized = []
        for fact in inserts:
            if not isinstance(fact, dict) or set(fact) - {"id", "value", "sources", "expires"}:
                raise ValueError("invalid fact fields")
            identifier = _identifier(fact.get("id"))
            if not isinstance(fact.get("value"), str):
                raise ValueError("fact value must be text")
            sources = fact.get("sources")
            if not isinstance(sources, (list, tuple)) or not sources:
                raise ValueError("fact requires source IDs")
            normalized.append(dict(id=identifier, value=fact["value"],
                                   sources=sorted({_identifier(s) for s in sources}),
                                   expires=_expiry(fact.get("expires"))))
        ids = [f["id"] for f in normalized]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate insert IDs")
        deletes = sorted({_identifier(d) for d in deletes})
        if set(ids) & set(deletes):
            raise ValueError("insert/delete overlap")
        return dict(inserts=sorted(normalized, key=lambda f: f["id"]), deletes=deletes)

    def stage(self, tenant, job, inserts=(), deletes=(), *, expected_revision):
        """Persist complete candidate mutations without modifying live facts."""
        _identifier(tenant), _identifier(job)
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError("expected_revision must be a nonnegative integer")
        payload = json.dumps(self._normalize(inserts, deletes), sort_keys=True, allow_nan=False)
        fingerprint = hashlib.sha256(payload.encode()).hexdigest()
        with self._transaction():
            old = self.db.execute("SELECT fingerprint,base FROM jobs WHERE tenant=? AND id=?",
                                  (tenant, job)).fetchone()
            if old:
                if old[0] != fingerprint or old[1] != expected_revision:
                    raise Conflict("job retry changed payload or revision")
                return old[1]
            base = self.revision(tenant)
            if expected_revision != base:
                raise Conflict("stale revision at staging")
            self.db.execute("INSERT INTO jobs VALUES (?,?,?,?,NULL,?)",
                            (tenant, job, payload, base, fingerprint))
            return base

    def publish(self, tenant, job):
        _identifier(tenant), _identifier(job)
        now = self._now()
        with self._transaction():
            row = self.db.execute("SELECT * FROM jobs WHERE tenant=? AND id=?", (tenant, job)).fetchone()
            if row is None:
                raise ValueError("unknown job")
            if row["published"] is not None:
                return row["published"]  # delivery retry never reapplies mutations
            if self.revision(tenant) != row["base"]:
                raise Conflict("stale revision at publication")
            batch = json.loads(row["payload"])
            for identifier in batch["deletes"]:
                self._delete_fact(tenant, identifier)
            for fact in batch["inserts"]:
                if fact["expires"] is not None and fact["expires"] <= now:
                    raise InvalidSource("candidate expired before publication")
                if self._tombstoned(tenant, "fact", fact["id"]):
                    raise Conflict("fact ID erased")
                for source in fact["sources"]:
                    episode = self.db.execute("SELECT expires FROM episodes WHERE tenant=? AND id=?",
                                              (tenant, source)).fetchone()
                    if episode is None or (episode[0] is not None and episode[0] <= now):
                        raise InvalidSource("source missing, erased, or expired")
                if self.db.execute("SELECT 1 FROM facts WHERE tenant=? AND id=?",
                                   (tenant, fact["id"])).fetchone():
                    raise Conflict("fact ID exists; use a new ID for a replacement")
                self.db.execute("INSERT INTO facts VALUES (?,?,?,?)",
                                (tenant, fact["id"], fact["value"], fact["expires"]))
                self.db.executemany("INSERT INTO lineage VALUES (?,?,?)",
                                    [(tenant, fact["id"], s) for s in fact["sources"]])
            revision = self._bump(tenant)
            self.db.execute("UPDATE jobs SET published=?,payload='{}' WHERE tenant=? AND id=?",
                            (revision, tenant, job))
            return revision

    def read(self, tenant):
        """A single SQL snapshot filters TTL on both facts and source episodes."""
        _identifier(tenant)
        return self._read(tenant, self._now())

    def _read(self, tenant, now):
        return [dict(row) for row in self.db.execute("""
            SELECT id,value FROM facts f WHERE tenant=? AND (expires IS NULL OR expires>?)
            AND NOT EXISTS (
                SELECT 1 FROM lineage l LEFT JOIN episodes e ON e.tenant=l.tenant AND e.id=l.source
                WHERE l.tenant=f.tenant AND l.fact=f.id
                AND (e.id IS NULL OR (e.expires IS NOT NULL AND e.expires<=?))) ORDER BY id
        """, (tenant, now, now))]

    def snapshot(self, tenant):
        """Read revision, visible facts and source episodes in one SQLite snapshot.

        Compute candidates from this result, then pass its revision to stage.
        Publication rechecks TTL because time can pass without a mutation.
        """
        _identifier(tenant)
        now = self._now()
        self.db.execute("BEGIN")
        try:
            revision = self.revision(tenant)
            facts = self._read(tenant, now)
            episodes = [dict(row) for row in self.db.execute(
                "SELECT id,content,expires FROM episodes WHERE tenant=? "
                "AND (expires IS NULL OR expires>?) ORDER BY id", (tenant, now))]
            self.db.execute("COMMIT")
            return dict(revision=revision, facts=facts, episodes=episodes)
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
