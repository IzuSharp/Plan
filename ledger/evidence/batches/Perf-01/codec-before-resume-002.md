# Perf-01 unchanged codec before attempt002

Status: source prepared for root review. No build, codec workload, supervisor,
or verifier has been executed for attempt002. The separately recorded finite
argv/hash/fresh-path boundary checks are preparation evidence, with zero duration
credit. Root owns publication, the exclusive timing queue and actual execution.

## Why another output directory is required

Attempt001 was interrupted by an execution runtime reset. Its original execution
receipt remains unchanged, including its last `running` state and absent actual
exit. Its retained partial rows are not a completed 30-minute sample. No normal
recovery, drain or exit is inferred. The original raw files, log, receipt and
immutable global freeze are never rewritten by this resume.

`codec-before-resume-002.json` inherits the published global freeze SHA-256
`85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3`
and original codec command document SHA-256
`cd7c7eafe989b1b3aada00d6cf5ab7732f331a75ddde3618844b82b05e0711e7`.
It is a fresh attempt of the same fixed workload, not a new selection or policy.

The supervisor derives the expected two command objects directly from that
hash-checked original document and requires complete equality with the resume
objects. Its only argv substitutions are:

| Command | Argument | Original suffix | Attempt002 suffix |
|---|---|---|---|
| Measurement | `--output` | `long/before/codec-001` | `long/before/codec-002` |
| Post-run verifier | `--output` | `long/before/codec-001` | `long/before/codec-002` |
| Post-run verifier | `--receipt` | `long/before/codec-001-verification.json` | `long/before/codec-002-verification.json` |

Command IDs, log and supervisor receipt names also use attempt002. No other
measured argv byte changes. Source, A21, producer manifest, corpus, actual package
and native verification, mixed action/interface cycle, 192 operations/s, two
workers, queue64, in-flight256, 1802 measurement seconds, 20 warmup seconds,
10 recovery seconds at 1/s, 60 idle seconds, CPUs, deadline and all original gates
remain fixed. Planned counts remain 3,861 warmup, 346,005 measurement and 12 recovery
operations. Only actual completed and independently verified rows grant credit.

## Exact reviewed execution entry point

After root integrates and publishes the exact source, verifies its readback,
confirms prior process cleanup and reserves the exclusive timing window:

```bash
PERF01_ROOT=/workspace/scratch/01c249676f47
source "$PERF01_ROOT/perf01-toolchain/env.sh"
taskset -c 8 /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  "$PERF01_ROOT/.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01/run_codec_before_resume_002.py" \
  --source-sha256 dac0016659b6352bb0e2c93c80fb8ad276507c113a635a72b3250c12cb01f131
```

The resume command document SHA-256 is
`225c9295a102de22a59e2bea01f2bb3f3abecbea98313f5b7c157322916a9e12`.
The supervisor binds this value internally and rechecks its supplied exact source
SHA before each command. It also rechecks the original freeze/publication record,
original source/metadata/selection pins, exact Python version/executable hash,
Linux x64/kernel and normalized (`strip`) kernel boot identity. The existing
unchanged codec driver retains actual corpus/artifact/native identity checks.

Do **not** wrap the whole supervisor in another flock. The measurement argv keeps
its original `/usr/bin/flock --nonblock timing.lock` prefix. Only the verifier
step is guarded by the supervisor's nonblocking `fcntl.flock` on that same file;
the verifier argv itself has no additional flock. Root retains queue ownership
between commands. A busy lock is orchestration contention, not an application
correctness result; inspect the actual log rather than infer its cause from a
shared nonzero exit code.

## Durable supervision and acceptance

The supervisor claims these fresh files and never resumes or overwrites an
existing attempt002 receipt:

- `ROOT/perf01-run/before-codec-long-002-execution.json`
- `ROOT/perf01-run/before-codec-long-002-supervision.jsonl`
- `ROOT/perf01-run/codec-before-r241-long-002.log`
- `ROOT/perf01-run/codec-before-r241-long-verify-002.log`

It rejects an existing output directory, verification receipt, either command log,
or a dangling symlink at a fresh path. Each command is rechecked immediately
before launch. Verification requires an actually observed measurement exit zero,
the new completed result/summary and a still-absent new verification receipt.

Actual child exits come only from `Popen.wait`/`poll`; source preparation, progress
and file existence never supply an exit code. The supervision journal flushes
and fsyncs started/ended events, errors and bounded progress snapshots at roughly
45-second intervals. The atomic execution receipt is updated alongside it. It
keeps only small phase-progress JSON; no growing operations/events file is read
inside the measurement window. Child stdout/stderr go to distinct durable logs.

Any command error stops the queue. Acceptance requires both actual exits zero,
`accepted=true` from the unchanged verifier, this exact new output and verifier
identity, the original controller/A21/manifest/corpus identity, and a finite actual
ordinary-operation duration credit of at least 1800 seconds. Original correctness,
service, owner drain and recovery requirements remain in the unchanged driver
and verifier. The actual returned duration is retained; 1802 nominal seconds do
not imply acceptance.

This supervisor does not detach, create a new session or PID namespace, or try to
survive execution-runtime controls. A runtime loss may leave only its last known
state. A caught orchestration failure records whether its direct child remains
live; root must use existing supervision/cleanup before another workload. No
successful exit, descendant cleanup or normal drain is fabricated. All failures
and interruptions retain zero accepted credit and their original outputs.

## Preparation validation and remaining gate

`checks/codec-before-resume-002/static_boundaries.py` extracts only the existing
supervisor's pure argument/hash/fresh-path functions from its AST. It checks exact
argv differences, unchanged configuration/selection/gates, unique selectors,
matching/mismatching small-file hashes, and missing/existing/dangling fresh paths
inside a temporary directory in its own evidence subtree. It never imports or
executes supervisor `main`, any codec/verifier command, a service or a build.
The actual command, exit, stdout, source pins and results are retained beside it.

The actual finite execution on 2026-11-19 at 21:31:00 UTC returned **exit 0,
21 checks passed**, using the locked Python 3.12.14 on CPU8. Measurement argv
length45 changes only index44; verifier argv length11 changes only indices8 and10.
The result SHA-256 is
`2f4b1185a46b0d84118f6f01ecc36a1eaaeac4a09352c0cd13c19d329422df58`.
This did not execute the supervisor preflight or claim that a load is valid.

Root still must review the final source and actual preparation receipt, integrate
and publish it, then perform the single complete attempt. The original interrupted
attempt and this preparation grant no long-test credit. The paired after workload
remains exactly the original freeze; no after producer hashes are invented here.
