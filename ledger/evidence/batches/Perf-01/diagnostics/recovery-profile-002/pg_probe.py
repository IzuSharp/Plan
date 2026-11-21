#!/usr/bin/env python3
"""Run one unchanged Shared probe inside the original private PG context.

Only profile.py's original finite owner may execute this child. It owns the
whole command, including startup failures before the context yields.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--driver', type=Path, required=True)
    parser.add_argument('--domain-source-sha256', required=True)
    parser.add_argument('--postgres-bin', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--executable-sha256', required=True)
    parser.add_argument('--count', type=int, choices=(1000,), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if os.sched_getaffinity(0) != {2, 3}:
        raise RuntimeError('Use the admitted two service CPUs')
    source = args.driver / 'src/Benchmarks.Domain/run.py'
    if sha(source) != args.domain_source_sha256 or sha(args.executable) != args.executable_sha256:
        raise RuntimeError('Actual original cluster source or selected AOT probe changed')
    sys.path.insert(0, str(source.parent))
    spec = importlib.util.spec_from_file_location('perf01_profile_domain', source)
    domain = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(domain)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    with domain.postgres(output / 'postgres', args.postgres_bin) as pg:
        identity = json.loads((output / 'postgres/identity.json').read_text())
        if identity['observed_settings'] != '18.0|on|on|on':
            raise RuntimeError('Original PostgreSQL version/durability differs')
        subprocess.run([str(args.executable), 'postgresql', pg['postgres_base'], str(args.count),
                        str(output / 'result.json')], check=True, timeout=600)


if __name__ == '__main__':
    main()
