#!/usr/bin/env python3
"""Actual public ABI diagnostic against frozen old/new libraries; no private bridge."""
import argparse
import ctypes as C
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import struct
import threading
import time

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'inputs'
HELPER = INPUT / 'product/tests/Migration.Cpp/abi_probe.py'
spec = importlib.util.spec_from_file_location('abi', HELPER)
abi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(abi)


def encode(value):
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode()


def seq(values):
    return abi.u32(len(values)) + b''.join(abi.u32(len(value)) + value for value in values)


def metadata():
    golden = INPUT / 'product/tests/Query.Binding/golden'
    parent = json.loads((golden / 'parent-model.json').read_text())
    child = json.loads((golden / 'child-model.json').read_text())
    # Column/table IDs depend on names, not scalar type. Use one text key so a
    # canonical key can exceed the registry budget while its metadata still fits.
    parent['columns'][0]['codec'] = 5
    child['columns'][1]['codec'] = 5
    pbytes, cbytes = encode(parent), encode(child)
    phash, chash = hashlib.sha256(pbytes).digest(), hashlib.sha256(cbytes).digest()
    pkey, ckey = parent['projection'][0], child['projection'][1]
    identity = encode({'version': 1, 'parent_model': phash.hex(), 'parent_table': parent['table_id'],
        'child_model': chash.hex(), 'child_table': child['table_id'], 'parent_columns': [pkey],
        'child_columns': [ckey], 'child_nullable': [True]})
    relation = abi.record(23, [(1, 1, abi.u32(parent['table_id'])), (2, 5, phash),
        (3, 1, abi.u32(child['table_id'])), (4, 5, chash), (5, 7, abi.u32(pkey)),
        (6, 7, abi.u32(ckey)), (7, 7, abi.u32(1)), (8, 5, hashlib.sha256(identity).digest())])
    fields, records = [], []
    by_id = {column['id']: column for column in child['columns']}
    for ordinal, identity in enumerate(child['projection']):
        column = by_id[identity]
        fields.append({'ordinal': ordinal, 'name': column['name'], 'codec': column['codec'],
            'codec_config': None, 'nullable': column['nullable']})
        records.append(abi.record(22, [(1, 1, abi.u32(ordinal)), (2, 4, column['name'].encode()),
            (3, 1, abi.u32(column['codec'])), (4, 1, abi.u32(int(column['nullable'])))]))
    projection = abi.record(13, [(1, 5, seq(records)),
        (2, 5, hashlib.sha256(encode({'version': 1, 'fields': fields})).digest())])
    return parent, pbytes, cbytes, relation, projection


def wire(model, model_bytes, profile, columns, values):
    payload = 96 + len(columns) * 40
    result = bytearray(payload + sum(len(value) for value in values))
    result[:4] = b'NWDB'
    struct.pack_into('<HHI', result, 4, 1, 4, 96)
    struct.pack_into('<Q', result, 16, len(result))
    result[24:56] = hashlib.sha256(model_bytes).digest()
    struct.pack_into('<III', result, 56, 1, len(columns), model['table_id'])
    struct.pack_into('<IQQ', result, 76, profile, 96, payload)
    by_id = {column['id']: column for column in model['columns']}
    cursor = payload
    for index, (identity, value) in enumerate(zip(columns, values, strict=True)):
        column = by_id[identity]
        codec = column['codec']
        struct.pack_into('<IHHII', result, 96 + index * 16, identity, codec, int(column['nullable']), codec, 0)
        struct.pack_into('<HHIQQ', result, 96 + len(columns) * 16 + index * 24, codec, 0, codec, cursor, len(value))
        result[cursor:cursor + len(value)] = value
        cursor += len(value)
    return bytes(result)


