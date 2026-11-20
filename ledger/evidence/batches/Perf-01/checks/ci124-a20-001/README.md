# Perf-01 CI124 A20 ownership and sanitizer verification

This is the actual A20 functional result for the **unretained** gRPC scratch
candidate, public head `458939dab00d4080cd36076d31d912114f245340`.
It grants zero performance or 30-minute measurement credit. It does not
replace the separately failed local B18 cancellation/retirement gate.

## Exact source and archive

[A20 job 136218971778](https://github.com/IzuSharp/NativeWeave/actions/runs/44715862136/job/136218971778)
in CI124, attempt 1, completed successfully. Its actual checkout is
`a2cb240f0c08face6eac2779d66e14b2ed828566`. GitHub commit reads and the
archived source-commit log agree; checkout and public head have the same tree,
`6dad1215d22d5c950c33dafeae3e9d876ec7cd0b`. The checkout parents are frozen
main `ea5fa528035d025bd7a28698ee7c71194432236c` and the stated public head.
Source status is empty and the harness reports source unchanged.

| Field | Actual observation |
| --- | --- |
| [GitHub artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44715862136/artifacts/14618728592) | 14618728592 |
| Complete ZIP bytes | 9,642,833 |
| Complete ZIP SHA-256 | `68c6c8e853cd53a177918845ceeb6caa5830b8f9530f65df605f1f7765d18734` |
| ZIP members | 202 |
| Result JSON bytes | 72,618 |
| Result JSON SHA-256 | `8c0b797e0194108aeee6eb988171fe0be4124df83d4e091dae868b3e7c5a8348` |
| GitHub expiration | 2026-12-04 10:04:37 UTC |

The normal artifact connector fetched the complete ZIP. Its actual byte count
and SHA-256 match GitHub metadata. The offline inspector read named members
directly without full extraction. The owner retains the complete archive,
identity reads and inspection receipts. Artifact availability beyond the stated
expiration is not promised. The small repository summary and manifest remain
available while repository history is retained.

## Actual execution

The original A20 harness ran from **2026-11-20 10:03:23 through 10:04:36 UTC**.
Preparation-only is false; source-dirty is false; source-unchanged is true.
All 48 commands returned their expected actual exit codes with no timeout.
All 96 declared stdout/stderr hashes were checked against archived bytes.
The numerical summary preserves deliberate nonzero negative outcomes.

| Scope | Actual evidence |
| --- | --- |
| Managed ownership and races | JIT and Native AOT each passed 8,925 assertions and 72 finite orders |
| Maintainer samples | Each execution mode passed basic 2 and advanced 886 checks |
| Sanitizers | Address, undefined-behavior and leak checking enabled; original halt and stacktrace options verified |
| Fuzz | Terminal DONE and actual executed-unit counter both report 20,000; coverage 103 and features 181 |
| Corpus | 19 initial and 74 final files; every declared corpus hash verified |
| Independent negative oracle | Original and minimized inputs returned expected exit 77; minimizer and corrected replay returned 0 |
| Oracle size | Original 61 bytes; minimized 61 bytes; no size reduction claimed |
| Managed negative children | JIT/AOT quarantine exit 43 and stale-cookie exit 42 with required markers |
| Fatal children | Invalid-pointer and wrong-owner release each returned expected exit 1 with ASan diagnostics |

Seven archived outputs were independently hashed: two AOT executables, three
C fuzz/fatal binaries and two oracle inputs. The original result lists 19
artifact identities; 12 are outside the ZIP and are not claimed independently
rehashed by this inspection. No unexpected-failure files were present.

## Boundaries and independent inspection

Sanitizer instrumentation covers the C serialized-input decoder, independent
C oracles and C fatal driver. The stable Rust libraries, CLR and Native AOT
runtime are explicitly uninstrumented. CI used .NET 11.0.100, Rust 1.100.0 and
Ubuntu Clang 18.1.3; the measurement host's fixed Clang 19 and workload settings
remain separate. No sanitizer was disabled to avoid a local failure.

The existing strict projection method was reused with the actual new source,
artifact and run identities. Its CPU8 execution exited 0 in 0.169020581 seconds,
without running any test or workload. A separate reviewer compared the CI123
and CI124 inspection sources: changes are limited to identities, locations and
the descriptive prior-version field. The reviewer also rehashed both complete
CI124 ZIPs and checked summary/source/receipt bindings. No gate was weakened
and the inspectors were not rerun.

This published projection contains fixed roles, numbers, booleans and hashes.
Raw commands, logs, host paths, process identifiers and operational controls are
excluded. The separate [canonical report](../ci124-canonical-001/README.md)
records the remainder of CI124. The local B18 cancellation timeout, candidate
retention decision, capacity and final-after long tests remain separate and
unresolved by this CI result.
