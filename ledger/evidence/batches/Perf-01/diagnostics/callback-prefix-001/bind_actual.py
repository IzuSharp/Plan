#!/usr/bin/env python3
"""Bind completed prerequisite metadata to a fresh diagnostic plan; never execute it."""
import argparse
import hashlib
import json
from pathlib import Path

CANDIDATE = '092e5e2c74d7419772f2455a2922ae4238f389de'
CURRENT = 'a5748ad4e03825e3da7706d074887952da6c2d43'
NATIVE = '2f40348c3db80a4fbee7a99e721b374a597b16df'
SERVER = '8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def need(value, message):
    if not value:
        raise ValueError(message)


def completed(directory):
    result = read(directory / 'execution.json')
    need(result['status'] == 'diagnostic-completed' and result['commands']
         and all(c['exit_code'] == 0 and c['retired'] is True for c in result['commands']),
         'Actual successful retired prerequisite required: ' + str(directory))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), 'Never overwrite a prior actual plan')
    plan = read(args.template)
    need(plan['task'] == 'Perf-01' and plan['performance_credit_seconds'] == 0
         and plan['source_commit'] == CANDIDATE, 'Expected prefix diagnostic plan')
    need(not Path(plan['output']).exists(), 'Execution output must remain fresh')
    bindings = plan['prerequisite_directories']
    b18 = Path(bindings['candidate_b18'])
    completed(b18)
    result = read(b18 / 'assembled/result.json')
    need(result['task'] == 'B18' and result['status'] == 'passed'
         and result['source_commit'] == CANDIDATE and result['native_source_commit'] == NATIVE
         and result['native']['sha256'] == SERVER, 'Matching actual prefix B18 is required')
    for role, commit in (('candidate_build', CANDIDATE), ('current_build', CURRENT)):
        if role not in bindings:
            continue
        directory = Path(bindings[role])
        completed(directory)
        build = read(directory / 'protocols/build.json')
        need(build['product_source_commit'] == commit and build['product_source_dirty'] is False
             and build['native_source_commit'] == NATIVE and build['experiment_only'] is True
             and build['formal_timing_eligible'] is False
             and set(build['server_native_sha256'].values()) == {SERVER},
             'Actual diagnostic producer role/native identity differs: ' + role)
    pending = plan.pop('pending_actual_hashes')
    need(pending and all(plan['inputs_sha256'].get(p) == mark for p, mark in pending.items()),
         'Pending prerequisite inventory differs from the template input map')
    bound = {}
    for name, expected in plan['inputs_sha256'].items():
        actual = sha(name)
        if name in pending:
            need(expected.startswith('PENDING_ACTUAL_'), 'Only explicit future hashes may be filled')
            bound[name] = actual
        else:
            need(actual == expected, 'Previously reviewed input changed: ' + name)
    plan['inputs_sha256'].update(bound)
    plan['bound_actual_hashes'] = bound
    plan['template_sha256'] = sha(args.template)
    plan['binding_helper_sha256'] = sha(__file__)
    plan['status'] = 'prepared-with-actual-prerequisites-no-execution'
    args.output.write_text(json.dumps(plan, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'plan': str(args.output), 'sha256': sha(args.output),
                      'execution_performed': False, 'performance_credit_seconds': 0}))


if __name__ == '__main__':
    main()
