# SQLMesh Production Patterns Template

*Purpose: Production-ready SQLMesh project patterns including environment management, testing scripts, seed data, documentation standards, and operational best practices.*

---

## When to Use

Use this template for:
- Setting up production-grade SQLMesh environments
- Managing seed/reference data
- Creating testing and deployment scripts
- Documenting access rights and model standards
- Organizing multi-environment configurations
- Implementing operational best practices

---

## 1. Multi-Environment Configuration

### Environment Files Structure

```
project_root/
├── .env_test           # Test environment credentials
├── .env_prod           # Production credentials (not committed)
├── sqlmesh/
│   └── config.yaml     # Gateway configurations
└── test_sqlmesh.sh     # Testing script
```

### .env_test (Test Environment)

```bash
# Database Connection
DESTINATION__POSTGRES__CREDENTIALS__HOST=trino-test.company.corp
DESTINATION__POSTGRES__CREDENTIALS__PORT=5432
DESTINATION__POSTGRES__CREDENTIALS__DATABASE=dwh
DESTINATION__POSTGRES__CREDENTIALS__USERNAME=your_username
DESTINATION__POSTGRES__CREDENTIALS__PASSWORD=your_password
DESTINATION__POSTGRES__CREDENTIALS__CONNECT_TIMEOUT=15

# Optional: Schema Overrides
SQLMESH_DEFAULT_GATEWAY=dwh_local_test
SQLMESH_ENVIRONMENT=test
```

### .env_prod (Production Environment)

```bash
# Database Connection
DESTINATION__POSTGRES__CREDENTIALS__HOST=prod-db.company.com
DESTINATION__POSTGRES__CREDENTIALS__PORT=5432
DESTINATION__POSTGRES__CREDENTIALS__DATABASE=dwh_prod
DESTINATION__POSTGRES__CREDENTIALS__USERNAME=${PROD_DB_USER}
DESTINATION__POSTGRES__CREDENTIALS__PASSWORD=${PROD_DB_PASSWORD}
DESTINATION__POSTGRES__CREDENTIALS__CONNECT_TIMEOUT=30

# Optional
SQLMESH_DEFAULT_GATEWAY=dwh
SQLMESH_ENVIRONMENT=prod
```

### config.yaml with Multiple Gateways

```yaml
gateways:
  # Production gateway
  dwh:
    connection:
      type: postgres
      connect_timeout: {{ env_var('DESTINATION__POSTGRES__CREDENTIALS__CONNECT_TIMEOUT', '30') }}
      database: {{ env_var('DESTINATION__POSTGRES__CREDENTIALS__DATABASE') }}
      host: {{ env_var('DESTINATION__POSTGRES__CREDENTIALS__HOST') }}
      password: '{{ env_var('DESTINATION__POSTGRES__CREDENTIALS__PASSWORD') }}'
      port: {{ env_var('DESTINATION__POSTGRES__CREDENTIALS__PORT', '5432') }}
      user: {{ env_var('DESTINATION__POSTGRES__CREDENTIALS__USERNAME') }}

  # Test/staging gateway
  dwh_local_test:
    connection:
      type: postgres
      connect_timeout: 15
      database: dwh
      host: trino-test.company.corp
      password: '{{ env_var('DESTINATION__POSTGRES__CREDENTIALS__PASSWORD') }}'
      port: 5432
      user: {{ env_var('DESTINATION__POSTGRES__CREDENTIALS__USERNAME') }}

  # Local development (DuckDB)
  local:
    connection:
      type: duckdb
      database: local_dev.duckdb

default_gateway: dwh

model_defaults:
  dialect: postgres
  start: 2024-01-01
  cron: '@daily'

# Snapshot cleanup
snapshot_ttl: in 1 day

# Janitor settings (cleanup failed snapshots)
janitor:
  warn_on_delete_failure: true
```

### Advanced Gateway Patterns

