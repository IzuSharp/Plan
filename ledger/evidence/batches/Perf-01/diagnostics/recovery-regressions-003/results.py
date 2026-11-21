"""Bind existing fixture markers, receipts and actual selected-native outputs."""
from pathlib import Path
import re

from bindings import Binding, need, read
from owner import sha


def binary_inputs(executable, native, server=True):
    executable = Path(executable)
    directory, b = executable.parent, Binding()
    b.pin(executable)
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix in ('.dll', '.json', '.so', '.txt'):
            b.pin(path)
    for path in sorted((directory / 'runtimes').rglob('*.so')):
        b.pin(path)
    if server:
        asset = b.document(directory / 'NativeWeave.server.assets.json')
        need(asset['engineId'] == 'server' and asset['rid'] == 'linux-x64'
             and asset['sha256'] == native['sha256'], 'Runtime Server asset selection differs')
        path = directory / asset['outputPath']
        need(path.resolve().is_relative_to(directory), 'Runtime asset escapes binary directory')
        b.pin(path, native['sha256'])
    return b.files


def original_commands(folder, b, suffix='.log', b15=False):
    commands = b.document(folder / 'commands.json')
    need(commands and len({c['label'] for c in commands}) == len(commands), 'Missing/duplicate original commands')
    for row in commands:
        need(row['exit_code'] == 0, 'Original fixture command failed: ' + row['label'])
        path = folder / row['log'] if b15 else folder / 'logs' / (row['label'] + suffix)
        b.pin(path, row['sha256'] if b15 else row['log_sha256'])
    return commands


def package(folder, task, selected, native, b):
    value = b.document(folder / 'summary.json')
    need(value['source_commit'] == selected and value['native_sha256'] == native['sha256'], 'Package source/native differs')
    flags = ['no_consumer_rust']
    if task == 'B20':
        need(value['task'] == 'B20' and value['platform'] == 'linux-x64', 'Wrong B20 package receipt')
        flags += ['no_parent_repository_imports', 'jit_disabled_local', 'aot_disabled_local']
        name = 'Consumer'
    else:
        flags += ['transitive_generator', 'minimal_advanced_jit_aot_http1_http2', 'ordinary_dto_edit_same_native']
        name = 'ServerApplication.Sample' if task == 'B15' else 'Mcp.Sample'
        if task == 'B19':
            flags += ['external_context_no_analyzer_reference', 'no_repository_build_imports',
                      'private_only_edit_regenerated_layout_proof', 'external_private_edit_jit_aot_http1_http2']
    need(all(value[key] is True for key in flags), 'Original package proof did not pass')
    commands = original_commands(folder, b, '.txt' if task == 'B20' else '.log')
    for row in value['packages'].values():
        b.pin(row['path'], row['sha256'])
    consumer = folder / 'consumer'
    modes = {'jit': consumer / ('bin/Release/net11.0/' + name + '.dll'), 'aot': consumer / ('publish/' + name)}
    if task == 'B19':
        modes.update({'external-jit': consumer / 'external/bin/Release/net11.0/External.Layout.Consumer.dll',
                      'external-aot': consumer / 'external/publish/External.Layout.Consumer'})
    need(set(value['sdk_output_records']) == set(modes), 'Package runtime mode population differs')
    for mode, executable in modes.items():
        need(read(executable.parent / 'NativeWeave.server.assets.json') == value['sdk_output_records'][mode], 'Package SDK output record differs')
        b.mapping(binary_inputs(executable, native))
    b.pin(modes['aot'], value['aot_executable_sha256'])
    if task == 'B19':
        b.pin(modes['external-aot'], value['external_aot_executable_sha256'])
    return dict(summary=str(folder / 'summary.json'), summary_sha256=sha(folder / 'summary.json'),
                commands=len(commands), packages=len(value['packages']), modes=list(modes), checks={key: value[key] for key in flags})


