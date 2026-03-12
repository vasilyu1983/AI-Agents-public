# SQLMesh Security & Compliance Template

*Purpose: Implement production-grade security patterns including Row-Level Security (RLS), PII masking, access control, and compliance requirements in SQLMesh projects.*

---

## When to Use

Use this template for:
- Implementing Row-Level Security (RLS) policies
- PII/sensitive data masking and protection
- Multi-tenant data isolation (by legal entity, region, organization)
- Role-based access control (RBAC)
- Compliance requirements (GDPR, HIPAA, SOC2, fintech regulations)
- Security-hardened views and tables

---

## 1. Row-Level Security (RLS)

### Basic RLS Implementation

**For TABLE models:**
```sql
MODEL (
  name public.users,
  kind FULL,
  audits (unique_values(columns := user_id))
);

SELECT
  user_id,
  email,
  full_name,
  legal_entity,  -- Key field for RLS filtering
  region,
  created_at
FROM intermediate.users;

JINJA_STATEMENT_BEGIN;
-- Enable RLS on the table
ALTER TABLE {{ this_model }} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {{ this_model }} FORCE ROW LEVEL SECURITY;

-- Full access roles
CREATE POLICY rls_data_engineer_all ON {{ this_model }}
  FOR ALL TO data_engineer USING (true) WITH CHECK (true);

CREATE POLICY rls_fincrime_select ON {{ this_model }}
  FOR SELECT TO fincrime USING (true);

-- Restricted access by legal entity
CREATE POLICY rls_eu_select ON {{ this_model }}
  FOR SELECT TO eu USING (legal_entity = 'CY-CBC');

CREATE POLICY rls_uk_select ON {{ this_model }}
  FOR SELECT TO uk USING (legal_entity = 'UK-FCA');

-- Drop existing policies on re-apply
DROP POLICY IF EXISTS rls_data_engineer_all ON {{ this_model }};
DROP POLICY IF EXISTS rls_fincrime_select ON {{ this_model }};
DROP POLICY IF EXISTS rls_eu_select ON {{ this_model }};
DROP POLICY IF EXISTS rls_uk_select ON {{ this_model }};
JINJA_END;
```

### Multi-Dimensional RLS

**Filter by multiple attributes:**
```sql
JINJA_STATEMENT_BEGIN;
ALTER TABLE {{ this_model }} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {{ this_model }} FORCE ROW LEVEL SECURITY;

-- Regional analyst: Only EU region AND active users
CREATE POLICY rls_eu_analyst_select ON {{ this_model }}
  FOR SELECT TO eu_analyst
  USING (region = 'EU' AND status = 'active');

-- Finance team: Only completed transactions
CREATE POLICY rls_finance_select ON {{ this_model }}
  FOR SELECT TO finance
  USING (transaction_status = 'completed' AND amount > 0);

-- Compliance: All data but masked PII (handled by view layer)
CREATE POLICY rls_compliance_select ON {{ this_model }}
  FOR SELECT TO compliance
  USING (true);
JINJA_END;
```

### RLS Pattern Decision Matrix

| Use Case | Pattern | Example |
|----------|---------|---------|
| Multi-tenant SaaS | Filter by tenant_id | `USING (tenant_id = current_setting('app.tenant_id')::uuid)` |
| Regional compliance | Filter by region/legal_entity | `USING (legal_entity = 'CY-CBC')` |
| Role-based | Filter by data classification | `USING (sensitivity_level <= current_user_clearance_level())` |
| Time-based | Filter by date ranges | `USING (created_at >= current_user_data_access_start())` |

---

## 2. PII Masking with Python Macros

### Creating Python Macros

**File: sqlmesh/macros/mask_name.py**
```python
from sqlmesh import macro

@macro()
def mask_name(evaluator, name_col: str):
    """
    Mask a name by showing only first character of each word.
    Example: "John Smith" -> "J*** S*****"
    """
    return f"""(
        SELECT array_to_string(
            array_agg(
                substring(word from 1 for 1) || repeat('*', char_length(word)-1)
            ), ' '
        )
        FROM unnest(regexp_split_to_array({name_col}, '\\s+')) AS word
    )"""

@macro()
def mask_email(evaluator, email_col: str):
    """
    Mask email: j***@example.com
    """
    return f"""(
        CASE
            WHEN {email_col} ~ '@' THEN
                substring({email_col} from 1 for 1) ||
                repeat('*', GREATEST(position('@' in {email_col}) - 2, 3)) ||
                substring({email_col} from position('@' in {email_col}))
            ELSE {email_col}
        END
    )"""

@macro()
def purse_seven(evaluator, purse_id: str):
    """
    Format wallet/purse ID to 7 digits with leading zeros.
    Example: "123" -> "0000123"
    """
    return f"REPLACE(LPAD({purse_id}::TEXT, 7, '0'), ' ', '0')"
```

