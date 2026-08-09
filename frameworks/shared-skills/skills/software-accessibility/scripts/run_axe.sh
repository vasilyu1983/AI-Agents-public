#!/usr/bin/env bash
# run_axe.sh — Runs axe-core/cli against a URL and exits non-zero on any violation.
#
# Usage:
#   ./run_axe.sh https://example.com
#   ./run_axe.sh https://example.com wcag2aa,wcag22aa   # custom tag set
#
# Requirements:
#   npx (Node.js 18+)
#   @axe-core/cli is invoked via npx — no global install required
#
# Exit codes:
#   0  — no violations found
#   1  — one or more violations found (or axe failed to run)

set -euo pipefail

TARGET_URL="${1:?Usage: $0 <url> [tags]}"
TAGS="${2:-wcag2a,wcag2aa,wcag22aa}"
REPORT_FILE="axe-report-$(date +%Y%m%dT%H%M%S).json"

echo "==> Running axe-core against: ${TARGET_URL}"
echo "    Tags: ${TAGS}"
echo "    Report: ${REPORT_FILE}"
echo ""

# Run axe; capture exit code without triggering set -e
npx --yes @axe-core/cli \
  "${TARGET_URL}" \
  --tags "${TAGS}" \
  --save "${REPORT_FILE}" \
  --exit || AXE_EXIT=$?

AXE_EXIT="${AXE_EXIT:-0}"

if [ "${AXE_EXIT}" -ne 0 ]; then
  echo ""
  echo "FAIL: axe found violations. See ${REPORT_FILE} for details."
  echo ""
  # Print violation summary if jq is available
  if command -v jq &>/dev/null && [ -f "${REPORT_FILE}" ]; then
    echo "Violation summary:"
    jq -r '.[0].violations[] | "  [\(.impact)] \(.id): \(.description)"' "${REPORT_FILE}" 2>/dev/null || true
  fi
  exit 1
fi

echo "PASS: No axe violations found."
exit 0