**Snowflake configuration:**
```yaml
gateways:
  snowflake_prod:
    connection:
      type: snowflake
      account: {{ env_var('SNOWFLAKE_ACCOUNT') }}
      user: {{ env_var('SNOWFLAKE_USER') }}
      password: {{ env_var('SNOWFLAKE_PASSWORD') }}
      database: ANALYTICS_PROD
      warehouse: COMPUTE_WH
      role: TRANSFORMER
      schema: PUBLIC
```

**BigQuery configuration:**
```yaml
gateways:
  bigquery_prod:
    connection:
      type: bigquery
      project: {{ env_var('GCP_PROJECT_ID') }}
      dataset: analytics
      credentials_path: {{ env_var('GOOGLE_APPLICATION_CREDENTIALS') }}
```

---

## 2. Testing Script (Bash)

### test_sqlmesh.sh

**Complete testing script with environment setup:**

```bash
#!/bin/bash

# SQLMesh Testing Script
# Purpose: Simplify testing by handling environment setup and running SQLMesh commands

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if variable is set
check_var() {
    local var_name=$1
    local var_value=${!var_name}

    if [ -z "$var_value" ]; then
        return 1
    else
        return 0
    fi
}

# Prompt for credentials
prompt_credentials() {
    print_status "Checking SQLMesh environment variables..."

    if ! check_var "DESTINATION__POSTGRES__CREDENTIALS__USERNAME"; then
        echo -n "Enter your database username: "
        read -r username
        export DESTINATION__POSTGRES__CREDENTIALS__USERNAME="$username"
        print_success "Username set"
    else
        print_status "Username already set: $DESTINATION__POSTGRES__CREDENTIALS__USERNAME"
    fi

    if ! check_var "DESTINATION__POSTGRES__CREDENTIALS__PASSWORD"; then
        echo -n "Enter your database password: "
        read -s -r password
        echo
        export DESTINATION__POSTGRES__CREDENTIALS__PASSWORD="$password"
        print_success "Password set"
    else
        print_status "Password already set"
    fi
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."

    # Load .env_test file if it exists
    if [ -f ".env_test" ]; then
        print_status "Loading environment variables from .env_test..."
        set -a  # automatically export all variables
        source .env_test
        set +a
        print_success "Loaded .env_test"
    else
        print_warning ".env_test not found. Using manual credentials."
    fi

    prompt_credentials

    # Verify required variables
    required_vars=(
        "DESTINATION__POSTGRES__CREDENTIALS__USERNAME"
        "DESTINATION__POSTGRES__CREDENTIALS__PASSWORD"
    )

    for var in "${required_vars[@]}"; do
        if ! check_var "$var"; then
            print_error "Required variable $var is not set"
            exit 1
        fi
    done

    print_success "Environment setup complete"
}

# Run SQLMesh test
run_sqlmesh_test() {
    print_status "Running SQLMesh test..."

    if [ ! -d "sqlmesh" ]; then
        print_error "sqlmesh directory not found. Run from project root."
        exit 1
    fi

    # Get current git branch
    local branch_name
    if command -v git &> /dev/null; then
        branch_name=$(git branch --show-current 2>/dev/null)
        if [ -z "$branch_name" ]; then
            print_warning "Could not determine git branch, using 'test'"
            branch_name="test"
        else
            print_status "Using git branch: $branch_name"
        fi
    else
        print_warning "git not found, using 'test' as branch"
        branch_name="test"
    fi

    cd sqlmesh

    if ! command -v sqlmesh &> /dev/null; then
        print_error "sqlmesh command not found. Install with: pip install sqlmesh"
        exit 1
    fi

    # Run SQLMesh with dry-run
    print_status "Executing: sqlmesh --gateway dwh_local_test plan $branch_name --dry-run --verbose --no-prompts --auto-apply"

    if sqlmesh --gateway dwh_local_test plan "$branch_name" --dry-run --verbose --no-prompts --auto-apply; then
        print_success "SQLMesh test completed successfully!"
    else
        print_error "SQLMesh test failed!"
        exit 1
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -e, --env-only     Only setup environment (don't run test)"
    echo "  -t, --test-only    Only run SQLMesh test (assume env is set)"
    echo "  -g, --gateway NAME Use specific gateway (default: dwh_local_test)"
    echo ""
    echo "Examples:"
    echo "  $0                       # Full setup and test"
    echo "  $0 --env-only            # Only setup environment"
    echo "  $0 --test-only           # Only run test"
    echo "  $0 --gateway dwh         # Use production gateway"
}

# Main script
main() {
    local env_only=false
    local test_only=false
    local gateway="dwh_local_test"

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -e|--env-only)
                env_only=true
                shift
                ;;
            -t|--test-only)
                test_only=true
                shift
                ;;
            -g|--gateway)
                gateway="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    print_status "Starting SQLMesh testing script..."

    if [ "$test_only" = false ]; then
        setup_environment
    fi

    if [ "$env_only" = false ]; then
        run_sqlmesh_test
    fi

    print_success "Script completed successfully!"
}

main "$@"
```

