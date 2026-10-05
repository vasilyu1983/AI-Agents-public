# Cookbook: Git-Anchored Multi-Repo Ingestion

Runnable pattern for RA10. Ingests a portfolio of git repos into a vector
store with bi-temporal commit anchoring, idempotent re-embedding, and a
tombstone-on-delete forget path.

This cookbook assumes Postgres + pgvector (regulated default per RA10). The
same pattern works on MongoDB Atlas with field-name swaps; the boundary
discussion in `references/managed-memory-boundaries.md` explains why memory
rows still need app-controlled embedding even on a converged stack.

## Schema

```sql
CREATE TABLE knowledge_chunk (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_repo         text NOT NULL,
  source_path         text NOT NULL,
  source_commit_sha   text NOT NULL,
  content_hash        bytea NOT NULL,
  chunk_anchor        text NOT NULL,
  text                text NOT NULL,
  embedding           vector(1024),
  owner_scope         jsonb NOT NULL,
  valid_from_commit   text NOT NULL,
  valid_to_commit     text,
  inserted_at         timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_chunk_idem
  ON knowledge_chunk (source_repo, source_path, content_hash);

CREATE INDEX ix_chunk_live
  ON knowledge_chunk (source_repo, source_path)
  WHERE valid_to_commit IS NULL;

CREATE INDEX ix_chunk_vec
  ON knowledge_chunk USING hnsw (embedding vector_cosine_ops);

CREATE TABLE ingest_run (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_repo     text NOT NULL,
  branch          text NOT NULL,
  from_sha        text,
  to_sha          text NOT NULL,
  started_at      timestamptz NOT NULL DEFAULT now(),
  finished_at     timestamptz,
  stats           jsonb,
  status          text NOT NULL DEFAULT 'running'
);

-- RLS: tenant isolation enforced at storage, not query.
ALTER TABLE knowledge_chunk ENABLE ROW LEVEL SECURITY;
CREATE POLICY chunk_tenant_isolation ON knowledge_chunk
  USING (owner_scope ->> 'tenant_id' = current_setting('app.tenant_id', true));
```

## Chunk emitter (markdown-aware)

Heading-aware split per `references/markdown-chunking-patterns.md`.

```python
import re, hashlib
from blake3 import blake3
from dataclasses import dataclass

HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$", re.M)
CODE_FENCE = re.compile(r"^```", re.M)

@dataclass
class Chunk:
    text: str
    anchor: str          # heading slug path
    content_hash: bytes

def slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"\s+", "-", s)

def emit_chunks(md_text: str, target_tokens: int = 900) -> list[Chunk]:
    sections, stack = [], []
    cursor = 0
    for m in HEADING_RE.finditer(md_text):
        if cursor < m.start():
            sections.append((list(stack), md_text[cursor:m.start()]))
        depth, title = len(m.group(1)), m.group(2)
        stack = stack[: depth - 1] + [(depth, title)]
        cursor = m.start()
    if cursor < len(md_text):
        sections.append((list(stack), md_text[cursor:]))

    out = []
    for path, body in sections:
        if not body.strip():
            continue
        anchor = " > ".join(slug(t) for _, t in path) or "_root"
        for piece in soft_split(body, target_tokens):
            norm = re.sub(r"\s+", " ", piece).strip()
            out.append(Chunk(piece, anchor, blake3(norm.encode()).digest()))
    return out

def soft_split(body: str, target_tokens: int) -> list[str]:
    # ~4 chars/token rough cap; never split inside a code fence.
    if len(body) < target_tokens * 4:
        return [body]
    parts, buf, in_code = [], [], False
    for line in body.splitlines(keepends=True):
        if CODE_FENCE.match(line):
            in_code = not in_code
        buf.append(line)
        if not in_code and sum(len(x) for x in buf) > target_tokens * 4:
            parts.append("".join(buf))
            buf = []
    if buf:
        parts.append("".join(buf))
    return parts
```

## Ingest run

```python
import subprocess, json
from pathlib import Path

def run_ingest(repo: str, repo_path: Path, branch: str, conn, embed):
    last = conn.execute(
        "SELECT to_sha FROM ingest_run "
        "WHERE source_repo=%s AND branch=%s AND status='ok' "
        "ORDER BY finished_at DESC LIMIT 1", (repo, branch)
    ).fetchone()
    last_sha = last[0] if last else None
    cur_sha = git(repo_path, "rev-parse", branch)

    # Force-push detection.
    if last_sha and not is_ancestor(repo_path, last_sha, cur_sha):
        last_sha = None       # full re-scan
        record_anomaly(conn, repo, "branch_rewrite", last[0], cur_sha)

    run_id = start_run(conn, repo, branch, last_sha, cur_sha)
    stats = {"added": 0, "updated": 0, "tombstoned": 0, "skipped": 0}

    changed = diff_paths(repo_path, last_sha, cur_sha)
    for path, change in changed.items():
        if not path.endswith(".md"):
            continue
        if change == "deleted":
            n = conn.execute(
                "UPDATE knowledge_chunk SET valid_to_commit=%s "
                "WHERE source_repo=%s AND source_path=%s "
                "AND valid_to_commit IS NULL",
                (cur_sha, repo, path)
            ).rowcount
            stats["tombstoned"] += n
            continue

        text = (repo_path / path).read_text(encoding="utf-8")
        seen_hashes = set()
        for chunk in emit_chunks(text):
            seen_hashes.add(chunk.content_hash)
            existing = conn.execute(
                "SELECT id FROM knowledge_chunk "
                "WHERE source_repo=%s AND source_path=%s "
                "AND content_hash=%s",
                (repo, path, chunk.content_hash)
            ).fetchone()
            if existing:
                stats["skipped"] += 1
                continue
            vec = embed(chunk.text)
            conn.execute(
                "INSERT INTO knowledge_chunk(source_repo, source_path, "
                "source_commit_sha, content_hash, chunk_anchor, text, "
                "embedding, owner_scope, valid_from_commit) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (repo, path, cur_sha, chunk.content_hash, chunk.anchor,
                 chunk.text, vec, json.dumps({"tenant_id": tenant_for(repo)}),
                 cur_sha)
            )
            stats["added"] += 1

        # Tombstone chunks that disappeared from this file at this commit.
        conn.execute(
            "UPDATE knowledge_chunk SET valid_to_commit=%s "
            "WHERE source_repo=%s AND source_path=%s "
            "AND valid_to_commit IS NULL "
            "AND content_hash NOT IN %s",
            (cur_sha, repo, path, tuple(seen_hashes) or (b"",))
        )

    finish_run(conn, run_id, "ok", stats)

