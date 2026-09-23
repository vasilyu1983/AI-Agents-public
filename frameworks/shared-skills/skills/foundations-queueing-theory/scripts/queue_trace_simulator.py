#!/usr/bin/env python3
"""Deterministic FCFS multi-server simulation for a finite arrival/service trace."""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


QUANTILES = (0.50, 0.90, 0.95, 0.99)


class InputError(ValueError):
    """Raised when the trace or simulation configuration is invalid."""


@dataclass(frozen=True)
class TraceJob:
    job_id: str
    arrival_time: float
    service_time: float
    input_order: int


@dataclass(frozen=True)
class JobResult:
    job_id: str
    input_order: int
    server_id: int
    arrival_time: float
    service_time: float
    start_time: float
    completion_time: float
    waiting_time: float
    response_time: float


def finite_nonnegative(value: object, field: str) -> float:
    """Return a finite nonnegative float while rejecting booleans."""
    if isinstance(value, bool):
        raise InputError(f"{field} must be a finite nonnegative number, not a boolean")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise InputError(f"{field} must be a finite nonnegative number") from exc
    if not math.isfinite(number) or number < 0:
        raise InputError(f"{field} must be a finite nonnegative number")
    return number


def positive_server_count(value: object) -> int:
    """Return a positive integer server count while rejecting booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InputError("servers must be a positive integer")
    return value


def load_trace(path: Path) -> list[TraceJob]:
    """Load and validate a CSV trace without separating paired observations."""
    try:
        handle = path.open("r", encoding="utf-8", newline="")
    except OSError as exc:
        raise InputError(f"cannot read input trace {path}: {exc}") from exc

    try:
        with handle:
            return _load_trace_rows(handle)
    except (UnicodeError, csv.Error) as exc:
        raise InputError(f"input trace is not valid UTF-8 CSV: {exc}") from exc


def _load_trace_rows(handle: Any) -> list[TraceJob]:
    """Parse validated trace rows from an open text stream."""
    reader = csv.DictReader(handle)
    if reader.fieldnames is None:
        raise InputError("input trace must have a CSV header")
    headers = [header.strip() for header in reader.fieldnames]
    if len(headers) != len(set(headers)):
        raise InputError("input trace has duplicate CSV headers")
    required = {"arrival_time", "service_time"}
    missing = sorted(required - set(headers))
    if missing:
        raise InputError(f"input trace is missing required column(s): {', '.join(missing)}")
    reader.fieldnames = headers

    jobs: list[TraceJob] = []
    seen_ids: set[str] = set()
    previous_arrival: float | None = None
    for row_number, row in enumerate(reader, start=2):
        if None in row:
            raise InputError(f"row {row_number} has more values than the CSV header")
        if all(value is None or not value.strip() for value in row.values()):
            continue
        arrival = finite_nonnegative(row.get("arrival_time"), f"row {row_number} arrival_time")
        service = finite_nonnegative(row.get("service_time"), f"row {row_number} service_time")
        if previous_arrival is not None and arrival < previous_arrival:
            raise InputError(
                f"row {row_number} arrival_time is earlier than the preceding arrival; "
                "rows must be in nondecreasing arrival order"
            )
        previous_arrival = arrival
        raw_id = row.get("job_id")
        job_id = raw_id.strip() if raw_id and raw_id.strip() else str(len(jobs) + 1)
        if job_id in seen_ids:
            raise InputError(f"row {row_number} duplicates job_id {job_id!r}")
        seen_ids.add(job_id)
        jobs.append(TraceJob(job_id, arrival, service, len(jobs)))

    if not jobs:
        raise InputError("input trace must contain at least one job")
    return jobs


def empirical_quantile(values: Sequence[float], probability: float) -> float:
    """Return the type-7 linearly interpolated empirical quantile."""
    if not values:
        raise InputError("cannot compute a quantile of an empty sample")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return finite_derived(
        ordered[lower] + fraction * (ordered[upper] - ordered[lower]),
        f"p{int(probability * 100)} quantile",
    )


def finite_derived(value: float, field: str) -> float:
    """Reject overflow in a derived value before JSON serialization."""
    if not math.isfinite(value):
        raise InputError(f"derived {field} is not finite; rescale the trace time unit or reduce the horizon")
    return value


def finite_sum(values: Iterable[float], field: str) -> float:
    """Accurately sum finite values and reject aggregate overflow."""
    try:
        total = math.fsum(values)
    except OverflowError as exc:
        raise InputError(f"derived {field} is not finite; rescale the trace time unit or reduce the horizon") from exc
    return finite_derived(total, field)


def distribution_summary(values: Sequence[float]) -> dict[str, float]:
    return {
        "mean": finite_derived(finite_sum(values, "distribution total") / len(values), "distribution mean"),
        **{f"p{int(probability * 100)}": empirical_quantile(values, probability) for probability in QUANTILES},
        "max": max(values),
    }


def overlap(start: float, end: float, window_start: float, window_end: float) -> float:
    return max(0.0, min(end, window_end) - max(start, window_start))


def maximum_queue_length(results: Iterable[JobResult]) -> int:
    """Count jobs waiting after all starts and arrivals at each timestamp."""
    changes: dict[float, int] = {}
    for result in results:
        if result.waiting_time > 0:
            changes[result.arrival_time] = changes.get(result.arrival_time, 0) + 1
            changes[result.start_time] = changes.get(result.start_time, 0) - 1
    queued = 0
    maximum = 0
    for timestamp in sorted(changes):
        queued += changes[timestamp]
        maximum = max(maximum, queued)
    return maximum


def state_at(results: Iterable[JobResult], timestamp: float) -> dict[str, int]:
    """Return post-event queue state at a timestamp using half-open intervals."""
    result_list = list(results)
    waiting = sum(result.arrival_time <= timestamp < result.start_time for result in result_list)
    in_service = sum(result.start_time <= timestamp < result.completion_time for result in result_list)
    return {
        "queue_length_at_end": waiting,
        "in_service_at_end": in_service,
        "unfinished_jobs_at_end": waiting + in_service,
    }


def simulate(
    jobs: Sequence[TraceJob],
    servers: int,
    measurement_start: object | None = None,
    measurement_end: object | None = None,
    *,
    include_jobs: bool = True,
) -> dict[str, Any]:
    """Simulate an initially empty, nonpreemptive FCFS queue through completion."""
    positive_server_count(servers)
    if not jobs:
        raise InputError("input trace must contain at least one job")

    previous_arrival: float | None = None
    seen_ids: set[str] = set()
    validated: list[TraceJob] = []
    for index, job in enumerate(jobs):
        if not isinstance(job, TraceJob):
            raise InputError(f"job at index {index} must be a TraceJob")
        arrival = finite_nonnegative(job.arrival_time, f"job {index} arrival_time")
        service = finite_nonnegative(job.service_time, f"job {index} service_time")
        if previous_arrival is not None and arrival < previous_arrival:
            raise InputError("jobs must be in nondecreasing arrival order")
        previous_arrival = arrival
        if not isinstance(job.job_id, str) or not job.job_id:
            raise InputError(f"job at index {index} must have a nonempty string job_id")
        if job.job_id in seen_ids:
            raise InputError(f"duplicate job_id {job.job_id!r}")
        seen_ids.add(job.job_id)
        validated.append(TraceJob(job.job_id, arrival, service, index))

    available_servers = [(0.0, server_id) for server_id in range(servers)]
    heapq.heapify(available_servers)
    results: list[JobResult] = []
    for job in validated:
        available_time, server_id = heapq.heappop(available_servers)
        start_time = max(job.arrival_time, available_time)
        completion_time = finite_derived(start_time + job.service_time, f"completion_time for job {job.job_id!r}")
        result = JobResult(
            job_id=job.job_id,
            input_order=job.input_order,
            server_id=server_id,
            arrival_time=job.arrival_time,
            service_time=job.service_time,
            start_time=start_time,
            completion_time=completion_time,
            waiting_time=start_time - job.arrival_time,
            response_time=completion_time - job.arrival_time,
        )
        results.append(result)
        heapq.heappush(available_servers, (completion_time, server_id))

    default_start = validated[0].arrival_time
    default_end = max(result.completion_time for result in results)
    window_start = default_start if measurement_start is None else finite_nonnegative(measurement_start, "measurement_start")
    window_end = default_end if measurement_end is None else finite_nonnegative(measurement_end, "measurement_end")
    if window_end < window_start:
        raise InputError("measurement_end must be greater than or equal to measurement_start")

    duration = window_end - window_start
    busy_time = finite_sum(
        (
            overlap(result.start_time, result.completion_time, window_start, window_end)
            for result in results
        ),
        "busy_time",
    )
    capacity_time = finite_derived(servers * duration, "capacity_time")
    utilization = busy_time / capacity_time if capacity_time > 0 else None
    queue_time = finite_sum(
        (
            overlap(result.arrival_time, result.start_time, window_start, window_end)
            for result in results
        ),
        "queue_time_integral",
    )
    waits = [result.waiting_time for result in results]
    responses = [result.response_time for result in results]

    report: dict[str, Any] = {
        "schema_version": "1.0",
        "analysis_scope": "finite_trace",
        "model": {
            "discipline": "FCFS",
            "service": "nonpreemptive",
            "buffer": "unbounded",
            "initial_state": "empty",
            "server_capacity": servers,
            "pairing": "each input row keeps its observed arrival_time and service_time together",
            "tie_policy": (
                "input row order for simultaneous arrivals; earliest available server then lowest server_id; "
                "a server released at time t is available to an arrival at time t"
            ),
        },
        "measurement": {
            "start": window_start,
            "end": window_end,
            "duration": duration,
            "busy_time": busy_time,
            "capacity_time": capacity_time,
            "utilization": utilization,
            "queue_time_integral": queue_time,
            **state_at(results, window_end),
        },
        "summary": {
            "scope": "all trace jobs after the queue drains",
            "jobs": len(results),
            "jobs_waited": sum(wait > 0 for wait in waits),
            "max_queue_length": maximum_queue_length(results),
            "waiting_time": distribution_summary(waits),
            "response_time": distribution_summary(responses),
        },
        "inference": {
            "confidence_intervals": None,
            "steady_state_claim": False,
            "note": (
                "Results are empirical for this finite trace and initially empty queue. "
                "They do not estimate steady-state performance or sampling uncertainty."
            ),
        },
    }
    if include_jobs:
        report["jobs"] = [
            {
                "job_id": result.job_id,
                "input_order": result.input_order,
                "server_id": result.server_id,
                "arrival_time": result.arrival_time,
                "service_time": result.service_time,
                "start_time": result.start_time,
                "completion_time": result.completion_time,
                "waiting_time": result.waiting_time,
                "response_time": result.response_time,
            }
            for result in results
        ]
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate an initially empty FCFS multi-server queue from a finite CSV trace."
    )
    parser.add_argument("--input", required=True, type=Path, help="CSV with arrival_time and service_time columns")
    parser.add_argument("--servers", required=True, type=int, help="fixed number of identical servers")
    parser.add_argument("--measurement-start", type=float, help="utilization/backlog integral window start")
    parser.add_argument("--measurement-end", type=float, help="utilization/backlog integral window end")
    parser.add_argument("--output", type=Path, help="write JSON here instead of stdout")
    parser.add_argument("--summary-only", action="store_true", help="omit per-job records")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        jobs = load_trace(args.input)
        report = simulate(
            jobs,
            args.servers,
            args.measurement_start,
            args.measurement_end,
            include_jobs=not args.summary_only,
        )
        rendered = json.dumps(report, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (InputError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