### Usage Examples

```bash
# Full test with environment setup
./test_sqlmesh.sh

# Test with production gateway
./test_sqlmesh.sh --gateway dwh

# Only setup environment
./test_sqlmesh.sh --env-only

# Run test (assuming env already set)
./test_sqlmesh.sh --test-only
```

---

## 3. Seed Data Management

### Seed Files Organization

```
sqlmesh/seeds/
├── mcc.csv                          # Merchant Category Codes
├── user_states.csv                  # User state lookup
├── card_state.csv                   # Card state reference
├── country_area.csv                 # Geographic classifications
├── countries_risk_scores.csv        # Country risk ratings
├── industries_risk_scores.csv       # Industry risk ratings
├── purposes_risk_scores.csv         # Purpose of account risk
├── verification_status.csv          # Verification status codes
├── transaction_status.csv           # Transaction status codes
├── currency.csv                     # Currency reference data
└── ...
```

### Seed File Format

**Example: mcc.csv**
```csv
mcc_code,description,category
5411,"Grocery Stores, Supermarkets","retail"
5812,"Eating Places, Restaurants","food"
5814,"Fast Food Restaurants","food"
4121,"Taxicabs and Limousines","transportation"
```

**Example: user_states.csv**
```csv
id,name,category,description
1,new,active,"New user registration"
2,verified,active,"KYC verification completed"
3,suspended,inactive,"Account temporarily suspended"
4,blocked,inactive,"Account permanently blocked"
```

### Using Seed Data in Models

**Reference seed data in models:**
```sql
MODEL (
  name intermediate.transactions_enriched,
  kind FULL
);

SELECT
  t.transaction_id,
  t.mcc_code,
  mcc.description AS merchant_category_description,
  mcc.category AS merchant_category,
  t.amount,
  curr.currency_name,
  curr.currency_symbol
FROM stage.transactions t
LEFT JOIN seed.mcc ON t.mcc_code = mcc.mcc_code
LEFT JOIN seed.currency curr ON t.currency_id = curr.currency_id;
```

### Seed Data Best Practices

**When to use seeds:**
- Static reference data (< 10,000 rows)
- Lookup tables that rarely change
- Configuration data (statuses, categories, mappings)
- Risk scores and regulatory classifications

**When NOT to use seeds:**
- Large datasets (> 10,000 rows) → Use stage models
- Frequently updated data → Use stage models with incremental loading
- Transactional data → Never use seeds

**Seed file standards:**
- Use CSV format with headers
- Include primary key column
- Add `updated_at` timestamp column
- Version control all seed files
- Document changes in commit messages

---

## 4. Documentation Standards

### access_rights.md

**Create in sqlmesh/ directory:**