def collect(output, product, selected, native, receipts, inventories):
    b, logs = Binding(), {}
    b.pin(native['path'], native['sha256'])
    for actual in receipts:
        receipt = Path(actual['path'])
        b.pin(receipt, actual['sha256'])
        row = b.document(receipt)
        need(row['status'] == 'completed' and row['exit_code'] == 0 and row['retired'], 'Finite owner did not retire successfully')
        b.mapping(row['logs_sha256'], receipt.parent)
        logs[actual['label']] = (receipt.parent / 'stdout.log').read_text()
    for path in inventories:
        b.mapping(b.document(path)['files_sha256'])
    results = {}
    for mode, dynamic in (('jit', 'True'), ('aot', 'False')):
        text = logs['b17-' + mode + '-execute']
        markers = ['PASS transport Http1 TLS=False HTTP=1.1', 'PASS transport Http2 TLS=False HTTP=2.0',
                   'PASS transport Http1AndHttp2 TLS=True HTTP=2.0', 'PASS transport Http1AndHttp2 TLS=True HTTP=1.1',
                   'PASS request admission and final-lease retirement HTTP/1.1 + HTTP/2 TLS',
                   'PASS B17 checks=105 dispatches=43 dynamic=' + dynamic]
        need(all(marker in text for marker in markers), 'Original B17 ' + mode + ' completion markers differ')
        results.setdefault('B17', {})[mode] = dict(checks=105, dispatches=43, dynamic=dynamic == 'True', markers=markers)
    results['B17']['scope'] = 'Six managed fixture commands; no B17 native producer or benchmark modes'

    folder = output / 'B15'
    value = b.document(folder / 'result.json')
    need(value['task'] == 'B15' and value['platform'] == 'linux-x64' and value['status'] == 'passed'
         and value['source_commit'] == selected and value['source_dirty'] is False
         and value['native_sha256'] == native['sha256'] and value['jit_assertions'] == value['aot_assertions'] == 85
         and value['public_symbols'] == 278, 'Original B15 result differs')
    b.mapping(value['input_sha256'], product)
    need(original_commands(folder, b, b15=True) == value['commands'], 'B15 command receipt differs')
    for label, markers in {'actual-jit': ('85 assertions', 'dynamic=True'), 'actual-aot': ('85 assertions', 'dynamic=False'),
                           'api-exact': ('278 exact symbols',)}.items():
        need(all(marker in (folder / 'logs' / (label + '.log')).read_text() for marker in markers), 'B15 output markers differ: ' + label)
    b.pin(folder / 'input/libnativeweave_server.so', native['sha256'])
    b.mapping(binary_inputs(product / 'tests/Server.Application/bin/Release/net11.0/NativeWeave.Server.Application.Tests.dll', native))
    b.mapping(binary_inputs(folder / 'aot/NativeWeave.Server.Application.Tests', native))
    b.pin(folder / 'aot/NativeWeave.Server.Application.Tests', value['aot_executable_sha256'])
    b.pin(folder / 'package/summary.json', value['package_summary_sha256'])
    results['B15'] = dict(scope='Unchanged selected-native B15 verifier, including JSON/component, API and package checks',
                          jit_assertions=85, aot_assertions=85, public_symbols=278,
                          package=package(folder / 'package', 'B15', selected, native, b))

    markers = ['PASS Real managed cancellation tail retains Pending until the finite close wait expires',
               'PASS Canceled nested callback retains request and scope until application returns',
               'PASS Global-pressure/cancel terminal drains both native and managed credits']
    for mode, dynamic in (('jit', 'True'), ('aot', 'False')):
        text = logs['b19-actual-' + mode]
        match = re.search(r'assertions=(\d+), managed_retirements=(\d+), dynamic=' + dynamic, text)
        need(match and int(match[1]) >= 230 and all(marker in text for marker in markers), 'Original B19 ' + mode + ' markers differ')
        results.setdefault('B19', {})[mode] = dict(assertions=int(match[1]), managed_retirements=int(match[2]),
                                                  dynamic=dynamic == 'True', lifecycle_marker_counts={m: text.count(m) for m in markers})
    need(results['B19']['jit']['assertions'] == results['B19']['aot']['assertions'], 'B19 JIT/AOT assertion counts differ')
    need(all(m in logs['b19-api-exact'] for m in ('65 exact symbols', '5 exact static consumer cases passed')), 'B19 API proof differs')
    results['B19'].update(scope='Ten managed/API/package commands; native producer, native unit/preparse and generator-specific suites excluded',
                          public_symbols=65, consumer_compile_fixtures=5,
                          package=package(output / 'B19-managed/package', 'B19', selected, native, b))

    for mode, expected_count, dynamic, configuration in (('debug', 5, 'True', 'Debug'), ('jit', 122, 'True', 'Release'), ('aot', 122, 'False', 'Release')):
        text = logs['b20-actual-' + mode]
        matches = re.findall(r'^B20 actual diagnostics: (\d+) assertions, dynamic=' + dynamic
                             + ', configuration=' + configuration + r'\.$', text, re.MULTILINE)
        need(len(matches) == 1 and int(matches[0]) == expected_count,
             'Source-bound B20 ' + mode + ' observed assertion count/configuration differs')
        count = int(matches[0])
        need('PASS Default diagnostics preserve complete ownership join.' in text, 'B20 ownership join marker missing')
        close_markers = {}
        if mode != 'debug':
            need('PASS Throwing listener cannot prevent request/root retirement.' in text, 'B20 throwing listener retirement missing')
            # These are existing Check() output strings in the exact bound
            # Program.cs. Its Main calls both H1 and H2 regressions once.
            for version in ('1.1', '2.0'):
                marker = 'PASS Actual ' + version + ' delivers the exact Content-Length payload before managed Finish.'
                close_markers[marker] = text.count(marker)
                need(close_markers[marker] == 1, 'B20 actual protocol close/Finish marker differs: ' + version)
            for marker in (
                'PASS Close keeps admitted dispatch pending before its deadline while Finish is gated.',
                'PASS Accepted response Finish succeeds during graceful close: ',
                'PASS Close joins the completed Finish and releases every business owner.',
                'PASS Graceful close preserves the exact response end without extra payload.',
                'PASS Successful close-versus-Finish emits one success Activity and no failure warning.'):
                close_markers[marker] = text.count(marker)
                need(close_markers[marker] == 2, 'B20 close/Finish lifecycle marker differs: ' + marker)
        results.setdefault('B20', {})[mode] = dict(assertions=count, dynamic=dynamic == 'True', configuration=configuration,
                                                   close_before_finish_marker_counts=close_markers)
    need('PASS B20 internal-only applicability; 10 exact RequestContext declarations/XML; no additional public types; public-only sample/reference contribution present.'
         in logs['b20-api-public-xml'], 'B20 API/XML applicability marker differs')
    for label, local in (('disabled', 'False'), ('explicit-local', 'True')):
        need('Rust Host complete; explicit_local=' + local + ';' in logs['b20-sample-debug-' + label], 'B20 sample mode differs')
    results['B20'].update(scope='Twelve managed/API/sample/package commands; native producer/unit suites and all cost modes excluded',
                          public_context_symbols=10, package=package(output / 'B20-managed/package', 'B20', selected, native, b))
    return dict(status='passed', task='Perf-01', epoch='recovery-002', global_acceptance=False,
                scope='Selected Server native: B17 managed, full selected-native B15, B19/B20 managed/API/package subsets',
                product_commit=selected, native_asset=native,
                results=results, files_sha256=b.files, historical_credit_transferred=False, performance_credit_seconds=0)
