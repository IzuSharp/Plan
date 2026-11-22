#!/usr/bin/env python3
"""Independent in-memory consistency probes; never writes synthetic ledger evidence."""
import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys

TASK_ROOT = Path('/workspace/scratch/b938bf45c750')
PLAN = TASK_ROOT / '.worktree/DB-CPP-01-linux/Plan'
EVIDENCE = TASK_ROOT / '_validation/migration-compare-final-2'
sys.path.insert(0, str(PLAN / 'tools'))
v = importlib.import_module('verify_db_cpp')
helper = importlib.import_module('db_cpp_evidence')
PREFIX = helper.PREFIX + 'selftest/independent-review/'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
encode = lambda value: json.dumps(value, sort_keys=True).encode()
records = []


def read(path):
    return json.loads(path.read_text())


def product_context():
    graph = read(PLAN / 'delivery-graph.json')
    acceptance = read(PLAN / helper.PREFIX / 'acceptance.json')
    baseline = read(PLAN / helper.PREFIX / 'baseline.json')
    acceptance['state'] = 'in_progress'
    acceptance['checks'] = {name: {'status': 'pending', 'evidence': []} for name in v.CHECKS}
    acceptance['prs'] = {repo: {'url': f'https://github.com/IzuSharp/{repo}/pull/{number}', 'state': 'open'}
                         for repo, number in [('NativeWeave', 21), ('NativeWeave-Design', 15), ('Plan', 26)]}
    acceptance['candidate_sources'] = {'NativeWeave': {
        'commit': '3e49cee95d206468a32c94f0a3b98e923f02acbf',
        'tree': 'f696ce6db636a3371ccf52ec777f710afa8c2a55'}}
    return graph, acceptance, baseline


def record(name, expected_rejection, action):
    try:
        action()
    except AssertionError as error:
        result = {'case': name, 'expected_rejection': expected_rejection, 'rejected': True,
                  'reason': str(error)}
    except Exception as error:
        result = {'case': name, 'expected_rejection': expected_rejection, 'error': type(error).__name__,
                  'reason': str(error)}
    else:
        result = {'case': name, 'expected_rejection': expected_rejection, 'rejected': False}
    result['passed'] = 'error' not in result and result['rejected'] is expected_rejection
    records.append(result)


def migration_fixture(mutate=lambda artifacts, receipt, acceptance, graph: None):
    graph, acceptance, baseline = product_context()
    artifacts = {'baseline': read(EVIDENCE / 'baseline/result.json'),
                 'candidate': read(EVIDENCE / 'candidate/result.json'),
                 'comparison': read(EVIDENCE / 'comparison.json')}
    receipt = {'schema_version': 2, 'task': 'DB-CPP-01', 'platform': 'linux-x64',
               'claims': ['query_semantic_parity'], 'outcome': 'passed',
               'sources': copy.deepcopy(acceptance['candidate_sources']), 'artifacts': []}
    mutate(artifacts, receipt, acceptance, graph)
    # Reseal both layers after mutations: rejection must be semantic, not a stale byte hash.
    fixture = {}
    for phase in ['baseline', 'candidate']:
        raw = encode(artifacts[phase])
        path = PREFIX + phase + '.json'
        fixture[path] = raw
        receipt['artifacts'].append({'path': path, 'sha256': sha(raw), 'kind': 'migration-run'})
        artifacts['comparison'][phase + '_result_sha256'] = sha(raw)
    raw = encode(artifacts['comparison'])
    path = PREFIX + 'comparison.json'
    fixture[path] = raw
    receipt['artifacts'].append({'path': path, 'sha256': sha(raw), 'kind': 'migration-comparison'})
    raw = encode(receipt)
    path = PREFIX + 'receipt.json'
    fixture[path] = raw
    acceptance['checks']['query_semantic_parity'] = {'status': 'passed',
        'evidence': [{'path': path, 'sha256': sha(raw)}]}
    v.validate(graph, acceptance, baseline, read_bytes=lambda name: fixture[name])


def set_artifact(key, field, value):
    return lambda artifacts, receipt, acceptance, graph: artifacts[key].__setitem__(field, value)


record('actual-migration-results', False, migration_fixture)
record('wrapper-source-differs-from-candidate', True, lambda: migration_fixture(
    lambda a, r, c, g: r['sources']['NativeWeave'].__setitem__('commit', '0' * 40)))
