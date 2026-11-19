# Perf-01 fresh database comparator preparation

Status: **built and golden vectors executed; performance not run by this task**.
The integration owner controls all formal timing and HTTP/SQL readiness. No
historical B23 timing or readiness result is reused as a new observation.

## Sources and builds

The reusable producer is `tests/Perf01.Database/prepare_comparators.py` in
NativeWeave commit `c57a684eb55faeade60270981773bd15133e4f53`. It was executed
against that committed source snapshot. Comparator application/runtime sources
remain the unchanged B23 implementations inherited from baseline
`ea5fa528035d025bd7a28698ee7c71194432236c`; the Perf-01 commits at this point add
only harness files. Copies of all selected source, root build, SQL resource and
lock inputs are retained in the build output.

```sh
source /workspace/scratch/01c249676f47/perf01-toolchain/env.sh
python3 tests/Perf01.Database/prepare_comparators.py \
  --product-root /workspace/scratch/01c249676f47/.worktree/Perf-01-db-linux/NativeWeave \
  --output /workspace/scratch/01c249676f47/perf01-build/comparators \
  --amalgamation /workspace/scratch/01c249676f47/perf01-toolchain/cargo/registry/src/index.crates.io-1949cf8c6b5b557f/libsqlite3-sys-0.37.0/sqlite3
```

The producer verified SDK **11.0.100**, Rust **1.100.0**, shared locked engine
versions, and the expected SQLite amalgamation hashes. Both source copies and
original selected files were unchanged after build. Managed restore used
`--locked-mode`; publish used `Release`, `linux-x64`, `PublishAot=true` and
explicit `IlcInstructionSet=x86-64-v2`. Direct Rust used `--locked --release`,
`-C target-cpu=x86-64`, thin LTO, one codegen unit and unwinding. The separate
managed SQLite library used the existing B23 producer and reported **3.51.3**.

## Actual artifacts

All paths below are under
`/workspace/scratch/01c249676f47/perf01-build/comparators`.

| Artifact | SHA-256 |
| --- | --- |
| `comparators.json` | `6149c4a5895bacaa4287caf2ebfc23262b8a488ca0cc66883513a5a3dce59db1` |
| `direct-rust/nativeweave-b23-direct-rust` | `1c74ea9f982b6f8a316383663ec7dcbb51bb585a35026dc97573a9286dd09736` |
| `managed-aot/NativeWeave.Benchmarks.ManagedComparator` | `19c39bfc9685f681135684eac1c038ef3db884f41d87af0849a73b95422163a8` |
| `managed-aot/libsqlite3.so` | `2b99b38b699d3834c39b1e38d089dade94f64f8beac82d2461217d81a251b654` |

`comparators.json` uses the existing B23 schema and fresh absolute pins. The
actual B23 `comparator_route` resolver successfully verified each artifact,
source file and lock against it. The manifest retains the existing applicability
and architectural caveats; no claim of exact overload/byte-credit/cancellation
equivalence is added for the comparison hosts.

## Executed checks and limits

Both new executables ran `--golden-vectors`. Their parsed output matched the
independent B21 `golden.py` oracle and immutable `golden-v1.json`. The managed
executable also emitted the actual `B23_RUNTIME dynamic=False` witness. Captured
stdout/stderr hashes, every build command, versions and setup durations are in
`progress.json` and `logs/`; selected source hashes are in `source-inputs.json`.
The independent SQL/HTTP workload oracles still need to run against these exact
binaries. Golden vectors alone do not establish persistence, protocol operation,
steady-state capacity, performance improvement or long-run stability.

Local build output is reproducible setup evidence, not a durable publication
location. The integration handoff must record the final retrievable artifact
location and retention alongside the complete Perf-01 evidence. Builds were
stopped after successful completion so the integration owner can reserve the
machine for exclusive profiling and timing.
