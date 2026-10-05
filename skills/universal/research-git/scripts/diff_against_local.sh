#!/usr/bin/env bash
# diff_against_local.sh — compare an extracted external skill to a local equivalent
#
# Usage:
#   ./diff_against_local.sh <external_dir> <local_skill_dir>
#
# Example:
#   ./diff_against_local.sh \
#     docs/research/2026-04-12-ios/raw/twostraws__Swift-Concurrency-Agent-Skill/ \
#     skills/universal/software-ios-native/
#
# Output: a diff report showing:
#   - Reference files in external NOT in local (potential new content)
#   - Reference files in local NOT in external (your gaps may already be covered)
#   - Sections in external SKILL.md headings not in local (potential new patterns)
#
# Exit codes: 0 = report written; 1 = usage error or directory not found;
# 2 = an input is not a skill bundle (no SKILL.md in it)

set -euo pipefail

usage() { sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; }

for arg in "$@"; do
    case "$arg" in -h|--help) usage; exit 0 ;; esac
done

if [[ $# -lt 2 ]]; then
    usage >&2
    exit 1
fi

EXTERNAL="${1%/}"
LOCAL="${2%/}"

if [[ ! -d "$EXTERNAL" ]]; then
    echo "ERROR: external dir not found: $EXTERNAL" >&2
    exit 1
fi

if [[ ! -d "$LOCAL" ]]; then
    echo "ERROR: local dir not found: $LOCAL" >&2
    exit 1
fi

# Both inputs must be skill bundles. A directory without SKILL.md (the raw/
# parent, a practice or code extract) would otherwise diff as "nothing new".
for side in "$EXTERNAL" "$LOCAL"; do
    if [[ ! -f "$side/SKILL.md" ]]; then
        echo "ERROR: not a skill bundle (no SKILL.md): $side" >&2
        echo "Pass the directory that contains SKILL.md, e.g. raw/<owner>__<repo>/ and skills/<name>/" >&2
        exit 2
    fi
done

echo "=== DIFF: $(basename "$EXTERNAL") vs $(basename "$LOCAL") ==="
echo ""

# 1. Reference file diff
echo "## Reference Files"
echo ""

EXT_REFS=$(ls "$EXTERNAL/references/" 2>/dev/null | sort || echo "")
LOC_REFS=$(ls "$LOCAL/references/" 2>/dev/null | sort || echo "")

if [[ -z "$EXT_REFS" && -z "$LOC_REFS" ]]; then
    echo "(neither side has a references/ directory)"
else
    NEW_IN_EXT=$(comm -23 <(echo "$EXT_REFS") <(echo "$LOC_REFS") 2>/dev/null || echo "")
    ONLY_IN_LOC=$(comm -13 <(echo "$EXT_REFS") <(echo "$LOC_REFS") 2>/dev/null || echo "")
    SHARED=$(comm -12 <(echo "$EXT_REFS") <(echo "$LOC_REFS") 2>/dev/null || echo "")

    if [[ -n "$NEW_IN_EXT" ]]; then
        echo "### Reference files in EXTERNAL but NOT in LOCAL (potential new content):"
        echo "$NEW_IN_EXT" | sed 's/^/  + /'
    else
        echo "(no new reference files in external)"
    fi
    echo ""

    if [[ -n "$SHARED" ]]; then
        echo "### Reference files present in BOTH (compare contents manually):"
        echo "$SHARED" | sed 's/^/  ~ /'
    fi
    echo ""

    if [[ -n "$ONLY_IN_LOC" ]]; then
        echo "### Reference files only in LOCAL (you have these, external doesn't):"
        echo "$ONLY_IN_LOC" | sed 's/^/  - /'
    fi
fi

echo ""
echo "## SKILL.md Section Headings"
echo ""

# grep exits 1 on no match; with pipefail that would kill the script silently.
EXT_HEADINGS=$(grep -E '^##[^#]' "$EXTERNAL/SKILL.md" | sed 's/^## //' | sort -u || true)
LOC_HEADINGS=$(grep -E '^##[^#]' "$LOCAL/SKILL.md" | sed 's/^## //' | sort -u || true)

NEW_HEADINGS=$(comm -23 <(echo "$EXT_HEADINGS") <(echo "$LOC_HEADINGS") 2>/dev/null || echo "")

if [[ -n "$NEW_HEADINGS" ]]; then
    echo "### Section headings in EXTERNAL but NOT in LOCAL:"
    echo "$NEW_HEADINGS" | sed 's/^/  + ## /'
else
    echo "(no new section headings in external)"
fi

echo ""
echo "## Source Citations"
echo ""

EXT_LINKS=$(grep -oE 'https://[^[:space:])]+' "$EXTERNAL/SKILL.md" "$EXTERNAL/references/"*.md 2>/dev/null | grep -oE 'https://[^[:space:])]+' | sort -u || echo "")
LOC_LINKS=$(grep -oE 'https://[^[:space:])]+' "$LOCAL/SKILL.md" "$LOCAL/references/"*.md 2>/dev/null | grep -oE 'https://[^[:space:])]+' | sort -u || echo "")

NEW_LINKS=$(comm -23 <(echo "$EXT_LINKS") <(echo "$LOC_LINKS") 2>/dev/null || echo "")

if [[ -n "$NEW_LINKS" ]]; then
    echo "### Source citations in EXTERNAL but NOT in LOCAL:"
    echo "$NEW_LINKS" | head -20 | sed 's/^/  + /'
    TOTAL=$(echo "$NEW_LINKS" | wc -l | tr -d ' ')
    if [[ "$TOTAL" -gt 20 ]]; then
        echo "  (and $((TOTAL - 20)) more)"
    fi
else
    echo "(no new source citations in external)"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Review the new reference files above for extractable patterns"
echo "2. Read shared reference files side-by-side to find updates"
echo "3. Check new source citations for primary sources you might be missing"
echo "4. Use insight-mining.md filters to decide what's worth merging"
