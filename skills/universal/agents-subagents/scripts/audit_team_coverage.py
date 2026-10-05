#!/usr/bin/env python3
"""Audit shared members, repository team recipes, and Codex parity."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
from library_layout import AGENTS_DIR, skill_names  # noqa: E402

CLAUDE_MEMBERS = AGENTS_DIR / "claude"
CODEX_MEMBERS = AGENTS_DIR / "codex"
TEAMS_DIR = AGENTS_DIR / "teams"
ALIAS_FILE = ROOT / "data" / "naming-aliases.json"
ALIAS_ID = re.compile(r"[a-z0-9][a-z0-9-]*")
DEBATE_METHODS_DIR = AGENTS_DIR / "templates" / "debate-methods"
DECISION_MASKS_DIR = AGENTS_DIR / "templates" / "decision-masks"

# Team manifests name masks by their canonical mask identity, which for two masks
# differs from the filename that carries them (`anchoring-reset` lives in
# `anchoring-mask.md`). Resolve through this map before falling back to
# `<name>.md`, so a rename of either side is a real error rather than a silent
# alias miss.
MASK_FILE_ALIASES = {
    "anchoring-reset": "anchoring-mask",
    "base-rate-reset": "base-rate-mask",
}

# Values `synthesis_owner` may take beyond a team's own member ids.
SYNTHESIS_OWNER_SENTINELS = {"parent-thread"}

OWNED_FILES_READ_ONLY_SENTINEL = "none — read-only analysis team"


def parse_team_manifest(path: Path) -> dict:
    """Parse the subset of YAML these manifests use.

    Top-level keys are either scalars, lists, or one-level mappings. A mapping's
    nested list may be indented 2 or 4 spaces depending on the file, so nested
    list items are attributed to the last nested key that opened a list rather
    than to a fixed indent level. Values are left as strings; callers compare
    against literals such as "true".
    """
    data: dict[str, object] = {}
    current_key = None
    nested_key = None
    list_keys = {"best_for", "members", "required_context", "optional_context", "verdict_options"}
    dict_keys = {
        "debate",
        "coordination",
        "expansion_gate",
        "stopping_rule",
        "synthesis",
        "hold_policy",
        "constraint_diagnosis",
        "throughput_target",
        "buffer_management",
        "algedonic_channel",
        "contribution_tracking",
        "trust",
        "install_guidance",
        "deliverable",
    }
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if stripped == "---":
            continue

        if indent == 0 and stripped.startswith("- ") and isinstance(data.get(current_key), list):
            data[current_key].append(stripped[2:].strip())
            continue

        if indent == 0:
            nested_key = None
            if stripped.endswith(":"):
                current_key = stripped[:-1]
                if current_key in dict_keys:
                    data[current_key] = {}
                else:
                    data[current_key] = []
            else:
                key, value = stripped.split(":", 1)
                current_key = key
                data[key] = value.strip()
            continue

        if stripped.startswith("- "):
            value = stripped[2:].split("#")[0].strip()
            container = data.get(current_key)
            if isinstance(container, dict):
                # Nested list under a mapping, e.g. debate.decision_masks.
                if nested_key is not None and isinstance(container.get(nested_key), list):
                    container[nested_key].append(value)
            elif isinstance(container, list):
                container.append(value)
            continue

        if isinstance(data.get(current_key), dict) and ":" in stripped:
            key, value = stripped.split(":", 1)
            value = value.split("#")[0].strip() if value.strip() else ""
            nested_key = key
            data[current_key][key] = [] if value == "" else value
    return data


def frontmatter_skills(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return []
    frontmatter = match.group(1)
    skills: list[str] = []
    in_skills = False
    for line in frontmatter.splitlines():
        if line.startswith("skills:"):
            if "[" in line and "]" in line:
                inside = line.split("[", 1)[1].rsplit("]", 1)[0]
                return [item.strip() for item in inside.split(",") if item.strip()]
            in_skills = True
            continue
        if in_skills:
            if line.startswith("  - "):
                skills.append(line[4:].strip())
            elif line and not line.startswith(" "):
                break
    return skills


def frontmatter_scalar(path: Path, key: str) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    frontmatter = match.group(1)
    scalar_match = re.search(rf"^{re.escape(key)}:\s*\"?([^\n\"]+)\"?$", frontmatter, re.M)
    return scalar_match.group(1).strip() if scalar_match else None


def expected_family(agent_id: str) -> str:
    if agent_id.startswith("project-"):
        parts = agent_id.split("-")
        return parts[1] if len(parts) > 1 else "project"
    if agent_id.startswith("idea-product-evaluation-"):
        return "evaluation"
    return agent_id.split("-", 1)[0]


def mask_path(mask_name: str) -> Path:
    stem = MASK_FILE_ALIASES.get(mask_name, mask_name)
    return DECISION_MASKS_DIR / f"{stem}.md"


def normalized_sentinel(value: str) -> str:
    """Compare sentinel prose ignoring dash style and spacing."""
    return re.sub(r"[\s‐-―-]+", " ", value).strip().lower()


def check_team_values(
    team_name: str,
    manifest: dict,
    errors: list[str],
    warnings: list[str],
) -> None:
    """Assert on team.yaml values, not merely on key presence."""
    debate = manifest.get("debate")
    if isinstance(debate, dict):
        if str(debate.get("enabled", "")).strip().lower() == "true":
            method = debate.get("method")
            if not isinstance(method, str) or not method.strip():
                errors.append(f"{team_name}: debate.enabled is true but debate.method is unset")
            else:
                method_file = DEBATE_METHODS_DIR / f"{method.strip()}.md"
                if not method_file.is_file():
                    errors.append(
                        f"{team_name}: debate.method '{method.strip()}' has no template at "
                        f"agents/templates/debate-methods/{method.strip()}.md"
                    )

        masks = debate.get("decision_masks")
        if isinstance(masks, list):
            for mask in masks:
                if not isinstance(mask, str) or not mask.strip():
                    continue
                resolved = mask_path(mask.strip())
                if not resolved.is_file():
                    errors.append(
                        f"{team_name}: debate.decision_masks entry '{mask.strip()}' has no "
                        f"template at agents/templates/decision-masks/{resolved.name}"
                    )

    synthesis_owner = manifest.get("synthesis_owner")
    if isinstance(synthesis_owner, str) and synthesis_owner.strip():
        owner = synthesis_owner.strip()
        members = manifest.get("members")
        member_ids = set(members) if isinstance(members, list) else set()
        if owner not in member_ids | SYNTHESIS_OWNER_SENTINELS:
            errors.append(
                f"{team_name}: synthesis_owner '{owner}' is neither a team member nor "
                + ", ".join(sorted(SYNTHESIS_OWNER_SENTINELS))
            )

    constraint = manifest.get("constraint_diagnosis")
    if isinstance(constraint, dict):
        identified = constraint.get("identified_constraint")
        if isinstance(identified, str) and identified.strip().lower() == "unknown":
            warnings.append(
                f"{team_name}: constraint_diagnosis.identified_constraint is 'unknown' (dead field)"
            )

    # Schema fields still being rolled out: validate shape when present, warn when
    # absent. Absence must not fail this pass.
    owned_files = manifest.get("owned_files")
    if owned_files is None:
        warnings.append(f"{team_name}: missing owned_files")
    elif isinstance(owned_files, str):
        if normalized_sentinel(owned_files) != normalized_sentinel(OWNED_FILES_READ_ONLY_SENTINEL):
            errors.append(
                f"{team_name}: owned_files scalar must be '{OWNED_FILES_READ_ONLY_SENTINEL}', "
                f"got '{owned_files}'"
            )
    elif not isinstance(owned_files, list):
        errors.append(f"{team_name}: owned_files must be a list or the read-only sentinel string")

    do_not_touch = manifest.get("do_not_touch")
    if do_not_touch is None:
        warnings.append(f"{team_name}: missing do_not_touch")
    elif not isinstance(do_not_touch, list):
        errors.append(f"{team_name}: do_not_touch must be a list")

    deliverable = manifest.get("deliverable")
    if deliverable is None:
        warnings.append(f"{team_name}: missing deliverable")
    elif not isinstance(deliverable, dict):
        errors.append(f"{team_name}: deliverable must be a mapping")
    else:
        for field in ("shape", "required_sections"):
            if field not in deliverable:
                errors.append(f"{team_name}: deliverable is missing '{field}'")
        sections = deliverable.get("required_sections")
        if sections is not None and not isinstance(sections, list):
            errors.append(f"{team_name}: deliverable.required_sections must be a list")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--aliases",
        type=Path,
        default=ALIAS_FILE,
        help=f"naming-aliases JSON file (default: {ALIAS_FILE.relative_to(ROOT)})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.aliases.is_file():
        print(
            f"error: alias file not found: {args.aliases}; alias-collision checks cannot run",
            file=sys.stderr,
        )
        return 2
    known_skills = set(skill_names())
    claude_members = {path.stem: path for path in CLAUDE_MEMBERS.glob("*.md")}
    codex_members = {path.stem.replace("_", "-"): path for path in CODEX_MEMBERS.glob("*.toml")}
    teams = {path.parent.name: parse_team_manifest(path) for path in TEAMS_DIR.glob("*/team.yaml")}
    def unique_keys(pairs):
        keys = [k for k, _ in pairs]
        dupes = sorted({k for k in keys if keys.count(k) > 1})
        if dupes:
            raise ValueError(f"duplicate keys {dupes}")
        return dict(pairs)

    try:
        aliases = json.loads(args.aliases.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    except ValueError as exc:  # JSONDecodeError and duplicate keys (a later value silently won)
        print(f"error: cannot read alias file {args.aliases}: {exc}", file=sys.stderr)
        return 2
    # A misspelled or missing top-level key would otherwise skip the alias
    # checks and exit 0, so a broken alias file must stop the audit.
    if not isinstance(aliases, dict) or not all(
        isinstance(aliases.get(kind), dict) for kind in ("members", "teams")
    ):
        print(
            f"error: alias file lacks 'members'/'teams' mapping: {args.aliases}; "
            "alias-collision checks cannot run",
            file=sys.stderr,
        )
        return 2
    # A list or null canonical id crashed the collision check, and an empty,
    # padded or invisible-character name matched nothing, so each must stop the
    # audit as a bad file rather than pass or read as a missing id.
    bad = [
        f"{kind}: {alias!r} -> {canonical!r}"
        for kind in ("members", "teams")
        for alias, canonical in aliases[kind].items()
        if not (ALIAS_ID.fullmatch(alias) and isinstance(canonical, str) and ALIAS_ID.fullmatch(canonical))
    ]
    if bad:
        print(
            f"error: alias names and canonical ids must be non-empty strings of lowercase letters, digits and hyphens in {args.aliases}: "
            + "; ".join(bad),
            file=sys.stderr,
        )
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    missing_codex_members: set[str] = set()
    missing_skill_links: list[str] = []
    invalid_skill_refs: dict[str, list[str]] = {}
    codex_context_drift: list[str] = []

    required_team_keys = {
        "name",
        "family",
        "description",
        "members",
        "best_for",
        "required_context",
        "optional_context",
        "concurrency_mode",
        "synthesis_owner",
        "debate",
    }

    for team_name, manifest in sorted(teams.items()):
        missing_keys = sorted(required_team_keys - manifest.keys())
        if missing_keys:
            errors.append(f"{team_name}: missing keys {missing_keys}")
        if manifest.get("name") != team_name:
            errors.append(f"{team_name}: manifest name '{manifest.get('name')}' does not match directory")
        family = str(manifest.get("family", ""))
        expected = expected_family(team_name)
        if family != expected:
            errors.append(f"{team_name}: family '{family}' should be '{expected}'")
        for member_id in manifest.get("members", []):
            if member_id not in claude_members:
                errors.append(f"{team_name}: missing canonical Claude member '{member_id}'")
            elif member_id not in codex_members:
                missing_codex_members.add(member_id)
        check_team_values(team_name, manifest, errors, warnings)

    for member_id, member_path in sorted(claude_members.items()):
        family = frontmatter_scalar(member_path, "family")
        if not family:
            errors.append(f"{member_id}: missing family frontmatter")
            continue
        expected = expected_family(member_id)
        if family != expected:
            errors.append(f"{member_id}: family '{family}' should be '{expected}'")

    context_first_needles = (
        "Read provided context artifacts in order:",
        "Do not rediscover the repo when prepared context covers the task.",
    )
    for member_id, member_path in sorted(claude_members.items()):
        codex_path = codex_members.get(member_id)
        if not codex_path:
            continue
        claude_text = member_path.read_text(encoding="utf-8")
        codex_text = codex_path.read_text(encoding="utf-8")
        missing = [needle for needle in context_first_needles if needle in claude_text and needle not in codex_text]
        if missing:
            codex_context_drift.append(f"{member_id}: missing Codex parity for {', '.join(repr(n) for n in missing)}")

    skill_prefix_counts: dict[str, int] = {}
    for member_id, member_path in claude_members.items():
        skills = frontmatter_skills(member_path)
        if not skills:
            missing_skill_links.append(member_id)
            continue
        bad_skills = [skill for skill in skills if skill not in known_skills]
        if bad_skills:
            invalid_skill_refs[member_id] = bad_skills
            continue
        for skill in skills:
            prefix = skill.split("-", 1)[0]
            skill_prefix_counts[prefix] = skill_prefix_counts.get(prefix, 0) + 1

    if missing_skill_links:
        errors.append(
            "canonical Claude members missing skills links: "
            + ", ".join(sorted(missing_skill_links))
        )
    if invalid_skill_refs:
        errors.append(
            "invalid skill references: "
            + "; ".join(
                f"{member_id} -> {', '.join(skills)}"
                for member_id, skills in sorted(invalid_skill_refs.items())
            )
        )

    for kind in ("members", "teams"):
        existing = claude_members if kind == "members" else teams
        for alias, canonical in sorted(aliases[kind].items()):
            if canonical not in existing:
                errors.append(f"{kind[:-1]} alias '{alias}' resolves to missing canonical id '{canonical}'")
            if alias in existing:
                errors.append(f"{kind[:-1]} alias '{alias}' collides with canonical id")

    if missing_codex_members:
        warnings.append(
            "canonical Codex members missing for "
            f"{len(missing_codex_members)} shared roles; deploy fallback generation will be used"
        )
    if codex_context_drift:
        warnings.extend(codex_context_drift)

    summary = {
        "team_count": len(teams),
        "claude_member_count": len(claude_members),
        "codex_member_count": len(codex_members),
        "missing_codex_members": sorted(missing_codex_members),
        "missing_skill_links": sorted(missing_skill_links),
        "invalid_skill_refs": invalid_skill_refs,
        "all_claude_member_skill_refs_valid": not missing_skill_links and not invalid_skill_refs,
        "codex_context_drift": codex_context_drift,
        "skill_prefix_counts": dict(sorted(skill_prefix_counts.items())),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
