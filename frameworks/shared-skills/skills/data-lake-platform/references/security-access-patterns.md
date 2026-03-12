# Data Lake Security and Access Patterns

> Purpose: Operational reference for securing data lakes — ACL patterns, row/column-level security, encryption, PII handling, compliance automation, and audit logging. Freshness anchor: Q1 2026.

---

## Decision Tree: Choosing an Access Control Model

```
START: What is your data lake format?
│
├─ Iceberg (on S3/GCS/ADLS)
│   │
│   ├─ Using Databricks? → Unity Catalog (row/column/table ACLs)
│   ├─ Using AWS? → Lake Formation + Iceberg integration
│   ├─ Using Trino/Starburst? → Ranger or OPA policies
│   └─ Using Snowflake? → Snowflake RBAC on external tables
│
├─ Delta Lake
│   │
│   ├─ Databricks → Unity Catalog (native, recommended)
│   └─ Open-source Delta → Ranger or custom IAM
│
├─ Parquet/Hive (legacy)
│   │
│   ├─ AWS → Lake Formation
│   ├─ GCP → BigQuery external tables + IAM
│   └─ On-prem → Ranger + Kerberos
│
└─ Warehouse-native (Snowflake, BigQuery, Redshift)
    └─ Use native RBAC (roles, grants, row access policies)
```

---

## Quick Reference: Security Layers

| Layer | What It Protects | Mechanism | Tools |
|-------|-----------------|-----------|-------|
| Network | Connectivity | VPC, Private Link, firewalls | AWS VPC, Azure VNET |
| Authentication | Identity | SSO, MFA, service accounts | Okta, Azure AD, IAM |
| Authorization | Access to data | RBAC, ABAC, ACLs | Unity Catalog, Lake Formation, Ranger |
| Row-level security | Record visibility | Row access policies, views | Snowflake RLS, BigQuery RLS |
| Column-level security | Field visibility | Column masking, tags | Unity Catalog, dynamic masking |
| Encryption at rest | Storage | AES-256, KMS | AWS KMS, GCP CMEK, Azure Key Vault |
| Encryption in transit | Network | TLS 1.3 | Load balancer config, client cert |
| Audit | Accountability | Access logging | CloudTrail, Unity Catalog audit, BigQuery audit |

---

## ACL Patterns for Iceberg / Delta

### Unity Catalog (Databricks) — Recommended for 2026

```sql
-- Create catalog and schema
CREATE CATALOG IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS analytics.orders;

-- Grant schema-level access
GRANT USE CATALOG ON CATALOG analytics TO `data-analysts`;
GRANT USE SCHEMA ON SCHEMA analytics.orders TO `data-analysts`;
GRANT SELECT ON SCHEMA analytics.orders TO `data-analysts`;

-- Grant table-level access
GRANT SELECT ON TABLE analytics.orders.fct_orders TO `finance-team`;

-- Deny access to specific table
DENY SELECT ON TABLE analytics.orders.raw_pii TO `data-analysts`;

-- Service principal access for pipelines
GRANT ALL PRIVILEGES ON SCHEMA analytics.orders TO `etl-service-principal`;
```

### AWS Lake Formation

```json
{
  "Resource": {
    "Table": {
      "DatabaseName": "analytics",
      "Name": "fct_orders"
    }
  },
  "Permissions": ["SELECT"],
  "Principal": {
    "DataLakePrincipalIdentifier": "arn:aws:iam::123456789:role/data-analyst-role"
  },
  "PermissionsWithGrantOption": []
}
```

### Apache Ranger Policy (Open-source)

```json
{
  "policyType": 0,
  "name": "analytics_read_access",
  "resources": {
    "database": {"values": ["analytics"]},
    "table": {"values": ["fct_*", "dim_*"]},
    "column": {"values": ["*"]}
  },
  "policyItems": [
    {
      "groups": ["data-analysts"],
      "accesses": [{"type": "select", "isAllowed": true}]
    }
  ],
  "denyPolicyItems": [
    {
      "groups": ["data-analysts"],
      "accesses": [{"type": "select", "isAllowed": true}],
      "resources": {
        "column": {"values": ["ssn", "email", "phone"]}
      }
    }
  ]
}
```

---

## Row-Level Security (RLS)

### Snowflake RLS

