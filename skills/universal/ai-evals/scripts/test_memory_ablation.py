#!/usr/bin/env python3
"""Synthetic DEVELOPMENT observations test the validator, never agent quality."""
import copy
import csv
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from analyze_paired_results import load_rows
from memory_ablation import fingerprint, jsonl, main, score, strict, suite

BASE = Path(__file__).resolve().parent


class MemoryAblationTests(unittest.TestCase):
    def setUp(self):
        self.tasks = jsonl(BASE / 'fixtures/memory-development-tasks.jsonl')
        self.graders = jsonl(BASE / 'fixtures/memory-development-graders.jsonl')
        pins = {'model':'test-model', 'settings':{'seed':1}, 'tools_fingerprint':'tools',
                'corpus_fingerprint':'corpus', 'initial_state_fingerprint':'state',
                'budget':{'calls':10}, 'skills_hashes':{}}
        candidate = copy.deepcopy(pins)
        candidate['skills_hashes'] = {'memory-skill':'hash'}
        self.manifest = {'suite_fingerprint':fingerprint(self.tasks,self.graders),
                         'repeat_ids':['r1','r2'], 'arms':{'skills_off':pins,'skills_on':candidate}}
        self.outcomes = []
        # Test-only planted outcomes generated from keys calibrate deterministic grading.
        # They are never committed as measured agent observations.
        for arm, config in self.manifest['arms'].items():
            for grade in self.graders:
                for repeat in self.manifest['repeat_ids']:
                    self.outcomes.append({'arm':arm,'case_id':grade['case_id'],'repeat_id':repeat,
                        'suite_fingerprint':self.manifest['suite_fingerprint'], 'config':copy.deepcopy(config),
                        'actual':copy.deepcopy(grade['expected_actual']),
                        'telemetry':{'latency_ms':None,'input_tokens':None,'output_tokens':None}})

    def run_score(self):
        return score(self.tasks,self.graders,self.manifest,self.outcomes)

    def test_complete_pair_and_existing_analyzer_export(self):
        report, pairs = self.run_score()
        self.assertEqual(report['arms']['skills_off']['unpriced_results'],14)
        self.assertEqual(len(pairs),14)
        self.assertEqual(len({p['cluster_id'] for p in pairs}),7)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'paired.csv'
            with path.open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(pairs[0])); writer.writeheader(); writer.writerows(pairs)
            self.assertEqual(len(load_rows(path)),14)

    def test_planted_bad_is_failure_without_baked_winner(self):
        for arm in ('skills_off','skills_on'):
            with self.subTest(arm=arm):
                original=copy.deepcopy(self.outcomes)
                row=next(r for r in self.outcomes if r['arm']==arm)
                row['actual']['value']='French'
                report,pairs=self.run_score()
                self.assertEqual(report['arms'][arm]['critical_failures'],1)
                self.assertEqual(report['arms'][arm]['passed'],13)
                self.outcomes=original

    def test_missing_pair_blocks(self):
        self.outcomes.pop()
        with self.assertRaises(ValueError): self.run_score()

    def test_telemetry_means_use_only_observed_values(self):
        self.outcomes[0]['telemetry'].update(latency_ms=12, input_tokens=100, output_tokens=5)
        self.outcomes[1]['telemetry'].update(latency_ms=20, input_tokens=200, output_tokens=7)
        report, _ = self.run_score()
        metrics = report['arms']['skills_off']['measured_metrics']
        self.assertEqual(metrics['latency_ms'], {'observed':2, 'unknown':12, 'mean':16})
        self.assertEqual(metrics['input_tokens']['mean'],150)
        self.assertIsNone(report['arms']['skills_on']['measured_metrics']['latency_ms']['mean'])

    def test_duplicate_pair_blocks(self):
        self.outcomes.append(copy.deepcopy(self.outcomes[0]))
        with self.assertRaises(ValueError): self.run_score()

    def test_pin_mismatch_blocks(self):
        self.outcomes[0]['config']['model']='different'
        with self.assertRaises(ValueError): self.run_score()

    def test_arm_budget_mismatch_blocks(self):
        self.manifest['arms']['skills_on']['budget']['calls']=20
        with self.assertRaises(ValueError): self.run_score()

    def test_suite_hash_mismatch_blocks(self):
        self.outcomes[0]['suite_fingerprint']='wrong'
        with self.assertRaises(ValueError): self.run_score()

    def test_metrics_fail_closed(self):
        for field,value in [('latency_ms',float('nan')),('latency_ms',float('inf')),
                            ('input_tokens',True),('output_tokens',1.5),('latency_ms',-1),('cost','cheap')]:
            with self.subTest(field=field,value=value):
                self.outcomes[0]['telemetry']={field:value,'latency_ms':None,'input_tokens':None,'output_tokens':None}
                self.outcomes[0]['telemetry'][field]=value
                with self.assertRaises(ValueError): self.run_score()

    def test_cost_needs_provenance(self):
        self.outcomes[0]['telemetry']['cost']=0.001
        with self.assertRaises(ValueError): self.run_score()
        self.outcomes[0]['telemetry'].update(currency='USD',pricing_fingerprint='user-supplied-table-hash')
        report,_=self.run_score()
        self.assertEqual(report['arms']['skills_off']['unpriced_results'],13)

    def test_omitted_hard_negative_blocks(self):
        self.graders[0]['hard_negative']=False
        with self.assertRaises(ValueError): suite(self.tasks,self.graders)

    def test_missing_category_blocks(self):
        with self.assertRaises(ValueError): suite(self.tasks[:-1],self.graders[:-1])

    def test_answer_keys_in_payload_fields_block(self):
        self.tasks[0]['expected_actual']={}
        with self.assertRaises(ValueError): suite(self.tasks,self.graders)

    def test_nested_grader_fields_block(self):
        for field in ('expected_actual','safety_fields','hard_negative'):
            for target in ('payload','response_contract'):
                with self.subTest(field=field,target=target):
                    tasks=copy.deepcopy(self.tasks)
                    tasks[0][target]={'nested':[{'deep':{field:{}}}]}
                    with self.assertRaises(ValueError): suite(tasks,self.graders)

    def test_missing_or_malformed_task_inputs_block(self):
        for field in ('payload', 'response_contract'):
            for value in (None, '', '   ', {}, [], True):
                with self.subTest(field=field,value=value):
                    tasks=copy.deepcopy(self.tasks)
                    tasks[0][field]=value
                    with self.assertRaises(ValueError): suite(tasks,self.graders)
            tasks=copy.deepcopy(self.tasks)
            tasks[0].pop(field)
            with self.assertRaises(ValueError): suite(tasks,self.graders)

    def cli_files(self, directory):
        base=Path(directory)
        for filename,rows in [('tasks.jsonl',self.tasks),('graders.jsonl',self.graders),('outcomes.jsonl',self.outcomes)]:
            (base/filename).write_text(''.join(json.dumps(row)+'\n' for row in rows))
        (base/'manifest.json').write_text(json.dumps(self.manifest))
        return ['--tasks',str(base/'tasks.jsonl'),'--graders',str(base/'graders.jsonl'),
                '--manifest',str(base/'manifest.json'),'--outcomes',str(base/'outcomes.jsonl'),
                '--report',str(base/'report.json'),'--paired-csv',str(base/'paired.csv')]

    def test_failed_rerun_invalidates_success(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            args=self.cli_files(directory)
            self.assertEqual(main(args),0)
            self.assertEqual(json.loads((Path(directory)/'report.json').read_text())['status'],'descriptive')
            (Path(directory)/'outcomes.jsonl').write_text('{broken')
            self.assertEqual(main(args),2)
            self.assertEqual(json.loads((Path(directory)/'report.json').read_text())['status'],'inconclusive')
            with self.assertRaises(ValueError): load_rows(Path(directory)/'paired.csv')

    def test_nonobject_manifest_cli_is_inconclusive_without_traceback(self):
        for value in ([], None, 'bad manifest'):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                args=self.cli_files(directory)
                stdout,stderr=io.StringIO(),io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    self.assertEqual(main(args),0)
                    (Path(directory)/'manifest.json').write_text(json.dumps(value))
                    self.assertEqual(main(args),2)
                self.assertNotIn('Traceback',stderr.getvalue())
                self.assertIn('manifest must be a JSON object',stderr.getvalue())
                self.assertEqual(json.loads((Path(directory)/'report.json').read_text())['status'],'inconclusive')
                with self.assertRaises(ValueError): load_rows(Path(directory)/'paired.csv')

    def test_collisions_preserve_input_bytes(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            args=self.cli_files(directory)
            original=(Path(directory)/'tasks.jsonl').read_bytes()
            args[args.index('--report')+1]=args[args.index('--tasks')+1]
            self.assertEqual(main(args),2)
            self.assertEqual((Path(directory)/'tasks.jsonl').read_bytes(),original)
            args=self.cli_files(directory)
            args[args.index('--paired-csv')+1]=args[args.index('--report')+1]
            self.assertEqual(main(args),2)
            self.assertFalse((Path(directory)/'report.json').exists())

    def test_partial_output_publish_invalidates_both(self):
        import memory_ablation
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            args=self.cli_files(directory)
            self.assertEqual(main(args),0)
            real_replace=memory_ablation.os.replace
            def fail_success_report(source,target):
                if Path(target).name=='report.json' and '"status": "descriptive"' in Path(source).read_text():
                    raise OSError('planted publication failure')
                return real_replace(source,target)
            with patch('memory_ablation.os.replace',side_effect=fail_success_report):
                self.assertEqual(main(args),2)
            self.assertEqual(json.loads((Path(directory)/'report.json').read_text())['status'],'inconclusive')
            with self.assertRaises(ValueError): load_rows(Path(directory)/'paired.csv')
            self.assertEqual(list(Path(directory).glob('.report.json.*')),[])
            self.assertEqual(list(Path(directory).glob('.paired.csv.*')),[])

    def test_staging_failure_invalidates_report(self):
        import memory_ablation
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            args=self.cli_files(directory)
            self.assertEqual(main(args),0)
            original_stage=memory_ablation.stage
            def fail_csv(path,content):
                if path.name=='paired.csv' and content.startswith('unit_id'):
                    raise OSError('planted staging failure')
                return original_stage(path,content)
            with patch('memory_ablation.stage',side_effect=fail_csv):
                self.assertEqual(main(args),2)
            self.assertEqual(json.loads((Path(directory)/'report.json').read_text())['status'],'inconclusive')
            with self.assertRaises(ValueError): load_rows(Path(directory)/'paired.csv')

    def test_declared_control_values_fail_closed(self):
        for section,field,value in [('budget','max_tool_calls',-1),('budget','max_tool_calls',True),
                                    ('settings','temperature',None),('settings','seed_policy','')]:
            with self.subTest(section=section,field=field):
                saved=copy.deepcopy(self.manifest)
                for config in self.manifest['arms'].values(): config[section][field]=value
                with self.assertRaises(ValueError): self.run_score()
                self.manifest=saved

    def test_json_malformed_duplicates_nonfinite_block(self):
        for raw in ['{','{"x":1,"x":2}','{"x":NaN}','{"x":1e999}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError): strict(raw)

    def test_missing_telemetry_blocks(self):
        self.outcomes[0]['telemetry'].pop('input_tokens')
        with self.assertRaises(ValueError): self.run_score()

    def test_extra_output_and_json_boolean_not_number(self):
        self.outcomes[0]['actual']['unexpected']=True
        report,_=self.run_score()
        self.assertEqual(report['arms']['skills_off']['passed'],13)
        poison=next(r for r in self.outcomes if r['case_id']=='poison_persistence-dev-1')
        poison['actual']['export_executed']=0
        report,_=self.run_score()
        self.assertEqual(report['arms']['skills_off']['critical_failures'],2)


if __name__ == '__main__': unittest.main()