def git(p: Path, *args) -> str:
    return subprocess.check_output(["git", "-C", str(p), *args]).decode().strip()

def is_ancestor(p: Path, a: str, b: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(p), "merge-base", "--is-ancestor", a, b]
    ).returncode == 0

def diff_paths(p: Path, a: str | None, b: str) -> dict[str, str]:
    if a is None:
        out = git(p, "ls-tree", "-r", "--name-only", b).splitlines()
        return {x: "added" for x in out}
    out = git(p, "diff", "--name-status", a, b).splitlines()
    mapping = {"A": "added", "M": "updated", "D": "deleted", "R": "updated"}
    result = {}
    for line in out:
        parts = line.split("\t")
        status, path = parts[0][0], parts[-1]
        result[path] = mapping.get(status, "updated")
    return result
```

## Bi-temporal recall

```python
def recall_as_of(conn, repo: str, query_vec, target_sha: str, k: int = 8):
    return conn.execute("""
      WITH ancestors AS (
        SELECT sha FROM commit_graph_ancestors(%s)
      )
      SELECT id, source_path, source_commit_sha, chunk_anchor, text,
             1 - (embedding <=> %s) AS score
      FROM knowledge_chunk
      WHERE source_repo = %s
        AND valid_from_commit IN (SELECT sha FROM ancestors)
        AND (valid_to_commit IS NULL
             OR valid_to_commit NOT IN (SELECT sha FROM ancestors))
      ORDER BY embedding <=> %s
      LIMIT %s
    """, (target_sha, query_vec, repo, query_vec, k)).fetchall()
```

`commit_graph_ancestors(sha)` is a recursive CTE seeded from a `commit_graph`
table populated by the ingest run (`git rev-list <sha> --parents`).

## DSAR / forget path

A separate, audited code path. Tombstones live rows *and* redacts text so the
content is no longer recoverable; the row shape stays for audit
reconstruction.

```python
def dsar_purge(conn, tenant_id: str, requested_at, actor: str):
    rows = conn.execute(
        "UPDATE knowledge_chunk "
        "SET text='[redacted]', embedding=NULL, "
        "    valid_to_commit=COALESCE(valid_to_commit, '__dsar__') "
        "WHERE owner_scope ->> 'tenant_id' = %s "
        "RETURNING id", (tenant_id,)
    ).fetchall()
    audit(conn, actor, "dsar_purge", tenant_id, [r[0] for r in rows], requested_at)
    return len(rows)
```

The audit path (separate `audit_log` table) records who, what, when, why.
Other tenants' rows untouched; their bi-temporal queries continue to work.
This is what `test_dsar_preserves_unrelated_audit` (next task) verifies.

## Webhook entry point

```python
@app.post("/webhooks/git_push")
def webhook(req):
    verify_hmac(req)
    payload = req.json()
    enqueue_ingest(
        repo=payload["repository"]["full_name"],
        branch=payload["ref"].rsplit("/", 1)[-1],
    )
    return {"ok": True}
```

Worker holds an advisory lock per `(repo, branch)` so back-to-back pushes
serialize.

## Freshness loop

Nightly catch-up — webhooks are best-effort.

```sql
SELECT source_repo, branch, MAX(finished_at) AS last_ok
FROM ingest_run
WHERE status = 'ok'
GROUP BY 1, 2
HAVING MAX(finished_at) < now() - interval '24 hours';
```

Anything in this result triggers a forced ingest and an alert if it has
been stale >7 days.

## Smoke test

```bash
PG_DSN=postgresql://localhost/kb \
  TEST_REPO=$PWD/fixtures/sample-repo \
  pytest builds/evals/suites/git_ingest -v
```

## See also

- `references/git-anchored-ingestion.md` — the rules this cookbook implements.
- `references/markdown-chunking-patterns.md` — `emit_chunks` lineage.
- `pgvector.md` — substrate cookbook (RLS, HNSW, iterative scans).
- `mongodb_atlas.md` — converged-stack alternative.
- `references/reference-architectures.md` → RA10.