def complete_any(probe, operation, kind):
    done, terminals = threading.Event(), []

    @abi.Terminal
    def callback(cookie, status, error):
        terminals.append({'status': int(status), 'domain': int(error.contents.domain) if error else 0,
            'code': int(error.contents.code) if error else 0})
        done.set()
        return 0

    callbacks = abi.Callbacks(C.sizeof(abi.Callbacks), 0, 1, callback)
    probe.checked(probe.start, operation, C.byref(callbacks))
    if not done.wait(10) or len(terminals) != 1:
        raise AssertionError('Exactly one terminal callback required: ' + repr(terminals))
    deadline = time.monotonic() + 10
    while True:
        status = probe.retire(operation)
        if status == 0:
            break
        if status != 1 or time.monotonic() >= deadline:
            raise AssertionError('Operation failed to retire: ' + str(status))
        time.sleep(0.001)
    returned, count = abi.Pointer(), None
    if terminals[0]['status'] == 0:
        if kind == 100:
            value = C.c_int64()
            take_count = probe.function('operation_take_count', [abi.Pointer, C.POINTER(C.c_int64), C.POINTER(abi.Error)])
            probe.checked(take_count, operation, C.byref(value))
            count = value.value
        else:
            probe.checked(probe.take_owner, operation, kind, C.byref(returned))
    probe.release_operation(operation)
    return terminals[0], returned, count


