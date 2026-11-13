#!/usr/bin/env python3
"""Negative gate checks on an independently validated complete local bundle.

Synthetic records below test validator behavior only, inside temporary copies.
They are never acceptance records for research, contracts or the product.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile

PLAN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validator', PLAN/'tools/validate_graphs.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def copy_repository(source, target):
    """Copy tracked and unignored work-in-progress files, never .git/build caches.

    A valid copied baseline is required before any mutation can count as passed.
    No hard links are used: a mutation cannot change the original evidence.
    """
    source, target = Path(source).resolve(), Path(target)
    identity = subprocess.run(['git', '-C', str(source), 'rev-parse', '--show-toplevel'],
                              capture_output=True, text=True)
    if identity.returncode == 0 and Path(identity.stdout.strip()).resolve() == source:
        raw = subprocess.check_output(['git', '-C', str(source), 'ls-files', '-z',
                                       '--cached', '--others', '--exclude-standard'])
        files = sorted({Path(p.decode()) for p in raw.split(b'\0') if p})
    else:
        files = [p.relative_to(source) for p in source.rglob('*')
                 if p.is_file() and not {'.git', '__pycache__'}.intersection(p.relative_to(source).parts)]
    count = 0
    for relative in files:
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('unsafe repository file '+str(relative))
        path = source/relative
        if not path.is_file():
            continue
        destination = target/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        count += 1
    return count


def base_copy(destination, source_plan=PLAN):
    """Copy both repositories, including actual specs, reviews, logs and artifacts."""
    bundle = Path(destination)/'bundle'
    source_plan = Path(source_plan).resolve()
    copy_repository(source_plan, bundle/'Plan')
    copy_repository(source_plan.parent/'NativeWeave-Design', bundle/'NativeWeave-Design')

    # Referenced ignored artifacts remain required. This captures exact accesses
    # of the unchanged strict gate and does not waive any file or hash check.
    class ReferencedFiles(v.Validator):
        def require_file_hash(self, ref, sha, where):
            raw = super().require_file_hash(ref, sha, where)
            if raw is not None:
                repo, relative = v.path_parts(ref)
                target = bundle/repo/relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            return raw
    source = ReferencedFiles(source_plan).run()
    if not source['ok']:
        raise AssertionError({'invalid_source_baseline': source['errors']})
    root = bundle/'Plan'
    copied = v.Validator(root).run()
    if not copied['ok']:
        raise AssertionError({'invalid_copied_baseline': copied['errors']})
    return root


def change_graph(root, name, change):
    path = Path(root)/(name+'-graph.json')
    graph = json.loads(path.read_text())
    change(graph)
    path.write_text(json.dumps(graph, ensure_ascii=False, indent=2)+'\n')


def node(graph, task_id):
    return next(n for n in graph['nodes'] if n['id'] == task_id)


def run_case(name, mutate, expected, source_plan=PLAN):
    with tempfile.TemporaryDirectory(prefix='nativeweave-gate-mutation-') as temporary:
        root = base_copy(Path(temporary), source_plan)
        mutate(root)
        result = v.Validator(root).run()
        codes = {e['code'] for e in result['errors']}
        closed = not any(result['ready'].values()) and not any(result['continuable'].values())
        return {'case': name, 'passed': not result['ok'] and bool(codes & set(expected)) and closed,
                'copied_baseline_validated': True, 'expected_any_error': expected,
                'actual_errors': sorted(codes), 'ready_and_resume_fail_closed': closed}


def cycle(root):
    def mutate(graph):
        a, b = node(graph, 'R01'), node(graph, 'R02')
        for left, right in [(a, b), (b, a)]:
            left['start_dependencies'] = [right['id']]
            left['dependency_pins'] = {d: node(graph, d)['revision']
                                       for d in left['start_dependencies']+left['acceptance_dependencies']}
    change_graph(root, 'research', mutate)


def missing(root):
    def mutate(graph):
        n = node(graph, 'R01')
        n['start_dependencies'].append('R999')
        n['dependency_pins']['R999'] = '0.3.0'
    change_graph(root, 'research', mutate)


def overlap(root):
    def mutate(graph):
        a, b = node(graph, 'R01'), node(graph, 'R02')
        b['write_scopes'], b['outputs'] = deepcopy(a['write_scopes']), deepcopy(a['outputs'])
    change_graph(root, 'research', mutate)


def stale_packet(root):
    path = root/'research-tasks/R01.md'
    path.write_bytes(path.read_bytes()+b'\nChanged after review.\n')


def fake_contract(root):
    path = root.parent/'NativeWeave-Design/docs/contracts/registry.json'
    registry = json.loads(path.read_text())
    contract = registry['contracts'][0]
    contract['status'] = 'accepted'
    contract['evidence'] = [{'manifest_path': 'Plan:missing.json', 'sha256': '0'*64}]
    contract['reviews'] = [{'manifest_path': 'Plan:missing-review.json', 'sha256': '0'*64}]
    path.write_text(json.dumps(registry))


def oversized_output(root):
    def mutate(graph):
        graph['nodes'][0].update(write_scopes=['NativeWeave:src/Only/'], outputs=['NativeWeave:src/'])
    change_graph(root, 'research', mutate)


def pin_drift(root):
    def mutate(graph):
        target = next(n for n in graph['nodes'] if n['dependency_pins'])
        target['dependency_pins'][next(iter(target['dependency_pins']))] = '9.9.9'
    change_graph(root, 'delivery', mutate)


def empty_acceptance(state):
    return lambda root: change_graph(root, 'research', lambda graph: node(graph, 'R01').update(
        status=state, acceptance_evidence=[], independent_reviewers=[]))


def duplicate(root):
    change_graph(root, 'research', lambda graph: graph['nodes'].append(deepcopy(graph['nodes'][0])))


def fragment_mirror(root):
    path = root/'fragments/server.json'
    fragment = json.loads(path.read_text())
    fragment['task_details']['B17']['boundary_and_ownership'] = 'Unreviewed replacement'
    path.write_text(json.dumps(fragment))


def release_cycle(root):
    def mutate(graph):
        component, release = node(graph, 'B10'), node(graph, 'B24')
        component['acceptance_dependencies'].append('B24')
        component['dependency_pins']['B24'] = release['revision']
    change_graph(root, 'delivery', mutate)


def synthetic_evidence(checker, subject, name, kind='design_analysis'):
    """Validator fixture, explicitly not an assertion of actual execution."""
    directory = checker.plan/'verification/synthetic-gate-fixtures'
    directory.mkdir(parents=True, exist_ok=True)
    artifact = directory/(name+'.txt')
    artifact.write_text('Synthetic validator fixture; no command or product test was run.\n')
    evidence = {'schema_version': '1.0.0', 'is_template': False, 'subject': subject,
                'status': 'passed', 'kind': kind, 'producer': 'synthetic-validator-fixture',
                'recorded_at': '2026-11-13T00:00:00Z',
                'artifact': {'path': 'Plan:'+artifact.relative_to(checker.plan).as_posix(),
                             'sha256': digest(artifact)}}
    path = directory/(name+'.json')
    path.write_text(json.dumps(evidence, indent=2)+'\n')
    return path, evidence


def stale_subject_case(name, task_id, mutate, source_plan):
    with tempfile.TemporaryDirectory(prefix='nativeweave-subject-mutation-') as temporary:
        root = base_copy(Path(temporary), source_plan)
        checker = v.Validator(root)
        baseline = checker.run()
        assert baseline['ok'], baseline['errors']
        task = checker.nodes[task_id]
        old = checker.task_subject(task_id, task)
        path, _ = synthetic_evidence(checker, old, name)
        mutate(checker)
        new = checker.task_subject(task_id, task)
        checker.evidence([{'manifest_path': 'Plan:'+path.relative_to(root).as_posix(),
                           'sha256': digest(path)}], new, 'synthetic-stale-subject')
        codes = {e['code'] for e in checker.errors}
        ready, _, _ = checker.ready()
        return {'case': name, 'passed': old != new and 'EVIDENCE_SUBJECT' in codes and not any(ready.values()),
                'copied_baseline_validated': True, 'subject_changed': old != new,
                'actual_errors': sorted(codes), 'synthetic_record_not_execution': True}


def evidence_guard_case(name, mutate, expected, source_plan):
    with tempfile.TemporaryDirectory(prefix='nativeweave-evidence-mutation-') as temporary:
        root = base_copy(Path(temporary), source_plan)
        checker = v.Validator(root)
        baseline = checker.run()
        assert baseline['ok'], baseline['errors']
        subject = {'kind': 'synthetic-validator-test', 'id': name, 'source_commit': '1'*40}
        path, record = synthetic_evidence(checker, subject, name, 'native_aot_run')
        artifact = record['artifact']
        record.update(command=['synthetic-test-only'], exit_code=0, toolchain={'name': 'fixture'},
                      platform={'os': 'Linux', 'arch': 'x64'}, source_commit='1'*40,
                      logs={'stdout': artifact, 'stderr': artifact},
                      started_at='2026-11-13T00:00:00Z', finished_at='2026-11-13T00:00:01Z',
                      checks={'completed': True, 'timed_out': False, 'failed': 0},
                      aot={'published': True, 'executed': True, 'runtime_mode': 'native_aot',
                           'publish_command': ['synthetic-publish'], 'run_command': ['synthetic-run'],
                           'target_rid': 'linux-x64', 'binary': artifact})
        def check():
            path.write_text(json.dumps(record, indent=2)+'\n')
            return checker.evidence([{'manifest_path': 'Plan:'+path.relative_to(root).as_posix(),
                                      'sha256': digest(path)}], subject, 'synthetic-run-validator')
        check()
        assert not checker.errors, checker.errors
        mutate(record)
        check()
        codes = {e['code'] for e in checker.errors}
        ready, _, _ = checker.ready()
        return {'case': name, 'passed': expected in codes and not any(ready.values()),
                'copied_baseline_validated': True, 'synthetic_manifest_baseline_validated': True,
                'actual_errors': sorted(codes), 'synthetic_record_not_execution': True}


def run_checks(plan_root):
    baseline = v.Validator(plan_root).run()
    if not baseline['ok']:
        return {'scope': 'Validator regression checks only', 'baseline_ok': False,
                'baseline_errors': baseline['errors'], 'results': [], 'all_passed': False}
    cases = [('cycle', cycle, ['DEPENDENCY_CYCLE']),
             ('missing_dependency', missing, ['MISSING_DEPENDENCY']),
             ('duplicate_id', duplicate, ['DUPLICATE_ID']),
             ('shared_write_scope', overlap, ['WRITE_SCOPE_CONFLICT']),
             ('unowned_parent_output', oversized_output, ['OUTPUT_NOT_OWNED']),
             ('task_packet_changed', stale_packet, ['HASH_MISMATCH']),
             ('dependency_version_drift', pin_drift, ['DEPENDENCY_VERSION']),
             ('forged_accepted_contract', fake_contract, ['FILE_MISSING']),
             ('fragment_mirror_drift', fragment_mirror, ['FRAGMENT_MIRROR']),
             ('release_component_acceptance_cycle', release_cycle, ['DEPENDENCY_CYCLE'])]
    cases += [('empty_evidence_'+state, empty_acceptance(state),
               ['EVIDENCE_REQUIRED', 'INDEPENDENT_REVIEW_REQUIRED']) for state in sorted(v.TERMINAL)]
    results = [run_case(*case, source_plan=plan_root) for case in cases]
    results.append(stale_subject_case('release_component_same_revision_source_changed', 'B24',
                   lambda checker: checker.nodes['B10'].update(source_commit='2'*40), plan_root))
    results.append(stale_subject_case('release_component_same_revision_evidence_changed', 'B24',
                   lambda checker: checker.nodes['B10'].update(acceptance_evidence=[{'sha256': '2'*64}]), plan_root))
    for field, value in [('content_sha256', '3'*64), ('evidence', [{'sha256': '4'*64}]),
                         ('reviews', [{'sha256': '5'*64}])]:
        def mutate(checker, field=field, value=value):
            pin = checker.nodes['A01']['contract_inputs'][0]
            checker.contracts[(pin['id'], pin['version'])][field] = value
        results.append(stale_subject_case('same_contract_version_changed_'+field, 'A01', mutate, plan_root))
    guards = [('aot_publish_without_execution', lambda m: m['aot'].update(executed=False), 'AOT_NOT_EXECUTED'),
              ('aot_wrong_target', lambda m: m['aot'].update(target_rid='win-x64'), 'AOT_TARGET'),
              ('run_missing_log', lambda m: m['logs'].pop('stderr'), 'RUN_LOGS'),
              ('run_nonzero_exit', lambda m: m.update(exit_code=1), 'RUN_COMMAND'),
              ('run_incomplete', lambda m: m['checks'].update(completed=False), 'RUN_CHECKS_INCOMPLETE'),
              ('run_source_drift', lambda m: m.update(source_commit='2'*40), 'RUN_COMMIT_STALE'),
              ('template_evidence_rejected', lambda m: m.update(is_template=True), 'TEMPLATE_EVIDENCE')]
    results += [evidence_guard_case(*case, source_plan=plan_root) for case in guards]
    return {'scope': 'Graph/evidence safety gates only; synthetic validator records are not executions or approvals',
            'baseline_ok': True, 'copied_baseline_required_for_every_case': True,
            'baseline_counts': baseline['counts'], 'baseline_accepted_contracts': baseline['accepted_contracts'],
            'results': results, 'case_count': len(results), 'all_passed': all(r['passed'] for r in results),
            'checked_files_sha256': {name: digest(Path(plan_root)/name) for name in
                                    ['research-graph.json', 'documentation-graph.json', 'delivery-graph.json',
                                     'tools/validate_graphs.py', 'tools/mutation_checks.py']}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=PLAN)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = run_checks(args.root.resolve())
    except (AssertionError, OSError, ValueError, KeyError, TypeError) as error:
        report = {'all_passed': False, 'error': str(error), 'scope': 'Invalid baseline or test fixture; no passing mutation claimed'}
    output = args.output or args.root/'verification/mutation-checks.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['all_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
