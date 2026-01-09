#!/usr/bin/env bash
set -euo pipefail

# Deprecated wrapper: use ./frameworks/sync-skills.sh from repo root.
#
# This file remains for backwards compatibility with older docs and scripts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

exec "${ROOT_DIR}/frameworks/sync-skills.sh" "$@"
