#!/usr/bin/env bash
# search_repos.sh — discover public GitHub repos across four modes
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
# Filters: archived=false in every mode. Star floors (gh --stars filters, it
# does not only sort): practice >=500, code >=1000, killer-feature direct
# clones >=200. Skill, owner and topic searches have no star floor.
#
# Exit codes: 0 = searches ran (a search with no matches prints "(no results)");
# 1 = usage error or any gh failure (rate limit, auth, network). gh's error is
# printed; check your remaining budget with: gh api rate_limit
#
# Requires: gh CLI (https://cli.github.com/) authenticated + jq.

set -euo pipefail

usage() {
    local rc="${1:-0}"
    if [[ "$rc" -eq 0 ]]; then
        sed -n '2,33p' "$0" | sed 's/^# \{0,1\}//'
    else
        sed -n '2,33p' "$0" | sed 's/^# \{0,1\}//' >&2
    fi
    exit "$rc"
}

KIND=""
OWNER=""
AWESOME=0
QUERY=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) usage 0 ;;
        --kind) KIND="${2:?--kind requires a value}"; shift 2 ;;
        --owner) OWNER="${2:?--owner requires a value}"; shift 2 ;;
        --awesome) AWESOME=1; shift ;;
        *) QUERY="${QUERY}${QUERY:+ }$1"; shift ;;
    esac
done

if [[ -z "$KIND" && "$AWESOME" -eq 0 && -z "$OWNER" ]]; then
    echo "ERROR: --kind is required (skill | practice | code | killer-feature), or use --owner / --awesome" >&2
    usage 1
fi

case "$KIND" in
    skill|practice|code|killer-feature|"") ;;
    *) echo "ERROR: --kind must be one of: skill, practice, code, killer-feature" >&2; exit 1 ;;
esac

if ! command -v gh &> /dev/null; then
    echo "ERROR: gh CLI not found. Install from https://cli.github.com/" >&2
    exit 1
fi
if ! command -v jq &> /dev/null; then
    echo "ERROR: jq not found" >&2
    exit 1
fi
if ! gh auth status &> /dev/null; then
    echo "ERROR: gh not authenticated. Run: gh auth login" >&2
    exit 1
fi

# Bare mktemp ignores TMPDIR on macOS; pass a template so sandboxed runs work.
ERR_FILE=$(mktemp "${TMPDIR:-/tmp}/search_repos.XXXXXX")
trap 'rm -f "$ERR_FILE"' EXIT

# gh_fail <what> — report gh's own error and stop. Never swallow a failed call:
# a rate-limited search must not look like an empty result.
gh_fail() {
    echo "ERROR: $1 failed: $(tr '\n' ' ' < "$ERR_FILE")" >&2
    echo "Check your remaining budget with: gh api rate_limit" >&2
    exit 1
}

# gh_search <gh search repos args...> — runs one search into SEARCH_OUT.
# Call it directly (not inside $(...)) so its exit reaches the script.
SEARCH_OUT=""
gh_search() {
    SEARCH_OUT=$(gh search repos "$@" 2>"$ERR_FILE") || gh_fail "gh search repos $*"
}

# print_rows <jq filter> [jq args...] — renders SEARCH_OUT, or "(no results)".
print_rows() {
    local filter="$1"; shift
    local n
    n=$(jq 'length' <<<"$SEARCH_OUT")
    if [[ "$n" -eq 0 ]]; then
        echo "(no results)"
        return 0
    fi
    jq -r "$@" "$filter" <<<"$SEARCH_OUT" | column -t -s $'\t'
}

ROW='.[] | "\(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"'

# Mode-specific search-topic hints and header signals
search_mode_skill() {
    local q="$1"
    echo "=== Mode: skill | query: $q ==="
    echo ""
    echo "--- By topic agent-skills (noisy, triage required) ---"
    gh_search --topic agent-skills "$q" --sort stars --limit 20 --archived=false \
        --json fullName,description,stargazersCount,updatedAt
    print_rows "$ROW"

    echo ""
    echo "--- By topic claude-skills / codex-skills (narrower, higher signal) ---"
    for topic in claude-skills codex-skills; do
        gh_search --topic "$topic" "$q" --sort stars --limit 10 --archived=false \
            --json fullName,description,stargazersCount,updatedAt
        print_rows '.[] | "[\($t)] \(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' --arg t "$topic"
    done

    echo ""
    echo "--- By name pattern (*-agent-skill, *-skills) ---"
    gh_search "$q agent-skill" --sort stars --limit 15 --archived=false \
        --json fullName,description,stargazersCount,updatedAt
    print_rows "$ROW"
}