**File: sqlmesh/macros/mask_field_details.py**
```python
from sqlmesh import macro

@macro()
def mask_field_detail(evaluator, details_col: str, field_label: str):
    """
    Mask specific fields in semicolon-delimited detail strings.
    Example: "SenderName: John Smith; Amount: 100"
          -> "SenderName: J*** S*****; Amount: 100"
    """
    return f"""(
        SELECT string_agg(
            CASE
                WHEN split_part(detail, ': ', 1) = '{field_label}' THEN
                    split_part(detail, ': ', 1) || ': ' ||
                    (SELECT array_to_string(
                        array_agg(
                            substring(word from 1 for 1) || repeat('*', char_length(word)-1)
                        ), ' '
                    ) FROM unnest(regexp_split_to_array(split_part(detail, ': ', 2), '\\s+')) AS word)
                ELSE detail
            END,
            '; '
        )
        FROM unnest(string_to_array({details_col}, '; ')) AS detail
    )"""

@macro()
def mask_numbers(evaluator, text_col: str, mask_char: str = 'X'):
    """
    Mask numbers in text while preserving structure.
    Example: "Card 1234-5678-9012-3456" -> "Card XXXX-XXXX-XXXX-3456"
    """
    return f"""regexp_replace(
        {text_col},
        '\\d(?=\\d{{0,3}}\\D*$)',
        '{mask_char}',
        'g'
    )"""
```

### Using Macros in Models

**Public view with PII masking:**
```sql
MODEL (
  name public_limited.users_personal,
  kind VIEW,
  description 'User personal information with PII protection'
);

SELECT
  user_id,
  @mask_name(full_name) AS masked_name,
  @mask_email(email) AS masked_email,
  @mask_numbers(phone_number) AS masked_phone,
  @mask_field_detail(additional_details, 'Address') AS masked_details,
  country,
  created_at
FROM intermediate.users
WHERE user_id IS NOT NULL;
```

**Conditional masking based on role:**
```sql
MODEL (
  name public.transactions_secure,
  kind VIEW
);

SELECT
  transaction_id,
  user_id,
  -- Mask cardholder name for non-finance roles
  CASE
    WHEN current_user IN ('finance', 'compliance') THEN cardholder_name
    ELSE @mask_name(cardholder_name)
  END AS cardholder_name,
  -- Always mask full card number
  @mask_numbers(card_number) AS masked_card_number,
  amount,
  currency,
  transaction_date
FROM intermediate.transactions;
```

---

## 3. Security-Hardened Views

### ON_VIRTUAL_UPDATE Blocks

**For VIEW models with security requirements:**
```sql
MODEL (
  name public.users,
  kind VIEW,
  description 'Public user data with security controls'
);

SELECT * FROM intermediate.users;

ON_VIRTUAL_UPDATE_BEGIN;
-- Security invoker: Execute with caller's privileges (not definer's)
ALTER VIEW @this_model SET (security_invoker = true);

-- Security barrier: Prevent information leakage through query planning
ALTER VIEW @this_model SET (security_barrier = true);

-- Grant permissions
GRANT SELECT ON @this_model TO common;
GRANT SELECT ON @this_model TO analytics;

-- Revoke from public
REVOKE ALL ON @this_model FROM PUBLIC;
ON_VIRTUAL_UPDATE_END;
```

### Security Options Explained

| Option | Purpose | When to Use |
|--------|---------|-------------|
| `security_invoker = true` | Execute with caller's permissions | Multi-tenant apps, RLS enforcement |
| `security_barrier = true` | Prevent optimization-based info leakage | Views with WHERE clauses hiding sensitive data |
| `FORCE ROW LEVEL SECURITY` | Apply RLS even to table owner | Production tables with strict access control |

---

## 4. Role-Based Access Control (RBAC)

### Role Hierarchy Design

