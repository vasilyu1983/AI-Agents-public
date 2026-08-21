#!/usr/bin/env bash
# search_repos.sh — discover public GitHub repos across three modes
#
# Modes:
#   skill           — repos with SKILL.md (agent-skill ecosystem)
#   practice        — real production repos with strong CI/PR/release practices
#   code            — high-signal OSS repos in a given language/framework
#   killer-feature  — OSS clones of commercial products (oss_clone_focus signal
#                     for the bundle's Killer-Feature Convergence Protocol;
#                     see references/killer-feature-mining.md)
#
# Usage:
#   ./search_repos.sh --kind <skill|practice|code|killer-feature> <query>
#   ./search_repos.sh --owner <owner> [--kind <mode>]
#   ./search_repos.sh --awesome [--kind <mode>]
#
# Examples:
#   ./search_repos.sh --kind skill ios
#   ./search_repos.sh --kind practice monorepo
#   ./search_repos.sh --kind code "react i18n"
#   ./search_repos.sh --kind killer-feature firebase
#   ./search_repos.sh --owner twostraws --kind skill
#   ./search_repos.sh --awesome --kind skill
#
# Filters applied to all modes: archived=false, fork=false, stars>=50.
#
# Requires: gh CLI (https://cli.github.com/) authenticated + jq.

set -euo pipefail

if ! command -v gh &> /dev/null; then
    echo "ERROR: gh CLI not found. Install from https://cli.github.com/" >&2
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "ERROR: gh not authenticated. Run: gh auth login" >&2
    exit 1
fi

usage() {
    sed -n '2,21p' "$0" | sed 's/^# \?//'
    exit 0
}

KIND=""
MODE_FLAG=""
OWNER=""
AWESOME=0
QUERY=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) usage ;;
        --kind) KIND="${2:?--kind requires a value}"; MODE_FLAG="--kind $KIND"; shift 2 ;;
        --owner) OWNER="${2:?--owner requires a value}"; shift 2 ;;
        --awesome) AWESOME=1; shift ;;
        *) QUERY="${QUERY}${QUERY:+ }$1"; shift ;;
    esac
done

if [[ -z "$KIND" && "$AWESOME" -eq 0 && -z "$OWNER" ]]; then
    echo "ERROR: --kind is required (skill | practice | code)" >&2
    usage
fi

case "$KIND" in
    skill|practice|code|killer-feature|"") ;;
    *) echo "ERROR: --kind must be one of: skill, practice, code, killer-feature" >&2; exit 1 ;;
esac

# Mode-specific search-topic hints and header signals
search_mode_skill() {
    local q="$1"
    echo "=== Mode: skill | query: $q ==="
    echo ""
    echo "--- By topic agent-skills (noisy, triage required) ---"
    gh search repos --topic agent-skills "$q" \
        --sort stars --limit 20 --archived=false \
        --json fullName,description,stargazersCount,updatedAt 2>/dev/null \
        | jq -r '.[] | "\(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' \
        | column -t -s $'\t' || echo "(no results)"

    echo ""
    echo "--- By topic claude-skills / codex-skills (narrower, higher signal) ---"
    for topic in claude-skills codex-skills; do
        gh search repos --topic "$topic" "$q" \
            --sort stars --limit 10 --archived=false \
            --json fullName,description,stargazersCount,updatedAt 2>/dev/null \
            | jq -r --arg t "$topic" '.[] | "[\($t)] \(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' \
            | column -t -s $'\t' || true
    done

    echo ""
    echo "--- By name pattern (*-agent-skill, *-skills) ---"
    gh search repos "$q agent-skill" --sort stars --limit 15 --archived=false \
        --json fullName,description,stargazersCount,updatedAt 2>/dev/null \
        | jq -r '.[] | "\(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' \
        | column -t -s $'\t' || echo "(no results)"
}

search_mode_practice() {
    local q="$1"
    echo "=== Mode: practice | query: $q ==="
    echo ""
    echo "--- High-star repos matching query (CI/PR signal candidates) ---"
    gh search repos "$q" --sort stars --limit 25 \
        --archived=false --stars '>=500' \
        --json fullName,description,stargazersCount,updatedAt 2>/dev/null \
        | jq -r '.[] | "\(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' \
        | column -t -s $'\t' || echo "(no results)"

    echo ""
    echo "Triage signals to check next (per repo):"
    echo "  - gh api repos/<owner>/<repo>/contents/.github/workflows"
    echo "  - gh api repos/<owner>/<repo>/contents/CODEOWNERS"
    echo "  - gh api repos/<owner>/<repo>/contents/CONTRIBUTING.md"
    echo "  - gh api repos/<owner>/<repo>/contents/SECURITY.md"
}

