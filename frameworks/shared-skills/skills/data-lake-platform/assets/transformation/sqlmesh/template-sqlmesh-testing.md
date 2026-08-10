# SQLMesh Testing & Data Quality Template

*Purpose: Implement comprehensive testing and data quality checks for SQL models.*

## Audits (Built-in Data Quality)

### Model with Audits
```sql
MODEL (
  name marts.customer_metrics,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column metric_date
  ),
  audits [
    audit_not_null(columns := [customer_id, metric_date, revenue]),
    audit_unique_values(columns := [customer_id, metric_date]),
    audit_accepted_values(column := status, is_in := ['active', 'inactive']),
    audit_number_of_rows(threshold := 1000)
  ]
);
```

### Custom Audit (Basic)
```sql
AUDIT (
  name audit_revenue_positive
);

SELECT *
FROM @this_model
WHERE revenue < 0;
```

### Parameterized Custom Audits

**Create reusable audit templates in sqlmesh/audits/ directory:**

**File: sqlmesh/audits/reference_exists.sql**
```sql
AUDIT (name reference_exists);

-- Validates foreign key relationships with smart sampling
WITH missing AS (
    SELECT src.@column AS missing_value
    FROM @this_model AS src
    LEFT JOIN @reference_model AS ref
      ON src.@column = ref.@reference_column
    WHERE src.@column IS NOT NULL
      AND ref.@reference_column IS NULL
),
stats AS (
    SELECT
        COUNT(*) AS missing_count,
        ARRAY_AGG(missing_value ORDER BY missing_value LIMIT 5) AS sample_values
    FROM missing
)
SELECT
    'Missing reference count: ' || missing_count ||
    ', sample values: ' || sample_values::text AS error
FROM stats
WHERE missing_count > 5;  -- Tolerance: Allow up to 5 missing references
```

**File: sqlmesh/audits/row_count_for_date_range.sql**
```sql
AUDIT (name row_count_for_date_range);

-- Validates data volume within expected range with ±10 tolerance
WITH target AS (
    SELECT COUNT(*) AS cnt
    FROM @this_model
    WHERE @date_column >= @date_start
      AND @date_column < @date_end
)
SELECT 'Row count ' || cnt || ' outside expected range (' ||
       (@expected_count - 10) || ' to ' || (@expected_count + 10) || ')' AS error
FROM target
WHERE cnt > 0
  AND cnt NOT BETWEEN (@expected_count - 10)
                  AND (@expected_count + 10);
```

**File: sqlmesh/audits/missing_description_for_id.sql**
```sql
AUDIT (name missing_description_for_id);

-- Validates reference data completeness (lookup tables)
SELECT
  @id as id,
  'Missing description for id: ' || @id AS error
FROM @this_model
WHERE @id IS NOT NULL AND @name IS NULL;
```

### Using Parameterized Audits in Models

```sql
MODEL (
  name public.users_funnel,
  kind FULL,
  audits (
    -- Validate foreign key relationships
    reference_exists(
      column := user_id,
      reference_model := public.users,
      reference_column := user_id
    ),
    -- Validate row counts with tolerance
    row_count_for_date_range(
      date_column := created,
      date_start := '2025-02-01',
      date_end := '2025-03-01',
      expected_count := 11727
    ),
    -- Standard built-in audits
    unique_values(columns := user_id)
  )
);
```

**Example: Multiple audit validations**
```sql
MODEL (
  name intermediate.transactions,
  kind FULL,
  audits (
    -- Primary key uniqueness
    unique_values(columns := purse_transaction_id),
    -- Foreign key validation
    reference_exists(
      column := user_id,
      reference_model := intermediate.users,
      reference_column := user_id
    ),
    -- Volume validation for specific date range
    row_count_for_date_range(
      date_column := creation_date,
      date_start := '2025-02-01',
      date_end := '2025-03-01',
      expected_count := 7814
    ),
    -- Not null validation
    audit_not_null(columns := [purse_transaction_id, user_id, creation_date])
  )
);
```

### Audit Best Practices

