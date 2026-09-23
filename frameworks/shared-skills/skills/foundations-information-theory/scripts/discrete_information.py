#!/usr/bin/env python3
"""Finite distribution known answers in bits; no empirical estimation."""
import json
import math


def pmf(values):
    if not isinstance(values, (list, tuple)) or not values:
        raise ValueError('nonempty probability list required')
    if any(isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p) or p < 0 for p in values):
        raise ValueError('finite nonnegative probabilities required')
    if not math.isclose(math.fsum(values), 1, rel_tol=0, abs_tol=1e-12):
        raise ValueError('probabilities must sum to one; never normalized')
    return values


def entropy(p):
    return -math.fsum(x * math.log2(x) for x in pmf(p) if x)


def kl(p, q):
    pmf(p); pmf(q)
    if len(p) != len(q):
        raise ValueError('support dimensions must match')
    if any(x > 0 and y == 0 for x, y in zip(p, q)):
        return math.inf
    return math.fsum(x * (math.log2(x) - math.log2(y)) for x, y in zip(p, q) if x)


def js(p, q):
    pmf(p); pmf(q)
    if len(p) != len(q):
        raise ValueError('support dimensions must match')
    midpoint = [(x + y)/2 for x, y in zip(p, q)]
    return (kl(p, midpoint) + kl(q, midpoint))/2


def mutual_information(joint):
    if not isinstance(joint, list) or not joint or any(not isinstance(row, list) or len(row) != len(joint[0]) for row in joint) or not joint[0]:
        raise ValueError('nonempty rectangular joint table required')
    pmf([p for row in joint for p in row])
    rows = [math.fsum(row) for row in joint]
    columns = [math.fsum(row[j] for row in joint) for j in range(len(joint[0]))]
    return math.fsum(p * (math.log2(p) - math.log2(rows[i]) - math.log2(columns[j])) for i, row in enumerate(joint) for j, p in enumerate(row) if p)


def fano_floor(conditional_bits, classes):
    if isinstance(classes, bool) or not isinstance(classes, int) or classes < 2 or isinstance(conditional_bits, bool) or not isinstance(conditional_bits, (int, float)) or not math.isfinite(conditional_bits) or not 0 <= conditional_bits <= math.log2(classes):
        raise ValueError('finite conditional entropy within finite alphabet bound required')
    return max(0, (conditional_bits - 1)/math.log2(classes))


def bpb(total_bit_nll, byte_count):
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0 or isinstance(total_bit_nll, bool) or not isinstance(total_bit_nll, (int, float)) or not math.isfinite(total_bit_nll) or total_bit_nll < 0:
        raise ValueError('finite nonnegative bit NLL and positive byte count required')
    return total_bit_nll / byte_count


if __name__ == '__main__':
    print(json.dumps({'coin_entropy_bits': entropy([.5,.5]), 'independent_mi_bits': mutual_information([[.25,.25],[.25,.25]]), 'identical_mi_bits': mutual_information([[.5,0],[0,.5]]), 'disjoint_js_bits': js([1,0],[0,1]), 'disjoint_kl_support': 'infinite', 'model_a_bpb': bpb(2400000*math.log2(12.3),10000000)}, allow_nan=False, indent=2))
