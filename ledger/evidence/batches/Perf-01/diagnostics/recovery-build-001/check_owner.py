"""Bounded synthetic ownership checks; no product source/build/workload."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import signal
import sys
from owner import command, enable_subreaper, proc, public_tree, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--driver', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    enable_subreaper()
    tree = public_tree(args.driver.resolve())
    cases = [
        ('normal', 'print("normal")', 5, True),
        ('timeout', 'import time; time.sleep(30)', .2, False),
        ('detached', 'import os,time; p=os.fork();\nif p == 0:\n os.setsid(); time.sleep(30)\nelse:\n time.sleep(.2)', 5, False),
    ]
    results = []
    for name, code, timeout, success in cases:
        row = dict(label=name, argv=[sys.executable, '-c', code], cwd=str(root), timeout_seconds=timeout, environment_overrides={})
        passed = False
        try:
            asyncio.run(command(row, dict(os.environ), root / name, tree))
            passed = True
        except RuntimeError:
            pass
        path = root / name / 'receipt.json'
        receipt = json.loads(path.read_text())
        assert passed == success, (name, receipt)
        assert receipt['retired'] and not receipt['live_owned_after'] and not receipt['owner_children_after'], (name, receipt)
        assert all(proc(item['pid']) is None or proc(item['pid'])['start_ticks'] != item['start_ticks'] for item in receipt['owned_processes']), (name, receipt)
        if name == 'normal':
            assert receipt['status'] == 'completed' and receipt['exit_code'] == 0 and not receipt['signals'] and receipt['failure'] is None, receipt
        elif name == 'timeout':
            assert receipt['status'] == 'failed' and receipt['failure'].startswith('TimeoutError:') and receipt['exit_code'] != 0, receipt
            assert any(item['signal'] == signal.SIGTERM for item in receipt['signals']), receipt
        else:
            assert receipt['status'] == 'failed' and receipt['exit_code'] == 0, receipt
            assert receipt['failure'] == 'RuntimeError: Producer exited with live owned/adopted descendants', receipt
            assert len(receipt['owned_processes']) >= 2 and receipt['signals'], receipt
        results.append({'check': name, 'receipt': str(path), 'sha256': sha(path), 'expected_command_success': success})
        print('PASS', name, flush=True)
    print(json.dumps({'checks_passed': len(results), 'receipts': results}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
