# Perf-01 CI126 A20 ownership and sanitizer evidence

This is the actual finite A20 result for public head
`12c477f0cdbc01fb026e98ac0e26eb45617424ed`. That source contains both the
gRPC header-credit correction and managed request-admission lifetime correction,
alongside the still **unretained** managed scratch candidate. This report grants
**zero performance, capacity or 30-minute measurement credit**. The dedicated
local B17, B18 and shared-module gates retain their own outcomes.

## Exact source and archive

[A20 job 136276995126](https://github.com/IzuSharp/NativeWeave/actions/runs/44732929976/job/136276995126)
in CI126, attempt 1, completed successfully. Its actual checkout is
`abe83d5ae77049a2d4a7795ff45958a197bc787c`. The archived source-commit log
and independent GitHub commit reads agree. Checkout and public head have the
same tree, `0c763ba3b908dcc289528369231daf1788f87571`. Checkout parents
are frozen main `ea5fa528035d025bd7a28698ee7c71194432236c` and that public
head. Source status is empty and the harness reports unchanged source.

| Field | Actual observation |
| --- | --- |
| [GitHub artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44732929976/artifacts/14626977819) | 14626977819 |
| Complete ZIP bytes | 9,641,928 |
| Complete ZIP SHA-256 | `9e9ceb949d52f11886227787b1ad319e106d32cb8acf627d8a18f51da7ed2e86` |
| ZIP members | 199 |
| Result JSON bytes | 72,268 |
| Result JSON SHA-256 | `686bb1736ed670dcaa439bbd01034c6eb9b85c219fc9bc31aed14e4beb27d59f` |
| GitHub expiration | 2026-12-04 12:07:45 UTC |

The complete ZIP was downloaded and its actual size and SHA-256 match GitHub
metadata. The offline inspector read named members directly without full
extraction. Complete archive bytes, identity reads and inspection receipts are
retained privately. Artifact availability beyond the expiration is not promised.
The small repository summary and manifest remain retrievable while repository
history is retained.

## Actual execution

The original A20 harness ran from **2026-11-20 12:06:23 through 12:07:45 UTC**.
Preparation-only and source-dirty are false; source-unchanged is true. All 48
commands returned their expected actual exit codes without timeout. All 96
declared stdout/stderr hashes were verified against archived bytes. Deliberate
nonzero negative outcomes remain explicit in the numeric checklist.

| Scope | Actual evidence |
| --- | --- |
| Managed ownership and races | JIT and Native AOT each passed 8,925 assertions and 72 finite orders |
| Maintainer samples | Each mode passed basic 2 and advanced 886 checks |
| Sanitizers | Address, undefined-behavior and leak checking enabled; original halt and stacktrace settings verified |
| Fuzz | Terminal DONE and actual executed-unit counter both report 20,000; coverage 104 and features 180 |
| Corpus | 19 initial and 71 final files; every declared corpus hash verified |
| Independent negative oracle | Original and minimized inputs returned expected exit 77; minimizer and corrected replay returned 0 |
| Oracle size | Original 61 bytes and minimized 61 bytes; no size reduction claimed |
| Managed negative children | JIT/AOT quarantine exit 43 and stale-cookie exit 42 with required markers |
| Fatal children | Invalid-pointer and wrong-owner release each returned expected exit 1 with ASan diagnostics |

Seven archived outputs were independently hashed: two AOT executables, three
C fuzz/fatal binaries and two oracle inputs. The original result lists 19
artifact identities; the remaining 12 are outside the ZIP and are not claimed
independently rehashed. No unexpected-failure files were present. These are
CI126 observations; earlier coverage and feature counts were not copied.

## Inspection method and limits

The strict CI125 inspector was reused with only actual source, artifact, run,
job and location substitutions. It completed on CPU 8 with exit 0. The manifest
binds its source, projection receipt, source identity reads and download receipt.
No CI command, product test or workload was rerun locally. Existing CI125
reports and archives were preserved.

Sanitizer instrumentation covers the C serialized-input decoder, independent
C oracles and C fatal driver. Stable Rust libraries, CLR and the Native AOT
runtime remain explicitly uninstrumented. CI used .NET 11.0.100, Rust 1.100.0
and Clang 18.1.3. These tools and binaries are separate from the measurement
host's fixed Clang 19, locally produced domain packages and loaded native bytes.

The A20 job had completed when this projection was prepared; the full CI run
was still in progress. Its eventual canonical/package result is a separate
report. This A20 result does not claim execution of every module's dedicated
suite, validate later source changes, replace a failed local gate, select the
scratch implementation or grant acceptance of the final application workload.

The published projection contains fixed roles, numbers, booleans and verified
hashes. Raw commands, logs, host paths, process identifiers and operational
control records are excluded.
