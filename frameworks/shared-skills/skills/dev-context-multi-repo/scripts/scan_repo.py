#!/usr/bin/env python3
"""Extract a normalized repo profile from high-signal files."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


MANIFESTS = [
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
    "Package.swift",
    "project.yml",
    "Podfile",
    "Dockerfile",
    "docker-compose.yml",
    "pnpm-workspace.yaml",
    "turbo.json",
    "nx.json",
    "AGENTS.md",
    "CLAUDE.md",
    # .NET
    "Directory.Build.props",
    "nuget.config",
    ".gitlab-ci.yml",
]

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".build",
    ".next",
    ".swiftpm",
    "node_modules",
    "dist",
    "build",
    "vendor",
    ".archive",
    ".venv",
    "venv",
    "__pycache__",
    "coverage",
    ".turbo",
    "DerivedData",
    "Pods",
    "Carthage",
    "SourcePackages",
    "xcuserdata",
    # .NET
    "bin",
    "obj",
    "packages",
    "TestResults",
    ".vs",
}

# NuGet package → framework/capability mapping for .NET repos.
# Example shared-library package prefixes. Replace "Acme.Infrastructure.*" with your own org's NuGet/package namespace.
NUGET_FRAMEWORK_MAP: dict[str, str] = {
    "Microsoft.AspNetCore": "ASP.NET Core",
    "Swashbuckle.AspNetCore": "Swagger/OpenAPI",
    "MediatR": "MediatR",
    "Temporalio": "Temporal",
    "FluentResults": "FluentResults",
    "Refit": "Refit",
    "Quartz": "Quartz.NET",
    "Acme.Infrastructure.MediatR": "MediatR",
    "Acme.Infrastructure.Web": "ASP.NET Core",
    "Acme.Infrastructure.Quartz": "Quartz.NET",
    "Acme.Infrastructure.Refit": "Refit",
    "Acme.Infrastructure.FluentResults": "FluentResults",
    "Acme.Infrastructure.ModuleIntegration": "ModuleIntegration",
    "Acme.Infrastructure.OpenTelemetry": "OpenTelemetry",
    "Acme.Infrastructure.Serilog": "Serilog",
}

NUGET_DATA_STORE_MAP: dict[str, str] = {
    "MongoDB.Driver": "MongoDB",
    "Acme.Infrastructure.Storages.Mongo": "MongoDB",
    "Microsoft.EntityFrameworkCore.SqlServer": "SQL Server",
    "Microsoft.Data.SqlClient": "SQL Server",
    "System.Data.SqlClient": "SQL Server",
    "Acme.Infrastructure.Sql": "SQL Server",
    "Acme.Infrastructure.Ef": "Entity Framework Core",
    "Npgsql": "PostgreSQL",
    "Npgsql.EntityFrameworkCore.PostgreSQL": "PostgreSQL",
    "StackExchange.Redis": "Redis",
    "NEST": "Elasticsearch",
    "Elasticsearch.Net": "Elasticsearch",
    "Acme.Infrastructure.Vault": "HashiCorp Vault",
}

NUGET_MESSAGING_MAP: dict[str, str] = {
    "Confluent.Kafka": "Kafka",
    "Acme.Infrastructure.Kafka": "Kafka",
    "RabbitMQ.Client": "RabbitMQ",
    "EasyNetQ": "RabbitMQ",
    "Acme.Infrastructure.RabbitMq": "RabbitMQ",
    "AWSSDK.SQS": "SQS",
    "Acme.Infrastructure.Aws.Sqs": "SQS",
}

NUGET_INTEGRATION_MAP: dict[str, str] = {
    "AWSSDK.S3": "AWS S3",
    "AWSSDK.KeyManagementService": "AWS KMS",
    "Acme.Infrastructure.Aws.S3": "AWS S3",
    "Acme.Infrastructure.Aws.Kms": "AWS KMS",
    "Acme.Infrastructure.CloudFlare": "CloudFlare",
}


def add_once(items: list, value: str) -> None:
    if value and value not in items:
        items.append(value)


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def iter_repo_files(repo: Path):
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(repo)
        if should_skip(rel_path):
            continue
        yield path


def repo_contains_text(repo: Path, needle: str, suffixes: tuple[str, ...] | list[str] | None = None) -> bool:
    allowed_suffixes = tuple(suffix.lower() for suffix in suffixes) if suffixes else None
    for path in iter_repo_files(repo):
        if allowed_suffixes and path.suffix.lower() not in allowed_suffixes:
            continue
        try:
            if needle in path.read_text(encoding="utf-8", errors="ignore"):
                return True
        except Exception:
            continue
    return False


def detect_xcode_project(repo: Path) -> bool:
    return any(path.suffix == ".xcodeproj" for path in repo.glob("*.xcodeproj"))


def detect_xcode_workspace(repo: Path) -> bool:
    return any(path.suffix == ".xcworkspace" for path in repo.glob("*.xcworkspace"))


def detect_swift_entrypoints(repo: Path) -> list[str]:
    entrypoints: list[str] = []
    for path in iter_repo_files(repo):
        if path.suffix.lower() != ".swift":
            continue
        rel_path = path.relative_to(repo)
        if path.name.endswith("App.swift"):
            add_once(entrypoints, rel_path.as_posix())
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "@main" in content:
            add_once(entrypoints, rel_path.as_posix())
        if len(entrypoints) >= 3:
            break
    return entrypoints[:3]


def detect_languages(repo: Path) -> list[str]:
    languages: list[str] = []
    mapping = {
        "*.py": "Python",
        "*.ts": "TypeScript",
        "*.tsx": "TypeScript",
        "*.js": "JavaScript",
        "*.jsx": "JavaScript",
        "*.go": "Go",
        "*.rs": "Rust",
        "*.java": "Java",
        "*.kt": "Kotlin",
        "*.tf": "Terraform",
        "*.cs": "C#",
        "*.swift": "Swift",
    }
    suffix_mapping = {pattern.lstrip("*"): language for pattern, language in mapping.items()}
    seen_suffixes: set[str] = set()
    for path in iter_repo_files(repo):
        suffix = path.suffix.lower()
        if suffix in seen_suffixes:
            continue
        language = suffix_mapping.get(suffix)
        if language:
            add_once(languages, language)
            seen_suffixes.add(suffix)
    return languages


def load_package_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# .NET / C# support
# ---------------------------------------------------------------------------

def find_csproj_files(repo: Path) -> list[Path]:
    """Find all .csproj files, excluding bin/obj/packages."""
    results = []
    for path in repo.rglob("*.csproj"):
        rel = path.relative_to(repo)
        if not should_skip(rel):
            results.append(path)
    return sorted(results)


def find_sln_files(repo: Path) -> list[Path]:
    return sorted(repo.glob("*.sln"))


def parse_csproj(path: Path) -> dict:
    """Extract key metadata from a .csproj file."""
    result: dict = {
        "path": str(path),
        "name": path.stem,
        "target_framework": None,
        "package_refs": [],
        "project_refs": [],
        "is_test": False,
        "is_packable": False,
        "output_type": None,
    }
    try:
        tree = ET.parse(path)
    except Exception:
        return result

    root = tree.getroot()
    # Handle both namespaced and non-namespaced csproj
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    # TargetFramework(s)
    for tag in ("TargetFramework", "TargetFrameworks"):
        el = root.find(f".//{ns}PropertyGroup/{ns}{tag}")
        if el is not None and el.text:
            result["target_framework"] = el.text.strip()
            break

    # PackageReference
    for ref in root.findall(f".//{ns}PackageReference"):
        name = ref.get("Include") or ref.get("Update") or ""
        version = ref.get("Version") or ""
        if name:
            result["package_refs"].append({"name": name, "version": version})

    # ProjectReference
    for ref in root.findall(f".//{ns}ProjectReference"):
        inc = ref.get("Include") or ""
        if inc:
            result["project_refs"].append(inc)

    # IsPackable / GeneratePackageOnBuild
    for tag in ("IsPackable", "GeneratePackageOnBuild"):
        el = root.find(f".//{ns}PropertyGroup/{ns}{tag}")
        if el is not None and el.text and el.text.strip().lower() == "true":
            result["is_packable"] = True

    # OutputType
    el = root.find(f".//{ns}PropertyGroup/{ns}OutputType")
    if el is not None and el.text:
        result["output_type"] = el.text.strip()

    # Test project heuristic
    name_lower = result["name"].lower()
    if any(t in name_lower for t in ("test", "tests", "spec", "specs")):
        result["is_test"] = True
    for ref in result["package_refs"]:
        pkg = ref["name"].lower()
        if pkg in ("nunit", "xunit", "mstest.testframework", "microsoft.net.test.sdk"):
            result["is_test"] = True
            break

    return result


def has_dockerfiles(repo: Path) -> bool:
    """Check for Dockerfiles in root or docker-files/ subdirectory."""
    if (repo / "Dockerfile").exists():
        return True
    # docker-files/ pattern (common in many .NET repos)
    docker_dir = repo / "docker-files"
    if docker_dir.is_dir():
        if any(docker_dir.glob("*.Dockerfile")) or any(docker_dir.glob("*.dockerfile")):
            return True
    # Also check for docker-compose variants
    for pattern in ("docker-compose*.yml", "docker-compose*.yaml"):
        if list(repo.glob(pattern)):
            return True
    return False


def scan_dotnet(repo: Path) -> dict | None:
    """Extract .NET-specific metadata. Returns None if not a .NET repo."""
    csproj_files = find_csproj_files(repo)
    sln_files = find_sln_files(repo)
    if not csproj_files and not sln_files:
        return None

    parsed = [parse_csproj(p) for p in csproj_files]
    all_packages: dict[str, str] = {}  # name → version
    project_refs: list[str] = []
    target_frameworks: set[str] = set()
    test_projects: list[str] = []
    app_projects: list[str] = []

    for p in parsed:
        for ref in p["package_refs"]:
            all_packages[ref["name"]] = ref["version"]
        project_refs.extend(p["project_refs"])
        if p["target_framework"]:
            for tf in p["target_framework"].split(";"):
                target_frameworks.add(tf.strip())
        if p["is_test"]:
            test_projects.append(p["name"])
        elif not p["is_test"]:
            app_projects.append(p["name"])

    # Detect frameworks from NuGet packages
    frameworks: list[str] = []
    for pkg_name in all_packages:
        for prefix, framework in NUGET_FRAMEWORK_MAP.items():
            if pkg_name == prefix or pkg_name.startswith(prefix + "."):
                add_once(frameworks, framework)

    # Detect data stores
    data_stores: list[str] = []
    for pkg_name in all_packages:
        for prefix, store in NUGET_DATA_STORE_MAP.items():
            if pkg_name == prefix or pkg_name.startswith(prefix + "."):
                add_once(data_stores, store)

    # Detect messaging
    messaging: list[str] = []
    for pkg_name in all_packages:
        for prefix, msg in NUGET_MESSAGING_MAP.items():
            if pkg_name == prefix or pkg_name.startswith(prefix + "."):
                add_once(messaging, msg)

    # Detect integrations
    integrations: list[str] = []
    for pkg_name in all_packages:
        for prefix, integration in NUGET_INTEGRATION_MAP.items():
            if pkg_name == prefix or pkg_name.startswith(prefix + "."):
                add_once(integrations, integration)

    # Detect interfaces (REST from controllers)
    interfaces: list[str] = []
    for csproj_path in csproj_files:
        proj_dir = csproj_path.parent
        for cs_file in proj_dir.rglob("*Controller*.cs"):
            if not should_skip(cs_file.relative_to(repo)):
                add_once(interfaces, "REST")
                break
        if "REST" in interfaces:
            break
    # gRPC from .proto files
    if any(repo.rglob("*.proto")):
        add_once(interfaces, "gRPC")

    # Build tools
    build_tools: list[str] = []
    if (repo / ".nuke").exists() or any(repo.glob("_build/*.cs")):
        build_tools.append("nuke")
    if sln_files:
        build_tools.append("dotnet/msbuild")

    # Package managers
    package_managers: list[str] = ["nuget"]

    # Top NuGet dependencies (non-test, significant)
    skip_prefixes = ("Microsoft.NET", "System.", "NETStandard")
    deps_direct = sorted(
        {name for name in all_packages if not any(name.startswith(p) for p in skip_prefixes)}
    )[:100]

    # Entrypoints (projects with Exe output or *Api/*.Host in name)
    entrypoints: list[str] = []
    for p in parsed:
        if p["output_type"] and p["output_type"].lower() == "exe":
            rel = Path(p["path"]).relative_to(repo).as_posix()
            add_once(entrypoints, rel)
        elif any(kw in p["name"].lower() for kw in ("api", "host", "worker", "orchestrat")):
            if not p["is_test"]:
                rel = Path(p["path"]).relative_to(repo).as_posix()
                add_once(entrypoints, rel)

    # Architecture style inference
    arch = "unknown"
    if "ModuleIntegration" in frameworks:
        arch = "modular-monolith"
    elif "Temporal" in frameworks:
        arch = "event-driven"
    elif messaging:
        arch = "event-driven"
    elif len(entrypoints) == 1 and "MediatR" in frameworks:
        arch = "microservice"

    return {
        "frameworks": frameworks,
        "data_stores": data_stores,
        "messaging": messaging,
        "integrations": integrations,
        "interfaces": interfaces,
        "build_tools": build_tools,
        "package_managers": package_managers,
        "deps_direct": deps_direct,
        "entrypoints": entrypoints,
        "target_frameworks": sorted(target_frameworks),
        "test_projects": test_projects,
        "app_projects": app_projects,
        "all_packages": all_packages,
        "csproj_count": len(csproj_files),
        "sln_files": [s.name for s in sln_files],
        "architecture_style": arch,
    }


# ---------------------------------------------------------------------------
# Evidence and interface detection
# ---------------------------------------------------------------------------

def gather_evidence(repo: Path, dotnet: dict | None = None) -> list[dict]:
    evidence = []
    for rel in MANIFESTS:
        path = repo / rel
        if path.exists():
            evidence.append({"path": rel, "reason": "high-signal manifest"})
    for path in sorted(repo.glob("*.xcodeproj"))[:1]:
        evidence.append({"path": path.name, "reason": "xcode project"})
    for path in sorted(repo.glob("*.xcworkspace"))[:1]:
        evidence.append({"path": path.name, "reason": "xcode workspace"})
    for readme in sorted(repo.glob("README*"))[:1]:
        evidence.append({"path": readme.name, "reason": "repo overview"})
    # .NET evidence
    if dotnet:
        for sln in dotnet.get("sln_files", []):
            evidence.append({"path": sln, "reason": "dotnet solution"})
        if (repo / ".nuke").exists():
            evidence.append({"path": ".nuke", "reason": "nuke build system"})
        # Sample up to 3 csproj files as evidence
        csproj_files = find_csproj_files(repo)
        for p in csproj_files[:3]:
            evidence.append({"path": str(p.relative_to(repo)), "reason": "dotnet project"})
    return evidence


def detect_interfaces(repo: Path, dependencies: list[str]) -> list[str]:
    interfaces: list[str] = []
    openapi_patterns = ("openapi*.yml", "openapi*.yaml", "openapi*.json", "swagger*.yml", "swagger*.yaml", "swagger*.json")
    graphql_patterns = ("*.graphql", "*.gql", "schema.graphql", "schema.gql")

    if any(next(repo.rglob(pattern), None) is not None for pattern in openapi_patterns):
        interfaces.append("REST")
    if any(next(repo.rglob(pattern), None) is not None for pattern in graphql_patterns) or "graphql" in dependencies:
        interfaces.append("GraphQL")
    return interfaces


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------

def scan_repo(repo: Path) -> dict:
    repo_name = repo.name
    languages = detect_languages(repo)
    package_json = load_package_json(repo / "package.json") if (repo / "package.json").exists() else {}
    npm_dependencies = sorted(
        set((package_json.get("dependencies") or {}).keys()) |
        set((package_json.get("devDependencies") or {}).keys())
    )

    # .NET scan
    has_csharp = "C#" in languages
    dotnet = scan_dotnet(repo) if has_csharp else None

    frameworks: list[str] = []
    has_swift = "Swift" in languages
    has_xcode_project = detect_xcode_project(repo)
    has_xcode_workspace = detect_xcode_workspace(repo)
    has_xcodegen = (repo / "project.yml").exists()

    # JS/TS frameworks
    if "next" in npm_dependencies:
        add_once(frameworks, "Next.js")
    if "react" in npm_dependencies:
        add_once(frameworks, "React")
    if "express" in npm_dependencies:
        add_once(frameworks, "Express")
    if (repo / "pyproject.toml").exists():
        add_once(frameworks, "Python project")
    if (repo / "go.mod").exists():
        add_once(frameworks, "Go module")

    # Swift frameworks
    if has_swift:
        add_once(frameworks, "Swift")
    if repo_contains_text(repo, "import SwiftUI", suffixes=(".swift",)):
        add_once(frameworks, "SwiftUI")
    if repo_contains_text(repo, "import XCTest", suffixes=(".swift",)):
        add_once(frameworks, "XCTest")
    if (repo / "Package.swift").exists():
        add_once(frameworks, "Swift Package Manager")
    if has_xcodegen:
        add_once(frameworks, "XcodeGen")
    if has_xcode_project:
        add_once(frameworks, "Xcode project")
    if has_xcode_workspace:
        add_once(frameworks, "Xcode workspace")
    if (repo / "Podfile").exists():
        add_once(frameworks, "CocoaPods")

    # .NET frameworks
    if dotnet:
        for f in dotnet["frameworks"]:
            add_once(frameworks, f)

    # repo_kind
    repo_kind = "unknown"
    if has_dockerfiles(repo):
        repo_kind = "service"
    elif dotnet and dotnet["entrypoints"]:
        repo_kind = "service"
    if any((repo / name).exists() for name in ("pnpm-workspace.yaml", "nx.json", "turbo.json")):
        repo_kind = "mono-root"
    if has_swift and (has_xcode_project or has_xcode_workspace or has_xcodegen) and repo_kind == "unknown":
        repo_kind = "app"
    if dotnet and not dotnet["entrypoints"] and dotnet.get("all_packages") and repo_kind == "unknown":
        repo_kind = "library"
    if npm_dependencies and repo_kind == "unknown":
        repo_kind = "library"
    if (repo / "docs").is_dir() and repo_kind == "unknown" and not languages:
        repo_kind = "docs"

    # Interfaces
    interfaces = detect_interfaces(repo, npm_dependencies)
    if dotnet:
        for iface in dotnet["interfaces"]:
            add_once(interfaces, iface)

    # CI / delivery signals
    delivery_signals: list[str] = []
    if (repo / ".github" / "workflows").exists():
        delivery_signals.append("github-actions")
    if (repo / ".gitlab-ci.yml").exists():
        delivery_signals.append("gitlab-ci")

    # Risk flags
    risks: list[str] = []
    if not list(repo.glob("README*")):
        risks.append("missing-readme")
    if not delivery_signals:
        risks.append("missing-ci-signals")
    if not (repo / "AGENTS.md").exists() and not (repo / "CLAUDE.md").exists():
        risks.append("missing-agent-instructions")

    # Package managers
    package_managers: list[str] = []
    if (repo / "package.json").exists():
        package_managers.append("npm")
    if (repo / "Package.swift").exists():
        package_managers.append("swiftpm")
    if (repo / "Podfile").exists():
        package_managers.append("cocoapods")
    if dotnet:
        for pm in dotnet["package_managers"]:
            add_once(package_managers, pm)

    # Build tools
    build_tools: list[str] = [name for name in ("turbo", "nx") if (repo / f"{name}.json").exists()]
    if has_xcodegen:
        build_tools.append("xcodegen")
    if has_xcode_project or has_xcode_workspace:
        build_tools.append("xcodebuild")
    if dotnet:
        for bt in dotnet["build_tools"]:
            add_once(build_tools, bt)

    # Runtime targets
    runtime_targets: list[str] = []
    if repo_kind == "service":
        runtime_targets.append("api")
    if dotnet and dotnet.get("target_frameworks"):
        for tf in dotnet["target_frameworks"]:
            add_once(runtime_targets, tf)
    if repo_kind == "app" and has_swift:
        runtime_targets = ["iOS", "iPhone Simulator"]

    # Dependencies
    dependencies: list[str] = sorted(npm_dependencies)
    if dotnet:
        dependencies = sorted(set(dependencies) | set(dotnet["deps_direct"]))
    dependencies = dependencies[:100]

    # Data stores
    data_stores: list[str] = dotnet["data_stores"] if dotnet else []

    # Dependencies infra (messaging + integrations)
    dependencies_infra: list[str] = []
    if dotnet:
        for msg in dotnet["messaging"]:
            add_once(dependencies_infra, msg)
        for integ in dotnet["integrations"]:
            add_once(dependencies_infra, integ)

    # Integrates with
    integrates_with: list[str] = []
    if dotnet:
        for integ in dotnet["integrations"]:
            add_once(integrates_with, integ)
        for msg in dotnet["messaging"]:
            add_once(integrates_with, msg)

    # Entrypoints
    entrypoints: list[str] = [str(p.relative_to(repo)) for p in list(repo.glob("src/main.*"))[:3]]
    if dotnet and dotnet["entrypoints"]:
        entrypoints = dotnet["entrypoints"]
    if repo_kind == "app" and has_swift:
        entrypoints = detect_swift_entrypoints(repo) or entrypoints

    # Test signals
    test_signals: list[str] = []
    if any(repo.rglob("*.test.*")):
        test_signals.append("tests-present")
    if dotnet and dotnet["test_projects"]:
        test_signals.append("nunit/xunit-present")
        test_signals.append(f"{len(dotnet['test_projects'])}-test-projects")

    # Architecture style
    architecture_style = "workspace" if repo_kind == "mono-root" else "unknown"
    if dotnet and dotnet["architecture_style"] != "unknown":
        architecture_style = dotnet["architecture_style"]

    # Confidence score
    confidence = 0.35
    if dotnet:
        confidence = 0.7
        if dotnet["data_stores"] or dotnet["messaging"]:
            confidence = 0.8
        if dotnet["entrypoints"] and dotnet["data_stores"] and dotnet["messaging"]:
            confidence = 0.9
    elif frameworks or dependencies:
        confidence = 0.55

    # Summary
    parts = [f"{repo_name} is a {repo_kind} repo"]
    if languages:
        parts.append(f"using {', '.join(languages)}")
    if dotnet and dotnet.get("target_frameworks"):
        parts.append(f"targeting {', '.join(dotnet['target_frameworks'])}")
    if data_stores:
        parts.append(f"with {', '.join(data_stores)}")
    if dependencies_infra:
        parts.append(f"and {', '.join(dependencies_infra)}")
    summary = " ".join(parts) + "."

    return {
        "repo_id": repo_name.lower().replace(" ", "-"),
        "repo_name": repo_name,
        "repo_path": str(repo),
        "repo_group": repo.parent.name,
        "status": "active",
        "visibility": "unknown",
        "default_branch": "unknown",
        "languages": languages,
        "frameworks": frameworks,
        "package_managers": package_managers,
        "build_tools": build_tools,
        "runtime_targets": runtime_targets,
        "repo_kind": repo_kind,
        "entrypoints": entrypoints,
        "dependencies_direct": dependencies,
        "dependencies_infra": dependencies_infra,
        "interfaces_exposed": interfaces,
        "data_stores": data_stores,
        "architecture_style": architecture_style,
        "domain_tags": [],
        "integrates_with": integrates_with,
        "owner_signals": ["CODEOWNERS"] if (repo / "CODEOWNERS").exists() else [],
        "test_signals": test_signals,
        "delivery_signals": delivery_signals,
        "risk_flags": risks,
        "summary": summary,
        "evidence": gather_evidence(repo, dotnet),
        "confidence_score": confidence,
        "last_scanned_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="Path to the repo root")
    args = parser.parse_args()
    repo = Path(args.repo).expanduser().resolve()
    print(json.dumps(scan_repo(repo), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
