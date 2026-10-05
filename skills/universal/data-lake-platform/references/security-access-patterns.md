# Data Lake Security and Access Patterns

Choose where access is enforced, how PII is masked and erased, and what is audited. Grant/policy syntax is engine-specific; look it up in the engine's docs — the rules below decide *what* to configure.

## Choosing the Enforcement Point

| Estate | Default |
|--------|---------|
| Databricks (Delta or Iceberg) | Unity Catalog grants, row filters, column masks |
| AWS, Iceberg/Parquet on S3 | Lake Formation (table/column/row) + IAM |
| Trino or other open engines | Ranger- or OPA-style policies in the engine |
| Snowflake / BigQuery / Redshift | Native RBAC, row access policies, masking policies |
| On-prem Hive/Parquet | Ranger + Kerberos |

## Rules That Matter More Than Syntax

1. **Engine policies do not protect the files.** Row filters and column masks apply only to queries through that engine or catalog. Anyone with direct object-store read on the table location bypasses them. Restrict bucket/prefix access to the catalog's and pipelines' principals and give engines short-lived vended credentials.
2. **One policy source per table.** If two engines enforce different policy stores on the same table, they drift; pick one enforcement point per table and make other engines read through it (or deny them).
3. **Use native row/column policies, not views.** Views can be bypassed by anyone with base-table access and multiply with every audience.
4. **Least privilege by role hierarchy**: platform-admin -> domain-admin -> domain-writer / domain-reader; analyst (curated, no PII) vs pii-analyst; one service principal per pipeline with only the grants it needs. Shared pipeline credentials destroy the audit trail.
5. **Permissions as code** (Terraform or equivalent) in version control; manual grants drift.

## Masking by Data Type

| Data | Authorized | Analyst | Everyone else |
|------|-----------|---------|---------------|
| Email | full | first 2 chars + domain | masked constant |
| Phone | full | country/area code only | NULL |
| National ID / SSN | full | last 4 | NULL |
| Card number | never stored in the lake unless PCI scope is intended | last 4 | NULL |
| IP address | full | truncated network prefix | NULL |

Tag PII columns (`pii`, `sensitivity`) in the catalog and bind masks to tags where the platform supports it, so new columns inherit policy.

## PII Detection

Scan in CI on every schema change: column-name signals (email, phone, ssn, passport, dob, address, ip) plus value-pattern matching on a sample. Tune the match-rate threshold on columns you have already labeled; alert on new PII columns and block promotion to curated layers until they are tagged.

## Right to Erasure in a Lakehouse

A `DELETE` in Iceberg, Delta, or Hudi writes a new snapshot; the personal data **still exists in older data files** and remains readable by time travel until those snapshots are expired and the files physically removed (snapshot expiry + orphan cleanup, or Delta `VACUUM`).

- [ ] Delete (or null PII columns) in every layer: bronze, silver, gold, and serving copies.
- [ ] Expire snapshots and physically remove files within the erasure deadline; make the time-travel window shorter than that deadline for tables holding personal data.
- [ ] Purge or compact upstream copies: CDC topics (tombstones on compacted topics), raw landing files, backups, exports.
- [ ] Keep an audit record of the request without the personal data.
- [ ] Verify: time-travel query to the pre-delete snapshot fails or returns no rows.

## Encryption

- At rest: server-side encryption with KMS keys; separate keys per environment and for PII-heavy data; key rotation enabled; key access logged.
- In transit: TLS 1.2 or newer everywhere, enforced in client and connector configs; mTLS for internal service-to-service where a mesh exists.

## Audit Logging

Log, with who/what/when: reads of sensitive tables, data modifications (row counts), schema changes (before/after), permission changes, failed access attempts, and exports (destination, row count). Set retention per the applicable compliance regime, not a generic default. Audit sources: the catalog's or warehouse's system audit tables and the cloud audit trail.

## Compliance Checklists

- **GDPR**: PII inventoried and tagged; masking for unauthorized roles; erasure workflow (above); automated retention; lawful basis per dataset; cross-border transfer controls; breach process; DPIA where required.
- **CCPA**: personal-information inventory; opt-out propagated into pipelines; sale/sharing tracked; access/delete/correct request workflow; service-provider terms.

Legal interpretation of these regimes belongs with counsel. Related: `data-metabase` (BI-layer permissions), [data-mesh-patterns.md](data-mesh-patterns.md) (access in product specs).
