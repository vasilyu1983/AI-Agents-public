# Primitive: Evaporating Cloud (EC)

**Source**: Goldratt (1994), *It's Not Luck*; Dettmer 2007, *The Logical Thinking Process* (Evaporating Cloud / Conflict Resolution Diagram chapter — verify exact chapter number against the edition in hand before citing it as a page/chapter reference; secondary sources place it near chapter 5, not a fixed number across editions).

## Definition

The Evaporating Cloud (also called the Conflict Resolution Diagram or CRD) is a TOC Thinking Process tool for resolving conflicts that appear to require a compromise between two opposing actions. The cloud "evaporates" when the hidden assumption underlying the conflict is surfaced and challenged.

**Structure** (five nodes):

```
Objective (A)
├── Requirement 1 (B) → Prerequisite 1 (D)
└── Requirement 2 (C) → Prerequisite 2 (D′)

Conflict: D and D′ cannot both be satisfied simultaneously.
```

- **A**: the shared goal both sides are trying to achieve.
- **B** and **C**: the two requirements each side believes are necessary to achieve A.
- **D** and **D′**: the specific actions each requirement demands — which are in conflict.

**Resolution process**: articulate every assumption that connects each arrow (A→B, A→C, B→D, C→D′, and D↔D′). Challenge each assumption. An invalid assumption dissolves the conflict without compromise.

## When to Use

- A team is deadlocked between two approaches that both seem logical.
- A recurring conflict between departments (speed vs. quality, cost vs. capability).
- A strategic tension that keeps surfacing despite repeated negotiations.
- Before using an Evaporating Cloud with a Future Reality Tree (primitive 06) to design an injection.

## Inputs

- A clearly stated conflict: two actions that cannot both be done.
- Willingness to articulate *why* each side believes their action is necessary (the assumptions).

## Outputs

- A cloud diagram with all five nodes labeled.
- A list of assumptions for each arrow.
- At least one identified invalid or challengeable assumption (the "injection point").
- A proposed injection: an action that satisfies both requirements by removing the flawed assumption.

## Failure Modes

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| Cloud built around symptoms, not the real conflict | Conflict stated as a surface dispute | Keep asking "why" until you reach the requirement level |
| Assumptions listed but not challenged | Assumptions treated as facts | Explicitly label each assumption as "valid," "partially valid," or "challengeable" |
| Injection proposed without testing reality | New assumption introduced without checking feasibility | Validate injection in a Future Reality Tree (primitive 06) |
| Two clouds built instead of one | Each side builds their own cloud | Build one cloud that contains both sides' logic |
| Cloud used to win an argument | Combative framing poisons the process | Frame as "dissolving" the conflict, not winning it |

## Worked Example

**Context**: Engineering wants to delay a release to fix a critical edge-case bug. Product wants to ship on schedule to preserve a committed customer launch.

```
A: Deliver a successful product launch
├── B: Protect customer trust → D: Fix the edge-case bug before ship
└── C: Honor the schedule commitment → D′: Ship on the committed date

Conflict: D (fix bug, delay ship) ↔ D′ (ship on date, skip fix)
```

**Assumption audit for B→D**: "Customers will encounter this bug and it will damage trust."
**Challenge**: Is the bug on the critical path for the launch customer's workflow? If not, this assumption is invalid — the bug can be fixed post-launch for users who trigger it.

**Injection**: Ship on schedule with the bug flagged in the known-issues doc; deploy a hotfix within 48 hours of any customer hitting the edge case. The conflict evaporates: both requirements (trust, schedule) are met without compromise.

## Sources

- Goldratt, E.M. (1994). *It's Not Luck*. North River Press.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. (Evaporating Cloud chapter; confirm exact number against your printing — do not cite a chapter number from memory)
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press.
