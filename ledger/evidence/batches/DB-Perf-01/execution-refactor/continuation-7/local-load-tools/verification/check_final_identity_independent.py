#!/usr/bin/env python3
"""Independent finite image/owner controls; never runs a workload or invents final evidence."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

BASE = Path('/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7')
SUBJECT = BASE / 'local-load-tools/audit_final_identity.py'
EXPECTED = '99f458030b41cfe9f5740cd536a0f5d3314b0955a8a72de9abce10d3ab3c91e2'
FREEZE = BASE / 'local-load-tools/verification/freeze-controls-04.json'
RAW_ROOT = Path('/workspace/scratch/4a65d70f0fe1/measurements')
OUTPUT = Path('/workspace/scratch/fd78534029f7/native-review/auditor-independent-extra-01.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert sha(SUBJECT) == EXPECTED and not OUTPUT.exists()
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('independent_final_identity_subject', SUBJECT)
    subject = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = subject
    spec.loader.exec_module(subject)
    frozen = json.loads(FREEZE.read_text())
    bindings = frozen['bindings']
    original = dict(frozen['inputFiles'])
    original[str(FREEZE)] = sha(FREEZE)
    original[str(Path(__file__))] = sha(Path(__file__))
    samples = {}
    for provider in subject.PROVIDERS:
        for role in subject.COHORTS:
            raw_role = 'korda' if role == 'candidate' else role
            path = RAW_ROOT / ('single-command-' + provider + '-01') / (raw_role + '-numeric.json')
            original[str(path)] = sha(path)
            samples[provider, role] = json.loads(path.read_text())
    controls = []

    def check(name, call, accept):
        subject.FILES.clear()
        failure = None
        try:
            call()
        except Exception as error:
            failure = error
        assert (failure is None) is accept, (name, repr(failure))
        controls.append({'name': name, 'expected': 'accepted' if accept else 'rejected',
                         'passed': True, 'errorType': type(failure).__name__ if failure else None,
                         'message': str(failure) if failure else None})

    for (provider, role), raw in samples.items():
        binding = bindings['consumers'][provider][role]
        plan = bindings['plans'][provider]['plan']
        prefix = provider + '/' + role + '/'
        check(prefix + 'real-image-and-owner', lambda r=raw, b=binding, p=plan: subject.verify_owners_and_image(r, b, p), True)
        for (other_provider, other_role), other in samples.items():
            if (provider, role) != (other_provider, other_role):
                check(prefix + 'reject-raw-from-' + other_provider + '-' + other_role,
                      lambda r=other, b=binding, p=plan: subject.verify_owners_and_image(r, b, p), False)
        declaration = 'OwnersReturnedToZero' if role == 'candidate' else 'ApplicationConnectionsReturnedToZero'
        for field in ('NativeAot', declaration):
            for label, value in [('integer-one', 1), ('string-true', 'true'), ('null', None)]:
                changed = copy.deepcopy(raw)
                changed[field] = value
                check(prefix + field + '-' + label,
                      lambda r=changed, b=binding, p=plan: subject.verify_owners_and_image(r, b, p), False)
        owner = 'CommandCompletions' if role == 'candidate' else 'ApplicationConnections'
        for label, value in [('null', None), ('array', []), ('object', {}), ('large', 2**64)]:
            changed = copy.deepcopy(raw)
            changed['Drained'][owner] = value
            check(prefix + owner + '-' + label,
                  lambda r=changed, b=binding, p=plan: subject.verify_owners_and_image(r, b, p), False)

    for label, mutate in [
        ('candidate-executable-path-swapped', lambda x: x['bindings']['consumers']['sqlite']['candidate']['consumer']['executable'].update(path=bindings['consumers']['postgresql']['candidate']['consumer']['executable']['path'])),
        ('candidate-native-image-hash-swapped', lambda x: next(iter(x['bindings']['consumers']['sqlite']['candidate']['consumer']['nativeImages'].values())).update(sha256='0' * 64)),
        ('candidate-release-member-source-swapped', lambda x: x['bindings']['consumers']['sqlite']['candidate']['product']['nativePackageMember'].update(source_commit='0' * 40)),
        ('dapper-harness-commit-swapped', lambda x: x['bindings']['consumers']['sqlite']['dapper']['harnessSource'].update(commit='0' * 40)),
    ]:
        changed = copy.deepcopy(frozen)
        mutate(changed)
        check(label, lambda value=changed: subject.revalidate_frozen_bindings(value), False)

    for path, expected in original.items():
        assert sha(Path(path)) == expected, 'Changed original input: ' + path
    result = {'schemaVersion': 1, 'passed': True, 'count': len(controls), 'controls': controls,
              'auditorSha256': EXPECTED, 'reviewerSourceSha256': sha(Path(__file__)),
              'freeze': {'path': str(FREEZE), 'sha256': sha(FREEZE)},
              'originalEvidenceUnchanged': True, 'originalInputHashes': original,
              'workloadProcessesStarted': 0, 'finalCredit': '0/4',
              'scope': 'Real short receipt image/owner predicates only; no final positive report synthesized.'}
    with OUTPUT.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'count': len(controls), 'output': str(OUTPUT), 'sha256': sha(OUTPUT)}))


if __name__ == '__main__':
    main()