```sql
-- Create row access policy
CREATE OR REPLACE ROW ACCESS POLICY region_rls AS (region STRING)
RETURNS BOOLEAN ->
  CASE
    WHEN IS_ROLE_IN_SESSION('ADMIN') THEN TRUE
    WHEN IS_ROLE_IN_SESSION('US_ANALYST') AND region = 'US' THEN TRUE
    WHEN IS_ROLE_IN_SESSION('EU_ANALYST') AND region = 'EU' THEN TRUE
    ELSE FALSE
  END;

-- Apply to table
ALTER TABLE analytics.fct_orders
  ADD ROW ACCESS POLICY region_rls ON (region);
```

### BigQuery RLS

```sql
-- Create row access policy
CREATE OR REPLACE ROW ACCESS POLICY analytics.orders_rls
ON analytics.fct_orders
GRANT TO ("group:us-analysts@company.com")
FILTER USING (region = 'US');

CREATE OR REPLACE ROW ACCESS POLICY analytics.orders_rls_eu
ON analytics.fct_orders
GRANT TO ("group:eu-analysts@company.com")
FILTER USING (region = 'EU');
```

### PostgreSQL RLS

```sql
-- Enable RLS on table
ALTER TABLE analytics.fct_orders ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY region_access ON analytics.fct_orders
  FOR SELECT
  USING (
    region = current_setting('app.user_region')
    OR current_user = 'admin'
  );
```

---

## Column-Level Security and Dynamic Masking

### Unity Catalog Column Masking

```sql
-- Create masking function
CREATE OR REPLACE FUNCTION analytics.mask_email(email STRING)
RETURNS STRING
RETURN CASE
  WHEN IS_MEMBER('pii-authorized') THEN email
  ELSE CONCAT(LEFT(email, 2), '***@', SPLIT_PART(email, '@', 2))
END;

-- Apply to column
ALTER TABLE analytics.fct_orders
  ALTER COLUMN email SET MASK analytics.mask_email;
```

### Snowflake Dynamic Masking

```sql
-- Create masking policy
CREATE OR REPLACE MASKING POLICY email_mask AS (val STRING)
RETURNS STRING ->
  CASE
    WHEN IS_ROLE_IN_SESSION('PII_AUTHORIZED') THEN val
    WHEN IS_ROLE_IN_SESSION('ANALYST') THEN
      CONCAT(LEFT(val, 2), '***@', SPLIT(val, '@')[1])
    ELSE '***MASKED***'
  END;

-- Apply to column
ALTER TABLE analytics.fct_orders
  MODIFY COLUMN email SET MASKING POLICY email_mask;
```

### Masking Strategy by Data Type

| Data Type | Authorized | Analyst | Public |
|-----------|-----------|---------|--------|
| Email | `user@company.com` | `us***@company.com` | `***MASKED***` |
| Phone | `+1-555-123-4567` | `+1-555-***-****` | `NULL` |
| SSN | `123-45-6789` | `***-**-6789` | `NULL` |
| Name | `John Smith` | `J. S.` | `NULL` |
| IP Address | `192.168.1.100` | `192.168.x.x` | `NULL` |
| Credit Card | `4111-1111-1111-1111` | `****-****-****-1111` | `NULL` |

---

## Encryption

### At-Rest Encryption Checklist

- [ ] All S3/GCS/ADLS buckets use server-side encryption (SSE)
- [ ] KMS key rotation enabled (annual minimum)
- [ ] Separate KMS keys per environment (dev/staging/prod)
- [ ] Separate KMS keys for PII-containing tables
- [ ] Backup encryption matches primary encryption
- [ ] Key access logged in CloudTrail/audit log

### Encryption Configuration

```bash
# AWS S3 — SSE-KMS (recommended)
aws s3api put-bucket-encryption \
  --bucket data-lake-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789:key/abc-def-123"
      },
      "BucketKeyEnabled": true
    }]
  }'
```

### In-Transit Encryption

| Connection | Minimum TLS | Configuration |
|-----------|-------------|---------------|
| Client to warehouse | TLS 1.2 | Enforce in connection string |
| Warehouse to storage | TLS 1.2 | Default for managed services |
| ETL to warehouse | TLS 1.2 | Enforce in connector config |
| API endpoints | TLS 1.3 | Load balancer config |
| Internal services | mTLS | Service mesh (Istio, Linkerd) |

---

## PII Detection and Handling

### Automated PII Scanning

