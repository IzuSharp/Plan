#!/usr/bin/env python3
"""Verify portable exported bytes and the explicit correction evidence links."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'manifest.json').read_text())
sha = lambda value: hashlib.sha256(value).hexdigest()
assert manifest['formal_candidate_acceptance'] is False
assert manifest['base_product_commit'] == '3e49cee95d206468a32c94f0a3b98e923f02acbf'
rows = manifest['artifacts']
assert len({row['path'] for row in rows}) == len(rows)
assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == (
    {row['path'] for row in rows} | {'manifest.json'})
originals = {}
for row in rows:
    relative = Path(row['path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    raw = (ROOT / relative).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], row['path']
    text = raw.decode('utf-8')
    assert '\0' not in text
    assert not re.search(r"postgres(?:ql)?://[^\s\"'<>]+", text), row['path']
    if 'original' in row:
        originals.setdefault(row['original']['sha256'], []).append(row['path'])
        if relative.suffix == '.json':
            value = json.loads(text)
            assert value['sanitized'] is True
            assert value['source_artifact_sha256'] == row['original']['sha256']
        else:
            assert sha(raw) == row['original']['sha256']


def data(path):
    return json.loads((ROOT / path).read_text())['data']


def original_hash(path):
    return json.loads((ROOT / path).read_text())['source_artifact_sha256']


receipt = data('receipt.json')
assert receipt['sourceDirty'] is True
assert receipt['baseCommit'] == manifest['base_product_commit']
assert len(receipt['sourceFiles']) == 5
assert receipt['status'] == 'passed-targeted-development'
for ref in receipt['evidence'].values():
    assert ref['sha256'] in originals, ref['path']
for mode in ['release', 'asan-ubsan']:
    text = data('native/' + mode + '-ctest.json')['text']
    assert '100% tests passed, 0 tests failed out of 5' in text
negative = data('negative-controls.json')
assert negative['passed'] is True
assert {row['name'] for row in negative['negativeControls']} == {'physical-grant', 'provider-width'}
assert all(row['negativeRejected'] is True and row['exitCode'] == 1 for row in negative['negativeControls'])
assert all(receipt['sourceFiles'][key] == value for key, value in negative['sourceFiles'].items())
codec = data('codec-replay.json')
assert codec['passed'] is True and len(codec['commands']) == 6
assert all(row['exitCode'] == 0 and row['sha256'] in originals for row in codec['commands'])
for mode in ['jit', 'aot']:
    summary = codec['summaries'][mode]
    assert (summary['roundtrips'], summary['legacyFallibilityRefusals'], summary['malformedRejected']) == (120, 24, 4189)

fixed = data('public-abi/fixed-replay.json')
assert fixed['passed'] is True and fixed['formal_candidate_acceptance'] is False
assert fixed['base_head'] == receipt['baseCommit']
assert all(receipt['sourceFiles'][key] == value for key, value in fixed['source_files_sha256'].items())
expected_cases = {'postgresql-field-11', 'postgresql-field-12', 'sqlite-empty-exact',
                  'sqlite-empty-minus-one', 'sqlite-stream-valid', 'sqlite-stream-missing',
                  'sqlite-stream-valid-small-batch', 'sqlite-stream-missing-small-batch'}
assert set(fixed['cases']) == expected_cases
postgres = data('source3/postgresql-difference.json')
sqlite = data('source3/sqlite-difference.json')
assert fixed['reference_result_sha256'] == {
    'postgresql': original_hash('source3/postgresql-difference.json'),
    'sqlite': original_hash('source3/sqlite-difference.json')}
for name, case in fixed['cases'].items():
    assert case['passed'] is True
    old, new = case['reference'], case['result']
    reference = postgres if name.startswith('postgresql-') else sqlite
    old_key = 'rust-' + name.split('-', 1)[1]
    assert old == reference['cases'][old_key]
    assert old['original_result_sha256'] in originals and new['original_result_sha256'] in originals
    raw = data('public-abi/fixed-cases/' + name + '.json')
    assert original_hash('public-abi/fixed-cases/' + name + '.json') == new['original_result_sha256']
    assert all(new[key] == value for key, value in raw.items())
    for key in ['terminal', 'count', 'independent_sql_count', 'retired_counts', 'probe_sha256',
                'abi_helper_sha256', 'sql_template_sha256']:
        assert old[key] == new[key], (name, key)
    wire_key = 'parameter_wire_sha256' if name.startswith('postgresql-') else 'wire_sha256'
    assert old[wire_key] == new[wire_key]
    assert old['retired_counts'] == new['retired_counts'] == [0] * 6
assert postgres['observed_gap'] is True and postgres['same_inputs'] is True
assert postgres['cases']['rust-field-11']['terminal']['code'] == 3
assert postgres['cases']['cpp-source3-field-11']['terminal']['status'] == 0
assert postgres['cases']['rust-field-11']['independent_sql_count'] == 0
assert postgres['cases']['cpp-source3-field-11']['independent_sql_count'] == 1
assert sqlite['same_inputs'] is True
assert sqlite['cases']['rust-empty-minus-one']['terminal']['code'] == 6
assert sqlite['cases']['cpp-source3-empty-minus-one']['independent_sql_count'] == 1
for case in ['stream-valid-small-batch', 'stream-missing-small-batch']:
    assert sqlite['cases']['cpp-source3-' + case]['terminal']['code'] == 14

wiring = data('ci-wiring.json')
assert wiring['status'] == 'targeted-development-passed'
assert {row['profile'] for row in wiring['checks']} == {'release', 'asan'}
assert all(row['buildExitCode'] == row['testExitCode'] == 0 and row['mode'] == 'input-postgresql'
           for row in wiring['checks'])
assert all(receipt['sourceFiles'][key] == value for key, value in wiring['nativeSourceSha256'].items())
assert all(row['consumerLogSha256'] in originals for row in wiring['checks'])
shallow, full = data('git-transport/shallow.json'), data('git-transport/full-history.json')
assert shallow['sourceCommit'] == full['sourceCommit'] == manifest['base_product_commit']
assert shallow['sourceTree'] == full['sourceTree']
assert shallow['transportPassed'] is True and shallow['historyIntegrityPassed'] is False
assert full['transportPassed'] is True and full['historyIntegrityPassed'] is True
assert any(row['exitCode'] != 0 for row in shallow['commands'])
assert all(row['exitCode'] == 0 for row in full['commands'])
assert full['commitCount'] > 1
print(json.dumps({'passed': True, 'artifacts': len(rows), 'public_abi_cases': len(expected_cases),
                  'source_files': len(receipt['sourceFiles']), 'formal_candidate_acceptance': False,
                  'manifest_sha256': sha((ROOT / 'manifest.json').read_bytes())}, indent=2))
