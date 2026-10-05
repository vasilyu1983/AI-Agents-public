# Primitive 5: Channel Capacity

## Definition

C = max_{p(x)} I(X;Y) bits per channel use, for a channel with a named transition law p(y|x).
Binary symmetric channel with crossover p: C = 1 − H_b(p); C = 0 at p = 0.5.
AWGN (Shannon–Hartley): C = B log₂(1 + S/N) bits/s, with S/N linear (10^(dB/10)), not dB.
Coding theorem: rates below C are achievable with vanishing error asymptotically; above C, error is bounded away from zero. It is an existence result.

## Traps

1. **No channel model, no capacity.** Precision@k, accuracy or "fraction of wrong documents" does not identify p(y|x), symmetry or bits per query. Name input and output alphabets, measure transition probabilities, test memory assumptions, and compute I(X;Y) for the observed input distribution separately from capacity.
2. **Capacity is not a guaranteed rate.** Finite-blocklength rates depend on blocklength, target error and code (Polyanskiy–Poor–Verdú 2010). A noiseless binary channel reaches 1 bit/use at blocklength one, so "always strictly below C" is also wrong.
3. **Memory.** DMC formulas assume memorylessness; channels with memory need a state model.
4. **Non-Gaussian noise** needs the max-MI optimization, not log₂(1 + SNR).
5. **Human or team communication** has no defined p(x,y); capacity there is an analogy, not a number (foundations-team-theory, foundations-grounding-communication).

## Known answers

BSC(0.23): H_b(0.23) ≈ 0.778011, C ≈ 0.221989 bits/use (uniform input attains it). BSC(0.10): C ≈ 0.531004 bits/use.
Counterexample to reading accuracy as capacity: P(X=0) = 0.77 and Y always 0 gives 77% accuracy with identical transition rows and capacity 0.

## Sources

Shannon (1948); Cover & Thomas (2006) Ch. 7 (channel capacity) and Ch. 9 (Gaussian channel); Polyanskiy, Poor & Verdú (2010). Full references: [`../../../data/sources.json`](../../../data/sources.json).