**Create access_rights.md in sqlmesh/ directory:**
```markdown
# Access Rights Documentation

## Role Hierarchy

### Full Access Roles
- **data_engineer**: Full CRUD access to all schemas
  - GRANT: ALL on all tables/views
  - Use: Platform maintenance, schema changes

- **fincrime**: All data for compliance monitoring
  - GRANT: SELECT on all schemas including public_fincrime
  - Use: AML/fraud investigation

### Standard Roles
- **common**: Public schema + sandbox
  - GRANT: SELECT on public.*, sandbox.*
  - Restrictions: No access to _limited or _fincrime schemas

- **common_personal**: common + PII tables
  - GRANT: SELECT on public.*, public_limited.*
  - Use: Customer support, account management

- **common_fin**: common + financial data
  - GRANT: SELECT on public.*, public_fincrime.*
  - Use: Finance team, accounting

### Restricted Roles (Legal Entity-based)
- **eu**: Only CY-CBC (Cyprus) entity data
  - RLS: `legal_entity = 'CY-CBC'`
  - GRANT: SELECT on public.* (filtered by RLS)

- **uk**: Only UK-FCA entity data
  - RLS: `legal_entity = 'UK-FCA'`
  - GRANT: SELECT on public.* (filtered by RLS)

## Schema Access Matrix

| Role | public | public_limited | public_fincrime | sandbox | stage | intermediate |
|------|--------|----------------|-----------------|---------|-------|--------------|
| data_engineer | ALL | ALL | ALL | ALL | ALL | ALL |
| fincrime | SELECT | SELECT | SELECT | - | - | - |
| common | SELECT | - | - | SELECT | - | - |
| common_personal | SELECT | SELECT | - | SELECT | - | - |
| common_fin | SELECT | - | SELECT | SELECT | - | - |
| eu | SELECT (RLS) | SELECT (RLS) | - | - | - | - |
| uk | SELECT (RLS) | SELECT (RLS) | - | - | - | - |

## Applying Roles to Models

Use JINJA blocks to grant permissions:

\`\`\`sql
JINJA_STATEMENT_BEGIN;
-- Common access
GRANT SELECT ON {{ this_model }} TO common;
GRANT SELECT ON {{ this_model }} TO common_personal;

-- Restricted roles (RLS applied)
GRANT SELECT ON {{ this_model }} TO eu;
GRANT SELECT ON {{ this_model }} TO uk;

-- Admin roles
GRANT ALL ON {{ this_model }} TO data_engineer;
JINJA_END;
\`\`\`
```

### Role Assignment Pattern

**In model files:**
```sql
MODEL (
  name public.transactions,
  kind FULL
);

SELECT * FROM intermediate.transactions;

JINJA_STATEMENT_BEGIN;
-- Define RLS policies first
ALTER TABLE {{ this_model }} ENABLE ROW LEVEL SECURITY;

CREATE POLICY rls_common_select ON {{ this_model }}
  FOR SELECT TO common, common_fin
  USING (transaction_status IN ('completed', 'pending'));

CREATE POLICY rls_eu_select ON {{ this_model }}
  FOR SELECT TO eu
  USING (legal_entity = 'CY-CBC' AND transaction_status IN ('completed', 'pending'));

-- Then grant table access
GRANT SELECT ON {{ this_model }} TO common;
GRANT SELECT ON {{ this_model }} TO common_fin;
GRANT SELECT ON {{ this_model }} TO eu;
GRANT ALL ON {{ this_model }} TO data_engineer;
JINJA_END;
```

---

## 5. Layer-Based Security Architecture

### Schema Isolation Pattern

```
sqlmesh/models/
├── stage/              # Raw data - Restricted to data_engineer only
├── intermediate/       # Business logic - No direct access
├── public/            # Public analytics - Role-based access
├── public_limited/    # PII data - Requires common_personal role
├── public_fincrime/   # Compliance data - Requires fincrime role
└── sandbox/           # Experimental - Open access for testing
```

### Access Control by Layer

**stage/ models:**
```sql
MODEL (
  name stage.raw_users,
  kind VIEW
);

SELECT * FROM source_postgres.users;

JINJA_STATEMENT_BEGIN;
-- Only data engineers can access raw data
GRANT SELECT ON @this_model TO data_engineer;
REVOKE ALL ON @this_model FROM PUBLIC;
JINJA_END;
```

