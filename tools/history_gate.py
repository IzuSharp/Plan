#!/usr/bin/env python3
"""Execute an original gate at its immutable original pair, preserving its checks."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys
import tempfile

PLAN = Path(__file__).resolve().parents[1]
DESIGN = PLAN.parent / 'NativeWeave-Design'
PLAN_COMMIT = '5b346ebb5acdb387077d0faae16b00bbc77cb299'
DESIGN_COMMIT = 'ba21ecb5c2299b303584b120f2e6bd1c6d74783a'
ALLOWED = {'verify_source_lifecycle.py', 'host_selection_checks.py', 'rust1100_checks.py'}

def run_frozen(tool):
    if tool not in ALLOWED:
        raise ValueError('Unknown historical gate: ' + str(tool))
    output = PLAN / 'verification/current-gates/frozen-history'
    output.mkdir(parents=True, exist_ok=True)
    created = []
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='nw-historical-gate-') as temporary:
        base = Path(temporary)
        try:
            for repository, commit in ((PLAN, PLAN_COMMIT), (DESIGN, DESIGN_COMMIT)):
                target = base / repository.name
                run = subprocess.run(['git', 'worktree', 'add', '--detach', str(target), commit],
                                     cwd=repository, capture_output=True, timeout=60)
                if run.returncode:
                    raise RuntimeError(run.stderr.decode(errors='replace'))
                created.append((repository, target))
                actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=target, text=True).strip()
                assert actual == commit, (tool, actual, commit)
            original = base / 'Plan/tools' / tool
            source_hash = hashlib.sha256(original.read_bytes()).hexdigest()
            result = subprocess.run([sys.executable, str(original)], cwd=base/'Plan',
                                    capture_output=True, timeout=240)
            (output/(tool+'.stdout')).write_bytes(result.stdout)
            (output/(tool+'.stderr')).write_bytes(result.stderr)
            record = {
                'tool': tool, 'plan_commit': PLAN_COMMIT, 'design_commit': DESIGN_COMMIT,
                'original_tool_sha256': source_hash, 'exit_code': result.returncode,
                'started_at': started, 'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
                'stderr_sha256': hashlib.sha256(result.stderr).hexdigest(),
                'scope': 'Original complete check at its original pair; no current-state assertion or native rerun.'}
            (output/(tool+'.json')).write_text(json.dumps(record, indent=2)+'\n')
            if result.returncode:
                raise RuntimeError(tool+': '+result.stderr[-3000:].decode(errors='replace'))
            return record
        finally:
            for repository, target in reversed(created):
                # These are this invocation's temporary detached worktrees only.
                subprocess.run(['git', 'worktree', 'remove', '--force', str(target)],
                               cwd=repository, capture_output=True, timeout=60, check=True)
