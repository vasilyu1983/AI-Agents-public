# Multi-Agent Coding Team Checklist

Pre-dispatch validation for coding agent teams. Complete before launching workers.

## Pattern Selection

- [ ] Chose pattern: Coordinator-Led / Fork Subagents / Agent Teams (Peer Swarm)
- [ ] Pattern matches the coordination needs (leader control vs peer messaging vs background work)
- [ ] Started from matching template

## Role Design

- [ ] Each worker has a clear, bounded role (researcher, implementer, verifier, etc.)
- [ ] No role overlap — each worker owns a distinct concern
- [ ] Worker prompts are self-contained (workers can't see coordinator's conversation)
- [ ] Verifier is separate from implementer (never self-verify)

## Interface Contracts

- [ ] Interfaces frozen before dispatch — all contracts defined
- [ ] Each worker knows its expected output format (structured report)
- [ ] Coordinator knows how to parse worker outputs
- [ ] Handoff payloads include: task ID, owned files, expected output, verify command

## File Ownership

- [ ] Each worker has exclusive owned_files (no overlap)
- [ ] No two workers edit the same file
- [ ] File assignments documented in task graph or dispatch prompt
- [ ] Workers instructed: "Do NOT modify files outside your assigned set"

## Communication

- [ ] Communication pattern chosen:
  - Coordinator: `<task-notification>` XML → SendMessage for follow-up
  - Fork: parent notification only (no mid-flight peeking)
  - Teams: mailbox messaging via SendMessage
- [ ] Broadcast rules defined (who can message whom)
- [ ] Status reporting expected (completion notification, progress if long-running)

## Isolation

- [ ] Worktree isolation evaluated:
  - Required if: multiple workers edit files, merge conflicts possible
  - Not needed if: read-only workers, single editor
- [ ] Permission mode set per worker (read-only workers get default, editors get acceptEdits)
- [ ] Background execution configured where appropriate

## Verification

- [ ] Separate verification worker assigned (adversarial posture)
- [ ] Verifier uses fresh context (doesn't know implementation details)
- [ ] Verification includes: run tests, check output format, validate file changes
- [ ] Verification evidence required (command output, not just assertion)

## Escalation

- [ ] Escalation path defined:
  1. Worker self-corrects (once)
  2. Escalates to lead with diagnosis
  3. Lead reassigns or rescopes
  4. Human escalation if still stuck
- [ ] Timeout behavior defined (what happens if worker takes too long)

## State Persistence

- [ ] Task graph persisted to file (JSON/YAML/Markdown)
- [ ] Decisions documented (why this approach, what was tried)
- [ ] Dependency outputs stored (research findings, test results)
- [ ] Progress trackable by human if they check in

## Synthesis Gate

- [ ] Coordinator/lead MUST read and understand all worker findings before directing implementation
- [ ] Implementation specs include exact file paths, line numbers, and changes
- [ ] Never "based on your findings, fix it" — always synthesize first
