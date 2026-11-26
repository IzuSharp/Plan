#!/usr/bin/env python3
"""Apply the same strict reader to the one explicitly selected PostgreSQL experiment.

The existing two-provider command-line report requires both providers. This
adapter selects one recorded PostgreSQL directory and its three comparison
pairs without inventing a SQLite experiment or granting final-candidate credit.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analyzer', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--series', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use fresh output')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('command_analyzer', args.analyzer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.load_helpers(args.source)
    module.identity(args.analyzer)
    module.identity(__file__)
    folder = args.directory.resolve()
    run = module.analyze_folder(folder, 'ordinary')
    module.require(run['provider'] == 'postgresql' and run['status'] == 'valid', 'Invalid PostgreSQL experiment')
    series = module.read(args.series)
    matched = [x for x in series if x['command'][-2:] == ['--output', str(folder)]]
    module.require(len(matched) == 1, 'Missing/duplicate outer execution')
    actual = matched[0]
    plan = module.read(folder / 'plan.json')
    module.require(actual['exitCode'] == 0 and actual['command'] == plan['runnerCommand']
                   and actual['planSha256'] == module.identity(folder / 'plan.json')['sha256'], 'Outer identity differs')
    module.identity(actual['log'], actual['logSha256'])
    pairs = [x for x in module.comparisons([run], False) if x['provider'] == 'postgresql']
    module.require(len(pairs) == 3 and all(x['status'] == 'valid' for x in pairs), 'Invalid experiment comparison')
    changed = [str(p) for p, sha in module.FILES.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest() != sha]
    module.require(not changed, 'Inputs changed during analysis')
    result = {'schemaVersion': 1, 'scope': __doc__, 'provider': 'postgresql', 'status': 'valid_observations',
              'selectedForProduct': False, 'finalCandidateCredit': False, 'longRunAcceptance': False,
              'frameworkOnlyBytes': None, 'run': run, 'comparisons': pairs,
              'outerExecution': actual, 'inputFiles': module.FILES, 'originalInputsUnchanged': True}
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'provider': 'postgresql', 'comparisons': len(pairs)}))


if __name__ == '__main__':
    main()