def run(args):
    if args.output.exists():
        raise AssertionError('Do not overwrite an executed diagnostic.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    profile = 1 if args.provider == 'sqlite' else 2
    database = args.output.with_suffix('.db')
    if profile == 1:
        with sqlite3.connect(database) as observer:
            observer.executescript('CREATE TABLE "Parents"("Id" TEXT PRIMARY KEY,"Name" TEXT NOT NULL);'
                'CREATE TABLE "Children"("Id" BIGINT PRIMARY KEY,"ParentId" TEXT NULL);'
                'INSERT INTO "Children" VALUES(7,\'parent-1\');')
    probe = abi.Probe(args.library)
    relation_register = probe.function('relation_register', [abi.Pointer, abi.Pointer, abi.Pointer, abi.View, C.POINTER(abi.Pointer), C.POINTER(abi.Error)])
    relation_load = probe.function('relation_load_create', [abi.Pointer, abi.Pointer, abi.View, abi.UInt32, C.POINTER(abi.Pointer), C.POINTER(abi.Error)])
    mutation_create = probe.function('mutation_create', [abi.Pointer, abi.Pointer, abi.UInt32, abi.View, C.POINTER(abi.Pointer), C.POINTER(abi.Error)])
    command_ns = 100_000_000
    maximum = 8192
    values = [1, 8, 5_000_000_000, 64, 65536, 64, 65536, 65536, 4096, 64, 4096, maximum, 32, 4 * 1024 * 1024, command_ns]
    limits = abi.record(10, [(index, 3 if index in (3, 15) else 2, abi.u64(value)) for index, value in enumerate(values, 1)])
    if profile == 1:
        options = abi.record(9, [(1, 1, abi.u32(0)), (2, 1, abi.u32(0)), (3, 1, abi.u32(1)),
            (4, 1, abi.u32(0)), (5, 2, abi.u64(1_000_000)), (6, 1, abi.u32(1))])
        connection = str(database)
    else:
        options = abi.record(8, [(1, 1, abi.u32(1)), (3, 4, b'relation-adapter-review'), (4, 3, abi.u64(5_000_000_000))])
        connection = args.connection
    config = abi.record(1, [(1, 1, abi.u32(1 if profile == 1 else 0)), (2, 4, connection.encode()),
        (3, 5, limits), (4, 5, options), (5, 4, b'relation-adapter-review')])
    source, operation = abi.Pointer(), abi.Pointer()
    probe.checked(probe.create, probe.view(config), C.byref(source))
    probe.checked(probe.open_session, source, C.byref(operation))
    session = probe.complete(operation, 1)
    parent, pbytes, cbytes, relation_data, projection_data = metadata()
    parent_owner, child_owner, relation = abi.Pointer(), abi.Pointer(), abi.Pointer()
    for value, output in [(pbytes, parent_owner), (cbytes, child_owner)]:
        probe.checked(probe.metadata, source, probe.view(abi.record(2, [(1, 5, value), (2, 5, hashlib.sha256(value).digest())])), C.byref(output))
    probe.checked(relation_register, source, parent_owner, child_owner, probe.view(relation_data), C.byref(relation))
    projection = abi.UInt32()
    probe.checked(probe.projection, source, probe.view(projection_data), C.byref(projection))
    key_value = b'k' * 9000 if args.case.startswith('capacity-') else b'parent-1'
    key = wire(parent, pbytes, profile, parent['projection'][:1], [key_value])
    row = wire(parent, pbytes, profile, parent['projection'], [b'parent-1', b'Inserted'])
    payload = abi.record(4, [(1, 1, abi.u32(parent['table_id'])), (2, 5, row)])
    operation, error = abi.Pointer(123), abi.Error(C.sizeof(abi.Error))
    created_at = time.monotonic_ns()
    if args.case.startswith('mutation-'):
        status = mutation_create(session, parent_owner, 0, probe.view(payload), C.byref(operation), C.byref(error))
    else:
        key_view = abi.View(None, 1) if args.case == 'null-key-invalid-projection' else probe.view(key)
        projection_id = 0xffffffff if args.case.endswith('invalid-projection') else projection.value
        status = relation_load(session, relation, key_view, projection_id, C.byref(operation), C.byref(error))
    admission = {'status': int(status), 'domain': int(error.domain), 'code': int(error.code), 'output_nonnull': bool(operation.value)}
    created_duration_ns = time.monotonic_ns() - created_at
    terminal, returned, affected, delay_ns = None, abi.Pointer(), None, 0
    if status == 0:
        wait_started = time.monotonic_ns()
        if args.case.endswith('-delayed'):
            time.sleep(0.3)
        delay_ns = time.monotonic_ns() - wait_started
        terminal, returned, affected = complete_any(probe, operation, 100 if args.case.startswith('mutation-') else 2)
    for owner in [relation, child_owner, parent_owner]:
        probe.release(owner)
    for owner in ([returned] if returned else []) + [session, source]:
        operation = abi.Pointer()
        probe.checked(probe.close, owner, C.byref(operation))
        buffer = probe.complete(operation, 0)
        probe.release_buffer(buffer)
        probe.release(owner)
    deadline = time.monotonic() + 10
    while True:
        counts = [int(probe.count(index)) for index in range(6)]
        if not any(counts):
            break
        if time.monotonic() >= deadline:
            raise AssertionError('Native counts did not return to zero: ' + repr(counts))
        time.sleep(0.001)
    independent = None
    if profile == 1:
        with sqlite3.connect(database) as observer:
            independent = {'parents': observer.execute('SELECT count(*) FROM "Parents"').fetchone()[0],
                'children': observer.execute('SELECT count(*) FROM "Children"').fetchone()[0]}
    inputs = {'parent_model': abi.sha_bytes(pbytes) if hasattr(abi, 'sha_bytes') else hashlib.sha256(pbytes).hexdigest(),
        'child_model': hashlib.sha256(cbytes).hexdigest(), 'relation': hashlib.sha256(relation_data).hexdigest(),
        'projection': hashlib.sha256(projection_data).hexdigest(), 'key_wire': hashlib.sha256(key).hexdigest(),
        'mutation_payload': hashlib.sha256(payload).hexdigest(), 'limits': hashlib.sha256(limits).hexdigest(),
        'provider_options': hashlib.sha256(options).hexdigest()}
    result = {'case': args.case, 'provider': args.provider, 'native_sha256': abi.sha(args.library),
        'probe_sha256': abi.sha(__file__), 'abi_helper_sha256': abi.sha(HELPER), 'frozen_inputs_sha256': abi.sha(INPUT / 'manifest.json'),
        'input_sha256': inputs, 'command_timeout_ns': command_ns, 'maximum_parameter_bytes': maximum,
        'key_wire_bytes': len(key), 'create_duration_ns': created_duration_ns, 'created_to_start_delay_ns': delay_ns,
        'admission': admission, 'terminal': terminal, 'affected': affected, 'retired_counts': counts,
        'independent_sql': independent, 'loaded_library': str(args.library.resolve())}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--provider', choices=['sqlite', 'postgresql'], required=True)
    parser.add_argument('--connection')
    parser.add_argument('--case', choices=['mutation-immediate', 'mutation-delayed', 'relation-immediate', 'relation-delayed',
        'capacity-valid-projection', 'capacity-invalid-projection', 'regular-invalid-projection', 'null-key-invalid-projection'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args())
