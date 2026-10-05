#!/usr/bin/env python3
"""Generate the deterministic Codex parent-led plan for a board-engine workflow (default: expert-board)."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
# The agent catalog lives outside this skill, at <repo>/agents (see scripts/library_layout.py).
AGENTS_DIR = Path(__file__).resolve().parents[4] / "agents"
WORKFLOW_DIR = AGENTS_DIR / "workflows"
OUTPUT = WORKFLOW_DIR / "expert-board.codex-plan.json"
CODEX_MEMBERS = AGENTS_DIR / "codex"

sys.path.insert(0, str(SCRIPT_DIR))
from generate_workflows import EXPERT_BOARD_MANIFEST, resolved_manifest  # noqa: E402


def deep_merge(base: dict, override: dict) -> dict:
    """Merge nested mappings without mutating either input."""
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def codex_agent_name(member_id: str) -> str:
    member_file = CODEX_MEMBERS / f"{member_id.replace('-', '_')}.toml"
    if not member_file.is_file():
        raise ValueError(f"missing canonical Codex member: {member_file}")
    match = re.search(
        r'^name\s*=\s*"([a-z0-9_]+)"\s*$',
        member_file.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise ValueError(f"missing or invalid Codex agent name: {member_file}")
    return match.group(1)


def worker(wid: str, board_key: str, variant_key: str, member: dict, candidate: bool = False) -> dict:
    role = member["role"]
    prefix = "candidate" if candidate else "panel"
    spawn = {
        "task_name": f"{slug(wid)}_{slug(board_key)}_{slug(variant_key)}_{prefix}_{slug(role)}",
        "fork_turns": "none",
    }
    if member.get("agentType"):
        spawn["agent_type"] = codex_agent_name(member["member_id"])
        spawn["on_agent_unavailable"] = {
            "action": "spawn_default_agent",
            "omit": "agent_type",
            "preserve": ["brief", "skills", "read_only"],
        }
    return {
        "role": role,
        "member_id": member["member_id"],
        "brief": member["brief"],
        "skills": member["skills"],
        "read_only": True,
        "spawn": spawn,
    }


def variant_plan(wid: str, board_key: str, variant_key: str, config: dict) -> dict:
    deliverable = copy.deepcopy(config.get("deliverable", {}))
    if config.get("deliverable_sections"):
        deliverable["required_sections"] = copy.deepcopy(config["deliverable_sections"])

    candidates = config.get("expansion_gate", {}).get("candidates", [])
    debate = copy.deepcopy(config.get("debate", {}))
    algedonic = copy.deepcopy(config.get("algedonic_channel", {}))
    expansion = config.get("expansion_gate", {})
    verification = copy.deepcopy(config.get("verification", {}))
    stopping = copy.deepcopy(config.get("stopping_rule", {}))
    return {
        "mode": None if variant_key == "default" else variant_key,
        "required_context": copy.deepcopy(config.get("required_context", [])),
        "optional_context": copy.deepcopy(config.get("optional_context", [])),
        "panel": [worker(wid, board_key, variant_key, item) for item in config.get("panel", [])],
        "candidate_panel": [
            worker(wid, board_key, variant_key, item, candidate=True) for item in candidates
        ],
        "dispatch_gates": {
            "context": {
                "rule": "every required_context field must be present and nonblank",
                "on_fail": "return data-gap result immediately; do not dispatch the normal panel",
                "strict": True,
            },
            "algedonic": {
                "signals": copy.deepcopy(algedonic.get("bypass_routing_for", [])),
                "match": "exact",
                "on_match": "return an immediate algedonic escalation; bypass normal panel, challenge, expansion, and synthesis",
                "panelist_alarm": "when signals exist, each memo may set alarm to one signal it sees happening now; any core memo alarm returns the same escalation with the alarmed memos, before expansion and synthesis",
            },
            "challenge": {
                "enabled": bool(debate.get("enabled", True)),
                "triggers": copy.deepcopy(debate.get("triggers", [])),
                "match": "exact",
                "on_no_match": "skip challenge and record that no documented debate trigger fired",
            },
            "evpi_expansion": {
                "rule": expansion.get("rule", "evpi"),
                "max_dynamic_members": expansion.get("max_dynamic_members", 0),
                "condition": "candidate_panel is nonempty and expected value of information justifies dispatch",
                "on_fail": "skip candidate dispatch",
            },
            "verification": {
                "required": bool(verification.get("required", False)),
                "mode": verification.get("mode"),
                "condition": "run after provisional synthesis when required; otherwise record skipped",
                "context": "use a new verifier with fork_turns none and pass only the question, evidence, and provisional synthesis",
            },
            "regret": {
                "protocol": stopping.get("protocol", "regret-min"),
                "reversibility": stopping.get("reversibility"),
                "max_regret_threshold": copy.deepcopy(stopping.get("max_regret_threshold")),
                "condition": "evaluate after challenge, EVPI expansion, and any required verification before final return",
            },
        },
        "contract": {
            "debate": debate,
            "coordination": copy.deepcopy(config.get("coordination", {})),
            "expansion_gate": {
                key: copy.deepcopy(value)
                for key, value in config.get("expansion_gate", {}).items()
                if key != "candidates"
            },
            "stopping_rule": stopping,
            "synthesis": copy.deepcopy(config.get("synthesis", {})),
            "deliverable": deliverable,
            "hold_policy": copy.deepcopy(config.get("hold_policy", {})),
            "verification": verification,
            "guardrails": copy.deepcopy(config.get("guardrails", [])),
            "algedonic_channel": algedonic,
        },
    }


def build_plan(path: Path = EXPERT_BOARD_MANIFEST) -> dict:
    wid = path.name.removesuffix(".manifest.json")
    manifest = resolved_manifest(path)
    defaults = manifest.get("defaults", {})
    boards = {}
    for board_key, board in manifest["boards"].items():
        board_base = {key: value for key, value in board.items() if key != "modes"}
        resolved_base = deep_merge(defaults, board_base)
        variants = {"default": variant_plan(wid, board_key, "default", resolved_base)}
        for mode_key, mode in board.get("modes", {}).items():
            variants[mode_key] = variant_plan(
                wid, board_key, mode_key, deep_merge(resolved_base, mode)
            )
        boards[board_key] = {
            "name": board.get("name", board_key),
            "migrated_from_recipe": board.get("migrated_from_recipe"),
            "variants": variants,
        }

    return {
        "schema_version": 1,
        "generated_from": f"agents/workflows/{path.name}",
        "runtime": "codex-parent-led-subagents",
        "native_saved_workflow": False,
        # Codex has no saved-workflow surface that loads this file, so a parent reads it
        # itself. Do not pull the whole document into context: it is one object keyed by
        # board, so slice the single board/variant being run (~3k tokens) instead of ~30k.
        "context_budget": {
            "whole_file_tokens": "~30k — do not load",
            "extract": f"jq '.execution_contract, .boards[\"<board>\"].variants[\"<variant>\"]' {wid}.codex-plan.json",
            "boards_are_independent": True,
        },
        "execution_contract": {
            "workspace": "same-chat workers share the parent checkout; use one writer or a separate worktree",
            "context": "launch every blind worker with fork_turns none and a self-contained brief",
            "orchestrator": "the parent owns context validation, dispatch, waits, expansion, and synthesis",
            "named_agent_fallback": "if a planned agent_type is unavailable, retry once with the default agent by omitting agent_type while preserving the role brief, skills list, and read-only constraint",
            "phases": [
                {"phase": "select-and-validate", "owner": "parent", "primitive": "local reasoning", "gate": "strict nonblank required_context"},
                {"phase": "algedonic-bypass", "owner": "parent", "primitive": "immediate return", "gate": "exact selected-variant algedonic signal"},
                {"phase": "blind-panel", "owner": "parent", "primitive": "spawn_agent", "gate": "context passed and no algedonic bypass"},
                {"phase": "collect", "owner": "parent", "primitive": "wait_agent", "gate": "any core memo alarm: algedonic escalation, stop"},
                {
                    "phase": "challenge",
                    "owner": "parent",
                    # `features.multi_agent` (default true) exposes exactly spawn_agent,
                    # send_input, resume_agent, wait_agent, and close_agent (config
                    # reference, verified 2026-09-11). Follow-ups go through send_input;
                    # no separate follow-up primitive or v2 flag is documented.
                    "primitive": "send_input",
                    "gate": "exact selected-variant debate trigger",
                },
                {"phase": "collect-challenge", "owner": "parent", "primitive": "wait_agent", "gate": "challenge dispatched"},
                {"phase": "evpi-expansion", "owner": "parent", "primitive": "spawn_agent", "gate": "EVPI justifies a listed candidate"},
                {"phase": "provisional-synthesis", "owner": "parent", "primitive": "local reasoning"},
                {"phase": "verification", "owner": "parent", "primitive": "spawn_agent", "gate": "selected variant requires verification"},
                {"phase": "regret-gate", "owner": "parent", "primitive": "local reasoning", "gate": "selected-variant regret threshold"},
                {"phase": "final-return", "owner": "parent", "primitive": "local reasoning"},
            ],
        },
        "boards": boards,
    }


def render(path: Path = EXPERT_BOARD_MANIFEST) -> str:
    return json.dumps(build_plan(path), ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when the generated plan is stale")
    parser.add_argument("--stdout", action="store_true", help="print the generated plan without writing")
    args = parser.parse_args()
    expected = render()
    if args.stdout:
        print(expected, end="")
        return 0
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print(f"stale generated Codex plan: {OUTPUT}", file=sys.stderr)
            return 1
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
