#!/usr/bin/env python3
"""Reconcile completed channel ABI and mapper-scope receipts; never run workloads."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--tag', required=True, help='actual consumer/measurement directory tag')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    inputs, ffi, allocations = {}, [], []

    def digest(path):
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()

    def read(path):
        path = path.resolve()
        data = path.read_bytes()
        inputs[str(path)] = hashlib.sha256(data).hexdigest()
        return json.loads(data)

    for provider in ('sqlite', 'postgresql'):
        build = read(root / f'consumers/ffi-{args.tag}-{provider}/diagnostic-build.json')
        assert build['timingCredit'] is False and build['allocationCredit'] is False
        assert build['nativeImagesUnchanged'] is True
        names = build['symbols']
        assert len(names) == len(set(names))
        for rows in (1, 100, 1000):
            name = f'candidate-rows{rows}'
            folder = root / f'measurements/ffi-{args.tag}-{provider}-01'
            command = read(folder / (name + '.command.json'))
            assert command['success'] and command['exitCode'] == 0 and not command['observerErrors']
            data = read(folder / (name + '.json'))
            assert data['ResultRows'] == rows
            assert all(data['Drained'][key] == 0 for key in
                       ('Sources', 'Sessions', 'Operations', 'Cursors', 'Buffers', 'Owners', 'PullChannels'))
            for route in ('fluent', 'prepared', 'host-sql'):
                windows = [item for item in data['Windows'] if item['Route'] == route]
                count = sum(item['Operations'] for item in windows)
                calls, pending = [0] * len(names), [0] * len(names)
                sql = protocol = 0
                poll = {key: 0 for key in ('ProviderPollCalls', 'ProviderPollTimeouts', 'ProviderPollErrors', 'ProviderPollNanoseconds')}
                for window in windows:
                    before, after = window['NativeBefore'], window['NativeAfter']
                    sql += after['SqlExecutions'] - before['SqlExecutions']
                    protocol += after['ProtocolSubmissions'] - before['ProtocolSubmissions']
                    for target, key in ((calls, 'Calls'), (pending, 'PendingReturns')):
                        assert len(before['Ffi'][key]) == len(after['Ffi'][key]) == len(names)
                        for index in range(len(names)):
                            delta = after['Ffi'][key][index] - before['Ffi'][key][index]
                            assert delta >= 0
                            target[index] += delta
                    for key in poll:
                        poll[key] += after['Ffi'][key] - before['Ffi'][key]
                measured = dict(zip(names, calls))
                assert sql == count
                assert measured['nw_db_operation_start_v1'] == measured['nw_db_operation_try_retire_v1'] == 0
                assert measured['nw_db_close_create_v1'] == measured['nw_db_cursor_fetch_create_v1'] == 0
                assert measured['nw_db_cursor_pull_close_request_v1'] == measured['nw_db_cursor_pull_close_take_v1'] == count
                expected = (rows + 31) // 32
                assert measured['nw_db_cursor_pull_request_v1'] == measured['nw_db_cursor_pull_take_v1'] == expected * count
                ffi.append(dict(provider=provider, rows=rows, route=route, operations=count,
                    calls=measured, pendingReturns=dict(zip(names, pending)), callsPerOperation=sum(calls) / count,
                    sqlExecutions=sql, protocolSubmissions=protocol, providerPoll=poll))

            folder = root / f'measurements/allocation-{args.tag}-{provider}-01'
            command = read(folder / (name + '.command.json'))
            assert command['success'] and command['exitCode'] == 0 and not command['observerErrors']
            base_path = folder / (name + '.json')
            base = read(base_path)
            data = read(folder / (name + '.json.allocation.json'))
            assert data['NativeAot'] and not data['TimingCredit'] and not data['Failed']
            assert data['BaseReceiptSha256'] == digest(base_path)
            build_path = Path(data['BuildReceiptPath'])
            assert data['BuildReceiptSha256'] == digest(build_path)
            read(build_path)
            ordinary = {(item['Route'], item['Index']): item for item in base['Windows']}
            for window in data['Windows']:
                paired = ordinary[(window['Route'], window['Index'])]
                count = window['Operations']
                assert count == paired['Operations'] and window['RowsPerOperation'] == rows
                assert window['MapperCalls'] == window['ListAddCalls'] == count * rows
                assert window['ListConstructorCalls'] == count and window['FrameworkOnlyBytes'] is None
                assert window['ProcessAllocatedBytes'] == paired['AllocatedAfter'] - paired['AllocatedBefore']
                assert all(window['ProcessGen' + str(gen)] == paired['Gen' + str(gen)] for gen in (0, 1, 2))
                allocations.append(dict(provider=provider, rows=rows, **window,
                    observedMapperAndListBytesPerOperation=window['ObservedMapperAndListBytes'] / count))

    assert all(digest(Path(path)) == expected for path, expected in inputs.items())
    result = dict(schemaVersion=1, tag=args.tag, timingCredit=False, frameworkOnlyBytes=None,
        scope='Separate instrumented processes. ABI calls, SQL submissions and OS poll waits are distinct; no RTT inference or subtraction from uninstrumented allocation.',
        inputs=inputs, ffi=ffi, allocationWindows=allocations)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(ffiRoutes=len(ffi), allocationWindows=len(allocations), stableInputs=len(inputs))))


if __name__ == '__main__':
    main()