search_mode_code() {
    local q="$1"
    echo "=== Mode: code | query: $q ==="
    echo ""
    echo "--- High-star repos in topic/language ---"
    gh search repos "$q" --sort stars --limit 25 \
        --archived=false --stars '>=1000' \
        --json fullName,description,stargazersCount,updatedAt,language 2>/dev/null \
        | jq -r '.[] | "\(.stargazersCount)\t\(.language // "?")\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' \
        | column -t -s $'\t' || echo "(no results)"

    echo ""
    echo "Triage signals to check next (per repo):"
    echo "  - tsconfig / biome.json / eslint / ruff / pyproject for idioms"
    echo "  - tests/ or __tests__ layout"
    echo "  - scripts/ or Makefile for workflow automation"
    echo "  - OpenSSF Scorecard (https://securityscorecards.dev/viewer/?uri=github.com/<owner>/<repo>)"
}

search_mode_killer_feature() {
    local q="$1"
    echo "=== Mode: killer-feature | target commercial product: $q ==="
    echo ""
    echo "Premise: OSS clones of a commercial product reveal which features the"
    echo "OSS community considers load-bearing — a strong proxy for what's"
    echo "monetizable. Contributes the 'oss_clone_focus' signal to the bundle's"
    echo "Killer-Feature Convergence Protocol (research-review-mining)."
    echo ""
    echo "--- Direct clone repos ('alternative', 'open source', 'self-hosted') ---"
    for prefix in "alternative to" "open source" "self-hosted"; do
        gh search repos "$prefix $q" --sort stars --limit 10 \
            --archived=false --stars '>=200' \
            --json fullName,description,stargazersCount,updatedAt 2>/dev/null \
            | jq -r --arg p "$prefix" '.[] | "[\($p)] \(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' \
            | column -t -s $'\t' || true
    done

    echo ""
    echo "--- By alternative-topic ---"
    for topic in "${q}-alternative" "alternative-to-${q}"; do
        gh search repos --topic "$topic" --sort stars --limit 10 --archived=false \
            --json fullName,description,stargazersCount,updatedAt 2>/dev/null \
            | jq -r --arg t "$topic" '.[] | "[\($t)] \(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' \
            | column -t -s $'\t' || true
    done

    echo ""
    echo "Triage signals to check next (per repo):"
    echo "  - README.md headline + comparison matrix + 'Limitations vs $q' section"
    echo "  - docs/ or website/ landing pages with 'why $q' framing"
    echo "  - CHANGELOG.md (what shipped first = perceived load-bearing at launch)"
    echo "  - Owner does NOT also sell a hosted commercial version (otherwise downgrade)"
    echo "  - Distinct owner (Convergence Rule counts repos by distinct owner only)"
    echo ""
    echo "Next: scripts/fetch_repo_assets.sh <owner>/<repo> <out> --kind killer-feature"
    echo "Then: feed README to LLM prompts §1/§2 in references/killer-feature-mining.md"
}

if [[ "$AWESOME" -eq 1 ]]; then
    echo "Scanning major awesome lists (triage required — many are LLM-curated as of April 2026):"
    for repo in \
        "VoltAgent/awesome-agent-skills" \
        "ComposioHQ/awesome-claude-skills" \
        "heilcheng/awesome-agent-skills" \
        "skillmatic-ai/awesome-agent-skills" \
        "alirezarezvani/claude-skills"
    do
        stars=$(gh api "repos/$repo" --jq '.stargazers_count' 2>/dev/null || echo "?")
        updated=$(gh api "repos/$repo" --jq '.updated_at[:10]' 2>/dev/null || echo "?")
        echo "★ $stars  $repo  ($updated)"
    done
    echo ""
    echo "Next: gh api repos/<owner>/<repo>/contents/README.md --jq '.content' | base64 -d | grep -i '<your-domain>'"
    exit 0
fi

if [[ -n "$OWNER" ]]; then
    echo "Listing repos for: $OWNER (kind: ${KIND:-any})"
    case "$KIND" in
        skill) PATTERN='[Ss]kill' ;;
        *) PATTERN='.' ;;
    esac
    gh search repos --owner "$OWNER" --limit 100 --archived=false \
        --json fullName,description,stargazersCount,updatedAt 2>/dev/null \
        | jq -r --arg p "$PATTERN" '.[] | select(.fullName | test($p)) | "\(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' \
        | column -t -s $'\t'
    exit 0
fi

[[ -z "$QUERY" ]] && { echo "ERROR: query required (or use --owner / --awesome)" >&2; exit 1; }

case "$KIND" in
    skill)          search_mode_skill "$QUERY" ;;
    practice)       search_mode_practice "$QUERY" ;;
    code)           search_mode_code "$QUERY" ;;
    killer-feature) search_mode_killer_feature "$QUERY" ;;
esac

echo ""
echo "Tips:"
echo "  - Always spot-check 3 random results for LLM-generated content before trusting the list."
echo "  - Cross-check stars with commit-signing ratio and contributor count (gh api repos/<r>/contributors)."
echo "  - Rerun with --owner <author> to narrow to a trusted maintainer."
