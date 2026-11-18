"""Read-only closure binding and in-memory receipt-policy checks; no application runs."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/scratch/58d2a6adf1c3')
REPO = ROOT / '.worktree/Task-07-B22-transport-linux/NativeWeave'
HERE = ROOT / 'task07-runs/b22-transport-review'
RUN = ROOT / 'task07-runs/b22-transport-final-002'
EXECUTED = '9f4e1429f4f4d5fd51bfceafb0b02b9341858b31'
FINAL = '8736c72e07c009db89763215c5f67234045dd946'
FILES = ['tests/Verification.EndToEnd/transport_faults.py',
    'tests/Verification.EndToEnd/transport-faults.md', 'tests/Verification.EndToEnd/harness.py',
    'tests/Verification.EndToEnd/faults.py', 'tests/Reference.TaskService/run.py']
EXPECTED = ['slow-upload', 'slow-download-window', 'active-upload-shutdown']

def sha(value):
    if isinstance(value, Path):
        with value.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    return hashlib.sha256(value).hexdigest()

def source(commit, file):
    return subprocess.check_output(['git', '-C', str(REPO), 'show', commit + ':' + file])

def tree_function(tree, name):
    return next(x for x in tree.body if isinstance(x, (ast.FunctionDef, ast.ClassDef)) and x.name == name)

old = ast.parse(source(EXECUTED, FILES[0]))
new = ast.parse(source(FINAL, FILES[0]))
assert ast.dump(tree_function(old, 'Transports')) == ast.dump(tree_function(new, 'Transports'))
assert ast.dump(tree_function(old, 'process_snapshot')) == ast.dump(tree_function(new, 'process_snapshot'))
main = tree_function(new, 'main')
finalizer = next(x.finalbody for x in main.body if isinstance(x, ast.Try) and x.finalbody)
code = compile(ast.fix_missing_locations(ast.Module(body=finalizer, type_ignores=[])), str(REPO / FILES[0]), 'exec')

class Timeline:
    def __init__(self): self.closed = False
    def close(self): self.closed = True

class Evidence:
    def __init__(self, record, fail=False):
        self.record = record; self.writes = []; self.timeline = Timeline(); self.fail = fail
    def save(self):
        if self.fail: raise OSError('simulated publication failure')
        self.writes.append(copy.deepcopy(self.record))

full = {'status': 'running', 'cases': [{'id': name, 'status': 'passed'} for name in EXPECTED], 'artifactsUnchanged': True}
policies = []
variants = [('complete', full, 0, 'passed'),
    ('partial', dict(full, cases=full['cases'][:2]), 0, 'incomplete'),
    ('empty', dict(full, cases=[]), 0, 'incomplete'),
    ('artifact-changed', dict(full, artifactsUnchanged=False), 0, 'incomplete'),
    ('artifact-unchecked', {key: value for key, value in full.items() if key != 'artifactsUnchanged'}, 0, 'incomplete'),
    ('case-failed', dict(full, cases=[{'id': name, 'status': 'failed' if index == 1 else 'passed'} for index, name in enumerate(EXPECTED)]), 1, 'incomplete'),
    ('outer-failure', dict(full, outerFailure={'type': 'AssertionError', 'interrupted': False}), 1, 'incomplete'),
    ('interrupted', dict(full, outerFailure={'type': 'KeyboardInterrupt', 'interrupted': True}), 1, 'incomplete'),
    ('case-order-wrong', dict(full, cases=list(reversed(full['cases']))), 0, 'incomplete')]
for name, record, exit_code, expected in variants:
    evidence = Evidence(copy.deepcopy(record))
    exec(code, {'evidence': evidence, 'expected_cases': EXPECTED, 'exit_code': exit_code})
    assert evidence.timeline.closed and len(evidence.writes) == 1 and evidence.writes[0]['status'] == expected
    policies.append({'id': name, 'status': 'passed', 'published_status': expected, 'publication_calls': 1, 'timeline_closed': True})
evidence = Evidence(copy.deepcopy(full), fail=True)
try:
    exec(code, {'evidence': evidence, 'expected_cases': EXPECTED, 'exit_code': 0})
    raise AssertionError('Publication failure was unexpectedly swallowed')
except OSError:
    assert not evidence.writes and evidence.timeline.closed
    policies.append({'id': 'publication-failure', 'status': 'passed', 'published_status': None, 'publication_calls_succeeded': 0, 'timeline_closed': True})

rows = []
progress = json.loads((RUN / 'progress.json').read_text())
for launch in progress:
    path = RUN / launch['row'] / 'receipt.json'
    record = json.loads(path.read_text()); identity = record['identity']
    assert launch['exit_code'] == 0 and launch['status'] == record['status'] == 'passed'
    assert [case['id'] for case in record['cases']] == EXPECTED == record['requiredCases']
    assert record['artifactsUnchanged'] is True and 'outerFailure' not in record
    assert identity['controllerSha256'] == sha(source(EXECUTED, FILES[0]))
    assert identity['harnessSha256'] == sha(source(EXECUTED, FILES[2]))
    assert identity['faultHelperSha256'] == sha(source(EXECUTED, FILES[3]))
    assertions = [item for case in record['cases'] for item in case['assertions']]
    assert len(assertions) == 22 and all(item['status'] == 'passed' for item in assertions)
    held = next(item['observations'] for item in assertions if item['id'] == 'slow-download-withheld-credit-observed')
    assert held == {'bytesBeforeHold': 4096, 'bytesAfterHold': 4096, 'heldFlowControlledBytes': 4096}
    timeline_path = path.parent / 'timeline.jsonl'
    timeline = [json.loads(line) for line in timeline_path.read_text().splitlines()]
    hold = next(item for item in timeline if item['event'] == 'receive-window-withheld')
    assert hold['socketReadDuringHold'] is True and hold['seconds'] >= 2.2
    artifact = Path(launch['argv'][launch['argv'].index('--artifact-directory') + 1])
    actual = {str(file.relative_to(artifact)): sha(file) for file in artifact.rglob('*') if file.is_file()}
    assert actual == identity['artifacts']
    logs = list(path.parent.glob('*/service/service.log')) + list(path.parent.glob('*/restarted-service/service.log'))
    witness = 'B21_RUNTIME dynamic=' + ('True' if identity['mode'] == 'jit' else 'False')
    assert len(logs) == 4 and all(witness in log.read_text() for log in logs)
    rows.append({'id': launch['row'], 'status': 'passed', 'assertions': len(assertions),
        'receipt': str(path), 'receipt_sha256': sha(path), 'timeline_sha256': sha(timeline_path),
        'runtime_witness': witness, 'held_flow_controlled_bytes': held['heldFlowControlledBytes'],
        'hold_seconds': hold['seconds'], 'artifacts_equal_current_immutable_files': True,
        'executable_sha256': identity['executableSha256'], 'source_controller_sha256': identity['controllerSha256'],
        'strict_finalizer_applicability': 'Exact required case IDs, every case/assertion passed, exit0, unchanged artifacts, no outer failure; final status unchanged under 8736c72 predicates.'})

base = json.loads((HERE / 'baseline-review.json').read_text())
review = copy.deepcopy(base)
review.update(reviewed_commit=FINAL, executed_commit=EXECUTED,
    reviewed_file_sha256={file: sha(source(FINAL, file)) for file in FILES},
    executed_file_sha256={file: sha(source(EXECUTED, file)) for file in FILES},
    verdict='No open concrete findings in the requested transport/controller scope.',
    actual_run_rows=rows, actual_assertions=sum(row['assertions'] for row in rows),
    receipt_policy_checks={'scope': 'Exact current main.finally AST executed only against in-memory record/save doubles; no product, network, database, workload or timing run.', 'cases': policies},
    applicability={'network_case_ast_equal': True, 'process_snapshot_ast_equal': True,
        'explanation': '9f4e142 executed the corrected transport/data assertions. 8736c72 changes final receipt publication only. The successful immutable rows satisfy its stricter finalizer without rerunning or relabelling binaries.'},
    closure_script_sha256=sha(Path(__file__)))
closures = {
    'B22-TRANSPORT-T1': '9f4e142 reads/parses socket frames during hold without acknowledging DATA, limits cumulative flow-controlled bytes including padding to 4096, and rejects end/reset. All four actual rows retain 4096 bytes before/after >2.2s holds and exact full delivery afterward.',
    'B22-TRANSPORT-T2': '9f4e142 checks canonical operation UUID, responseVersion1, same item, deterministic SHA256, length and version2, plus independent SQL replay tuple (1,200,actual returned body). All four actual rows pass.',
    'B22-TRANSPORT-T3': '9f4e142 adds exact named cases, exit0 and unchanged artifacts. 8736c72 removes the intermediate Evidence.close publication and performs one atomic final save after strict predicates. Nine in-memory policy variants and a publication-failure path pass. Existing four actual successful rows meet all predicates.'}
for finding in review['findings']:
    finding['status'] = 'closed'; finding['closure'] = closures[finding['id']]
(HERE / 'review.json').write_text(json.dumps(review, indent=2, sort_keys=True) + '\n')
lines = ['# B22 transport controller independent review', '',
    'Reviewer: `/root/b21_service`; not an author of the reviewed transport controller.', '',
    f'Final reviewed commit: `{FINAL}`. Actual network/data executions: `{EXECUTED}`.', '',
    '**Verdict: all three concrete findings closed.** No remaining blocker was found within the requested transport cases and their directly used helper scope.', '',
    '## Closure', '']
for finding in review['findings']:
    lines += [f"- **{finding['id']}** — {finding['closure']}"]
lines += ['', '## Actual retained observations', '',
    '| Row | Assertions | Held flow-controlled bytes | Hold seconds | Status |',
    '| --- | ---: | ---: | ---: | --- |']
for row in rows:
    lines += [f"| {row['id']} | {row['assertions']} | {row['held_flow_controlled_bytes']} | {row['hold_seconds']:.6f} | passed |"]
lines += ['', 'The four rows contain the exact three required cases and 88 passed assertions. Artifact hashes were independently re-read and remain identical. Each row has the expected actual JIT/AOT witness. The exact executable, controller, receipt and timeline hashes are retained in `review.json`.', '',
    'The final receipt-only correction does not change any transport case or process-snapshot AST. Existing successful rows meet every current strict finalization predicate. They remain attributed to their actual executed controller; no application or network cases were rerun and no old binaries were relabelled.', '',
    'The small policy check extracts the actual current `main.finally` AST and exercises in-memory completion, partial, empty, artifact-change/unverified, failed, interrupted, order-mismatch and publication-failure records. It verifies one final publication and timeline closure. This is controller policy evidence only.', '',
    '## Limits', '',
    'This review does not establish aggregate managed-root/native-owner accounting, all B22 fault correctness, performance, or any 30-minute/24-hour/72-hour duration. Those claims remain explicitly absent. It does not re-audit the full inherited fault corpus.', '',
    '## Reviewed file hashes', '', '| File | SHA-256 |', '| --- | --- |']
for file, digest in review['reviewed_file_sha256'].items(): lines += [f'| `{file}` | `{digest}` |']
(HERE / 'review.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({'verdict': review['verdict'], 'actual_rows': len(rows), 'actual_assertions': review['actual_assertions'],
    'policy_checks': len(policies), 'review_json_sha256': sha(HERE / 'review.json'), 'review_md_sha256': sha(HERE / 'review.md')}, indent=2))
