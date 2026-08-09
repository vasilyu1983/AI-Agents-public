# Primitive: Future Reality Tree (FRT)

**Source**: Goldratt (1994), *It's Not Luck*; Dettmer 2007, *The Logical Thinking Process* (Future Reality Tree chapter — verify chapter number against your printing before citing it precisely).

## Definition

The Future Reality Tree (FRT) is a TOC Thinking Process tool for designing and validating an intervention. It answers: "If we inject this change, will it actually produce the Desirable Effects (DEs) we want — and will it create any new Undesirable Effects (UDEs)?"

The FRT uses the same sufficiency logic as the CRT ("If…Then") but runs forward from proposed injections to predicted outcomes.

**Key distinction**:
- CRT (primitive 05) diagnoses *what is wrong and why*.
- FRT *designs and tests* a proposed solution before investing in it.
- An "injection" is a new action or policy not currently in place.

**Negative Branch Reservation (NBR)**: when the FRT reveals a new UDE created by the injection, a Negative Branch Reservation is added to capture and trim that branch before implementation.

## When to Use

- After building a CRT and identifying the core problem — before committing to a solution.
- To pressure-test a proposed strategy: "Does this injection actually break the constraint?"
- When a solution has side effects that have not been mapped.
- In product roadmap design: validate that a proposed feature set eliminates the root cause UDEs.

## Inputs

- The identified injection(s) — specific, actionable changes.
- The CRT entities (core problem and intermediate entities) to verify the injection actually severs the causal chain.
- Target Desirable Effects: the positive outcomes the injection should produce.

## Outputs

- An FRT diagram tracing injections → intermediate effects → Desirable Effects.
- A list of Negative Branch Reservations with proposed trimming actions.
- A go/no-go recommendation: does the injection reliably produce DEs without unacceptable new UDEs?

## Failure Modes

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| Injection does not connect to core problem | CRT was incomplete or FRT built without reference to CRT | Verify the injection severs at least one arrow on the CRT |
| FRT built for a preferred solution only | Confirmation bias | Build the FRT before deciding on the solution; let the logic guide the injection |
| Negative branches not explored | Optimism bias | Explicitly ask "what could go wrong?" for each injection; add NBRs |
| FRT too vague to test | Injections stated as goals ("improve communication") | Injections must be specific actions ("weekly cross-team prioritization meeting") |
| DEs stated as vague positives | "Things will be better" is not a DE | State DEs as specific, observable outcomes that mirror the UDEs in the CRT |

## Worked Example

**Context**: CRT identified core problem "no shared prioritization system." Proposed injection: introduce a weekly constraint-aligned prioritization meeting with a defined owner and protocol.

**FRT (simplified)**:

```
Injection: Weekly prioritization meeting with constraint-aware protocol
  ↓
All requests ranked by throughput impact on the constraint
  ↓
Engineers receive one clear priority queue; context-switching declines
  ↓
DE1: Sprint velocity stabilizes
DE2: Production bugs decline (engineers focused; no rushed work)
DE3: Engineer burnout reduces
```

**Negative Branch found**: "Weekly meeting adds 2 hours of overhead per engineer."
**NBR trim**: meeting capped at 30 minutes; async pre-read distributed in advance. Branch trimmed.

**Result**: FRT validates the injection resolves all three UDEs with the trimmed NBR. Proceed to Prerequisite Tree (primitive 07) to plan implementation.

## Sources

- Goldratt, E.M. (1994). *It's Not Luck*. North River Press.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. (Future Reality Tree chapter; confirm exact number against your printing)
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press.
