#!/bin/bash

# Sync shared skills to all agent platforms (Claude Code, Codex CLI)
# Usage: ./sync-skills.sh [target...]
#
# Targets: claude, agents (default: all)
#   - claude → ~/.claude/skills (Claude Code user skills)
#   - agents → ~/.agents/skills (Codex CLI user skills, per OpenAI docs)
#
# Codex reads skills from ~/.agents/skills, so that is the only Codex target.
# ~/.codex/skills is NOT synced: it predates that convention. It still holds
# externally installed skills (pdf, playwright, playwright-interactive, the
# Cloudflare set), which is why it is left in place rather than deleted.
#
# The claude target also symlinks the library's saved workflows
# (agents/workflows/*.js,
# e.g. build-mvp.js, adversarial-review.js) into ~/.claude/workflows so
# they are invocable from any session, and edits to the canonical file take
# effect everywhere with no re-sync. The repo's own .claude/workflows holds
# relative symlinks to the same canonical files. Same safety rules as skills:
# real files, real directories and foreign symlinks are never overwritten, and
# only symlinks pointing into this repo's workflow source are ever removed.
#
# Examples:
#   ./sync-skills.sh              # sync both
#   ./sync-skills.sh claude       # sync only Claude Code
#   ./sync-skills.sh agents       # sync only Codex (~/.agents/skills)
#
# This is the single implementation; there are no per-target wrappers.
#
# Externally installed skills (plugins, marketplaces, `npx skills add`) land as
# REAL DIRECTORIES, not symlinks. Two rules keep them safe:
#   1. A same-name real directory, plain file, or symlink pointing outside this
#      repo is never overwritten — it is reported as SKIP (foreign ...) and counted.
#   2. Removal only ever touches symlinks that point into THIS repo.
# A symlink pointing anywhere else came from another tool and is left alone,
# even when it is broken.
#
# Portable: works on any computer by deriving paths from script location

set -euo pipefail

