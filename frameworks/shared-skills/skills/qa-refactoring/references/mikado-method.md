# Mikado Method

A disciplined technique for making large, entangled changes safely: attempt the goal, let the compiler and tests surface what breaks, record each prerequisite as a node in a dependency graph, revert, then work leaf-first until the goal is reachable without breaking anything.

Named after the Japanese game Mikado (pick-up sticks), where you must remove individual sticks without disturbing the pile.

## Contents

- [Core Concept](#core-concept)
- [When to Use](#when-to-use)
- [The Five-Step Loop](#the-five-step-loop)
- [Building the Prerequisite Tree](#building-the-prerequisite-tree)
- [Leaf-First Execution](#leaf-first-execution)
- [Worked Example](#worked-example)
- [Common Pitfalls](#common-pitfalls)
- [Related Patterns](#related-patterns)

---

## Core Concept

A Mikado graph is a directed acyclic graph (DAG) where:

- The **root node** is the goal change (e.g., "Replace HashMap with ConcurrentHashMap in OrderService").
- Each **child node** is a prerequisite discovered by attempting the parent.
- **Leaf nodes** are changes with no further prerequisites — safe to merge immediately.

The graph makes hidden coupling visible before any code is committed. Progress is always releasable: every merged leaf is a valid, green state of the codebase.

---

## When to Use

Use the Mikado method when:

- The target change cascades into 5+ files or modules.
- There are no existing tests covering the area (so "just refactor" is unsafe).
- Previous attempts at the change caused a "while I'm here" sprawl that never shipped.
- The team cannot afford a long-lived feature branch; incremental progress must stay on `main`.

Do **not** use when:

- The change is contained to a single module with adequate test coverage. A direct refactor with a safety net is faster.
- The goal itself is unclear. Clarify the design before mapping prerequisites.

---

## The Five-Step Loop

```text
1. SET GOAL      — Write the goal as a single node at the root of the graph.
2. ATTEMPT       — Make the smallest code change that moves toward the goal.
3. RECORD        — When a compile/test failure surfaces, add a new child node
                   labeled with the prerequisite that must be true first.
4. REVERT        — Undo all changes from this attempt (git checkout -- .).
5. REPEAT        — Recurse: pick any leaf node and run the loop for it.
```

After reverting, the codebase is always green. Each iteration either adds leaves to the graph or (when the goal compiles and tests pass) removes the root node.

---

## Building the Prerequisite Tree

Start with a blank graph. The first attempt produces the first set of children.

```
Goal: Migrate OrderService to use Repository<Order>
  └── OrderService uses List<Order> directly
        └── List<Order> returned by LegacyDao
              ├── LegacyDao has no interface
              └── OrderService tests call LegacyDao.findAll() directly
```

Key practices:

- One node = one atomic, reviewable change.
- Keep node descriptions as imperative statements: "Extract OrderRepository interface from LegacyDao."
- If a node's attempt surfaces more prerequisites, add children before reverting.
- Use a whiteboard, index cards, or a lightweight tool (e.g., a plain text file committed as `mikado.md`) to track the graph during the refactor.

---

## Leaf-First Execution

A leaf node has no children: it can be done right now without breaking anything else.

Process:

1. Pick any leaf.
2. Make the change, run tests, verify CI is green.
3. Commit and merge to `main`.
4. Remove the node from the graph.
5. Re-examine its parent — it may now be a new leaf.

This produces a steady stream of small, shippable PRs. The root node is the last thing merged.

Benefits over a long-lived feature branch:

- No merge conflicts accumulating over weeks.
- Each PR is reviewable in isolation.
- The team can stop at any leaf boundary if priorities change; the codebase remains coherent.

---

## Worked Example

**Goal:** Replace `synchronized` blocks with `java.util.concurrent.locks.ReentrantLock` in `InventoryService`.

### Initial Attempt

Edit `InventoryService`, replace first `synchronized` block, run tests.

**Failure:** `InventoryServiceTest` mocks `synchronized` timing and asserts on thread state.

### Graph after first attempt

```
[ROOT] Replace synchronized with ReentrantLock in InventoryService
  └── [A] InventoryServiceTest couples to synchronized timing
```

Revert. Graph now has one leaf: A.

### Work leaf A

Edit `InventoryServiceTest`: remove timing assertions, replace with deterministic state checks. Tests pass. Commit: "refactor(test): decouple InventoryServiceTest from synchronized timing". Merge.

Remove A from graph. Root is now a leaf.

### Work root

Edit `InventoryService`, replace `synchronized` blocks with `ReentrantLock`. Tests pass. Commit: "refactor: replace synchronized with ReentrantLock in InventoryService". Merge.

Graph is empty. Done.

---

## Common Pitfalls

| Pitfall | Consequence | Remedy |
|---------|-------------|--------|
| Not reverting after each attempt | Accumulates broken state; graph becomes unreliable | Always revert before picking the next leaf |
| Nodes that are too large | Leaf merges cause their own cascades | Split: one node = one type or one method |
| Skipping the graph for "small" goals | Sprawl creeps back in | If you catch yourself editing 3+ files, start the graph |
| Merging non-leaf nodes | Breaks `main`; blocks other work | Only merge when tests are green with no open children |

---

## Related Patterns

- **Strangler Fig**: Mikado handles prerequisite untangling within a system; Strangler Fig handles routing traffic away from a legacy system. Use both when the goal spans architectural boundaries.
- **Characterization Testing**: Write characterization tests as Mikado leaf nodes when the legacy code has no coverage.
- **Branch by Abstraction / Expand-Contract**: Once prerequisites are cleared, use expand-contract to swap implementations without a flag or a long branch.

---

**Reference:** Ola Ellnestam & Daniel Brolund, *The Mikado Method* (The Pragmatic Bookshelf, 2014). Pattern origin: https://mikadomethod.info
