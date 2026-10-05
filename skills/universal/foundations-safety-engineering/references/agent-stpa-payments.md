# Worked STPA: LLM agent with payment-capable tools

Synthetic example. It shows the method and the traceability, not measured risk. Every test below is planned, so nothing here supports a claim that the system is safe to deploy.

Method: STPA Handbook (Leveson and Thomas 2018). Two published applications to AI systems: Mylius (arXiv:2506.01782) applies STPA to the agent scenario in Korbak et al.'s control safety case and reports that STPA surfaces causal factors that unstructured hazard analysis can miss. Doshi et al. (arXiv:2601.08012, ICSE NIER 2026) propose turning STPA-derived requirements on agent workflows into enforceable specifications on data flows and tool sequences, backed by capability, confidentiality and trust labels on MCP tools. Both papers were read at abstract level only, so no figures from them are used here.

## 1. Losses and system-level hazards

| ID | Loss |
|---|---|
| L1 | Funds leave the organization without a valid obligation: wrong payee, wrong amount, or a duplicate. |
| L2 | A legitimate payment is not made within its obligation window. |
| L3 | A payment breaches a legal or policy restriction on who may be paid. |
| L4 | Payment credentials or payee data are disclosed outside the authorized boundary. |

| ID | Hazard (system state) | Losses | System-level constraint |
|---|---|---|---|
| H1 | The agent system issues a payment instruction that no valid, current mandate covers. | L1, L3 | SC1: every executed instruction matches a current mandate on payee, amount and reference. |
| H2 | One obligation is paid more than once. | L1 | SC2: each obligation settles at most once. |
| H3 | A due, authorized payment is not issued within its window. | L2 | SC3: authorized payments are issued within the window, or escalated before it closes. |
| H4 | The agent acts with authority that was revoked, has expired, or was never granted. | L1, L3 | SC4: authority is checked at execution time against the current grant. |
| H5 | Credentials or payee data cross the trust boundary. | L4, L1 | SC5: payment secrets never enter model context or leave through tool outputs. |

Five hazards is within the handbook's rule of thumb. If there are more than about seven to ten system-level hazards, group them and refine into sub-hazards later.

## 2. Control structure

From top to bottom:

- **Policy owner (human).** Sets limits and payee allow-lists, grants and revokes the agent's credentials, and holds the kill switch. Feedback: audit log, anomaly alerts.
- **Human approver.** Approves or rejects payments above a threshold. Feedback: the approval view, which may be written by the model.
- **Planner LLM.** Proposes `send_payment(payee, amount, ref, idempotency_key)`. Its inputs include untrusted content: customer messages, invoices and retrieved documents. Feedback: tool results.
- **Policy hook.** Deterministic code at the mutation boundary that allows or blocks each call. Feedback: mandate store, grant store, ledger.
- **Payment gateway (actuator)** and **payment rail/provider (controlled process)**. Feedback: synchronous responses, asynchronous status webhooks, ledger reconciliation.

The planner's process model is built from text. It cannot tell an instruction from data unless the structure tells it. Treat any path from untrusted content to a tool argument as a control input from an adversarial source.

## 3. Unsafe control actions (all four types)

| UCA | Controller / action | Type | Context | Hazard |
|---|---|---|---|---|
| U1 | Policy hook does not block `send_payment` | Not provided | Payee differs from the mandate's payee | H1 |
| U2 | Policy owner does not suspend the agent | Not provided | Anomaly alert on payout volume is active | H1, H4 |
| U3 | Planner provides `send_payment` | Provided | Payee or amount came from untrusted content, for example "our bank details changed" in an invoice | H1 |
| U4 | Approver provides Approve | Provided | The approval view shows a summary that differs from the parameters actually executed | H1 |
| U5 | Planner provides `send_payment` | Too late / wrong order | Issued after the mandate or credential was revoked | H4 |
| U6 | Planner provides a retry | Too early | Retries before the status of the earlier attempt is known | H2 |
| U7 | Planner provides `send_payment` | Too late | Issued after the obligation window closed | H3 |
| U8 | Approval grant is applied | Too long | A standing approval covers transactions after the one reviewed | H1, H4 |
| U9 | Agent suspension is applied | Too long | Suspension outlives the incident and blocks due payouts | H3 |

The Duration type applies to continuous or persistent actions, here grants and suspensions. It is N/A for the discrete `send_payment` call.

Controller constraints come from inverting each UCA. For U4: the approver must not approve unless the view shows the canonical call parameters, rendered by the hook and not by the model. For U6: the planner must not retry without the original idempotency key.

## 4. Loss scenarios

Type (a) asks why the UCA would occur. Type (b) asks why a control action is improperly executed or not executed.

- **S1 (a → U3).** A retrieved invoice contains changed bank details. The planner's process model treats document text as an instruction. The hook checks the amount limit but not where the payee came from. Every component works as specified.
- **S2 (a → U4).** High request volume and mostly benign requests make the approver rely on the model-written summary: automation bias and approval fatigue. The approver's mental model is "the summary is the call."
- **S3 (a → U6).** The gateway times out after the provider has accepted the payment. The tool returns an error. The planner concludes the payment failed and retries with a new key.
- **S4 (b → U1).** A generic HTTP tool or a code sandbox with network access can reach the provider API directly, so the call never passes the hook.
- **S5 (a → U5).** Revocation reaches a token cache late. The planner's cached credential still works.

## 5. Traceability: hazard → constraint → guardrail → test

| Hazard | Constraint | Guardrail (type @ enforcement point) | Bypass test (planned) |
|---|---|---|---|
| H1 | SC1: executed call matches the mandate on payee and amount | Deterministic mandate match @ policy hook; tag each payee argument with its provenance | Inject changed bank details through an invoice; the call must be blocked (S1) |
| H1 | U4 constraint: approval binds canonical parameters | Hook renders the approval card and signs the parameter hash; the gateway rejects on hash mismatch | Make the model summary differ from the call; execution must fail |
| H1, H4 | No execution path avoids the hook | Network egress allow-list: only the hook's service identity can reach the provider | From the sandbox and the HTTP tool, call the provider directly; must fail (S4) |
| H2 | SC2: settle at most once | Idempotency key derived from the obligation ID @ gateway; reconcile the ledger before any retry | Simulate a timeout after acceptance; exactly one settlement (S3) |
| H4 | SC4: authority checked at execution | Check grant and mandate at call time, not at plan time; short token lifetime | Revoke mid-run; the next call must be blocked (S5) |
| H4 | U8 constraint: one approval covers one transaction | Approval token bound to the parameter hash and single-use | Replay the approval on a second payment; must fail |
| H3 | SC3: issue or escalate within the window | Deadline monitor outside the model; escalate to a human before the window closes | Suspend the agent with a payment due; escalation must fire (U9) |
| H5 | SC5: secrets stay out of context | Gateway holds the credentials; the model sees only opaque handles | Prompt for the credentials; nothing must leak through outputs or logs |

Put guardrails where the mutation happens, not in the prompt. A prompt instruction is a process-model input for the planner, not a constraint on the system. Record a guardrail as verified only after its bypass test passes against the deployed version.

Residual unknowns: collusion between compromised upstream data and a lenient mandate, provider-side duplicate handling, and approver behaviour under real volume. Review triggers: a new tool with network reach, a new approval surface, or a change of payment provider.