# Get the directory where this script lives (scripts/distribution folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Derive AI-Agents root (two levels up: scripts/distribution -> AI-Agents)
AI_AGENTS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source directory. Skills live one level down in group folders:
# skills/universal/<name>, skills/project/<name>, skills/personal/<name>,
# skills/client/<client>/<name>.
# The runtime targets stay flat, so every skill name must be unique across groups.
SKILLS_SOURCE="$AI_AGENTS_ROOT/skills"
SKILL_GROUPS=(universal project personal client/*)

# Former source location (before the 2026-10-03 re-layout). Links into it are
# ours too, so a re-sync replaces them instead of skipping them as foreign.
LEGACY_SKILLS_SOURCE="$AI_AGENTS_ROOT/frameworks/shared-skills/skills"

# Target definitions (parallel arrays for Bash 3.2 compatibility)
ALL_NAMES=(claude agents)
ALL_PATHS=("$HOME/.claude/skills" "$HOME/.agents/skills")

# Guard against parallel-array drift
if [ "${#ALL_NAMES[@]}" -ne "${#ALL_PATHS[@]}" ]; then
    echo "Error: ALL_NAMES (${#ALL_NAMES[@]}) and ALL_PATHS (${#ALL_PATHS[@]}) must be the same length" >&2
    exit 1
fi

# Resolve target name to path
target_path_for() {
    local name="$1"
    for i in "${!ALL_NAMES[@]}"; do
        if [ "${ALL_NAMES[$i]}" = "$name" ]; then
            echo "${ALL_PATHS[$i]}"
            return 0
        fi
    done
    return 1
}

# Determine which targets to sync
if [ $# -gt 0 ]; then
    TARGETS=("$@")
    for t in "${TARGETS[@]}"; do
        if ! target_path_for "$t" >/dev/null 2>&1; then
            echo "Error: Unknown target '$t'. Valid targets: ${ALL_NAMES[*]}" >&2
            exit 1
        fi
    done
else
    TARGETS=("${ALL_NAMES[@]}")
fi

echo "=========================================="
echo "Skills Sync"
echo "=========================================="
echo ""

# Verify source directory exists
if [ ! -d "$SKILLS_SOURCE" ]; then
    echo "Error: Source directory not found: $SKILLS_SOURCE" >&2
    exit 1
fi

# Physical path of the source, so ownership comparison is not defeated by a
# symlinked prefix (/tmp -> /private/tmp and friends).
SKILLS_SOURCE_REAL="$(cd "$SKILLS_SOURCE" && pwd -P)"
AI_AGENTS_ROOT_REAL="$(cd "$AI_AGENTS_ROOT" && pwd -P)"

# Collect the current skill set once: a directory is a skill only if it carries
# SKILL.md. The runtimes ignore a directory without one, so linking it costs
# nothing visible but leaves a bogus entry (and a broken link once it goes away).
CURRENT_SKILLS=()
CURRENT_PATHS=()
for group in "${SKILL_GROUPS[@]}"; do
    for skill_dir in "$SKILLS_SOURCE"/$group/*/; do
        [ -f "${skill_dir}SKILL.md" ] || continue
        name="$(basename "$skill_dir")"
        for seen in "${CURRENT_SKILLS[@]+"${CURRENT_SKILLS[@]}"}"; do
            if [ "$seen" = "$name" ]; then
                echo "Error: skill name '$name' exists in more than one group; runtime folders are flat" >&2
                exit 1
            fi
        done
        CURRENT_SKILLS+=("$name")
        CURRENT_PATHS+=("$(cd "$skill_dir" && pwd -P)")
    done
done

if [ "${#CURRENT_SKILLS[@]}" -eq 0 ]; then
    echo "Error: no skills (directories containing SKILL.md) found in $SKILLS_SOURCE" >&2
    echo "Refusing to sync — this would look like every skill was deleted." >&2
    exit 1
fi

echo "Source: $SKILLS_SOURCE"
echo "Skills: ${#CURRENT_SKILLS[@]}"
echo ""

# Is this name in the current skill set?
is_current_skill() {
    local needle="$1" name
    for name in "${CURRENT_SKILLS[@]}"; do
        [ "$name" = "$needle" ] && return 0
    done
    return 1
}

# Is this symlink one WE created — i.e. does it point into the shared-skills
# skills/ directory? Only those are ours to remove.
#
# Deliberately narrower than "somewhere in the AI-Agents repo": a link into any
# other part of the repo was put there by something else, and a target directory
# that happens to live inside the repo would otherwise make every sibling alias
# in it look like ours.
#
# A symlink's target is interpreted relative to the LINK's directory, not the
# caller's cwd — so resolution anchors on dirname "$link". We canonicalise the
# target's PARENT and re-append its basename: canonicalising the target itself
# would follow a final symlink hop, and dropping the basename would answer a
# question about the wrong path entirely.
is_repo_owned_link() {
    local link="$1" raw parent base resolved
    raw="$(readlink "$link")"

    # Fast path: absolute target already under the skills source (current or legacy).
    case "$raw" in
        "$SKILLS_SOURCE"/*|"$SKILLS_SOURCE_REAL"/*) return 0 ;;
        "$LEGACY_SKILLS_SOURCE"/*|"$AI_AGENTS_ROOT_REAL/frameworks/shared-skills/skills"/*) return 0 ;;
    esac

    # Any other absolute target is not ours. Deciding this here keeps the
    # relative-resolution below from mixing in the link's own directory.
    case "$raw" in
        /*) return 1 ;;
    esac

    # Relative target: resolve against the link's directory.
    parent="$(dirname "$raw")"
    base="$(basename "$raw")"
    resolved="$(cd "$(dirname "$link")" 2>/dev/null && cd "$parent" 2>/dev/null && pwd -P || true)"
    [ -n "$resolved" ] || return 1
    [ "$base" = "." ] || resolved="$resolved/$base"

    case "$resolved" in
        "$SKILLS_SOURCE_REAL"/*) return 0 ;;
        "$AI_AGENTS_ROOT_REAL/frameworks/shared-skills/skills"/*) return 0 ;;
    esac
    return 1
}

# What kind of foreign entry sits at a path, for the SKIP line.
foreign_kind() {
    if [ -L "$1" ]; then
        echo "symlink"
    elif [ -d "$1" ]; then
        echo "directory"
    else
        echo "file"
    fi
}

# Sync skills to a single target directory
sync_to_target() {
    local name="$1"
    local target_dir="$2"

    echo "── $name → $target_dir"

    mkdir -p "$target_dir"

    # Link every current skill
    local linked=0 skipped=0 skill_name target_path i
    for i in "${!CURRENT_SKILLS[@]}"; do
        skill_name="${CURRENT_SKILLS[$i]}"
        target_path="$target_dir/$skill_name"
        if [ -L "$target_path" ] && is_repo_owned_link "$target_path"; then
            rm "$target_path"
        elif [ -L "$target_path" ] || [ -e "$target_path" ]; then
            echo "   SKIP (foreign $(foreign_kind "$target_path")): $skill_name"
            skipped=$((skipped + 1))
            continue
        fi
        ln -s "${CURRENT_PATHS[$i]}" "$target_path"
        linked=$((linked + 1))
    done

    # Reclaim stale links: repo-owned but no longer a current skill (renamed,
    # removed, moved out of skills/, or lost its SKILL.md). Symlinks pointing
    # outside the repo belong to another tool and are never touched, broken or not.
    local stale=0 link base
    shopt -s nullglob dotglob
    for link in "$target_dir"/*; do
        [ -L "$link" ] || continue
        base="$(basename "$link")"
        is_current_skill "$base" && continue
        is_repo_owned_link "$link" || continue
        if [ ! -e "$link" ]; then
            echo "   Removing broken symlink: $base"
            rm "$link"
            stale=$((stale + 1))
        else
            echo "   Removing stale repo symlink: $base -> $(readlink "$link")"
            rm "$link"
            stale=$((stale + 1))
        fi
    done
    shopt -u nullglob dotglob

    # Count what the runtime will actually see: symlinks to dirs + real dirs
    local total
    total="$(find "$target_dir" -maxdepth 1 -mindepth 1 \( -type d -o -type l \) -exec test -d {} \; -print 2>/dev/null | wc -l | tr -d ' ')"
    echo "   Linked: $linked | External skipped: $skipped | Stale removed: $stale | Total visible: $total"
    echo ""
}

# Keep the repository launch surface repo-relative so a clone remains portable.
# Only canonical .js workflows are linked; tests remain beside their sources.
sync_workflows_repo() {
    local source_dir="$AI_AGENTS_ROOT/agents/workflows"
    local target_dir="$AI_AGENTS_ROOT/.claude/workflows"
    local relative_prefix="../../agents/workflows"
    # Former location (before the 2026-10-03 re-layout); links into it are ours.
    local legacy_prefix="../../frameworks/shared-skills/skills/agents-subagents/assets/workflows"

    [ -d "$source_dir" ] || return 0
    mkdir -p "$target_dir"

    local src base target_path raw
    shopt -s nullglob
    for src in "$source_dir"/*.js; do
        base="$(basename "$src")"
        target_path="$target_dir/$base"
        raw=""
        [ -L "$target_path" ] && raw="$(readlink "$target_path")"
        case "$raw" in
            "$relative_prefix"/*|"$legacy_prefix"/*) rm "$target_path" ;;
            *)
                if [ -L "$target_path" ] || [ -e "$target_path" ]; then
                    echo "   SKIP repo workflow (foreign $(foreign_kind "$target_path")): $base"
                    continue
                fi
                ;;
        esac
        ln -s "$relative_prefix/$base" "$target_path"
    done

    for target_path in "$target_dir"/*; do
        [ -L "$target_path" ] || continue
        raw="$(readlink "$target_path")"
        case "$raw" in
            "$relative_prefix"/*)
                [ -e "$target_path" ] || rm "$target_path"
                ;;
        esac
    done
    shopt -u nullglob
}

# Sync saved workflows (canonical: agents-subagents assets/workflows/*.js) to
# ~/.claude/workflows. Only .js workflow scripts are linked — .mjs test files
# and anything else in the source directory stay repo-local.
sync_workflows_claude() {
    local source_dir="$AI_AGENTS_ROOT/agents/workflows"
    local target_dir="$HOME/.claude/workflows"

    [ -d "$source_dir" ] || return 0
    sync_workflows_repo
    local source_real
    source_real="$(cd "$source_dir" && pwd -P)"
    local legacy_dir="$AI_AGENTS_ROOT/frameworks/shared-skills/skills/agents-subagents/assets/workflows"

    echo "── workflows → $target_dir"
    mkdir -p "$target_dir"

    local linked=0 skipped=0 stale=0 src base target_path link raw
    shopt -s nullglob
    for src in "$source_dir"/*.js; do
        base="$(basename "$src")"
        target_path="$target_dir/$base"
        raw=""
        [ -L "$target_path" ] && raw="$(readlink "$target_path")"
        case "$raw" in
            "$source_real"/*|"$source_dir"/*|"$legacy_dir"/*|"$AI_AGENTS_ROOT_REAL/frameworks/shared-skills/skills/agents-subagents/assets/workflows"/*) rm "$target_path" ;;
            *)
                if [ -L "$target_path" ] || [ -e "$target_path" ]; then
                    echo "   SKIP (foreign $(foreign_kind "$target_path")): $base"
                    skipped=$((skipped + 1))
                    continue
                fi
                ;;
        esac
        ln -s "$source_real/$base" "$target_path"
        linked=$((linked + 1))
    done

    # Reclaim symlinks we own that no longer resolve (workflow renamed/removed).
    for link in "$target_dir"/*; do
        [ -L "$link" ] || continue
        raw="$(readlink "$link")"
        case "$raw" in
            "$source_real"/*|"$source_dir"/*|"$legacy_dir"/*|"$AI_AGENTS_ROOT_REAL/frameworks/shared-skills/skills/agents-subagents/assets/workflows"/*)
                if [ ! -e "$link" ]; then
                    echo "   Removing broken workflow symlink: $(basename "$link")"
                    rm "$link"
                    stale=$((stale + 1))
                fi
                ;;
        esac
    done
    shopt -u nullglob

    echo "   Linked: $linked | External skipped: $skipped | Stale removed: $stale"
    echo ""
}

# Run sync for each selected target
for target in "${TARGETS[@]}"; do
    sync_to_target "$target" "$(target_path_for "$target")"
    if [ "$target" = "claude" ]; then
        sync_workflows_claude
    fi
done

echo "=========================================="
echo "Sync complete!"
echo "=========================================="
