#!/usr/bin/env bash
# check_hub_freshness.config.example.sh — Stack-specific pattern overrides
#
# Copy this file to check_hub_freshness.config.sh (gitignored or local) and
# uncomment / edit the variables for your stack.  The main script sources
# check_hub_freshness.config.sh when it exists in the same directory.
#
# Each variable is a regex matched against git diff file paths (ERE syntax).
# Separate alternatives with |  (no spaces around |).

# ── .NET / C# ────────────────────────────────────────────────────────────────
# SCHEMA_PATTERNS='Migrations/|DbContext\.cs|MongoRegistry\.cs|MongoDbRegistry\.cs|\.sql$|InitSchema'
# API_PATTERNS='Controller.*\.cs|/routes/|openapi|swagger|\.proto$'
# MESSAGING_PATTERNS='Consumer.*\.cs|Producer.*\.cs|Message\.cs|Handler.*\.cs|kafka|rabbit|\.avsc$'
# CONFIG_PATTERNS='appsettings.*\.json|\.csproj|package\.json|docker-compose|\.env\.'
# INFRA_PATTERNS='Dockerfile|\.ya?ml$|\.gitlab-ci|\.github/workflows|helm|k8s|terraform'

# ── Node / TypeScript ─────────────────────────────────────────────────────────
# SCHEMA_PATTERNS='prisma/|knex/|\.sql$|migrations/'
# API_PATTERNS='routes/.*\.ts$|openapi.*\.ya?ml|swagger|\.proto$|handler.*\.ts$'
# MESSAGING_PATTERNS='consumer.*\.ts$|producer.*\.ts$|kafka|rabbit|\.avsc$'
# CONFIG_PATTERNS='package\.json|tsconfig|docker-compose|\.env\.'
# INFRA_PATTERNS='Dockerfile|\.ya?ml$|\.gitlab-ci|\.github/workflows|helm|terraform'

# ── Python ────────────────────────────────────────────────────────────────────
# SCHEMA_PATTERNS='alembic/|migrations/|\.sql$|models\.py'
# API_PATTERNS='views\.py|urls\.py|routers?/|openapi|swagger|\.proto$'
# MESSAGING_PATTERNS='consumers?\.py|producers?\.py|tasks?\.py|kafka|celery|\.avsc$'
# CONFIG_PATTERNS='pyproject\.toml|requirements.*\.txt|docker-compose|\.env\.'
# INFRA_PATTERNS='Dockerfile|\.ya?ml$|\.gitlab-ci|\.github/workflows|helm|terraform'

# ── Go ────────────────────────────────────────────────────────────────────────
# SCHEMA_PATTERNS='migrate/|\.sql$|schema\.go'
# API_PATTERNS='handler.*\.go|openapi|swagger|\.proto$'
# MESSAGING_PATTERNS='consumer.*\.go|producer.*\.go|kafka|rabbit|\.avsc$'
# CONFIG_PATTERNS='go\.mod|go\.sum|docker-compose|\.env\.'
# INFRA_PATTERNS='Dockerfile|\.ya?ml$|\.gitlab-ci|\.github/workflows|helm|terraform'

# ── Rust ──────────────────────────────────────────────────────────────────────
# SCHEMA_PATTERNS='migrations/|\.sql$|diesel\.toml'
# API_PATTERNS='handler.*\.rs|openapi|swagger|\.proto$|axum|actix'
# MESSAGING_PATTERNS='consumer.*\.rs|producer.*\.rs|kafka|rabbit|\.avsc$'
# CONFIG_PATTERNS='Cargo\.toml|Cargo\.lock|docker-compose|\.env\.'
# INFRA_PATTERNS='Dockerfile|\.ya?ml$|\.gitlab-ci|\.github/workflows|helm|terraform'
