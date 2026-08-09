#!/usr/bin/env bash
# spectral_lint.sh — Lint an OpenAPI (or AsyncAPI/Arazzo) file with Spectral.
#
# Required env vars:
#   OPENAPI_FILE  — path to the OpenAPI (or AsyncAPI / Arazzo) file to lint
#
# Optional env vars:
#   SPECTRAL_RULESET     — path or URL to the Spectral ruleset (default: .spectral.yaml)
#   SPECTRAL_FAIL_SEVERITY — minimum severity that causes a non-zero exit (default: error)
#                            Choices: hint | info | warn | error
#
# Exit codes:
#   0 — lint passed (no violations at or above fail-severity)
#   1 — lint failed or Spectral could not run

set -euo pipefail

: "${OPENAPI_FILE:?OPENAPI_FILE is required}"

RULESET="${SPECTRAL_RULESET:-.spectral.yaml}"
FAIL_SEVERITY="${SPECTRAL_FAIL_SEVERITY:-error}"

echo "==> spectral lint: linting ${OPENAPI_FILE} (ruleset=${RULESET}, fail-severity=${FAIL_SEVERITY})"

spectral lint "${OPENAPI_FILE}" \
  --fail-severity "${FAIL_SEVERITY}" \
  --ruleset "${RULESET}"

echo "==> spectral lint: OK — ${OPENAPI_FILE} passed with no violations at severity '${FAIL_SEVERITY}' or above"
