# Comparability and drift

Compare interpretations before comparing numbers. Record group, language, administration mode, task composition, model/tool/scorer version, and selection into the observed sample.

For a latent-variable model, distinguish configural structure, loading relationships, and intercept/threshold behavior. Comparable latent means require stronger support than a common pattern of factors; residual constraints address further comparisons. Report the actual model, estimation assumptions, fit evidence, and tested restrictions. Do not declare invariance from a nonsignificant test, a universal fit-change cutoff, or equal alpha coefficients. Partial invariance needs explicit anchors and sensitivity analysis; differential item functioning can reveal item-specific differences without establishing their cause.

For physical measurements, document whether results share an adequate reference, range, uncertainty, and operating conditions. Two calibrated instruments may still be incomparable outside their calibration scope.

For longitudinal monitoring, preserve anchor items or reference specimens, version scoring rules, and use overlap samples when replacing instruments. Distinguish target change from composition change, administration change, and instrument drift. Predefine decision-relevant drift tolerances using the intended use and error consequences rather than inventing universal limits.

If no bridge study exists after an instrument changes, label trend continuity conditional or insufficient. Historical scores should retain their original provenance instead of being silently rescored or pooled.

## Drift from selection pressure

Goodhart's law (Goodhart 1975) and Campbell's law (Campbell 1979) name the same failure: once a score is used to control or reward, the regularity between score and construct weakens because people and optimizers act on the score. In LLM evaluation this appears as benchmark hacking, judge-specific tuning and gate-specific prompt engineering. Messing (2026, [arXiv 2604.11581](https://arxiv.org/abs/2604.11581)) treats the unmodelled judge, temperature and prompt variance as the surface that benchmark hacking exploits. Decision rules:

- Date the moment a metric became a target. Values before and after are on different instruments until an untargeted holdout (fresh items, a second judge, a task the optimizer never saw) links them.
- Keep at least one measure that nobody is rewarded on, and check that it moves with the targeted one. Divergence is the drift signal; agreement is only weak reassurance.
- A training objective or selection criterion that includes the eval score voids that score as validity evidence for the same system.

Source scope: Meredith (1993), DOI 10.1007/BF02294825, introduces measurement and factorial-invariance distinctions; its primary publisher abstract was inspected. This workflow does not attribute universal fit thresholds or exact theorem claims to that abstract. Goodhart (1975) and Campbell (1979) are cited for the concept only; their wording was checked against secondary summaries, not the original papers.
