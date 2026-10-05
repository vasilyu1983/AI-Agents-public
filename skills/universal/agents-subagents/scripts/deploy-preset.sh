#!/usr/bin/env bash
# deploy-preset.sh — Install shared members or repository team recipes
#
# Usage:
#   deploy-preset.sh <team-or-member> [options]
#
# Options:
#   --member                  Treat the target as a canonical member id instead of a team id
#   --platform claude|codex   Target platform (default: claude)
#   --user                    Deploy to user-level agents (default)
#   --project                 Deploy to project-level agents (cwd)
#   --repo PATH               Deploy into a specific repo's .claude/ or .codex/ directory
#   --force                   Overwrite existing agent files
#   --refresh-managed         Refresh only installer-owned, unmodified files (bulk installer use)
#   --include-candidates      Also install expansion-gate candidate specialists
#   --remove                  Remove the target instead of installing it
#   --list                    List available teams
#   --list-members            List available canonical members
#
# Examples:
#   deploy-preset.sh software-code-review-board --platform claude --project
#   deploy-preset.sh software-security-reviewer --member --platform codex --user
#   deploy-preset.sh software-code-review-board --platform claude --user --remove

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# The agent catalog lives at <repo>/agents/{claude,codex,teams}, outside this
# skill. Resolve the physical script folder (pwd -P) so a runtime symlink such as
# ~/.claude/skills/agents-subagents still finds the repository.
REPO_ROOT="$(cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/../../../.." && pwd)"
TEAMS_DIR="$(cd "$REPO_ROOT/agents/teams" && pwd)"
MEMBERS_DIR="$(cd "$REPO_ROOT/agents" && pwd)"
# Library skills sit in group folders: skills/universal, skills/project, skills/personal,
# skills/client/<client>.
SHARED_SKILL_GROUP_DIRS=("$REPO_ROOT/skills/universal" "$REPO_ROOT/skills/project" "$REPO_ROOT/skills/personal")
for _client_dir in "$REPO_ROOT"/skills/client/*/; do
  [[ -d "$_client_dir" ]] && SHARED_SKILL_GROUP_DIRS+=("${_client_dir%/}")
done
unset _client_dir
ALIAS_FILE="$SCRIPT_DIR/../data/naming-aliases.json"
MODEL_POLICY_FILE="$SCRIPT_DIR/../data/model-policy.json"

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

PLATFORM="claude"
SCOPE="user"
REPO_PATH=""
FORCE=false
REFRESH_MANAGED=false
INCLUDE_CANDIDATES=false
REMOVE=false
LIST=false
LIST_MEMBERS=false
MODE="team"
ITEM_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --member)
      MODE="member"
      shift
      ;;
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
    --force)
      FORCE=true
      shift
      ;;
    --refresh-managed)
      REFRESH_MANAGED=true
      shift
      ;;
    --include-candidates)
      INCLUDE_CANDIDATES=true
      shift
      ;;
    --remove)
      REMOVE=true
      shift
      ;;
    --list)
      LIST=true
      shift
      ;;
    --list-members)
      LIST_MEMBERS=true
      shift
      ;;
    -h|--help)
      head -25 "$0" | grep '^#' | sed 's/^# \?//'
      exit 0
      ;;
    *)
      ITEM_NAME="$1"
      shift
      ;;
  esac
done

if [[ "$PLATFORM" != "claude" && "$PLATFORM" != "codex" ]]; then
  echo "Error: Platform must be 'claude' or 'codex'"
  exit 1
fi

if [[ "$SCOPE" == "repo" ]]; then
  [[ -n "$REPO_PATH" ]] || { echo "Error: --repo requires a path"; exit 1; }
  REPO_PATH="$(cd "$REPO_PATH" 2>/dev/null && pwd)" || {
    echo "Error: Repo path '$REPO_PATH' does not exist"
    exit 1
  }
fi

case "$SCOPE" in
  user)
    SCOPE_BASE="$HOME"
    ROOT_DIR="$HOME/.${PLATFORM}"
    ;;
  project)
    SCOPE_BASE="$(pwd)"
    ROOT_DIR=".${PLATFORM}"
    ;;
  repo)
    SCOPE_BASE="$REPO_PATH"
    ROOT_DIR="$REPO_PATH/.${PLATFORM}"
    ;;
esac

TARGET_DIR="$ROOT_DIR/agents"
# Repository-owned recipes are deliberately kept out of ~/.claude/teams,
# which Claude Code reserves for live native Agent Team state. Neither runtime
# reads these recipes as native configuration.
META_DIR="$SCOPE_BASE/.agents/team-recipes/$PLATFORM"
LEGACY_META_DIR="$ROOT_DIR/teams"
MANAGED_MEMBERS_FILE="$META_DIR/managed-members.tsv"
MANAGED_RECIPES_FILE="$META_DIR/managed-recipes.tsv"

require_safe_id() {
  local kind="$1"
  local value="$2"
  if [[ ! "$value" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
    echo "Error: unsafe $kind id '$value' (expected lowercase hyphenated slug)" >&2
    return 1
  fi
}

assert_path_within() {
  local base="$1"
  local target="$2"
  # Paths ride env vars, not argv: endpoint-security scanners open argv paths
  # that look like script files, and opening a FIFO with no writer blocks forever.
  ASSERT_BASE="$base" ASSERT_TARGET="$target" "$PYTHON_BIN" - <<'PY'
from pathlib import Path
import os
import sys

base = Path(os.environ["ASSERT_BASE"]).resolve()
raw_target = Path(os.environ["ASSERT_TARGET"])
target = raw_target.parent.resolve() / raw_target.name
try:
    target.relative_to(base)
except ValueError:
    raise SystemExit(f"unsafe installer target escapes {base}: {target}")
PY
}

assert_managed_base() {
  local scope_root="$1"
  local base="$2"
  ASSERT_SCOPE="$scope_root" ASSERT_BASE="$base" "$PYTHON_BIN" - <<'PY'
from pathlib import Path
import os
import sys

raw_scope = Path(os.path.abspath(os.environ["ASSERT_SCOPE"]))
scope = raw_scope.resolve()
raw = Path(os.path.abspath(os.environ["ASSERT_BASE"]))
try:
    relative = raw.relative_to(raw_scope)
except ValueError:
    raise SystemExit(f"unsafe managed base escapes scope {scope}: {raw}")
cursor = scope
for part in relative.parts:
    cursor /= part
    if cursor.is_symlink():
        raise SystemExit(f"unsafe managed base contains symlink: {cursor}")
resolved = raw.resolve(strict=False)
try:
    resolved.relative_to(scope)
except ValueError:
    raise SystemExit(f"unsafe managed base resolves outside scope {scope}: {resolved}")
PY
}

resolve_alias() {
  local kind="$1"
  local value="$2"
  "$PYTHON_BIN" - <<'PY' "$ALIAS_FILE" "$kind" "$value"
from pathlib import Path
import json
import sys

alias_path = Path(sys.argv[1])
kind = sys.argv[2]
value = sys.argv[3]
if alias_path.exists():
    data = json.loads(alias_path.read_text(encoding="utf-8"))
    print(data.get(kind, {}).get(value, value))
else:
    print(value)
PY
}

lookup_board() {
  "$PYTHON_BIN" - "$ALIAS_FILE" "$1" <<'BOARDPY'
from pathlib import Path
import json
import sys

alias_path = Path(sys.argv[1])
if alias_path.exists():
    data = json.loads(alias_path.read_text(encoding="utf-8"))
    board = data.get("boards", {}).get(sys.argv[2])
    if board:
        print(board)
BOARDPY
}

list_aliases() {
  local kind="$1"
  "$PYTHON_BIN" - <<'PY' "$ALIAS_FILE" "$kind"
from pathlib import Path
import json
import sys

alias_path = Path(sys.argv[1])
kind = sys.argv[2]
if not alias_path.exists():
    raise SystemExit(0)
data = json.loads(alias_path.read_text(encoding="utf-8"))
aliases = data.get(kind, {})
for alias, canonical in sorted(aliases.items()):
    print(f"  {alias} -> {canonical}")
PY
}

member_filename() {
  local member_id="$1"
  if [[ "$PLATFORM" == "claude" ]]; then
    printf '%s.md' "$member_id"
  else
    printf '%s.toml' "${member_id//-/_}"
  fi
}

member_source_path() {
  local member_id="$1"
  local ext
  if [[ "$PLATFORM" == "claude" ]]; then
    ext="md"
  else
    ext="toml"
  fi
  local path="$MEMBERS_DIR/$PLATFORM/$member_id.$ext"
  # Codex canonical files may use snake_case filenames
  if [[ ! -f "$path" && "$PLATFORM" == "codex" ]]; then
    path="$MEMBERS_DIR/$PLATFORM/${member_id//-/_}.$ext"
  fi
  printf '%s' "$path"
}

team_manifest_path() {
  local team_id="$1"
  printf '%s/%s/team.yaml' "$TEAMS_DIR" "$team_id"
}

team_manifest_install_path() {
  local team_id="$1"
  printf '%s/%s/team.yaml' "$META_DIR" "$team_id"
}

list_members() {
  "$PYTHON_BIN" - <<'PY' "$MEMBERS_DIR"
from pathlib import Path
import sys
root = Path(sys.argv[1])
ids = set()
for path in [p for sub in ("claude", "codex") for p in (root / sub).rglob("*")]:
    if path.suffix in {".md", ".toml"}:
        if path.stem == "README":
            continue
        ids.add(path.stem.replace("_", "-"))
for member_id in sorted(ids):
    print(member_id)
PY
}

list_teams() {
  for manifest in "$TEAMS_DIR"/*/team.yaml; do
    [[ -f "$manifest" ]] || continue
    team_id="$(basename "$(dirname "$manifest")")"
    description="$(awk '
      /^description:[[:space:]]*>[[:space:]]*$/ {capture=1; next}
      /^description:[[:space:]]*/ {sub(/^description:[[:space:]]*/, ""); print; exit}
      capture && /^[[:space:]]+/ {
        line=$0
        gsub(/^[[:space:]]+/, "", line)
        if (out == "") out=line; else out=out " " line
        next
      }
      capture && !/^[[:space:]]/ {print out; printed=1; exit}
      END {if (capture && out != "" && !printed) print out}
    ' "$manifest")"
    member_count="$(awk '
      /^members:/ {in_members=1; next}
      in_members && /^[[:space:]]*-[[:space:]]+/ {count++; next}
      in_members && !/^[[:space:]]*-/ {in_members=0}
      END {print count+0}
    ' "$manifest")"
    echo "  $team_id  ($member_count members) ${description}"
  done
}

