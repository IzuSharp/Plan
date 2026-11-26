#!/usr/bin/env python3
"""Run the two already-frozen Go plans serially; retain a restart-visible state."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "freeze.json"
STATE = ROOT / "campaign-state.json"
EVENTS = ROOT / "campaign-events.jsonl"
child = None
interrupted = False


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def event(kind, **values):
    item = {"utc": utc(), "monotonicNs": time.monotonic_ns(), "kind": kind, **values}
    with EVENTS.open("a") as stream:
        stream.write(json.dumps(item, separators=(",", ":")) + "\n")
    temp = STATE.with_suffix(".tmp")
    temp.write_text(json.dumps(item, indent=2) + "\n")
    temp.replace(STATE)
    print(json.dumps(item, separators=(",", ":")), flush=True)


def verify_inputs(freeze):
    bad = [item["path"] for item in freeze["files"] if sha(item["path"]) != item["sha256"]]
    if bad:
        raise RuntimeError("frozen inputs changed: " + repr(bad))


def stop(signum, frame):
    global interrupted
    interrupted = True
    if child is not None and child.poll() is None:
        # The existing runner handles KeyboardInterrupt by retiring the client
        # and its owned PostgreSQL server and preserving command receipts.
        os.killpg(child.pid, signal.SIGINT)


def main():
    global child
    if STATE.exists() or EVENTS.exists():
        raise RuntimeError("campaign state exists; inspect it instead of restarting completed cells")
    freeze = json.loads(FREEZE.read_text())
    if freeze["order"] != ["sqlite", "postgresql"] or len(freeze["plans"]) != 2:
        raise RuntimeError("unexpected campaign order")
    verify_inputs(freeze)
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    event("campaign-start", supervisorPid=os.getpid(), freezeSha256=sha(FREEZE), cpuAffinity=sorted(os.sched_getaffinity(0)))
    for provider in freeze["order"]:
        if interrupted:
            raise InterruptedError("campaign interrupted before next cell")
        plan_path = Path(freeze["plans"][provider])
        plan = json.loads(plan_path.read_text())
        log = ROOT / (provider + "-final-runner.log")
        if log.exists():
            raise RuntimeError("refuse to overwrite campaign runner output")
        started = time.monotonic()
        with log.open("x") as stream:
            child = subprocess.Popen(plan["runnerCommand"], stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            event("cell-start", provider=provider, observerPid=child.pid, runnerLog=str(log), planSha256=sha(plan_path))
            while child.poll() is None:
                time.sleep(1)
                elapsed = time.monotonic() - started
                if int(elapsed) % 30 == 0:
                    event("cell-running", provider=provider, observerPid=child.pid, observerElapsedSeconds=elapsed)
            code = child.returncode
        event("cell-finished", provider=provider, exitCode=code, observerElapsedSeconds=time.monotonic() - started)
        child = None
        if code != 0 or interrupted:
            raise RuntimeError(f"{provider} runner did not finish successfully; no later cell is started")
        verify_inputs(freeze)
    event("campaign-finished", exitCode=0, inputsUnchanged=True)


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        event("campaign-failed", errorType=type(error).__name__, error=str(error), interrupted=interrupted)
        raise
