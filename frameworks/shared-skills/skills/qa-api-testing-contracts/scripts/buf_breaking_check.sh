#!/usr/bin/env bash
# buf_breaking_check.sh — Detect breaking changes in .proto files using buf.
#
# Required env vars:
#   REMOTE  — buf against target: a git ref, branch, or buf registry reference.
#             Examples:
#               git reference   — ".git#branch=main"
#               buf registry    — "buf.build/acme/petapis:v1.0.0"
#               local directory — "../proto-baseline"
#
# Optional env vars:
#   BUF_CONFIG  — path to buf.yaml (default: buf.yaml in working directory)
#   BUF_INPUT   — proto root directory or module to check (default: . )
#
# Exit codes:
#   0 — no breaking changes detected
#   1 — breaking changes found or buf could not run

set -euo pipefail

: "${REMOTE:?REMOTE is required (e.g. \".git#branch=main\" or \"buf.build/org/repo\")}"

INPUT="${BUF_INPUT:-.}"

CONFIG_ARGS=()
if [[ -n "${BUF_CONFIG:-}" ]]; then
  CONFIG_ARGS+=(--config "${BUF_CONFIG}")
fi

echo "==> buf breaking: checking ${INPUT} against ${REMOTE}"

buf breaking "${INPUT}" \
  --against "${REMOTE}" \
  "${CONFIG_ARGS[@]+"${CONFIG_ARGS[@]}"}"

echo "==> buf breaking: OK — no breaking changes detected in ${INPUT}"
