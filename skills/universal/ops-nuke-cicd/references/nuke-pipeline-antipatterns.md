# NUKE Pipeline Antipatterns

## Purpose
Catch common design mistakes before they become recurring CI incidents.

## Antipatterns and Corrections
- Antipattern: Use `After` where hard prerequisite is required.  
  Correction: Replace with `DependsOn` for mandatory dependencies.
- Antipattern: Trigger all tests in local fast-feedback targets.  
  Correction: Keep local fast path focused; run full matrix in `TestAll`.
- Antipattern: Keep filter expressions duplicated and inconsistent across targets.  
  Correction: Centralize category intent and verify by target.
- Antipattern: Publish mutable image tags to deployment jobs.  
  Correction: Export digest-pinned references and consume those.
- Antipattern: Couple cleanup (`docker rmi`) with critical output generation.  
  Correction: Generate and persist outputs before cleanup.
- Antipattern: Mix restore/build/test logic in one large target.  
  Correction: Split into composable targets with explicit graph edges.
- Antipattern: Rely on local-only behavior to pass failing tests.  
  Correction: Keep CI path as source of truth and re-validate locally with CI-like targets.
- Antipattern: Change artifact names without downstream updates.
  Correction: Treat artifacts as versioned contracts.
- Antipattern: Hard-coded fixed ports in Docker-backed test configurations.
  Correction: Use dynamic host-port reservation and verify tests pass when old fixed ports are intentionally occupied.
- Antipattern: Assume `localhost` as Docker host in CI environments.
  Correction: Resolve from Testcontainers API or `DOCKER_HOST` env var — CI runners may use remote Docker.
- Antipattern: Add test suites without pipeline wiring.
  Correction: Treat integration into the canonical CI entry point as part of feature completion, not follow-up cleanup.

## Pre-Merge Review
- Verify graph edges map to intended execution model.
- Verify category filters include/exclude intended suites.
- Verify coverage merge target runs after all required tests.
- Verify deploy outputs include digest-pinned image references.
- Verify local-vs-CI conditionals are minimal and intentional.
- Verify Docker-backed suites use dynamic ports and resolve Docker host from Testcontainers/`DOCKER_HOST`.
- Verify new test targets are reachable from the CI entry point without introducing circular dependencies.

