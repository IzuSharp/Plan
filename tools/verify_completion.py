#!/usr/bin/env python3
"""Check current research/design acceptance and exact input bytes; never execute Delivery."""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_graphs import Validator, node_digest
from review_bindings import required_paths, verify_acceptance_index, verify_scoped_review, verify_binding_attestations

P = Path(__file__).resolve().parents[1]
D = P.parent / 'NativeWeave-Design'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path):
    return json.loads(path.read_bytes())

def git_bytes(root, commit, path):
    assert re.fullmatch('[0-9a-f]{40}', commit), commit
    return subprocess.check_output(['git', 'show', commit+':'+path], cwd=root)

def input_manifest(checker, record, required):
    raw = checker.require_file_hash(record['path'], record['sha256'], 'current-input-manifest')
    assert raw is not None, checker.errors
    data = json.loads(raw)
    assert data['record_kind'] == 'research_design_input_snapshot'
    assert data['files'] and data['product_execution'] is False
    sources = data['source_commits']
    assert isinstance(sources, dict) and sources
    seen = set()
    for row in data['files']:
        assert row['path'] not in seen, row['path']
        seen.add(row['path'])
        assert not row['path'].startswith('NativeWeave:'), row['path']
        value = checker.require_file_hash(row['path'], row['sha256'], 'accepted-input')
        assert value is not None and len(value) == row['bytes'], row['path']
        repo, path = row['path'].split(':', 1)
        assert row['source_commit'] == sources[repo]
        assert value == git_bytes(P.parent/repo, row['source_commit'], path), row['path']
    assert required <= seen, ('incomplete subject snapshot', sorted(required-seen))
    return data

