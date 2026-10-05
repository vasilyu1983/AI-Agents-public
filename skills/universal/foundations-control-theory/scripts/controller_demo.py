#!/usr/bin/env python3
"""Deterministic illustrative PI plant simulation; not production tuning."""
import argparse
import json
import math
from collections import deque


def integral_step(integral, error, kp, ki, dt, lower, upper, anti_windup=True):
    """Integral state is in actuator units; positive Ki and direct plant action."""
    if not all(math.isfinite(v) for v in (integral, error, kp, ki, dt, lower, upper)):
        raise ValueError('controller inputs must be finite')
    if dt <= 0 or ki < 0 or lower >= upper:
        raise ValueError('invalid period, integral gain, or bounds')
    raw = kp * error + integral
    increment = ki * error * dt
    if not math.isfinite(raw) or not math.isfinite(increment):
        raise ValueError('controller arithmetic overflow')
    outward = (raw > upper and increment > 0) or (raw < lower and increment < 0)
    if not anti_windup or not outward:
        integral += increment
    raw = kp * error + integral
    if not math.isfinite(integral) or not math.isfinite(raw):
        raise ValueError('controller arithmetic overflow')
    return integral, min(upper, max(lower, raw))


def simulate(anti_windup=True):
    # First-order stable plant, gain 1, tau 5s; two-second transport delay.
    # Setpoint 2 is deliberately infeasible with actuator [0,1], then falls to .5.
    dt, tau, delay = .1, 5., 20
    pending = deque([0.] * delay)
    y = integral = effort = violations = 0.
    crossed_target = False
    post_crossing_excess = None
    settled_at = None
    recovery_values = []
    for k in range(1000):
        t = k * dt
        target = 2. if t < 30 else .5
        # Fixed deterministic bounded sensor disturbance.
        measurement = y + .005 * math.sin(k * .37)
        integral, u = integral_step(integral, target - measurement, 1., .2, dt, 0., 1., anti_windup)
        violations += float(not 0 <= u <= 1)
        delayed = pending.popleft()
        pending.append(u)
        y += dt * (delayed - y) / tau
        effort += abs(u) * dt
        if t >= 30:
            if y <= target:
                crossed_target = True
            if crossed_target:
                post_crossing_excess = max(post_crossing_excess or 0., y - target)
            recovery_values.append(y)
    # Settling: earliest recovery sample after which all remaining observations
    # remain within 2% of the .5 target; finite observation-window metric only.
    for j, value in enumerate(recovery_values):
        if abs(value - .5) <= .01 and all(abs(v - .5) <= .01 for v in recovery_values[j:]):
            settled_at = j * dt
            break
    return dict(anti_windup=anti_windup,
                post_crossing_excess=(round(post_crossing_excess, 6)
                                      if post_crossing_excess is not None else None),
                settling_seconds=settled_at, constraint_violations=int(violations),
                control_effort=round(effort, 6), final_state=round(y, 6))


def self_test():
    # At upper/lower saturation, outward error freezes; opposite error unwinds.
    assert integral_step(12., 2., 0., 1., 1., 0., 10.) == (12., 10.)
    assert integral_step(12., -2., 0., 1., 1., 0., 10.) == (10., 10.)
    assert integral_step(-2., -2., 0., 1., 1., 0., 10.) == (-2., 0.)
    assert integral_step(-2., 2., 0., 1., 1., 0., 10.) == (0., 0.)
    good, bad = simulate(), simulate(False)
    assert good['constraint_violations'] == bad['constraint_violations'] == 0
    assert good['settling_seconds'] is not None
    assert bad['settling_seconds'] is None or good['settling_seconds'] < bad['settling_seconds']
    assert good == simulate(), 'simulation must be reproducible'
    return [good, bad]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    print(json.dumps(self_test() if args.self_test else [simulate(), simulate(False)], indent=2))
