#!/usr/bin/env python3
"""Audit installed Claude/Codex agents against the local tier policy.

The audit is offline and intentionally reads only model-routing fields. It does
not print configuration values outside those fields or any environment value.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
try:
    import tomllib
except ImportError:  # Python 3.10 and older
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError as exc:  # pragma: no cover - environment guard
        raise SystemExit(
            "TOML support unavailable: run with Python 3.11+ (this file needs "
            "the stdlib tomllib) or install the 'tomli' backport."
        ) from exc
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data/model-policy.json"
# The agent catalog lives outside this skill, at <repo>/agents (see scripts/library_layout.py).
AGENTS_DIR = Path(__file__).resolve().parents[4] / "agents"
CODEX_CATALOG = AGENTS_DIR / "codex"
CLAUDE_CATALOG = AGENTS_DIR / "claude"
TEAMS_DIR = AGENTS_DIR / "teams"
TIERS = {"critical", "mechanical", "standard"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
CODEX_AGENT_KEYS = {
    "default_subagent_model",
    "default_subagent_reasoning_effort",
    "max_concurrent_threads_per_session",
    "max_threads",  # documented legacy alias
}
MAX_RUNTIME_FILE_BYTES = 1024 * 1024


def read_runtime_text(path: Path) -> str:
    """Read one bounded regular file without blocking on special files."""
    resolved = path.resolve(strict=True)
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(resolved, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise OSError("runtime input is not a regular file")
        if info.st_uid != os.getuid():
            raise OSError("runtime input is not owned by the current user")
        if info.st_size > MAX_RUNTIME_FILE_BYTES:
            raise OSError("runtime input exceeds the 1 MiB safety limit")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, MAX_RUNTIME_FILE_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_RUNTIME_FILE_BYTES:
                raise OSError("runtime input exceeds the 1 MiB safety limit")
        return b"".join(chunks).decode("utf-8")
    finally:
        os.close(fd)


def canonical_id(path: Path, platform: str) -> str:
    return path.stem.replace("_", "-") if platform == "codex" else path.stem


def load_policy(path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    try:
        policy = json.loads(read_runtime_text(path))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {}, [f"policy cannot be loaded: {exc}"]
    if not isinstance(policy, dict):
        return {}, ["policy root must be an object"]

    expected_root = {
        "schema_version",
        "last_verified",
        "codex",
        "claude",
        "claude_global_subagent_override",
    }
    unknown = sorted(set(policy) - expected_root)
    missing = sorted(expected_root - set(policy))
    if unknown:
        errors.append("policy has unknown keys: " + ", ".join(unknown))
    if missing:
        errors.append("policy is missing keys: " + ", ".join(missing))
    if type(policy.get("schema_version")) is not int or policy.get("schema_version") != 1:
        errors.append("policy schema_version must be 1")
    try:
        date.fromisoformat(policy.get("last_verified", ""))
    except (TypeError, ValueError):
        errors.append("policy last_verified must be a real ISO date")

    override = policy.get("claude_global_subagent_override")
    if not isinstance(override, dict):
        errors.append("policy claude_global_subagent_override must be an object")
    else:
        allowed_override_keys = {"allowed_models"}
        unknown_override_keys = sorted(set(override) - allowed_override_keys)
        missing_override_keys = sorted(allowed_override_keys - set(override))
        if unknown_override_keys:
            errors.append(
                "policy claude_global_subagent_override has unknown keys: "
                + ", ".join(unknown_override_keys)
            )
        if missing_override_keys:
            errors.append(
                "policy claude_global_subagent_override is missing keys: "
                + ", ".join(missing_override_keys)
            )
        allowed_models = override.get("allowed_models")
        if not isinstance(allowed_models, list) or not allowed_models:
            errors.append(
                "policy claude_global_subagent_override.allowed_models must be a non-empty list"
            )
        elif (
            any(
                not isinstance(model, str)
                or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", model)
                for model in allowed_models
            )
            or len(set(allowed_models)) != len(allowed_models)
        ):
            errors.append(
                "policy claude_global_subagent_override.allowed_models must contain unique safe model IDs"
            )

    for platform in ("codex", "claude"):
        section = policy.get(platform)
        if not isinstance(section, dict):
            errors.append(f"policy {platform} section must be an object")
            continue
        tier_keys = set(section)
        if tier_keys != TIERS:
            errors.append(
                f"policy {platform} tiers must be exactly: " + ", ".join(sorted(TIERS))
            )
        for tier, entry in section.items():
            if tier not in TIERS or not isinstance(entry, dict):
                continue
            allowed = (
                {"model", "model_reasoning_effort", "materialize"}
                if platform == "codex"
                else {"model", "effort"}
            )
            unknown_entry = sorted(set(entry) - allowed)
            required = allowed - {"materialize"}
            missing_entry = sorted(required - set(entry))
            if unknown_entry:
                errors.append(
                    f"policy {platform}.{tier} has unknown keys: "
                    + ", ".join(unknown_entry)
                )
            if missing_entry:
                errors.append(
                    f"policy {platform}.{tier} is missing keys: "
                    + ", ".join(missing_entry)
                )
            model = entry.get("model")
            effort_key = "model_reasoning_effort" if platform == "codex" else "effort"
            effort = entry.get(effort_key)
            if not isinstance(model, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", model):
                errors.append(f"policy {platform}.{tier}.model is invalid")
            if effort not in EFFORTS:
                errors.append(f"policy {platform}.{tier}.{effort_key} is invalid")
            if "materialize" in entry and not isinstance(entry["materialize"], bool):
                errors.append(f"policy {platform}.{tier}.materialize must be boolean")
    return policy, errors


def optional_members(teams_dir: Path) -> set[str]:
    """Members that appear only in teams marked ``install: opt-in``.

    deploy-all-teams.sh skips opt-in teams unless ``--include-opt-in`` is passed,
    so a complete-inventory gate must not demand those members either. A member
    listed by any default-install team stays required. Parsing is deliberately
    stdlib-only and tolerant: a malformed recipe yields no optional members,
    which keeps the gate strict rather than lenient.
    """
    opt_in: set[str] = set()
    default: set[str] = set()
    if not teams_dir.is_dir():
        return set()
    for recipe in sorted(teams_dir.glob("*/team.yaml")):
        try:
            text = read_runtime_text(recipe)
        except (OSError, UnicodeError):
            continue
        members: list[str] = []
        in_block = False
        for line in text.splitlines():
            if re.match(r"^members:\s*$", line):
                in_block = True
                continue
            if in_block:
                item = re.match(r"^\s*-\s*([A-Za-z0-9_.-]+)\s*$", line)
                if item:
                    members.append(item.group(1).replace("_", "-"))
                    continue
                if line.strip() and not line.startswith((" ", "\t")):
                    in_block = False
        is_opt_in = re.search(r"^install:\s*opt-in\s*$", text, re.MULTILINE) is not None
        (opt_in if is_opt_in else default).update(members)
    return opt_in - default


def catalog_tiers(platform: str, policy: dict) -> tuple[dict[str, str], list[str]]:
    root = CODEX_CATALOG if platform == "codex" else CLAUDE_CATALOG
    suffix = "*.toml" if platform == "codex" else "*.md"
    result: dict[str, str] = {}
    errors: list[str] = []
    claude_pairs = {
        (entry["model"], entry["effort"]): tier
        for tier, entry in policy.get("claude", {}).items()
        if isinstance(entry, dict) and "model" in entry and "effort" in entry
    }
    for path in sorted(root.glob(suffix)):
        item_id = canonical_id(path, platform)
        try:
            text = read_runtime_text(path)
        except (OSError, UnicodeError) as exc:
            errors.append(f"{platform} catalog agent {item_id} cannot be read safely: {exc}")
            continue
        if platform == "codex":
            match = re.search(r"^# model_tier: ([a-z-]+)$", text, re.MULTILINE)
            tier = match.group(1) if match else "standard"
        else:
            model = re.search(r"^model:\s*([^\s#]+)", text, re.MULTILINE)
            effort = re.search(r"^effort:\s*([^\s#]+)", text, re.MULTILINE)
            tier = claude_pairs.get(
                (model.group(1) if model else "", effort.group(1) if effort else ""), ""
            )
        if tier not in TIERS:
            errors.append(f"{platform} catalog agent {item_id} has unrecognized tier")
            continue
        result[item_id] = tier
    return result, errors


def read_codex_defaults(path: Path) -> tuple[tuple[str, str] | None, list[str]]:
    try:
        data = tomllib.loads(read_runtime_text(path))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        return None, [f"Codex config cannot be loaded: {exc}"]
    agents = data.get("agents")
    if not isinstance(agents, dict):
        # Not a runtime breakage: `agents.enabled` defaults to true in Codex, so
        # subagents still spawn. What is missing is the model default, so every
        # standard-tier member silently inherits the parent session's model.
        # deploy-preset.sh provisions this table on user-scope Codex installs.
        return None, [
            "Codex config is missing an [agents] table, so standard-tier members inherit "
            "the parent session's model instead of the policy default. "
            "Provision it with: deploy-preset.sh <member> --member --platform codex --user "
            "(or paste [agents] with default_subagent_model and "
            "default_subagent_reasoning_effort from data/model-policy.json codex.standard). "
            "Subagents themselves still run: agents.enabled defaults to true."
        ]
    unknown = sorted(set(agents) - CODEX_AGENT_KEYS)
    errors = []
    if unknown:
        errors.append("Codex [agents] has unknown keys: " + ", ".join(unknown))
    model = agents.get("default_subagent_model")
    effort = agents.get("default_subagent_reasoning_effort")
    if not isinstance(model, str) or not isinstance(effort, str):
        errors.append("Codex [agents] must declare recognized default model and effort keys")
        return None, errors
    return (model, effort), errors


def audit_codex(
    directory: Path,
    config_path: Path,
    catalog: dict[str, str],
    policy: dict,
    exemptions: set[str],
    require_complete: bool,
    optional: set[str] | None = None,
) -> tuple[dict, list[str]]:
    defaults, errors = read_codex_defaults(config_path)
    standard = policy["codex"]["standard"]
    expected_default = (standard["model"], standard["model_reasoning_effort"])
    if defaults is not None and defaults != expected_default:
        errors.append("Codex inherited standard tier differs from model-policy.json")

    counts: Counter[str] = Counter()
    recognized: list[str] = []
    exempt: list[str] = []
    unknown: list[str] = []
    for path in sorted(directory.glob("*.toml")) if directory.is_dir() else []:
        item_id = canonical_id(path, "codex")
        if item_id not in catalog:
            if item_id in exemptions:
                exempt.append(item_id)
            else:
                unknown.append(item_id)
            continue
        tier = catalog[item_id]
        counts[tier] += 1
        recognized.append(item_id)
        try:
            installed = tomllib.loads(read_runtime_text(path))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"Codex agent {item_id} cannot be parsed: {exc}")
            continue
        model = installed.get("model")
        effort = installed.get("model_reasoning_effort")
        expected = policy["codex"][tier]
        expected_pair = (expected["model"], expected["model_reasoning_effort"])
        materialized = expected.get("materialize", True)
        if (model is None) != (effort is None):
            errors.append(f"Codex agent {item_id} has an incomplete model/effort pin")
        elif materialized and (model, effort) != expected_pair:
            errors.append(f"Codex agent {item_id} must materialize tier {tier}")
        elif not materialized and model is not None and (model, effort) != expected_pair:
            errors.append(f"Codex agent {item_id} effective routing differs from tier {tier}")
    if unknown:
        errors.append("unrecognized Codex installed agents require an explicit exemption: " + ", ".join(unknown))
    optional = optional or set()
    absent = set(catalog) - set(recognized) - exemptions
    optional_not_installed = sorted(absent & optional)
    missing = sorted(absent - optional)
    if require_complete and missing:
        errors.append("missing canonical Codex agents: " + ", ".join(missing))
    return {
        "recognized": recognized,
        "exempt": exempt,
        "unknown": unknown,
        "missing_catalog_count": len(missing),
        "missing": missing,
        "optional_not_installed": optional_not_installed,
        "tiers": dict(sorted(counts.items())),
    }, errors


def claude_override_sources(settings_path: Path) -> tuple[list[tuple[str, str]], bool]:
    """Return override source/model pairs without exposing models to callers."""
    sources: list[tuple[str, str]] = []
    current_process_model = os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL")
    if current_process_model:
        sources.append(("current-process environment", current_process_model))
    try:
        settings = json.loads(read_runtime_text(settings_path))
    except FileNotFoundError:
        return sources, False
    except (OSError, UnicodeError, json.JSONDecodeError):
        return sources, True
    if not isinstance(settings, dict):
        return sources, True
    env = settings.get("env", {})
    if not isinstance(env, dict):
        return sources, True
    persistent_model = env.get("CLAUDE_CODE_SUBAGENT_MODEL")
    if persistent_model:
        if not isinstance(persistent_model, str):
            return sources, True
        sources.append(("persistent Claude settings", persistent_model))
    return sources, False


def parse_claude_pair(path: Path) -> tuple[str | None, str | None]:
    text = read_runtime_text(path)
    model = re.search(r"^model:\s*([^\s#]+)", text, re.MULTILINE)
    effort = re.search(r"^effort:\s*([^\s#]+)", text, re.MULTILINE)
    return (model.group(1) if model else None, effort.group(1) if effort else None)


def audit_claude(
    directory: Path,
    settings_path: Path,
    catalog: dict[str, str],
    policy: dict,
    exemptions: set[str],
    require_complete: bool,
    optional: set[str] | None = None,
) -> tuple[dict, list[str]]:
    errors: list[str] = []
    overrides, settings_unreadable = claude_override_sources(settings_path)
    if settings_unreadable:
        errors.append("Claude persistent settings could not be parsed")
    override_sources = [source for source, _model in overrides]
    allowed_models = set(policy["claude_global_subagent_override"]["allowed_models"])
    unapproved_sources = [
        source for source, model in overrides if model not in allowed_models
    ]
    if unapproved_sources:
        errors.append(
            "CLAUDE_CODE_SUBAGENT_MODEL is not an allowed global override (source: "
            + ", ".join(unapproved_sources)
            + "; value withheld)"
        )

    counts: Counter[str] = Counter()
    recognized: list[str] = []
    exempt: list[str] = []
    unknown: list[str] = []
    for path in sorted(directory.glob("*.md")) if directory.is_dir() else []:
        item_id = canonical_id(path, "claude")
        if item_id not in catalog:
            if item_id in exemptions:
                exempt.append(item_id)
            else:
                unknown.append(item_id)
            continue
        tier = catalog[item_id]
        counts[tier] += 1
        recognized.append(item_id)
        expected = policy["claude"][tier]
        try:
            pair = parse_claude_pair(path)
        except (OSError, UnicodeError) as exc:
            errors.append(f"Claude agent {item_id} cannot be read: {exc}")
            continue
        if pair != (expected["model"], expected["effort"]):
            errors.append(f"Claude agent {item_id} routing differs from tier {tier}")
    if unknown:
        errors.append("unrecognized Claude installed agents require an explicit exemption: " + ", ".join(unknown))
    optional = optional or set()
    absent = set(catalog) - set(recognized) - exemptions
    optional_not_installed = sorted(absent & optional)
    missing = sorted(absent - optional)
    if require_complete and missing:
        errors.append("missing canonical Claude agents: " + ", ".join(missing))
    return {
        "recognized": recognized,
        "exempt": exempt,
        "unknown": unknown,
        "missing_catalog_count": len(missing),
        "missing": missing,
        "optional_not_installed": optional_not_installed,
        "tiers": dict(sorted(counts.items())),
        "global_override_sources": override_sources,
        "global_override_policy": (
            "allowed" if override_sources and not unapproved_sources
            else "unapproved" if override_sources
            else "none"
        ),
    }, errors


def parse_args() -> argparse.Namespace:
    home = Path.home()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=POLICY_PATH)
    parser.add_argument("--codex-config", type=Path, default=home / ".codex/config.toml")
    parser.add_argument("--codex-agents", type=Path, default=home / ".codex/agents")
    parser.add_argument("--claude-settings", type=Path, default=home / ".claude/settings.json")
    parser.add_argument("--claude-agents", type=Path, default=home / ".claude/agents")
    parser.add_argument("--teams-dir", type=Path, default=TEAMS_DIR,
                        help="team recipes; members only in `install: opt-in` teams are optional")
    parser.add_argument("--exempt-codex", action="append", default=[])
    parser.add_argument("--exempt-claude", action="append", default=[])
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="fail when any canonical agent is not installed or explicitly exempted",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy, errors = load_policy(args.policy)
    report: dict[str, object] = {"status": "FAIL"}
    if not errors:
        codex_catalog, codex_catalog_errors = catalog_tiers("codex", policy)
        claude_catalog, claude_catalog_errors = catalog_tiers("claude", policy)
        errors.extend(codex_catalog_errors + claude_catalog_errors)
        optional = optional_members(args.teams_dir)
        codex, codex_errors = audit_codex(
            args.codex_agents, args.codex_config, codex_catalog, policy,
            set(args.exempt_codex), args.require_complete, optional,
        )
        claude, claude_errors = audit_claude(
            args.claude_agents, args.claude_settings, claude_catalog, policy,
            set(args.exempt_claude), args.require_complete, optional,
        )
        errors.extend(codex_errors + claude_errors)
        report.update({"codex": codex, "claude": claude})
    report["errors"] = errors
    report["status"] = "PASS" if not errors else "FAIL"
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"effective-runtime audit: {report['status']}")
        for platform in ("codex", "claude"):
            item = report.get(platform)
            if isinstance(item, dict):
                print(
                    f"  {platform}: recognized={len(item['recognized'])} "
                    f"exempt={len(item['exempt'])} unknown={len(item['unknown'])} "
                    f"tiers={item['tiers']}"
                )
                if item.get("optional_not_installed"):
                    print(
                        f"  {platform}: optional (opt-in teams only), not installed: "
                        + ", ".join(item["optional_not_installed"])
                    )
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
