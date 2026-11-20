# Perf-01 CI125 A20 ownership and sanitizer evidence

This is the actual finite A20 result for public head
`423c07c1d8969298e605e9488b4c271ea3d0148a`, which includes the gRPC
header-credit correction and the still **unretained** managed scratch candidate.
It grants **zero performance or 30-minute measurement credit**. It does not
replace the separately failed local corrected-control B18 Native AOT gate.

## Exact source and archive

[A20 job 136256707444](https://github.com/IzuSharp/NativeWeave/actions/runs/44726962784/job/136256707444)
in CI125, attempt 1, completed successfully. Its actual checkout is
`45a20165f6344f91b79ad703b36cebb0cf26bd9c`. GitHub commit reads and the
archived source-commit log agree. Checkout and public head have the same tree,
`86c4ac7a7c4d17f705d3fa52af4fafdb6959d2da`. The checkout parents are frozen
main `ea5fa528035d025bd7a28698ee7c71194432236c` and the stated public head.
Source status is empty and the harness reports source unchanged.

| Field | Actual observation |
| --- | --- |
| [GitHub artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44726962784/artifacts/14624890818) | 14624890818 |
| Complete ZIP bytes | 9,641,850 |
| Complete ZIP SHA-256 | `13dfa77668cbaa9cb453089e8963aa0946e0487144c408fb0d6e6c0e34d2d229` |
| ZIP members | 199 |
| Result JSON bytes | 72,266 |
| Result JSON SHA-256 | `d24371088a8ec880ea8b7d023b7a9658a0e87b7ce2f4ce11eb142df98bb8132c` |
| GitHub expiration | 2026-12-04 11:23:10 UTC |

The artifact connector fetched the complete ZIP. Its actual byte count and
SHA-256 match GitHub metadata. The offline inspector read named members
directly without full extraction. The owner retains the complete archive,
identity reads and inspection receipts. Artifact availability beyond the stated
expiration is not promised. The small repository summary and manifest remain
available while repository history is retained.

## Actual execution

The original A20 harness ran from **2026-11-20 11:22:02 through 11:23:10 UTC**.
Preparation-only is false, source-dirty is false and source-unchanged is true.
All 48 commands returned their expected actual exit codes without timeout.
All 96 declared stdout/stderr hashes were checked against archived bytes.
The summary preserves the deliberate nonzero negative outcomes.

| Scope | Actual evidence |
| --- | --- |
| Managed ownership and races | JIT and Native AOT each passed 8,925 assertions and 72 finite orders |
| Maintainer samples | Each execution mode passed basic 2 and advanced 886 checks |
| Sanitizers | Address, undefined-behavior and leak checking enabled; original halt and stacktrace options verified |
| Fuzz | Terminal DONE and actual executed-unit counter both report 20,000; coverage 104 and features 173 |
| Corpus | 19 initial and 71 final files; every declared corpus hash verified |
| Independent negative oracle | Original and minimized inputs returned expected exit 77; minimizer and corrected replay returned 0 |
| Oracle size | Original 61 bytes; minimized 61 bytes; no size reduction claimed |
| Managed negative children | JIT/AOT quarantine exit 43 and stale-cookie exit 42 with required markers |
| Fatal children | Invalid-pointer and wrong-owner release each returned expected exit 1 with ASan diagnostics |

Seven archived outputs were independently hashed: two AOT executables, three
C fuzz/fatal binaries and two oracle inputs. The original result lists 19
artifact identities; 12 are outside the ZIP and are not claimed independently
rehashed by this inspection. No unexpected-failure files were present. The
actual coverage, feature and corpus counts above belong to CI125; prior CI124
values were not copied into this report.

## Boundaries and inspection method

Sanitizer instrumentation covers the C serialized-input decoder, independent
C oracles and C fatal driver. Stable Rust libraries, CLR and Native AOT runtime
are explicitly uninstrumented. CI used .NET 11.0.100, Rust 1.100.0 and Ubuntu
Clang 18.1.3. The measurement host's fixed Clang 19 and workload settings remain
separate. No sanitizer was disabled to avoid a local failure.

The existing strict CI124 projection was reused with only the actual source,
artifact, run, job and location substitutions. Its CPU 8 execution exited 0 in
**0.115544184 seconds**, without running any test or workload. The manifest
binds the private inspector, actual execution and complete-download receipts.
Existing CI124 reports and archives were not changed.

This published projection contains fixed roles, numbers, booleans and hashes.
Raw commands, logs, host paths, process identifiers and operational controls are
excluded. The separate [canonical report](../ci125-canonical-001/README.md)
records the remainder of CI125. The local corrected-control B18 run passed JIT
but failed AOT at the second persistent TLS/H2 call with the original Internal
dispatch error. That failure, candidate retention, capacity and final-after long
tests remain separate and unresolved by this A20 result.
