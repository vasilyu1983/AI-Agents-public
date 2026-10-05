# Grounding & Communication Primitives — Overview

Read when selecting an understanding check or repair mechanism. Classical definitions are summarized here; source details and empirical scope are in [`../data/sources.json`](../data/sources.json). Application checks are design conventions to evaluate locally.

## Table of Contents

1. [Common Ground](#1-common-ground)
2. [Grounding Criterion](#2-grounding-criterion)
3. [Contributions: Presentation + Acceptance](#3-contributions-presentation--acceptance)
4. [Evidence of Understanding](#4-evidence-of-understanding)
5. [Repair](#5-repair)
6. [Presupposition](#6-presupposition)
7. [Audience Design](#7-audience-design)
8. [Joint Commitment](#8-joint-commitment)
9. [Least Collaborative Effort](#9-least-collaborative-effort)
10. [Grounding Cost / Tracks](#10-grounding-cost--tracks)

## 1. Common Ground

Common ground concerns information believed to be shared, rather than merely delivered. Communal knowledge comes from shared group background; personal common ground comes from interaction history (Clark 1996).

**Agent failure:** sender and recipient received identical text but interpret different goals or retain different settled decisions after compression.
**Check:** compare their interpretations of the current goal, targets, constraints, and unresolved issues. Preserve settled state explicitly when context may be lost. Do not treat a paraphrase as proof of correctness.

Yao et al. (2026, preprint) find individually capable agents failing as dyads in their negotiation game. Shared state and explicit proposal status are operational responses to the observed failures, not interventions guaranteed by the paper.

## 2. Grounding Criterion

Understanding need only be sufficient for the current purpose (Clark & Schaefer 1989).

**Agent failure:** one confirmation rule applies to every task, producing either unnecessary pauses or untested consequential ambiguity.
**Check:** proceed with inspectable evidence for clear, authorized reversible work. Before consequential action, verify the target, constraints, and authority; pause only for unresolved ambiguity or missing authorization that changes the action. Preserve authorization already supplied.

## 3. Contributions: Presentation + Acceptance

A contribution combines presentation by the speaker and acceptance evidence from the recipient (Clark & Schaefer 1989). Acceptance can be implicit and criterion-relative.

**Agent failure:** a successful send is treated as successful understanding, or an explicit reply is required despite a relevant first artifact already demonstrating it.
**Check:** define the evidence needed at dispatch. A task-specific next move can suffice for reversible work; stronger checks should resolve the ambiguity before consequential execution.

## 4. Evidence of Understanding

[Clark & Schaefer (1989, p. 267)](https://web.stanford.edu/~clark/1980s/Clark.Schaefer.89.pdf) distinguish continued attention, a relevant next contribution, acknowledgment, demonstration of meaning, and verbatim display of the presentation. Their strength ordering is approximate and task-dependent. **Display means repeating the presentation; producing a work artifact is an application check, not their definition of display.**

**Agent failure:** "ack" or a copied instruction substitutes for a task-specific interpretation.
**Check:** choose evidence that reveals the likely mistake: paraphrase for meaning, read-back for an exact identifier, or an inspectable artifact for an authorized reversible task.

Rifts (ACL 2025) reports threefold lower clarification initiation and sixteenfold lower follow-up requests in its sampled human-LLM conversations relative to humans. These are dataset observations, not rates for every production model. NewsInterview supplies related audience-sensitive questioning evidence; see its source entry before quoting figures.

## 5. Repair

Repair detects and corrects conversational trouble. The initiating and repairing party can each be either speaker or recipient (Schegloff et al. 1977).

**Agent failure:** a correction lands but old assumptions or referents continue to drive actions.
**Check:** restate the resulting state, mark the superseded assumption, and propagate the correction to dependent recipients before their next affected action. Check a correction against verified artifacts when they conflict; faithful propagation of a correction alone does not establish its truth.

Poelitz et al. (2026, preprint) observed unreliable updates after repairs and a small, decreasing shared vocabulary in a GPT-4.1 puzzle-matching study. Its discussion explicitly limits conclusions to that model and setup. NC-Bench examines conversational repair in small open models; inspect the source/model scope before transferring its accuracy figures. Neither establishes a universal repair rate.

For clarification channels and operational examples, read [`patterns-scenarios-traps.md`](patterns-scenarios-traps.md#trap-repair-without-common-ground-update).

## 6. Presupposition

An utterance can assume an already shared referent or fact (Stalnaker 1974).

**Agent failure:** "the file," "the second option," or team shorthand lacks a recoverable antecedent in the recipient's available context.
**Check:** bind the relevant entity by stable identity at the handoff. A referent obvious to the sender may have disappeared from the recipient's compressed context.

## 7. Audience Design

Messages are shaped for their recipient (Bell 1984; Clark & Murphy 1982).

**Agent failure:** a brief depends on the sender's private context, tools, or vocabulary; identical briefs go to differently equipped agents.
**Check:** cold-read using only the recipient's actual context. Keep the missing information needed to perform the task and trim what is demonstrably shared.

## 8. Joint Commitment

Communication is joint action: both parties participate in establishing enough understanding (Clark 1996).

**Agent failure:** sender responsibility ends at transmission, or the recipient alone bears the cost of discovering ambiguity.
**Check:** assign clarity to the sender and interpretation/repair evidence to the recipient. Shared understanding and operational permission remain separate.

CRSA (EMNLP 2025) formally models private information, task targets, and dialogue-history-dependent beliefs. Its MDDial table reports nearly identical CRSA and RSA results; use it as a formal model, not proof of a general coordination gain.

## 9. Least Collaborative Effort

Optimize joint effort rather than one party's effort (Clark & Wilkes-Gibbs 1986).

**Agent failure:** shortening the brief shifts larger interpretation and repair costs to recipients.
**Check:** estimate brief cost + acceptance cost + probability of misunderstanding × repair cost. Measure the inputs locally; a shorter message alone is not an efficiency result.

CRSA's history-conditioned gain trades utterance cost against task information; it does not directly minimize all real-world costs of both parties' work.

## 10. Grounding Cost / Tracks

Grounding costs depend on the communication medium (Clark & Brennan 1991). Reviewability, revisability, delay, and available feedback change which checks are cheap.

**Agent failure:** a synchronous-chat protocol is copied into an asynchronous job without accounting for repair latency, or confirmation cost is removed while the failure tail stays unmeasured.
**Check:** price formulation, reception, understanding, acceptance, and repair for the actual medium. Whether a subagent can be interrupted is a runtime property to check, not a universal limitation. In [Clark (1996, chapter 8)](https://web.stanford.edu/~clark/1990s/Using%20language/Clark.Ch8.Using%20language.96.pdf), the two tracks concern the official business and signals about meaning/understanding; they are not names for communication media.