def verify(require_complete=False):
    baseline = read(P/'source-driven-baseline.json')
    assert baseline['current_phase'] == 'research_design_planning'
    assert baseline['product_implementation_authorized'] is False
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=D, text=True).strip()
    assert head == baseline['design_merge_commit'], (head, baseline['design_merge_commit'])
    registry_raw = (D/'docs/contracts/registry.json').read_bytes()
    assert digest(registry_raw) == baseline['contract_registry_sha256']
    assert registry_raw == git_bytes(D, head, 'docs/contracts/registry.json')
    checker = Validator(P)
    result = checker.run()
    assert result['ok'], result['errors']
    assert result['counts'] == {'research': 34, 'documentation': 32, 'delivery': 48}
    expected = {'research': {f'R{i:02}' for i in range(1, 35)},
                'documentation': {f'D{i:02}' for i in range(1, 33)},
                'delivery': {f'{letter}{i:02}' for letter in 'AB' for i in range(1, 25)}}
    states = {}
    for kind in expected:
        nodes = checker.graphs[kind]['nodes']
        assert {n['id'] for n in nodes} == expected[kind]
        states[kind] = dict(Counter(n['status'] for n in nodes))
        for node in nodes:
            packet = P/node['prompt']
            assert digest(packet.read_bytes()) == node['packet_sha256'], node['id']
            assert 'Task revision **'+node['revision']+'**' in packet.read_text(), node['id']
            if kind != 'delivery':
                for output in node['outputs']:
                    assert checker.resolve(output).is_file(), (node['id'], output)
            else:
                assert node['status'] == 'planned_candidate', node['id']
                assert node['implementation_authorization'] == {'status': 'not_authorized', 'approval_record': None}
                assert node['implementation_steps'] and node['specific_acceptance'], node['id']
    registry = json.loads(registry_raw)['contracts']
    assert len(registry) == 21 and len({c['id'] for c in registry}) == 21
    for contract in registry:
        assert digest((D/contract['spec_path']).read_bytes()) == contract['content_sha256'], contract['id']
    stage = baseline.get('completion_stage', 'review_ready')
    assert stage in {'review_ready', 'accepted_design'}, stage
    complete = stage == 'accepted_design' or require_complete
    if complete:
        assert states['research'] == {'accepted': 34}
        assert states['documentation'] == {'accepted': 32}
        assert result['accepted_contracts'] == 21
    else:
        assert set(states['research']) <= {'review_ready', 'accepted'}
        assert set(states['documentation']) <= {'review_ready', 'accepted'}
    checked_inputs = 0
    subjects = []
    for contract in registry:
        if contract['status'] != 'accepted':
            continue
        subject = {'kind': 'contract', 'id': contract['id'], 'version': contract['version'],
                   'content_sha256': contract['content_sha256']}
        for entry in contract['evidence']:
            evidence = read(checker.resolve(entry['manifest_path']))
            snapshot = input_manifest(checker, evidence['artifact'], required_paths(checker, 'contract', contract)[1])
            assert snapshot['subject'] == subject
            assert snapshot['source_commits']['NativeWeave-Design'] == contract['source_commit']
            expected_dependencies = {c['id']+'@'+c['version']:
                {'spec_path': checker.contracts[(c['id'],c['version'])]['spec_path'],
                 'content_sha256': checker.contracts[(c['id'],c['version'])]['content_sha256'],
                 'evidence_sha256': [e['sha256'] for e in checker.contracts[(c['id'],c['version'])]['evidence']],
                 'review_sha256': [r['sha256'] for r in checker.contracts[(c['id'],c['version'])]['reviews']]}
                for c in contract['dependencies']}
            assert snapshot['contract_dependency_snapshot'] == expected_dependencies
            checked_inputs += len(snapshot['files'])
        subjects.append(('contract', contract['id'], contract['evidence'], contract['reviews']))
    for kind in ('research', 'documentation'):
        for node in checker.graphs[kind]['nodes']:
            if node['status'] != 'accepted':
                continue
            original = json.loads(git_bytes(P, node['source_commit'], kind+'-graph.json'))
            original_node = next(n for n in original['nodes'] if n['id'] == node['id'])
            assert node_digest(original_node) == node_digest(node), (node['id'], 'source node changed')
            for entry in node['acceptance_evidence']:
                evidence = read(checker.resolve(entry['manifest_path']))
                snapshot = input_manifest(checker, evidence['artifact'], required_paths(checker, 'task', node)[1])
                assert snapshot['subject'] == checker.task_subject(node['id'], node)
                assert snapshot['source_commits']['Plan'] == node['source_commit']
                checked_inputs += len(snapshot['files'])
            subjects.append(('task', node['id'], node['acceptance_evidence'], node['independent_reviewers']))
    for kind, identity, evidence, reviews in subjects:
        for entry in reviews:
            review = read(checker.resolve(entry['manifest_path']))
            report = review['independent_report']
            raw = checker.require_file_hash(report['path'], report['sha256'], identity+'/independent-report')
            assert raw is not None, checker.errors
            actual = json.loads(raw)
            assert actual['reviewer'] == review['reviewer']
            value = checker.nodes[identity] if kind == 'task' else next(c for c in registry if c['id'] == identity)
            verify_scoped_review(checker, actual, kind, value)
            assert review['recorded_by'] == '/root' and review['review_kind'] == 'binding_of_actual_independent_technical_review'
    if subjects:
        attestations = []
        kinds = {kind for kind, identity, evidence, reviews in subjects}
        ledgers = ([D/'docs/contracts/acceptance-index.json'] if 'contract' in kinds else [])
        ledgers += ([P/'ledger/completion-acceptance.json'] if 'task' in kinds else [])
        for path in ledgers:
            ledger = read(path)
            ledger_kind = 'contract' if path.parent == D/'docs/contracts' else 'task'
            values = ([c for c in registry if c['status'] == 'accepted'] if ledger_kind == 'contract'
                      else [n for kind in ('research','documentation') for n in checker.graphs[kind]['nodes'] if n['status'] == 'accepted'])
            verify_acceptance_index(checker, ledger, ledger_kind, values,
                                    {'accepted_research_and_detailed_design'})
            verify_binding_attestations(checker, ledger, ledger_kind, values)
            for ref in ledger['binding_attestations']:
                raw = checker.require_file_hash(ref['path'], ref['sha256'], 'binding-attestation')
                assert raw is not None, checker.errors
                data = json.loads(raw)
                assert data['verdict'] == 'accepted' and data['blocking_findings'] == []
                attestations.extend((data['reviewer'], s) for s in data['subjects'])
        for kind, identity, evidence, reviews in subjects:
            review_objects = [read(checker.resolve(r['manifest_path'])) for r in reviews]
            expected_record = {'kind': kind, 'id': identity,
                'evidence_sha256': [e['sha256'] for e in evidence],
                'review_sha256': [r['sha256'] for r in reviews]}
            assert any(item == expected_record and any(r['reviewer'] == reviewer for r in review_objects)
                       for reviewer, item in attestations), (kind, identity, 'independent exact binding not attested')
    assert not checker.errors, checker.errors
    return {'schema_version': '1.0.0', 'ok': True, 'stage': stage,
            'design_commit': head, 'counts': result['counts'], 'states': states,
            'accepted_contracts': result['accepted_contracts'], 'checked_input_entries': checked_inputs,
            'fragments': 10, 'packets': 114, 'product_implementation_authorized': False,
            'product_delivery_executed': False, 'native_experiments_rerun': False,
            'scope': 'Current exact research/design/task bindings, independent review linkage and planning integrity; not product conformance or identity authentication.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    report = verify(require_complete=args.require_complete)
    (P/'verification/completion.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