**intermediate/ models:**
```sql
MODEL (
  name intermediate.users,
  kind FULL
);

-- Business logic transformations
SELECT
  user_id,
  email,
  full_name,
  -- No PII masking at intermediate layer
  -- Security applied at public layer
FROM stage.raw_users;

JINJA_STATEMENT_BEGIN;
-- No direct grants - only accessible via public layer
REVOKE ALL ON @this_model FROM PUBLIC;
GRANT SELECT ON @this_model TO data_engineer;
JINJA_END;
```

**public/ models:**
```sql
MODEL (
  name public.users,
  kind VIEW
);

SELECT
  user_id,
  email,
  first_name || ' ' || last_name AS full_name,
  country,
  registration_date
FROM intermediate.users;

JINJA_STATEMENT_BEGIN;
ALTER VIEW @this_model SET (security_invoker = true);
GRANT SELECT ON @this_model TO common;
GRANT SELECT ON @this_model TO eu;
GRANT SELECT ON @this_model TO uk;
JINJA_END;
```

**public_limited/ models:**
```sql
MODEL (
  name public_limited.users_personal,
  kind VIEW
);

SELECT
  user_id,
  full_name,  -- Unmasked
  email,      -- Unmasked
  phone_number,
  address,
  date_of_birth
FROM intermediate.users;

JINJA_STATEMENT_BEGIN;
ALTER VIEW @this_model SET (security_invoker = true);
-- Only roles with personal data access
GRANT SELECT ON @this_model TO common_personal;
GRANT SELECT ON @this_model TO fincrime;
GRANT SELECT ON @this_model TO data_engineer;
JINJA_END;
```

---

## 6. Compliance Patterns

### GDPR Right to be Forgotten

**Soft delete pattern:**
```sql
MODEL (
  name public.users,
  kind VIEW
);

SELECT
  user_id,
  CASE
    WHEN deleted_at IS NOT NULL THEN NULL
    ELSE email
  END AS email,
  CASE
    WHEN deleted_at IS NOT NULL THEN 'DELETED'
    ELSE full_name
  END AS full_name,
  -- Preserve non-PII for analytics
  country,
  registration_date,
  deleted_at
FROM intermediate.users;
```

### Data Retention Policies

**Time-based filtering:**
```sql
MODEL (
  name public.transactions_recent,
  kind VIEW,
  description 'Transactions within data retention period (7 years)'
);

SELECT *
FROM intermediate.transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 years'
  OR transaction_status IN ('pending', 'disputed');

JINJA_STATEMENT_BEGIN;
COMMENT ON VIEW {{ this_model }} IS
  'Data retention: 7 years per financial regulations.
   Older data archived to cold storage.';
JINJA_END;
```

### Audit Logging Pattern

**Track data access:**
```sql
MODEL (
  name public.sensitive_transactions,
  kind VIEW
);

SELECT * FROM intermediate.transactions
WHERE amount > 10000;

JINJA_STATEMENT_BEGIN;
-- Enable audit logging for high-value transactions
ALTER VIEW {{ this_model }} SET (security_invoker = true);

-- Create audit trigger (PostgreSQL)
CREATE OR REPLACE FUNCTION audit_sensitive_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.data_access_log (
        table_name,
        accessed_by,
        accessed_at,
        query_text
    )
    VALUES (
        TG_TABLE_NAME,
        current_user,
        now(),
        current_query()
    );
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_access_trigger
    AFTER SELECT ON {{ this_model }}
    FOR EACH STATEMENT
    EXECUTE FUNCTION audit_sensitive_access();
JINJA_END;
```

---

## 7. Security Checklist

Before deploying models to production:

**Model-Level Security:**
- [ ] RLS policies defined for all role types
- [ ] PII fields masked appropriately
- [ ] `security_invoker = true` set on views with RLS
- [ ] `security_barrier = true` set on views with WHERE filters
- [ ] Permissions granted to appropriate roles only
- [ ] No direct access to intermediate/stage layers

**Macro-Level Security:**
- [ ] Masking macros tested with sample data
- [ ] Edge cases handled (NULL values, empty strings)
- [ ] Performance validated (no cartesian products)
- [ ] Macros versioned and documented

**Infrastructure Security:**
- [ ] Access rights documented in access_rights.md
- [ ] Role hierarchy reviewed and approved
- [ ] Credentials stored in environment variables
- [ ] Connection pooling configured (pgBouncer)
- [ ] SSL/TLS enabled for database connections

