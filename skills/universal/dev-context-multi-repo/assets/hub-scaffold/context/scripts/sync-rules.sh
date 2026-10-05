#!/usr/bin/env bash
# sync-rules.sh — propagate the hub's rules/ into source repos.
#
# Generic: drops a short AGENTS.md pointer into each repo so any coding
# agent routes back to the hub's rule layer instead of re-deriving policy.
# Edit REPOS_ROOT / HUB_REL for your layout. Idempotent.
set -euo pipefail

HUB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPOS_ROOT="${1:-$(dirname "$HUB_DIR")}"   # default: sibling of the hub
HUB_REL="${HUB_REL:-../requirements-hub}"  # path from a repo back to the hub

shopt -s nullglob
for repo in "$REPOS_ROOT"/*/; do
  name="$(basename "$repo")"
  [ "$repo" = "$HUB_DIR/" ] && continue
  [ -d "$repo/.git" ] || continue
  agents="$repo/AGENTS.md"
  if [ -f "$agents" ] && grep -q "requirements hub" "$agents" 2>/dev/null; then
    echo "ok    $name (already points at hub)"
    continue
  fi
  cat > "$agents" <<EOF
# AGENTS.md — $name

Cross-repo context lives in the requirements hub, not here.

- Hub: $HUB_REL
- Binding rules: $HUB_REL/rules/
- This repo's catalog page: $HUB_REL/<domain>/as-is/$name.md

Do not paste cross-repo inventories here. Update the hub catalog page.
EOF
  echo "wrote $name/AGENTS.md"
done
echo "Done. Review and commit per repo."
