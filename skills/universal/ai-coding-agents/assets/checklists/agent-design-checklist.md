# Agent Design Checklist

Pre-creation validation for single coding agents. Complete each item before deploying.

## Task Classification

- [ ] What code does the agent read or modify?
- [ ] What is the input? (user prompt, file paths, diff, PR URL)
- [ ] What is the expected output? (findings report, test files, refactored code, migration log)
- [ ] Is the task read-only or does it require edits?

## Archetype Selection

- [ ] Chose an archetype (reviewer, test generator, refactoring, migration, docs, security)
- [ ] Started from the matching template in `assets/templates/`
- [ ] Customized for specific use case

## Tool Scoping

- [ ] Tools limited to the minimum needed
- [ ] Read-only agents have `disallowedTools: [Edit, Write, NotebookEdit]`
- [ ] Bash commands restricted to safe operations (if applicable)
- [ ] No `tools: ['*']` unless explicitly justified

## Boundaries

- [ ] `maxTurns` set (8-10 analysis, 15-20 implementation, 25+ migration)
- [ ] Owned files or directories specified in the system prompt
- [ ] Explicit "must NOT" constraints documented
- [ ] `permissionMode` set appropriately (default for read-only, acceptEdits for editors)

## Context Strategy

- [ ] File discovery approach defined (targeted reads vs grep/glob discovery)
- [ ] Token budget considered (instruction + code + output)
- [ ] Large file handling planned (offset/limit, search-then-read)
- [ ] Cross-file dependencies accounted for (imports, types, interfaces)

## Verification

- [ ] Self-verification approach defined (run tests, grep for anti-patterns, before/after comparison)
- [ ] Output contract specified (what the agent must produce)
- [ ] Failure behavior defined ("if stuck after 2 attempts, report and stop")

## Description (Triggering)

- [ ] Description is 120-180 characters
- [ ] Written in third person
- [ ] Includes specific trigger phrases (not generic)
- [ ] Distinguishes from adjacent agents

## Smoke Test

- [ ] Tested on simple happy path
- [ ] Tested on edge case (empty file, missing file)
- [ ] Tested on large input (1000+ line file)
- [ ] Output format matches contract
- [ ] Token usage within budget
