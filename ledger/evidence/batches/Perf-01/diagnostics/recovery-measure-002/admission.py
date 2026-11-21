"""Explicit epoch-002 measurement admission; no timing or workload implementation."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BEFORE = 'ea5fa528035d025bd7a28698ee7c71194432236c'
DRIVER = '2e3995df8d86583ee9443348276ca8d918056bfc'
ROUTES = {'before': 'nativeweave-aot-rust', 'after': 'nativeweave-aot-rust',
          'direct': 'direct-rust', 'managed': 'managed-aot'}
CODEC_ROUTES = {'before': 'nativeweave', 'after': 'nativeweave', 'direct': 'direct-rust', 'managed': 'managed-zlib'}


def need(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def confined(root, value):
    path = Path(value)
    need(not path.is_absolute() and '..' not in path.parts, 'Root-relative admission path required')
    result = (root / path).resolve()
    need(result.is_relative_to(root), 'Admission path escapes root')
    return result


class Context:
    def __init__(self, root, path, expected, source_index_sha256, final_binding=None, final_binding_sha256=None):
        sys.dont_write_bytecode = True
        need(sys.version_info[:3] == (3, 12, 14) and platform.system() == 'Linux'
             and platform.machine() == 'x86_64', 'Exact Python/Linux x64 required')
        self.root, self.path = Path(root).resolve(strict=True), Path(path).resolve(strict=True)
        self.sha256, self.index_sha256 = expected, source_index_sha256
        need(sha(self.path) == expected and sha(HERE / 'measurement-sources.json') == source_index_sha256,
             'Measurement admission/source index changed')
        self.value, self.index = read(self.path), read(HERE / 'measurement-sources.json')
        need(self.value['epoch'] == 'recovery-002' and self.value['selected_final_commit'] is None,
             'Keep the before admission immutable; final identity is a separate explicit binding')
        self.selected, self.final_binding = None, None
        self.plan = confined(self.root, self.value['plan'])
        self.batch = self.plan / 'ledger/evidence/batches/Perf-01'
        self.pins = {str(self.path): expected, str(HERE / 'measurement-sources.json'): source_index_sha256}
        final = None
        if final_binding is not None:
            need(final_binding_sha256 and sha(final_binding) == final_binding_sha256, 'Final binding identity differs')
            final = read(final_binding)
            need(final['epoch'] == 'recovery-002' and final['before_admission_sha256'] == expected
                 and re.fullmatch('[0-9a-f]{40}', final['selected_final_commit']), 'Final binding does not name this exact baseline context')
            self.selected = final['selected_final_commit']
            self.final_binding = dict(path=str(Path(final_binding).resolve()), sha256=final_binding_sha256)
            self.pin(final_binding, final_binding_sha256)
        for name, digest in self.index['files_sha256'].items():
            self.pin(HERE / name, digest)
        for name, digest in self.index['plan_source_sha256'].items():
            self.pin(self.batch / name, digest)
        self.build_input_path, self.inputs = self.document(self.value['build_inputs'])
        build_index_path, build_index = self.document(self.value['build_source_index'])
        need(self.inputs['epoch'] == 'recovery-002' and self.inputs['products']['before']['commit'] == BEFORE
             and self.inputs['products']['after']['commit'] is None, 'Wrong build input roles')
        for name, digest in build_index['files_sha256'].items():
            self.pin(build_index_path.parent / name, digest)
        original = build_index_path.parent.parent / 'recovery-build-001'
        for name, digest in build_index['reused_control_sha256'].items():
            self.pin(original / name, digest)
        sys.path.insert(0, str(original))
        self.build = module('perf01_epoch002_original_build', original / 'build.py')
        self.bindings, self.owner = self.build.bindings, sys.modules['owner']
        self.build_caller = module('perf01_epoch002_build_caller', build_index_path.parent / 'run.py')
        self.driver = confined(self.root, self.inputs['driver'])
        self.build.source(self.driver, DRIVER)
        for name, digest in self.index['native_source_sha256'].items():
            self.pin(self.driver / name, digest)
        _, self.freeze = self.document(self.inputs['freeze'])
        need(self.freeze['epoch'] == 'recovery-002' and self.freeze['baseline_product_commit'] == BEFORE
             and self.freeze['driver_checkout_commit'] == DRIVER
             and self.freeze['selected_final_runtime_commit'] in (None, self.selected), 'Wrong frozen source roles')
        self.boot = hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_bytes().strip()).hexdigest()
        need(self.boot == self.freeze['machine']['kernel_boot_sha256'], 'Host boot changed')
        _, self.toolchain = self.document(self.inputs['toolchain'])
        need(self.toolchain['ready'] is True, 'Complete toolchain restoration required')
        for row in self.toolchain['tools'].values():
            self.pin(row['path'], row['invocation_path_sha256'])
            self.pin(row['executable_path'], row['executable_sha256'])
        for rows in self.toolchain['actual_dynamic_dependencies_sha256'].values():
            for name, digest in rows.items():
                self.pin(name, digest)
        self.python = self.toolchain['tools']['python']['path']
        need(Path(sys.executable).resolve() == Path(self.toolchain['tools']['python']['executable_path']), 'Wrong executing Python')
        _, dependencies = self.document(self.inputs['python_dependencies'])
        need({k: v['version'] for k, v in dependencies['metadata'].items()} == self.build_caller.PYTHON_VERSIONS,
             'Python client dependency versions changed')
        python_path = Path(dependencies['environment']['PYTHONPATH'])
        for name, digest in dependencies['installed_files_sha256'].items():
            self.pin(python_path / name, digest)
        for name, digest in dependencies['runtime_files_sha256'].items():
            self.pin(name, digest)
        self.inputs.update(_sha256=self.value['build_inputs']['sha256'],
                           _source_index_sha256=self.value['build_source_index']['sha256'], _tools=self.toolchain['tools'])
        self.built, self.build_proofs = {}, {}
        receipts = dict(self.value['build_receipts'])
        need(set(receipts) == {'before', 'common'}, 'Base admission binds only the actual before/common producers')
        self.functional_inputs = dict(self.value['functional'])
        need(set(self.functional_inputs) == {'before'}, 'Base admission binds actual functional-before only')
        if final is not None:
            receipts['after'] = final['after_build_receipt_sha256']
            self.functional_inputs['after'] = final['functional_after']
        for role, digest in receipts.items():
            proof, bound = self.build.completed(self.root, self.inputs, role, digest)
            self.build_proofs[role], self.built[role] = proof, bound
        if final is not None:
            self.build_caller.paired(self.built['before'], self.built['after'], self.selected)
        roles = {'before': BEFORE, **({'after': self.selected} if final is not None else {})}
        self.products = {role: confined(self.root, self.inputs['products'][role]['path']) for role in roles}
        for role, commit in roles.items():
            need(self.built[role]['status'] == 'built-and-bound' and self.built[role]['product_commit'] == commit
                 and self.built[role]['driver_commit'] == DRIVER
                 and self.built[role]['selected_b24_version'] == self.inputs['products'][role]['version'],
                 'Actual producer binding differs from the selected runtime/common source roles')
            self.build.source(self.products[role], commit)
            for name, digest in self.freeze['product_locks_sha256'].items():
                self.pin(self.products[role] / name, digest)
            self.functional(role, commit)
        self.output = confined(self.root, self.value['output'])
        self.reservation = confined(self.root, self.inputs['exclusive_lock'])
        self.timing_lock = confined(self.root, self.value['protocol_timing_lock'])
        need(self.reservation != self.timing_lock, 'Protocol child timing lock must differ from the outer/build reservation')
        self.policy_path, self.policy = self.document(self.value['policy'])
        need(self.value['policy']['sha256'] == self.freeze['effective_policy_sha256'], 'Changed capacity/resource policy')
        self.workload_path = self.batch / 'reproduction/workloads-001/workloads.json'
        self.pin(self.workload_path, self.freeze['workload_bundle_sha256'])
        self.workloads = read(self.workload_path)
        need(self.workloads['long_groups'] == self.freeze['long_groups'], 'Inherited fixed long configurations changed')
        self.certificate, _ = self.file(self.value['tls']['certificate'])
        self.private_key, _ = self.file(self.value['tls']['private_key'])
        self.build_root = confined(self.root, self.inputs['output'])
        self.corpus = self.build_root / 'common/codec-corpus'
        for role in roles:
            for name in ('reference/progress.json', 'db-observer/manifest.json', 'protocols/build.json', 'codec/manifest.json'):
                path = self.build_root / role / name
                self.pin(path, self.built[role]['files_sha256'][str(path)])
        for name in ('protocols/build.json', 'database/comparators.json', 'codec-corpus/manifest.json'):
            path = self.build_root / 'common' / name
            self.pin(path, self.built['common']['files_sha256'][str(path)])
        self.pg = Path(self.toolchain['tools']['postgres']['path']).parent
        self.environment = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME', 'SSL_CERT_FILE', 'SSL_CERT_DIR') if k in os.environ}
        self.environment.update(self.toolchain['environment'])
        self.environment.update(self.inputs['build_environment'])
        self.environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(python_path))
        self.a21_path = self.driver / 'src/Benchmarks.Harness/nativeweave_bench.py'
        self.a21 = module('perf01_epoch002_a21', self.a21_path)
        self.reader = module('perf01_epoch002_long_reader', self.driver / 'tests/Perf01/verify_long.py')
        self.db_reader = module('perf01_epoch002_database_reader', HERE / 'readers/database_compare.py')
        self.protocol_reader = module('perf01_epoch002_protocol_reader', self.batch / 'protocol_compare.py')
        self.codec_reader = module('perf01_epoch002_codec_reader', self.batch / 'codec_compare.py')
        self.gc = module('perf01_epoch002_gc', self.driver / 'tests/Perf01.Database/scheduler_gc.py')
        self.database_controller = module('perf01_epoch002_database_commands', self.batch / 'database_observer_calibrate.py')
        self.sampling = self.database_controller.sampling_descriptor(self.driver, 'threaded')
        self.gc_policy = self.gc.policy('deferred')

    def pin(self, path, expected):
        path = Path(path).resolve(strict=True)
        need(sha(path) == expected, 'Bound file changed: ' + str(path))
        self.pins[str(path)] = expected
        return path

    def file(self, descriptor):
        path = confined(self.root, descriptor['path'])
        self.pin(path, descriptor['sha256'])
        return path, descriptor['sha256']

    def document(self, descriptor):
        path, _ = self.file(descriptor)
        return path, read(path)

    def functional(self, role, commit):
        path, record = self.document(self.functional_inputs[role])
        need(record['stage'] == 'functional-' + role and record['status'] == 'completed'
             and record['inputs_sha256'] == self.value['build_inputs']['sha256']
             and record['source_index_sha256'] == self.value['build_source_index']['sha256']
             and record['freeze_sha256'] == self.inputs['freeze']['sha256']
             and record['toolchain_sha256'] == self.inputs['toolchain']['sha256'], 'Wrong actual B18 execution')
        output = confined(self.root, self.inputs['output']) / ('functional-' + role)
        rows, native = self.build_caller.functional_plan(self.products[role], commit, output, self.built[role],
                                                       self.toolchain['tools'], confined(self.root, self.inputs['design']))
        need(record['planned_commands'] == rows and len(record['commands']) == 2, 'B18 command recipe differs')
        for planned, actual in zip(rows, record['commands'], strict=True):
            child = self.pin(actual['path'], actual['sha256'])
            observed = read(child)
            need(observed['status'] == 'completed' and observed['retired'] and observed['exit_code'] == 0
                 and all(observed[k] == v for k, v in planned.items()), 'B18 command did not complete/retire exactly')
            for name, digest in observed['logs_sha256'].items():
                self.pin(child.parent / name, digest)
        bound = path.parent / 'binding.json'
        self.pin(bound, record['binding_sha256'])
        value = read(bound)
        need(value['status'] == 'functional-bound' and value['product_commit'] == commit
             and value['native_asset'] == native and value['functional_scope'] == 'B18 only', 'B18 role/native binding differs')
        self.bindings.Binding().mapping(value['files_sha256'])

    def stable(self):
        for name, digest in self.pins.items():
            need(sha(name) == digest, 'Admission/source/input changed: ' + name)
        need(hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_bytes().strip()).hexdigest() == self.boot, 'Host boot changed')
        self.build.source(self.driver, DRIVER)
        self.build.source(self.products['before'], BEFORE)
        if self.selected is not None:
            self.build.source(self.products['after'], self.selected)

    def protocol_build(self, role):
        return self.build_root / ('common' if role == 'direct' else role) / 'protocols/build.json'

    def codec_build(self, role):
        return self.build_root / ('after' if role == 'after' else 'before') / 'codec/manifest.json'

    def db_args(self, role):
        from types import SimpleNamespace
        selected = 'after' if role == 'after' else 'before'
        return SimpleNamespace(nativeweave=self.driver, package_probe=self.build_root / selected / 'reference',
            observer=self.build_root / selected / 'db-observer/manifest.json',
            comparators=self.build_root / 'common/database/comparators.json', postgres_bin=self.pg,
            variant=role, scheduler_gc_policy='deferred', resource_sampling_policy='threaded',
            isolation_note='Perf-01 recovery-002: one owned process tree; service/database CPUs2,3; generator CPUs0,1')

    def check_db(self, path, role, passing=True):
        value = self.db_reader.read_cell(path, role, self.a21, self.reader, sha(self.a21_path))
        summary, frozen = read(path / 'summary.json'), read(path / 'frozen-inputs.json')
        plan = read(path / 'plan.json')
        need(frozen['compact_observation'] is True and plan['settings']['features']['compact_observation'] is True
             and frozen['driver_source']['commit'] == DRIVER and frozen['driver_source']['scope_status'] == '',
             'DB actual common driver/compact observation differs')
        expected = read(self.db_args(role).observer)['artifacts'] if role in ('before', 'after') else read(self.db_args(role).comparators)['routes'][ROUTES[role]]['artifacts']
        loaded = summary['loaded_files']
        need(loaded and all(expected.get(name) == item['sha256'] for name, item in loaded.items()), 'DB mapped files differ from this exact role/route')
        need(frozen['route']['command'][0] in loaded, 'DB actual executable missing')
        if role in ('before', 'after'):
            engines = {x['engineId']: x['sha256'] for x in self.built[role]['native_assets']}
            actual = {item['sha256'] for item in loaded.values()}
            need({engines['server'], engines['database.' + summary['provider']]} <= actual, 'DB provider/Server native role assets absent')
        closed = summary['closed'] or {}
        app_path = Path(summary['application_receipt']['path'])
        need(sha(app_path) == summary['application_receipt']['sha256'], 'DB application receipt changed')
        app = self.reader.object_metadata(app_path, ('status', 'errors', 'durable_oracle', 'closed'))
        need(summary['supervision'] == 'completed' and summary['permanent_integrity_halt'] is False
             and app['status'] == 'passed' and not app['errors']
             and summary['durable_oracle']['passed'] is True
             and closed.get('databaseResourcesReleased') is True and closed.get('consumerResourcesReleased') is True
             and closed.get('databaseStatus') == closed.get('consumerStatus') == 'Succeeded'
             and closed.get('serverState') == ('Disposed' if role in ('before', 'after') else 'Stopped'),
             'DB correctness, durable result or final resource state failed')
        need(summary['scheduler_gc_policy_valid'] is True
             and summary['scheduler_gc_policy'] == frozen['scheduler_gc_policy'] == plan['settings']['features']['scheduler_gc_policy'] == self.gc_policy
             and summary['resource_sampling_policy'] == frozen['resource_sampling_policy'] == plan['settings']['features']['resource_sampling_policy'] == self.sampling,
             'DB GC/sampling policy differs')
        gc_path = path / 'observation.scheduler-gc.json'
        need(Path(summary['scheduler_gc_receipt']['path']).resolve() == gc_path.resolve()
             and sha(gc_path) == summary['scheduler_gc_receipt']['sha256']
             and self.gc.valid_receipt(read(gc_path), self.gc_policy, read(path / 'supervision/receipt.json'),
                                      frozen['plan_sha256'], frozen['source_files']), 'DB GC completion/restoration differs')
        observer = summary['generator_resource_observer']
        need(observer['status'] == 'completed' and not observer['errors'] and not observer['identity_failures']
             and observer['resource_sampling_policy'] == self.sampling, 'DB resource observer failed')
        if summary['provider'] == 'postgresql':
            identity = read(path / 'postgres/identity.json')
            need(identity['observed_settings'] == '18.0|on|on|on'
                 and identity['postgres_sha256'] == sha(self.pg / 'postgres')
                 and identity['psql_sha256'] == sha(self.pg / 'psql'), 'PostgreSQL actual version/durability/tool identity differs')
            commands = read(path / 'postgres/commands.json')
            need(commands and all(x['exit_code'] == 0 for x in commands)
                 and commands[-1]['argv'] == [str(self.pg / 'pg_ctl'), '-D', str(path / 'postgres/data'), '-m', 'fast', '-w', 'stop'],
                 'Original owned PostgreSQL shutdown did not complete')
        need(not passing or value['eligible'], 'DB cell did not meet original comparison validity/service criteria')
        return value

    def check_protocol(self, path, role, passing=True, long=False):
        plan = read(path / 'plan.json')
        receipt = read(path / 'execution/receipt.json')
        adapter = read(path / 'adapter.json')
        if long:
            # Exact sparse histograms can exceed the short reader's 64 MiB
            # control-file bound. Read only identity/lifecycle metadata here;
            # the unchanged original long verifier subsequently streams and
            # verifies every request, oracle row, effective second and resource.
            result = self.reader.object_metadata(path / 'result.json',
                ('status', 'valid', 'service_standard_met', 'idle_owner_and_request_gauges_receded',
                 'recovery'))
            identity = self.protocol_reader.build_identity(plan, adapter, receipt)
            self.protocol_reader.optional_build({'directory': str(path)}, identity)
            value = dict(build=identity,
                         eligible=result.get('valid') is True and result.get('service_standard_met') is True)
        else:
            value = self.protocol_reader.read_cell(path, role, self.a21, self.reader, sha(self.a21_path))
            result = read(path / 'result.json')
        need(result['status'] == 'completed' and receipt['status'] == 'passed' and not receipt['errors']
             and result['idle_owner_and_request_gauges_receded'] is True and result['recovery']['status'] == 'passed'
             and (long or all(row['correctness_failures'] == 0 for row in result['scenarios'].values())),
             'Protocol correctness or retirement failed')
        need(receipt['loaded_native_sha256'] == adapter['native_sha256'], 'Protocol mapped native identity differs')
        expected = read(self.protocol_build(role))
        need(Path(plan['build_manifest']).resolve() == self.protocol_build(role).resolve()
             and plan['artifacts'][plan['build_manifest']] == sha(self.protocol_build(role)), 'Protocol role build differs')
        if role != 'direct':
            need(value['build']['product_source_commit'] == (BEFORE if role == 'before' else self.selected), 'Protocol runtime source differs')
            need(expected['server_native_sha256'] == adapter['native_sha256'], 'Protocol role-native manifest differs')
        need(not passing or value['eligible'], 'Protocol cell did not meet original comparison validity/service criteria')
        return value

    def check_codec_identity(self, path, role):
        plan, result = read(path / 'plan.json'), read(path / 'result.json')
        build = read(self.codec_build(role))
        need(plan['manifest_sha256'] == sha(self.codec_build(role)) and plan['route'] == CODEC_ROUTES[role]
             and plan['source_commit'] == build['source_commit']
             and plan['corpus_manifest_sha256'] == sha(self.corpus / 'manifest.json'), 'Codec role/corpus identity differs')
        if role in ('before', 'after'):
            actual = plan['actual_loaded_native']
            need(len(actual) == 1 and actual[0]['sha256'] == build['native_sha256'], 'Codec mapped native asset differs')
        drained = []
        with (path / 'events.jsonl').open() as stream:
            for line in stream:
                event = json.loads(line)
                if event.get('kind') == 'drained':
                    drained.append(event)
        need(result['exit_code'] == 0 and result['complete'] is True and result.get('recovery_standard_met') is True
             and len(drained) == 1 and not drained[0].get('errors', 0), 'Codec correctness/recovery/drain failed')
        native = drained[0].get('native')
        need((role not in ('before', 'after') or native is not None)
             and (native is None or all(native[k] == 0 for k in ('live', 'capacity', 'active'))), 'Codec owners remain after drain')


def noise_projection(scene, noise):
    # Numeric band/provenance projection only: no internal paths or key material.
    if 'before_processes' in noise:
        hashes = [x['result_sha256'] for x in noise['before_processes']]
    elif 'calibration_cells' in noise:
        hashes = [x['summary_sha256'] for x in noise['calibration_cells']]
    else:
        hashes = [x['evidence_sha256']['summary.json'] for x in noise['processes']]
    return dict(scene=scene, noise_sha256=None, bands=noise['bands'], before_process_result_sha256=hashes)