record('actual-result-source-differs-from-wrapper', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['source_identity'].__setitem__('commit', '0' * 40)))
record('actual-controller-dirty', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['source_identity'].__setitem__('scope_status', ' M Consumer.csproj')))
record('passed-wrapper-around-failed-candidate', True, lambda: migration_fixture(
    set_artifact('candidate', 'passed', False)))
record('passed-wrapper-around-candidate-with-failures', True, lambda: migration_fixture(
    set_artifact('candidate', 'failures', ['deliberate in-memory failure'])))
record('failed-command-under-passed-candidate', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['commands'][0].__setitem__('exit_code', 1)))
record('no-candidate-commands', True, lambda: migration_fixture(
    set_artifact('candidate', 'commands', [])))
record('required-aot-row-removed', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['rows'].pop('sqlite-aot')))
record('required-aot-row-failed', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['rows']['sqlite-aot'].__setitem__('passed', False)))
record('failed-baseline-under-passed-comparison', True, lambda: migration_fixture(
    set_artifact('baseline', 'passed', False)))
record('changed-business-source', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['source_sha256'].__setitem__('Program.cs', '0' * 64)))
record('changed-dto-input', True, lambda: migration_fixture(
    set_artifact('candidate', 'dto_variant_sha256', '0' * 64)))
record('changed-sdk-input', True, lambda: migration_fixture(
    set_artifact('candidate', 'global_json_sha256', '0' * 64)))
record('changed-abi-probe-input', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['abi_inputs_sha256'].__setitem__('tests/Migration.Cpp/abi_probe.py', '0' * 64)))
record('different-postgresql-version', True, lambda: migration_fixture(
    set_artifact('candidate', 'postgres_version', 'postgres (PostgreSQL) 17.0')))


def remove_package(artifacts, receipt, acceptance, graph):
    artifacts['candidate']['packages'].pop('NativeWeave.Database.Sqlite.Native')
    artifacts['comparison']['cpp_packages'].pop('NativeWeave.Database.Sqlite.Native')


record('missing-native-package-in-both-summaries', True, lambda: migration_fixture(remove_package))
record('package-built-from-wrong-commit', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['packages']['NativeWeave.Core']['repository'].__setitem__('commit', '0' * 40)))
record('native-product-build-tool-invoked-by-consumer', True, lambda: migration_fixture(
    set_artifact('candidate', 'rust_or_cpp_build_tools_invoked', True)))
record('comparison-row-differs-from-actual', True, lambda: migration_fixture(
    lambda a, r, c, g: a['comparison']['rows']['sqlite-aot']['semantic_groups'].__setitem__('continue', 0)))
record('dto-native-hash-changed', True, lambda: migration_fixture(
    lambda a, r, c, g: a['comparison']['rows']['sqlite-aot']['dto_change'].__setitem__('native_sha256_unchanged', False)))
record('abi-refusal-differs-from-rust', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['abi']['cases']['unknown-column'].__setitem__('status', 0)))
record('abi-resource-leak', True, lambda: migration_fixture(
    lambda a, r, c, g: a['candidate']['abi'].__setitem__('retired_counts', [1, 0, 0, 0, 0, 0])))


def differing_abi(artifacts, receipt, acceptance, graph):
    artifacts['candidate']['abi']['cases']['unknown-column']['status'] = 0
    artifacts['comparison']['abi_compatibility']['candidate'] = copy.deepcopy(artifacts['candidate']['abi'])


def wrong_historical_snapshot(artifacts, receipt, acceptance, graph):
    artifacts['candidate']['rows']['sqlite-aot']['snapshots']['old_seed']['sha256'] = '0' * 64
    artifacts['comparison']['rows'] = copy.deepcopy(artifacts['candidate']['rows'])


record('different-actual-abi-with-consistent-wrapper', True, lambda: migration_fixture(differing_abi))
record('wrong-old-snapshot-with-consistent-wrapper', True, lambda: migration_fixture(wrong_historical_snapshot))
record('empty-phase-list', True, lambda: migration_fixture(
    lambda a, r, c, g: g['current_execution'].__setitem__('phases', [])))


