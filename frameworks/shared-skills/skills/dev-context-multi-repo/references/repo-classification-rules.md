# Repo Classification Rules

`repo_kind` defaults:
- `service` for deployable backend systems with runtime plus service interfaces
- `app` for user-facing web, mobile, or desktop applications
- `library` for shared packages or SDKs
- `infra` for Terraform, Helm, CI/platform repos
- `data` for analytics, ETL, warehouse, or ML pipelines
- `docs` for documentation-only repos
- `mono-root` for workspace roots coordinating many packages
- `unknown` when signals conflict or are insufficient

Native/mobile-specific guidance:
- classify as `app` when Swift is present and high-signal Apple project files such as `project.yml`, `.xcodeproj`, or `.xcworkspace` are present
- prefer project-file evidence over generic dependency heuristics for native repos
- ignore generated build trees such as `.build`, `DerivedData`, `Pods`, `Carthage`, and `SourcePackages` before making repo-shape claims

`status` defaults:
- `legacy` when repo naming, archived markers, or docs say it is superseded
- `archived` when git hosting or docs explicitly mark it archived
- `experimental` for POCs or labs
- `active` only when no legacy/archive signal is present