```markdown
# Access Rights Documentation

## Overview

This document defines the role-based access control (RBAC) structure for the data warehouse.

## Role Hierarchy

### Admin Roles
- **data_engineer**: Full access to all schemas and tables
  - Use: Platform maintenance, schema changes, debugging
  - Access: ALL privileges on all objects

- **fincrime**: Compliance and fraud monitoring
  - Use: AML/fraud investigation, regulatory reporting
  - Access: SELECT on all schemas including sensitive data

### Standard Roles
- **common**: General analytics access
  - Use: Business intelligence, reporting, dashboards
  - Access: SELECT on public.*, sandbox.*

- **common_personal**: Analytics + PII access
  - Use: Customer support, account management
  - Access: SELECT on public.*, public_limited.*

- **common_fin**: Analytics + financial data
  - Use: Finance team, accounting, revenue reporting
  - Access: SELECT on public.*, public_fincrime.*

### Restricted Roles
- **eu**: EU legal entity data only
  - RLS Policy: legal_entity = 'CY-CBC'
  - Use: EU-specific reporting and compliance

- **uk**: UK legal entity data only
  - RLS Policy: legal_entity = 'UK-FCA'
  - Use: UK-specific reporting and compliance

## Schema Access Matrix

| Schema | Description | common | common_personal | common_fin | eu/uk | fincrime | data_engineer |
|--------|-------------|--------|-----------------|------------|-------|----------|---------------|
| public | Public analytics | [OK] | [OK] | [OK] | [OK] (RLS) | [OK] | [OK] |
| public_limited | PII data | [FAIL] | [OK] | [FAIL] | [OK] (RLS) | [OK] | [OK] |
| public_fincrime | Compliance data | [FAIL] | [FAIL] | [OK] | [FAIL] | [OK] | [OK] |
| sandbox | Experimental | [OK] | [OK] | [OK] | [FAIL] | [FAIL] | [OK] |
| intermediate | Business logic | [FAIL] | [FAIL] | [FAIL] | [FAIL] | [FAIL] | [OK] |
| stage | Raw data | [FAIL] | [FAIL] | [FAIL] | [FAIL] | [FAIL] | [OK] |

## Requesting Access

1. Submit ticket to data engineering team
2. Specify: Schema + Role + Business justification
3. Manager approval required for personal/fincrime data
4. Access reviewed quarterly

## Auditing

All access to public_limited and public_fincrime schemas is logged.
```

### Model Documentation Standards

**Every model should have:**

1. **MODEL block description:**
```sql
MODEL (
  name public.users,
  kind FULL,
  description 'User master table containing account information,
               verification status, and demographic data.
               Updated daily. Used by BI dashboards and customer support.',
  owner 'data-team',
  tags ['users', 'master', 'daily']
);
```

2. **Inline field comments:**
```sql
SELECT
  user_id,                          -- Unique user identifier (primary key)
  email,                            -- User email (unique, used for login)
  full_name,                        -- Full legal name from KYC verification
  created_at,                       -- Account creation timestamp (UTC)
  verification_status,              -- Current KYC status (verified/pending/rejected)
  legal_entity,                     -- Entity under which account is registered
  country_of_residence,             -- ISO country code from address verification
  risk_score                        -- Composite risk score (0-100, higher = riskier)
FROM intermediate.users;
```

3. **JINJA comments for complex logic:**
```sql
JINJA_STATEMENT_BEGIN;
{#
  Row-Level Security Policy:
  - EU role: Only CY-CBC (Cyprus) entity data
  - UK role: Only UK-FCA entity data
  - Common roles: No entity filtering

  Security barrier enabled to prevent information leakage
  through query plan optimization.
#}
ALTER TABLE {{ this_model }} ENABLE ROW LEVEL SECURITY;
-- ... policy definitions
JINJA_END;
```

---

## 5. Layer Organization

### Standard Layer Structure

