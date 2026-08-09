#!/usr/bin/env bash
# schemathesis_baseline.sh — Run Schemathesis property-based API checks and emit a stable summary line.
#
# Requires Schemathesis v4+ (released June 2025). Run via uvx (recommended) or install globally.
# Migration note: --hypothesis-max-examples was renamed to --max-examples in v4.
#
# Required env vars:
#   OPENAPI_URL  — URL of the OpenAPI spec to test (e.g. http://localhost:8000/openapi.json)
#                  or a local file path (e.g. ./openapi.yaml)
#
# Optional env vars:
#   SCHEMATHESIS_MAX_EXAMPLES — max examples per test case (default: 200)
#   SCHEMATHESIS_BASE_URL     — override base URL for requests (--url flag; useful when spec URL
#                               differs from the API base URL)
#   SCHEMATHESIS_WORKERS      — number of parallel workers (default: auto)
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more checks failed or Schemathesis could not run

set -euo pipefail

: "${OPENAPI_URL:?OPENAPI_URL is required}"

MAX_EXAMPLES="${SCHEMATHESIS_MAX_EXAMPLES:-200}"

EXTRA_ARGS=()
if [[ -n "${SCHEMATHESIS_BASE_URL:-}" ]]; then
  EXTRA_ARGS+=(--url "${SCHEMATHESIS_BASE_URL}")
fi
if [[ -n "${SCHEMATHESIS_WORKERS:-}" ]]; then
  EXTRA_ARGS+=(--workers "${SCHEMATHESIS_WORKERS}")
fi

echo "==> schemathesis: running all checks against ${OPENAPI_URL} (max-examples=${MAX_EXAMPLES})"

# v4 flag: --max-examples (was --hypothesis-max-examples in v3)
uvx schemathesis run \
  --checks all \
  --max-examples="${MAX_EXAMPLES}" \
  "${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}" \
  "${OPENAPI_URL}"

echo "==> schemathesis: OK — all checks passed for ${OPENAPI_URL}"
