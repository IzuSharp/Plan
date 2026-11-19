"""Finite source-extracted argv/hash/fresh-path checks; never invoke a workload."""
import ast
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parents[1]
source = EVIDENCE / 'run_codec_before_resume_002.py'
document = EVIDENCE / 'codec-before-resume-002.json'
original_path = EVIDENCE / 'codec-before004-r241-long-commands.json'
freeze_path = EVIDENCE / 'frozen-execution.json'
pins = {
    source: 'dac0016659b6352bb0e2c93c80fb8ad276507c113a635a72b3250c12cb01f131',
    document: '225c9295a102de22a59e2bea01f2bb3f3abecbea98313f5b7c157322916a9e12',
    original_path: 'cd7c7eafe989b1b3aada00d6cf5ab7732f331a75ddde3618844b82b05e0711e7',
    freeze_path: '85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3'}
checks = []

def check(name, value):
    if not value:
        raise AssertionError(name)
    checks.append({'name': name, 'passed': True})

for path, expected in pins.items():
    check('actual-hash-' + path.name, hashlib.sha256(path.read_bytes()).hexdigest() == expected)
old = json.loads(original_path.read_text())
new = json.loads(document.read_text())
tree = ast.parse(source.read_text(), filename=str(source))
names = {'require', 'digest', 'read_json', 'checked', 'fresh', 'derived_commands'}
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
check('extract-only-six-pure-boundary-functions', {node.name for node in functions} == names)
namespace = {'copy': copy, 'os': os, 'Path': Path, 'hashlib': hashlib, 'json': json,
             'OUTPUT': Path(new['output']), 'VERIFICATION': Path(new['verification_receipt'])}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), namespace)
check('complete-command-objects-exact-allowed-transform', namespace['derived_commands'](old) == new['commands'])
differences = []
for index, (before, after) in enumerate(zip(old['commands'], new['commands'])):
    a, b = before['argv'], after['argv']
    expected = {a.index('--output') + 1: new['output']}
    if index == 1:
        expected[a.index('--receipt') + 1] = new['verification_receipt']
    diff = [{'index': i, 'before': x, 'after': y} for i, (x, y) in enumerate(zip(a, b)) if x != y]
    check('only-path-argv-changes-' + before['kind'], len(a) == len(b) and {r['index']: r['after'] for r in diff} == expected)
    differences.append({'kind': before['kind'], 'argv_length': len(a), 'differences': diff})
for name in ('configuration', 'selection', 'expected_result_checks'):
    check('unchanged-' + name, old[name] == new['unchanged_' + name])
check('original-measurement-flock-prefix-unchanged', new['commands'][0]['argv'][:3] == old['commands'][0]['argv'][:3]
      == ['/usr/bin/flock', '--nonblock', new['timing_lock']])
check('verifier-has-no-second-flock-argv', new['commands'][1]['argv'][0:3] == ['taskset', '-c', '8'])

def refused(name, callback):
    try:
        callback()
    except ValueError:
        checks.append({'name': name, 'passed': True})
    else:
        raise AssertionError(name)

bad = copy.deepcopy(old); bad['commands'][0]['argv'].extend(['--output', 'unexpected'])
refused('duplicate-output-rejected', lambda: namespace['derived_commands'](bad))
bad = copy.deepcopy(old); bad['commands'][1]['argv'].extend(['--receipt', 'unexpected'])
refused('duplicate-receipt-rejected', lambda: namespace['derived_commands'](bad))
with tempfile.TemporaryDirectory(prefix='finite-boundary-', dir=HERE) as temporary:
    base = Path(temporary)
    namespace['fresh'](base / 'missing')
    check('fresh-missing-path-accepted', True)
    file = base / 'present.json'; file.write_text('{"value": 1}\n')
    directory = base / 'present-directory'; directory.mkdir()
    link = base / 'dangling'; link.symlink_to(base / 'missing-target')
    for label, path in [('file', file), ('directory', directory), ('dangling-symlink', link)]:
        refused('fresh-existing-' + label + '-rejected', lambda path=path: namespace['fresh'](path))
    reference = {'path': str(file), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()}
    check('matching-hash-json-read', namespace['checked'](reference) == {'value': 1})
    file.write_text('{"value": 2}\n')
    refused('changed-hash-rejected', lambda: namespace['checked'](reference))
result = {'task': 'Perf-01', 'scope': 'Finite argv/hash/fresh-output boundaries only; no supervisor main, driver, subprocess, service, build or load executed',
          'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'inputs': {str(p): {'sha256': h, 'bytes': p.stat().st_size} for p, h in pins.items()},
          'checks': checks, 'passed_checks': len(checks), 'argv_differences': differences,
          'formal_duration_credit_seconds': 0, 'supervisor_preflight_execution': 'not executed'}
with (HERE / 'analysis.json').open('x') as stream:
    json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
print(json.dumps({'passed_checks': len(checks), 'argv_differences': differences, 'formal_duration_credit_seconds': 0}))
