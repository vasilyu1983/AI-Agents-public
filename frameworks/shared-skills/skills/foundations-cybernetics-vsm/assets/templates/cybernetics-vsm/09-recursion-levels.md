# Primitive 9: Recursion Levels

## Definition

**Recursion** in the VSM means that every viable system is composed of S1 units that are themselves viable systems, and is in turn contained within a larger viable system. The same five-system structure (S1–S5) applies at every level of organisation.

This is the **Fractal Organisation** principle: the management model is self-similar across scales. A squad looks like a VSM. A division looks like a VSM made of squads. A company looks like a VSM made of divisions.

Key implication: **the VSM must always be applied at a specific, explicitly chosen recursion level**. Applying it to the wrong level — treating company-level dynamics as squad-level problems, or vice versa — produces category errors in diagnosis and design.

Beer identified three levels as the minimum viable architecture:
1. The system-in-focus (the level you are designing for).
2. The system of which the system-in-focus is a component.
3. The systems contained within the system-in-focus as S1 units.

## When to Use

- Before applying any other VSM primitive — identify the level of recursion first.
- When designing multi-level organisations (company → division → team → squad).
- When an organisational intervention has failed to produce expected results (often a recursion mismatch).
- When designing nested agent architectures (swarm → orchestrator → executor).

## Inputs

| Input | Description |
|-------|-------------|
| System-in-focus definition | What system are you designing for at this level? |
| Parent system | The viable system that contains the system-in-focus as an S1 unit |
| Child systems | The viable systems that are S1 units within the system-in-focus |
| Recursion depth | How many levels up/down are relevant to the current problem |

## Outputs

| Output | Description |
|--------|-------------|
| Recursion diagram | Visual map of levels with parent, current, and child systems |
| Level assignment | Which VSM roles belong at which recursion level |
| Boundary definitions | Where each level ends and the next begins |
| Interference check | Confirmation that S3/S4 at one level are not doing the work of S3/S4 at another |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Recursion confusion | S5 of a squad treated as equivalent to S5 of the company | Draw the recursion diagram explicitly; separate levels |
| Missing recursion level | Jumping from company to individual without intermediate level | Insert the missing level; design its VSM structure |
| Recursion collapse | Two levels merged into one, eliminating a layer of management | Separate levels; assign distinct S1–S5 roles at each |
| Infinite regression | Recursing too deeply; modelling every sub-team to the individual level | Choose a practical floor; below a certain team size, VSM analysis adds no value |

## Worked Example

**Context**: A 200-person AI company with product, engineering, and data science functions.

**Three recursion levels**:

**Level 1 (system-in-focus: the company)**:
- S5: Founders/board — company identity and non-negotiables.
- S4: Chief Strategy Officer — market, competitive, and technology environment.
- S3: CEO / COO — allocation of capital and headcount across divisions.
- S2: Cross-functional coordination (product × engineering × data science planning process).
- S1 units: Product Division, Engineering Division, Data Science Division.

**Level 2 (system-in-focus: the Engineering Division)**:
- S5: CTO — engineering principles, architectural non-negotiables.
- S4: VP Architecture — technology horizon, tooling decisions.
- S3: Engineering Director — team capacity allocation, engineering performance.
- S2: Sprint planning, on-call scheduling, incident coordination.
- S1 units: Platform Squad, Product Squads (Growth, Retention, Monetisation).

**Level 3 (system-in-focus: the Growth Squad)**:
- S5: Squad charter — squad values, definition of done.
- S4: Product Manager — user research, competitive signals.
- S3: Tech Lead — sprint-level capacity, technical quality.
- S2: Daily standup, ticket assignment protocol.
- S1 units: Individual engineers (or paired sub-teams).

**Recursion check**: the CTO (Level 2 S5) is not the same as the company founders (Level 1 S5). Confusing them produces conflicting policy at the engineering level.

## Sources

- Beer, S. (1972). _Brain of the Firm_. Allen Lane. Discusses recursion across the "Hierarchies of Control" and "Autonomy" sections. *(2026-07 correction: earlier draft cited a standalone "Ch. 9"; the verified table of contents has no chapter titled specifically for recursion — the principle is developed across multiple sections and is treated more systematically in Beer 1979, _Heart of Enterprise_.)*
- Beer, S. (1985). _Diagnosing the System for Organizations_. Wiley. Recursion levels and the "system-in-focus" concept (ch. 2).
- Hoverstadt, P. (2009). _The Fractal Organization_. Wiley. Recursion as the primary design principle; multi-level application (ch. 6–7).
- Espinosa, A., & Walker, J. (2011). _A Complexity Approach to Sustainability_. Imperial College Press. Recursion in socio-ecological systems.
- Espinosa, A. (2025). "Revisiting the Viable System Model as an emancipatory systems approach." _Systems Research and Behavioral Science_, 42(1), 171–188. DOI: 10.1002/sres.3090. Empirically extends recursion-levels application to the community governance domain; VSM at community level surfaces power asymmetries invisible to standard S1–S5 mapping.
- Espinosa, A., & Martinez-Lozada, A. (2025). "The Viable System Model to Support Sustainable Self-Governance in Communities: Learning from Case Studies." _Systemic Practice and Action Research_. DOI: 10.1007/s11213-025-09724-3. Field application (Colombia community); VSM-guided S1–S5 design produced durable, self-funded community projects. Corroborates Espinosa 2025 SRBS.
