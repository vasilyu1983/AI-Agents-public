#!/usr/bin/env python3
"""Build the standard artifact set under one artifact root."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def artifact_paths(artifact_root: Path) -> dict[str, Path]:
    return {
        "artifact_root": artifact_root,
        "profiles_dir": artifact_root / "profiles",
        "catalog_dir": artifact_root / "catalog",
        "graphs_dir": artifact_root / "graphs",
        "reports_dir": artifact_root / "reports",
        "graph_path": artifact_root / "graphs" / "knowledge-graph.json",
        "validation_path": artifact_root / "reports" / "graph-validation.json",
        "drift_path": artifact_root / "reports" / "drift.json",
    }


def run_script(script_name: str, *args: str, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT_DIR / script_name), *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and not allow_failure:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the standard multi-repo artifact set beneath one artifact root. "
            "Outputs are written to profiles/, catalog/, graphs/, and reports/."
        )
    )
    parser.add_argument(
        "--artifact-root",
        default=".",
        help="Root directory for generated artifacts (default: current directory).",
    )
    parser.add_argument(
        "--profiles-dir",
        help="Use an existing profiles directory instead of scanning repo roots.",
    )
    parser.add_argument(
        "--hub",
        help="Use an existing hub directory to build graph and report outputs only.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip graph validation report generation.",
    )
    parser.add_argument(
        "--skip-graph-report",
        action="store_true",
        help="Skip static HTML/Markdown graph report generation.",
    )
    parser.add_argument(
        "--skip-drift",
        action="store_true",
        help="Skip drift report generation.",
    )
    parser.add_argument(
        "roots",
        nargs="*",
        help="Root directories to scan when profiles are not supplied directly.",
    )
    args = parser.parse_args()

    selected_sources = sum(bool(value) for value in (args.roots, args.profiles_dir, args.hub))
    if selected_sources != 1:
        parser.error("Provide exactly one source: repo roots, --profiles-dir, or --hub.")

    paths = artifact_paths(Path(args.artifact_root).expanduser().resolve())
    for key in ("profiles_dir", "catalog_dir", "graphs_dir", "reports_dir"):
        paths[key].mkdir(parents=True, exist_ok=True)

    summary: dict[str, object] = {
        "artifact_root": str(paths["artifact_root"]),
        "profiles_dir": str(paths["profiles_dir"]),
        "catalog_dir": str(paths["catalog_dir"]),
        "graph_path": str(paths["graph_path"]),
        "reports_dir": str(paths["reports_dir"]),
        "validation": "skipped" if args.skip_validation else "not-run",
        "graph_report": "skipped" if args.skip_graph_report else "not-run",
        "drift": "skipped" if args.skip_drift else "not-run",
    }

    if args.roots:
        run_script(
            "scan_portfolio.py",
            *args.roots,
            "--artifact-root",
            str(paths["artifact_root"]),
        )
        profiles_dir = paths["profiles_dir"]
        summary["source"] = {"mode": "roots", "roots": list(args.roots)}
    elif args.profiles_dir:
        profiles_dir = Path(args.profiles_dir).expanduser().resolve()
        summary["source"] = {"mode": "profiles", "profiles_dir": str(profiles_dir)}
    else:
        profiles_dir = None
        hub_dir = Path(args.hub).expanduser().resolve()
        summary["source"] = {"mode": "hub", "hub_dir": str(hub_dir)}

    if profiles_dir is not None:
        run_script(
            "build_hub_views.py",
            str(profiles_dir),
            "--out",
            str(paths["catalog_dir"]),
        )
        run_script(
            "build_knowledge_graph.py",
            "--profiles",
            str(profiles_dir),
            "--output",
            str(paths["graph_path"]),
        )
        if not args.skip_drift:
            run_script(
                "report_drift.py",
                str(profiles_dir),
                "--output",
                str(paths["drift_path"]),
            )
            summary["drift"] = str(paths["drift_path"])
    else:
        run_script(
            "build_knowledge_graph.py",
            "--hub",
            str(hub_dir),
            "--output",
            str(paths["graph_path"]),
        )

    if not args.skip_validation:
        validation_result = run_script(
            "validate_graph.py",
            str(paths["graph_path"]),
            "--output",
            str(paths["validation_path"]),
            allow_failure=True,
        )
        summary["validation"] = (
            str(paths["validation_path"])
            if validation_result.returncode == 0
            else f"{paths['validation_path']} (issues found)"
        )

    if not args.skip_graph_report:
        graph_report_result = run_script(
            "export_graph_report.py",
            str(paths["graph_path"]),
            "--output-dir",
            str(paths["reports_dir"]),
            allow_failure=False,
        )
        graph_report_payload = json.loads(graph_report_result.stdout or "{}")
        summary["graph_report"] = {
            "html": graph_report_payload.get("html"),
            "markdown": graph_report_payload.get("markdown"),
        }

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
