#!/usr/bin/env python3
"""Smoke test for structured_logs.py."""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import textwrap


def write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def main() -> int:
    script = pathlib.Path(__file__).with_name("structured_logs.py")
    with tempfile.TemporaryDirectory() as td:
        repo = pathlib.Path(td)
        write(
            repo / "src/Feature.cs",
            """
            using Microsoft.Extensions.Logging;
            using System.Collections.Generic;

            public class CreateOrderHandler : ICommandHandler<CreateOrder>
            {
                private readonly ILogger _logger;
                public void Handle(CreateOrder command)
                {
                    _logger.LogInformation("User " + command.UserId + " created order " + command.Id);
                    _logger.LogInformation($"Correlation: {command.CorrelationId}");
                    _logger.LogError(ex, "Failed for " + command.Id);
                }
            }
            """,
        )
        write(
            repo / "src/App.csproj",
            """
            <Project Sdk="Microsoft.NET.Sdk">
              <ItemGroup>
                <PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
              </ItemGroup>
            </Project>
            """,
        )
        write(
            repo / "appsettings.json",
            """
            {
              "Serilog": {
                "WriteTo": [
                  { "Name": "File", "Args": { "path": "logs/log.txt" } },
                  { "Name": "Console" }
                ]
              }
            }
            """,
        )

        proc = subprocess.run(
            ["python", str(script), "--path", str(repo), "--dry-run"],
            check=False,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            raise SystemExit(proc.stderr or proc.stdout)

        patch = (repo / "patch.diff").read_text(encoding="utf-8")
        report = json.loads((repo / "preview-report.json").read_text(encoding="utf-8"))

        assert "LogInformation(\"User {UserId} created order {Id}\"" in patch
        assert "formatter" in patch
        assert report, "preview report should not be empty"

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

