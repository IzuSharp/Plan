#!/usr/bin/env python3
"""Local, uninstrumented Release+symbols build using the product producer.

The same exact compiler options apply to unchanged main and every ordinary
candidate. This driver is external to the product and never a CI entry point.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--provider', choices=('sqlite', 'postgresql'))
parser.add_argument('--tests', action='store_true')
args = parser.parse_args()
root, output = args.root.resolve(), args.output.resolve()
sys.path.insert(0, str(root / 'eng'))
spec = importlib.util.spec_from_file_location('matched_native_product_producer', root / 'eng/task07_native.py')
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)
original_run = producer.run
flags = ['-DCMAKE_C_FLAGS_RELEASE=-O3 -DNDEBUG -g',
         '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG -g',
         '-DNW_BUILD_TESTS=' + ('ON' if args.tests else 'OFF')]

def matched_run(argv, log_output, label, env):
    if label == 'configure':
        argv = [*argv, *flags]
    return original_run(argv, log_output, label, env)

producer.run = matched_run
sys.argv = [str(root / 'eng/task07_native.py'), '--output', str(output)]
if args.provider:
    sys.argv.extend(['--provider', args.provider])
producer.main()
manifest = output / 'manifest.json'
data = json.loads(manifest.read_text())
data['localComparisonBuild'] = {
    'task': 'DB-Exec-Parity-01',
    'instrumented': False,
    'flags': flags,
    'driver': str(Path(__file__).resolve()),
    'driverSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'scope': 'Matched source-preserving Release build with symbols; distinct from archived no-g baseline.'
}
manifest.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
print(json.dumps({'manifest': str(manifest), 'sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()}))
