# SQLMesh Model Definition Template

*Purpose: Create SQL models with proper configuration, materialization strategies, and best practices.*

---

## Model Types

### 1. FULL Model (Complete Refresh)

```sql
MODEL (
  name marts.daily_revenue,
  kind FULL,
  cron '@daily',
  grain [date]
);

SELECT
  DATE(order_date) AS date,
  SUM(order_total) AS total_revenue,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM staging.stg_orders
WHERE status = 'completed'
GROUP BY 1;
```

**Use when:**
- Small tables (< 1M rows)
- Fast computation (<1 min)
- No need for history

---

### 2. INCREMENTAL_BY_TIME_RANGE (Recommended)

```sql
MODEL (
  name intermediate.int_enriched_orders,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column order_date
  ),
  start '2024-01-01',
  cron '@daily',
  grain [order_id]
);

SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  o.order_total,
  c.customer_segment,
  p.product_category
FROM staging.stg_orders o
LEFT JOIN staging.stg_customers c ON o.customer_id = c.customer_id
LEFT JOIN staging.stg_products p ON o.product_id = p.product_id
WHERE
  o.order_date BETWEEN @start_date AND @end_date;
```

**Use when:**
- Large tables
- Time-series data
- Incremental processing needed

---

### 3. INCREMENTAL_BY_UNIQUE_KEY (Upsert)

```sql
MODEL (
  name staging.stg_customers,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key customer_id
  ),
  cron '@hourly',
  grain [customer_id]
);

SELECT
  customer_id,
  email,
  first_name,
  last_name,
  customer_segment,
  created_at,
  updated_at
FROM raw.customers;
```

**Use when:**
- SCD Type 1 (latest snapshot)
- Slowly changing dimensions
- Need to update existing rows

---

### 4. VIEW Model

```sql
MODEL (
  name staging.v_active_customers,
  kind VIEW
);

SELECT *
FROM staging.stg_customers
WHERE status = 'active';
```

**Use when:**
- Lightweight transformations
- No materialization needed
- Fast query execution

---

## Model Configuration Options

### Complete Configuration Example

```sql
MODEL (
  name marts.customer_metrics,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column metric_date
  ),
  start '2023-01-01',
  cron '@daily',
  grain [customer_id, metric_date],
  audits [
    audit_not_null(columns := [customer_id, metric_date]),
    audit_unique_values(columns := [customer_id, metric_date])
  ],
  owner 'data-team',
  tags ['customer', 'metrics', 'daily'],
  description 'Daily customer engagement metrics'
);
```

---

## Common Patterns

### Pattern 1: Deduplication

```sql
WITH deduplicated AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY order_id
      ORDER BY updated_at DESC
    ) AS rn
  FROM raw.orders
  WHERE order_date BETWEEN @start_date AND @end_date
)
SELECT * EXCEPT (rn)
FROM deduplicated
WHERE rn = 1;
```

### Pattern 2: SCD Type 2 (Historical Tracking)

```sql
MODEL (
  name intermediate.int_customer_history,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column valid_from
  ),
  start '2024-01-01',
  cron '@daily'
);

SELECT
  customer_id,
  email,
  customer_segment,
  valid_from,
  COALESCE(
    LEAD(valid_from) OVER (
      PARTITION BY customer_id ORDER BY valid_from
    ),
    '9999-12-31'
  ) AS valid_to
FROM staging.stg_customers
WHERE valid_from BETWEEN @start_date AND @end_date;
```

### Pattern 3: Aggregations with Grain

```sql
MODEL (
  name marts.product_daily_sales,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column sale_date
  ),
  start '2024-01-01',
  cron '@daily',
  grain [product_id, sale_date]
);

SELECT
  product_id,
  DATE(order_date) AS sale_date,
  COUNT(*) AS orders,
  SUM(quantity) AS units_sold,
  SUM(order_total) AS revenue
FROM staging.stg_orders
WHERE
  order_date BETWEEN @start_date AND @end_date
  AND status = 'completed'
GROUP BY 1, 2;
```

### Pattern 4: NOT MATERIALIZED CTEs (PostgreSQL Optimization)

**Use for large models to improve query planning:**

