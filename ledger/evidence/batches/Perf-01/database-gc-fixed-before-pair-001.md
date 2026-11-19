# Fixed-before DB scheduler GC equivalence pair

Status: commands prepared, no application load executed by the author. The
separate finite policy gate actually passed four tests with exit 0; its exact
Python/source/argv/stdout/stderr receipt is in
[`checks/database-scheduler-gc-unit-001/`](checks/database-scheduler-gc-unit-001/execution.json).
The immutable source is NativeWeave `0b2af54419ecf6a11ec83a45725b1c5fbbaeb0d0`.
The common A21, common worker/supervision, target and common verifier remain
byte-identical to ce2. C#/Rust and the before package are unchanged.

The [command document](database-gc-fixed-before-pair-001.json) has SHA-256
`21b8f09254b41cbfe46f817d3fb61c0360b1470323b5191ef56c92e73c7d22a9`.
It copies the original frozen PostgreSQL command and dependency pins, changes
only the declared diagnostic parameters/source path, and adds an explicit GC
policy. Both commands use the same immutable new driver and actual before
package/observer. They differ from each other only in policy and fresh output.

| Setting | Both cells |
| --- | --- |
| Protocol/provider/mix | HTTP/1.1 PostgreSQL, alternating durable cycle / typed 100-row page |
| Offered rate/concurrency | 144/s, C16 |
| Effective request schedule | 120 seconds, 17,282 planned operations |
| Warmup/recovery/idle | 16 / 32 same-process cycles / 60 seconds; separate from measurement |
| Service / generator CPU masks | 2,3 / 0,1 |
| Service bounds | Zero unexpected errors, p99 at most 500 ms, application RSS at most 256 MiB |
| Generator bound | Unchanged 100 ms dispatch lag; preserve every violation |
| First / second policy | `automatic` / `deferred` |
| Formal long credit | Zero for both; this is not a product before/after comparison |

## Exact owner launch

The integration owner must finish/pause archive work, hold the exclusive
measurement window and confirm no other load/build/profile remains. Source the
locked toolchain environment. Run the following in an owned execution session;
the exec replaces the small metadata launcher with the command's original
nonblocking flock, taskset and DB supervisor. Do not run a shell loop unattended.

```bash
PERF01_ROOT=/workspace/scratch/01c249676f47
source "$PERF01_ROOT/perf01-toolchain/env.sh"
PERF01_PY=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF01_PAIR_DOC="$PERF01_ROOT/.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01/database-gc-fixed-before-pair-001.json"
taskset -c 8 "$PERF01_PY" - "$PERF01_PAIR_DOC" automatic <<'PY'
import hashlib, json, os, sys
from pathlib import Path
def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
path = Path(sys.argv[1])
assert sha(path) == '21b8f09254b41cbfe46f817d3fb61c0360b1470323b5191ef56c92e73c7d22a9'
document = json.loads(path.read_text())
assert 'NW_PERF01_GC_CONFIG' not in os.environ
for filename, expected in document['required_source_and_metadata_sha256'].items():
    assert sha(filename) == expected, filename
python = document['python']
assert sha(python['executable']) == python['recorded_executable_sha256']
selected = next(row for row in document['commands'] if row['policy'] == sys.argv[2])
assert not Path(selected['output']).exists()
os.chdir(selected['working_directory'])
os.execvp(selected['argv'][0], selected['argv'])
PY
```

Observe the first process's actual exit, summary, policy receipt, durable/drain
checks and supervision cleanup. Then run the same block with `deferred` as its
second positional argument. Preserve a failed first sample; do not relabel it
or rerun into its directory. The owner decides whether a new diagnosis is
needed before proceeding.

## Checks and next boundary

The command document lists the exact post-run requirements. Read both normal
summaries and hash-bound policy receipts; compare the dataset/count/mix and
before artifact identities, and inspect generator RSS/CPU and dispatch evidence
separately. The driver already rejects missing/wrong-source/wrong-process or
non-restored policy receipts; deferred requires zero GC collection-count deltas
inside the original worker call. All original correctness, persistence,
recovery, idle, cleanup and service checks remain required.

An interrupted command uses its actual cell's existing `control.json` protocol.
TERM/KILL cleanup is not normal drain or GC restoration and grants no gate
acceptance. No generic stop/restart framework is added here.

The 120-second pair has a smaller planned heap than the 259,526-entry PostgreSQL
long cell. It cannot establish long-run memory stability or exclude a later
pause. Fresh deferred DB calibration/noise and the prospective DB-only amendment
remain separate work. Previously frozen paired long rates stay PostgreSQL
144/s C16 and SQLite 40/s C16; all service/lag/resource constraints stay unchanged.
Old automatic-GC noise/capacity results are preserved under their original
identity and cannot qualify the new deferred cohort. HTTP/gRPC/codec are outside
this amendment.
