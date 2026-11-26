#!/usr/bin/env python3
"""Finite offline boundary controls over copies of retained diagnostic JSON.

No consumer, database, benchmark, original evidence mutation or CI action.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analyzer', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a fresh output')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('reviewed_command_analyzer', args.analyzer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.load_helpers(args.source)
    results = []
    sources = {}

    def read(path):
        data = path.read_bytes()
        sources[str(path)] = hashlib.sha256(data).hexdigest()
        return json.loads(data)

    for provider in ('sqlite', 'postgresql'):
        folder = args.root / 'measurements' / ('ffi-single-command-' + provider + '-01')
        plan, manifest, connection, returns, _ = module.validate_plan(folder, 'diagnostic')
        names = list(returns)
        for case in ('numeric', 'tx-rollback', 'tx-commit'):
            item = next(x for x in plan['commands'] if x['name'] == 'diagnostic-' + case)
            raw = read(folder / (item['name'] + '.json'))
            count = raw['Completed']
            mandatory = {'numeric': 0, 'tx-rollback': 3, 'tx-commit': 4}[case] * count
            optional = 0 if case == 'numeric' else count

            def delta(value, name, field='Calls'):
                index = names.index(name)
                return value['After']['Ffi'][field][index] - value['Before']['Ffi'][field][index]

            def set_delta(value, name, number, field='Calls'):
                index = names.index(name)
                value['After']['Ffi'][field][index] = value['Before']['Ffi'][field][index] + number

            def command_count(value, number):
                for name in ('nw_db_command_request_v1', 'nw_db_command_take_v1'):
                    for field in ('Calls', 'OkReturns'):
                        set_delta(value, name, number, field)

            def check(label, value, expected, whole=False):
                caught = None
                try:
                    if whole:
                        original = module.raw_receipt
                        try:
                            module.raw_receipt = lambda *_: value
                            observed = module.analyze_command(folder, plan, item, manifest, connection, returns)
                            accepted = observed['status'] == 'valid'
                        finally:
                            module.raw_receipt = original
                    else:
                        observed = module.ffi_counts(value, returns, case, count)
                        accepted = observed['expectedStructure']['status'] == 'matches'
                except (ValueError, TypeError, KeyError, IndexError) as error:
                    accepted = False
                    caught = str(error)
                if accepted is not expected:
                    raise AssertionError(provider + '/' + case + '/' + label + ': unexpected acceptance')
                results.append({'provider': provider, 'case': case, 'control': label,
                                'expectedAccepted': expected, 'accepted': accepted, 'error': caught})

            check('original-real-evidence', raw, True, whole=True)
            for label, number in [('zero-conditional-close', mandatory), ('all-conditional-close', mandatory + optional)]:
                value = copy.deepcopy(raw)
                command_count(value, number)
                check(label, value, True)
            if case != 'numeric':
                value = copy.deepcopy(raw)
                command_count(value, mandatory + count // 2)
                check('some-conditional-close', value, True)
                value = copy.deepcopy(raw)
                command_count(value, mandatory - 1)
                check('missing-mandatory-command', value, False)
            value = copy.deepcopy(raw)
            command_count(value, mandatory + optional + 1)
            check('more-than-one-child-close', value, False)
            for name in ('nw_db_command_request_v1', 'nw_db_command_take_v1'):
                value = copy.deepcopy(raw)
                if case == 'numeric':
                    set_delta(value, name, 1)
                    set_delta(value, name, 1, 'OkReturns')
                else:
                    set_delta(value, name, delta(value, name) - 1, 'OkReturns')
                check('unmatched-or-non-ok-' + name, value, False)
            for name in ('nw_db_command_take_error_v1', 'nw_db_command_cancel_v1',
                         'nw_db_operation_start_v1', 'nw_db_close_create_v1'):
                value = copy.deepcopy(raw)
                set_delta(value, name, 1)
                set_delta(value, name, 1, 'OkReturns')
                check('unexpected-' + name, value, False)
            value = copy.deepcopy(raw)
            set_delta(value, 'nw_db_operation_try_retire_v1', 1)
            set_delta(value, 'nw_db_operation_try_retire_v1', 1, 'PendingReturns')
            check('generic-retirement-pending', value, False)
            for field in ('Sources', 'Sessions', 'Operations', 'Cursors', 'Buffers', 'Owners', 'PullChannels', 'CommandCompletions'):
                value = copy.deepcopy(raw)
                value['Drained'][field] = 1
                check('leaked-' + field, value, False, whole=True)
            for label, key, new in [('business-error', 'Errors', ['synthetic negative control']),
                                    ('failed-operation', 'Failed', 1), ('sticky-oracle', 'OracleFailuresAfter', 1),
                                    ('false-owner-zero', 'OwnersReturnedToZero', False)]:
                value = copy.deepcopy(raw)
                value[key] = new
                check(label, value, False, whole=True)
    for path, digest in sources.items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest:
            raise AssertionError('Original evidence changed: ' + path)
    result = {'schemaVersion': 1, 'scope': __doc__, 'analyzer': str(args.analyzer.resolve()),
              'analyzerSha256': hashlib.sha256(args.analyzer.read_bytes()).hexdigest(),
              'controlSourceSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'inputFiles': sources, 'originalEvidenceUnchanged': True,
              'controls': results, 'count': len(results), 'passed': True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'count': len(results), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
