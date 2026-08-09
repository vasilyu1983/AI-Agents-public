# Primitive: Current Reality Tree (CRT)

**Source**: Goldratt (1994), *It's Not Luck*; Dettmer 2007, *The Logical Thinking Process* (Current Reality Tree chapter, consistent with the published table of contents — verify chapter number against your printing before citing it precisely).

## Definition

The Current Reality Tree (CRT) is a cause-and-effect diagram that traces a set of Undesirable Effects (UDEs) back to a small number of root causes — typically one or two Core Problems. It uses "If…Then" (sufficiency) logic to connect entities.

**Key concept**: most organizations experience 5–10 UDEs that feel unrelated but share one root cause. The CRT makes that root cause visible.

**Logic rules**:
- **Sufficiency**: "If [cause], then [effect]" — cause is sufficient on its own to produce the effect.
- **Necessity** (not used in CRT): "In order to…, we must…" — reserved for Prerequisite Trees (primitive 07).
- An entity at the bottom of the tree with no incoming arrows is a root cause candidate.
- Ellipse notation: when two causes must both be present to produce an effect, they are connected with an ellipse (logical AND).

## When to Use

- You observe multiple recurring problems and want to find the shared root cause.
- An organization has been "fixing" symptoms for years without lasting improvement.
- Before designing a solution (Future Reality Tree, primitive 06) — always diagnose first.
- Strategic planning: map current pain points before committing to a direction.

## Inputs

- A list of 5–10 Undesirable Effects (UDEs): observable, concrete negative outcomes.
- Willingness to ask "what causes this?" repeatedly until you cannot go further.

## Outputs

- A tree diagram where UDEs are at the top and root causes are at the bottom.
- One or two Core Problems identified at the root.
- A list of intermediate entities that propagate the core problem upward.

## Failure Modes

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| CRT stops at proximate cause | Team stops asking "why" too early | Keep tracing until the entity has no incoming arrows |
| CRT too large (> 30 entities) | Every entity treated as equally important | Scope to 5–10 UDEs; use separate CRTs for separate domains |
| Circular logic in the tree | Effect listed as its own cause | Audit for cycles; break them by introducing a time dimension |
| Jumping to solutions during CRT construction | Confirmation bias directs the tree toward a preferred fix | Separate CRT (diagnosis) from FRT (solution) rigorously |
| UDEs stated as solutions already | "We don't have X" is not a UDE | State UDEs as observable negative effects, not absences of solutions |

## Worked Example

**Context**: A startup reports three UDEs: (1) sprint velocity is declining, (2) production bugs are increasing, (3) engineers are burning out.

**CRT construction** (simplified):

```
UDE1: Sprint velocity declining
UDE2: Production bugs increasing
UDE3: Engineers burning out
        ↑
Entity: Engineers context-switching constantly
        ↑
Entity: No clear prioritization — every request is "urgent"
        ↑
Core Problem: Product and engineering have no shared prioritization system
```

The three UDEs all trace to the same core problem. Fixing velocity alone (hiring) or bugs alone (QA) would not address burnout; only a shared prioritization system dissolves all three.

**Next step**: use the Evaporating Cloud (primitive 04) to resolve any conflict in introducing the prioritization system, then design the solution in a Future Reality Tree (primitive 06).

## Sources

- Goldratt, E.M. (1994). *It's Not Luck*. North River Press.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. (Current Reality Tree chapter; confirm exact number against your printing)
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press.
- Scheinkopf, L.J. (1999). *Thinking for a Change: Putting the TOC Thinking Processes to Work*. CRC Press.
