# Perf-01 CI127 A20 ownership and sanitizer evidence

This is finite A20 evidence for retained public head
`2e3995df8d86583ee9443348276ca8d918056bfc`, after the three-file scratch
forward revert. Both ownership corrections remain. This report grants **zero
performance, capacity or 30-minute measurement credit**. Actual local module
gates and final003 producing/measurement receipts retain their own identities.

## Exact source and archive

[A20 job 136319599499](https://github.com/IzuSharp/NativeWeave/actions/runs/44745493272/job/136319599499)
in CI127 attempt 1 succeeded. Its actual checkout is
`d4a51f16c8154ee026a8fe0e1975f7ce087d90d5`, as reported by the archived
source-commit log. Raw GitHub commit reads establish that checkout and retained
public head have exact tree `246de1eb9368efbc62f46ce10c4a8a894d646152`.
Checkout parents are frozen main `ea5fa528035d025bd7a28698ee7c71194432236c`
and the public head. Source status is empty and the harness reports unchanged
source. Matching trees do not rename the actual producing commit.

| Field | Actual observation |
| --- | --- |
| [A20 artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44745493272/artifacts/14632577815) | 14632577815 |
| Complete ZIP bytes | 9,644,537 |
| Complete ZIP SHA-256 | `0fcb0b5152bab400316c6e33490946ca8a1bf1b31c39446016282daee1bcdf4e` |
| ZIP members | 208 |
| Result JSON bytes / SHA-256 | 73,310 / `0f3b474ae8d241ca321b35b4419e0c7b7c2d6505fd59032ce042b0f6ddf479b2` |
| GitHub expiration | 2026-12-04 13:35:56 UTC |

The complete downloaded ZIP's size and digest match GitHub metadata. Named
members were read directly without full extraction. Complete archives and private
inspection/identity receipts remain retained. Availability beyond the stated
expiration is not promised; small repository records remain retrievable while
repository history is retained.

## Actual execution

The original harness ran from **2026-11-20 13:34:51 through 13:35:56 UTC**.
Preparation-only and source-dirty are false; source-unchanged is true. All 48
commands returned their expected actual exit codes without timeout. All 96
stdout/stderr hashes were checked against archived bytes. Deliberate nonzero
negative outcomes remain explicit in the numeric checklist.

| Scope | Actual evidence |
| --- | --- |
| Managed ownership and races | JIT and Native AOT each passed 8,925 assertions and 72 finite orders |
| Maintainer samples | Each mode passed basic 2 and advanced 886 checks |
| Sanitizers | Address, undefined-behavior and leak checking enabled; original halt and stacktrace options verified |
| Fuzz | Terminal DONE and executed-unit counter both report 20,000; coverage 106, features 183 |
| Corpus | 19 initial and 80 final files; all declared corpus hashes verified |
| Independent negative oracle | Original/minimized inputs returned expected exit 77; minimizer and corrected replay returned 0 |
| Oracle size | Original 61 bytes and minimized 61 bytes; no reduction claimed |
| Managed negative children | JIT/AOT quarantine exit 43 and stale-cookie exit 42 with required markers |
| Fatal children | Invalid-pointer and wrong-owner release each returned expected exit 1 with ASan diagnostics |

Seven archived outputs were independently hashed: two AOT executables, three
C fuzz/fatal binaries and two oracle inputs. The original result lists 19
artifact identities; 12 are outside the ZIP and are not independently rehashed.
No unexpected-failure files were present. These coverage/corpus observations
come from CI127; no earlier CI values were substituted.

## Inspection method and limits

The strict CI126 inspector was reused with only actual source, artifact, run,
job and location substitutions. The CPU-8 offline invocation completed with
exit 0. Its source, invocation, projection and original download/identity
receipts are hash-bound by the manifest. No CI command, product test, native
code load or workload was replayed locally. Earlier CI records were unchanged.

Sanitizer instrumentation covers the C serialized-input decoder, independent
C oracles and C fatal driver. Stable Rust libraries, CLR and the Native AOT
runtime remain explicitly uninstrumented. CI used .NET 11.0.100, Rust 1.100.0
and Clang 18.1.3. Those CI tools/binaries are separate from the measurement host's
fixed Clang 19 and actual local domain packages.

All seven CI127 jobs subsequently completed successfully at 13:52:21 UTC;
the [canonical/package report](../ci127-canonical-001/README.md) records that
separate scope. This A20 result does not cover every dedicated module suite,
validate later source changes, replace a failed local gate or accept the final
application's performance. Published data contains fixed roles, numbers,
booleans and hashes; raw commands, logs, host paths, process identifiers and
operational control records are excluded.
