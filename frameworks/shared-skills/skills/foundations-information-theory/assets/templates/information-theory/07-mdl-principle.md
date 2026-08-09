# Primitive 7: MDL Principle

## Definition

**Minimum Description Length (MDL)** selects the model M that minimizes the total description length of both the model and the data given the model:

```
MDL(M) = L(M) + L(D | M)
```

where:
- L(M) = description length of model M in bits
- L(D|M) = description length of data D given model M in bits

Select M* = argmin_M [L(M) + L(D|M)].

**Two-part (crude) MDL**: separate the model and the data-given-model codes. Model is described first; data compressed using the model.

**Refined MDL (NML / universal codes)**: uses the normalized maximum likelihood (NML) or prequential codes that avoid the two-stage commitment. NML minimizes worst-case regret against any distribution in the model class.

```
Regret = log p*(D) − log p_M(D | M*)     [where p*(D) is the best in-class likelihood]
NML minimizes max_{D} regret
```

**Relation to Bayesian model selection**: MDL with universal codes is asymptotically equivalent to the Bayesian marginal likelihood (model evidence) with a Jeffreys prior. MDL is thus a frequentist justification for Bayesian Occam's razor.

**BIC approximation**:

```
BIC(M) ≈ −2 log L(D | θ̂_M) + k · log n
```

where k = number of free parameters, n = number of data points. BIC is a large-n approximation to two-part MDL.

**Stochastic complexity** (Rissanen): the normalized maximum likelihood code length — the most refined single-number summary of MDL for parametric families.

---

## When to Use

- **Model selection**: choosing between models of different complexity (e.g., decision tree depth, neural network width, polynomial degree).
- **Feature selection**: selecting the minimal set of features whose description of the data is shortest.
- **Hyperparameter tuning**: choosing regularization strength that minimizes total code length.
- **Anomaly detection**: a data point with high L(D|M) (hard to describe given the model) is anomalous.
- **Prompt / context compression**: selecting the shortest prompt that still encodes the task (MDL frames prompt design as description-length minimization).

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| Model class {M_i} | Set of models | Candidate models with different complexity levels |
| Data D | Dataset | Training examples to be described |
| Code for models | Prefix-free code | Maps each model to a binary string |
| Conditional code | Source code | Maps D to a binary string given M |

---

## Outputs

| Output | Type | Interpretation |
|--------|------|----------------|
| L(M) | Non-negative integer (bits) | Complexity cost of the model |
| L(D\|M) | Non-negative real (bits) | Data fit: compressed data length under M |
| MDL(M) | Non-negative real (bits) | Total description cost; minimize this |

---

## Failure Modes

1. **BIC as exact MDL**: BIC is a large-n approximation. For small n or non-regular models (e.g., neural nets, mixture models), BIC can differ substantially from true MDL. Use NML or prequential codes for small datasets.
2. **Ignoring model description cost for neural networks**: Neural network weights require a description. If parameters are treated as free (L(M)=0), MDL reduces to maximum likelihood — overfitting. Use quantization, pruning, or weight sharing as model description cost proxies.
3. **Treating MDL as a Bayesian prior**: MDL is not identical to Bayesian inference unless the code is the NML code. For non-NML codes, the implicit "prior" is often improper or misleading.
4. **Two-part MDL with poorly chosen codes**: The result depends on the code used to describe models. If L(M) is chosen arbitrarily, MDL can favor any model. Use universal codes (e.g., integer codes for continuous parameters via quantization resolution).
5. **MDL not accounting for context**: For sequential data, prequential MDL (online coding) is more appropriate than two-part MDL; it accumulates description cost as data arrives.

---

## Worked Example

**Model selection for a text classifier**

Three classifiers evaluated on 10,000 training examples (n=10,000):

| Model | Parameters k | L(M) [bits] | −log L(D\|θ̂) [nats→bits] | MDL [bits] |
|-------|-------------|-------------|--------------------------|-----------|
| Logistic (unigram) | 10,000 | 130,000 | 52,000 | 182,000 |
| LSTM | 2M | 26,000,000 | 18,000 | 26,018,000 |
| Logistic (bigram) | 100,000 | 1,300,000 | 41,000 | 1,341,000 |

L(M) estimated as k · log₂(precision) = k · 13 bits per parameter (32-bit float → ~13 bits effective). The LSTM achieves the best data fit but its model description cost dominates. Logistic-unigram minimizes total MDL, suggesting it explains the data as well as needed given its compactness.

---

## Sources

- Rissanen, J. (1978). Modeling by shortest data description. *Automatica*, 14(5), 465–471.
- Grünwald, P. (2007). *The Minimum Description Length Principle*. MIT Press.
- Rissanen, J. (1996). Fisher information and stochastic complexity. *IEEE Transactions on Information Theory*, 42(1), 40–47.
- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 14. Wiley.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 28. Cambridge.
- Schwarz, G. (1978). Estimating the dimension of a model. *Annals of Statistics*, 6(2), 461–464. (BIC derivation.)