```sql
MODEL (
  name intermediate.transactions_optimized,
  kind FULL,
  grain [transaction_id]
);

-- PostgreSQL: Prevent CTE materialization for better optimization
WITH applications AS NOT MATERIALIZED (
  SELECT
    operation_guid,
    application_type,
    application_os
  FROM intermediate.transaction_applications
),
verification AS NOT MATERIALIZED (
  SELECT DISTINCT ON (vr.user_id)
    vr.user_id,
    vr.status,
    vr.created_date
  FROM stage.verification_requests vr
  ORDER BY vr.user_id, vr.created_date DESC
),
rates AS NOT MATERIALIZED (
  SELECT
    transaction_id,
    rate_eur,
    rate_gbp
  FROM intermediate.currency_rates_daily
)
SELECT
  t.transaction_id,
  t.user_id,
  t.amount,
  a.application_type,
  a.application_os,
  v.status AS verification_status,
  r.rate_eur,
  r.rate_gbp
FROM stage.transactions t
LEFT JOIN applications a ON t.operation_guid = a.operation_guid
LEFT JOIN verification v ON t.user_id = v.user_id
LEFT JOIN rates r ON t.transaction_id = r.transaction_id;
```

**When to use NOT MATERIALIZED:**
- Large models with multiple CTEs
- CTEs used only once in final SELECT
- PostgreSQL only (not supported in other databases)
- Query planner can push down filters/joins
- Performance verified with EXPLAIN ANALYZE

**Performance impact:**
- [OK] Allows join reordering and filter pushdown
- [OK] Can reduce memory usage
- [WARNING] Test both ways - not always faster

### Pattern 5: Latest Record Pattern

**Using DISTINCT ON (PostgreSQL):**
```sql
WITH latest_verification AS (
  SELECT DISTINCT ON (user_id)
    user_id,
    status,
    verification_date,
    risk_score
  FROM stage.verification_requests
  WHERE parent_verification_request_id IS NULL
  ORDER BY user_id, verification_date DESC
)
SELECT * FROM latest_verification;
```

**Using Window Function (Cross-database):**
```sql
WITH ranked_verifications AS (
  SELECT
    user_id,
    status,
    verification_date,
    risk_score,
    ROW_NUMBER() OVER (
      PARTITION BY user_id
      ORDER BY verification_date DESC
    ) as rn
  FROM stage.verification_requests
)
SELECT
  user_id,
  status,
  verification_date,
  risk_score
FROM ranked_verifications
WHERE rn = 1;
```

### Pattern 6: Python Macro Usage

**Formatting and masking with macros:**

```sql
MODEL (
  name public.users,
  kind VIEW
);

SELECT
  user_id,
  @purse_seven(wallet_id) AS formatted_wallet_id,  -- Macro: Format to 7 digits
  @mask_name(full_name) AS masked_name,             -- Macro: Mask PII
  @mask_email(email) AS masked_email,
  country,
  created_at
FROM intermediate.users;
```

**See also:** [template-sqlmesh-security.md](template-sqlmesh-security.md) for complete macro examples

---

## Best Practices Checklist

- [ ] **Model name follows convention** (staging/intermediate/marts prefix)
- [ ] **Kind appropriate** for data volume and update frequency
- [ ] **Grain specified** for incremental models
- [ ] **Time column** for incremental by time range
- [ ] **Start date** set appropriately
- [ ] **Cron schedule** matches business requirements
- [ ] **Audits added** for data quality
- [ ] **Description** provided
- [ ] **Tags** for organization
- [ ] **Owner** assigned

---

## Testing Models

```bash
# Run specific model
sqlmesh run -s marts.daily_revenue

# Run for specific date range
sqlmesh run --start 2024-01-01 --end 2024-01-31

# Plan and preview
sqlmesh plan --select marts.daily_revenue

# Format model
sqlmesh format models/marts/daily_revenue.sql
```

---

## Advanced Features

### ON_VIRTUAL_UPDATE Blocks

**For VIEW models with security or permission requirements:**

```sql
MODEL (
  name public.users,
  kind VIEW,
  description 'Public user data with access controls'
);

SELECT
  user_id,
  email,
  full_name,
  country,
  created_at
FROM intermediate.users;

ON_VIRTUAL_UPDATE_BEGIN;
-- Security invoker: Execute with caller's privileges
ALTER VIEW @this_model SET (security_invoker = true);

-- Security barrier: Prevent information leakage
ALTER VIEW @this_model SET (security_barrier = true);

-- Grant permissions
GRANT SELECT ON @this_model TO common;
GRANT SELECT ON @this_model TO analytics;

-- Revoke from public
REVOKE ALL ON @this_model FROM PUBLIC;
ON_VIRTUAL_UPDATE_END;
```

**When to use ON_VIRTUAL_UPDATE:**
- VIEW models that need security settings
- Applying grants/revokes to views
- Setting view options (security_invoker, security_barrier)
- Any PostgreSQL DDL that affects the view itself

**Not needed for:**
- TABLE models (use JINJA_STATEMENT_BEGIN instead)
- Models without special permissions
- Development/sandbox models

### Index Creation

**Add indexes for query performance:**

