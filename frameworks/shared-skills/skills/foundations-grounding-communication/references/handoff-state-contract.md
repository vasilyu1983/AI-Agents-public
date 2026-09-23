# Inspectable Handoff and Revised State

## Minimal handoff record

| Field | Content |
|---|---|
| Identity/version | Stable handoff ID and current version |
| Goal and done | Task outcome and inspectable acceptance criterion |
| Targets | Stable entity/file IDs rather than “the second option” |
| Constraints | Scope, preserved behavior and relevant permissions |
| Owner/current state | Responsible recipient, settled decisions and last verified artifact |
| Unresolved issues | Load-bearing ambiguity and missing context/authority |
| Corrections | Delta, superseded assumption and affected downstream consumers |

A handoff record is an operational convention, not a theorem or mandatory wire schema. Use the minimum fields the task requires. A paraphrase/ack is fallible understanding evidence and cannot grant authority.

## Proportionate acceptance

For clear, authorized reversible work, expose the working interpretation and proceed with an inspectable first artifact. Do not create a blocking reconfirmation loop. Before consequential action, verify target, constraints and authority; pause only if unresolved ambiguity or missing authorization can change the action. Existing explicit authorization remains valid within its scope.

## Repair and compression

After a correction, update the goal/targets/constraints in the current version and propagate it to dependent recipients before their next affected action. Record what was superseded. At compression boundaries retain settled decisions, last verified work, current authority and unresolved issues; recompute cheap background facts when needed.

## Worked repair

Version 1 targets OAuth. User corrects target to SAML. Version 2 explicitly identifies the SAML handler, preserved endpoint behavior and unchanged authorized draft scope, marks OAuth superseded and notifies downstream work. “Ack” followed by editing OAuth is failed repair. The corrected state still authorizes only the existing scope.

## Regression checks

- Authorized reversible drafting proceeds without a new confirmation.
- Missing authority cannot be supplied by an acceptance signal.
- A correction replaces old referents in downstream state.
- Compression does not lose scope, current entity or unresolved issue.
- A relevant first artifact may be sufficient understanding evidence for low-stakes work.

## Primary sources

- Clark & Schaefer (1989), “Contributing to Discourse”: presentation and acceptance are joint, criterion-relative acts.
- Clark & Brennan (1991), “Grounding in Communication”: evidence and costs depend on medium and task.
- [Human-AI common-ground benchmark (preprint)](https://arxiv.org/abs/2602.21337): repair updates and efficiency are empirical targets; local tests remain necessary.
