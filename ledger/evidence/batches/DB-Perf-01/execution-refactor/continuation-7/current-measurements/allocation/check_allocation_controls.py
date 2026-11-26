#!/usr/bin/env python3
"""Finite in-memory controls for the adapted allocation counters and owners."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Never overwrite a control result')
    path = Path(__file__).with_name('audit_current_allocation.py')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('allocation_controls_target', path)
    target = importlib.util.module_from_spec(spec); spec.loader.exec_module(target)
    outcomes = []
    def check(label, expected, call):
        try:
            call(); actual = True
        except (ValueError, KeyError, TypeError):
            actual = False
        if actual != expected:
            raise AssertionError(label + ' produced unexpected acceptance=' + str(actual))
        outcomes.append({'case': label, 'accepted': actual, 'expected': expected})
    def sample(rows=1):
        native = {name: 0 for name in target.OWNERS}
        native.update(Sources=1, Sessions=1, Owners=4, SqlExecutions=100)
        after = dict(native, SqlExecutions=356)
        original = {'Route': 'fluent', 'Index': 0, 'Operations': 256, 'AllocatedBefore': 1000,
                    'AllocatedAfter': 11000, 'Gen0': 1, 'Gen1': 0, 'Gen2': 0,
                    'Samples': [{'Rows': rows} for _ in range(256)], 'NativeBefore': native, 'NativeAfter': after}
        window = {field: 0 for field in target.FIELDS}
        window.update(Route='fluent', Index=0, Operations=256, RowsPerOperation=rows,
                      ProcessAllocatedBefore=1000, ProcessAllocatedAfter=11000, ProcessAllocatedBytes=10000,
                      ProcessGen0=1, MapperCalls=256 * rows, ListConstructorCalls=256, ListAddCalls=256 * rows,
                      MapperBytes=3000, ListConstructorBytes=1000, ListAddBytes=2000,
                      ObservedMapperAndListBytes=6000, FrameworkOnlyBytes=None)
        return window, original
    for rows in target.ROWS:
        for candidate in (False, True):
            w, o = sample(rows)
            check(f'positive-{rows}-{candidate}', True, lambda: target.window_check(w, o, rows, candidate))
    for field in target.FIELDS:
        for invalid in (-1, False, 0.0, None, '0'):
            w, o = sample(); w[field] = invalid
            check(f'numeric-{field}-{invalid!r}', False, lambda: target.window_check(w, o, 1, True))
    for field in ('MapperCalls', 'ListConstructorCalls', 'ListAddCalls', 'ObservedMapperAndListBytes',
                  'ProcessAllocatedBytes', 'ProcessAllocatedBefore', 'ProcessAllocatedAfter', 'RowsPerOperation', 'Index'):
        w, o = sample(); w[field] += 1
        check('skew-' + field, False, lambda: target.window_check(w, o, 1, True))
    for value in (0, 1, False, 'null'):
        w, o = sample(); w['FrameworkOnlyBytes'] = value
        check('framework-' + repr(value), False, lambda: target.window_check(w, o, 1, True))
    for value in (False, 0.0, None, '0'):
        w, o = sample(); o['Index'] = value
        check('original-index-' + repr(value), False, lambda: target.window_check(w, o, 1, True))
    for mutation, edit in [
        ('missing-sample', lambda o: o['Samples'].pop()),
        ('wrong-row', lambda o: o['Samples'][0].update(Rows=2)),
        ('bool-row', lambda o: o['Samples'][0].update(Rows=True)),
        ('sql-skew', lambda o: o['NativeAfter'].update(SqlExecutions=357)),
        ('gc-skew', lambda o: o.update(Gen0=2)),
        ('gc-bool', lambda o: o.update(Gen1=False)),
        ('allocation-reversed', lambda o: o.update(AllocatedAfter=1)),
        ('missing-framework', lambda o: None),
    ]:
        w, o = sample(); edit(o)
        if mutation == 'missing-framework':
            del w['FrameworkOnlyBytes']
        check(mutation, False, lambda: target.window_check(w, o, 1, True))
    for name in target.OWNERS:
        for invalid in (1, -1, False, 0.0, None, '0'):
            native = {owner: 0 for owner in target.OWNERS}; native[name] = invalid
            check('drained-' + name + '-' + repr(invalid), False, lambda: target.owner_check(native, True))
        native = {owner: 0 for owner in target.OWNERS}; del native[name]
        check('missing-' + name, False, lambda: target.owner_check(native, True))
    check('valid-drained', True, lambda: target.owner_check({owner: 0 for owner in target.OWNERS}, True))
    for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}'):
        check('strict-json-' + text, False, lambda: target.strict(text))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = {'status': 'passed', 'scriptSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'controls': len(outcomes), 'outcomes': outcomes, 'productExecutions': 0,
              'measurementFilesRead': 0, 'hashSweeps': 0, 'timingCredit': False}
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'outcomes'}))


if __name__ == '__main__':
    main()
