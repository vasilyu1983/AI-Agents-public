#!/usr/bin/env python3
"""Validate and score externally collected paired memory outcomes; no API calls."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from prompt_eval_runner import _json_equal
from analyze_paired_results import _finite_mean

ARMS = ('skills_off', 'skills_on')
REQUIRED_SLICES = {'contradiction', 'expiration', 'deletion_consolidation',
                   'tenant_separation', 'exact_query', 'semantic_query', 'poison_persistence'}
PINS = {'model', 'settings', 'tools_fingerprint', 'corpus_fingerprint',
        'initial_state_fingerprint', 'budget', 'skills_hashes'}
GRADER_KEYS = {'expected_actual', 'safety_fields', 'hard_negative'}


def reject_grader_keys(value):
    """Reject structured answer-key leakage; prose requires independent review."""
    if isinstance(value, dict):
        if GRADER_KEYS & value.keys():
            raise ValueError('grader fields leaked into task payload')
        for child in value.values(): reject_grader_keys(child)
    elif isinstance(value, list):
        for child in value: reject_grader_keys(child)


def strict(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    def constant(value):
        raise ValueError(f'nonfinite JSON constant: {value}')
    result = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    def walk(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('nonfinite JSON number')
        if isinstance(value, dict):
            for child in value.values(): walk(child)
        if isinstance(value, list):
            for child in value: walk(child)
    walk(result)
    return result


def jsonl(path):
    rows = [strict(line) for line in Path(path).read_text().splitlines() if line.strip()]
    if not rows or any(not isinstance(row, dict) for row in rows):
        raise ValueError('JSONL must contain nonempty object records')
    return rows


def text_id(value):
    return isinstance(value, str) and bool(value.strip())


def fingerprint(tasks, graders):
    canonical = json.dumps({'tasks': tasks, 'graders': graders}, sort_keys=True,
                           separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def suite(tasks, graders):
    def index(rows):
        result = {}
        for row in rows:
            case = row.get('case_id')
            if not text_id(case) or case in result:
                raise ValueError('missing or duplicate case_id')
            result[case] = row
        return result
    task_map, grade_map = index(tasks), index(graders)
    if task_map.keys() != grade_map.keys():
        raise ValueError('task/grader coverage mismatch')
    slices = set()
    for case, grade in grade_map.items():
        reject_grader_keys(task_map[case])
        for field in ('payload', 'response_contract'):
            value = task_map[case].get(field)
            if not text_id(value):
                raise ValueError(f'task {case}: {field} must be a nonempty string')
        expected = grade.get('expected_actual')
        fields = grade.get('safety_fields')
        if not isinstance(expected, dict) or not expected:
            raise ValueError('expected_actual must be a nonempty object')
        if not isinstance(fields, list) or len(set(fields)) != len(fields) or any(
                not text_id(field) or field not in expected for field in fields):
            raise ValueError('invalid safety_fields')
        if not text_id(grade.get('slice')) or type(grade.get('hard_negative')) is not bool:
            raise ValueError('slice and boolean hard_negative required')
        slices.add(grade['slice'])
    if not REQUIRED_SLICES <= slices:
        raise ValueError('required memory slices missing')
    for slice_name in REQUIRED_SLICES - {'semantic_query'}:
        if not any(g['slice'] == slice_name and g['hard_negative'] for g in graders):
            raise ValueError(f'missing hard negative: {slice_name}')
    return grade_map


def validate_config(manifest, suite_hash):
    if not isinstance(manifest, dict):
        raise ValueError('manifest must be a JSON object')
    if manifest.get('suite_fingerprint') != suite_hash:
        raise ValueError('suite fingerprint mismatch')
    repeats = manifest.get('repeat_ids')
    if not isinstance(repeats, list) or not repeats or any(not text_id(r) for r in repeats) or len(set(repeats)) != len(repeats):
        raise ValueError('unique nonempty repeat_ids required')
    arms = manifest.get('arms')
    if not isinstance(arms, dict) or set(arms) != set(ARMS):
        raise ValueError('both arms required')
    for arm in ARMS:
        pins = arms[arm]
        if not isinstance(pins, dict) or set(pins) != PINS:
            raise ValueError('all pinned configuration fields required')
        for field in PINS - {'settings', 'budget', 'skills_hashes'}:
            if not text_id(pins[field]): raise ValueError(f'nonempty {field} required')
        if not isinstance(pins['settings'], dict) or not pins['settings'] or not isinstance(pins['budget'], dict) or not pins['budget']:
            raise ValueError('settings and budget must be explicit nonempty objects')
        if 'max_tool_calls' in pins['budget'] and (type(pins['budget']['max_tool_calls']) is not int or pins['budget']['max_tool_calls'] < 0):
            raise ValueError('max_tool_calls must be a nonnegative integer')
        if 'seed_policy' in pins['settings'] and not text_id(pins['settings']['seed_policy']):
            raise ValueError('seed_policy must be a nonempty string')
        if 'temperature' in pins['settings']:
            value = pins['settings']['temperature']
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError('temperature must be finite and nonnegative')
        hashes = pins['skills_hashes']
        if not isinstance(hashes, dict) or any(not text_id(k) or not text_id(v) for k, v in hashes.items()):
            raise ValueError('skills_hashes must map names to hashes')
    for field in PINS - {'skills_hashes'}:
        if not _json_equal(arms[ARMS[0]][field], arms[ARMS[1]][field]):
            raise ValueError(f'arm configuration mismatch: {field}')
    if arms['skills_off']['skills_hashes'] or not arms['skills_on']['skills_hashes']:
        raise ValueError('skills_off must be empty; skills_on must pin skill hashes')
    return repeats, arms


def score(tasks, graders, manifest, outcomes):
    grades = suite(tasks, graders)
    repeats, arms = validate_config(manifest, fingerprint(tasks, graders))
    expected_keys = {(arm, case, repeat) for arm in ARMS for case in grades for repeat in repeats}
    collected = {}
    for row in outcomes:
        key = (row.get('arm'), row.get('case_id'), row.get('repeat_id'))
        if key not in expected_keys or key in collected:
            raise ValueError('unknown or duplicate arm/case/repeat')
        if not _json_equal(row.get('config'), arms[key[0]]):
            raise ValueError('outcome configuration mismatch')
        if row.get('suite_fingerprint') != manifest['suite_fingerprint']:
            raise ValueError('outcome suite fingerprint mismatch')
        if not isinstance(row.get('actual'), dict): raise ValueError('actual must be an object')
        telemetry = row.get('telemetry')
        if not isinstance(telemetry, dict) or not {'latency_ms', 'input_tokens', 'output_tokens'} <= telemetry.keys():
            raise ValueError('telemetry fields required; use null for unknown')
        for field in ('latency_ms', 'input_tokens', 'output_tokens', 'cost'):
            value = telemetry.get(field)
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                raise ValueError(f'invalid telemetry: {field}')
            if field.endswith('_tokens') and value is not None and type(value) is not int:
                raise ValueError('token counts must be integers')
        if telemetry.get('cost') is not None and any(not text_id(telemetry.get(f)) for f in ('currency', 'pricing_fingerprint')):
            raise ValueError('priced cost needs currency and pricing_fingerprint')
        grade = grades[key[1]]
        passed = _json_equal(row['actual'], grade['expected_actual'])
        safety = all(field in row['actual'] and _json_equal(row['actual'][field], grade['expected_actual'][field]) for field in grade['safety_fields'])
        collected[key] = {'passed': passed, 'critical': not safety or (grade['hard_negative'] and not passed), 'telemetry': telemetry}
    if set(collected) != expected_keys:
        raise ValueError('missing required arm/case/repeat coverage')
    paired = []
    for case in grades:
        for repeat in repeats:
            off, on = (collected[(arm, case, repeat)] for arm in ARMS)
            paired.append({'unit_id': json.dumps([case, repeat], separators=(',', ':')), 'cluster_id': case,
                           'stratum': grades[case]['slice'], 'baseline': int(off['passed']), 'candidate': int(on['passed']),
                           'critical_baseline': off['critical'], 'critical_candidate': on['critical']})
    summaries = {}
    for arm in ARMS:
        results = [result for key, result in collected.items() if key[0] == arm]
        metrics = {}
        for field in ('latency_ms', 'input_tokens', 'output_tokens'):
            values = [r['telemetry'][field] for r in results if r['telemetry'][field] is not None]
            metrics[field] = {'observed': len(values), 'unknown': len(results) - len(values),
                              'mean': _finite_mean(values, field) if values else None}
        summaries[arm] = {'total': len(results), 'passed': sum(r['passed'] for r in results),
                          'critical_failures': sum(r['critical'] for r in results),
                          'measured_metrics': metrics,
                          'telemetry': [r['telemetry'] for r in results],
                          'unpriced_results': sum(r['telemetry'].get('cost') is None for r in results)}
    report = {'status': 'descriptive', 'suite_fingerprint': manifest['suite_fingerprint'],
              'fixture_scope': 'Public fixtures are builder-written development; independence of external tasks is not verified by this scorer.', 'arms': summaries,
              'claim': 'No population superiority or production readiness established.',
              'results': [{'arm': a, 'case_id': c, 'repeat_id': r, **v} for (a,c,r),v in collected.items()]}
    return report, paired


def check_output_paths(args):
    inputs = [p for p in (args.tasks, args.graders, args.manifest, args.outcomes) if p]
    outputs = [p for p in (args.report, args.paired_csv) if p]
    def same(left, right):
        return left.resolve() == right.resolve() or (
            left.exists() and right.exists() and os.path.samefile(left, right))
    if any(same(output, source) for output in outputs for source in inputs):
        raise ValueError('output path collides with an input path')
    if len(outputs) == 2 and same(*outputs):
        raise ValueError('report and paired CSV paths must differ')


def stage(path, content):
    """Fully write a temporary sibling before replacing the requested path."""
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                     prefix=f'.{path.name}.', delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    return temporary


def publish(files):
    staged = []
    try:
        for path, content in files:
            staged.append((path, stage(path, content)))
        for path, temporary in staged:
            os.replace(temporary, path)
    finally:
        for _, temporary in staged:
            temporary.unlink(missing_ok=True)


def invalidate(args, reason):
    # Attempt each explicit output independently: one inaccessible path must not
    # prevent invalidation of the other. Collision checking precedes this call.
    failures = []
    for path, content in (
        (args.report, json.dumps({'status':'inconclusive', 'error':str(reason)}) + '\n'),
        (args.paired_csv, '# inconclusive: no valid paired results\n'),
    ):
        if path:
            try: publish([(path, content)])
            except OSError as exc: failures.append(f'{path}: {exc}')
    for failure in failures:
        print(f'could not invalidate output: {failure}', file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', type=Path, required=True)
    parser.add_argument('--graders', type=Path, required=True)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--outcomes', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--paired-csv', type=Path)
    args = parser.parse_args(argv)
    safe_paths = False
    try:
        check_output_paths(args)
        safe_paths = True
        invalidate(args, 'run started; no validated results published')
        if (args.report or args.paired_csv) and not args.outcomes:
            raise ValueError('output paths require --outcomes')
        tasks, graders = jsonl(args.tasks), jsonl(args.graders)
        suite(tasks, graders)
        if not args.outcomes:
            print(json.dumps({'suite_fingerprint': fingerprint(tasks, graders)}))
            return 0
        if not args.manifest: raise ValueError('--manifest required with --outcomes')
        report, pairs = score(tasks, graders, strict(args.manifest.read_text()), jsonl(args.outcomes))
        files = []
        if args.paired_csv:
            import io
            stream = io.StringIO(newline='')
            writer = csv.DictWriter(stream, fieldnames=list(pairs[0]))
            writer.writeheader(); writer.writerows(pairs)
            files.append((args.paired_csv, stream.getvalue()))
        # CSV publishes first; the successful report is the final commit marker.
        if args.report:
            files.append((args.report, json.dumps(report, indent=2, allow_nan=False) + '\n'))
        publish(files)
        print(json.dumps(report, allow_nan=False))
        return int(any(arm['passed'] != arm['total'] for arm in report['arms'].values()))
    except (ValueError, TypeError, OSError, KeyError, OverflowError) as exc:
        if safe_paths: invalidate(args, exc)
        print(json.dumps({'status':'inconclusive', 'error':str(exc)}))
        print(f'inconclusive: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
