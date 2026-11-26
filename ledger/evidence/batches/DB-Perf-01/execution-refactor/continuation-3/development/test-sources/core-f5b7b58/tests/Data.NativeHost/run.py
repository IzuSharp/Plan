#!/usr/bin/env python3
"""Run one real two-provider managed host consumer against an isolated TCP PostgreSQL cluster."""
import argparse
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--postgres-bin', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('command', nargs=argparse.REMAINDER)
args = parser.parse_args()
command = args.command[1:] if args.command[:1] == ['--'] else args.command
if not command:
    parser.error('provide an executable command after --')
args.output.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='nw-b04-pg-') as temporary:
    directory = Path(temporary)
    with socket.socket() as socket_owner:
        socket_owner.bind(('127.0.0.1', 0))
        port = socket_owner.getsockname()[1]
    def pg(name, *arguments, **options):
        return subprocess.run([str(args.postgres_bin / name), *map(str, arguments)], check=True, **options)
    with (args.output / 'postgres-init.log').open('w') as log:
        pg('initdb', '-D', directory, '-U', 'postgres', '--no-locale', '--encoding=UTF8', '-A', 'trust', stdout=log, stderr=subprocess.STDOUT)
    pg('pg_ctl', '-D', directory, '-l', args.output.resolve() / 'postgres.log', '-o', f"-p {port} -h 127.0.0.1 -k ''", '-w', 'start', stdout=subprocess.DEVNULL)
    try:
        environment = os.environ.copy()
        environment['NW_TEST_POSTGRES'] = f'postgresql://postgres@127.0.0.1:{port}/postgres'
        with (args.output / 'consumer.log').open('w') as log:
            result = subprocess.run(command, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        print((args.output / 'consumer.log').read_text())
        if result.returncode:
            raise SystemExit(result.returncode)
    finally:
        pg('pg_ctl', '-D', directory, '-m', 'fast', '-w', 'stop', stdout=subprocess.DEVNULL)
