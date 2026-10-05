# Manifest Detection Matrix

| Ecosystem | Primary Files | Useful Secondary Files |
|-----------|---------------|------------------------|
| Node.js | `package.json` | `pnpm-lock.yaml`, `turbo.json`, `nx.json`, `tsconfig.json` |
| Python | `pyproject.toml` | `requirements.txt`, `poetry.lock`, `tox.ini` |
| Go | `go.mod` | `go.sum`, `Makefile` |
| Rust | `Cargo.toml` | `Cargo.lock` |
| Java | `pom.xml` | `build.gradle`, `settings.gradle` |
| .NET / C# | `*.sln`, `*.csproj` | `Directory.Build.props`, `global.json`, `NuGet.Config`, `Packages.props` |
| Kotlin / JVM | `build.gradle.kts` | `settings.gradle.kts`, `gradle.properties` |
| Containers | `Dockerfile` | `docker-compose.yml`, Helm charts |
| Infra | Terraform files | Kubernetes manifests, Helm charts |

Read the smallest set that reveals runtime, dependencies, and build model.

