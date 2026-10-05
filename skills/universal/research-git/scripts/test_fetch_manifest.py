"""Fetch completeness is observable with mocked GitHub; no network."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

class FetchTests(unittest.TestCase):
    def test_failed_assets_are_partial_and_never_empty_success(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);bins=p/'bin';bins.mkdir()
            gh=bins/'gh'
            gh.write_text('''#!/usr/bin/env python3
import json,sys
path=sys.argv[2]
if path == 'repos/example/repo':
 print(json.dumps(dict(license=dict(spdx_id='MIT'),stargazers_count=0,updated_at='2026-09-11',description='',default_branch='main',archived=False,fork=False)))
elif '/commits/' in path: print('abc123')
else: sys.exit(1)
''');gh.chmod(0o755)
            curl=bins/'curl';curl.write_text('#!/bin/sh\necho "{}"\n');curl.chmod(0o755)
            script=Path(__file__).with_name('fetch_repo_assets.sh')
            run=subprocess.run(['bash',str(script),'example/repo',str(p/'out'),'--kind','code'],
                               env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH']),capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            out=p/'out/example__repo'
            meta=json.loads((out/'_metadata.json').read_text())
            self.assertEqual(meta['fetch_status'],'partial')
            self.assertGreater(meta['unavailable_or_failed_paths'],0)
            self.assertFalse(list(out.rglob('*.part')))
            self.assertNotIn('✓ done',run.stdout)
            before=(out/'_metadata.json').read_bytes()
            (out/'retained.txt').write_text('old source file')
            repeat=subprocess.run(['bash',str(script),'example/repo',str(p/'out'),'--kind','code'],
                                  env=dict(os.environ,PATH=str(bins)+os.pathsep+os.environ['PATH']),capture_output=True,text=True)
            self.assertNotEqual(repeat.returncode,0)
            self.assertIn('nonempty',repeat.stderr)
            self.assertEqual((out/'_metadata.json').read_bytes(),before)
            self.assertEqual((out/'retained.txt').read_text(),'old source file')

if __name__=='__main__': unittest.main()
