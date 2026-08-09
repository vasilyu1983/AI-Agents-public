#!/usr/bin/env bash
# install-script-skeleton.sh
#
# Skeleton for a coding-agent distribution installer.
# Fill in the TODO sections before shipping.
#
# Design principles:
#   1. Detect platform and architecture before downloading anything.
#   2. Verify the downloaded archive against a SHA-256 checksum.
#   3. Check for conflicting existing installs before writing to disk.
#   4. Support dry-run mode (AGENT_INSTALL_DRY_RUN=1) for CI smoke tests.
#   5. Print clear resolution instructions on every failure, not just error codes.
#
# Usage:
#   curl -fsSL https://get.yourorg.example/install.sh | bash
#   AGENT_INSTALL_DRY_RUN=1 bash install.sh   # dry-run: detect and plan, no writes

set -euo pipefail

# ── Configuration (fill in before shipping) ───────────────────────────────────
AGENT_NAME="your-agent"                               # TODO: set binary name
AGENT_VERSION="${AGENT_VERSION:-1.0.0}"               # TODO: update on release
DOWNLOAD_BASE="https://releases.yourorg.example"      # TODO: set your release CDN
INSTALL_DIR="${AGENT_INSTALL_DIR:-/usr/local/bin}"    # override via env
CHECKSUM_URL="${DOWNLOAD_BASE}/${AGENT_VERSION}/checksums.txt"
DRY_RUN="${AGENT_INSTALL_DRY_RUN:-0}"

# ── Helpers ───────────────────────────────────────────────────────────────────

info()  { echo "[install] $*"; }
warn()  { echo "[install] WARN: $*" >&2; }
error() { echo "[install] ERROR: $*" >&2; exit 1; }

dry_run_guard() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] would run: $*"
  else
    "$@"
  fi
}

# ── 1. Detect OS and architecture ─────────────────────────────────────────────

detect_platform() {
  local os arch
  os="$(uname -s)"
  arch="$(uname -m)"

  case "$os" in
    Linux)  os="linux"  ;;
    Darwin) os="darwin" ;;
    *)      error "Unsupported OS: $os. Resolution: install manually from $DOWNLOAD_BASE." ;;
  esac

  case "$arch" in
    x86_64 | amd64) arch="amd64"  ;;
    arm64  | aarch64) arch="arm64" ;;
    *)      error "Unsupported architecture: $arch. Resolution: install manually from $DOWNLOAD_BASE." ;;
  esac

  PLATFORM="${os}-${arch}"
  info "Detected platform: $PLATFORM"
}

# ── 2. Check for existing install ─────────────────────────────────────────────

check_existing() {
  if command -v "$AGENT_NAME" &>/dev/null; then
    local existing_version
    existing_version="$("$AGENT_NAME" --version 2>/dev/null | head -1 || echo "unknown")"
    warn "$AGENT_NAME is already installed: $existing_version"
    warn "Resolution: run '$AGENT_NAME update' to upgrade, or set AGENT_INSTALL_DIR to install alongside."
    if [[ "$DRY_RUN" != "1" ]]; then
      read -r -p "Overwrite existing install? [y/N] " answer
      [[ "$answer" =~ ^[Yy]$ ]] || error "Installation cancelled."
    fi
  fi
}

# ── 3. Download archive ───────────────────────────────────────────────────────

download_archive() {
  ARCHIVE_NAME="${AGENT_NAME}-${AGENT_VERSION}-${PLATFORM}.tar.gz"
  ARCHIVE_URL="${DOWNLOAD_BASE}/${AGENT_VERSION}/${ARCHIVE_NAME}"
  TMPDIR_LOCAL="$(mktemp -d)"
  ARCHIVE_PATH="${TMPDIR_LOCAL}/${ARCHIVE_NAME}"

  info "Downloading $ARCHIVE_URL"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] would download: $ARCHIVE_URL → $ARCHIVE_PATH"
    return
  fi

  if command -v curl &>/dev/null; then
    curl -fsSL --retry 3 "$ARCHIVE_URL" -o "$ARCHIVE_PATH"
  elif command -v wget &>/dev/null; then
    wget -q --tries=3 "$ARCHIVE_URL" -O "$ARCHIVE_PATH"
  else
    error "Neither curl nor wget found. Resolution: install curl or wget, then re-run this script."
  fi
}