team_all_members() {
  # Extract core members plus expansion-gate candidates. This is used only
  # when --include-candidates was explicit and as a safe removal fallback for
  # metadata produced by older installers that eagerly installed candidates.
  local manifest="$1"
  awk '
    function strip_comment(line,   pos) {
      pos = index(line, "#")
      if (pos > 0) line = substr(line, 1, pos - 1)
      sub(/[[:space:]]+$/, "", line)
      return line
    }
    /^members:/ {capture=1; indent=""; next}
    /^[[:space:]]+candidate_specialists:[[:space:]]*$/ {
      capture=1
      match($0, /^[[:space:]]+/)
      indent=substr($0, 1, RLENGTH)
      next
    }
    capture && /^[[:space:]]*-[[:space:]]+/ {
      line=strip_comment($0)
      sub(/^[[:space:]]*-[[:space:]]+/, "", line)
      if (line != "") print line
      next
    }
    capture && /^[^[:space:]]/ {capture=0; indent=""}
    capture && indent != "" {
      match($0, /^[[:space:]]*/)
      if (RLENGTH <= length(indent)) {capture=0; indent=""}
    }
  ' "$manifest" | awk '!seen[$0]++'
}

team_members() {
  # Core members are the normal installation surface. Candidate specialists
  # remain catalog metadata until an operator explicitly materializes them.
  awk '
    function strip_comment(line,   pos) {
      pos = index(line, "#")
      if (pos > 0) line = substr(line, 1, pos - 1)
      sub(/[[:space:]]+$/, "", line)
      return line
    }
    /^members:/ {capture=1; next}
    capture && /^[[:space:]]*-[[:space:]]+/ {
      line=strip_comment($0)
      sub(/^[[:space:]]*-[[:space:]]+/, "", line)
      if (line != "") print line
      next
    }
    capture {exit}
  ' "$1" | awk '!seen[$0]++'
}

team_core_member_count() {
  awk '
    /^members:/ {in_members=1; next}
    in_members && /^[[:space:]]*-[[:space:]]+/ {count++; next}
    in_members && !/^[[:space:]]*-/ {in_members=0}
    END {print count+0}
  ' "$1"
}

load_members_from_stream() {
  members=()
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    members+=("$line")
  done
}

