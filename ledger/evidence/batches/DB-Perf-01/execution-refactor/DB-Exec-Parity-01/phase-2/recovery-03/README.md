# Recovery continuation 03 — active matched-build recovery

Captured UTC: 2026-11-27T04:40:29.787814+00:00

The owner resumed the task with later reported progress about native `-g` build
options and a relation transfer candidate's Query.Binding test. Neither the previous
local root nor its later candidate source/logs is available in this environment.
The remote recovery boundary remains Plan `4b9859ec`. That reported progress is
not assigned current artifact or test credit. Stage 1 is retained, not repeated.

All five Stage 1 archives, 91 parts and 6,132 extracted files were SHA256 verified.
See `stage1-extracted-verification.json`. Locked SDK 11.0.100, LLVM 23.1.5, CMake
4.3.3 and Ninja 1.13.2 have been restored and verified. Real PostgreSQL 18.0 was
compiled from locked, patched sources and passed a TCP startup/query/shutdown
check. Unix-domain sockets are unavailable; the retained campaign already uses TCP.

## Matched uninstrumented baseline

Unchanged product main `7ff7b57` was rebuilt with exactly `-O3 -DNDEBUG -g` for both
C and C++, using the retained product producer via the external driver recorded
here. These are uninstrumented Release builds with debug information. Ordinary
candidates will use the same driver, options and dependency identities. The old
no-debug native images retain their original hashes; `.text` comparisons are
recorded without treating build differences as optimization. Dapper's shared
SQLite engine is being rebuilt to the same actual engine compilation recipe.

Four new baseline-final Native AOT consumers and two standalone local packages
are built. Only the previously approved process GC pause endpoint property was
added to the copied measurement source. The original mixed35 manifest is unchanged.
Actual generated C#, ELF/debug, native/package and source hashes are in
`matched-baseline-final-builds.json`. These builds have no workload acceptance
credit yet. Runtime defaults and original workloads remain unchanged.

## Active experiments

The selected narrow canonical decimal parser was recovered as a new source
identity. Worker-D's admitted native execution and managed coordinator halves
are being rebuilt separately from unchanged main. The exact committed managed
patch is preserved here; it has only a successful library compile so far.
Current native correctness, managed AOT, ordinary reverse A/B, integrated package
acceptance and release verification remain required.

Relation first- and second-layer diagnostics are being recovered separately.
Only source-bound allocation/count results will choose that private optimization;
public Combine snapshots and all ownership/error/limit semantics remain required.
Previously rejected A, C, lease-B and ready-row-C are not reimplemented.

## Recovery position

Current root: `/workspace/scratch/0669b59f9cae/DB-Exec-Parity-01`. Source `toolchain/environment.sh`.
Product integration worktree: `worktrees/Korda`; Plan and Design continue their
existing task branch and Draft PR36/PR21. The untouched baseline producer is
`worktrees/Korda-baseline`. Experimental worktrees have task-named branches.
The tracked patches in this directory preserve new committed source independently
of the temporary root. New ELF/packages/logs still require publication with their
receipts before a final measurement claim.

Final campaign remains **0/4**. Next: finish causal/correctness gates and matched
ordinary A/B, integrate supported candidates, run the zero-rejection/pressure
screen, freeze current identities and execute adequate same-host before data plus
four serial 1800-second final cells. All performance work stays local. No CI
benchmark/profiling/calibration/load route is added or invoked. Normal reviewed
merge, existing CI, rule-selected release and public NuGet AOT verification remain
authorized and pending. Go drafts remain untouched.