def ci_fixture(directory, mutate=lambda row, sources, artifacts: None):
    folder = PLAN / helper.PREFIX / 'ci' / directory
    artifacts = {}
    references = {}
    for name in ['run', 'jobs']:
        path = folder / (name + '.json')
        raw = path.read_bytes()
        key = path.relative_to(PLAN).as_posix()
        references[name] = {'path': key, 'sha256': sha(raw)}
        artifacts[key] = {**references[name], 'kind': 'github-' + name, 'data': json.loads(raw)}
    run = artifacts[references['run']['path']]['data']
    sources = {'NativeWeave-Design': {'commit': run['head_sha'], 'tree': run['head_commit']['tree_id']}}
    row = {'repository': 'NativeWeave-Design',
           'scope': 'pr_head' if 'pr-head' in directory else 'merged_main',
           'workflow_path': run['path'], 'url': run['html_url'], **references}
    mutate(row, sources, artifacts)
    for name in ['run', 'jobs']:
        path = row[name]['path']
        artifacts[path]['sha256'] = sha(encode(artifacts[path]['data']))
        row[name]['sha256'] = artifacts[path]['sha256']
    helper.validate_ci_row(row, sources, artifacts, {
        'NativeWeave-Design': {'url': 'https://github.com/IzuSharp/NativeWeave-Design/pull/15'}})


for name in ['design-pr-head-44956346986', 'design-pr-head-44956346889',
             'design-merged-main-44956543416', 'design-merged-main-44956543440']:
    record('actual-ci-' + name, False, lambda name=name: ci_fixture(name))


def ci_mutation(name, fn):
    record(name, True, lambda: ci_fixture('design-merged-main-44956543416', fn))


ci_mutation('raw-ci-run-failed', lambda r, s, a: a[r['run']['path']]['data'].__setitem__('conclusion', 'failure'))
ci_mutation('raw-ci-run-in-progress', lambda r, s, a: a[r['run']['path']]['data'].__setitem__('status', 'in_progress'))
ci_mutation('raw-ci-run-wrong-source', lambda r, s, a: a[r['run']['path']]['data'].__setitem__('head_sha', '0' * 40))
ci_mutation('raw-ci-run-wrong-tree', lambda r, s, a: a[r['run']['path']]['data']['head_commit'].__setitem__('tree_id', '0' * 40))
ci_mutation('raw-ci-run-wrong-repository', lambda r, s, a: a[r['run']['path']]['data']['repository'].__setitem__('full_name', 'IzuSharp/Plan'))
ci_mutation('raw-ci-run-wrong-url', lambda r, s, a: a[r['run']['path']]['data'].__setitem__('url', 'https://api.github.com/repos/IzuSharp/Plan/actions/runs/44956543416'))
ci_mutation('raw-ci-run-wrong-event', lambda r, s, a: a[r['run']['path']]['data'].__setitem__('event', 'workflow_dispatch'))
ci_mutation('raw-main-ci-run-wrong-branch', lambda r, s, a: a[r['run']['path']]['data'].__setitem__('head_branch', 'task/DB-CPP-01-linux'))
ci_mutation('raw-ci-job-failed', lambda r, s, a: a[r['jobs']['path']]['data']['jobs'][0].__setitem__('conclusion', 'failure'))
ci_mutation('raw-ci-job-skipped', lambda r, s, a: a[r['jobs']['path']]['data']['jobs'][0].__setitem__('conclusion', 'skipped'))
ci_mutation('raw-ci-job-another-run', lambda r, s, a: a[r['jobs']['path']]['data']['jobs'][0].__setitem__('run_id', 1))
ci_mutation('raw-ci-job-another-attempt', lambda r, s, a: a[r['jobs']['path']]['data']['jobs'][0].__setitem__('run_attempt', 2))
ci_mutation('raw-ci-job-another-head', lambda r, s, a: a[r['jobs']['path']]['data']['jobs'][0].__setitem__('head_sha', '0' * 40))
ci_mutation('raw-ci-jobs-page-incomplete', lambda r, s, a: a[r['jobs']['path']]['data'].__setitem__('total_count', 2))
ci_mutation('raw-ci-required-job-omitted', lambda r, s, a: a[r['jobs']['path']]['data'].__setitem__('jobs', []))
ci_mutation('raw-ci-required-step-skipped', lambda r, s, a: next(
    x for x in a[r['jobs']['path']]['data']['jobs'][0]['steps']
    if x['name'] == 'Validate migration decision and unchanged accepted database scope at its frozen input').__setitem__('conclusion', 'skipped'))


