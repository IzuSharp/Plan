#!/usr/bin/env python3
"""Finite offline final-supplement controls using real immutable short receipts.

No final receipt or performance result is synthesized. A real freeze and image/
owner predicates are exercised, the old arithmetic is rerun on actual phase
evidence, and a non-final report must fail the top-level final gate. Full final
acceptance remains unavailable until the four real 1800-second intervals exist.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('auditor', 'freeze', 'root', 'phase-analysis', 'work', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists(), 'Fresh control paths required'
    args.work.mkdir(parents=True)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('final_identity_control_subject', args.auditor)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    frozen = json.loads(args.freeze.read_text())
    assert frozen['status'] == 'frozen' and frozen['auditor']['sha256'] == sha(args.auditor)
    bindings = frozen['bindings']
    original_hashes = dict(frozen['inputFiles'])
    for path in (args.freeze, args.phase_analysis, Path(__file__)):
        original_hashes[str(path.resolve())] = sha(path)
    controls = []

    def check(label, call, accepted, message=None):
        module.FILES.clear()
        error = None
        try:
            call()
        except Exception as caught:
            error = caught
        assert (error is None) is accepted, label + ': ' + repr(error)
        if message is not None:
            assert error is not None and message in str(error), label + ': wrong rejection: ' + repr(error)
        controls.append({'name': label, 'expected': 'accepted' if accepted else 'rejected', 'passed': True,
                         'errorType': type(error).__name__ if error else None, 'message': str(error) if error else None})

    check('real-freeze-complete-revalidation', lambda: module.revalidate_frozen_bindings(frozen), True)
    for label, mutate in [
            ('missing-command-reader-binding', lambda x: x['bindings'].pop('consumerReader')),
            ('missing-source-tree', lambda x: x['bindings']['candidateSource'].pop('tree')),
            ('wrong-source-commit', lambda x: x['bindings']['candidateSource'].update(commit='0' * 40)),
            ('wrong-source-tree', lambda x: x['bindings']['candidateSource'].update(tree='0' * 40)),
            ('missing-generated-source-inventory', lambda x: x['bindings']['consumers']['sqlite']['dapper'].pop('generatedSources')),
            ('missing-freeze-input', lambda x: x['inputFiles'].pop(next(iter(x['inputFiles'])))),
            ('changed-freeze-input-hash', lambda x: x['inputFiles'].__setitem__(next(iter(x['inputFiles'])), '0' * 64)),
            ('extra-freeze-input', lambda x: x['inputFiles'].update({str(args.phase_analysis.resolve()): sha(args.phase_analysis)}))]:
        altered = copy.deepcopy(frozen)
        mutate(altered)
        check(label, lambda x=altered: module.revalidate_frozen_bindings(x), False)

    for provider in module.PROVIDERS:
        for cohort, original_cohort in [('candidate', 'korda'), ('dapper', 'dapper')]:
            path = args.root / 'measurements' / ('single-command-' + provider + '-01') / (original_cohort + '-numeric.json')
            original_hashes[str(path.resolve())] = sha(path)
            raw = json.loads(path.read_text())
            binding, plan = bindings['consumers'][provider][cohort], bindings['plans'][provider]['plan']
            prefix = provider + '/' + cohort + '/'
            check(prefix + 'actual-short-image-and-owner-positive', lambda: module.verify_owners_and_image(raw, binding, plan), True)

            def raw_control(label, mutate):
                value = copy.deepcopy(raw)
                mutate(value)
                check(prefix + label, lambda: module.verify_owners_and_image(value, binding, plan), False)

            raw_control('missing-native-aot', lambda x: x.pop('NativeAot'))
            raw_control('not-native-aot', lambda x: x.update(NativeAot=False))
            raw_control('wrong-route', lambda x: x.update(Route='another-route'))
            raw_control('wrong-package-version', lambda x: x.update(PackageVersion='other/0.0'))
            raw_control('missing-package-version', lambda x: x.pop('PackageVersion'))
            raw_control('missing-executable-hash', lambda x: x.pop('ExecutableSha256'))
            raw_control('wrong-executable-hash', lambda x: x.update(ExecutableSha256='0' * 64))
            raw_control('missing-native-path', lambda x: x.pop('LoadedNativePath'))
            raw_control('missing-native-hash', lambda x: x.pop('LoadedNativeSha256'))
            raw_control('wrong-native-path', lambda x: x.update(LoadedNativePath='/unrelated/native.so'))
            raw_control('wrong-native-hash', lambda x: x.update(LoadedNativeSha256='0' * 64))
            raw_control('missing-drained', lambda x: x.pop('Drained'))
            declaration = 'OwnersReturnedToZero' if cohort == 'candidate' else 'ApplicationConnectionsReturnedToZero'
            raw_control('missing-zero-declaration', lambda x: x.pop(declaration))
            raw_control('false-zero-declaration', lambda x: x.update({declaration: False}))
            names = module.OWNERS if cohort == 'candidate' else ('ApplicationConnections',)
            for name in names:
                raw_control('missing-' + name, lambda x, n=name: x['Drained'].pop(n))
                for label, value in [('leak', 1), ('negative', -1), ('boolean', False), ('float', 0.0), ('string', '0')]:
                    raw_control(label + '-' + name, lambda x, n=name, v=value: x['Drained'].__setitem__(n, v))

    repository = Path(bindings['repository'])
    candidate = bindings['consumers']['sqlite']['candidate']
    release_path = candidate['product']['releaseReceipt']['path']
    release = json.loads(Path(release_path).read_text())
    for label, mutate in [('missing-release-source', lambda x: x.pop('source_commit')),
                           ('wrong-release-source', lambda x: x.update(source_commit=bindings['runnerSource']['commit'])),
                           ('missing-release-tree', lambda x: x.pop('source_tree')),
                           ('wrong-release-tree', lambda x: x.update(source_tree='0' * 40)),
                           ('dirty-release', lambda x: x.update(source_dirty=True)),
                           ('wrong-release-rid', lambda x: x.update(rid='win-x64')),
                           ('missing-package-hash', lambda x: x['packages'][0].pop('upload_archive_sha256')),
                           ('wrong-package-hash', lambda x: x['packages'][0].update(upload_archive_sha256='0' * 64)),
                           ('missing-native-hash', lambda x: x['packages'][0]['native'].pop('sha256')),
                           ('wrong-native-hash', lambda x: x['packages'][0]['native'].update(sha256='0' * 64)),
                           ('wrong-native-source', lambda x: x['packages'][0]['native'].update(source_commit='0' * 40)),
                           ('wrong-package-member-hash', lambda x: x['packages'][0]['unsigned_entries'].__setitem__('README.md', '0' * 64))]:
        value = copy.deepcopy(release)
        mutate(value)
        path = args.work / (label + '.json')
        path.write_text(json.dumps(value))
        check(label, lambda p=path: module.package_source(repository, bindings['candidateSource']['commit'],
                    candidate['consumer']['receiptData'], candidate['consumer'], p), False)

    # Real binary bytes are never changed. Malformed/tampered binary cases use
    # a small separate scratch file, with an independently computed digest.
    malformed = args.work / 'malformed-elf.bin'
    malformed.write_bytes(b'not-an-ELF-image' + b'\0' * 24)
    check('non-elf-with-correct-file-hash', lambda: module.elf(malformed, sha(malformed)), False, 'Not Linux x64 ELF')
    check('changed-file-hash', lambda: module.identity(malformed, '0' * 64), False, 'Changed bound input')
    check('source-ref-alias', lambda: module.source_identity(repository, 'HEAD'), False, 'Exact full source commit')
    check('source-content-hash-mismatch', lambda: module.source_file(repository, bindings['runnerSource']['commit'],
          'benchmarks/db-perf/run.py', expected='0' * 64), False, 'Producer source differs')
    check('duplicate-json-key', lambda: module.read(write_control(args.work / 'duplicate.json', '{"a":1,"a":2}')), False, 'Duplicate JSON key')
    check('nonfinite-json-number', lambda: module.read(write_control(args.work / 'nonfinite.json', '{"a":NaN}')), False, 'Nonfinite JSON')

    phase = json.loads(args.phase_analysis.read_text())
    check('existing-arithmetic-independent-real-reread', lambda: module.verify_arithmetic_report(phase, bindings), True)
    altered = copy.deepcopy(phase)
    altered['observations'][0]['timingCredit'] = not altered['observations'][0]['timingCredit']
    check('changed-arithmetic-result', lambda: module.verify_arithmetic_report(altered, bindings), False, 'Arithmetic report differs')
    command = [sys.executable, str(args.auditor.resolve()), 'audit', '--freeze', str(args.freeze.resolve()),
               '--freeze-sha256', sha(args.freeze), '--analysis', str(args.phase_analysis.resolve()),
               '--output', str((args.work / 'non-final-rejection.json').resolve())]
    process = subprocess.run(command, capture_output=True, text=True)
    rejection = json.loads((args.work / 'non-final-rejection.json').read_text())
    assert process.returncode == 1 and rejection['status'] == 'failed' and rejection['message'] == 'Existing arithmetic final-four checks failed'
    controls.append({'name': 'top-level-refuses-real-non-final-report', 'expected': 'rejected', 'passed': True,
                     'exitCode': process.returncode, 'receipt': str((args.work / 'non-final-rejection.json').resolve()),
                     'receiptSha256': sha(args.work / 'non-final-rejection.json')})
    for path, expected in original_hashes.items():
        assert sha(path) == expected, 'Original input changed: ' + path
    receipt = {'schemaVersion': 1, 'scope': __doc__, 'passed': True, 'count': len(controls), 'controls': controls,
               'auditorSha256': sha(args.auditor), 'controlSourceSha256': sha(__file__),
               'freeze': {'path': str(args.freeze.resolve()), 'sha256': sha(args.freeze)},
               'originalEvidenceUnchanged': True, 'originalInputHashes': original_hashes,
               'workloadProcessesStarted': 0, 'finalCredit': '0/4', 'topLevelExpectedRejection': {'argv': command, 'stdout': process.stdout}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'count': len(controls), 'output': str(args.output)}))


def write_control(path, text):
    with path.open('x') as stream:
        stream.write(text)
    return path


if __name__ == '__main__':
    main()
