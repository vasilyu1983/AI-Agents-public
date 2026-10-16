# Graph model evaluation contracts

Load only for graph pretraining, explanations, or comparison of temporal/inferred graph models. These are proposed local evaluation recipes, not reproduced research results. Choose topology assumptions and representation with `foundations-network-science`; this reference owns evaluation of the resulting model. No training framework or dependency is prescribed.

## Shared evaluation record

Record task unit (node, edge, or graph), target, scoring time, feature/edge availability, graph-construction version, split manifest, seeds, tuning budget, primary metric and acceptance condition before experiments. Keep the final test partition untouched until selection ends. Save per-seed results and paired candidate-minus-baseline differences; report spread and failures, not only the best seed.

For an inductive claim, exclude held-out nodes/graphs and their incident edges from fitting, including graph construction and pretraining. A transductive experiment can use permitted unlabeled test-node features/topology; declare that access and do not describe it as unseen-node generalization. Labels remain held out in both settings. For link prediction, exclude held-out target occurrences and their reverse/duplicate copies from message passing; permitted historical occurrences can remain for recurring-edge prediction. Declare the candidate-pair universe, negative sampling and observation horizon. An unobserved pair is not necessarily a permanent negative.

## Self-supervision when labels are scarce

Start with graph-level classification and one semantically justified augmentation pair. [GraphCL, §3](https://arxiv.org/html/2010.13902v3) contrasts two transformed views of the same graph against other graphs. Its encoder and projection head learn representations; downstream evaluation uses the encoder. Node dropping, edge perturbation, attribute masking and subgraph sampling encode different invariance assumptions. Do not transfer its graph-level recipe to a node/event task without defining positives, negatives and leakage controls again.

1. Freeze graph/entity/time splits before choosing label budgets. Draw nested labeled subsets from training only, with the same subsets and seeds for every candidate. Record class support; reject a budget whose sampling silently removes a required class.
2. Compare a simple feature baseline, the same encoder trained with supervision only, and self-supervised initialization followed by supervised fine-tuning. Keep architecture and downstream tuning budgets equal. Count pretraining time separately and also compare under a declared total compute cap; a longer run is not a free label-efficiency gain.
3. Pretrain only on the declared eligible pool. Fit normalizers and construction thresholds within that pool. Validation labels select augmentation strength and stopping; test labels select nothing. Record transductive access explicitly if allowed.
4. Inspect transformed examples against task semantics before training. Reject edge drops that remove a target-defining chemical bond, dependency, direction or timestamp. Use an identity-view control and a single-augmentation ablation; prevent duplicate or equivalent graphs from becoming false negatives.
5. Evaluate each label budget on the same locked test set with task metrics, calibration, relevant slices and compute. Adopt only if the preregistered comparison passes. Reduced pretext loss alone is not evidence of downstream benefit.

Sanity checks: split manifests remain identical across candidates; increasing a label budget preserves earlier labeled examples; no pretraining row exceeds the availability cutoff. If an augmentation changes a fixture's known target, the augmentation is invalid even if the contrastive loss improves. A label-permuted control that retains strong held-out discrimination requires a leakage investigation.

## Explanations for a frozen graph model

[GNNExplainer, §§4–5](https://arxiv.org/html/1903.03894v4) learns structural and feature masks for a fixed prediction, seeking a compact predictive subgraph. Its synthetic motif tests motivate a check with known structure; its objective is not a causal guarantee. Keep explanation optimization separate from model fitting.

1. Freeze model, predicted class, computation graph and feature values. Choose edge/feature budget on validation examples. Save the original probability `p`, masks, seed, target class, and how masking changes normalization, self-loops and features. Recompute predictions without retraining.
2. At the same mask size, compare selected edges/features with random masks and a simple degree-based edge ranking. Report retention gap `p - p_keep` and deletion drop `p - p_delete` for the original class. Smaller retention gap indicates sufficiency under this masking rule; larger deletion drop indicates reliance. Neither must hold universally when the model has redundant evidence.
3. Vary the mask budget and report both curves. An all-edge mask can preserve a prediction trivially; a visually compact mask can still fail fidelity. Check feature-only and edge-only masking separately, because one can conceal failure of the other.
4. Repeat explainer seeds and small, task-preserving input perturbations. Compare top-k overlap after mapping edges to canonical IDs, and record prediction changes separately. For symmetric interchangeable motifs, compare equivalent structures as well as raw overlap. Mask instability on unchanged predictions limits a unique explanation claim.
5. Use a synthetic planted motif plus irrelevant features/edges as a sanity case. First verify that the trained model actually relies on that motif by controlled removal. Then measure mask edge precision/recall against the known motif. A shortcut model can accurately explain the wrong rule; failed motif recovery alone does not distinguish model failure from explainer failure.

Worked scorer check (illustrative probabilities, not an experiment): `p=0.9`, `p_keep=0.85`, `p_delete=0.4` gives retention gap `0.05` and deletion drop `0.5`. With an unchanged all-edge mask, retention gap must be zero within numerical tolerance. With an empty deletion mask, deletion drop must be zero. Failure indicates mask application or scoring errors. Removal may create invalid or out-of-distribution graphs; state this limitation and prefer domain-valid perturbations when possible. Predictive fidelity, stability and motif recovery do not establish real-world causation or fairness.

## Temporal comparison contract

After selecting fixed topology with changing features, snapshots, or events, compare a static baseline with a snapshot candidate and an event candidate only where the task and data support each. Use identical chronological targets, eligible histories, tuning budgets and negative-pair rules. For stateful models, reset/replay state from permitted history for each evaluation window; never carry a future-updated state backwards.

Report recurring versus first-seen edges separately, and identify unseen-node cases. Include quality, calibration, runtime, peak memory, update lag and snapshot staleness. A future-edge injection must not alter any earlier prediction or fitted graph artifact. If it does, the availability gate fails. An event model adds value only if the matched comparison justifies its extra operational cost; this recipe claims no measured advantage.

## Inferred-topology comparison contract

Keep observed and inferred edges separately tagged. Fit graph construction, sparsity and downstream models using training observations only; choose settings on validation data. Compare a feature-only/no-edge baseline with candidates under the same downstream budget. Test a synthetic known graph, a shared-driver case and an unrelated-signal control before real data.

Report edge precision/recall against known synthetic truth, held-out observation reconstruction, bootstrap edge-selection frequency and downstream quality separately. Use time-block resampling for dependent observations. Define directedness, signs, threshold and edge universe before scoring. A shared latent driver can produce predictive marginal edges without direct interactions; mark those as false edges only when direct structure is the declared target. Good reconstruction or stable edges alone do not establish structural recovery or causality. On real data without verified edges, label topology accuracy unmeasured.

## Source boundary

Book leads: Chelliah et al. (eds.), *Graph Neural Networks: Essentials and Use Cases*, applications chapter §§5.1–5.2 (printed pp. 175–176; PDF pp. 192–193). The primary papers above support the method descriptions. Split controls, comparison gates and worked checks here are evaluation design recommendations; no published improvement figure is adopted.
