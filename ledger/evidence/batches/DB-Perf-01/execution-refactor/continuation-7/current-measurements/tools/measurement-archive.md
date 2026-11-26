# Retain original measurement evidence

`archive_measurement_evidence.py` is a new offline retention tool. It neither
executes a workload nor evaluates correctness, throughput, duration or final
acceptance. Original analyzer, selector, freeze and raw-result bytes remain
unchanged. It never deletes an input or overwrites an existing output directory.

As prepared, the actual final four segments have **not** been archived or run.
The immediate intended scope is all completed 17da short measurements, the
rejected 92b9230 paired experiment, the completed 120-second baseline supplement,
and the pre-final freeze. A later final archive requires its own fresh output and
the real final analysis/audit inputs; this page does not grant that work credit.

## What enters an archive

The tool takes the union of every file under `--measurements`, optional
`--retain-root`/`--retain-file` inputs, and the path-to-SHA-256 objects named by
one or more `--inventory JSON JSON_POINTER EXPECTED_JSON_SHA256` arguments.
Each inventory document itself is preserved. Use the exact field from each
actual report, such as `/inputFiles`; missing fields, malformed hashes, missing
files, conflicting hashes and changed bytes fail the operation. This union is
explicit: a pre-final freeze alone does not add every earlier comparison's
producer/source input. Include the actual baseline/short/diagnostic input maps
or their already retained source evidence as needed for the chosen scope.

Every included file preserves its original bytes, including failed stdout,
malformed result files and non-UTF-8 diagnostic bytes. There is no result
rewriting. Members under the measurement root use `measurements/...`; other
inputs use `original-inputs/...` with their absolute source path below that
prefix. File symlinks are read as their actual target bytes, with the original
link and resolved path recorded. Directory symlinks require an explicitly
retained real directory and otherwise fail, rather than silently omitting a
subtree. Repository metadata is rejected.

Each original has its absolute path, origins, byte size and actual SHA-256 in
`manifest.json`. Included records also name the archive member. Excluded
records explicitly carry a reason; excluded bytes are still hashed and checked
again before success. The archive does not claim to recover executable or
package bytes from their hash.

## Exclusions

| Input | Default handling |
| --- | --- |
| SQLite database and recognized sidecars | Hash and record; omit bytes |
| `.nupkg` / `.snupkg` | Hash and record; omit bytes |
| Executable/native ELF, PE, object/static-library/symbol files | Hash and record; omit bytes |
| ELF core dump | Preserve raw failure bytes |
| Measurement JSON/JSONL, stdout, logs, plans, receipts, manifests, scripts, copied/generated source | Preserve raw bytes |
| Existing database archive | Preserve by default; explicitly exclude its exact path as described below |

Use `--exclude-file database /absolute/stopped-database.tar.gz` for each archive
produced by the separate stopped-database retention tool. Keep that tool's
manifest and receipt included; excluding its whole evidence directory would
also omit these small records. PostgreSQL data directories without a SQLite
header require `--exclude-root database /absolute/pgdata` if present in a
retained tree. Explicit root rules only classify files already included in the
input union; they do not silently walk arbitrary external roots.

Other accepted explicit reason codes are `package`, `binary`, `package-cache`
and `binary-build-output`. Every explicit excluded file is added to the hash
inventory even if it is outside the measurement tree. These are provenance
exclusions, not new claims that each old binary can be reproduced bit for bit.

## Run only in an agreed measurement gap

The script hashes all originals twice, streams gzip compression, reads every
archive member back, and checks both the complete original file inventory and
file identities for changes. Run serially with the separate database-retention
tool, outside builds and timed measurements. It writes only the fresh output
directory. A failed attempt retains its `failure.json` and any partial output;
use a new directory for a corrected attempt.

The following is the minimum pre-final invocation, from the Plan worktree. It
does not assert that the baseline/diagnostic input union is complete. Add each
actual additional report inventory and each exact database-archive exclusion
before executing the full intended scope. The parent of `--output-dir` must
already exist, and the directory itself must not.

```bash
python3 ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/tools/archive_measurement_evidence.py \
  --measurements /workspace/scratch/fd78534029f7/measurements \
  --inventory /workspace/scratch/fd78534029f7/measurements/final-freeze-01.json /inputFiles fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a \
  --scope 'pre-final: completed short/paired/baseline results and supplied pinned inputs; zero final segments' \
  --output-dir /workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/retained-pre-final-01
```

Success produces `receipt.json`, the original-file `manifest.json`, and
`evidence.tar.gz`. The manifest is also the final archive member. Tar and gzip
timestamps and owner metadata are normalized without changing member bytes.
The receipt records the actual start/end time, archive/manifest hashes, byte
counts, complete readback and input revalidation. `finalAcceptanceCredit` is
always false: final acceptance remains the existing analyzer plus frozen
identity supplement.

## Finite controls

The current tool SHA-256 is
`0e3d18c4c67072c119cba0477fc2ead22f60ab6c0c722a40dbee1960f195be3b`.
It passed all 20 controls in [archive-controls-02.json](archive-controls-02.json),
executed by [check_archive_controls.py](check_archive_controls.py) in 0.97 seconds.
Only tiny synthetic files and temporary output directories were used: zero real
measurement inputs, product executions, real evidence archives or final credit.
Controls include exact raw/non-UTF-8 byte preservation, file symlinks, retained
core dumps and library-named JSON reports, explicit database-archive exclusion,
wrong/missing/malformed input hashes, missing inputs, existing output, lexical
and physical output nesting, directory-symlink rejection, and no-replace archive
publication against both an existing regular file and a dangling symlink. These finite
controls do not replace each actual archive's member readback and input checks.

The earlier 17-control record [archive-controls-01.json](archive-controls-01.json)
and its tool SHA `1fb46f27…` remain unchanged. Independent source review by the
native-review agent found no blocking issue under the explicit-input/fresh-output
scope, and recommended replacing the final check-then-rename publication with
atomic no-replace publication. The current code uses a same-directory hardlink
followed by unlink and creates its output directory with mode 0700; the added
three controls cover absent, existing-file and dangling-symlink destinations.
That review did not run a real archive or inspect any database fixture.

To repeat controls, supply a fresh result path:

```bash
python3 ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/tools/check_archive_controls.py \
  --tool /workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/tools/archive_measurement_evidence.py \
  --output /tmp/DB-Exec-10-archive-controls-next.json
```