```
sqlmesh/models/
├── stage/                    # Raw data layer (VIEW models)
│   ├── source_postgres/     # PostgreSQL sources
│   ├── source_mongodb/      # MongoDB sources
│   ├── source_api/          # API data sources
│   └── ...
│
├── intermediate/            # Business logic layer (FULL models)
│   ├── users.sql
│   ├── transactions.sql
│   ├── cards.sql
│   └── ...
│
├── public/                  # Public analytics layer (VIEW/FULL)
│   ├── users.sql           # RLS-protected, accessible to common
│   ├── transactions.sql
│   └── ...
│
├── public_limited/          # PII data layer (VIEW)
│   ├── users_personal.sql  # Full PII access
│   ├── users_contacts.sql
│   └── ...
│
├── public_fincrime/         # Compliance layer (VIEW)
│   ├── high_risk_transactions.sql
│   ├── sanctions_matches.sql
│   └── ...
│
├── sandbox/                 # Experimental layer
│   ├── prototype_*.sql     # Proof of concepts
│   └── ...
│
└── stage_fincrime/          # Compliance source data
    └── ...
```

### Layer Naming Conventions

| Layer | Prefix | Model Kind | Access | Example |
|-------|--------|------------|--------|---------|
| stage | `stage.<source>_` | VIEW | data_engineer only | `stage.postgres_users` |
| intermediate | `intermediate.` | FULL | data_engineer only | `intermediate.users` |
| public | `public.` | VIEW/FULL | Role-based | `public.users` |
| public_limited | `public_limited.` | VIEW | Restricted | `public_limited.users_personal` |
| public_fincrime | `public_fincrime.` | VIEW | fincrime + finance | `public_fincrime.aml_alerts` |
| sandbox | `sandbox.` | Any | common + | `sandbox.experiment_churn` |

---

## 6. Operational Best Practices

### Daily Operations Checklist

**Morning:**
- [ ] Check SQLMesh plan for overnight changes
- [ ] Review failed models (if any)
- [ ] Verify snapshot cleanup completed
- [ ] Check audit failures

**After Changes:**
- [ ] Run `sqlmesh plan dev` first
- [ ] Review DAG changes
- [ ] Run audits: `sqlmesh audit`
- [ ] Test with dry-run: `--dry-run --verbose`
- [ ] Deploy to prod: `sqlmesh plan prod --auto-apply`

**Weekly:**
- [ ] Review unused models (check query logs)
- [ ] Update seed data if needed
- [ ] Review access logs for anomalies
- [ ] Update documentation

### Deployment Workflow

```bash
# 1. Develop on feature branch
git checkout -b feature/add-revenue-model

# 2. Create/modify models
vim sqlmesh/models/public/revenue_daily.sql

# 3. Test locally
./test_sqlmesh.sh

# 4. Plan in dev environment
cd sqlmesh
sqlmesh plan dev

# 5. Run audits
sqlmesh audit

# 6. Commit changes
git add .
git commit -m "Add daily revenue model"

# 7. Create PR and deploy to staging
git push origin feature/add-revenue-model

# 8. After approval, deploy to production
git checkout main
git pull
cd sqlmesh
sqlmesh plan prod --auto-apply
```

### Monitoring

**Key metrics to track:**
```sql
-- Model execution times
SELECT
  model_name,
  AVG(execution_duration_seconds) as avg_duration,
  MAX(execution_duration_seconds) as max_duration
FROM sqlmesh.model_execution_log
WHERE execution_date >= CURRENT_DATE - 7
GROUP BY model_name
ORDER BY avg_duration DESC;

-- Failed audits
SELECT
  model_name,
  audit_name,
  error_message,
  failed_at
FROM sqlmesh.audit_failures
WHERE failed_at >= CURRENT_DATE - 7;

-- Snapshot growth
SELECT
  DATE_TRUNC('day', created_at) as date,
  COUNT(*) as snapshot_count,
  SUM(size_mb) as total_size_mb
FROM sqlmesh.snapshots
GROUP BY 1
ORDER BY 1 DESC;
```

---

## 7. CI/CD Integration

### GitHub Actions Workflow