search_mode_practice() {
    local q="$1"
    echo "=== Mode: practice | query: $q ==="
    echo ""
    echo "--- Repos with >=500 stars matching query (CI/PR signal candidates) ---"
    gh_search "$q" --sort stars --limit 25 --archived=false --stars '>=500' \
        --json fullName,description,stargazersCount,updatedAt
    print_rows "$ROW"

    echo ""
    echo "Triage signals to check next (per repo):"
    echo "  - gh api repos/<owner>/<repo>/contents/.github/workflows"
    echo "  - gh api repos/<owner>/<repo>/contents/CODEOWNERS"
    echo "  - gh api repos/<owner>/<repo>/contents/CONTRIBUTING.md"
    echo "  - gh api repos/<owner>/<repo>/contents/SECURITY.md"
    echo "  - sample ~20 recently merged PRs to confirm the practice is enforced, not just configured"
    echo "  - compare the repo's contributor count and PR volume to the target team before transplanting"
}

search_mode_code() {
    local q="$1"
    echo "=== Mode: code | query: $q ==="
    echo ""
    echo "--- Repos with >=1000 stars in topic/language ---"
    gh_search "$q" --sort stars --limit 25 --archived=false --stars '>=1000' \
        --json fullName,description,stargazersCount,updatedAt,language
    print_rows '.[] | "\(.stargazersCount)\t\(.language // "?")\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"'

    echo ""
    echo "Triage signals to check next (per repo):"
    echo "  - tsconfig / biome.json / eslint / ruff / pyproject for idioms"
    echo "  - tests/ or __tests__ layout"
    echo "  - scripts/ or Makefile for workflow automation"
    echo "  - OpenSSF Scorecard, if published (https://securityscorecards.dev/viewer/?uri=github.com/<owner>/<repo>), or run the scorecard CLI"
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
    echo "--- Direct clone repos with >=200 stars ('alternative', 'open source', 'self-hosted') ---"
    for prefix in "alternative to" "open source" "self-hosted"; do
        gh_search "$prefix $q" --sort stars --limit 10 --archived=false --stars '>=200' \
            --json fullName,description,stargazersCount,updatedAt
        print_rows '.[] | "[\($p)] \(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' --arg p "$prefix"
    done

    echo ""
    echo "--- By alternative-topic ---"
    for topic in "${q}-alternative" "alternative-to-${q}"; do
        gh_search --topic "$topic" --sort stars --limit 10 --archived=false \
            --json fullName,description,stargazersCount,updatedAt
        print_rows '.[] | "[\($t)] \(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' --arg t "$topic"
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
    echo "Scanning major awesome lists (triage required — many are LLM-curated and list dead repos):"
    for repo in \
        "VoltAgent/awesome-agent-skills" \
        "ComposioHQ/awesome-claude-skills" \
        "heilcheng/awesome-agent-skills" \
        "skillmatic-ai/awesome-agent-skills" \
        "alirezarezvani/claude-skills"
    do
        meta=$(gh api "repos/$repo" --jq '"\(.stargazers_count)\t\(.updated_at[:10])"' 2>"$ERR_FILE") \
            || gh_fail "gh api repos/$repo"
        echo "★ ${meta%%$'\t'*}  $repo  (${meta#*$'\t'})"
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
    gh_search --owner "$OWNER" --limit 100 --archived=false \
        --json fullName,description,stargazersCount,updatedAt
    print_rows '.[] | select(.fullName | test($p)) | "\(.stargazersCount)\t\(.fullName)\t\(.updatedAt[:10])\t\(.description // "—")"' --arg p "$PATTERN"
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
echo "  - Cross-check stars with commit history, outside contributors, and contributor count (gh api repos/<r>/contributors)."
echo "  - Rerun with --owner <author> to narrow to a trusted maintainer."
