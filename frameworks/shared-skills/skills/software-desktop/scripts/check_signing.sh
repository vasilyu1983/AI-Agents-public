#!/usr/bin/env bash
# check_signing.sh — Verifies code signing and notarization status for desktop apps.
#
# macOS: checks .app bundle with codesign and spctl (notarization gate).
# Windows: signtool /verify command is provided as a commented example — run on Windows.
#
# Usage:
#   ./check_signing.sh /path/to/MyApp.app
#   ./check_signing.sh /path/to/MyApp.dmg
#
# Requirements (macOS):
#   Xcode Command Line Tools (codesign, spctl, xcrun stapler)
#
# Exit codes:
#   0 — all checks pass (signed + notarized)
#   1 — one or more checks fail
#   2 — usage error (missing path)

set -euo pipefail

TARGET="${1:?Usage: $0 <path-to-app-or-dmg>}"
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

if [ "${OS}" = "Darwin" ]; then
  # ─── macOS checks ─────────────────────────────────────────────────────────

  section "Code signature (codesign -v)"
  if codesign --verify --deep --strict --verbose=2 "${TARGET}" 2>&1; then
    pass "codesign --verify passed"
  else
    fail "codesign --verify failed — bundle is not signed or signature is broken"
  fi

  section "Hardened Runtime flag"
  ENTITLEMENTS=$(codesign --display --verbose=4 "${TARGET}" 2>&1 || true)
  if echo "${ENTITLEMENTS}" | grep -q "flags=0x10000(runtime)"; then
    pass "Hardened Runtime is enabled (flags include 0x10000)"
  else
    fail "Hardened Runtime NOT enabled — required for notarization (Apple, 2019+)"
    echo "  Hint: add --options runtime to your codesign call or set hardened-runtime=true in your build config"
  fi

  section "Notarization gate (spctl --assess)"
  SPCTL_OUT=$(spctl --assess --type execute --verbose=4 "${TARGET}" 2>&1 || true)
  echo "  spctl output: ${SPCTL_OUT}"
  if echo "${SPCTL_OUT}" | grep -q "accepted"; then
    pass "Notarization accepted by Gatekeeper"
  elif echo "${SPCTL_OUT}" | grep -q "source=Notarized Developer ID"; then
    pass "Notarized Developer ID source confirmed"
  else
    fail "Notarization not accepted — run 'xcrun notarytool submit' and 'xcrun stapler staple'"
  fi

  section "Stapled ticket check (stapler validate)"
  if xcrun stapler validate "${TARGET}" 2>&1 | grep -q "The validate action worked"; then
    pass "Notarization ticket is stapled to the bundle"
  else
    fail "Notarization ticket NOT stapled — run: xcrun stapler staple ${TARGET}"
    echo "  Note: unstapled apps require internet access to pass Gatekeeper on first launch"
  fi

  section "Team identifier"
  TEAM=$(codesign --display --verbose=4 "${TARGET}" 2>&1 | grep "TeamIdentifier" || true)
  if [ -n "${TEAM}" ]; then
    pass "Team identifier present: ${TEAM}"
  else
    fail "Team identifier not found — check signing identity"
  fi

  section "Entitlements dump (informational)"
  codesign --display --entitlements :- "${TARGET}" 2>/dev/null | head -30 || echo "  (no entitlements or not accessible)"

else
  echo "Platform: ${OS} — macOS checks skipped"
  echo ""
  echo "For Windows, use signtool (run in a Windows shell or GitHub Actions windows runner):"
  echo ""
  echo "  # Verify Authenticode signature"
  echo '  signtool verify /pa /v "MyApp.exe"'
  echo ""
  echo "  # Verify MSIX/AppX package"
  echo '  signtool verify /pa /all "MyApp.msix"'
  echo ""
  echo "  # Check timestamp"
  echo '  signtool verify /pa /v /debug "MyApp.exe" 2>&1 | Select-String "Timestamp"'
  echo ""
  echo "  # For EV certificates — check Enhanced Key Usage includes Code Signing (1.3.6.1.5.5.7.3.3)"
  echo '  certutil -dump "MyApp.exe" | findstr /i "code signing"'
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
