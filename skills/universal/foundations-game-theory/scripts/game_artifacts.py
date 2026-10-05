#!/usr/bin/env python3
"""Exact small finite-game and Shapley examples; no empirical calibration claim."""
import argparse
import json
import math
from fractions import Fraction


def pure_equilibria(payoffs):
    """Two-player rectangular matrix; ties are best responses."""
    if not payoffs or not payoffs[0]:
        raise ValueError('nonempty rectangular matrix required')
    rows, cols = len(payoffs), len(payoffs[0])
    if not rows or not cols or any(len(row) != cols for row in payoffs):
        raise ValueError('nonempty rectangular matrix required')
    return [(r, c) for r in range(rows) for c in range(cols)
            if payoffs[r][c][0] == max(payoffs[x][c][0] for x in range(rows))
            and payoffs[r][c][1] == max(payoffs[r][x][1] for x in range(cols))]


def shapley(values, n):
    """Enumerate all subsets; values maps bitmask to coalition utility."""
    if n < 1 or n > 10 or set(values) != set(range(1 << n)):
        raise ValueError('complete characteristic function required; 1<=n<=10')
    exact_values = {mask: Fraction(value) for mask, value in values.items()}
    result = [Fraction(0)] * n
    for member in range(n):
        for mask in range(1 << n):
            if mask & (1 << member):
                continue
            size = mask.bit_count()
            weight = Fraction(math.factorial(size) * math.factorial(n-size-1), math.factorial(n))
            result[member] += weight * (exact_values[mask | (1 << member)] - exact_values[mask])
    return result


def artifacts():
    # Prisoner's dilemma: rows/columns [cooperate, defect], utility per player.
    payoffs = [[(3, 3), (0, 5)], [(5, 0), (1, 1)]]
    # A contributes2, B contributes1, A+B synergy3, C harms quality by1.
    values = {mask: 2*bool(mask&1) + bool(mask&2) + 3*bool(mask&1 and mask&2) - bool(mask&4)
              for mask in range(8)}
    credit = shapley(values, 3)
    return dict(payoff_matrix=payoffs, pure_equilibria=pure_equilibria(payoffs),
                coalition_values=values, shapley=credit,
                evaluated_coalitions=len(values), efficiency_total=sum(credit),
                grand_coalition_increment=values[7]-values[0])


def self_test():
    result = artifacts()
    assert result['pure_equilibria'] == [(1, 1)]
    assert result['shapley'] == [3.5, 2.5, -1.]
    assert result['efficiency_total'] == result['grand_coalition_increment'] == 5.
    seven = {mask: mask.bit_count() for mask in range(128)}
    assert shapley(seven, 7) == [Fraction(1)] * 7
    assert sum(shapley(seven, 7)) == Fraction(7)
    equal = {mask: mask.bit_count() for mask in range(32)}
    assert all(math.isclose(v, 1.) for v in shapley(equal, 5))
    assert all(math.isclose(v/5, .2) for v in shapley(equal, 5))
    matching_pennies = [[(1,-1),(-1,1)],[(-1,1),(1,-1)]]
    assert pure_equilibria(matching_pennies) == []  # no claim of no mixed equilibrium
    try:
        shapley({0: 0}, 2)
    except ValueError:
        pass
    else:
        raise AssertionError('missing coalitions must fail')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    print(json.dumps(self_test() if args.self_test else artifacts(), indent=2,
                     default=lambda value: {"exact_fraction": str(value), "float_projection": float(value)}))
