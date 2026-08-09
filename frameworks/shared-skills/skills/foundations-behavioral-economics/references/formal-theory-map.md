---
description: Formal theory map for behavioral-economics foundations. Use to separate empirical behavioral effects from ethical product application.
last_verified: 2026-05-02
status: stable
---

# Behavioral Economics Formal Theory Map

## Purpose

Use this map when a behavioral recommendation needs a source-level effect, ethical boundary, or distinction between descriptive human behavior and prescriptive welfare.

## Theory Areas

| Area | Formal Objects | What It Supports | Boundary |
|---|---|---|---|
| Prospect theory | Reference point, value function, probability weighting | Gain/loss framing and loss aversion | Descriptive model, not welfare proof. Parameter estimates vary substantially across elicitation designs — Imai et al. 2025 (CESifo WP 12334; 166 papers, 812 estimates) finds that measurement procedure is the strongest predictor of parameter variation; treat published canonical values as design-dependent, not universal |
| Heuristics and biases | Anchoring, availability, representativeness | Fast judgment under uncertainty | Effect sizes vary by context |
| Nudge and choice architecture | Defaults, salience, mapping, feedback | Ethical interface defaults and option design | Requires easy opt-out and user benefit |
| Social norms | Descriptive/injunctive norms, proof signals | Social proof and norm messaging | Fake proof is deception |
| Scarcity and reactance | Perceived availability, opportunity loss | Real urgency and limited supply | Manufactured scarcity is a dark pattern |
| Intertemporal choice | Hyperbolic and beta-delta discounting | Present bias, trials, commitments | Do not exploit self-control failures |
| Mental accounting | Account labels, sunk costs, transaction utility | Bundles, budgets, price framing | Labels must clarify, not obscure cost |
| Context effects | Decoy, compromise, ordering effects | Pricing tier and menu design | Target option must be defensible |

## Production Rule

Every behavioral lever must pass three gates: truth of the signal, user-benefit alignment, and easy reversal. If disclosure would destroy the mechanism or embarrass the team, do not ship it.
