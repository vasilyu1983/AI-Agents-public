# PostgreSQL Row-Level Security (RLS) Template

*Purpose: Implement Row-Level Security for multi-tenant applications, data isolation, and fine-grained access control in PostgreSQL databases.*

---

## When to Use RLS

**Use Row-Level Security when:**
- Building multi-tenant SaaS applications
- Enforcing legal entity or regional data isolation
- Implementing role-based data access controls
- Complying with data privacy regulations (GDPR, HIPAA)
- Separating customer data in shared databases
- Implementing organization-level access controls

**Don't use RLS when:**
- Single-tenant applications with simple access needs
- Performance is critical and filtering can be done at application layer
- Schema-based separation is sufficient
- You need cross-tenant queries frequently

---

## 1. RLS Fundamentals

### Basic Concepts

**Row-Level Security (RLS):**
- Database-enforced row filtering on SELECT, INSERT, UPDATE, DELETE
- Applied transparently to all queries
- Cannot be bypassed (even by table owner with FORCE)
- Performance: Uses indexes, part of query plan

**Key Components:**
1. **Enable RLS**: `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`
2. **Policies**: Rules that filter rows based on user/role
3. **FORCE RLS**: Apply policies even to table owner
4. **Roles**: PostgreSQL roles that policies apply to

### Simple Example

```sql
-- Create table
CREATE TABLE tenants_data (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    data TEXT
);

-- Enable RLS
ALTER TABLE tenants_data ENABLE ROW LEVEL SECURITY;

-- Create policy: Users only see their tenant's data
CREATE POLICY tenant_isolation ON tenants_data
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant')::integer);

-- Grant table access
GRANT SELECT ON tenants_data TO app_user;
```

**Using in application:**
```sql
-- Set tenant context (once per connection/transaction)
SET app.current_tenant = '123';

-- Query automatically filtered by policy
SELECT * FROM tenants_data;  -- Only returns tenant_id = 123
```

---

## 2. Policy Types

### SELECT Policies (Read Access)

**Basic SELECT policy:**
```sql
CREATE POLICY tenant_read ON customers
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

**Role-based SELECT:**
```sql
-- Admin sees everything
CREATE POLICY admin_read_all ON customers
    FOR SELECT
    TO admin_role
    USING (true);

-- Regular users see only their tenant
CREATE POLICY user_read_tenant ON customers
    FOR SELECT
    TO app_user
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

**Time-based access:**
```sql
CREATE POLICY historical_data_read ON transactions
    FOR SELECT
    USING (
        transaction_date >= CURRENT_DATE - INTERVAL '7 years'
        OR status IN ('pending', 'disputed')
    );
```

### INSERT Policies (Create Access)

**Enforce tenant on INSERT:**
```sql
CREATE POLICY tenant_insert ON customers
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::uuid);
```

**Prevent certain inserts:**
```sql
CREATE POLICY no_future_dates ON transactions
    FOR INSERT
    WITH CHECK (transaction_date <= CURRENT_DATE);
```

### UPDATE Policies (Modify Access)

**Allow updates only to own tenant:**
```sql
CREATE POLICY tenant_update ON customers
    FOR UPDATE
    USING (tenant_id = current_setting('app.current_tenant')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::uuid);
```

**Prevent modification of audit fields:**
```sql
CREATE POLICY protect_audit_fields ON customers
    FOR UPDATE
    USING (true)
    WITH CHECK (
        created_at = (SELECT created_at FROM customers WHERE id = customers.id)
        AND created_by = (SELECT created_by FROM customers WHERE id = customers.id)
    );
```

### DELETE Policies (Remove Access)

**Allow deletion only of own tenant data:**
```sql
CREATE POLICY tenant_delete ON customers
    FOR DELETE
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

**Soft delete only:**
```sql
CREATE POLICY soft_delete_only ON customers
    FOR DELETE
    USING (false);  -- Prevent hard deletes entirely
```

### ALL Operations Policy

**Single policy for all operations:**
```sql
CREATE POLICY tenant_full_access ON customers
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::uuid);
```

---

## 3. Multi-Tenant Patterns

### Pattern 1: Tenant ID Column

**Most common pattern:**

```sql
-- Table design
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL,
    customer_name TEXT,
    amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_orders_tenant_id ON orders(tenant_id);

-- Enable RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders FORCE ROW LEVEL SECURITY;

