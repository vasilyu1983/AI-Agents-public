#!/usr/bin/env bash
# check_signing.sh — Verifies code signing and notarization status for desktop apps.
#
# macOS: checks .app bundle with codesign and spctl (notarization gate).
# Windows: signtool /verify command is provided as a commented example — run on Windows.
#
# Usage:
#   ./check_signing.sh /path/to/MyApp.app
#
# Requirements (macOS):
#   Xcode Command Line Tools (codesign, spctl, xcrun stapler)
#
# Exit codes:
#   0 — all checks pass (signed + notarized)
#   1 — one or more checks fail
#   2 — usage error (missing path)

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <path-to-Developer-ID-app>" >&2
  exit 2
fi
TARGET="$1"
PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)) || true; }
fail() { echo "  FAIL: $1"; ((FAIL++)) || true; }
section() { echo ""; echo "==> $1"; }

if [ ! -e "${TARGET}" ]; then
  echo "ERROR: Path does not exist: ${TARGET}"
  exit 2
fi

# ─── Detect platform ──────────────────────────────────────────────────────────
OS="$(uname -s)"
if [ "$OS" != "Darwin" ]; then
  echo "UNSUPPORTED: artifact verification requires macOS; no checks ran" >&2
  exit 2
fi
if [[ "$TARGET" != *.app ]] || [ ! -d "$TARGET" ]; then
  echo "UNSUPPORTED: this verifier accepts .app bundles, not DMG/PKG/EXE/MSIX" >&2
  exit 2
fi

if [ "${OS}" = "Darwin" ]; then
  # ─── macOS checks ─────────────────────────────────────────────────────────

  section "Code signature (codesign -v)"
  if codesign --verify --deep --strict --verbose=2 "${TARGET}" 2>&1; then
    pass "codesign --verify passed"
  else
    fail "codesign --verify failed — bundle is not signed or signature is broken"
  fi

  section "Hardened Runtime flag"
  DISPLAY_OK=0
  if ENTITLEMENTS=$(codesign --display --verbose=4 "${TARGET}" 2>&1); then
    DISPLAY_OK=1
  fi
  if [ "$DISPLAY_OK" -eq 1 ] && echo "${ENTITLEMENTS}" | grep -Eq 'flags=0x[0-9a-fA-F]+\([^)]*runtime[^)]*\)'; then
    pass "Hardened Runtime is enabled (flags include 0x10000)"
  else
    fail "Hardened Runtime NOT enabled — required for notarization (Apple, 2019+)"
    echo "  Hint: add --options runtime to your codesign call or set hardened-runtime=true in your build config"
  fi

  section "Notarization gate (spctl --assess)"
  if SPCTL_OUT=$(spctl --assess --type execute --verbose=4 "${TARGET}" 2>&1); then
    if printf '%s\n' "$SPCTL_OUT" | grep -q '^source=Notarized Developer ID$'; then
      pass "Gatekeeper accepted a Notarized Developer ID app"
    else
      fail "Gatekeeper success did not establish a Notarized Developer ID source"
    fi
  else
    fail "Gatekeeper assessment failed"
  fi

  section "Stapled ticket check (stapler validate)"
  if xcrun stapler validate "${TARGET}"; then
    pass "Notarization ticket validation succeeded"
  else
    fail "Notarization ticket validation failed"
  fi

  section "Team identifier"
  TEAM=$(printf '%s\n' "$ENTITLEMENTS" | grep "TeamIdentifier" || true)
  if [ "$DISPLAY_OK" -eq 1 ] && printf '%s\n' "$TEAM" | grep -Eq '^TeamIdentifier=[A-Z0-9]+$'; then
    pass "Team identifier present: ${TEAM}"
  else
    fail "Team identifier not found — check signing identity"
  fi

  section "Entitlements dump (informational)"
  codesign --display --entitlements :- "${TARGET}" 2>/dev/null | head -30 || echo "  (no entitlements or not accessible)"

fi

# ─── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "────────────────────────────────────────"
echo "Signing check summary: ${PASS} passed, ${FAIL} failed"
echo "────────────────────────────────────────"

if [ "${FAIL}" -gt 0 ]; then
  echo "FAIL: Fix the issues above before submitting for distribution."
  exit 1
fi

echo "PASS: All signing checks passed."
exit 0