```sql
MODEL (
  name public.transactions,
  kind FULL,
  grain [transaction_id]
);

SELECT
  transaction_id,
  user_id,
  creation_date,
  amount,
  currency,
  status
FROM intermediate.transactions;

JINJA_STATEMENT_BEGIN;
-- Primary key index
CREATE INDEX IF NOT EXISTS idx_transactions_transaction_id
  ON {{ this_model }} (transaction_id);

-- Foreign key index
CREATE INDEX IF NOT EXISTS idx_transactions_user_id
  ON {{ this_model }} (user_id);

-- Date range queries
CREATE INDEX IF NOT EXISTS idx_transactions_creation_date
  ON {{ this_model }} (creation_date);

-- Composite index for common query pattern
CREATE INDEX IF NOT EXISTS idx_transactions_user_id_creation_date
  ON {{ this_model }} (user_id, creation_date);

-- Partial index for active transactions
CREATE INDEX IF NOT EXISTS idx_transactions_active
  ON {{ this_model }} (user_id, creation_date)
  WHERE status IN ('pending', 'completed');
JINJA_END;
```

**Index Best Practices:**

1. **Add indexes for:**
   - Primary keys (transaction_id, user_id)
   - Foreign keys (user_id, product_id)
   - WHERE clause columns (status, created_at)
   - ORDER BY columns (created_at, updated_at)
   - JOIN conditions

2. **Composite index column order:**
   - Most selective column first
   - Equality filters before range filters
   - Example: (user_id, created_at) for queries like:
     ```sql
     WHERE user_id = 123 AND created_at > '2024-01-01'
     ```

3. **When NOT to index:**
   - Small tables (< 10,000 rows)
   - High cardinality columns rarely queried
   - Columns with very few distinct values (boolean flags)
   - Heavily updated tables (indexes slow down writes)

4. **PostgreSQL-specific index types:**
```sql
-- B-tree (default) - Most common
CREATE INDEX idx_email ON users (email);

-- GIN for JSONB/arrays
CREATE INDEX idx_metadata_gin ON events USING gin (metadata);

-- GiST for spatial/range queries
CREATE INDEX idx_location_gist ON stores USING gist (location);

-- Partial index
CREATE INDEX idx_active_users ON users (email) WHERE status = 'active';
```

### Documentation Patterns

**Inline field comments (strongly recommended):**

```sql
MODEL (
  name public.users,
  kind FULL,
  description 'User master table with account information and verification status.
               Updated daily. Used by BI dashboards and customer support tools.',
  owner 'data-team',
  tags ['users', 'master', 'pii']
);

SELECT
  user_id,                          -- Unique user identifier (primary key)
  email,                            -- User email address (unique, used for login)
  full_name,                        -- Full legal name from KYC verification
  phone_number,                     -- Phone number with country code
  country_of_residence,             -- ISO 3166-1 alpha-2 country code
  date_of_birth,                    -- Date of birth (YYYY-MM-DD)
  created_at,                       -- Account creation timestamp (UTC)
  verified_at,                      -- KYC verification completion timestamp
  verification_status,              -- Current status: verified|pending|rejected|expired
  risk_score,                       -- Composite risk score (0-100, higher = riskier)
  legal_entity,                     -- Legal entity: CY-CBC|UK-FCA|US-FinCEN
  last_login_at,                    -- Most recent login timestamp
  is_active                         -- Account status: true = active, false = suspended
FROM intermediate.users;
```

**Benefits of inline comments:**
- Self-documenting code
- Helps data consumers understand fields
- Appears in database metadata
- Visible in BI tools and query editors
- Essential for compliance and auditing

**Model description best practices:**
```sql
MODEL (
  name public.customer_360,
  kind FULL,
  description 'Customer 360 view combining user profile, transaction history,
               and engagement metrics.

               **Update frequency:** Daily at 2 AM UTC
               **Data freshness:** T-1 (previous day)
               **Row grain:** One row per customer
               **Dependencies:** intermediate.users, intermediate.transactions,
                               intermediate.engagement_events
               **Use cases:** Customer segmentation, churn analysis, LTV modeling
               **Owner:** Data Analytics Team
               **Last major update:** 2024-11-15 - Added engagement metrics',
  owner 'data-analytics',
  tags ['customer', '360', 'master']
);
```

### JINJA Comments

**Document complex logic:**

```sql
JINJA_STATEMENT_BEGIN;
{#
  Row-Level Security Implementation:

  Purpose: Restrict data access based on user roles and legal entity.

  Policies:
  - data_engineer: Full access (no filtering)
  - fincrime: All records for compliance monitoring
  - eu: Only CY-CBC (Cyprus) entity data
  - uk: Only UK-FCA entity data
  - common: Public data with status filter

  Security considerations:
  - security_barrier = true prevents query plan information leakage
  - FORCE ROW LEVEL SECURITY applies policies to table owner
  - Policies use indexed columns for performance

  Last reviewed: 2024-11-15 by Security Team
#}
ALTER TABLE {{ this_model }} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {{ this_model }} FORCE ROW LEVEL SECURITY;

CREATE POLICY rls_eu_select ON {{ this_model }}
  FOR SELECT TO eu USING (legal_entity = 'CY-CBC');
-- ... more policies
JINJA_END;
```