- **Column name signals**: email, phone, ssn, social_security, passport, credit_card, dob, address, zip_code, ip_address, first_name, last_name
- **Data pattern regex**: email, SSN, phone, credit card, IP address patterns
- **Approach**: Sample 1000 rows; if >10% match a PII regex, flag as potential PII
- **Confidence**: >50% match rate = high, 10-50% = medium
- **Integration**: Run in CI pipeline on schema changes; alert on new PII columns

### PII Classification Tags

```sql
-- Unity Catalog tagging
ALTER TABLE analytics.fct_orders
  ALTER COLUMN email SET TAGS ('pii' = 'email', 'sensitivity' = 'high');

ALTER TABLE analytics.fct_orders
  ALTER COLUMN customer_name SET TAGS ('pii' = 'name', 'sensitivity' = 'medium');
```

---

## Compliance Patterns

### GDPR Checklist

- [ ] PII columns identified and tagged in catalog
- [ ] Data masking applied for non-authorized roles
- [ ] Right to erasure (deletion) workflow implemented
- [ ] Data retention policies enforced automatically
- [ ] Processing lawful basis documented per table
- [ ] Cross-border transfer controls in place
- [ ] Breach notification process documented
- [ ] Data Protection Impact Assessment completed

### CCPA Checklist

- [ ] Personal information inventory maintained
- [ ] Opt-out mechanism integrated with data pipeline
- [ ] Sale/sharing of PI tracked and controllable
- [ ] Consumer request workflow (access, delete, correct)
- [ ] Service provider agreements include data handling terms

### Right to Erasure

- Soft delete: set `is_deleted = true`, NULL all PII columns, set name to 'REDACTED'
- Propagate to fact tables: NULL PII columns where customer_id matches
- Maintain audit trail of deletion request (without PII)

---

## Audit Logging

### What to Log

| Event | Required Fields | Retention |
|-------|----------------|-----------|
| Table access (SELECT) | who, what, when, query hash | 90 days |
| Data modification (INSERT/UPDATE/DELETE) | who, what, when, row count | 1 year |
| Schema change (ALTER, CREATE, DROP) | who, what, when, before/after | 2 years |
| Permission change (GRANT, REVOKE) | who, what, when, grantee | 2 years |
| Failed access attempt | who, what, when, reason | 1 year |
| Data export/download | who, what, when, row count, destination | 1 year |

### Audit Query Sources

- **Unity Catalog**: `system.access.audit` — filter by `action_name`, `request_params.table_name`
- **Snowflake**: `snowflake.account_usage.query_history` — filter by `query_text ILIKE`
- **BigQuery**: `region-us.INFORMATION_SCHEMA.JOBS` — filter by `referenced_tables`

---

## Access Control Automation

### Infrastructure-as-Code

- Use Terraform `aws_lakeformation_permissions` for Lake Formation grants
- Use `table_with_columns` resource for column-level exclusions
- Manage Unity Catalog grants via Terraform Databricks provider
- Store all permission definitions in version control

### Role Hierarchy Best Practice

```
admin
├── data-platform-admin (full access to all schemas)
├── domain-admin (full access to domain schema)
│   ├── domain-writer (INSERT/UPDATE/DELETE on domain tables)
│   └── domain-reader (SELECT on domain tables)
├── analyst (SELECT on curated schemas, no PII)
├── pii-analyst (SELECT on curated schemas + PII access)
└── service-account (per-pipeline, minimum required access)
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Shared credentials for pipelines | No audit trail, over-permissioned | Per-pipeline service accounts with minimum privileges |
| PII in unencrypted lake buckets | Compliance violation, breach risk | SSE-KMS + PII tagging + masking |
| All users in admin role | No access control | Role hierarchy with least-privilege |
| No audit logging | Cannot investigate breaches | Enable and retain audit logs per compliance requirements |
| Column security via views only | Views can be bypassed, hard to maintain | Use native column masking policies |
| Encryption key shared across environments | Dev compromise exposes prod | Separate KMS keys per environment |
| Manual permission management | Drift, inconsistency, slow onboarding | Infrastructure-as-code (Terraform, Pulumi) |
| No PII detection automation | New PII columns go undetected | Automated PII scanning in CI pipeline |

---

## Cross-References

- `data-quality-patterns.md` — PII detection as a quality check
- `data-mesh-patterns.md` — Access policies within data product specifications
- `permissions-collections.md` — BI-layer access control (Metabase)
- `monitoring-alerting-patterns.md` — Alerting on failed access attempts

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
