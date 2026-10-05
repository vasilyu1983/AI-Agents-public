#!/usr/bin/env bash
# deploy-all-teams.sh — Roll out every repository team recipe and its members into
# user-level or project-level Claude Code and/or Codex agent folders.
#
# Portable: resolves repo path from the script location and writes to
# $HOME, so it works on any machine regardless of username.
#
# Usage:
#   deploy-all-teams.sh [options]
#
# Options:
#   --platform claude|codex|both   Which platform(s) to deploy to (default: both)
#   --user                         Deploy into ~/.claude or ~/.codex (default)
#   --project                      Deploy into .claude or .codex under the current repo
#   --repo PATH                    Deploy into PATH/.claude or PATH/.codex
#   --include-opt-in               Also deploy teams marked `install: opt-in`
#   --include-candidates           Also install expansion-gate candidate specialists
#   --refresh-installed-managed   Refresh only existing, unchanged files in the ownership ledger
#   --confirm-bulk-deploy          Confirm this administrative catalog-wide write operation
#   --dry-run                      Show what would be deployed, change nothing
#   --remove                       Remove all teams instead of installing them
#   --no-prune                     Skip cleanup of orphaned/broken agents after install
#   --quiet                        Only print the final summary
#   -h, --help                     Show this help
#
# Examples:
#   ./deploy-all-teams.sh --dry-run                # safe preview; writes nothing
#   ./deploy-all-teams.sh --confirm-bulk-deploy    # deploy all default teams administratively
#   ./deploy-all-teams.sh --confirm-bulk-deploy --platform claude    # Claude only, user-level
#   ./deploy-all-teams.sh --confirm-bulk-deploy --project            # deploy into this repo
#   ./deploy-all-teams.sh --confirm-bulk-deploy --repo /path/to/repo # deploy into another repo
#   ./deploy-all-teams.sh --confirm-bulk-deploy --include-opt-in     # include opt-in teams
#   ./deploy-all-teams.sh --refresh-installed-managed --dry-run       # preview safe managed refresh
#   ./deploy-all-teams.sh --dry-run                # preview without writing
#   ./deploy-all-teams.sh --remove --platform both # tear everything down
#
# Sync rule: if you edit any member or repository team recipe, rerun this
# script to push changes to the global folders. Skill discovery is handled
# separately through the runtime's configured skill locations; only deployed
# agents and repository recipe metadata need a manual redeploy from this script.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY="$SCRIPT_DIR/deploy-preset.sh"
# The agent catalog lives at <repo>/agents/{claude,codex,teams}, outside this
# skill. Resolve the physical script folder (pwd -P) so a runtime symlink still
# finds the repository.
REPO_ROOT="$(cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/../../../.." && pwd)"
TEAMS_DIR="$(cd "$REPO_ROOT/agents/teams" && pwd)"
MEMBERS_DIR="$(cd "$REPO_ROOT/agents" && pwd)"

# Resolve a Python interpreter that ships tomllib (3.11+). Honour PYTHON_BIN when the
# caller sets it; otherwise probe common names so a 3.9 system python3 does not break
# the TOML-reading heredocs below.
resolve_python() {
  local candidate
  for candidate in "${PYTHON_BIN:-}" python3 python3.14 python3.13 python3.12 python3.11; do
    [[ -n "$candidate" ]] || continue
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import tomllib' >/dev/null 2>&1; then
      command -v "$candidate"
      return 0
    fi
  done
  echo "Error: no Python 3.11+ interpreter with tomllib found; set PYTHON_BIN=/path/to/python3.11+" >&2
  return 1
}
PYTHON_BIN="$(resolve_python)"
export PYTHON_BIN

