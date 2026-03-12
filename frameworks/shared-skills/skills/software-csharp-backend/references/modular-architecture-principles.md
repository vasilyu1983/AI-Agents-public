# Modular Architecture Principles

## Purpose
Use this guide when a backend should keep modular boundaries inside one deployable unit before splitting into independent services.

## When This Fits
- Domain boundaries are still evolving.
- Teams need stronger isolation than a layered monolith but lower operational overhead than microservices.
- You want explicit module contracts, independent module testing, and incremental extraction paths.

## Core Principles
- Organize by business modules, not technical layers alone.
- Keep each module internally layered (presentation/application/domain/infrastructure as needed).
- Treat inter-module interaction as integration: explicit contracts, versioned DTOs/events, no direct internal-type coupling.
- Use one composition/deployment host to wire modules and cross-cutting concerns.
- Keep business logic inside modules; keep host projects focused on transport, composition, and runtime wiring.
- Share only stable abstractions in a small shared kernel; avoid dumping business logic into shared libraries.

## Design Checklist
- Define module ownership: entities, use cases, data stores, and integration contracts.
- Enforce boundaries with project references and architectural tests/review checks.
- Choose sync vs async integration per use case and consistency requirements.
- Keep module APIs explicit and independently testable.
- Plan extraction seams early: contracts, anti-corruption adapters, and idempotent integration flows.

## Concrete Example
One modular-architecture shape is a pricing system where business behavior is split into dedicated modules (for example, administration and calculation) and a separate API host acts as the deployment/composition unit.

## External References
See `../Data/data.json` for curated external links.