-- Policy
CREATE POLICY tenant_isolation ON orders
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Grant access
GRANT SELECT, INSERT, UPDATE, DELETE ON orders TO app_user;
```

**Application code (Node.js example):**
```javascript
// Set tenant context at start of request
async function setTenantContext(client, tenantId) {
    await client.query('SET app.current_tenant_id = $1', [tenantId]);
}

// All queries automatically filtered
app.get('/orders', async (req, res) => {
    const client = await pool.connect();
    try {
        await setTenantContext(client, req.user.tenantId);
        const result = await client.query('SELECT * FROM orders');
        res.json(result.rows);  // Only this tenant's orders
    } finally {
        client.release();
    }
});
```

### Pattern 2: Organization Hierarchy

**Multi-level organization access:**

```sql
-- Table with org hierarchy
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL,
    parent_org_id INTEGER,  -- NULL for top-level orgs
    content TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Function to get org hierarchy
CREATE OR REPLACE FUNCTION get_accessible_orgs(root_org_id INTEGER)
RETURNS TABLE(org_id INTEGER) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE org_tree AS (
        SELECT root_org_id AS org_id
        UNION
        SELECT o.org_id
        FROM organizations o
        JOIN org_tree ot ON o.parent_org_id = ot.org_id
    )
    SELECT * FROM org_tree;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Policy with hierarchy
CREATE POLICY org_hierarchy_access ON documents
    FOR SELECT
    USING (
        org_id IN (
            SELECT get_accessible_orgs(
                current_setting('app.current_org_id')::integer
            )
        )
    );
```

### Pattern 3: Legal Entity Isolation

**Regional/legal entity separation (from your codebase):**

```sql
-- Table with legal entity
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    full_name TEXT,
    legal_entity TEXT NOT NULL,  -- 'CY-CBC', 'UK-FCA', 'US-FinCEN'
    country TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_users_legal_entity ON users(legal_entity);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;

-- Full access roles
CREATE POLICY admin_full_access ON users
    FOR ALL
    TO data_engineer, fincrime
    USING (true)
    WITH CHECK (true);

-- EU role: Only CY-CBC entity
CREATE POLICY eu_access ON users
    FOR SELECT
    TO eu_role
    USING (legal_entity = 'CY-CBC');

-- UK role: Only UK-FCA entity
CREATE POLICY uk_access ON users
    FOR SELECT
    TO uk_role
    USING (legal_entity = 'UK-FCA');

-- Grants
GRANT SELECT ON users TO eu_role, uk_role;
GRANT ALL ON users TO data_engineer, fincrime;
```

### Pattern 4: User-Level Access

**Individual user data isolation:**

```sql
-- User preferences table
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY,
    theme TEXT,
    language TEXT,
    notifications_enabled BOOLEAN
);

-- Policy: Users only see their own preferences
CREATE POLICY own_preferences ON user_preferences
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::integer)
    WITH CHECK (user_id = current_setting('app.current_user_id')::integer);

-- Admin override
CREATE POLICY admin_all_preferences ON user_preferences
    FOR ALL
    TO admin_role
    USING (true)
    WITH CHECK (true);
```

---

## 4. Performance Optimization

### Index Strategy

**Critical: Index RLS filter columns**

```sql
-- Single-column index
CREATE INDEX idx_orders_tenant_id ON orders(tenant_id);

-- Composite index for common queries
CREATE INDEX idx_orders_tenant_date ON orders(tenant_id, created_at);

-- Partial index for active data
CREATE INDEX idx_active_orders_tenant
    ON orders(tenant_id, created_at)
    WHERE status IN ('pending', 'processing');
```

### Query Planning

**Verify RLS uses indexes:**

```sql
-- Set tenant context
SET app.current_tenant_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';

-- Check query plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE created_at > '2024-01-01';

-- Should see:
-- Index Scan using idx_orders_tenant_date
--   Index Cond: (tenant_id = '...' AND created_at > ...)
```

**Bad plan (missing index):**
```
Seq Scan on orders
  Filter: (tenant_id = '...')
  Rows Removed by Filter: 9,999,000
```

**Good plan (with index):**
```
Index Scan using idx_orders_tenant_id
  Index Cond: (tenant_id = '...')
  Rows: 1000
```

### Statistics and Vacuum

**Maintain statistics for RLS columns:**

```sql
-- Increase statistics target for tenant column
ALTER TABLE orders ALTER COLUMN tenant_id SET STATISTICS 1000;

-- Analyze after loading data
ANALYZE orders;