PLATFORM="both"
SCOPE="user"
REPO_PATH=""
INCLUDE_OPT_IN=false
INCLUDE_CANDIDATES=false
REFRESH_INSTALLED_MANAGED=false
CONFIRM_BULK_DEPLOY=false
DRY_RUN=false
REMOVE=false
QUIET=false
PRUNE=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    --user)
      SCOPE="user"
      shift
      ;;
    --project)
      SCOPE="project"
      shift
      ;;
    --repo)
      SCOPE="repo"
      REPO_PATH="$2"
      shift 2
      ;;
    --include-opt-in)
      INCLUDE_OPT_IN=true
      shift
      ;;
    --include-candidates)
      INCLUDE_CANDIDATES=true
      shift
      ;;
    --refresh-installed-managed)
      REFRESH_INSTALLED_MANAGED=true
      shift
      ;;
    --confirm-bulk-deploy)
      CONFIRM_BULK_DEPLOY=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --remove)
      REMOVE=true
      shift
      ;;
    --no-prune)
      PRUNE=false
      shift
      ;;
    --quiet)
      QUIET=true
      shift
      ;;
    -h|--help)
      head -30 "$0" | grep '^#' | sed 's/^# \?//'
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Run with --help for usage." >&2
      exit 1
      ;;
  esac
done

if [[ "$REFRESH_INSTALLED_MANAGED" == true ]] && {
  [[ "$REMOVE" == true ]] || [[ "$INCLUDE_OPT_IN" == true ]] ||
  [[ "$INCLUDE_CANDIDATES" == true ]] || [[ "$PRUNE" != true ]];
}; then
  echo "Error: --refresh-installed-managed cannot be combined with --remove, --include-opt-in, --include-candidates, or --no-prune." >&2
  exit 2
fi

if [[ "$DRY_RUN" != true && "$REMOVE" != true && "$CONFIRM_BULK_DEPLOY" != true ]]; then
  if [[ "$REFRESH_INSTALLED_MANAGED" == true ]]; then
    echo "Refusing managed-file refresh without --confirm-bulk-deploy." >&2
  else
    echo "Refusing catalog-wide installation without --confirm-bulk-deploy." >&2
  fi
  echo "Use --dry-run to preview, or deploy one selected team with deploy-preset.sh." >&2
  exit 2
fi

if [[ ! -x "$DEPLOY" ]]; then
  echo "Error: deploy-preset.sh not found or not executable at $DEPLOY" >&2
  exit 1
fi

if [[ "$SCOPE" == "repo" ]]; then
  [[ -n "$REPO_PATH" ]] || { echo "Error: --repo requires a path" >&2; exit 1; }
  REPO_PATH="$(cd "$REPO_PATH" 2>/dev/null && pwd)" || {
    echo "Error: Repo path '$REPO_PATH' does not exist" >&2
    exit 1
  }
fi

case "$PLATFORM" in
  claude|codex|both) ;;
  *)
    echo "Error: --platform must be claude, codex, or both (got: $PLATFORM)" >&2
    exit 1
    ;;
esac

refresh_installed_managed() {
  local platform="$1"
  local scope_base target_root target_dir ledger plan_file
  local scope_args=("--user")
  case "$SCOPE" in
    user)
      scope_base="$HOME"
      target_root="$HOME/.${platform}"
      ;;
    project)
      scope_base="$(pwd)"
      target_root="$(pwd)/.${platform}"
      scope_args=("--project")
      ;;
    repo)
      scope_base="$REPO_PATH"
      target_root="$REPO_PATH/.${platform}"
      scope_args=("--repo" "$REPO_PATH")
      ;;
  esac
  target_dir="$target_root/agents"
  ledger="$scope_base/.agents/team-recipes/$platform/managed-members.tsv"

  if [[ ! -e "$ledger" && ! -L "$ledger" ]]; then
    $QUIET || echo "[$platform] no managed member ledger; nothing to refresh"
    echo "$platform: refreshed=0 dry_run=0 skipped=0 failed=0"
    return 0
  fi

  plan_file="$(mktemp "${TMPDIR:-/tmp}/deploy-all-teams.plan.XXXXXX")"
  if ! "$PYTHON_BIN" - <<'PY' "$ledger" "$target_dir" "$platform" "$MEMBERS_DIR" > "$plan_file"; then
import hashlib
import os
from pathlib import Path
import re
import stat
import sys

ledger_arg, target_arg, platform, members_arg = sys.argv[1:]
ledger = Path(ledger_arg)
target_dir = Path(target_arg)
members = Path(members_arg)

flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
try:
    fd = os.open(ledger, flags)
except OSError as exc:
    raise SystemExit(f"unsafe managed member ledger {ledger}: {exc}")
