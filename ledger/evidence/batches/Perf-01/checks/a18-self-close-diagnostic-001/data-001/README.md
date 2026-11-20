# Perf-01 A18 self-close assertion: fixed baseline/candidate diagnostic

The unchanged original A18 test reproduced the same self-close assertion failure
on both the baseline and retained-runtime candidate. Each side completed one of
three fresh processes and failed two at the original assertion. This establishes
that the assertion failure also exists on the baseline; it does not establish
R2 causality or estimate a failure probability. The original failed A18 gate is
preserved and remains failed in this record.

The [public summary](public-summary.json) contains only fixed fields,
numeric/Boolean/null values, enumerated labels, UTC and hashes. The
[projection receipt](projection-execution.json) records 48 passed extraction and
source-identity checks. No commands, host paths, raw logs or private control
metadata are published. This projection itself performed no build or test.

## Actual fixed six-process execution

The owner selected three processes per variant in advance, interleaving the
variants and reversing the middle repetition. No failed process was replaced.
The complete diagnostic ran from 2026-11-20 03:53:13.843219 UTC to
03:53:31.743859 UTC, including the baseline locked restore and build. The latter
two recorded preparation commands both exited zero. All six tests used the
original full JIT test source, not a modified or isolated self-close assertion.

| Execution sequence | Repetition | Variant | Actual exit | Original self-close assertion | Full-test summary |
| --- | ---: | --- | ---: | --- | --- |
| 1 | 0 | Baseline | 0 | Absent | 127 checks, 12 races, zero live resources |
| 2 | 0 | Candidate | -6 | Present | Not completed |
| 3 | 1 | Candidate | -6 | Present | Not completed |
| 4 | 1 | Baseline | -6 | Present | Not completed |
| 5 | 2 | Baseline | -6 | Present | Not completed |
| 6 | 2 | Candidate | 0 | Absent | 127 checks, 12 races, zero live resources |

All four failures have the original expected-canceled/closed-operation assertion
at the same self-close case. Failed processes have no complete resource-zero
claim. The two successful full-test summaries report actual native HTTP and JIT;
this diagnostic did not perform Native AOT or package-consumption acceptance.
The recorded per-process durations are diagnostic execution durations, not
comparable application latency or throughput measurements.

| Bound identity | Value |
| --- | --- |
| Baseline source commit | `ea5fa528035d025bd7a28698ee7c71194432236c` |
| Candidate source commit | `7b588c48e2898d93423ff278814370cdd7b49030` |
| Original full test source SHA-256, equal on both | `230b0affcfb74ff5629e81f2ddd7a0c430b162e4328faf37c6b48bcb778f125e` |
| Common native asset SHA-256, recorded by execution | `547167f19edcfc21b98cf42f364f604e5694cd230025c30f7ed6517067b00062` |
| Diagnostic execution receipt SHA-256 | `c50d5a5c411b0eefcb1224666ca56f474c965769b1ed698bd7243e1957fdfc09` |
| Original failed gate result SHA-256 | `864a7ae1314f4c45b633cf15b757de11c26495b9f4ca3d220648aa386cd0ca0a` |

The summary separately retains each variant's actual test/Core DLL hashes.
Equal test source does not mean equal compiled assemblies. The shared native
asset was intentional: the A18 native engine source was unchanged. The baseline
was built against that actual asset rather than recompiling an alternative
native implementation for this diagnostic.

## Source-supported ordering and narrow correction

Independent source comparison found byte-identical baseline/candidate versions
of the original A18 test, managed HTTP proof host, A06 callback registration and
coordinator, native HTTP engine/exports, and documented async-proof contract.
Their exact hashes are in the public summary. The existing contract permits a
committed successful native result to win a cooperative cancellation race.

The source permits this ordering: self-close first marks managed admission
closed and queues A06 cleanup; the handler-scope check then rejects waiting for
its own retirement. The handler catches that rejection and returns its response.
The handler reply can reach native response publication before the queued native
stop. Native response registration and native close share an admission gate,
so publication before native close is a legal winner. This is a source-supported
ordering, not an instrumented schedule trace from the six diagnostic processes.

The retained R2 change requests at most one additional queued A07 retirement poll
only after result processing. It does not alter the native terminal outcome or
the A06 self-wait rule. These facts and the baseline reproduction support fixing
the local test assumption; they do not waive separate ownership/concurrency
regression gates or prove that scheduling frequencies are identical.

The proposed test-only correction is commit
`f5ff2101614cc059d0369cb4924b43c7f584853a`, with changed test source SHA-256
`c3f0888acdad662318b3ccc5d80aabf584a0c76eb7611590170e4d8537a6dab8`.
It changes only the existing self-close case. A local catch surrounds only the
Get wait and allows the documented cancellation or native HTTP-domain failure.
A successful response must have status 200. The independent self-wait-rejected
assertion remains. A finally block disposes any returned response, awaits actual
host close and checks all resources zero, including when the local assertions
fail. Other cases and the shared canceled-or-transport helper are unchanged.

No retry loop, timing delay, barrier or production change is introduced. All
production and documentation files remain unchanged by this test commit. The
source patch was whitespace-checked but was not executed by its author. Full
A18 JIT, Native AOT and package validation after integration remain the owner's
next gate; no passing outcome for that corrected gate is claimed here.

This record grants zero formal comparison and long-duration credit. It neither
overwrites the original failed gate nor counts the fixed diagnostic as repeated
gate attempts until success.
