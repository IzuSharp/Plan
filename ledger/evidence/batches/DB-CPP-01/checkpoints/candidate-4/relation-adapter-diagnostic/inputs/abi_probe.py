#!/usr/bin/env python3
"""Replay actual frozen Rust C ABI rejection results against one SQLite product ELF.

No private test bridge is loaded. Every owner is created, queried and retired
through the unchanged public database ABI. The expected status/domain/code rows
were captured from the immutable Rust provider named in reference.lock.json.
"""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import threading
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GOLDEN = ROOT / 'tests/Query.Binding/golden'
Pointer, UInt32, UInt64 = C.c_void_p, C.c_uint32, C.c_uint64


class View(C.Structure):
    _fields_ = [('data', Pointer), ('length', UInt64)]


class Error(C.Structure):
    _fields_ = [('size', UInt32), ('domain', UInt32), ('code', C.c_int32),
        ('flags', UInt32), ('correlation', UInt64)]


Terminal = C.CFUNCTYPE(UInt32, C.c_size_t, UInt32, C.POINTER(Error))


class Callbacks(C.Structure):
    _fields_ = [('size', UInt32), ('flags', UInt32), ('cookie', C.c_size_t), ('terminal', Terminal)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def record(kind, fields):
    offset = 16 + 16 * len(fields)
    header = bytearray(struct.pack('<HHIII', 1, kind, offset + sum(len(value) for _, _, value in fields), len(fields), 0))
    payload = bytearray()
    for identity, scalar_type, value in fields:
        header += struct.pack('<HHIQ', identity, scalar_type, len(value), offset + len(payload))
        payload += value
    return bytes(header + payload)


def u32(value):
    return struct.pack('<I', value)


def u64(value):
    return struct.pack('<Q', value)


class Probe:
    def __init__(self, path):
        self.path = path.resolve()
        self.library = C.CDLL(str(self.path))
        self.keep = []
        self.results = {}
        output = C.POINTER(Pointer)
        error = C.POINTER(Error)
        token = C.POINTER(UInt64)
        self.create = self.function('source_create', [View, output, error])
        self.open_session = self.function('session_open_create', [Pointer, output, error])
        self.start = self.function('operation_start', [Pointer, C.POINTER(Callbacks), error])
        self.retire = self.function('operation_try_retire', [Pointer])
        self.release_operation = self.function('operation_release', [Pointer], None)
        self.take_owner = self.function('operation_take_owner', [Pointer, UInt32, output, error])
        self.take_buffer = self.function('operation_take_buffer', [Pointer, output, error])
        self.close = self.function('close_create', [Pointer, output, error])
        self.release = self.function('owner_release', [Pointer], None)
        self.release_buffer = self.function('buffer_release', [Pointer], None)
        self.metadata = self.function('metadata_register', [Pointer, View, output, error])
        self.query_create = self.function('query_create', [Pointer, Pointer, UInt32, output, error])
        self.column = self.function('expr_column', [Pointer, UInt64, UInt32, token, error])
        self.value = self.function('expr_value', [Pointer, View, token, error])
        self.clause = self.function('query_clause', [Pointer, UInt32, View, token, error])
        self.parameter = self.function('expr_parameter', [Pointer, UInt32, View, UInt32, UInt32, token, error])
        self.projection = self.function('projection_register', [Pointer, View, C.POINTER(UInt32), error])
        self.codec = self.function('codec_register', [Pointer, UInt32, View, C.POINTER(UInt32), error])
        self.query_import = self.function('query_import', [Pointer, Pointer, UInt32, token, error])
        self.seal = self.function('query_seal', [Pointer, UInt32, output, error])
        self.execute = self.function('execute_create', [Pointer, Pointer, View, output, error])
        self.count = self.function('diagnostic_count', [UInt32], UInt64)

    def function(self, name, arguments, result=UInt32):
        function = getattr(self.library, 'nw_db_' + name + '_v1')
        function.argtypes = arguments
        function.restype = result
        return function

    def view(self, value):
        if not value:
            return View(None, 0)
        buffer = C.create_string_buffer(value)
        self.keep.append(buffer)
        return View(C.cast(buffer, Pointer), len(value))

    @staticmethod
    def checked(function, *arguments):
        error = Error(C.sizeof(Error))
        status = function(*arguments, C.byref(error))
        if status != 0:
            raise AssertionError((function.__name__, status, error.code))

    def complete(self, operation, kind):
        done, statuses = threading.Event(), []

        @Terminal
        def callback(cookie, status, error):
            statuses.append(status)
            done.set()
            return 0

        callbacks = Callbacks(C.sizeof(Callbacks), 0, 1, callback)
        self.checked(self.start, operation, C.byref(callbacks))
        if not done.wait(10) or statuses != [0]:
            raise AssertionError('Terminal callback failed or timed out: ' + repr(statuses))
        deadline = time.monotonic() + 10
        while True:
            status = self.retire(operation)
            if status == 0:
                break
            if status != 1 or time.monotonic() >= deadline:
                raise AssertionError('Native operation did not retire: ' + str(status))
            time.sleep(0.001)
        output = Pointer()
        if kind:
            self.checked(self.take_owner, operation, kind, C.byref(output))
        else:
            self.checked(self.take_buffer, operation, C.byref(output))
        self.release_operation(operation)
        return output

    def reject(self, name, function, output_type, *arguments):
        output, error = output_type(123), Error(C.sizeof(Error))
        status = function(*arguments, C.byref(output), C.byref(error))
        self.results[name] = {'status': int(status), 'domain': int(error.domain), 'code': int(error.code), 'output': int(output.value or 0)}
        if status == 0:
            raise AssertionError('A fixed rejection was admitted: ' + name)

    def run(self):
        values = [1, 8, 5_000_000_000, 64, 65536, 64, 65536, 65536, 4096, 64, 4096, 4 * 1024 * 1024, 32, 4 * 1024 * 1024, 5_000_000_000]
        limits = record(10, [(index, 3 if index in (3, 15) else 2, u64(value)) for index, value in enumerate(values, 1)])
        options = record(9, [(1, 1, u32(3)), (2, 1, u32(2)), (3, 1, u32(1)), (4, 1, u32(0)), (5, 2, u64(1_000_000)), (6, 1, u32(1))])
        config = record(1, [(1, 1, u32(1)), (2, 4, b':memory:'), (3, 5, limits), (4, 5, options), (5, 4, b'abi-status-reference')])
        source, operation = Pointer(), Pointer()
        self.checked(self.create, self.view(config), C.byref(source))
        self.checked(self.open_session, source, C.byref(operation))
        session = self.complete(operation, 1)
        model_bytes = (GOLDEN / 'parent-model.json').read_bytes()
        model, query = Pointer(), Pointer()
        self.checked(self.metadata, source, self.view(record(2, [(1, 5, model_bytes), (2, 5, hashlib.sha256(model_bytes).digest())])), C.byref(model))
        self.checked(self.query_create, session, model, json.loads(model_bytes)['table_id'], C.byref(query))
        self.reject('unknown-column', self.column, UInt64, query, 0, 123)
        self.reject('empty-clause', self.clause, UInt64, query, 1, self.view(b''))
        self.reject('malformed-clause', self.clause, UInt64, query, 1, self.view(b'\x00' * 16))
        self.reject('empty-value', self.value, UInt64, query, self.view(b''))
        malformed = bytearray((GOLDEN / 'value.bin').read_bytes()); malformed[0] ^= 1
        self.reject('malformed-value-wire', self.value, UInt64, query, self.view(bytes(malformed)))
        self.reject('borrow-null-value', self.value, UInt64, query, View(None, 1))
        self.reject('borrow-null-clause', self.clause, UInt64, query, 1, View(None, 1))
        self.reject('borrow-oversize-value', self.value, UInt64, query, View(None, 16 * 1024 * 1024 + 1))
        self.reject('wrong-query-owner', self.column, UInt64, source, 0, 123)
        self.reject('null-query-owner', self.column, UInt64, None, 0, 123)
        self.reject('parameter-invalid-nullable', self.parameter, UInt64, query, 1, self.view(b'p'), 3, 2)
        self.reject('parameter-invalid-utf8', self.parameter, UInt64, query, 1, self.view(b'\xff'), 3, 0)
        self.reject('parameter-unknown-codec', self.parameter, UInt64, query, 1, self.view(b'p'), 999, 0)
        self.reject('parameter-invalid-name', self.parameter, UInt64, query, 1, self.view(b'9bad'), 3, 0)
        self.reject('wrong-import-kind', self.query_import, UInt64, query, source, 99)
        self.reject('projection-malformed', self.projection, UInt32, source, self.view(b''))
        self.reject('projection-empty-sequence', self.projection, UInt32, source, self.view(record(13, [(1, 5, u32(0)), (2, 5, b'\x00' * 32)])))
        self.reject('projection-oversize-sequence', self.projection, UInt32, source, self.view(record(13, [(1, 5, u32(4097)), (2, 5, b'\x00' * 32)])))
        self.reject('projection-null-borrow', self.projection, UInt32, source, View(None, 1))
        self.reject('codec-invalid-logical', self.codec, UInt32, source, 999, self.view(b''))
        self.reject('codec-wrong-owner-and-utf8', self.codec, UInt32, session, 3, self.view(b'\xff'))
        self.reject('codec-wrong-owner-and-null-borrow', self.codec, UInt32, session, 3, View(None, 1))
        plan = Pointer()
        self.checked(self.seal, query, 4, C.byref(plan))
        self.reject('plan-malformed-parameters', self.execute, Pointer, session, plan, self.view(b''))
        self.reject('plan-null-borrow', self.execute, Pointer, session, plan, View(None, 1))
        for owner in (plan, query, model):
            self.release(owner)
        for owner in (session, source):
            operation = Pointer()
            self.checked(self.close, owner, C.byref(operation))
            buffer = self.complete(operation, 0)
            self.release_buffer(buffer)
            self.release(owner)
        deadline = time.monotonic() + 10
        while True:
            counts = [self.count(index) for index in range(6)]
            if not any(counts):
                return counts
            if time.monotonic() >= deadline:
                raise AssertionError('Native owners did not retire: ' + repr(counts))
            time.sleep(0.001)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-library', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    probe = Probe(args.native_library)
    counts = probe.run()
    expected = json.loads((HERE / 'abi-status.expected.json').read_text())
    differences = sorted(name for name in set(expected['cases']) | set(probe.results) if expected['cases'].get(name) != probe.results.get(name))
    result = {'passed': not differences, 'library': str(probe.path), 'native_sha256': sha(probe.path),
        'probe_sha256': sha(__file__), 'expected_sha256': sha(HERE / 'abi-status.expected.json'),
        'inputs_sha256': {name: sha(GOLDEN / name) for name in ('parent-model.json', 'value.bin')},
        'reference': expected['reference'], 'cases': probe.results, 'differences': differences, 'retired_counts': counts}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    if differences:
        raise AssertionError('Frozen Rust ABI error contract changed: ' + ', '.join(differences))
    print('PASS actual database C ABI: ' + str(len(probe.results)) + ' frozen rejection cases; all six native counts zero')


if __name__ == '__main__':
    main()
