# Perf-01 CI123 A20 ownership and sanitizer verification

This report is the actual A20 functional gate for source head
`0715ffb6376b1ae08259ad7e2cb30ff0320d83e7`, including removal of the extra post-result retirement retry and the retained
native Host shutdown correction. It grants no local performance or 30-minute
measurement credit. The complete CI123 workflow, including its aggregate Verify
job, completed successfully at 2026-11-20 07:14:28 UTC. Its separate canonical
archive audit is recorded in the adjacent `ci123-canonical-001` report.

## Source and artifact identity

[A20 job 136136417002](https://github.com/IzuSharp/NativeWeave/actions/runs/44690977311/job/136136417002)
in normal pull-request CI123, attempt1, completed successfully. Its actual
checkout is `36a10cb612d06edc0298596a843b7a4dc66b258a`. Independent GitHub
commit reads confirmed that checkout and product head have the same tree:
`cd0a6022e0115c22f133aedf6c801d9244640523`. The checkout's parents are the
frozen main and the reported product head. The A20 source-commit log agrees;
source status is empty and the completed harness reports source unchanged.

| Artifact field | Actual observation |
| --- | --- |
| [GitHub artifact](https://github.com/IzuSharp/NativeWeave/actions/runs/44690977311/artifacts/14608019637) | 14608019637 |
| Complete ZIP bytes | 9,642,211 |
| Complete ZIP SHA-256 | `d0a6e65f4e71bf6b2522b99b6a5650c19f0290fa0f245309e72054445deee0ac` |
| ZIP member count | 201 |
| Result JSON bytes | 72,500 |
| Result JSON SHA-256 | `0887967dc41a72ae313e159ad630de1d494c7bf0f5ccbcb852af07604a661e21` |
| Retention expiration | 2026-12-04 06:55:08 UTC |

The complete ZIP was fetched through the normal GitHub artifact connector.
Its actual byte count and SHA-256 match GitHub metadata. Named members were
read directly from the ZIP without full extraction. The owner retains the
complete downloaded archive, source/API identity reads, job log and actual
local projection receipt. GitHub artifact access after the expiration above
is not promised. This repository records the strict scalar summary and its
manifest, without copying raw commands, logs, process identifiers, host paths
or control records.

## Actual gate results

The original A20 harness ran from 2026-11-20 06:54:00 UTC through 06:55:08 UTC.
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
| Fuzz | Actual terminal DONE and executed-unit counter both report 20,000; coverage105/features179 |
| Corpus | 19 initial and 73 final corpus members; every declared corpus SHA-256 verified |
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
local failure or of earlier CI120/CI121/CI122 records.

The offline projection reused the previous strict named-member verification
method with the new actual source and artifact identities. It exited0 without
rerunning tests or modifying the artifact. The whole CI's canonical/pristine
checks and the local B17/B19/B15/B18 regressions are separate records.

An independent reviewer compared this inspection source with the preceding
CI122 method and checked the new small summary bindings. No verification gate
was weakened; changes were confined to exact identities and output locations.
That review did not rerun the inspectors or rehash the archives. The actual
full-byte and named-member audit execution is recorded separately above.