-- Regular vacuum/analyze
VACUUM ANALYZE orders;
```

### Connection Pooling Considerations

**Reset session variables between requests:**

```javascript
// Using pg (Node.js)
pool.on('connect', (client) => {
    // Reset all session variables on connection reuse
    client.query('RESET ALL');
});

// Or explicitly reset
async function resetSession(client) {
    await client.query('RESET app.current_tenant_id');
}
```

**Use transaction-level settings:**

```sql
-- Set for transaction only (safer in pooled connections)
BEGIN;
SET LOCAL app.current_tenant_id = 'abc-123';
-- ... queries ...
COMMIT;  -- Setting automatically cleared
```

---

## 5. Security Best Practices

### FORCE Row-Level Security

**Always use FORCE for production tables:**

```sql
-- Enable RLS
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- FORCE applies policies even to table owner
ALTER TABLE sensitive_data FORCE ROW LEVEL SECURITY;
```

**Why FORCE?**
- Table owner bypasses policies by default
- Application role might have ownership
- Migration scripts might run as owner
- FORCE ensures policies ALWAYS apply

### Bypass RLS Safely

**Create dedicated bypass role:**

```sql
-- Create role that can bypass RLS (for admin/migrations)
CREATE ROLE rls_bypass WITH LOGIN PASSWORD 'strong_password';
GRANT ALL ON ALL TABLES IN SCHEMA public TO rls_bypass;

-- Explicitly grant bypass
ALTER ROLE rls_bypass SET row_security = OFF;

-- Or per-table
GRANT ALL ON sensitive_data TO rls_bypass;
-- Bypass role is table owner or has BYPASSRLS attribute
```

**BYPASSRLS attribute:**

```sql
-- Superuser only
ALTER ROLE admin_user BYPASSRLS;

-- Check which roles can bypass
SELECT rolname, rolbypassrls
FROM pg_roles
WHERE rolbypassrls = true;
```

### Audit RLS Access

**Log policy evaluations:**

```sql
-- Enable statement logging
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();

-- Create audit table
CREATE TABLE rls_audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_name TEXT,
    tenant_id TEXT,
    table_name TEXT,
    operation TEXT,
    timestamp TIMESTAMP DEFAULT now()
);