try:
    info = os.fstat(fd)
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or info.st_nlink != 1 or info.st_size > 1024 * 1024):
        raise SystemExit(f"unsafe managed member ledger {ledger}")
    payload = os.read(fd, info.st_size + 1)
finally:
    os.close(fd)

try:
    lines = payload.decode("utf-8").splitlines()
except UnicodeError as exc:
    raise SystemExit(f"invalid managed member ledger {ledger}: {exc}")

seen = set()
entries = []
for line in lines:
    fields = line.split("\t")
    if len(fields) != 2:
        raise SystemExit(f"invalid managed member ledger row: {line!r}")
    filename, expected = fields
    pattern = r"([a-z0-9][a-z0-9-]*)\.md" if platform == "claude" else r"([a-z0-9][a-z0-9_]*)\.toml"
    match = re.fullmatch(pattern, filename)
    if match is None or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
        raise SystemExit(f"invalid managed member ledger row: {line!r}")
    if filename in seen:
        raise SystemExit(f"duplicate managed member ledger key: {filename}")
    seen.add(filename)
    member_id = match.group(1).replace("_", "-")
    entries.append((filename, expected, member_id))

for filename, expected, member_id in entries:
    target = target_dir / filename
    canonical = members / platform / filename
    if not canonical.is_file():
        print("unknown", member_id, filename, sep="\t")
        continue
    try:
        info = target.lstat()
    except FileNotFoundError:
        print("missing", member_id, filename, sep="\t")
        continue
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
        print("unsafe", member_id, filename, sep="\t")
        continue
    if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        print("modified", member_id, filename, sep="\t")
        continue
    print("refresh", member_id, filename, sep="\t")
PY
    rm -f "$plan_file"
    return 1
  fi

  local status member_id filename
  local refreshed=0 dry_run_count=0 skipped=0 failed=0
  while IFS=$'\t' read -r status member_id filename; do
    [[ -n "$status" ]] || continue
    case "$status" in
      refresh)
        if [[ "$DRY_RUN" == true ]]; then
          dry_run_count=$((dry_run_count + 1))
          $QUIET || echo "  [dry-run] refresh $platform:$filename"
        elif "$DEPLOY" "$member_id" --member --platform "$platform" "${scope_args[@]}" --refresh-managed >/dev/null 2>&1; then
          refreshed=$((refreshed + 1))
          $QUIET || echo "  refreshed $platform:$filename"
        else
          failed=$((failed + 1))
          $QUIET || echo "  FAILED    $platform:$filename" >&2
        fi
        ;;
      missing|modified|unsafe|unknown)
        skipped=$((skipped + 1))
        $QUIET || echo "  skipped   $platform:$filename ($status)"
        ;;
      *)
        rm -f "$plan_file"
        echo "Error: unexpected refresh plan status '$status'" >&2
        return 1
        ;;
    esac
  done < "$plan_file"
  rm -f "$plan_file"
  echo "$platform: refreshed=$refreshed dry_run=$dry_run_count skipped=$skipped failed=$failed"
  [[ "$failed" -eq 0 ]]
}

if [[ "$REFRESH_INSTALLED_MANAGED" == true ]]; then
  REFRESH_PLATFORMS=()
  case "$PLATFORM" in
    claude) REFRESH_PLATFORMS=(claude) ;;
    codex) REFRESH_PLATFORMS=(codex) ;;
    both) REFRESH_PLATFORMS=(claude codex) ;;
  esac
  $QUIET || echo "Refreshing existing unchanged installer-owned members only"
  refresh_failures=0
  for refresh_platform in "${REFRESH_PLATFORMS[@]}"; do
    if ! refresh_installed_managed "$refresh_platform"; then
      refresh_failures=$((refresh_failures + 1))
    fi
  done
  [[ "$refresh_failures" -eq 0 ]]
  exit
fi

if [[ ! -d "$TEAMS_DIR" ]]; then
  echo "Error: teams directory not found at $TEAMS_DIR" >&2
  exit 1
fi

# Discover teams from the catalog so the script never drifts when teams
# are added or removed. Each team lives in its own directory containing
# team.yaml. Uses `while read` for portability with macOS bash 3.2.
TEAMS=()
while IFS= read -r line; do
  TEAMS+=("$line")
