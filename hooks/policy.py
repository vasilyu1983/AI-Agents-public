"""Shared policy loader for the hooks and the installer.

Rule: a missing or malformed policy is a visible failure (PolicyError), never a
silent fallback to main/dev or any other built-in value. No defaults live here.

Resolution order: explicit path, env AGENTS_POLICY, ~/.agents/policy.json (if it
exists), then config/policy.json in this repository.
"""

import json
import os
from pathlib import Path

REQUIRED = ("vcs", "roles", "labels", "thresholds")
REPO_FILE = Path(__file__).resolve().parent.parent / "config" / "policy.json"


class PolicyError(RuntimeError):
    pass


def _resolve(path):
    if path:
        return Path(path)
    if os.environ.get("AGENTS_POLICY"):
        return Path(os.environ["AGENTS_POLICY"])
    home = Path(os.path.expanduser("~")) / ".agents" / "policy.json"
    return home if home.exists() else REPO_FILE


def load(path=None):
    p = _resolve(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except OSError as e:
        raise PolicyError("policy unreadable: %s (%s)" % (p, e))
    except ValueError as e:
        raise PolicyError("policy is not valid JSON: %s (%s)" % (p, e))
    if not isinstance(data, dict):
        raise PolicyError("policy must be a JSON object: %s" % p)
    for key in REQUIRED:
        if key not in data:
            raise PolicyError("policy %s is missing required key '%s'" % (p, key))
    vcs = data["vcs"]
    branches = vcs.get("protected_branches") if isinstance(vcs, dict) else None
    if not (isinstance(branches, list) and branches and all(isinstance(b, str) for b in branches)):
        raise PolicyError("policy %s: vcs.protected_branches must be a non-empty list of strings" % p)
    if not isinstance(vcs.get("default_base"), str):
        raise PolicyError("policy %s: vcs.default_base must be a string" % p)
    return data