**When to use custom audits:**
- Foreign key validation (reference_exists)
- Volume checks with tolerance (row_count_for_date_range)
- Domain-specific business rules
- Data completeness checks
- Cross-table consistency checks

**When to use built-in audits:**
- NOT NULL constraints: `audit_not_null()`
- Uniqueness: `audit_unique_values()`
- Accepted values: `audit_accepted_values()`
- Row count thresholds: `audit_number_of_rows()`

**Audit performance tips:**
- Keep audit queries simple and fast
- Use indexes on audited columns
- Add tolerance thresholds to avoid false positives
- Sample large datasets (LIMIT) for pattern detection
- Avoid expensive aggregations in audits

---

## Unit Tests

### Create tests/test_staging.yaml
```yaml
test_stg_orders:
  model: staging.stg_orders
  inputs:
    raw.orders:
      rows:
        - order_id: 1
          customer_id: 100
          order_date: '2024-01-01'
          order_total: 50.00
          status: 'completed'
  outputs:
    query:
      rows:
        - order_id: 1
          customer_id: 100
          order_date: '2024-01-01'
          order_total: 50.00
```

## Run Tests

```bash
# Run all tests
sqlmesh test

# Run specific test
sqlmesh test test_stg_orders

# Run audits
sqlmesh audit
```

## Shell Script Testing

### Production Testing Script

**Many production environments use shell scripts instead of YAML tests:**

**File: test_sqlmesh.sh**
```bash
#!/bin/bash
set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Setup environment
setup_environment() {
    print_status "Loading environment variables..."

    if [ -f ".env_test" ]; then
        set -a
        source .env_test
        set +a
        print_success "Environment loaded"
    else
        print_error ".env_test not found"
        exit 1
    fi
}

# Run SQLMesh test
run_sqlmesh_test() {
    print_status "Running SQLMesh tests..."

    # Get current git branch
    local branch_name=$(git branch --show-current 2>/dev/null || echo "test")
    print_status "Using branch: $branch_name"

    cd sqlmesh

    # Dry-run with verbose output
    print_status "Running: sqlmesh plan $branch_name --dry-run --verbose"

    if sqlmesh --gateway dwh_local_test plan "$branch_name" --dry-run --verbose --no-prompts --auto-apply; then
        print_success "SQLMesh test passed!"
    else
        print_error "SQLMesh test failed!"
        exit 1
    fi
}

# Main
main() {
    print_status "Starting SQLMesh tests..."
    setup_environment
    run_sqlmesh_test
    print_success "All tests passed!"
}

main "$@"
```

### Shell Script Usage

```bash
# Make executable
chmod +x test_sqlmesh.sh

# Run full test
./test_sqlmesh.sh

# With specific gateway
./test_sqlmesh.sh --gateway dwh_local_test

# With environment setup only
./test_sqlmesh.sh --env-only
```

### Dry-Run Testing Pattern

**Key command for testing:**
```bash
# Dry-run: Validate without applying changes
sqlmesh plan dev --dry-run --verbose --no-prompts

# With specific gateway
sqlmesh --gateway dwh_local_test plan test --dry-run --verbose

# Test specific models
sqlmesh plan dev --select public.users --dry-run
```

**What dry-run validates:**
- SQL syntax correctness
- Model dependencies (DAG)
- Audit queries (syntax only)
- Configuration validity
- No actual data changes

---

## Testing Strategy Comparison

### Audit-Based Testing (Production Pattern)

**Used in production for:**
- Data quality validation
- Foreign key integrity
- Row count validation
- Business rule enforcement

**Advantages:**
- Runs on real data
- Catches data quality issues
- Part of deployment pipeline
- No mock data needed

**When to use:**
- Production data validation
- Continuous monitoring
- Post-deployment checks
- Data quality gates

### YAML Unit Tests

**Used in development for:**
- Model logic testing
- Edge case validation
- Transformation correctness
- Regression testing

**Advantages:**
- Fast execution
- Deterministic results
- Version controlled test data
- Isolated testing

**When to use:**
- Development/TDD
- Complex logic validation
- Pre-deployment testing
- CI/CD pipelines

### Recommended Approach

**Use both strategies:**