done < <(
  find "$TEAMS_DIR" -mindepth 2 -maxdepth 2 -name 'team.yaml' \
    -exec dirname {} \; \
    | xargs -n1 basename \
    | sort
)

if [[ ${#TEAMS[@]} -eq 0 ]]; then
  echo "Error: no teams discovered under $TEAMS_DIR" >&2
  exit 1
fi

# Filter out opt-in teams unless explicitly requested. Teams with
# `install: opt-in` in team.yaml are project-specific and excluded from the
# default bulk rollout to avoid cluttering general registries.
FILTERED_TEAMS=()
SKIPPED_OPT_IN=()
for team in "${TEAMS[@]}"; do
  manifest="$TEAMS_DIR/$team/team.yaml"
  install_mode="$(sed -n 's/^install:[[:space:]]*//p' "$manifest" | head -n 1)"
  install_mode="${install_mode%%[[:space:]]*}"
  if [[ "$install_mode" == "opt-in" && "$INCLUDE_OPT_IN" != true && "$REMOVE" != true ]]; then
    SKIPPED_OPT_IN+=("$team")
    continue
  fi
  FILTERED_TEAMS+=("$team")
done
TEAMS=("${FILTERED_TEAMS[@]}")

if [[ ${#TEAMS[@]} -eq 0 ]]; then
  echo "Error: no installable team recipes remain after filtering opt-in entries" >&2
  exit 1
fi

# Resolve which platforms we touch this run.
PLATFORMS=()
case "$PLATFORM" in
  claude) PLATFORMS=(claude) ;;
  codex)  PLATFORMS=(codex) ;;
  both)   PLATFORMS=(claude codex) ;;
esac

ACTION="install"
$REMOVE && ACTION="remove"

scope_target() {
  local platform="$1"
  case "$SCOPE" in
    user)
      printf '%s' "$HOME/.${platform}"
      ;;
    project)
      printf '%s' "$(pwd)/.${platform}"
      ;;
    repo)
      printf '%s' "$REPO_PATH/.${platform}"
      ;;
  esac
}

scope_base() {
  case "$SCOPE" in
    user) printf '%s' "$HOME" ;;
    project) printf '%s' "$(pwd)" ;;
    repo) printf '%s' "$REPO_PATH" ;;
  esac
}

if ! $QUIET; then
  echo "deploy-all-teams.sh"
  echo "  repo:       $REPO_ROOT"
  echo "  teams dir:  $TEAMS_DIR"
  echo "  platforms:  ${PLATFORMS[*]}"
  echo "  scope:      $SCOPE"
  [[ "$SCOPE" == "repo" ]] && echo "  target repo: $REPO_PATH"
  echo "  include opt-in: $INCLUDE_OPT_IN"
  echo "  include candidates: $INCLUDE_CANDIDATES"
  echo "  prune orphans:  $PRUNE"
  echo "  action:     $ACTION$($DRY_RUN && echo " (dry-run)")"
  echo "  team count: ${#TEAMS[@]}"
  if [[ "$INCLUDE_OPT_IN" != true && ${#SKIPPED_OPT_IN[@]} -gt 0 ]]; then
    echo "  skipped (install: opt-in, install explicitly via deploy-preset.sh):"
    for team in "${SKIPPED_OPT_IN[@]}"; do
      echo "    - $team"
    done
  fi
  echo ""
fi

deploy_one() {
  local team="$1"
  local platform="$2"
  local scope_args=("--user")
  case "$SCOPE" in
    project)
      scope_args=("--project")
      ;;
    repo)
      scope_args=("--repo" "$REPO_PATH")
      ;;
  esac
  # Refresh only files previously recorded as installer-owned and unchanged.
  # A coincidentally matching filename must never authorize an overwrite.
  local args=("$team" "--platform" "$platform" "${scope_args[@]}" "--refresh-managed")
  $INCLUDE_CANDIDATES && args+=("--include-candidates")
  $REMOVE && args=("$team" "--platform" "$platform" "--user" "--remove")
  if $REMOVE; then
    case "$SCOPE" in
      project)
        args=("$team" "--platform" "$platform" "--project" "--remove")
        ;;
      repo)
        args=("$team" "--platform" "$platform" "--repo" "$REPO_PATH" "--remove")
        ;;
    esac
  fi

  if $DRY_RUN; then
    echo "  [dry-run] $DEPLOY ${args[*]}"
    return 0
  fi

  if "$DEPLOY" "${args[@]}" >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