generate_codex_from_claude() {
  # Fallback when agents/codex/<id>.toml is missing. Uses the same generator that
  # produces the committed Codex files, so there is one conversion path only.
  local member_id="$1"
  local claude_source="$MEMBERS_DIR/claude/$member_id.md"
  [[ -f "$claude_source" ]] || {
    echo "Error: Missing Claude source for member '$member_id'" >&2
    return 1
  }

  local tmp_file
  tmp_file="$(mktemp "${TMPDIR:-/tmp}/${member_id//-/_}.XXXXXX")"

  "$PYTHON_BIN" - "$SCRIPT_DIR" "$claude_source" "$tmp_file" <<'PY' || { rm -f "$tmp_file"; return 1; }
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
import generate_codex_agents as gen

try:
    text = gen.generate_member(Path(sys.argv[2]))
except gen.GenerationError as exc:
    raise SystemExit(f"Error: {exc}")
Path(sys.argv[3]).write_text(text, encoding="utf-8")
PY

  printf '%s' "$tmp_file"
}

member_source_for_install() {
  local member_id="$1"
  local source_path
  source_path="$(member_source_path "$member_id")"
  if [[ -f "$source_path" ]]; then
    printf '%s' "$source_path"
    return 0
  fi
  if [[ "$PLATFORM" == "codex" ]]; then
    generate_codex_from_claude "$member_id" || return 1
    return 0
  fi
  echo "Error: Canonical member '$member_id' not found for platform '$PLATFORM'" >&2
  return 1
}

member_skills() {
  local member_id="$1"
  local codex_source="$MEMBERS_DIR/codex/${member_id//-/_}.toml"
  local claude_source="$MEMBERS_DIR/claude/$member_id.md"

  if [[ -f "$codex_source" ]]; then
    "$PYTHON_BIN" - <<'PY' "$codex_source"
from pathlib import Path
import re
import sys
import tomllib

source = tomllib.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
instructions = source.get("developer_instructions", "")
patterns = (
    # Current canonical footer.
    r"^Linked skills:\s*([^\n.]+)\.\s*Declared for Codex\b",
    # Legacy footer retained so older detached member files still install.
    r"^Linked shared skills \(([^)]+)\) "
    r"(?:are resolved independently for Codex|are declared for Codex)\b",
)
match = next(
    (match for pattern in patterns if (match := re.search(pattern, instructions, re.MULTILINE))),
    None,
)
if match:
    seen = set()
    for raw_skill_id in match.group(1).split(","):
        skill_id = raw_skill_id.strip()
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", skill_id):
            raise SystemExit(f"invalid linked skill id {skill_id!r} in {sys.argv[1]}")
        if skill_id not in seen:
            print(skill_id)
            seen.add(skill_id)
PY
    return 0
  fi

  [[ -f "$claude_source" ]] || return 0

  "$PYTHON_BIN" - <<'PY' "$claude_source"
from pathlib import Path
import re
import sys

source = Path(sys.argv[1]).read_text(encoding="utf-8")
parts = source.split("---", 2)
if len(parts) < 3:
    raise SystemExit(0)
frontmatter = parts[1]

capture = False
for line in frontmatter.splitlines():
    if re.match(r"^skills:\s*$", line):
        capture = True
        continue
    if not capture:
        continue
    if re.match(r"^\s*-\s+", line):
        print(re.sub(r"^\s*-\s+", "", line).strip())
        continue
    if line.strip() == "":
        continue
    break
PY
}

resolve_skill_path() {
  local skill_id="$1"
  local search_roots=()
  local candidate

  if [[ "$SCOPE" == "repo" ]]; then
    search_roots+=("$REPO_PATH/.agents/skills")
  elif [[ "$SCOPE" == "project" ]]; then
    search_roots+=("$(pwd)/.agents/skills")
  fi

  search_roots+=(
    "$HOME/.agents/skills"
    "${SHARED_SKILL_GROUP_DIRS[@]}"
  )

  for root in "${search_roots[@]}"; do
    candidate="$root/$skill_id"
    if [[ -f "$candidate/SKILL.md" ]]; then
      printf '%s' "$candidate"
      return 0
    fi
  done

  return 1
}

target_skill_path() {
  local skill_id="$1"
  case "$SCOPE" in
    user)
      printf '%s/.agents/skills/%s' "$HOME" "$skill_id"
      ;;
    project)
      printf '%s/.agents/skills/%s' "$(pwd)" "$skill_id"
      ;;
    repo)
      printf '%s/.agents/skills/%s' "$REPO_PATH" "$skill_id"
      ;;
  esac
}

materialize_skill_path() {
  local skill_id="$1"
  local source_path target_path target_dir

  source_path="$(resolve_skill_path "$skill_id" || true)"
  [[ -n "$source_path" ]] || return 1

  target_path="$(target_skill_path "$skill_id")"
  target_dir="$(dirname "$target_path")"
  mkdir -p "$target_dir"

  if [[ -f "$target_path/SKILL.md" ]]; then
    printf '%s' "$target_path"
    return 0
  fi

  if [[ -L "$target_path" ]]; then
    rm -f "$target_path"
  elif [[ -e "$target_path" ]]; then
    return 1
  fi

  ln -s "$source_path" "$target_path"
  printf '%s' "$target_path"
}

