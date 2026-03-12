# SQLMesh Project Setup Template

*Purpose: Initialize and configure a SQLMesh project for SQL-based data transformation orchestration.*

---

## When to Use

Use this template for:
- Setting up a new SQLMesh project
- Organizing SQL models for analytics engineering
- Creating data transformation pipelines with version control
- Establishing incremental model workflows

---

## 1. Project Initialization

### Create Project Structure

```bash
# Install SQLMesh
pip install sqlmesh

# Initialize new project
sqlmesh init my_project

cd my_project
```

### Directory Structure

```
my_project/
├── config.yaml              # SQLMesh configuration
├── models/                  # SQL model definitions
│   ├── staging/            # Raw data cleaning
│   ├── intermediate/       # Business logic transformations
│   └── marts/              # Final analytics tables
├── audits/                 # Data quality tests
├── macros/                 # Reusable SQL snippets
├── seeds/                  # Static reference data
└── tests/                  # Unit tests for models
```

---

## 2. Configuration (config.yaml)

### Basic Configuration

```yaml
gateways:
  local:
    connection:
      type: duckdb
      database: db.duckdb

  production:
    connection:
      type: postgres
      host: localhost
      port: 5432
      database: analytics
      user: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}

default_gateway: local

model_defaults:
  dialect: postgres
  start: 2024-01-01
```

### Advanced Configuration

```yaml
gateways:
  local:
    connection:
      type: duckdb
      database: db.duckdb

  staging:
    connection:
      type: snowflake
      account: ${SNOWFLAKE_ACCOUNT}
      user: ${SNOWFLAKE_USER}
      password: ${SNOWFLAKE_PASSWORD}
      database: ANALYTICS_STAGING
      warehouse: COMPUTE_WH
      schema: PUBLIC

  production:
    connection:
      type: snowflake
      account: ${SNOWFLAKE_ACCOUNT}
      user: ${SNOWFLAKE_USER}
      password: ${SNOWFLAKE_PASSWORD}
      database: ANALYTICS_PROD
      warehouse: COMPUTE_WH
      schema: PUBLIC

default_gateway: local

model_defaults:
  dialect: snowflake
  start: 2024-01-01
  cron: '@daily'

# Environment configuration
environments:
  dev:
    suffix: _dev
  staging:
    suffix: _staging
  prod:
    suffix: ''  # No suffix for production

# Notification settings
notifications:
  on_failure:
    - type: slack
      webhook_url: ${SLACK_WEBHOOK_URL}
```

---

## 3. Environment Setup

### Development Environment (.env)

```bash
# Database credentials
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=your_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=analytics

# Snowflake credentials
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password

# Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### .gitignore

```
# SQLMesh
.sqlmesh/
db.duckdb
db.duckdb.wal

# Environment
.env
*.env

# Python
__pycache__/
*.pyc
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
```

---

## 4. Model Organization Strategy

### Staging Layer (models/staging/)
- **Purpose**: Raw data cleaning and standardization
- **Naming**: `stg_<source>__<entity>.sql`
- **Example**: `stg_shopify__orders.sql`

### Intermediate Layer (models/intermediate/)
- **Purpose**: Business logic, joins, calculations
- **Naming**: `int_<domain>__<description>.sql`
- **Example**: `int_sales__enriched_orders.sql`

### Marts Layer (models/marts/)
- **Purpose**: Final analytics-ready tables
- **Naming**: `<domain>__<entity>.sql`
- **Example**: `sales__daily_revenue.sql`

---

## 5. First Model Example

### Create models/staging/stg_orders.sql

```sql
MODEL (
  name staging.stg_orders,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column order_date
  ),
  start '2024-01-01',
  cron '@daily',
  grain [order_id]
);

SELECT
  order_id::INT AS order_id,
  customer_id::INT AS customer_id,
  order_date::DATE AS order_date,
  order_total::DECIMAL(10,2) AS order_total,
  status::VARCHAR AS status,
  CURRENT_TIMESTAMP AS _loaded_at
FROM raw.orders
WHERE
  order_date BETWEEN @start_date AND @end_date
  AND status != 'cancelled';
```

---

## 6. Development Workflow

### Run SQLMesh Commands

```bash
# Plan changes (dry run)
sqlmesh plan

# Apply changes to dev environment
sqlmesh plan dev

# Run specific date range
sqlmesh run --start 2024-01-01 --end 2024-01-31

# Test models
sqlmesh test

# Validate audits
sqlmesh audit

# Deploy to production
sqlmesh plan prod
```

### UI for Exploration

```bash
# Start SQLMesh UI
sqlmesh ui

# Access at http://localhost:8000
```

---

## 7. Version Control Setup

### Initialize Git

```bash
git init
git add .
git commit -m "Initial SQLMesh project setup"
```

### Branch Strategy

```bash
# Feature development
git checkout -b feature/add-revenue-models

# After changes, plan in dev
sqlmesh plan dev

# Commit and push
git add models/
git commit -m "Add daily revenue model"
git push origin feature/add-revenue-models
```

---

## 8. CI/CD Integration

### GitHub Actions (.github/workflows/sqlmesh.yml)

```yaml
name: SQLMesh CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install sqlmesh

      - name: Run tests
        run: sqlmesh test

      - name: Run audits
        run: sqlmesh audit

      - name: Plan changes
        run: sqlmesh plan --auto-apply
        env:
          POSTGRES_USER: ${{ secrets.POSTGRES_USER }}
          POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
```

---

## 9. Quality Checklist

Before finalizing project setup:

- [ ] config.yaml configured for all environments
- [ ] .env file created (not committed)
- [ ] .gitignore includes sensitive files
- [ ] Directory structure follows staging/intermediate/marts pattern
- [ ] First model created and tested
- [ ] SQLMesh plan runs successfully
- [ ] Tests pass (sqlmesh test)
- [ ] CI/CD workflow configured
- [ ] Documentation created (README.md)

---

## 10. README Template

```markdown
# Analytics Data Models

SQLMesh-based data transformation pipelines.

## Setup

\`\`\`bash
pip install sqlmesh
cp .env.example .env  # Add your credentials
sqlmesh plan dev
\`\`\`

## Project Structure

- \`models/staging/\` - Raw data cleaning
- \`models/intermediate/\` - Business logic
- \`models/marts/\` - Final analytics tables

## Development

\`\`\`bash
# Plan changes
sqlmesh plan dev

# Run models
sqlmesh run --start 2024-01-01

# Test models
sqlmesh test

# Start UI
sqlmesh ui
\`\`\`

## Deployment

\`\`\`bash
# Deploy to production
sqlmesh plan prod
\`\`\`
```

---

## 11. Next Steps

After project setup:
1. BEST: Create first staging model
2. NEXT: Add intermediate models (see template-sqlmesh-model.md)
3. → Implement incremental logic (see template-sqlmesh-incremental.md)
4. → Add data quality tests (see template-sqlmesh-testing.md)
5. → Organize model dependencies (see template-sqlmesh-dag.md)
