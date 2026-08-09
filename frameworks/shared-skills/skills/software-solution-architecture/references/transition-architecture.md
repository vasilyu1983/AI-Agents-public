# Transition Architecture

Use this reference when the target state cannot be reached in one cutover.

## States To Define

- **Current state**: what exists today, including pain and hard dependencies
- **Interim state**: safe temporary architecture that supports migration progress
- **Target state**: architecture that should remain after legacy removal

## Minimum State Model

Write one short paragraph for each state:

- what systems are active
- where writes go
- where reads go
- which compatibility layer exists
- what would make the state safe to exit

## Migration Patterns

- Strangler facade in front of legacy capability
- Anti-corruption layer between new and legacy models
- Parallel run with reconciliation where financial or regulated correctness matters
- Expand/contract for schema and contract changes
- Channel cutover first or provider cutover first, depending on blast radius

## Wave Controls

Every migration wave should name:

- cutover unit
- validation evidence
- rollback trigger
- rollback mechanism
- retirement or decommission condition

## Required Controls

- rollback point per migration wave
- ownership of each coexistence boundary
- observability for old and new paths
- explicit criteria for decommissioning the interim layer

## Anti-Patterns

- Calling the target state "phased" when there is no defined interim state
- Leaving temporary compatibility layers without retirement criteria
- Mixing migration sequencing with runtime design depth; hand runtime decisions to software architecture once the transition shape is clear
