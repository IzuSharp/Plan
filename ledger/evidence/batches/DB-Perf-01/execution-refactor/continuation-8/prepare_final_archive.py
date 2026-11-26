from pathlib import Path
import hashlib
import json
import re

recovery = Path('/workspace/scratch/166b48a091b9/recovery')
measurements = Path('/workspace/scratch/fd78534029f7/measurements')
prior = Path('/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/pre-final-evidence-01')
target = recovery / 'final-evidence-inputs-01.json'
assert not target.exists(), 'Use a fresh inventory; never overwrite evidence'
sha_pattern = re.compile(r'[0-9a-f]{64}\Z')
inputs, origins, explicit = {}, [], []

def add(path, digest):
    path = str(path)
    assert Path(path).is_absolute() and '..' not in Path(path).parts, path
    assert isinstance(digest, str) and sha_pattern.fullmatch(digest), path
    assert path not in inputs or inputs[path] == digest, 'Conflicting identity: ' + path
    inputs[path] = digest

def pin(path, expected=None):
    path = Path(path)
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert expected is None or digest == expected, 'Document changed: ' + str(path)
    add(path, digest)
    return data, digest

def inventory_document(path, shape, expected=None):
    raw, digest = pin(path, expected)
    document = json.loads(raw)
    source = document['inputFiles']
    if shape == 'object':
        assert isinstance(source, dict) and source
        entries = source.items()
    else:
        assert shape == 'identity-array' and isinstance(source, list) and source
        assert len({x['path'] for x in source}) == len(source)
        assert all(x['storedSha256'] == x['contentSha256'] for x in source)
        entries = [(x['path'], x['storedSha256']) for x in source]
    for original, digest_value in entries:
        add(original, digest_value)
    origins.append({'path': str(path), 'sha256': digest, 'field': '/inputFiles',
                    'shape': shape, 'entries': len(source)})
    return document

freeze_sha = 'fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a'
freeze = inventory_document(measurements / 'final-freeze-01.json', 'object', freeze_sha)
assert freeze['status'] == 'frozen' and len(freeze['inputFiles']) == 373

audit = inventory_document(recovery / 'final-identity-audit-01.json', 'object')
assert audit['status'] == 'passed' and audit['inputsUnchanged'] is True
assert len(audit['segments']) == 4 and audit['freeze']['sha256'] == freeze_sha
analysis_path = recovery / 'final-analysis-01.json'
assert audit['arithmeticReport']['path'] == str(analysis_path)
analysis = inventory_document(analysis_path, 'identity-array', audit['arithmeticReport']['sha256'])
assert analysis['inputsChangedDuringAnalysis'] == []
assert analysis['finalFour']['fourCompleteRawReceipts'] is True
assert analysis['finalFour']['sameHostAndSerialIncludingRecordedIdle'] is True
assert analysis['index']['path'] == str(recovery / 'final-index-01.json')
pin(recovery / 'final-index-01.json', analysis['index']['storedSha256'])

supervisor = json.loads((recovery / 'campaign-supervisor-01.json').read_text())
assert [x['provider'] for x in supervisor['runs']] == ['sqlite', 'postgresql']
assert all(x['status'] == 'completed' and x['exitCode'] == 0 and x['finishedUtc']
           for x in supervisor['runs']), 'Wait for both complete provider runners'
required_recovery = [
    'final-index-01.json', 'final-analysis-01.json', 'final-analysis-01.md',
    'final-identity-audit-01.json', 'campaign-supervisor-01.json',
    'host-before-final-recovery-01.json', 'frozen-input-rehash-before-01.json',
    'observe_campaign.py', 'review-freeze-01.md', 'review-design-ci-01.md',
    'review-implementation-01.md', 'preexisting-measurement-summary-01.json',
    'preexisting-measurement-summary-01.md', 'final-archive-plan-01.md',
    'impact-current-01.json', 'impact-current-01.receipt.json',
    'remote-checkpoint-and-ci-01.json', 'recovery-publication-01.json',
]
for name in required_recovery:
    path = recovery / name
    _, digest = pin(path)
    explicit.append({'path': str(path), 'sha256': digest})
prior_expected = {
    'evidence.tar.gz': '544bcb1e77fd48fd04c74f1f6edf800431ca4ffac55c59b78d4b491ecc2eea5d',
    'manifest.json': '26f6b469978c66d838f55b7b22216a8a41bacd372301af6d396112d6beb29f81',
    'receipt.json': None, 'command.json': None, 'README.md': None,
}
for name, expected in prior_expected.items():
    path = prior / name
    _, digest = pin(path, expected)
    explicit.append({'path': str(path), 'sha256': digest})
package_roots = [
    Path('/workspace/scratch/4a65d70f0fe1/tools/nuget-packages'),
    Path('/workspace/scratch/fd78534029f7/builds/candidate-sqlite-02/consumer-workload/packages'),
    Path('/workspace/scratch/fd78534029f7/builds/candidate-postgresql-02/consumer-workload/packages'),
]
for name in inputs:
    path = Path(name)
    if any(path == root or root in path.parents for root in package_roots):
        assert path.suffix.lower() in ('.nupkg', '.snupkg'), \
            'Review cache exclusion before omitting inventoried text: ' + name
result = {
    'schemaVersion': 1,
    'scope': 'Final completed evidence union; retention only, no new acceptance credit. Historical pre-final archive is retained as an identified dependency.',
    'sourceInventories': origins, 'explicitFiles': explicit,
    'inputFiles': dict(sorted(inputs.items())),
}
with target.open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
    stream.write('\n')
print(json.dumps({'inventory': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                  'entries': len(inputs), 'archiveCreated': False}))