def bare_command(claim):
    graph, acceptance, baseline = product_context()
    source = acceptance['candidate_sources']['NativeWeave']
    value = {'passed': True, 'sourceCommit': source['commit'], 'sourceTree': source['tree'],
             'sourceDirty': False, 'sourceStable': True,
             'commands': [{'argv': ['/usr/bin/printf', 'not-a-product-test'], 'exitCode': 0}]}
    path = PREFIX + 'arbitrary-command.json'
    fixture = {path: encode(value)}
    receipt = {'schema_version': 2, 'task': 'DB-CPP-01', 'platform': 'linux-x64',
               'claims': [claim], 'outcome': 'passed', 'sources': {'NativeWeave': source},
               'artifacts': [{'path': path, 'sha256': sha(fixture[path]), 'kind': 'command-result'}]}
    path = PREFIX + 'arbitrary-command-receipt.json'
    fixture[path] = encode(receipt)
    acceptance['checks'][claim] = {'status': 'passed', 'evidence': [{'path': path, 'sha256': sha(fixture[path])}]}
    v.validate(graph, acceptance, baseline, read_bytes=lambda name: fixture[name])


for claim in ['native_sanitizers', 'rust_free_build_pack_run', 'native_format_tidy']:
    record('arbitrary-success-command-as-' + claim, True, lambda claim=claim: bare_command(claim))


def closeout_fixture(mutate=lambda fixture: None):
    # Reuse only the author's explicit synthetic accepted-state fixture layout;
    # these additional mutations and the expected policy are independently chosen.
    negative = importlib.import_module('verify_db_cpp_negative')
    graph, acceptance, baseline = product_context()
    fixture = negative.Fixture(graph, acceptance)
    mutate(fixture)
    v.validate(fixture.graph, fixture.acceptance, baseline, read_bytes=fixture.read, complete=True)


record('synthetic-complete-delivery-fixture', False, closeout_fixture)
record('delivered-plan-tested-tree-mismatch', True, lambda: closeout_fixture(
    lambda f: f.acceptance['delivery_snapshot']['plan_tested'].__setitem__('tree', '0' * 40)))
record('delivered-plan-followup-policy-removed', True, lambda: closeout_fixture(
    lambda f: f.acceptance['delivery_snapshot'].pop('record_policy')))
record('delivered-plan-future-self-ci-predicted', True, lambda: closeout_fixture(
    lambda f: f.acceptance['delivery_snapshot'].__setitem__('self_ci', 'success')))
record('accepted-plan-still-open', True, lambda: closeout_fixture(
    lambda f: f.acceptance['prs']['Plan'].__setitem__('state', 'open')))
record('accepted-plan-missing-main-ci', True, lambda: closeout_fixture(
    lambda f: f.acceptance['prs']['Plan'].pop('merged_main_checks')))
record('accepted-plan-candidate-source-mismatch', True, lambda: closeout_fixture(
    lambda f: f.acceptance['candidate_sources']['Plan'].__setitem__('commit', '0' * 40)))
record('accepted-plan-unobserved-merge', True, lambda: closeout_fixture(
    lambda f: f.change(f.acceptance['prs']['Plan']['observation']['path'], lambda d: d.__setitem__('merged', False))))
record('accepted-plan-main-ci-uses-pr-head-receipt', True, lambda: closeout_fixture(
    lambda f: f.acceptance['prs']['Plan'].__setitem__('merged_main_checks', f.acceptance['prs']['Plan']['head_checks'])))

result = {'schema_version': 1, 'scope': 'Independent in-memory verifier consistency review; no synthetic ledger evidence',
          'verifier_sha256': {name: sha((PLAN / 'tools' / name).read_bytes())
                              for name in ['verify_db_cpp.py', 'db_cpp_evidence.py']},
          'actual_migration_comparison_sha256': sha((EVIDENCE / 'comparison.json').read_bytes()),
          'cases': records, 'passed': all(row['passed'] for row in records)}
output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('result.json')
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': result['passed'], 'cases': len(records),
                  'failures': [row for row in records if not row['passed']], 'output': str(output)}, indent=2))
raise SystemExit(0 if result['passed'] else 1)
