"""Offline regression checks for the executable examples in references/."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECIPE = Path(os.environ.get('SWARM_RECIPE', ROOT / 'references/recipe-wave-dispatch.md'))
WORKFLOW = Path(os.environ.get('SWARM_WORKFLOW', ROOT / 'references/scripted-workflows.md'))


class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'tasks').mkdir()
        (self.root / 'outputs').mkdir()
        blocks = re.findall(r'```bash\n(.*?)\n```', RECIPE.read_text(), re.S)
        for name in ('worker', 'synthesizer', 'orchestrator'):
            block = next(b for b in blocks if b.startswith('#!/usr/bin/env bash\n# ' + name + '.sh'))
            # Relocate the original fixed-path recipe too, so baseline failures test behavior.
            block = block.replace('/tmp/wave-demo', str(self.root))
            (self.root / (name + '.sh')).write_text(block)
        for n in range(1, 4):
            (self.root / 'tasks' / f'task-{n}.txt').write_text(f'synthetic payload {n}\n')

    def run_script(self, name, *args):
        return subprocess.run(['bash', str(self.root / (name + '.sh')), *map(str, args)],
                              capture_output=True, text=True, timeout=10)

    def test_complete_wave(self):
        result = self.run_script('orchestrator', self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        for n in range(1, 4):
            self.assertIn(f'Worker task-{n} processed: synthetic payload {n}', result.stdout)

    def test_incomplete_inventory_rejected(self):
        (self.root / 'tasks/task-3.txt').unlink()
        result = self.run_script('orchestrator', self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('SYNTHESIS RESULT', result.stdout)

    def test_zero_exit_worker_without_artifacts_rejected(self):
        (self.root / 'worker.sh').write_text('#!/usr/bin/env bash\nexit 0\n')
        # These artifacts belong to an earlier run and cannot prove completion.
        for n in range(1, 4):
            (self.root / 'outputs' / f'task-{n}.txt').write_text('stale output\n')
        result = self.run_script('orchestrator', self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('SYNTHESIS RESULT', result.stdout)

    def test_worker_failure_rejected(self):
        (self.root / 'worker.sh').write_text('#!/usr/bin/env bash\nexit 7\n')
        result = self.run_script('orchestrator', self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('SYNTHESIS RESULT', result.stdout)

    def test_synthesizer_empty_inventory_rejected(self):
        result = self.run_script('synthesizer', self.root / 'outputs')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_synthesizer_empty_artifact_rejected(self):
        for n in range(1, 4):
            (self.root / 'outputs' / f'task-{n}.txt').write_text('ok\n' if n != 3 else '')
        result = self.run_script('synthesizer', self.root / 'outputs')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')


class WorkflowTests(unittest.TestCase):
    def run_workflow(self, mode):
        if not shutil.which('node'):
            self.fail('node is required to execute the documented JavaScript loop')
        blocks = re.findall(r'```(?:text|javascript)\n(.*?)\n```', WORKFLOW.read_text(), re.S)
        code = next(b for b in blocks if b.startswith('const seen = new Set()'))
        # Stand in only for runtime primitives; the loop itself is extracted unchanged.
        prefix = '''
const FINDERS = [{prompt: 'find'}], FINDINGS = {}, VERDICT = {};
const HARD_CAP = 3, key = f => f.desc;
let calls = 0;
const parallel = thunks => Promise.all(thunks.map(t => t()));
const agent = async prompt => {
  calls++;
  if (MODE === 'missing') return null;
  if (MODE === 'dry') return {findings: []};
  return prompt.startsWith('Refute:') ? {refuted: false} : {findings: [{desc: String(calls)}]};
};
'''.replace('MODE', repr(mode))
        wrapped = prefix + '\n(async () => {\n' + code + '\n})().then(() => console.log("ok"))' + \
            '.catch(e => {console.error(e.message); process.exitCode = 1;});'
        return subprocess.run(['node', '-e', wrapped], capture_output=True, text=True, timeout=10)

    def test_successful_dry_rounds_converge(self):
        result = self.run_workflow('dry')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_finder_is_incomplete(self):
        result = self.run_workflow('missing')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('incomplete finder wave', result.stderr)

    def test_novel_rounds_hit_cap(self):
        result = self.run_workflow('novel')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('round cap reached', result.stderr)


if __name__ == '__main__':
    unittest.main()
