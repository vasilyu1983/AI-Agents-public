# AI Planning And Search Formal Theory Map

## Contents

- [State-Space Search](#state-space-search)
- [Heuristic Guarantees](#heuristic-guarantees)
- [Constraint Satisfaction](#constraint-satisfaction)
- [Game-Tree Search](#game-tree-search)
- [Automated Planning](#automated-planning)
- [Uncertainty Boundary](#uncertainty-boundary)

## State-Space Search

State-space search studies graph traversal over states connected by actions. Completeness and optimality depend on finite branching, depth bounds, repeated-state handling, and path-cost assumptions.

## Heuristic Guarantees

A heuristic is admissible when it never overestimates remaining cost. It is consistent when each heuristic estimate obeys the triangle inequality relative to step costs. These properties determine when A* can guarantee optimal paths.

## Constraint Satisfaction

CSPs separate variables, domains, and constraints. Propagation reduces domains; search assigns variables. Ordering heuristics such as minimum remaining values and least-constraining value reduce branching without changing the solution set.

## Game-Tree Search

Minimax assumes alternating moves and known utilities. Alpha-beta pruning preserves minimax value while reducing explored nodes. MCTS estimates action value through simulated rollouts and tree policy selection.

## Automated Planning

Classical planning assumes symbolic states and action schemas with preconditions and effects. Plan validity is replayable: each action's preconditions must hold before execution and its effects must update the next state.

## Uncertainty Boundary

Partial observability turns state into belief state; nondeterminism turns a single action sequence into a policy or contingency tree. If probability and utility dominate, use `foundations-decision-theory`; if feedback stability dominates, use `foundations-control-theory`.
