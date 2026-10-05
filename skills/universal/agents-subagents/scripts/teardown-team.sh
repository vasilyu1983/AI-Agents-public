#!/usr/bin/env bash
# teardown-team.sh — Explicit legacy cleanup for old Claude Code Agent Team state
#
# Usage:
#   teardown-team.sh [options]
#
# Options:
#   --legacy-cleanup  Explicitly opt in to destructive legacy cleanup
#   --force           Skip confirmation prompts
#   --max-age HOURS   Only clean teams older than HOURS (default: 24)
#   --remove-agents   Also remove canonical-member agent files from ~/.claude/agents/
#
# Examples:
#   teardown-team.sh                         # safe no-op with current guidance
#   teardown-team.sh --legacy-cleanup
#   teardown-team.sh --legacy-cleanup --force --max-age 1

set -euo pipefail

FORCE=false
LEGACY_CLEANUP=false
MAX_AGE_HOURS=24
MAX_AGE_MAX_HOURS=87600
REMOVE_AGENTS=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --legacy-cleanup)
      LEGACY_CLEANUP=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --max-age)
      if [[ $# -lt 2 ]]; then
        echo "Error: --max-age requires an integer number of hours." >&2
        exit 2
      fi
      MAX_AGE_HOURS="$2"
      shift 2
      ;;
    --remove-agents)
      REMOVE_AGENTS=true
      shift
      ;;
    -h|--help)
      head -18 "$0" | grep '^# ' | sed 's/^# //; s/^#$//'
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [[ ! "$MAX_AGE_HOURS" =~ ^[0-9]{1,5}$ ]] || (( 10#$MAX_AGE_HOURS < 1 || 10#$MAX_AGE_HOURS > MAX_AGE_MAX_HOURS )); then
  echo "Error: --max-age must be a positive integer from 1 to $MAX_AGE_MAX_HOURS hours." >&2
  exit 2
fi

if [[ "$LEGACY_CLEANUP" != true ]]; then
  echo "No cleanup performed. Current Claude Code releases clean up Agent Team state automatically."
  echo "Use --legacy-cleanup only to inspect and remove demonstrably stale legacy state."
  echo "Repository team recipes live under ~/.agents/team-recipes/ and are never handled by this script."
  exit 0
fi

TEAMS_DIR="$HOME/.claude/teams"
TASKS_DIR="$HOME/.claude/tasks"

if [[ ! -d "$TEAMS_DIR" ]]; then
  echo "No teams directory found at $TEAMS_DIR"
  exit 0
fi

# Find teams
teams_found=0
teams_cleaned=0
now=$(date +%s)
max_age_seconds=$((MAX_AGE_HOURS * 3600))

echo "Scanning for teams (max age: ${MAX_AGE_HOURS}h)..."
echo ""

for team_dir in "$TEAMS_DIR"/*/; do
  [[ ! -d "$team_dir" ]] && continue
  team_name="$(basename "$team_dir")"
  config_file="$team_dir/config.json"

  if [[ ! -f "$config_file" ]]; then
    echo "  $team_name: no config.json (orphaned directory)"
    age_display="unknown"
  else
    # Try to extract creation time
    if command -v jq &>/dev/null; then
      created_at=$(jq -r '.createdAt // empty' "$config_file" 2>/dev/null || true)
    else
      created_at=""
    fi

    if [[ -n "$created_at" ]]; then
      # Parse ISO timestamp
      created_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${created_at%%.*}" +%s 2>/dev/null || stat -f %m "$config_file" 2>/dev/null || echo "$now")
    else
      created_epoch=$(stat -f %m "$config_file" 2>/dev/null || echo "$now")
    fi

    age_seconds=$((now - created_epoch))
    age_hours=$((age_seconds / 3600))
    age_display="${age_hours}h ago"

    if [[ $age_seconds -lt $max_age_seconds ]]; then
      echo "  $team_name: $age_display (recent, skipping)"
      continue
    fi
  fi

  teams_found=$((teams_found + 1))
  echo "  $team_name: $age_display"

  if [[ "$FORCE" != true ]]; then
    read -rp "    Remove this team? [y/N] " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
      echo "    Skipped."
      continue
    fi
  fi

  # Remove team config
  rm -rf "$team_dir"
  echo "    Removed: $team_dir"

  # Remove associated tasks
  task_dir="$TASKS_DIR/$team_name"
  if [[ -d "$task_dir" ]]; then
    rm -rf "$task_dir"
    echo "    Removed: $task_dir"
  fi

  teams_cleaned=$((teams_cleaned + 1))
done

echo ""
echo "Found $teams_found stale team(s), cleaned $teams_cleaned."

# Optionally remove canonical-member agents
if [[ "$REMOVE_AGENTS" == true ]]; then
  echo ""
  echo "Checking for canonical-member agents in ~/.claude/agents/..."
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  # Canonical members live at <repo>/agents/claude; pwd -P follows a runtime symlink to the repo.
  MEMBERS_DIR="$(cd "$(cd "$SCRIPT_DIR" && pwd -P)/../../../../agents/claude" 2>/dev/null && pwd -P || echo "")"

  if [[ -z "$MEMBERS_DIR" ]]; then
    echo "Could not find members directory."
  else
    removed=0
    for member_file in "$MEMBERS_DIR"/*.md; do
      [[ ! -f "$member_file" ]] && continue
      filename="$(basename "$member_file")"
      target="$HOME/.claude/agents/$filename"
      if [[ -L "$target" ]]; then
        resolved="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve(strict=False))' "$target")"
        case "$resolved" in
          "$MEMBERS_DIR"/*) ;;
          *)
            echo "  Kept agent: $filename (symlink is not installer-owned)"
            continue
            ;;
        esac
      elif [[ -f "$target" ]] && ! cmp -s "$member_file" "$target"; then
        echo "  Kept agent: $filename (locally modified or not installer-owned)"
        continue
      fi
      if [[ -f "$target" || -L "$target" ]]; then
        rm "$target"
        echo "  Removed agent: $filename"
        removed=$((removed + 1))
      fi
    done
    echo "Removed $removed canonical-member agent(s)."
  fi
fi
