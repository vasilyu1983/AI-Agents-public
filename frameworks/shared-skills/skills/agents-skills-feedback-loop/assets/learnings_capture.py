#!/usr/bin/env python3
"""Closed learnings loop — Layer 1 (auto-capture). Runtime-neutral.

ONE script, TWO registrations:
  - Claude Code: ~/.claude/settings.json  hooks.SessionEnd  (fires once/session)
  - Codex CLI:   ~/.codex/hooks.json       hooks.Stop        (may fire per turn)

Both runtimes deliver {session_id, transcript_path, cwd, ...} on stdin, so the
logic is identical. Install via scripts/install_capture_hook.py.

Design contract (see references/closed-loop-capture.md):
  - Recursion-guarded: the reflection model call is itself an agent session
    whose end re-enters this hook -> CLOSED_LOOP_HOOK_ACTIVE sentinel, line 1.
  - Blast-radius limited: these are MACHINE-GLOBAL hooks; they run in every
    repo. The transcript parse is the gate. No wired skill used -> silent
    exit 0, no model call, no cost.
  - Per-(session,skill) dedupe with bounded retries: correct whether the host
    fires once/session (Claude SessionEnd) or per-turn (Codex Stop).
  - Fail-silent, fail-logged: always exit 0; every decision is logged, and
    that log IS the capture-rate instrumentation the loop design requires.
  - No hardcoded user paths: skills root is discovered under $HOME or set via
    LEARNINGS_SKILLS_ROOT. Portable to any laptop / any username.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SENTINEL = "CLOSED_LOOP_HOOK_ACTIVE"
HOME = Path.home()
STATE_DIR = HOME / ".agents" / "hooks"
LOG_PATH = STATE_DIR / "learnings_capture.log"
SEEN_DIR = STATE_DIR / ".seen"

APPEND_REL = "agents-skills-feedback-loop/scripts/append_learning.py"
VALID_SECTIONS = {"Patterns That Work", "Mistakes to Avoid", "Domain Knowledge"}
MAX_TRANSCRIPT_CHARS = 6000
ENTRY_CAP = 240            # mirror append_learning.py's atomicity cap
MAX_ATTEMPTS = 3           # per (session, skill); bounds Codex per-turn cost
SEEN_TTL_SECONDS = 7 * 86400

# Skills-root discovery: env wins; else common $HOME-relative layouts. Never a
# hardcoded username. A candidate must actually contain append_learning.py.
ROOT_CANDIDATES = (
    "Documents/Code/AI-Agents/frameworks/shared-skills/skills",
    "Documents/AI-Agents/frameworks/shared-skills/skills",
    "AI-Agents/frameworks/shared-skills/skills",
    "projects/AI-Agents/frameworks/shared-skills/skills",
    "code/AI-Agents/frameworks/shared-skills/skills",
    ".agents/skills",
)


def log(msg: str) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        ts = _dt.datetime.now().isoformat(timespec="seconds")
        with LOG_PATH.open("a") as fh:
            fh.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def discover_skills_root() -> Path | None:
    env = os.environ.get("LEARNINGS_SKILLS_ROOT")
    cands = [Path(env)] if env else []
    cands += [HOME / c for c in ROOT_CANDIDATES]
    for d in cands:
        if d.is_dir() and (d / APPEND_REL).is_file():
            return d
    return None


def wired_skill_dir(skills_root: Path, name: str) -> Path | None:
    name = name.split(":", 1)[-1].strip()  # drop any plugin: prefix
    d = skills_root / name
    sm = d / "SKILL.md"
    if not sm.is_file():
        return None
    try:
        if "## Learnings Loop" not in sm.read_text(errors="ignore"):
            return None
    except Exception:
        return None
    if not (d / "learnings.md").exists() and not (
        d / "learnings.consolidated.md"
    ).exists():
        return None
    return d


def skills_used(transcript_path: Path) -> set[str]:
    """Deterministic [Rule 5]: parse JSONL for Skill tool invocations."""
    used: set[str] = set()
    try:
        with transcript_path.open(errors="ignore") as fh:
            for line in fh:
                if '"Skill"' not in line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                msg = obj.get("message", obj)
                content = msg.get("content") if isinstance(msg, dict) else None
                if not isinstance(content, list):
                    continue
                for b in content:
                    if (
                        isinstance(b, dict)
                        and b.get("type") == "tool_use"
                        and b.get("name") == "Skill"
                    ):
                        inp = b.get("input") or {}
                        sk = inp.get("skill") or inp.get("command")
                        if isinstance(sk, str) and sk:
                            used.add(sk)
    except Exception as e:
        log(f"transcript parse failed: {e!r}")
    return used


def transcript_text(transcript_path: Path) -> str:
    parts: list[str] = []
    try:
        with transcript_path.open(errors="ignore") as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                msg = obj.get("message", obj)
                if not isinstance(msg, dict) or msg.get("role") not in (
                    "user", "assistant"
                ):
                    continue
                c = msg.get("content")
                if isinstance(c, str):
                    parts.append(c)
                elif isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "text":
                            parts.append(b.get("text", ""))
    except Exception:
        return ""
    return "\n".join(parts)[-MAX_TRANSCRIPT_CHARS:]


def _seen_path(session_id: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_"
                    for ch in session_id)[:120] or "nosession"
    return SEEN_DIR / f"{safe}.json"


def load_seen(session_id: str) -> dict:
    try:
        return json.loads(_seen_path(session_id).read_text())
    except Exception:
        return {}


def save_seen(session_id: str, data: dict) -> None:
    try:
        SEEN_DIR.mkdir(parents=True, exist_ok=True)
        _seen_path(session_id).write_text(json.dumps(data))
    except Exception:
        pass


def prune_seen() -> None:
    try:
        cutoff = time.time() - SEEN_TTL_SECONDS
        for f in SEEN_DIR.glob("*.json"):
            if f.stat().st_mtime < cutoff:
                f.unlink(missing_ok=True)
    except Exception:
        pass


def reflect(skill: str, convo: str) -> tuple[str, str] | None:
    """The ONE judgment call [Rule 5]. Returns (section, text) or None."""
    prompt = (
        f"You are reviewing one work session that used the '{skill}' skill.\n"
        "If the session revealed ONE durable, reusable learning for that "
        "skill (a pattern that worked, a mistake to avoid, or a surprising "
        "domain fact), output exactly:\n"
        "SECTION|||one atomic sentence (<=240 chars, no date prefix)\n"
        "where SECTION is one of: Patterns That Work | Mistakes to Avoid | "
        "Domain Knowledge\n"
        "If there is no durable learning, output exactly: SKIP\n"
        "Output nothing else.\n\n"
        f"SESSION TRANSCRIPT (trimmed):\n{convo}\n"
    )
    override = os.environ.get("LEARNINGS_REFLECT_CMD")
    env = dict(os.environ)
    env[SENTINEL] = "1"  # recursion guard for the spawned model session
    try:
        if override:
            out = subprocess.run(
                ["bash", "-c", override], input=prompt,
                capture_output=True, text=True, timeout=120, env=env,
            ).stdout
        else:
            _model = os.environ.get("LEARNINGS_REFLECT_MODEL", "claude-haiku-4-5")
            out = subprocess.run(
                ["claude", "-p", prompt,
                 "--model", _model,
                 "--max-budget-usd", "0.05"],
                capture_output=True, text=True, timeout=150, env=env,
            ).stdout
    except FileNotFoundError:
        log("reflect cmd not found -> no-op (capability-agnostic degrade)")
        return None
    except subprocess.TimeoutExpired:
        log(f"reflect timeout for {skill}")
        return None
    except Exception as e:
        log(f"reflect error for {skill}: {e!r}")
        return None

    out = (out or "").strip()
    if not out or out.upper().startswith("SKIP") or "|||" not in out:
        return None
    section, _, text = out.partition("|||")
    section, text = section.strip(), text.strip()
    if section not in VALID_SECTIONS:
        section = "Patterns That Work"
    if not text or len(text) > ENTRY_CAP:
        log(f"reflect output rejected (empty/oversized) for {skill}")
        return None
    return section, text


def main() -> int:
    if os.environ.get(SENTINEL) == "1":
        return 0  # recursion guard: inside our own reflection call

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    skills_root = discover_skills_root()
    if skills_root is None:
        log("skills root not found (set LEARNINGS_SKILLS_ROOT) -> no-op")
        return 0

    tp = payload.get("transcript_path")
    if not tp or not Path(tp).is_file():
        return 0
    transcript_path = Path(tp)
    sid = str(payload.get("session_id", "?"))

    prune_seen()
    wired = {
        s: d
        for s in skills_used(transcript_path)
        if (d := wired_skill_dir(skills_root, s)) is not None
    }
    if not wired:
        log(f"session={sid} wired_skills=0 -> exit (no-op)")
        return 0

    append_py = skills_root / APPEND_REL
    seen = load_seen(sid)  # {skill: {"attempts": int, "done": bool}}
    convo = transcript_text(transcript_path)
    appended = 0

    for skill, skill_dir in wired.items():
        st = seen.get(skill, {"attempts": 0, "done": False})
        if st.get("done") or st.get("attempts", 0) >= MAX_ATTEMPTS:
            continue  # already handled this skill earlier in the session
        st["attempts"] = st.get("attempts", 0) + 1
        seen[skill] = st

        r = reflect(skill, convo)
        if r is None:
            # No learning OR transient failure. Mark done only if we have
            # spent our retry budget; else allow a later Stop to retry.
            if st["attempts"] >= MAX_ATTEMPTS:
                st["done"] = True
            log(f"session={sid} skill={skill} -> SKIP "
                f"(attempt {st['attempts']}/{MAX_ATTEMPTS})")
            continue

        section, text = r
        try:
            res = subprocess.run(
                ["python3", str(append_py), str(skill_dir),
                 "--section", section, "--text", text],
                capture_output=True, text=True, timeout=30,
            )
            if res.returncode == 0:
                appended += 1
                st["done"] = True
                log(f"session={sid} skill={skill} APPENDED "
                    f"[{section}] {text}")
            else:
                st["done"] = True  # don't retry a content-rejected entry
                log(f"session={sid} skill={skill} append rejected: "
                    f"{res.stdout.strip()} {res.stderr.strip()}")
        except Exception as e:
            log(f"session={sid} skill={skill} append error: {e!r}")

    save_seen(sid, seen)
    log(f"session={sid} wired={len(wired)} appended={appended} (capture-rate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