---

## Complete Example: Production-Ready Model

```sql
MODEL (
  name public.transactions,
  kind FULL,
  cron '@daily',
  grain [transaction_id],
  audits [
    audit_not_null(columns := [transaction_id, user_id, creation_date]),
    audit_unique_values(columns := [transaction_id]),
    audit_accepted_values(column := status, is_in := ['pending', 'completed', 'failed', 'refunded'])
  ],
  owner 'data-team',
  tags ['transactions', 'finance', 'daily'],
  description 'Transaction master table containing all financial transactions
               with enriched user and business context.

               **Update frequency:** Daily at 3 AM UTC
               **Data freshness:** Real-time (< 5 min delay)
               **Row grain:** One row per transaction
               **Use cases:** Revenue reporting, fraud detection, reconciliation'
);

-- NOT MATERIALIZED for better query optimization
WITH user_enrichment AS NOT MATERIALIZED (
  SELECT
    user_id,
    legal_entity,
    country_of_residence,
    risk_score,
    verification_status
  FROM intermediate.users
),
currency_rates AS NOT MATERIALIZED (
  SELECT
    currency_id,
    rate_to_eur,
    rate_to_gbp,
    rate_date
  FROM intermediate.daily_currency_rates
  WHERE rate_date = CURRENT_DATE
)
SELECT
  t.transaction_id,                 -- Unique transaction identifier
  t.user_id,                        -- User who initiated transaction
  t.creation_date,                  -- Transaction creation timestamp (UTC)
  t.amount,                         -- Transaction amount in original currency
  t.currency,                       -- Currency code (ISO 4217)
  t.status,                         -- Transaction status
  t.transaction_type,               -- Type: payment|transfer|withdrawal|deposit
  t.merchant_name,                  -- Merchant name (NULL for P2P)
  t.merchant_category_code,         -- MCC code for categorization
  u.legal_entity,                   -- User's legal entity
  u.country_of_residence,           -- User's country
  u.risk_score,                     -- User risk score at transaction time
  u.verification_status,            -- User KYC status at transaction time
  t.amount * cr.rate_to_eur AS amount_eur,    -- Amount in EUR
  t.amount * cr.rate_to_gbp AS amount_gbp,    -- Amount in GBP
  t.system_created_at               -- System processing timestamp
FROM intermediate.transactions t
LEFT JOIN user_enrichment u ON t.user_id = u.user_id
LEFT JOIN currency_rates cr ON t.currency = cr.currency_id
WHERE t.is_test = false;  -- Exclude test transactions

JINJA_STATEMENT_BEGIN;
-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_transactions_transaction_id
  ON {{ this_model }} (transaction_id);

CREATE INDEX IF NOT EXISTS idx_transactions_user_id
  ON {{ this_model }} (user_id);

CREATE INDEX IF NOT EXISTS idx_transactions_creation_date
  ON {{ this_model }} (creation_date);

CREATE INDEX IF NOT EXISTS idx_transactions_user_date
  ON {{ this_model }} (user_id, creation_date);

CREATE INDEX IF NOT EXISTS idx_transactions_status
  ON {{ this_model }} (status)
  WHERE status IN ('pending', 'failed');

-- Row-Level Security
ALTER TABLE {{ this_model }} ENABLE ROW LEVEL SECURITY;

CREATE POLICY rls_common_select ON {{ this_model }}
  FOR SELECT TO common
  USING (status = 'completed');

CREATE POLICY rls_finance_select ON {{ this_model }}
  FOR SELECT TO finance
  USING (true);

-- Grants
GRANT SELECT ON {{ this_model }} TO common;
GRANT SELECT ON {{ this_model }} TO finance;
GRANT ALL ON {{ this_model }} TO data_engineer;
JINJA_END;
```

---

## Related Templates

- **Security & Compliance**: [template-sqlmesh-security.md](template-sqlmesh-security.md)
- **Production Patterns**: [template-sqlmesh-production.md](template-sqlmesh-production.md)
- **Testing & Audits**: [template-sqlmesh-testing.md](template-sqlmesh-testing.md)
- **Incremental Models**: [template-sqlmesh-incremental.md](template-sqlmesh-incremental.md)
- **DAG Management**: [template-sqlmesh-dag.md](template-sqlmesh-dag.md)
