# Perf-01 CI122 A20 ownership and sanitizer verification

This report is the actual A20 functional gate for source head
`ada13b865ec5d19876745498f6f51d8ad2367399`, including the native Host shutdown
correction. It grants no local performance or 30-minute measurement credit.
At this report's preparation, the separate canonical build job was still
running; this report does not infer the whole workflow's conclusion.

## Source and artifact identity

[A20 job 136083168197](https://github.com/IzuSharp/NativeWeave/actions/runs/44674553861/job/136083168197)
in normal pull-request CI122, attempt1, completed successfully. Its actual
checkout is `34ed067343298abfb78947f750730f7efb29c101`. Independent GitHub
commit reads confirmed that checkout and product head have the same tree:
`0d1b1ca390b582b1f2ebf004f7778c8f084a68a4`. The checkout's parents are the
frozen main and the reported product head. The A20 source-commit log agrees;
source status is empty and the completed harness reports source unchanged.

| Artifact field | Actual observation |
| --- | --- |
| [GitHub artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44674553861/artifacts/14602355702) | 14602355702 |
| Complete ZIP bytes | 9,642,395 |
| Complete ZIP SHA-256 | `6690ca88d18e3727c2bed9e178e915458f8047bc5e7484352ff630a111adb522` |
| ZIP member count | 202 |
| Result JSON bytes | 72,617 |
| Result JSON SHA-256 | `877bbad7c77a3a31cbd4679394352d2d91e320ab143b503f1cd9937b3139a0a9` |
| Retention expiration | 2026-12-04 04:29:36 UTC |

The complete ZIP was fetched through the normal GitHub artifact connector.
Its actual byte count and SHA-256 match GitHub metadata. Named members were
read directly from the ZIP without full extraction. The owner retains the
complete downloaded archive, source/API identity reads, job log and actual
local projection receipt. GitHub artifact access after the expiration above
is not promised. This repository records the strict scalar summary and its
manifest, without copying raw commands, logs, process identifiers, host paths
or control records.

## Actual gate results

The original A20 harness ran from 2026-11-20 04:28:09 UTC through 04:29:36 UTC.
It reports passed, preparation-only false, source-dirty false and
source-unchanged true. All 48 commands have their expected actual exit codes
and no timeouts; all 96 named stdout/stderr hashes were independently verified
against their ZIP bytes. The summary retains each fixed command role and its
actual expected outcome, including deliberate nonzero negative children.

| Scope | Actual evidence |
| --- | --- |
| Managed ownership/races | JIT and Native AOT each passed 8,925 assertions and 72 finite orders |
| Maintainer samples | JIT and Native AOT each passed basic2 and advanced886 checks |
| Sanitizers | Address, undefined-behavior and leaks enabled; original `detect_leaks=1:halt_on_error=1` and undefined-behavior halt/stacktrace options checked |
| Fuzz | Actual terminal DONE and executed-unit counter both report 20,000; coverage105/features184 |
| Corpus | 19 initial and 74 final corpus members; every declared corpus SHA-256 verified |
| Independent negative oracle | Original and minimized inputs both exited77 with the expected assertion; minimizer and corrected replay exited0 |
| Oracle size | Original61 bytes, minimized61 bytes; no reduction claimed |
| Managed negative children | JIT/AOT quarantine43 and stale-cookie42 with required protocol markers |
| Fatal children | Invalid-pointer and wrong-owner release each exited1 with the expected ASan SEGV/double-free diagnostics |

Seven archived outputs were independently byte-hashed: the two AOT
executables, three C fuzz/fatal binaries and two oracle files. The result lists
19 artifact identities in total; 12 are outside the ZIP and are not claimed
as independently rehashed by this inspection. The harness's own successful
execution and inventory remain preserved. No unexpected-failure files were
present.

## Scope boundaries

Sanitizer instrumentation covers the C serialized-input decoder, independent
C oracles and C fatal driver. The stable Rust libraries, CLR and Native AOT
runtime are explicitly reported uninstrumented. This is the existing A20
contract, not blanket sanitizer coverage of all code.

The actual functional CI tools were .NET11.0.100, Rust1.100.0 and Ubuntu
Clang18.1.3. The pinned measurement-host Clang19 and performance configuration
remain separate. No sanitizer was disabled to avoid the earlier local LSan
ptrace limitation. This new actual CI result is not a rewrite of that retained
local failure or of earlier CI120/CI121 records.

The offline projection reused the previous strict named-member verification
method with the new actual source and artifact identities. It exited0 without
rerunning tests or modifying the artifact. The whole CI's canonical/pristine
checks and the local B17/B19/B15/B18 regressions are separate records.
