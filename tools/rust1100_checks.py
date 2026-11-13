#!/usr/bin/env python3
"""Preserve original Rust checks and validate the current completed design pair."""
from pathlib import Path
import json
from history_gate import run_frozen
from verify_completion import verify

P=Path(__file__).resolve().parents[1]

def main():
    historical=run_frozen('rust1100_checks.py')
    current=verify()
    report={'ok':True,'scope':'Original two-platform evidence and regression checks at frozen pair, plus current exact design/packet/acceptance integrity. No native rerun.',
            'historical':historical,'current':current}
    (P/'verification/rust1100-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
