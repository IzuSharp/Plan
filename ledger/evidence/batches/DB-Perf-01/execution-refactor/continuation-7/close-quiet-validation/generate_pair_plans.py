#!/usr/bin/env python3
"""Prepare two ordinary phase rounds; never launch a workload or database."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--reference-root', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    reference = args.reference_root.resolve(strict=True)
    source = args.source.resolve(strict=True)
    generator = Path(__file__).resolve().parents[2] / 'continuation-4/generate_local_plan.py'
    script = Path(__file__).resolve()
    manifests = []
    for round_number in (1, 2):
        for provider in ('sqlite', 'postgresql'):
            name = f'close-paired-{provider}-r{round_number}'
            output = root / 'measurements' / name
            plan = root / 'measurements/plans' / (name + '.json')
            generated = plan if round_number == 1 else plan.with_suffix('.original.json')
            command = [sys.executable, str(generator), '--source', str(source),
                       '--provider', provider, '--lane', 'phases',
                       '--before-dir', str(root / 'builds' / f'candidate-{provider}-02/consumer-query-phases/out'),
                       '--candidate-dir', str(root / 'builds' / f'close-{provider}-02/consumer-query-phases/out'),
                       '--dapper-dir', str(reference / 'consumers' / f'dapper-{provider}-phases/out'),
                       '--plan', str(generated), '--output', str(output)]
            if provider == 'sqlite':
                command += ['--sqlite-library', str(reference / 'consumers/direct-native/libsqlite3.so')]
            else:
                command += ['--postgres-bin', str(reference / 'tools/postgres/install/bin')]
            subprocess.run(command, check=True)
            if round_number == 2:
                original = json.loads(generated.read_text())
                commands = original['commands']
                assert len(commands) == 10 and commands[0]['phase'] == 'fixture'
                for offset, rows in ((1, 1), (4, 100), (7, 1000)):
                    group = commands[offset:offset + 3]
                    assert {c['name'] for c in group[:2]} == {f'before-rows{rows}', f'candidate-rows{rows}'}
                    assert group[2]['name'] == f'dapper-rows{rows}'
                    commands[offset:offset + 2] = group[1::-1]
                original['pairedOrderProvenance'] = {
                    'originalPlan': str(generated), 'originalSha256': sha(generated),
                    'generator': str(generator), 'generatorSha256': sha(generator),
                    'selector': str(script), 'selectorSha256': sha(script),
                    'change': 'Reverse only the two Korda positions for each row count; preserve Dapper SQL receipt dependency.'}
                original['runnerCommand'][5] = str(plan)
                with plan.open('x') as stream:
                    json.dump(original, stream, indent=2)
                    stream.write('\n')
            manifests.append({'round': round_number, 'provider': provider,
                              'plan': str(plan), 'sha256': sha(plan), 'output': str(output)})
    index = root / 'measurements/close-paired-plans-01.json'
    with index.open('x') as stream:
        json.dump({'script': str(script), 'scriptSha256': sha(script),
                   'beforeCommit': '17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa',
                   'candidateCommit': '92b923075952bac347619ee7817c372ee6e415cb',
                   'plans': manifests}, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'index': str(index), 'sha256': sha(index)}))


if __name__ == '__main__':
    main()
