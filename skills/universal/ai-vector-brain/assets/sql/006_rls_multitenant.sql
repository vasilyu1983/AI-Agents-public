-- Row Level Security template for multi-tenant brains.
--
-- Use ONLY when the brain hosts more than one tenant in the same schema.
-- Single-tenant or single-project deployments should not enable RLS -- it
-- adds overhead with no isolation benefit.
--
-- Tenancy contract:
--   * Caller (app or pgbouncer prepend) MUST set the session variable:
--       SELECT set_config('app.tenant_id', $1, true);
--     before any query. The `true` makes it transaction-local.
--   * Missing/empty tenant_id => zero rows visible. This is intentional: it
--     fails closed rather than leaking another tenant's data on app drift.
--   * Service-role workloads (ingest, eval, migration) should connect as a
--     role with BYPASSRLS or set `app.tenant_id` to the operating tenant.

ALTER TABLE documents
  ADD COLUMN IF NOT EXISTS tenant_id TEXT;

ALTER TABLE chunks
  ADD COLUMN IF NOT EXISTS tenant_id TEXT;

ALTER TABLE embeddings
  ADD COLUMN IF NOT EXISTS tenant_id TEXT;

-- Backfill from documents into chunks/embeddings if migrating an existing brain.
-- Adapt to your data; do not run on a populated brain without inspection.
--   UPDATE chunks c SET tenant_id = d.tenant_id
--     FROM documents d WHERE c.document_id = d.id AND c.tenant_id IS NULL;
--   UPDATE embeddings e SET tenant_id = c.tenant_id
--     FROM chunks c WHERE e.chunk_id = c.id AND e.tenant_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_documents_tenant   ON documents   (tenant_id);
CREATE INDEX IF NOT EXISTS idx_chunks_tenant      ON chunks      (tenant_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_tenant  ON embeddings  (tenant_id);

ALTER TABLE documents  ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks     ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;

ALTER TABLE documents  FORCE ROW LEVEL SECURITY;
ALTER TABLE chunks     FORCE ROW LEVEL SECURITY;
ALTER TABLE embeddings FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_documents ON documents
  USING (tenant_id = current_setting('app.tenant_id', true))
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

CREATE POLICY tenant_isolation_chunks ON chunks
  USING (tenant_id = current_setting('app.tenant_id', true))
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

CREATE POLICY tenant_isolation_embeddings ON embeddings
  USING (tenant_id = current_setting('app.tenant_id', true))
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

-- Service-role example (run as a superuser, adapt the role name):
--   CREATE ROLE brain_ingest BYPASSRLS;
--   GRANT brain_ingest TO your_app_user;
--   -- Then ingest jobs `SET ROLE brain_ingest;` before bulk loads.