# ── 4. Verify checksum ────────────────────────────────────────────────────────

verify_checksum() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] would verify SHA-256 of $ARCHIVE_PATH against $CHECKSUM_URL"
    return
  fi

  info "Verifying checksum..."
  local checksums_file="${TMPDIR_LOCAL}/checksums.txt"

  if command -v curl &>/dev/null; then
    curl -fsSL "$CHECKSUM_URL" -o "$checksums_file"
  else
    wget -q "$CHECKSUM_URL" -O "$checksums_file"
  fi

  local expected_hash
  expected_hash="$(grep "$ARCHIVE_NAME" "$checksums_file" | awk '{print $1}')"

  if [[ -z "$expected_hash" ]]; then
    error "Checksum for $ARCHIVE_NAME not found in $CHECKSUM_URL. Resolution: report to the distribution maintainer."
  fi

  local actual_hash
  if command -v sha256sum &>/dev/null; then
    actual_hash="$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}')"
  elif command -v shasum &>/dev/null; then
    actual_hash="$(shasum -a 256 "$ARCHIVE_PATH" | awk '{print $1}')"
  else
    error "No SHA-256 tool found (sha256sum or shasum). Resolution: install one, then re-run."
  fi

  if [[ "$actual_hash" != "$expected_hash" ]]; then
    error "Checksum mismatch! Expected $expected_hash, got $actual_hash. Resolution: the archive may be corrupt or tampered; delete it and re-run."
  fi

  info "Checksum verified."
}

# ── 5. Extract and install ────────────────────────────────────────────────────

install_binary() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] would extract $ARCHIVE_PATH and install binary to $INSTALL_DIR/$AGENT_NAME"
    return
  fi

  info "Extracting archive..."
  tar -xzf "$ARCHIVE_PATH" -C "$TMPDIR_LOCAL"

  local binary_path="${TMPDIR_LOCAL}/${AGENT_NAME}"
  if [[ ! -f "$binary_path" ]]; then
    # Some archives nest the binary in a subdirectory
    binary_path="$(find "$TMPDIR_LOCAL" -type f -name "$AGENT_NAME" | head -1)"
    [[ -n "$binary_path" ]] || error "Binary '$AGENT_NAME' not found in archive. Resolution: check the archive structure at $DOWNLOAD_BASE."
  fi

  dry_run_guard install -m 755 "$binary_path" "$INSTALL_DIR/$AGENT_NAME"
  info "Installed $AGENT_NAME to $INSTALL_DIR/$AGENT_NAME"
}

# ── 6. Verify installed binary ────────────────────────────────────────────────

verify_install() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] would verify: $AGENT_NAME --version"
    return
  fi

  if ! "$INSTALL_DIR/$AGENT_NAME" --version &>/dev/null; then
    error "Installed binary failed to run. Resolution: check that $INSTALL_DIR is in PATH and the binary is executable."
  fi
  info "Installed version: $("$INSTALL_DIR/$AGENT_NAME" --version 2>&1 | head -1)"
}

# ── 7. Cleanup ────────────────────────────────────────────────────────────────

cleanup() {
  [[ -n "${TMPDIR_LOCAL:-}" ]] && rm -rf "$TMPDIR_LOCAL"
}
trap cleanup EXIT

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
  [[ "$DRY_RUN" == "1" ]] && info "DRY-RUN mode — no changes will be written."
  detect_platform
  check_existing
  download_archive
  verify_checksum
  install_binary
  verify_install
  info "Installation complete. Run: $AGENT_NAME --help"
}

main "$@"