prune_orphans() {
  # Remove deployed agents that are either broken symlinks or no longer
  # referenced by any deployed team's .members manifest. Three decay modes
  # are handled: stale .members files (teams removed from the catalog or
  # made opt-in), stale recipe directories, source files renamed in the catalog
  # (leaving broken symlinks), and agents removed from every team recipe. Member ids
  # are normalized to dashed form since Codex filenames use snake_case.
  local platform="$1"
  local target_root="$2"
  local target_dir="$target_root/agents"
  local meta_dir="$(scope_base)/.agents/team-recipes/$platform"
  local managed_index="$meta_dir/managed-members.tsv"
  local managed_recipes="$meta_dir/managed-recipes.tsv"
  local member_source_dir="$MEMBERS_DIR/$platform"
  local ext="md"
  [[ "$platform" == "codex" ]] && ext="toml"

  [[ -d "$target_dir" ]] || { echo "0 0 0 0"; return 0; }

  managed_file_matches() {
    local ledger="$1"
    local key="$2"
    local file="$3"
    local mode="${4:-check}"
    "$PYTHON_BIN" - <<'PY' "$ledger" "$key" "$file" "$mode"
import hashlib
import os
import re
import stat
import sys

ledger_path, key, target_path, mode = sys.argv[1:]

def read_regular(path: str, limit: int = 1024 * 1024) -> bytes:
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or info.st_nlink != 1 or info.st_size > limit):
            raise OSError("unsafe managed file")
        data = bytearray()
        while True:
            chunk = os.read(fd, min(65536, limit + 1 - len(data)))
            if not chunk:
                return bytes(data)
            data.extend(chunk)
            if len(data) > limit:
                raise OSError("managed file is too large")
    finally:
        os.close(fd)

try:
    ledger = read_regular(ledger_path).decode("utf-8")
    expected = None
    for line in ledger.splitlines():
        name, separator, checksum = line.partition("\t")
        if name == key and separator and re.fullmatch(r"[0-9a-f]{64}", checksum):
            expected = checksum
    if expected is None:
        raise OSError("missing ownership record")
    target = read_regular(target_path)
    if hashlib.sha256(target).hexdigest() != expected:
        raise OSError("managed checksum mismatch")
    if mode == "members":
        lines = target.decode("utf-8").splitlines()
        if (len(lines) > 4096
                or any(re.fullmatch(r"[a-z0-9][a-z0-9-]*", line) is None for line in lines)):
            raise OSError("invalid members index")
        if lines:
            print("\n".join(lines))
    elif mode != "check":
        raise OSError("unknown validation mode")
    raise SystemExit(0)
except (OSError, UnicodeError):
    raise SystemExit(1)
PY
  }

  read_managed_members() {
    local key="$1"
    local file="$2"
    managed_file_matches "$managed_recipes" "$key" "$file" members
  }

  forget_managed_key() {
    local ledger="$1"
    local key="$2"
    "$PYTHON_BIN" - <<'PY' "$ledger" "$key"
import os
import stat
import sys
import tempfile

path, key = sys.argv[1:]
flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
try:
    fd = os.open(path, flags)
except FileNotFoundError:
    raise SystemExit(0)
try:
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
        raise OSError("unsafe ownership ledger")
    data = os.read(fd, 1024 * 1024 + 1)
finally:
    os.close(fd)
if len(data) > 1024 * 1024:
    raise OSError("ownership ledger is too large")
lines = data.decode("utf-8").splitlines()
kept = [line for line in lines if line.partition("\t")[0] != key]
parent = os.path.dirname(path)
temp_fd, temp_path = tempfile.mkstemp(prefix=f".{os.path.basename(path)}.", dir=parent)
try:
    os.fchmod(temp_fd, 0o600)
    payload = (("\n".join(kept) + "\n") if kept else "").encode()
    os.write(temp_fd, payload)
    os.fsync(temp_fd)
finally:
    os.close(temp_fd)
os.replace(temp_path, path)
PY
  }

  is_owned_recipe() {
    local team_id="$1"
    local recipe="$2"
    if [[ -L "$recipe" ]]; then
      "$PYTHON_BIN" - <<'PY' "$recipe" "$TEAMS_DIR/$team_id/team.yaml"
from pathlib import Path
import os
import sys

link = Path(sys.argv[1])
expected = Path(sys.argv[2]).resolve(strict=False)
try:
    target = (link.parent / os.readlink(link)).resolve(strict=False)
except OSError:
    raise SystemExit(1)
raise SystemExit(0 if target == expected else 1)
PY
      return
    fi
    managed_file_matches "$managed_recipes" "$team_id/team.yaml" "$recipe"
  }

  local active_file
  active_file="$(mktemp "${TMPDIR:-/tmp}/deploy-all-teams.active.XXXXXX")"
  local unsafe_indexes=false
  local pruned_team=0
  local pruned_manifest=0
  shopt -s nullglob
  if [[ -d "$meta_dir" ]]; then
    local expected_teams=" ${TEAMS[*]} "
    for meta_file in "$meta_dir"/*.members; do
      local team_id
      team_id="$(basename "$meta_file" .members)"
      if [[ "$expected_teams" != *" $team_id "* ]]; then
        if managed_file_matches "$managed_recipes" "$team_id.members" "$meta_file"; then
          rm -f "$meta_file"
          forget_managed_key "$managed_recipes" "$team_id.members"
          pruned_team=$((pruned_team + 1))
          $QUIET || echo "  pruned (stale team)     $team_id.members" >&2
        else
          unsafe_indexes=true
          $QUIET || echo "  kept (unowned/modified) $team_id.members" >&2
        fi
      elif ! read_managed_members "$team_id.members" "$meta_file" >> "$active_file"; then
        unsafe_indexes=true
        $QUIET || echo "  kept (unsafe index)     $team_id.members; orphan pruning disabled" >&2
      fi
    done
    for manifest_dir in "$meta_dir"/*; do
      [[ -d "$manifest_dir" ]] || continue
      [[ -L "$manifest_dir" ]] && continue
      local team_id
      team_id="$(basename "$manifest_dir")"
      if [[ "$expected_teams" != *" $team_id "* ]]; then
        local recipe="$manifest_dir/team.yaml"
        if [[ -e "$recipe" || -L "$recipe" ]]; then
          if is_owned_recipe "$team_id" "$recipe"; then
            rm -f "$recipe"
            forget_managed_key "$managed_recipes" "$team_id/team.yaml"
            rmdir "$manifest_dir" 2>/dev/null || true
            pruned_manifest=$((pruned_manifest + 1))
            $QUIET || echo "  pruned (stale manifest) $team_id/team.yaml" >&2
          else
            $QUIET || echo "  kept (unowned/modified) $team_id/team.yaml" >&2
          fi
        fi
      fi
    done
  fi

  is_managed_agent_file() {
    local file="$1"
    local stem source_path filename
    stem="$(basename "$file" ".$ext")"
    filename="$(basename "$file")"
    source_path="$member_source_dir/$filename"

    if [[ -L "$file" ]]; then
      [[ -e "$source_path" && "$file" -ef "$source_path" ]] && return 0
      return 1
    fi

    managed_file_matches "$managed_index" "$filename" "$file"
  }
  sort -u -o "$active_file" "$active_file"

  local pruned_orphan=0
  local pruned_broken=0
  for f in "$target_dir"/*."$ext"; do
    local stem member_id is_broken=false is_orphan=false
    stem="$(basename "$f" ".$ext")"
    member_id="${stem//_/-}"

    if ! is_managed_agent_file "$f"; then
      continue
    fi

    if [[ -L "$f" && ! -e "$f" ]]; then
      is_broken=true
    fi

    if [[ "$unsafe_indexes" != true ]] && ! grep -qsx "$member_id" "$active_file" 2>/dev/null; then
      is_orphan=true
    fi

    if $is_broken || $is_orphan; then
      rm -f "$f"
      forget_managed_key "$managed_index" "$(basename "$f")"
      if $is_broken; then
        pruned_broken=$((pruned_broken + 1))
        $QUIET || echo "  pruned (broken symlink) $stem.$ext" >&2
      else
        pruned_orphan=$((pruned_orphan + 1))
        $QUIET || echo "  pruned (orphan)         $stem.$ext" >&2
      fi
    fi
  done
  shopt -u nullglob
  rm -f "$active_file"
  echo "$pruned_orphan $pruned_broken $pruned_team $pruned_manifest"
}

OK_COUNT=0
FAIL_COUNT=0
FAILED=()

for platform in "${PLATFORMS[@]}"; do
  $QUIET || echo "[$platform]"
  for team in "${TEAMS[@]}"; do
    if deploy_one "$team" "$platform"; then
      OK_COUNT=$((OK_COUNT + 1))
      $QUIET || printf "  ok    %s\n" "$team"
    else
      FAIL_COUNT=$((FAIL_COUNT + 1))
      FAILED+=("$platform:$team")
      $QUIET || printf "  FAIL  %s\n" "$team"
    fi
  done
  $QUIET || echo ""
done

# Final summary
TOTAL=$((${#TEAMS[@]} * ${#PLATFORMS[@]}))
echo "Summary"
echo "  total operations: $TOTAL"
echo "  succeeded:        $OK_COUNT"
echo "  failed:           $FAIL_COUNT"

if $DRY_RUN; then
  echo ""
  echo "Dry run — no files were written. Re-run without --dry-run to apply."
  exit 0
fi

if [[ $FAIL_COUNT -gt 0 ]]; then
  echo ""
  echo "Failed deployments:"
  for f in "${FAILED[@]}"; do
    echo "  - $f"
  done
  exit 1
fi

if ! $REMOVE; then
  echo ""
  if $PRUNE; then
    for platform in "${PLATFORMS[@]}"; do
      target_root="$(scope_target "$platform")"
      $QUIET || echo "[$platform] pruning orphans"
      read -r prune_orphans_count prune_broken_count prune_team_count prune_manifest_count \
        < <(prune_orphans "$platform" "$target_root")
      if ! $QUIET; then
        if (( prune_orphans_count == 0 && prune_broken_count == 0 && prune_team_count == 0 && prune_manifest_count == 0 )); then
          echo "  no orphans, broken symlinks, stale teams, or stale manifests"
        else
          echo "  pruned: $prune_orphans_count orphan(s), $prune_broken_count broken symlink(s), $prune_team_count stale team(s), $prune_manifest_count stale manifest(s)"
        fi
        echo ""
      fi
    done
  fi

  for platform in "${PLATFORMS[@]}"; do
    target_root="$(scope_target "$platform")"
    case "$platform" in
      claude)
        agent_count=$(find -L "$target_root/agents" -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
        recipe_root="$(scope_base)/.agents/team-recipes/$platform"
        team_count=$(find -L "$recipe_root" -maxdepth 1 -type f -name '*.members' 2>/dev/null | wc -l | tr -d ' ')
        manifest_count=$(find -L "$recipe_root" -mindepth 2 -maxdepth 2 -type f -name 'team.yaml' 2>/dev/null | wc -l | tr -d ' ')
        echo "  $target_root/agents  $agent_count files"
        echo "  $recipe_root  $team_count recipe member indexes"
        echo "  $recipe_root  $manifest_count repository team recipes"
        ;;
      codex)
        agent_count=$(find -L "$target_root/agents" -maxdepth 1 -type f -name '*.toml' 2>/dev/null | wc -l | tr -d ' ')
        recipe_root="$(scope_base)/.agents/team-recipes/$platform"
        team_count=$(find -L "$recipe_root" -maxdepth 1 -type f -name '*.members' 2>/dev/null | wc -l | tr -d ' ')
        manifest_count=$(find -L "$recipe_root" -mindepth 2 -maxdepth 2 -type f -name 'team.yaml' 2>/dev/null | wc -l | tr -d ' ')
        echo "  $target_root/agents   $agent_count files"
        echo "  $recipe_root  $team_count recipe member indexes"
        echo "  $recipe_root  $manifest_count repository team recipes"
        ;;
    esac
  done
  echo ""
  echo "Restart your Claude Code session (or run /agents) to load new members."
  echo "Restart your Codex session, then smoke-test by explicitly spawning one installed agent by its TOML name."
fi