-- Trigger to log access
CREATE OR REPLACE FUNCTION audit_rls_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO rls_audit_log (user_name, tenant_id, table_name, operation)
    VALUES (
        current_user,
        current_setting('app.current_tenant_id', true),
        TG_TABLE_NAME,
        TG_OP
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_customers_access
    AFTER INSERT OR UPDATE OR DELETE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION audit_rls_access();
```

### Policy Conflicts

**Multiple policies are combined with OR:**

```sql
-- Policy 1: See own tenant
CREATE POLICY tenant_access ON data
    FOR SELECT USING (tenant_id = current_setting('app.tenant')::int);

-- Policy 2: Admins see all
CREATE POLICY admin_access ON data
    FOR SELECT TO admin_role USING (true);

-- Result: Regular users see own tenant, admins see all
```

**Use RESTRICTIVE for AND logic:**

```sql
-- Default: PERMISSIVE (OR logic)
CREATE POLICY tenant_access ON data FOR SELECT USING (...);

-- RESTRICTIVE (AND logic - all must pass)
CREATE POLICY no_deleted_records ON data FOR SELECT
    USING (deleted_at IS NULL)
    AS RESTRICTIVE;

-- Both must be true: tenant match AND not deleted
```

---

## 6. Testing RLS Policies

### Manual Testing

```sql
-- Create test role
CREATE ROLE test_user WITH LOGIN PASSWORD 'test123';
GRANT SELECT ON orders TO test_user;

-- Set tenant context and test
\c dbname test_user
SET app.current_tenant_id = 'test-tenant-123';
SELECT * FROM orders;  -- Should only see test-tenant-123 data

-- Verify isolation
SET app.current_tenant_id = 'other-tenant-456';
SELECT * FROM orders;  -- Should see different data
```

### Automated Testing

**SQL test script:**

```sql
-- Test tenant isolation
DO $$
DECLARE
    tenant1_count INTEGER;
    tenant2_count INTEGER;
BEGIN
    -- Set to tenant 1
    PERFORM set_config('app.current_tenant_id', 'tenant-1', false);
    SELECT COUNT(*) INTO tenant1_count FROM orders;

    -- Set to tenant 2
    PERFORM set_config('app.current_tenant_id', 'tenant-2', false);
    SELECT COUNT(*) INTO tenant2_count FROM orders;

    -- Verify different counts
    IF tenant1_count = tenant2_count THEN
        RAISE EXCEPTION 'RLS policy not working: same count for different tenants';
    END IF;

    RAISE NOTICE 'RLS test passed: tenant1=%, tenant2=%', tenant1_count, tenant2_count;
END $$;
```

**Application test (Jest example):**

```javascript
describe('RLS Policies', () => {
    it('should isolate tenant data', async () => {
        // Tenant 1
        const client1 = await pool.connect();
        await client1.query('SET app.current_tenant_id = $1', ['tenant-1']);
        const result1 = await client1.query('SELECT * FROM orders');

        // Tenant 2
        const client2 = await pool.connect();
        await client2.query('SET app.current_tenant_id = $1', ['tenant-2']);
        const result2 = await client2.query('SELECT * FROM orders');

        // Verify no overlap
        const ids1 = result1.rows.map(r => r.id);
        const ids2 = result2.rows.map(r => r.id);
        const overlap = ids1.filter(id => ids2.includes(id));

        expect(overlap).toHaveLength(0);

        client1.release();
        client2.release();
    });
});
```

### Policy Validation Checklist

- [ ] Policies prevent cross-tenant data access
- [ ] INSERT policies enforce correct tenant_id
- [ ] UPDATE policies prevent tenant_id changes
- [ ] DELETE policies respect tenant boundaries
- [ ] Admin roles can bypass when needed
- [ ] Indexes exist on policy columns
- [ ] FORCE RLS enabled on all tables
- [ ] Session variables properly set/reset
- [ ] Performance acceptable (query plans checked)
- [ ] Audit logging captures access

---

## 7. Common Pitfalls

### Pitfall 1: Missing Indexes

**Problem:**
```sql
-- RLS policy without index
CREATE POLICY tenant_filter ON large_table
    USING (tenant_id = current_setting('app.tenant')::uuid);

-- Results in sequential scan
EXPLAIN SELECT * FROM large_table;  -- Seq Scan (slow!)
```

**Solution:**
```sql
-- Create index first
CREATE INDEX idx_large_table_tenant ON large_table(tenant_id);

-- Now uses index
EXPLAIN SELECT * FROM large_table;  -- Index Scan (fast!)
```

### Pitfall 2: Forgetting FORCE

**Problem:**
```sql
ALTER TABLE data ENABLE ROW LEVEL SECURITY;
-- Owner/superuser bypasses policies!
```

**Solution:**
```sql
ALTER TABLE data ENABLE ROW LEVEL SECURITY;
ALTER TABLE data FORCE ROW LEVEL SECURITY;
-- Now policies apply to everyone
```

### Pitfall 3: Connection Pool Leakage

**Problem:**
```sql
-- Connection 1
SET app.tenant_id = 'tenant-A';
-- ... queries for tenant A ...
-- Connection released to pool

-- Connection 2 (reuses same connection)
-- Still has tenant_id = 'tenant-A'!
-- Queries return wrong tenant's data
```

**Solution:**
```javascript
// Reset on acquire
pool.on('connect', (client) => {
    client.query('RESET ALL');
});

// Or use transaction-local
await client.query('BEGIN');
await client.query('SET LOCAL app.tenant_id = $1', [tenantId]);
// ... queries ...
await client.query('COMMIT');  // LOCAL settings cleared
```

### Pitfall 4: NULL Tenant IDs

**Problem:**
```sql
-- Policy allows NULL to match anything
CREATE POLICY tenant_filter ON data
    USING (tenant_id = current_setting('app.tenant', true)::uuid);
-- current_setting returns NULL if not set
-- NULL = NULL is NULL (not true), but might allow unintended access
```

**Solution:**
```sql
-- Explicit NULL handling
CREATE POLICY tenant_filter ON data
    USING (
        tenant_id IS NOT NULL
        AND tenant_id = current_setting('app.tenant')::uuid
    );

-- Or fail-safe default
CREATE POLICY tenant_filter ON data
    USING (
        tenant_id = COALESCE(
            current_setting('app.tenant', true),
            '00000000-0000-0000-0000-000000000000'
        )::uuid
    );
```

### Pitfall 5: Policy Ordering

**Problem:**
```sql
-- Permissive policies combined with OR
CREATE POLICY see_own ON data USING (owner_id = current_user_id());
CREATE POLICY see_public ON data USING (is_public = true);
-- User sees: own records OR public records (both!)
```

**If you want AND:**
```sql
-- Use RESTRICTIVE for AND logic
CREATE POLICY must_be_active ON data
    USING (deleted_at IS NULL)
    AS RESTRICTIVE;  -- Must be true for all queries
```

---

## 8. Migration Strategy

### Adding RLS to Existing Tables

**Step-by-step migration:**

```sql
-- 1. Analyze current access patterns
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 2. Add tenant_id column (if missing)
ALTER TABLE orders ADD COLUMN tenant_id UUID;

-- 3. Backfill tenant_id
UPDATE orders SET tenant_id =
    (SELECT tenant_id FROM customers WHERE customers.id = orders.customer_id);

-- 4. Make NOT NULL
ALTER TABLE orders ALTER COLUMN tenant_id SET NOT NULL;

-- 5. Create index
CREATE INDEX CONCURRENTLY idx_orders_tenant ON orders(tenant_id);

-- 6. Create policies (but don't enable yet)
CREATE POLICY tenant_isolation ON orders
    FOR ALL
    USING (tenant_id = current_setting('app.tenant')::uuid)
    WITH CHECK (tenant_id = current_setting('app.tenant')::uuid);

-- 7. Test in non-production environment first!

-- 8. Enable RLS (during maintenance window)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders FORCE ROW LEVEL SECURITY;

-- 9. Monitor and verify
```

### Gradual Rollout

**Phase 1: Read-only RLS (safe to test)**
```sql
-- Only filter SELECTs, allow all writes
CREATE POLICY read_isolation ON data
    FOR SELECT
    USING (tenant_id = current_setting('app.tenant')::uuid);

-- Allow all inserts/updates/deletes
CREATE POLICY write_permissive ON data
    FOR INSERT, UPDATE, DELETE
    USING (true)
    WITH CHECK (true);
```

**Phase 2: Full RLS**
```sql
-- Drop permissive write policy
DROP POLICY write_permissive ON data;

-- Add proper write policies
CREATE POLICY write_isolation ON data
    FOR INSERT, UPDATE, DELETE
    USING (tenant_id = current_setting('app.tenant')::uuid)
    WITH CHECK (tenant_id = current_setting('app.tenant')::uuid);
```

---

## 9. Monitoring and Troubleshooting

### Check RLS Status

```sql
-- List tables with RLS enabled
SELECT
    schemaname,
    tablename,
    rowsecurity,  -- RLS enabled
    relforcerowsecurity  -- FORCE enabled
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE schemaname = 'public';

-- List all policies
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,  -- PERMISSIVE or RESTRICTIVE
    roles,
    cmd,  -- SELECT, INSERT, UPDATE, DELETE, ALL
    qual,  -- USING expression
    with_check  -- WITH CHECK expression
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

### Debug Policy Issues

```sql
-- Check current session settings
SHOW app.current_tenant_id;
SELECT current_setting('app.current_tenant_id', true);

-- Check user's role memberships
SELECT
    r.rolname,
    ARRAY_AGG(m.rolname) as member_of
FROM pg_roles r
LEFT JOIN pg_auth_members am ON r.oid = am.member
LEFT JOIN pg_roles m ON am.roleid = m.oid
WHERE r.rolname = current_user
GROUP BY r.rolname;

-- Test policy manually
SELECT * FROM orders
WHERE tenant_id = current_setting('app.current_tenant_id')::uuid;
-- Should match policy logic
```

### Performance Monitoring

```sql
-- Identify slow queries with RLS
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
WHERE query LIKE '%tenant_id%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,  -- Number of index scans
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename IN ('orders', 'customers', 'users')
ORDER BY idx_scan DESC;
```

---

## 10. Real-World Examples

### Example 1: SaaS Multi-Tenant Application

```sql
-- Schema design
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    plan TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE documents (
    document_id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Indexes
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_documents_tenant ON documents(tenant_id);
CREATE INDEX idx_documents_user ON documents(user_id);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY tenant_users ON users
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::uuid)
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_documents ON documents
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::uuid)
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);

-- Application role
CREATE ROLE saas_app WITH LOGIN PASSWORD 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON users, documents TO saas_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO saas_app;
```

### Example 2: Healthcare Data (HIPAA Compliance)

```sql
-- Patient data with access control
CREATE TABLE patients (
    patient_id BIGSERIAL PRIMARY KEY,
    mrn TEXT UNIQUE NOT NULL,  -- Medical Record Number
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    ssn TEXT,  -- Encrypted
    facility_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE patient_access_log (
    log_id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT REFERENCES patients,
    accessed_by TEXT,
    access_time TIMESTAMP DEFAULT now(),
    access_reason TEXT
);

-- Enable RLS
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients FORCE ROW LEVEL SECURITY;

-- Policies
-- Doctors see patients in their facility
CREATE POLICY doctor_facility_access ON patients
    FOR SELECT
    TO doctor_role
    USING (
        facility_id = current_setting('app.user_facility_id')::integer
    );

-- Nurses see only assigned patients
CREATE POLICY nurse_assigned_patients ON patients
    FOR SELECT
    TO nurse_role
    USING (
        patient_id IN (
            SELECT patient_id FROM patient_assignments
            WHERE nurse_id = current_setting('app.user_id')::integer
            AND assignment_date = CURRENT_DATE
        )
    );

-- Admins see all (but log access)
CREATE POLICY admin_all_patients ON patients
    FOR SELECT
    TO admin_role
    USING (true);

-- Audit trigger
CREATE OR REPLACE FUNCTION log_patient_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO patient_access_log (patient_id, accessed_by, access_reason)
    VALUES (
        NEW.patient_id,
        current_user,
        current_setting('app.access_reason', true)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_patient_access
    AFTER SELECT ON patients
    FOR EACH ROW
    EXECUTE FUNCTION log_patient_access();
```

### Example 3: Financial Services (Multi-Entity)

```sql
-- From your real codebase pattern
CREATE TABLE transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency TEXT NOT NULL,
    legal_entity TEXT NOT NULL,  -- 'CY-CBC', 'UK-FCA', 'US-FinCEN'
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_transactions_legal_entity ON transactions(legal_entity);
CREATE INDEX idx_transactions_user_entity ON transactions(user_id, legal_entity);

-- Enable RLS
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions FORCE ROW LEVEL SECURITY;

-- Full access roles
CREATE POLICY data_engineer_full ON transactions
    FOR ALL
    TO data_engineer
    USING (true)
    WITH CHECK (true);

CREATE POLICY fincrime_full ON transactions
    FOR SELECT
    TO fincrime
    USING (true);

-- Regional roles
CREATE POLICY eu_entity_only ON transactions
    FOR SELECT
    TO eu_role
    USING (legal_entity = 'CY-CBC');

CREATE POLICY uk_entity_only ON transactions
    FOR SELECT
    TO uk_role
    USING (legal_entity = 'UK-FCA');

CREATE POLICY us_entity_only ON transactions
    FOR SELECT
    TO us_role
    USING (legal_entity = 'US-FinCEN');

-- Finance role: All entities, completed transactions only
CREATE POLICY finance_completed ON transactions
    FOR SELECT
    TO finance_role
    USING (status = 'completed');
```

---

## 11. Related Resources

**PostgreSQL Documentation:**
- [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [CREATE POLICY](https://www.postgresql.org/docs/current/sql-createpolicy.html)
- [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)

**Related Templates:**
- [template-security-audit.md](../cross-platform/template-security-audit.md) - Security audit checklist
- [template-pg-index.md](template-pg-index.md) - PostgreSQL indexing
- [template-pg-explain.md](template-pg-explain.md) - Query optimization

**For SQLMesh-specific RLS:**
- See [template-sqlmesh-security.md](../../../data-lake-platform/assets/transformation/sqlmesh/template-sqlmesh-security.md)

---

## 12. Quick Reference

### Enable RLS
```sql
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;
ALTER TABLE table_name FORCE ROW LEVEL SECURITY;
```

### Create Policy
```sql
CREATE POLICY policy_name ON table_name
    FOR operation  -- SELECT, INSERT, UPDATE, DELETE, ALL
    TO role_name   -- Optional
    USING (condition)  -- For SELECT, UPDATE, DELETE
    WITH CHECK (condition);  -- For INSERT, UPDATE
```

### Check RLS Status
```sql
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
SELECT * FROM pg_policies WHERE schemaname = 'public';
```

### Test Policy
```sql
SET app.tenant_id = 'test-value';
SELECT * FROM table_name;  -- Filtered by policy
```

### Disable RLS (Temporary)
```sql
ALTER TABLE table_name DISABLE ROW LEVEL SECURITY;
-- Or use bypass role with BYPASSRLS attribute
```

---

Use RLS to build secure, multi-tenant applications with database-enforced access controls.
