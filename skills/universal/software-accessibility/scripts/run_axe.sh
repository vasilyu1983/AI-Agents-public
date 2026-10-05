#!/usr/bin/env bash
# run_axe.sh — Runs axe-core/cli against a URL and exits non-zero on any violation.
#
# Usage:
#   ./run_axe.sh https://example.com
#   ./run_axe.sh https://example.com wcag2aa,wcag21aa,wcag22aa   # custom tag set
#
# Requirements:
#   npx and python3; verify the installed CLI's Node requirement
#   @axe-core/cli is invoked via npx — no global install required
#
# Exit codes:
#   0  — no violations found
#   1  — one or more violations found (or axe failed to run)

set -euo pipefail

TARGET_URL="${1:?Usage: $0 <url> [tags]}"
TAGS="${2:-wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa}"
REPORT_FILE="$(python3 -c 'import os, tempfile; fd, name = tempfile.mkstemp(prefix="axe-report-", suffix=".json", dir="."); os.close(fd); print(name)')"

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

# A successful process without a valid scan is not evidence of a clean page.
python3 - "${REPORT_FILE}" <<'PYREPORT'
import json
import sys
from pathlib import Path
try:
    reports = json.loads(Path(sys.argv[1]).read_text())
    if not isinstance(reports, list) or not reports:
        raise ValueError("report must contain at least one scan")
    for report in reports:
        if not isinstance(report, dict):
            raise ValueError("scan must be an object")
        for field in ("violations", "passes", "incomplete", "inapplicable"):
            if not isinstance(report.get(field), list):
                raise ValueError(f"missing or invalid {field}")
        if not report["passes"]:
            raise ValueError("no passing rules recorded")
        if report["violations"]:
            raise ValueError("violations present despite CLI exit 0")
    pending = sum(len(report["incomplete"]) for report in reports)
    print(f"PASS: No recorded axe violations; {pending} incomplete checks require manual review.")
except (OSError, ValueError, TypeError) as exc:
    print(f"FAIL: scan report could not establish a clean result: {exc}", file=sys.stderr)
    sys.exit(1)
PYREPORT
exit 0
