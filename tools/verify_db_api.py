#!/usr/bin/env python3
"""Validate DB-API-01 progress, evidence bindings and unchanged historical inputs."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'ledger/evidence/batches/DB-API-01/'
BATCH = ROOT / PREFIX
FROZEN = '5be447a868be78713ada52f46cee16409f0edc13'
BASELINES = {
    'Korda': '7275396176b928c8879d59f4bf20ad8fa7ffb62c',
    'NativeWeave-Design': 'de1f4796dc199250b405ea99f2129d611f17b1f6',
    'Plan': FROZEN,
}
PHASES = ['baseline', 'plan-first', 'design-contract', 'implementation',
          'aot-consumers', 'review-and-merge', 'main-and-release']
CHECKS = {'model_projection', 'reusable_mappings', 'query_composition',
          'cursor_relations', 'writes_concurrency', 'transaction_outcomes',
          'onboarding', 'migrations_scaffold', 'module_routing', 'api_compatibility',
          'postgresql_aot', 'sqlite_aot', 'native_reuse', 'independent_review',
          'pr_checks', 'merged_main', 'release_observation'}


def sha(value, size=40):
    assert isinstance(value, str) and re.fullmatch(r'[0-9a-f]{' + str(size) + '}', value), 'Invalid digest'


def local_path(value):
    path = Path(value)
    assert not path.is_absolute() and '..' not in path.parts, 'Unsafe evidence path'
    return ROOT / path


def json_read(path):
    return json.loads(path.read_text())


def bound_file(ref):
    assert set(ref) == {'path', 'sha256'}, 'Evidence reference fields'
    sha(ref['sha256'], 64)
    path = local_path(ref['path'])
    assert path.is_file(), 'Missing evidence: ' + ref['path']
    content = path.read_bytes()
    assert hashlib.sha256(content).hexdigest() == ref['sha256'], 'Evidence digest mismatch'
    return content


def identity(value):
    assert set(value) == {'commit', 'tree'}, 'Expected commit/tree identity'
    sha(value['commit'])
    sha(value['tree'])


def validate(graph, baseline, acceptance, read_bound=bound_file, require_complete=False):
    current = graph['current_execution']
    assert current['task'] == baseline['task'] == acceptance['task'] == 'DB-API-01'
    assert baseline['schema_version'] == acceptance['schema_version'] == 1
    assert current['branch'] == baseline['branch'] == 'task/DB-API-01-linux'
    assert current['platforms'] == ['linux-x64']
    assert baseline['platform'] == acceptance['platform'] == 'linux-x64'
    assert current['source_main'] == baseline['observed_merged_main'] == acceptance['baseline'] == BASELINES
    for field in ('plan', 'handoff', 'acceptance'):
        assert current[field].startswith(PREFIX) and local_path(current[field]).is_file()
    phases = current['phases']
    assert [phase['id'] for phase in phases] == PHASES
    predecessor_complete = True
    for index, phase in enumerate(phases):
        assert phase['state'] in {'pending', 'in_progress', 'complete', 'blocked'}
        assert phase['depends_on'] == PHASES[max(0, index - 1):index]
        if phase['state'] in {'in_progress', 'complete'}:
            assert predecessor_complete, 'Phase started before prerequisite'
        predecessor_complete = phase['state'] == 'complete'
    assert acceptance['state'] in {'in_progress', 'blocked', 'accepted'}
    assert set(acceptance['checks']) == CHECKS
    sources = acceptance['candidate_sources']
    assert set(sources) <= set(BASELINES)
    for value in sources.values():
        identity(value)
    contract = acceptance['design_contract']
    if contract is not None:
        assert set(contract) == {'repository', 'commit', 'path', 'sha256'}
        assert contract['repository'] == 'IzuSharp/NativeWeave-Design'
        assert contract['path'] == 'docs/database/fluent-orm.json'
        sha(contract['commit'])
        sha(contract['sha256'], 64)
    if phases[2]['state'] == 'complete' or phases[3]['state'] in {'in_progress', 'complete'}:
        assert contract is not None, 'Product work lacks Design checkpoint'
    for name, check in acceptance['checks'].items():
        assert check['requirement'].strip()
        assert check['status'] in {'pending', 'passed', 'failed', 'blocked'}
        assert isinstance(check['evidence'], list)
        assert len({ref['path'] for ref in check['evidence']}) == len(check['evidence']), 'Duplicate receipt'
        if check['status'] == 'passed':
            assert check['evidence'], 'Passed claim lacks evidence'
        for ref in check['evidence']:
            assert ref['path'].startswith(PREFIX), 'Receipt belongs to another task'
            receipt = json.loads(read_bound(ref))
            assert receipt['schema_version'] == 1 and receipt['task'] == 'DB-API-01'
            assert receipt['platform'] == 'linux-x64' and receipt['check'] == name
            assert receipt['status'] in {'passed', 'failed', 'blocked'}
            assert receipt['observations'], 'Empty observation'
            assert receipt['sources'], 'Unbound receipt source'
            for repo, source in receipt['sources'].items():
                assert repo in BASELINES
                identity(source)
                if check['status'] == 'passed':
                    assert source == sources.get(repo), 'Pass rebound to a different candidate'
            assert receipt.get('files') or receipt.get('urls'), 'Receipt lacks raw evidence or observation URL'
            for item in receipt.get('files', []):
                read_bound(item)
            for url in receipt.get('urls', []):
                assert isinstance(url, str) and url.startswith('https://'), 'Invalid observation URL'
            if check['status'] == 'passed':
                assert receipt['status'] == 'passed', 'Failure used to accept a claim'
    assert acceptance['self_ci'] == 'checked-separately', 'Evidence cannot predict its own future CI'
    release = acceptance['release']
    assert release['state'] in {'not_observed', 'pending', 'published', 'policy_skipped', 'failed'}
    assert isinstance(release['packages'], list)
    if acceptance['checks']['release_observation']['status'] == 'passed':
        assert release['state'] in {'published', 'policy_skipped'}
        if release['state'] == 'policy_skipped':
            assert release.get('reason'), 'Unexplained release skip'
        else:
            assert release['packages'], 'Published state lacks package identities'
            for package in release['packages']:
                assert package['id'] in {'Korda.Database.PostgreSql', 'Korda.Database.Sqlite'}
                assert package['version'] and package['url'].startswith('https://')
                assert package['consumer_result'] == 'passed'
    if require_complete or acceptance['state'] == 'accepted':
        assert acceptance['state'] == 'accepted'
        assert all(phase['state'] == 'complete' for phase in phases)
        assert all(check['status'] == 'passed' for check in acceptance['checks'].values())
        assert set(sources) == set(BASELINES)
        assert set(acceptance['prs']) == set(BASELINES)
        for pr in acceptance['prs'].values():
            assert pr['url'].startswith('https://github.com/') and '/pull/' in pr['url']
            assert pr['state'] == 'merged'
            identity(pr['tested'])
            identity(pr['merged'])
            assert pr['tested']['tree'] == pr['merged']['tree'], 'Merge changed reviewed content'
            assert pr['pr_ci'] and pr['main_ci'], 'Missing observed CI URLs'


def negative_controls(graph, baseline, acceptance):
    cases = []
    bad = copy.deepcopy(acceptance); bad['task'] = 'DB-CPP-01'; cases.append((graph, baseline, bad))
    bad = copy.deepcopy(acceptance); bad['checks']['model_projection']['status'] = 'passed'; bad['checks']['model_projection']['evidence'] = []; cases.append((graph, baseline, bad))
    bad = copy.deepcopy(acceptance); bad['state'] = 'accepted'; bad['checks']['postgresql_aot']['status'] = 'pending'; cases.append((graph, baseline, bad))
    bad = copy.deepcopy(graph); bad['current_execution']['phases'][2]['state'] = 'pending'; bad['current_execution']['phases'][3]['state'] = 'in_progress'; cases.append((bad, baseline, acceptance))
    bad = copy.deepcopy(acceptance); bad['self_ci'] = 'predicted-success'; cases.append((graph, baseline, bad))
    bad = copy.deepcopy(acceptance); bad['baseline']['Korda'] = '0' * 40; cases.append((graph, baseline, bad))
    bad = copy.deepcopy(acceptance); del bad['checks']['transaction_outcomes']; cases.append((graph, baseline, bad))
    for values in cases:
        try:
            validate(*values)
        except (AssertionError, KeyError):
            continue
        raise AssertionError('Invalid acceptance fixture was accepted')
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    graph = json_read(ROOT / 'delivery-graph.json')
    old = json.loads(subprocess.check_output(['git', 'show', FROZEN + ':delivery-graph.json'], cwd=ROOT))
    for key, value in old.items():
        if key not in {'current_execution', 'completed_executions'}:
            assert graph[key] == value, 'Historical graph field changed: ' + key
    assert graph['completed_executions'] == {**old['completed_executions'], 'DB-CPP-01': old['current_execution']}
    protected = ['ledger/evidence/batches/DB-CPP-01', 'ledger/evidence/batches/DB-Scope-01',
                 'research-graph.json', 'documentation-graph.json', 'source-driven-baseline.json',
                 'tasks', 'research-tasks', 'documentation-tasks', 'tools/verify_db_cpp.py',
                 'tools/verify_db_cpp_negative.py', 'tools/verify_db_scope.py']
    changed = subprocess.check_output(['git', 'diff', '--name-only', FROZEN, '--', *protected], cwd=ROOT, text=True)
    assert not changed.strip(), 'Historical accepted inputs changed: ' + changed
    baseline, acceptance = json_read(BATCH / 'baseline.json'), json_read(BATCH / 'acceptance.json')
    validate(graph, baseline, acceptance, require_complete=args.require_complete)
    for name in ['plan.md', 'handoff-linux.md']:
        path = BATCH / name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            assert (path.parent / target.split('#', 1)[0]).is_file(), 'Broken local link: ' + target
    print(json.dumps({'task': 'DB-API-01', 'document_gate': 'passed', 'acceptance': acceptance['state'],
                      'negative_controls': negative_controls(graph, baseline, acceptance),
                      'product_execution_performed_by_gate': False}, indent=2))


if __name__ == '__main__':
    main()
