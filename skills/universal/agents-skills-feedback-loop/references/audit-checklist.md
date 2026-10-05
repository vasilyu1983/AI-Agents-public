# Audit Checklist

Run periodically (monthly) across all wired skills to catch loop drift.

## Mechanical Checks

For every skill that has a `learnings.md` or `learnings.consolidated.md`:

1. **Addendum present?** Does `SKILL.md` contain the *Learnings Loop* section? If not, the loop is orphaned.
2. **Both files within caps?** Raw ≤150, consolidated ≤60.
3. **Dates well-formed?** Every entry starts with `- [YYYY-MM-DD]`.
4. **One bullet per entry?** No multi-paragraph entries.
5. **No undated entries?** Reject.
6. **Section headers match the canonical five?** No invented sections except the optional `## Filter Override`.

Run:

```bash
for skill in skills/universal/*/ skills/project/*/ skills/client/*/*/; do
  if [ -f "$skill/learnings.consolidated.md" ]; then
    python3 skills/universal/agents-skills-feedback-loop/scripts/consolidate.py "$skill" --audit
  fi
done
```

## Semantic Checks (human)

- **Stale entries.** Any entry older than 90 days that has not recurred — flag for exclusion from consolidated memory; retain raw history.
- **Promotion-out candidates.** Consolidated entries that have been stable for 3+ cycles — move to host's `references/` by reviewed skill edit and remove from loop.
- **Contradictions.** An entry contradicts the host skill's `SKILL.md` — fix the skill, not the loop.
- **Cross-skill leakage.** An entry that really belongs in another skill — move it.
- **Generic advice.** An entry that is really a coding rule — move to `AGENTS.md` or `coding-behavior.md` by reviewed edit and remove from consolidated memory; retain raw history.

## Orphan Detection

A loop is orphaned when:

- Host skill was renamed or deleted but learnings files remain.
- Host skill's `SKILL.md` no longer carries the addendum (someone edited it out).
- An empty consolidated file and prolonged silence are cues to inspect authorized usage evidence; they do not establish an orphan by themselves.

Action: surface an orphan for an explicit retention decision; do not delete history automatically.

## Reporting

The audit produces a single line per skill:

```
<skill>  raw=<n>/150  consolidated=<n>/60  oldest=<YYYY-MM-DD>  addendum=<yes|no>  status=<ok|warn|orphan>
```

Anything not `status=ok` needs a human pass.

## Lesson Receipts

Use this procedure before closing a routing lesson in this library. It records evidence for a fixed commit, not proof of better answers.

1. Give the lesson a unique `YYYY-MM-DD STALL|MISROUTE subject` key in `skills/routing-log.md`.
2. Put `Lesson-Ref: <key>` in the fix commit's final trailer block.
3. Run a relevant regression gate against that commit's files. Record the actual command and exit code.
4. Save the gate record below as a repository-relative JSON file. Do not store secrets or transcript text.
5. Append one receipt to `audit/lesson-receipts.jsonl`. Do not invent receipts for old fixes with no evidence.
6. Add `→ fix <sha9> → result verifier passed` to the lesson only if the gate passed. Otherwise use `pending` or `verifier failed`.
7. Run `python3 audit/skill-status.py lessons --ref HEAD`. Missing, duplicate, mismatched, pending, and failed evidence cannot pass.

Each JSONL receipt has these fields:

| Field | Contract |
|---|---|
| `schema_version` | Integer `1` |
| `lesson_ref` | The unique lesson key, exactly as in the trailer |
| `fix_commit` | Full 40-character commit SHA, reachable from `--ref` |
| `artifacts` | Nonempty list of unique repository-relative paths to regular files in the fix commit |
| `artifact_digest` | SHA-256 of the canonical map described below |
| `gate_path` | Repository-relative path to the gate JSON file |
| `gate_digest` | SHA-256 of the exact gate file bytes |

The artifact map associates each path with the SHA-256 of its committed blob bytes. Serialize it with `json.dumps(hashes, sort_keys=True, separators=(",", ":"))`, encode as UTF-8, then hash those bytes with SHA-256. The checker rejects paths that leave the repository.

The gate JSON contains `schema_version: 1`, `fix_commit`, `artifact_digest`, `command`, and `exit_code`. The command is a nonempty array of arguments. A passing gate has integer `exit_code: 0`; if `result` is present, it must be `"passed"`.

The checker recomputes both digests and matches the gate, trailer, receipt, and routing log. It verifies recorded evidence integrity. It does not execute the command or authenticate who recorded its result. Human review must confirm that the recorded run used the named source files.

`consolidate.py --queue` checks result syntax and age. It keeps old fix notes and pending results visible with exit 1; failed results also return 1. Only an exact successful result closes that syntax check. The receipt checker provides the separate evidence check.

The library's `release` validation profile runs both checks. An empty receipt set fails. Historical `FIXED` and `→ fix applied` claims require evidence migration; the checker never creates evidence or changes history.