**Compliance:**
- [ ] Data retention policies implemented
- [ ] Audit logging enabled for sensitive tables
- [ ] GDPR/CCPA requirements addressed
- [ ] Data classification labels applied
- [ ] Privacy impact assessment completed

---

## 8. Testing Security Controls

### Test RLS Policies

```bash
# Connect as specific role
PGUSER=eu PGPASSWORD=secret psql -h localhost -d dwh

# Verify RLS filtering
SELECT COUNT(*) FROM public.users WHERE legal_entity != 'CY-CBC';
-- Should return 0 rows

# Test role permissions
SELECT * FROM public_limited.users_personal;
-- Should fail with permission denied
```

### Test PII Masking

```sql
-- Verify masking works
SELECT
  full_name,
  @mask_name(full_name) AS masked_name,
  email,
  @mask_email(email) AS masked_email
FROM intermediate.users
LIMIT 10;

-- Expected:
-- full_name: "John Smith"    masked_name: "J*** S*****"
-- email: "john@example.com"  masked_email: "j***@example.com"
```

### Automated Security Tests

**tests/test_security.yaml:**
```yaml
test_rls_enforcement:
  model: public.users
  inputs:
    intermediate.users:
      rows:
        - user_id: 1
          legal_entity: 'CY-CBC'
          email: 'eu@test.com'
        - user_id: 2
          legal_entity: 'UK-FCA'
          email: 'uk@test.com'
  outputs:
    query: |
      SET ROLE eu;
      SELECT * FROM public.users;
    rows:
      - user_id: 1
        legal_entity: 'CY-CBC'
    # Should not include user_id: 2
```

---

## 9. Production Security Patterns

### Multi-Tenant SaaS

```sql
MODEL (
  name public.customer_data,
  kind VIEW
);

SELECT
  tenant_id,
  customer_id,
  customer_name,
  revenue
FROM intermediate.customers;

JINJA_STATEMENT_BEGIN;
ALTER TABLE {{ this_model }} ENABLE ROW LEVEL SECURITY;

-- Use session variable for tenant isolation
CREATE POLICY tenant_isolation ON {{ this_model }}
  FOR ALL
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
JINJA_END;
```

### Dynamic Data Masking

```sql
MODEL (
  name public.customers_masked,
  kind VIEW
);

SELECT
  customer_id,
  -- Mask based on current user's role
  CASE
    WHEN pg_has_role(current_user, 'common_personal', 'member')
      THEN full_name
    ELSE @mask_name(full_name)
  END AS full_name,
  CASE
    WHEN pg_has_role(current_user, 'common_personal', 'member')
      THEN email
    ELSE @mask_email(email)
  END AS email,
  country
FROM intermediate.customers;
```

---

## 10. Common Security Anti-Patterns

**BAD: DON'T:**
```sql
-- Hardcoded credentials
MODEL (
  name stage.external_data,
  kind VIEW
);
SELECT * FROM dblink(
  'host=db.example.com password=hardcoded123 dbname=prod',
  'SELECT * FROM users'
);
```

**GOOD: DO:**
```sql
-- Use environment variables
MODEL (
  name stage.external_data,
  kind VIEW
);
SELECT * FROM dblink(
  'host={{ env_var("DB_HOST") }} password={{ env_var("DB_PASSWORD") }} dbname=prod',
  'SELECT * FROM users'
);
```

**BAD: DON'T:**
```sql
-- Expose PII without masking
MODEL (
  name public.users,
  kind VIEW
);
SELECT * FROM intermediate.users;  -- Includes SSN, DOB, etc.
```

**GOOD: DO:**
```sql
-- Mask PII or use separate limited schema
MODEL (
  name public.users,
  kind VIEW
);
SELECT
  user_id,
  @mask_name(full_name) AS name,
  country,
  registration_date
FROM intermediate.users;
```

---

## Related Resources

- **SQLMesh Model Patterns**: [template-sqlmesh-model.md](template-sqlmesh-model.md)
- **SQLMesh Testing**: [template-sqlmesh-testing.md](template-sqlmesh-testing.md)
- **Database Security**: [template-security-audit.md](../../../../data-sql-optimization/assets/cross-platform/template-security-audit.md)
- **Application Security**: [Software Security AppSec](../../../../software-security-appsec/SKILL.md)

---

Use these patterns to build production-grade, compliant, and secure data pipelines with SQLMesh.
