"""Check the shipped Vale template against its upstream configuration contract.

Sources: docs.vale.sh/keys/packages, docs.vale.sh/keys/vocabularies,
and github.com/vale-cli/vale-action/blob/v2/action.yml.
Run: python3 -m pytest skills/docs-codebase/scripts/test_docs_quality.py
"""

from configparser import ConfigParser
from pathlib import Path
import shlex

import yaml


ROOT = Path(__file__).resolve().parents[1]


def config():
    parser = ConfigParser(interpolation=None)
    parser.read_string("[global]\n" + (ROOT / "assets/ci/.vale.ini").read_text())
    return parser


def vale_step():
    workflow = yaml.safe_load((ROOT / "assets/ci/docs-quality.yml").read_text())
    return next(step for step in workflow["jobs"]["vale"]["steps"] if "with" in step)


def test_styles_have_global_package_declarations():
    parser = config()
    packages = {item.strip() for item in parser["global"].get("Packages", "").split(",")}
    for section in parser.sections()[1:]:
        for style in parser[section].get("BasedOnStyles", "").split(","):
            style = style.strip()
            if style and style != "Vale":
                assert style in packages, f"{style} cannot be installed by vale sync"


def test_enabled_vocabularies_exist():
    parser = config()
    style_path = ROOT / parser["global"]["StylesPath"]
    for name in parser["global"].get("Vocab", "").split(","):
        if name.strip():
            for filename in ("accept.txt", "reject.txt"):
                path = style_path / "config/vocabularies" / name.strip() / filename
                assert path.is_file(), f"enabled vocabulary is missing {path}"


def test_action_uses_published_owner():
    step = vale_step()
    assert step["uses"].split("@")[0] == "vale-cli/vale-action"


def test_action_accepts_configuration_inputs():
    inputs = vale_step()["with"]
    # The action ignores undeclared inputs; config is not a supported input.
    supported = {
        "version", "files", "debug", "reporter", "fail_on_error", "level",
        "filter_mode", "vale_flags", "separator", "reviewdog_url", "token",
    }
    assert set(inputs) <= supported
    flags = shlex.split(inputs.get("vale_flags", ""))
    assert "--config=.vale.ini" in flags


def test_action_blocks_only_errors():
    flags = shlex.split(vale_step()["with"].get("vale_flags", ""))
    assert "--minAlertLevel=error" in flags


def test_action_checks_errors_outside_added_lines():
    inputs = vale_step()["with"]
    assert inputs.get("filter_mode") == "nofilter"
    assert inputs.get("fail_on_error") is True
