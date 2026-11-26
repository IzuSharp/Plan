#!/usr/bin/env python3
"""Independent finite count-conservation controls; never launch a workload."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
BASE = Path('/workspace/scratch/4a65d70f0fe1')
SOURCE = BASE / 'worktrees/DB-Exec-02-continuation'
ANALYZER = Path('/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/recovered-short-evidence/tools/analyze_command_single_v2.py')
OUTPUT = Path('/workspace/scratch/fd78534029f7/native-review/analyzer-independent-extra-02.json')
spec = importlib.util.spec_from_file_location('independent_analyzer', ANALYZER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.load_helpers(SOURCE)
results = []
files = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind(path):
    files[str(path)] = digest(path)
    return json.loads(path.read_bytes())


for provider in ('sqlite', 'postgresql'):
    folder = BASE / 'measurements' / ('ffi-single-command-' + provider + '-01')
    plan, _, _, returns, _ = module.validate_plan(folder, 'diagnostic')
    names = list(returns)
    for case in ('numeric', 'tx-rollback', 'tx-commit'):
        raw = bind(folder / ('diagnostic-' + case + '.json'))
        count = raw['Completed']
        mandatory = {'numeric': 0, 'tx-rollback': 3, 'tx-commit': 4}[case] * count
        maximum = mandatory + (0 if case == 'numeric' else count)

        def set_delta(value, name, number, field='Calls'):
            index = names.index(name)
            value['After']['Ffi'][field][index] = value['Before']['Ffi'][field][index] + number

        def set_commands(value, number):
            for name in ('nw_db_command_request_v1', 'nw_db_command_take_v1'):
                set_delta(value, name, number)
                set_delta(value, name, number, 'OkReturns')
                set_delta(value, name, 0, 'PendingReturns')

        def check(label, value, expected=False):
            error = None
            try:
                found = module.ffi_counts(value, returns, case, count)
                accepted = found['expectedStructure']['status'] == 'matches'
            except (ValueError, TypeError, KeyError, IndexError) as caught:
                accepted = False
                error = str(caught)
            if accepted != expected:
                raise AssertionError(f'{provider}/{case}/{label}: accepted={accepted}, expected={expected}')
            results.append({'provider': provider, 'case': case, 'control': label,
                            'expectedAccepted': expected, 'accepted': accepted, 'error': error})

        check('original', raw, True)
        for label, total in [('minimum', mandatory), ('maximum', maximum)]:
            value = copy.deepcopy(raw)
            set_commands(value, total)
            check(label, value, True)
        value = copy.deepcopy(raw)
        set_commands(value, maximum + 1)
        check('paired-extra-command-beyond-close-bound', value)
        for name in ('nw_db_command_request_v1', 'nw_db_command_take_v1'):
            value = copy.deepcopy(raw)
            set_commands(value, mandatory)
            set_delta(value, name, mandatory + 1)
            set_delta(value, name, mandatory + 1, 'OkReturns')
            check('request-take-skew-' + name, value)

            value = copy.deepcopy(raw)
            total = max(mandatory, 1)
            set_commands(value, total)
            set_delta(value, name, total - 1, 'OkReturns')
            set_delta(value, name, 1, 'PendingReturns')
            check('pending-in-place-of-ok-' + name, value)

            value = copy.deepcopy(raw)
            total = max(mandatory, 1)
            set_commands(value, total)
            set_delta(value, name, total - 1, 'OkReturns')
            check('unaccounted-status-return-' + name, value)

        for name, result in returns.items():
            if not name.startswith('nw_db_operation_'):
                continue
            value = copy.deepcopy(raw)
            set_delta(value, name, 1)
            if result == 'nw_status':
                set_delta(value, name, 1, 'OkReturns')
            check('any-generic-call-' + name, value)
            if result == 'nw_status':
                value = copy.deepcopy(raw)
                set_delta(value, name, 1)
                set_delta(value, name, 1, 'PendingReturns')
                check('any-generic-pending-' + name, value)

        for label, edit in [
            ('short-vector', lambda value: value['After']['Ffi']['Calls'].pop()),
            ('long-vector', lambda value: value['After']['Ffi']['Calls'].append(0)),
            ('negative-counter', lambda value: value['After']['Ffi']['Calls'].__setitem__(0, -1)),
            ('boolean-counter', lambda value: value['After']['Ffi']['Calls'].__setitem__(0, True)),
            ('fraction-counter', lambda value: value['After']['Ffi']['Calls'].__setitem__(0, 0.5)),
            ('decreasing-counter', lambda value: value['Before']['Ffi']['Calls'].__setitem__(0, value['After']['Ffi']['Calls'][0] + 1)),
        ]:
            value = copy.deepcopy(raw)
            edit(value)
            check(label, value)

for path, expected in files.items():
    if digest(Path(path)) != expected:
        raise AssertionError('Original evidence changed: ' + path)
report = {'schemaVersion': 1, 'scope': __doc__, 'analyzerPath': str(ANALYZER),
          'analyzerSha256': digest(ANALYZER), 'controlSourceSha256': digest(Path(__file__)),
          'sourceHelperHashes': {str(path): digest(path) for path in (
              SOURCE / 'benchmarks/db-perf/analysis/strict_io.py',
              SOURCE / 'benchmarks/db-perf/analysis/raw_metrics.py',
              SOURCE / 'src/Data.NativeHost/DataSource.cs')},
          'inputFiles': files, 'originalEvidenceUnchanged': True,
          'controls': results, 'count': len(results), 'passed': True}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({'passed': True, 'count': len(results), 'output': str(OUTPUT)}))