codex_skill_config_path() {
  local skill_path="$1"
  case "$SCOPE" in
    user)
      case "$skill_path" in
        "$HOME"/.agents/skills/*)
          printf '~%s/SKILL.md' "${skill_path#"$HOME"}"
          return 0
          ;;
      esac
      ;;
    project)
      case "$skill_path" in
        "$(pwd)"/.agents/skills/*)
          printf '%s/SKILL.md' "${skill_path#"$(pwd)/"}"
          return 0
          ;;
      esac
      ;;
    repo)
      case "$skill_path" in
        "$REPO_PATH"/.agents/skills/*)
          printf '%s/SKILL.md' "${skill_path#"$REPO_PATH/"}"
          return 0
          ;;
      esac
      ;;
  esac

  printf '%s/SKILL.md' "$skill_path"
}

append_codex_skill_links() {
  local member_id="$1"
  local target_file="$2"
  local skill_id skill_path config_path
  local appended=false

  grep -q '^\[\[skills\.config\]\]' "$target_file" && return 0

  while IFS= read -r skill_id; do
    [[ -n "$skill_id" ]] || continue
    skill_path="$(materialize_skill_path "$skill_id" || true)"
    [[ -n "$skill_path" ]] || continue
    config_path="$(codex_skill_config_path "$skill_path")"

    if [[ "$appended" == false ]]; then
      printf '\n# Linked shared skills, resolved independently for Codex at install time.\n' >> "$target_file"
      appended=true
    fi

    printf '[[skills.config]]\npath = "%s"\nenabled = true\n\n' "$config_path" >> "$target_file"
  done < <(member_skills "$member_id")
}

member_reference_root() {
  # Installed references/ root for the current platform. The shared skill lands
  # in ~/.claude/skills/agents-subagents for Claude and ~/.agents/skills/
  # agents-subagents for Codex; project and repo scopes read the same user-level
  # skill install, so this is deliberately $HOME-anchored for every scope.
  case "$PLATFORM" in
    codex) printf '%s/.agents/skills/agents-subagents/references' "$HOME" ;;
    *) printf '%s/.claude/skills/agents-subagents/references' "$HOME" ;;
  esac
}

rewrite_member_reference_links() {
  # Canonical member bodies link siblings as
  # `../../skills/universal/agents-subagents/references/<file>`, which is only
  # correct while the file sits in <repo>/agents/<platform>/. Once the
  # member is materialized into an agents/ directory the relative hop dangles, so
  # rewrite it to the deployed shared-skills reference path. This runs on the
  # installed copy only, never on the canonical source, and applies to both
  # platforms — a copied Claude member dangles exactly like a Codex one. Only
  # rewrite when the target actually exists at install time; a missing target
  # keeps the original link and warns, because an absolute path to a nonexistent
  # file is strictly worse than a relative one an operator can still trace.
  # Implemented in shell (grep gate + perl in-place) rather than a python3
  # heredoc: an interpreter spawn per installed file made a team deploy ~100x
  # slower and tripped test_installer_ownership's 5s per-deploy timeout.
  local target_file="$1"
  local reference_root_path="$2"
  grep -q '\.\./\.\./skills/universal/agents-subagents/references/' "$target_file" || return 0

  local name resolved
  while IFS= read -r name; do
    [[ -n "$name" ]] || continue
    resolved="$reference_root_path/$name"
    if [[ -f "$resolved" ]]; then
      REF_NAME="$name" REF_RESOLVED="$resolved" perl -pi -e \
        's{\.\./\.\./skills/universal/agents-subagents/references/\Q$ENV{REF_NAME}\E}{$ENV{REF_RESOLVED}}g' \
        "$target_file"
    else
      echo "  Warning: $(basename "$target_file") links ../../skills/universal/agents-subagents/references/${name}, but ${resolved} is not installed; link left unrewritten" >&2
    fi
  done < <(grep -o '\.\./\.\./skills/universal/agents-subagents/references/[A-Za-z0-9._-]*' "$target_file" | awk -F/ '{print $NF}' | sort -u)
}

MODEL_POLICY_LOADED=false
CODEX_CRITICAL_MODEL=""
CODEX_CRITICAL_EFFORT=""
CODEX_CRITICAL_MATERIALIZE="true"
CODEX_MECHANICAL_MODEL=""
CODEX_MECHANICAL_EFFORT=""
CODEX_MECHANICAL_MATERIALIZE="true"
CODEX_STANDARD_MODEL=""
CODEX_STANDARD_EFFORT=""
CODEX_STANDARD_MATERIALIZE="true"

load_codex_model_policy() {
  [[ "$MODEL_POLICY_LOADED" == true ]] && return 0
  [[ -f "$MODEL_POLICY_FILE" ]] || {
    echo "Error: model policy not found at $MODEL_POLICY_FILE" >&2
    return 1
  }

  local tier model effort materialize policy_cache
  policy_cache="$(mktemp "${TMPDIR:-/tmp}/deploy-preset.policy.XXXXXX")"
  if ! "$PYTHON_BIN" - <<'PY' "$MODEL_POLICY_FILE" > "$policy_cache"
import importlib.util
import json
from pathlib import Path
import sys

policy_path = Path(sys.argv[1])
policy = json.loads(policy_path.read_text(encoding="utf-8"))
validator_path = policy_path.parent.parent / "scripts" / "validate_catalog_integrity.py"
spec = importlib.util.spec_from_file_location("catalog_integrity", validator_path)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load model-policy validator at {validator_path}")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
complaints = validator.validate_model_policy(policy)
if complaints:
    raise SystemExit("invalid model policy: " + "; ".join(complaints))
for tier in ("critical", "mechanical", "standard"):
    entry = policy["codex"][tier]
    print(
        tier,
        entry["model"],
        entry["model_reasoning_effort"],
        str(entry.get("materialize", True)).lower(),
        sep="\t",
    )
PY
  then
    rm -f "$policy_cache"
    return 1
  fi
  while IFS=$'\t' read -r tier model effort materialize; do
    case "$tier" in
      critical)
        CODEX_CRITICAL_MODEL="$model"
        CODEX_CRITICAL_EFFORT="$effort"
        CODEX_CRITICAL_MATERIALIZE="$materialize"
        ;;
      mechanical)
        CODEX_MECHANICAL_MODEL="$model"
        CODEX_MECHANICAL_EFFORT="$effort"
        CODEX_MECHANICAL_MATERIALIZE="$materialize"
        ;;
      standard)
        CODEX_STANDARD_MODEL="$model"
        CODEX_STANDARD_EFFORT="$effort"
        CODEX_STANDARD_MATERIALIZE="$materialize"
        ;;
    esac
  done < "$policy_cache"
  rm -f "$policy_cache"
  MODEL_POLICY_LOADED=true
}

apply_codex_model_tier() {
  local target_file="$1"
  local tier model effort materialize tmp
  load_codex_model_policy

  tier="$(awk '/^# model_tier: (critical|mechanical|standard)$/ {print $3; exit}' "$target_file")"
  [[ -n "$tier" ]] || return 0
  case "$tier" in
    critical)
      model="$CODEX_CRITICAL_MODEL"; effort="$CODEX_CRITICAL_EFFORT"; materialize="$CODEX_CRITICAL_MATERIALIZE"
      ;;
    mechanical)
      model="$CODEX_MECHANICAL_MODEL"; effort="$CODEX_MECHANICAL_EFFORT"; materialize="$CODEX_MECHANICAL_MATERIALIZE"
      ;;
    standard)
      model="$CODEX_STANDARD_MODEL"; effort="$CODEX_STANDARD_EFFORT"; materialize="$CODEX_STANDARD_MATERIALIZE"
      ;;
  esac
  [[ "$materialize" == true ]] || return 0
  if grep -Eq '^(model|model_reasoning_effort)[[:space:]]*=' "$target_file"; then
    echo "Error: refusing to overwrite an existing model pin in $target_file" >&2
    return 1
  fi

  tmp="$(mktemp "${TMPDIR:-/tmp}/deploy-preset.XXXXXX")"
  awk -v model="$model" -v effort="$effort" '
    {print}
    !inserted && /^name = / {
      print "model = \"" model "\""
      print "model_reasoning_effort = \"" effort "\""
      inserted=1
    }
    END {if (!inserted) exit 1}
  ' "$target_file" > "$tmp" || {
    rm -f "$tmp"
    echo "Error: missing name field in $target_file" >&2
    return 1
  }
  mv "$tmp" "$target_file"
}

managed_codex_wrapper_path() {
  local member_id="$1"
  printf '%s/managed-agents/%s' "$ROOT_DIR" "$(member_filename "$member_id")"
}

file_sha256() {
  local file="$1"
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$file" | awk '{print $1}'
  else
    sha256sum "$file" | awk '{print $1}'
  fi
}

is_canonical_member_symlink() {
  local file="$1"
  local expected="$MEMBERS_DIR/$PLATFORM/$(basename "$file")"
  [[ -L "$file" ]] || return 1
  [[ -e "$expected" && "$file" -ef "$expected" ]]
}

managed_member_checksum() {
  local filename="$1"
  [[ -f "$MANAGED_MEMBERS_FILE" ]] || return 1
  awk -F '\t' -v name="$filename" '$1 == name {print $2; found=1} END {if (!found) exit 1}' \
    "$MANAGED_MEMBERS_FILE"
}

is_managed_member_unchanged() {
  local file="$1"
  local filename expected actual
  [[ -e "$file" || -L "$file" ]] || return 1
  is_canonical_member_symlink "$file" && return 0
  [[ -f "$file" ]] || return 1
  filename="$(basename "$file")"
  expected="$(managed_member_checksum "$filename" || true)"
  [[ -n "$expected" ]] || return 1
  actual="$(file_sha256 "$file")"
  [[ "$actual" == "$expected" ]]
}

record_managed_member() {
  local file="$1"
  local filename checksum tmp
  [[ -f "$file" ]] || return 0
  filename="$(basename "$file")"
  checksum="$(file_sha256 "$file")"
  mkdir -p "$META_DIR"
  tmp="$(mktemp "${TMPDIR:-/tmp}/deploy-preset.XXXXXX")"
  if [[ -f "$MANAGED_MEMBERS_FILE" ]]; then
    awk -F '\t' -v name="$filename" '$1 != name' "$MANAGED_MEMBERS_FILE" > "$tmp"
  fi
  printf '%s\t%s\n' "$filename" "$checksum" >> "$tmp"
  mv "$tmp" "$MANAGED_MEMBERS_FILE"
}

forget_managed_member() {
  local filename="$1"
  local tmp
  [[ -f "$MANAGED_MEMBERS_FILE" ]] || return 0
  tmp="$(mktemp "${TMPDIR:-/tmp}/deploy-preset.XXXXXX")"
  awk -F '\t' -v name="$filename" '$1 != name' "$MANAGED_MEMBERS_FILE" > "$tmp"
  mv "$tmp" "$MANAGED_MEMBERS_FILE"
}

managed_recipe_checksum() {
  local key="$1"
  [[ -f "$MANAGED_RECIPES_FILE" ]] || return 1
  awk -F '\t' -v name="$key" '$1 == name {print $2; found=1} END {if (!found) exit 1}' \
    "$MANAGED_RECIPES_FILE"
}

is_managed_metadata_unchanged() {
  local key="$1"
  local file="$2"
  local expected actual
  CHECK_FILE="$file" "$PYTHON_BIN" - <<'PY' || return 1
import os
from pathlib import Path
import stat
import sys

try:
    info = Path(os.environ["CHECK_FILE"]).lstat()
except OSError:
    raise SystemExit(1)
raise SystemExit(0 if stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1 else 1)
PY
  expected="$(managed_recipe_checksum "$key" || true)"
  [[ -n "$expected" ]] || return 1
  actual="$(file_sha256 "$file")"
  [[ "$actual" == "$expected" ]]
}

is_managed_recipe_unchanged() {
  local team_id="$1"
  local file="$2"
  local key="$team_id/team.yaml" expected actual
  [[ -e "$file" || -L "$file" ]] || return 1
  [[ -L "$file" && "$file" -ef "$(team_manifest_path "$team_id")" ]] && return 0
  [[ -f "$file" ]] || return 1
  expected="$(managed_recipe_checksum "$key" || true)"
  [[ -n "$expected" ]] || return 1
  actual="$(file_sha256 "$file")"
  [[ "$actual" == "$expected" ]]
}

record_managed_recipe() {
  local team_id="$1"
  local file="$2"
  local key="$team_id/team.yaml" checksum tmp
  [[ -f "$file" ]] || return 0
  checksum="$(file_sha256 "$file")"
  mkdir -p "$META_DIR"
  tmp="$(mktemp "${TMPDIR:-/tmp}/deploy-preset.XXXXXX")"
  if [[ -f "$MANAGED_RECIPES_FILE" ]]; then
    awk -F '\t' -v name="$key" '$1 != name' "$MANAGED_RECIPES_FILE" > "$tmp"
  fi
  printf '%s\t%s\n' "$key" "$checksum" >> "$tmp"
  mv "$tmp" "$MANAGED_RECIPES_FILE"
}

record_managed_members_index() {
  local team_id="$1"
  local file="$2"
  local key="$team_id.members" checksum tmp
  [[ -f "$file" && ! -L "$file" ]] || return 0
  checksum="$(file_sha256 "$file")"
  mkdir -p "$META_DIR"
  tmp="$(mktemp "${TMPDIR:-/tmp}/deploy-preset.XXXXXX")"
  if [[ -f "$MANAGED_RECIPES_FILE" ]]; then
    awk -F '\t' -v name="$key" '$1 != name' "$MANAGED_RECIPES_FILE" > "$tmp"
  fi
  printf '%s\t%s\n' "$key" "$checksum" >> "$tmp"
  mv "$tmp" "$MANAGED_RECIPES_FILE"
}

write_managed_members_index() {
  local team_id="$1"
  local file="$2"
  shift 2
  local tmp
  if [[ -e "$file" || -L "$file" ]]; then
    if ! is_managed_metadata_unchanged "$team_id.members" "$file"; then
      echo "  Kept index: $team_id.members (not installer-owned or locally modified)"
      return 0
    fi
  fi
  tmp="$(mktemp "$META_DIR/.${team_id}.members.XXXXXX")"
  chmod 600 "$tmp"
  printf '%s\n' "$@" > "$tmp"
  mv -f "$tmp" "$file"
  record_managed_members_index "$team_id" "$file"
}

forget_managed_recipe() {
  local team_id="$1"
  local key="$team_id/team.yaml" tmp
  [[ -f "$MANAGED_RECIPES_FILE" ]] || return 0
  tmp="$(mktemp "${TMPDIR:-/tmp}/deploy-preset.XXXXXX")"
  awk -F '\t' -v name="$key" '$1 != name' "$MANAGED_RECIPES_FILE" > "$tmp"
  mv "$tmp" "$MANAGED_RECIPES_FILE"
}

forget_managed_members_index() {
  local team_id="$1"
  local key="$team_id.members" tmp
  [[ -f "$MANAGED_RECIPES_FILE" ]] || return 0
  tmp="$(mktemp "${TMPDIR:-/tmp}/deploy-preset.XXXXXX")"
  awk -F '\t' -v name="$key" '$1 != name' "$MANAGED_RECIPES_FILE" > "$tmp"
  mv "$tmp" "$MANAGED_RECIPES_FILE"
}

# User-scope Codex installs provision the [agents] defaults the effective-runtime
# audit expects. Idempotent: only absent keys are written, an existing table is
# extended in place, user values are never overwritten, the table is never
# duplicated. `agents.enabled` is deliberately not written (defaults to true).
provision_codex_agents_defaults() {
  local config_file="$HOME/.codex/config.toml"
  mkdir -p "$(dirname "$config_file")"
  CODEX_CONFIG="$config_file" "$PYTHON_BIN" - <<'PY' "$MODEL_POLICY_FILE"
import json
import os
import re
import sys
from pathlib import Path

policy = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
standard = policy["codex"]["standard"]
wanted = {
    "default_subagent_model": standard["model"],
    "default_subagent_reasoning_effort": standard["model_reasoning_effort"],
}
config = Path(os.environ["CODEX_CONFIG"])
text = config.read_text(encoding="utf-8") if config.exists() else ""
lines = text.splitlines()
start = next((i for i, l in enumerate(lines) if l.strip() == "[agents]"), None)
if start is None:
    if lines and lines[-1].strip():
        lines.append("")
    lines.append("[agents]")
    lines.extend(f'{k} = "{v}"' for k, v in wanted.items())
else:
    end = start + 1
    while end < len(lines) and not re.match(r"^\s*\[", lines[end]):
        end += 1
    present = set()
    for l in lines[start + 1:end]:
        m = re.match(r"^\s*([A-Za-z0-9_.-]+)\s*=", l)
        if m:
            present.add(m.group(1))
    insert_at = end
    while insert_at > start + 1 and not lines[insert_at - 1].strip():
        insert_at -= 1
    lines[insert_at:insert_at] = [f'{k} = "{v}"' for k, v in wanted.items() if k not in present]
config.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
}

install_member() {
  local member_id="$1"
  local source_file target_file managed_file
  require_safe_id "member" "$member_id"
  source_file="$(member_source_for_install "$member_id")"
  target_file="$TARGET_DIR/$(member_filename "$member_id")"
  assert_path_within "$TARGET_DIR" "$target_file"

  if [[ -e "$target_file" || -L "$target_file" ]]; then
    if [[ "$FORCE" != true && "$REFRESH_MANAGED" != true ]]; then
      echo "  Skipped: $(basename "$target_file") (exists, use --force to overwrite)"
      return 0
    fi
    if [[ "$REFRESH_MANAGED" == true ]] && ! is_managed_member_unchanged "$target_file"; then
      echo "  Skipped: $(basename "$target_file") (not installer-owned or locally modified)"
      return 0
    fi
  fi

  if [[ "$PLATFORM" == "codex" ]]; then
    # Every Codex scope needs a materialized TOML: a symlink cannot carry the
    # appended model tier, the native [[skills.config]] entries, or the rewritten
    # reference links. Project and repo scopes previously fell through to the
    # generic path below and silently received none of that config.
    if [[ "$SCOPE" == "user" ]]; then
      managed_file="$(managed_codex_wrapper_path "$member_id")"
      assert_path_within "$ROOT_DIR/managed-agents" "$managed_file"
      rm -f "$managed_file"
    fi
    rm -f "$target_file"
    cp "$source_file" "$target_file"
    apply_codex_model_tier "$target_file"
    append_codex_skill_links "$member_id" "$target_file"
    rewrite_member_reference_links "$target_file" "$(member_reference_root)"
    record_managed_member "$target_file"
    [[ "$SCOPE" == "user" ]] && provision_codex_agents_defaults
    echo "  Deployed: $(basename "$target_file") → $TARGET_DIR/"
    return 0
  fi

  if [[ -e "$target_file" ]]; then
    if "$PYTHON_BIN" - <<'PY' "$source_file" "$target_file"
from pathlib import Path
import os
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
try:
    raise SystemExit(0 if os.path.samefile(source, target) else 1)
except FileNotFoundError:
    raise SystemExit(1)
PY
    then
      echo "  Current: $(basename "$target_file") already points at the canonical source"
      record_managed_member "$target_file"
      return 0
    fi
  fi

  rm -f "$target_file"

  # Claude-only path; every Codex scope returned from the materialization branch
  # above.
  cp "$source_file" "$target_file"
  rewrite_member_reference_links "$target_file" "$(member_reference_root)"
  record_managed_member "$target_file"
  echo "  Deployed: $(basename "$target_file") → $TARGET_DIR/"
}

install_team_manifest() {
  local team_id="$1"
  local source_file="$2"
  local target_file target_dir
  target_file="$(team_manifest_install_path "$team_id")"
  require_safe_id "team" "$team_id"
  assert_path_within "$META_DIR" "$target_file"
  target_dir="$(dirname "$target_file")"
  RECIPE_INSTALL_STATUS="installed"
  mkdir -p "$target_dir"

  if [[ -e "$target_file" || -L "$target_file" ]]; then
    if "$PYTHON_BIN" - <<'PY' "$source_file" "$target_file"
from pathlib import Path
import os
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
try:
    raise SystemExit(0 if os.path.samefile(source, target) else 1)
except FileNotFoundError:
    raise SystemExit(1)
PY
    then
      echo "  Current: $team_id/team.yaml already points at the canonical recipe"
      record_managed_recipe "$team_id" "$target_file"
      RECIPE_INSTALL_STATUS="current"
      return 0
    fi
    if [[ "$REFRESH_MANAGED" == true ]] && ! is_managed_recipe_unchanged "$team_id" "$target_file"; then
      echo "  Skipped recipe: $team_id/team.yaml (not installer-owned or locally modified)"
      RECIPE_INSTALL_STATUS="skipped"
      return 0
    fi
    if [[ "$FORCE" != true && "$REFRESH_MANAGED" != true ]]; then
      echo "  Skipped: $team_id/team.yaml (exists, use --force to overwrite)"
      RECIPE_INSTALL_STATUS="skipped"
      return 0
    fi
    rm -f "$target_file"
  fi

  if [[ "$SCOPE" == "user" ]]; then
    ln -s "$source_file" "$target_file"
    echo "  Linked recipe: $team_id/team.yaml → $source_file"
  else
    cp "$source_file" "$target_file"
    echo "  Deployed recipe: $team_id/team.yaml → $target_dir/"
  fi
  record_managed_recipe "$team_id" "$target_file"
}

remove_team_manifest() {
  local team_id="$1"
  local target_dir="$META_DIR/$team_id"
  local target_file="$target_dir/team.yaml"
  require_safe_id "team" "$team_id"
  assert_path_within "$META_DIR" "$target_dir"
  if [[ -e "$target_file" || -L "$target_file" ]]; then
    if is_managed_recipe_unchanged "$team_id" "$target_file"; then
      rm -f "$target_file"
      forget_managed_recipe "$team_id"
      rmdir "$target_dir" 2>/dev/null || true
    else
      echo "  Kept recipe: $team_id/team.yaml (not installer-owned or locally modified)"
    fi
  fi
  remove_legacy_team_recipe "$team_id"
}

remove_legacy_team_recipe() {
  local team_id="$1"
  local legacy_recipe="$LEGACY_META_DIR/$team_id/team.yaml"
  require_safe_id "team" "$team_id"
  # Older installers recorded no checksum for .members files, so they cannot be
  # distinguished from user metadata and must be preserved. An exact canonical
  # recipe symlink is the only legacy artifact whose ownership is provable.
  if [[ -L "$legacy_recipe" && -e "$(team_manifest_path "$team_id")" && \
        "$legacy_recipe" -ef "$(team_manifest_path "$team_id")" ]]; then
    rm -f "$legacy_recipe"
  fi
  rmdir "$LEGACY_META_DIR/$team_id" 2>/dev/null || true
}

remove_member_if_unused() {
  local member_id="$1"
  local target_file="$TARGET_DIR/$(member_filename "$member_id")"
  local managed_file=""
  require_safe_id "member" "$member_id"
  assert_path_within "$TARGET_DIR" "$target_file"
  [[ -f "$target_file" ]] || return 0

  if [[ -d "$META_DIR" ]] && grep -Rqsx "$member_id" "$META_DIR"/*.members 2>/dev/null; then
    echo "  Kept: $(basename "$target_file") (still referenced by another team)"
    return 0
  fi

  if [[ "$PLATFORM" == "codex" && "$SCOPE" == "user" ]]; then
    managed_file="$(managed_codex_wrapper_path "$member_id")"
    assert_path_within "$ROOT_DIR/managed-agents" "$managed_file"
  fi
  if ! is_managed_member_unchanged "$target_file"; then
    echo "  Kept: $(basename "$target_file") (not installer-owned or locally modified)"
    return 0
  fi
  rm "$target_file"
  forget_managed_member "$(basename "$target_file")"
  [[ -n "$managed_file" ]] && rm -f "$managed_file"
  echo "  Removed: $target_file"
}

member_references() {
  local member_id="$1"
  [[ -d "$META_DIR" ]] || return 0
  local found=false
  for meta in "$META_DIR"/*.members; do
    [[ -f "$meta" ]] || continue
    if grep -qsx "$member_id" "$meta"; then
      found=true
      printf '%s\n' "$(basename "$meta" .members)"
    fi
  done
  [[ "$found" == true ]]
}

if [[ "$LIST" == true ]]; then
  echo "Available teams:"
  list_teams
  echo ""
  echo "Aliases:"
  list_aliases teams
  echo ""
  echo "Read-only panels served by the expert-board workflow (no install needed):"
  list_aliases boards
  exit 0
fi

if [[ "$LIST_MEMBERS" == true ]]; then
  echo "Available members:"
  list_members
  echo ""
  echo "Aliases:"
  list_aliases members
  exit 0
fi

[[ -n "$ITEM_NAME" ]] || {
  echo "Error: Team or member name required. Use --list or --list-members."
  exit 1
}

assert_managed_base "$SCOPE_BASE" "$TARGET_DIR"
assert_managed_base "$SCOPE_BASE" "$META_DIR"
assert_managed_base "$SCOPE_BASE" "$LEGACY_META_DIR"
assert_managed_base "$SCOPE_BASE" "$ROOT_DIR/managed-agents"
mkdir -p "$TARGET_DIR" "$META_DIR"

if [[ "$MODE" == "member" ]]; then
  ITEM_NAME="$(resolve_alias members "$ITEM_NAME")"
  require_safe_id "member" "$ITEM_NAME"
  if [[ "$REMOVE" == true ]]; then
    refs="$(member_references "$ITEM_NAME" || true)"
    if [[ -n "$refs" && "$FORCE" != true ]]; then
      echo "Error: Member '$ITEM_NAME' is still referenced by installed team(s):"
      printf '  %s\n' $refs
      echo "Use --force to remove it anyway."
      exit 1
    fi
    target_file="$TARGET_DIR/$(member_filename "$ITEM_NAME")"
    assert_path_within "$TARGET_DIR" "$target_file"
    if [[ -f "$target_file" ]]; then
      if [[ "$FORCE" != true ]] && ! is_managed_member_unchanged "$target_file"; then
        echo "Kept member '$ITEM_NAME': file is not installer-owned or was locally modified. Use --force to remove it explicitly."
        exit 0
      fi
      rm "$target_file"
      forget_managed_member "$(basename "$target_file")"
      if [[ "$PLATFORM" == "codex" && "$SCOPE" == "user" ]]; then
        managed_file="$(managed_codex_wrapper_path "$ITEM_NAME")"
        assert_path_within "$ROOT_DIR/managed-agents" "$managed_file"
        rm -f "$managed_file"
      fi
      echo "Removed member '$ITEM_NAME' from $TARGET_DIR"
    else
      echo "Member '$ITEM_NAME' is not installed in $TARGET_DIR"
    fi
    exit 0
  fi

  install_member "$ITEM_NAME"
  echo ""
  echo "Member '$ITEM_NAME' ($PLATFORM) installed → $TARGET_DIR/"
  exit 0
fi

ITEM_NAME="$(resolve_alias teams "$ITEM_NAME")"
require_safe_id "team" "$ITEM_NAME"
MANIFEST_PATH="$(team_manifest_path "$ITEM_NAME")"
[[ -f "$MANIFEST_PATH" ]] || {
  echo "Error: Team '$ITEM_NAME' not found at $MANIFEST_PATH"
  BOARD_NAME="$(lookup_board "$ITEM_NAME")"
  if [[ -n "$BOARD_NAME" ]]; then
    echo "This read-only panel now runs as the 'expert-board' workflow with board: \"$BOARD_NAME\". Nothing to install."
  fi
  echo "Use --list to see available teams."
  exit 1
}

TEAM_META_FILE="$META_DIR/$ITEM_NAME.members"
assert_path_within "$META_DIR" "$TEAM_META_FILE"

if [[ "$REMOVE" == true ]]; then
  TEAM_RECIPE_FILE="$META_DIR/$ITEM_NAME/team.yaml"
  LEGACY_TEAM_INDEX="$LEGACY_META_DIR/$ITEM_NAME.members"
  LEGACY_TEAM_RECIPE="$LEGACY_META_DIR/$ITEM_NAME/team.yaml"
  if [[ -e "$LEGACY_TEAM_INDEX" || -L "$LEGACY_TEAM_INDEX" || \
        -e "$LEGACY_TEAM_RECIPE" || -L "$LEGACY_TEAM_RECIPE" ]]; then
    echo "  Kept legacy metadata for $ITEM_NAME (ownership cannot be proven safely)"
    echo "Removal aborted: preserving all members referenced by retained legacy metadata."
    exit 0
  fi
  if [[ -e "$TEAM_META_FILE" || -L "$TEAM_META_FILE" ]]; then
    if ! is_managed_metadata_unchanged "$ITEM_NAME.members" "$TEAM_META_FILE"; then
      echo "  Kept index: $ITEM_NAME.members (not installer-owned or locally modified)"
      echo "Removal aborted: preserving the team recipe and all referenced members."
      exit 0
    fi
  fi
  if [[ -e "$TEAM_RECIPE_FILE" || -L "$TEAM_RECIPE_FILE" ]]; then
    if ! is_managed_recipe_unchanged "$ITEM_NAME" "$TEAM_RECIPE_FILE"; then
      echo "  Kept recipe: $ITEM_NAME/team.yaml (not installer-owned or locally modified)"
      echo "Removal aborted: preserving the team index and all referenced members."
      exit 0
    fi
  fi

  if is_managed_metadata_unchanged "$ITEM_NAME.members" "$TEAM_META_FILE"; then
    load_members_from_stream < "$TEAM_META_FILE"
  else
    # Never trust unowned or modified metadata as path input. The canonical
    # recipe is the safe fallback; preserved .members files will also prevent
    # their referenced installed agents from being pruned below.
    load_members_from_stream < <(team_all_members "$MANIFEST_PATH")
  fi

  if [[ -e "$TEAM_META_FILE" || -L "$TEAM_META_FILE" ]]; then
    if is_managed_metadata_unchanged "$ITEM_NAME.members" "$TEAM_META_FILE"; then
      rm -f "$TEAM_META_FILE"
      forget_managed_members_index "$ITEM_NAME"
    else
      echo "  Kept index: $ITEM_NAME.members (not installer-owned or locally modified)"
    fi
  fi
  remove_team_manifest "$ITEM_NAME"
  for member_id in "${members[@]}"; do
    [[ -n "$member_id" ]] || continue
    remove_member_if_unused "$member_id"
  done
  echo "Removed team '$ITEM_NAME' metadata from $META_DIR"
  exit 0
fi

if [[ "$INCLUDE_CANDIDATES" == true ]]; then
  load_members_from_stream < <(team_all_members "$MANIFEST_PATH")
else
  load_members_from_stream < <(team_members "$MANIFEST_PATH")
fi
[[ "${#members[@]}" -gt 0 ]] || {
  echo "Error: Team '$ITEM_NAME' has no members in $MANIFEST_PATH"
  exit 1
}

for member_id in "${members[@]}"; do
  [[ -n "$member_id" ]] || continue
  install_member "$member_id"
done

write_managed_members_index "$ITEM_NAME" "$TEAM_META_FILE" "${members[@]}"
install_team_manifest "$ITEM_NAME" "$MANIFEST_PATH"
remove_legacy_team_recipe "$ITEM_NAME"

CORE_MEMBER_COUNT="$(team_core_member_count "$MANIFEST_PATH")"
ALL_MEMBER_COUNT="$(team_all_members "$MANIFEST_PATH" | wc -l | tr -d ' ')"
CANDIDATE_MEMBER_COUNT=$((ALL_MEMBER_COUNT - CORE_MEMBER_COUNT))
INSTALLED_CANDIDATE_COUNT=$((${#members[@]} - CORE_MEMBER_COUNT))

echo ""
echo "Team recipe '$ITEM_NAME' ($PLATFORM): ${#members[@]} referenced member definition(s) checked → $TARGET_DIR/"
echo "  core members: $CORE_MEMBER_COUNT"
echo "  optional candidate specialists: $CANDIDATE_MEMBER_COUNT available; $INSTALLED_CANDIDATE_COUNT installed"
echo "Repository team index written to $TEAM_META_FILE"
echo "Repository team recipe status: $RECIPE_INSTALL_STATUS at $(team_manifest_install_path "$ITEM_NAME")"
echo "This recipe is installer metadata; neither Claude nor Codex reads it as native runtime configuration."
if [[ "$SCOPE" == "repo" ]]; then
  echo "Commit .${PLATFORM}/agents/ and .agents/team-recipes/ if you want to share this setup."
elif [[ "$PLATFORM" == "claude" ]]; then
  echo "Restart your Claude Code session or run /agents to load new members."
else
  echo "Restart your Codex session, then smoke-test by explicitly spawning one installed agent by its TOML name."
fi