1. **Development**: YAML unit tests for logic validation
2. **Deployment**: Shell script + dry-run for syntax validation
3. **Production**: Audits for continuous data quality monitoring

**Example workflow:**
```bash
# 1. Development: Unit tests
sqlmesh test

# 2. Pre-deployment: Dry-run
./test_sqlmesh.sh

# 3. Deployment: Apply with audits
sqlmesh plan prod --auto-apply

# 4. Post-deployment: Run audits
sqlmesh audit --gateway dwh
```

---

## CI/CD Quality Gates

### GitHub Actions
```yaml
name: SQLMesh CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install SQLMesh
        run: pip install sqlmesh[postgres]

      - name: Run unit tests
        run: sqlmesh test

      - name: Run audits (dry-run)
        run: sqlmesh audit --dry-run

      - name: Validate plan
        env:
          DESTINATION__POSTGRES__CREDENTIALS__HOST: ${{ secrets.TEST_DB_HOST }}
          DESTINATION__POSTGRES__CREDENTIALS__USERNAME: ${{ secrets.TEST_DB_USER }}
          DESTINATION__POSTGRES__CREDENTIALS__PASSWORD: ${{ secrets.TEST_DB_PASSWORD }}
        run: |
          cd sqlmesh
          sqlmesh plan dev --dry-run --verbose --no-prompts
```

### GitLab CI
```yaml
stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.10
  before_script:
    - pip install sqlmesh[postgres]
  script:
    - sqlmesh test
    - sqlmesh audit --dry-run
    - cd sqlmesh && sqlmesh plan dev --dry-run --no-prompts
  only:
    - merge_requests
```

---

## Monitoring & Alerting

### Track Audit Failures

**PostgreSQL query to monitor failures:**
```sql
-- Failed audits in last 24 hours
SELECT
  model_name,
  audit_name,
  error_message,
  failed_at
FROM sqlmesh_audit_log
WHERE failed_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY failed_at DESC;

-- Audit failure rate by model
SELECT
  model_name,
  COUNT(*) FILTER (WHERE status = 'failed') as failures,
  COUNT(*) as total_runs,
  ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'failed') / COUNT(*), 2) as failure_rate_pct
FROM sqlmesh_audit_log
WHERE created_at >= CURRENT_DATE - 7
GROUP BY model_name
HAVING COUNT(*) FILTER (WHERE status = 'failed') > 0
ORDER BY failure_rate_pct DESC;
```

### Alert Configuration

**Slack notification on failures:**
```bash
#!/bin/bash
# add to cron: 0 9 * * * /path/to/check_audits.sh

FAILURES=$(psql -t -c "SELECT COUNT(*) FROM sqlmesh_audit_log WHERE failed_at >= CURRENT_DATE")

if [ "$FAILURES" -gt 0 ]; then
    curl -X POST ${SLACK_WEBHOOK_URL} \
      -H 'Content-Type: application/json' \
      -d "{\"text\":\"[WARNING] SQLMesh: $FAILURES audit failures detected today\"}"
fi
```

---

## Testing Checklist

Before deploying to production:

**Unit Tests:**
- [ ] All YAML tests passing (`sqlmesh test`)
- [ ] Edge cases covered
- [ ] New models have tests

**Audits:**
- [ ] All audits passing (`sqlmesh audit`)
- [ ] Custom audits validated
- [ ] Tolerance thresholds appropriate

**Integration:**
- [ ] Dry-run successful (`--dry-run`)
- [ ] No DAG circular dependencies
- [ ] All dependencies available

**Shell Script:**
- [ ] test_sqlmesh.sh executes successfully
- [ ] Environment variables validated
- [ ] All gateways accessible

**Documentation:**
- [ ] Audit failures documented
- [ ] Testing strategy documented
- [ ] Rollback procedure defined

---

## Related Resources

- **SQLMesh Security**: [template-sqlmesh-security.md](template-sqlmesh-security.md)
- **SQLMesh Production**: [template-sqlmesh-production.md](template-sqlmesh-production.md)
- **SQLMesh Models**: [template-sqlmesh-model.md](template-sqlmesh-model.md)