**.github/workflows/sqlmesh-test.yml:**
```yaml
name: SQLMesh CI

on:
  pull_request:
    branches: [main]
    paths:
      - 'sqlmesh/**'
      - '.env_test'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install sqlmesh[postgres]

      - name: Run SQLMesh tests
        env:
          DESTINATION__POSTGRES__CREDENTIALS__HOST: ${{ secrets.TEST_DB_HOST }}
          DESTINATION__POSTGRES__CREDENTIALS__USERNAME: ${{ secrets.TEST_DB_USER }}
          DESTINATION__POSTGRES__CREDENTIALS__PASSWORD: ${{ secrets.TEST_DB_PASSWORD }}
          DESTINATION__POSTGRES__CREDENTIALS__DATABASE: dwh_test
        run: |
          cd sqlmesh
          sqlmesh plan dev --dry-run --verbose --no-prompts

      - name: Run audits
        run: |
          cd sqlmesh
          sqlmesh audit --gateway dwh_local_test
```

### GitLab CI Pipeline

**.gitlab-ci.yml:**
```yaml
stages:
  - test
  - deploy

variables:
  PYTHON_VERSION: "3.10"

test:
  stage: test
  image: python:${PYTHON_VERSION}
  before_script:
    - pip install sqlmesh[postgres]
  script:
    - cd sqlmesh
    - sqlmesh plan dev --dry-run --verbose --no-prompts
    - sqlmesh audit --gateway dwh_local_test
  only:
    - merge_requests
    - main

deploy_prod:
  stage: deploy
  image: python:${PYTHON_VERSION}
  before_script:
    - pip install sqlmesh[postgres]
  script:
    - cd sqlmesh
    - sqlmesh plan prod --auto-apply --no-prompts
  only:
    - main
  when: manual
```

---

## 8. Troubleshooting Guide

### Common Issues

**Issue: "Gateway not found"**
```bash
# Check config.yaml syntax
sqlmesh config validate

# List available gateways
grep -A5 "gateways:" sqlmesh/config.yaml
```

**Issue: "Environment variable not set"**
```bash
# Load environment file
source .env_test

# Verify variable
echo $DESTINATION__POSTGRES__CREDENTIALS__USERNAME
```

**Issue: "Permission denied on model"**
```sql
-- Check grants
SELECT grantee, privilege_type
FROM information_schema.table_privileges
WHERE table_name = 'users'
  AND table_schema = 'public';

-- Re-apply model to refresh grants
sqlmesh run -s public.users --gateway dwh_local_test
```

**Issue: "Snapshot cleanup failing"**
```bash
# Manual cleanup
cd sqlmesh
sqlmesh janitor --gateway dwh

# Check disk space
df -h
```

---

## 9. Production Checklist

Before deploying to production:

**Configuration:**
- [ ] All credentials in environment variables (not hardcoded)
- [ ] Production gateway configured in config.yaml
- [ ] Snapshot TTL appropriate (1 day for prod)
- [ ] Janitor configured (`warn_on_delete_failure: true`)

**Security:**
- [ ] RLS policies applied to sensitive tables
- [ ] Access rights documented in access_rights.md
- [ ] Roles and permissions reviewed
- [ ] PII masking macros tested

**Testing:**
- [ ] All audits passing
- [ ] Dry-run successful
- [ ] Test environment mirrors production
- [ ] Seed data validated

**Documentation:**
- [ ] Model descriptions complete
- [ ] Inline comments on all fields
- [ ] access_rights.md up to date
- [ ] README.md includes deployment instructions

**Monitoring:**
- [ ] Execution time alerts configured
- [ ] Audit failure notifications enabled
- [ ] Snapshot growth monitoring
- [ ] Failed model alerts

---

## Related Resources

- **SQLMesh Security**: [template-sqlmesh-security.md](template-sqlmesh-security.md)
- **SQLMesh Model Patterns**: [template-sqlmesh-model.md](template-sqlmesh-model.md)
- **SQLMesh Testing**: [template-sqlmesh-testing.md](template-sqlmesh-testing.md)
- **DevOps Patterns**: [../../ops-devops-platform/SKILL.md](../../../../ops-devops-platform/SKILL.md)

---

Use these production patterns to build robust, well-documented, and maintainable SQLMesh projects.
