#!/usr/bin/env python3
"""Locate and read a skill's own data files from inside that skill.

Why this exists
---------------
Each skill is fully self-contained: it owns its `data/` and its `_lib/` copy of
this resolver. There is no repo-level shared directory to fall back to. That is
what lets a skill work when detached from the repo — public-repo clone, a copied
folder, or a Claude Code plugin (plugins cannot reference files outside their
own directory, so no shared path could reach them anyway).

    <skill>/
      +- SKILL.md               <- marks the skill root
      +- data/versions.json     framework/runtime versions (refresh-versions.py)
      +- data/model-pricing.json  LLM prices per 1M tokens (hand-maintained: no
      |                           public API resolves provider pricing)
      +- _lib/resolve_versions.py   <- this file
      +- scripts/cost_estimator.py

Paths are resolved with `resolve()` before any walking, and that is load-bearing.
`sync-*-skills.sh` deploys each skill as its OWN symlink:

    ~/.claude/skills/ai-llm -> <repo>/frameworks/shared-skills/skills/ai-llm

so a *lexical* relative path escapes into the deployment root:

    ~/.claude/skills/ai-llm/scripts/../../data/versions.json
      -> ~/.claude/data/versions.json          # wrong tree, usually absent

That path can even "succeed" by hitting an unrelated file of the same name,
which is worse than failing. `resolve()` follows the symlink back to the real
skill directory first.

Resolution order (first hit wins):
  1. $SHARED_SKILLS_VERSIONS / $SHARED_SKILLS_PRICING — explicit override
  2. the CALLER's skill-local data/ — found by walking up to the nearest
     ancestor holding a SKILL.md, the spec's own marker for "this is a skill"
  3. this file's own skill-local data/, for when the caller is outside a skill

Every function degrades to None/default rather than raising: a skill script must
stay runnable when the data file is absent, and a missing version is a reason to
say "unknown", never to crash.

Usage:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_lib"))
    from resolve_versions import version_of, price_of, pricing_stale_days

    version_of("next")            -> "16.3.0" or None
    version_of("next", "unknown") -> "16.3.0" or "unknown"
    price_of("claude-haiku-4-5")  -> {"input_per_1m": 1.0, ...} or None
    pricing_stale_days()          -> 42 if the table is 42d old past its
                                     window, else None
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Directory name holding the data files, relative to the skill root.
_DATA_DIRNAME = "data"
_DATA_FILENAME = "versions.json"
_PRICING_FILENAME = "model-pricing.json"

# How far up to walk before giving up. The real depth from a skill script is 3
# (scripts -> <skill> -> skills -> shared-skills); the extra headroom covers
# nested asset/build directories without walking to the filesystem root.
_MAX_WALK_UP = 8


def _walk_up_for_data(start: Path, filename: str = _DATA_FILENAME) -> Path | None:
    """Walk up from `start` looking for <ancestor>/data/<filename>.

    `resolve()` is essential, not cosmetic: skills deploy as symlinks, so a
    lexical walk stays inside ~/.claude|.agents|.codex and can silently match an
    unrelated same-named file. Resolving first puts us in the real repo tree.
    """
    try:
        here = start.resolve()
    except OSError:
        return None
    if here.is_file():
        here = here.parent
    for ancestor in [here, *here.parents][:_MAX_WALK_UP]:
        candidate = ancestor / _DATA_DIRNAME / filename
        if candidate.is_file():
            return candidate
    return None


def _skill_local_data(start: Path, filename: str) -> Path | None:
    """Find <skill-root>/data/<filename> for the skill containing `start`.

    The skill root is the nearest ancestor holding a SKILL.md — the spec's own
    marker for "this directory is a skill". Falling back to a plain few-levels-up
    walk would wrongly match a sibling skill's data/ when skills sit side by side.

    Deliberately does NOT resolve() the caller: a skill deployed by symlink
    should still prefer the data shipped alongside it in the repo, and resolve()
    lands in the same place for that case anyway.
    """
    try:
        here = start if start.is_dir() else start.parent
    except OSError:
        return None
    for ancestor in [here, *here.parents][:_MAX_WALK_UP]:
        if (ancestor / "SKILL.md").is_file():
            candidate = ancestor / _DATA_DIRNAME / filename
            return candidate if candidate.is_file() else None
    return None


def _locate(filename: str, env_var: str, caller_file: str | Path | None) -> Path | None:
    """Resolution order for any data file.

    The CALLER's own skill wins: each skill ships its own data/ and its own copy
    of this resolver, so a skill published alone — the public repo's allowlist, a
    single copied folder, a packaged plugin — finds its data without reaching
    outside itself. There is no repo-level master; the plain walk-up at the end
    only serves callers that sit outside any skill (a bare script, a test).
    """
    override = os.environ.get(env_var, "").strip()
    if override:
        p = Path(override).expanduser()
        return p if p.is_file() else None

    # 1. The calling skill's own data/ — self-contained, works when detached.
    if caller_file is not None:
        local = _skill_local_data(Path(caller_file), filename)
        if local is not None:
            return local

    # 2. This file's own skill-local data/ (the usual path: running as _lib/).
    local = _skill_local_data(Path(__file__), filename)
    if local is not None:
        return local

    # 3. No SKILL.md above either location — caller is outside a skill. Fall back
    #    to a plain walk for a sibling data/ so bare scripts still work.
    found = _walk_up_for_data(Path(__file__), filename)
    if found is not None:
        return found

    if caller_file is not None:
        return _walk_up_for_data(Path(caller_file), filename)
    return None


def versions_path(caller_file: str | Path | None = None) -> Path | None:
    """Return the path to versions.json, or None if it cannot be located.

    `caller_file` is optionally the calling module's `__file__`; passing it lets
    a skill that lives outside this tree still find a data/ dir of its own.
    """
    return _locate(_DATA_FILENAME, "SHARED_SKILLS_VERSIONS", caller_file)


def load_versions(caller_file: str | Path | None = None) -> dict[str, Any]:
    """Return the parsed versions document, or {} if unavailable/unparseable."""
    path = versions_path(caller_file)
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def version_of(
    package: str,
    default: str | None = None,
    caller_file: str | Path | None = None,
) -> str | None:
    """Return the resolved `latest` version for `package`, else `default`.

    `package` is the key used in versions.json (an npm name like "next" or
    "@angular/core", or an endoflife.date slug like "go"/"python").
    """
    entry = load_versions(caller_file).get("versions", {}).get(package)
    if isinstance(entry, dict):
        latest = entry.get("latest")
        if isinstance(latest, str) and latest:
            return latest
    return default


def refreshed_utc(caller_file: str | Path | None = None) -> str | None:
    """Return the ISO timestamp of the last refresh, or None."""
    stamp = load_versions(caller_file).get("refreshed_utc")
    return stamp if isinstance(stamp, str) and stamp else None


# --------------------------------------------------------------- model pricing

def pricing_path(caller_file: str | Path | None = None) -> Path | None:
    """Return the path to model-pricing.json, or None if unavailable."""
    return _locate(_PRICING_FILENAME, "SHARED_SKILLS_PRICING", caller_file)


def load_pricing(caller_file: str | Path | None = None) -> dict[str, Any]:
    """Return the parsed pricing document, or {} if unavailable/unparseable."""
    path = pricing_path(caller_file)
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def price_of(
    model_id: str,
    caller_file: str | Path | None = None,
) -> dict[str, Any] | None:
    """Return the pricing entry for `model_id`, or None.

    Accepts either the qualified key ("anthropic/claude-haiku-4-5") or the bare
    model name ("claude-haiku-4-5"); the bare form matches the first vendor that
    carries it, which is unambiguous in practice because vendors do not share
    model names.
    """
    models = load_pricing(caller_file).get("models", {})
    if not isinstance(models, dict):
        return None
    entry = models.get(model_id)
    if isinstance(entry, dict):
        return entry
    if "/" not in model_id:
        for key, value in models.items():
            if key.split("/", 1)[-1] == model_id and isinstance(value, dict):
                return value
    return None


def pricing_stale_days(caller_file: str | Path | None = None) -> int | None:
    """Days the pricing table is PAST its staleness window, or None if fresh.

    Returns None when the table is fresh, absent, or undated — callers warn only
    on a positive number, so a missing file never produces a spurious warning.
    """
    from datetime import date as _date

    doc = load_pricing(caller_file)
    stamp = doc.get("last_verified")
    if not isinstance(stamp, str):
        return None
    try:
        verified = _date.fromisoformat(stamp)
    except ValueError:
        return None
    window = doc.get("stale_after_days")
    window = window if isinstance(window, int) else 30
    age = (_date.today() - verified).days
    return age if age > window else None


if __name__ == "__main__":
    import sys

    # Pass __file__ exactly as the skill's scripts do. Without it the skill-local
    # tier cannot be used at all and resolution degrades to the bare walk-up —
    # so a self-test that omits it exercises the weakest path, not the real one.
    _self = __file__

    # A skill carries only the data it consumes: ai-llm has model-pricing.json
    # and no versions.json, and that is correct, not a failure. Report each file
    # independently and fail only when NEITHER resolves, which is the one case
    # that means resolution itself is broken.
    vpath = versions_path(_self)
    ppath = pricing_path(_self)

    if vpath is None:
        print("versions.json     : not carried by this skill")
    else:
        doc = load_versions(_self)
        entries = doc.get("versions", {})
        print(f"versions.json     : {vpath}")
        print(f"refreshed_utc     : {refreshed_utc(_self) or 'unknown'}")
        print(f"entries           : {len(entries)}")
        for key, entry in sorted(entries.items()):
            if isinstance(entry, dict):
                print(f"  {entry.get('label', key):16} {entry.get('latest', '?'):12} {key}")

    print()
    if ppath is None:
        print("model-pricing.json: not carried by this skill")
    else:
        pdoc = load_pricing(_self)
        stale = pricing_stale_days(_self)
        window = pdoc.get("stale_after_days", 30)
        window = window if isinstance(window, int) else 30
        state = f"[STALE by {stale - window}d]" if stale else "[fresh]"
        print(f"model-pricing.json: {ppath}")
        print(f"last_verified     : {pdoc.get('last_verified', 'unknown')}  {state}")
        print(f"models            : {len(pdoc.get('models', {}))}")

    if vpath is None and ppath is None:
        print("\nNeither data file resolved — resolution is broken, not merely absent.",
              file=sys.stderr)
        raise SystemExit(1)
