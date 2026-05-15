# Architecture Inference Rules

Prefer explicit evidence over naming heuristics.

Strong signals:
- API specs imply external or internal service contracts.
- workspace manifests imply multi-package architecture.
- `services/`, `apps/`, `packages/`, `libs/` plus workspace config imply monorepo or package workspace.
- queue, topic, or consumer config implies event-driven components.
- migration folders plus HTTP framework usually imply a stateful service.

Weak signals:
- folder names alone
- generic `src/` structure
- one-off integration mentions in comments

If only weak signals exist, keep `architecture_style` as `unknown` or `mixed`.

