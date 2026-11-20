# Perf-01 retained-runtime gates: A08 and two A20 attempts

This is a numerical and checklist projection of three actual local gate results
for product commit `bf0755977b16d049ee35a192f456779ce74c3767`, Linux x64.
**A08 passed. Both A20 attempts failed; A20 remains unaccepted.** No CI outcome,
whole-product acceptance or performance improvement is asserted here. Later
regression gates are outside this snapshot.

The accompanying [public summary](public-summary.json) contains only fixed
fields, numeric/Boolean/null values, enumerated states, UTC timestamps and hashes.
No raw logs, source code, commands, host paths or private process/control metadata
are included. The [projection receipt](projection-execution.json) binds 21 actual
small inputs and 71 passed extraction checks. This extraction performed no
build, test or load and replayed no large raw evidence.

## Actual outer results

Elapsed times below are the recorded outer monotonic durations of the gate
processes, including their preparation/build/test work. They are not application
performance measurements.

| Gate | Attempt | Actual start UTC | Actual end UTC | Elapsed seconds | Outer exit | Recorded result |
| --- | ---: | --- | --- | ---: | ---: | --- |
| A08 | 1 | 2026-11-20 03:12:05.857182 | 2026-11-20 03:13:03.661844 | 57.804548115 | 0 | Passed |
| A20 | 1 | 2026-11-20 03:13:03.663975 | 2026-11-20 03:14:05.964932 | 62.300842263 | 1 | Failed at fuzz link |
| A20 | 2 | 2026-11-20 03:26:27.201005 | 2026-11-20 03:27:25.094318 | 57.893210490 | 1 | Failed at fuzz execution / LSan environment check |

| Gate / attempt | Recorded commands | Exit zero | Expected nonzero | Unexpected exit | Reported command timeouts |
| --- | ---: | ---: | ---: | ---: | ---: |
| A08 / 1 | 34 | 34 | 0 | 0 | 0 |
| A20 / 1 | 37 | 32 | 4 | 1 | 0 |
| A20 / 2 | 40 | 35 | 4 | 1 | 0 |

Each A20 attempt contains two JIT/Native AOT quarantine-child exits of 43 and
two JIT/Native AOT stale-cookie-child exits of 42. These exactly match the
expected exits recorded by the original verifier. They are deliberate negative
cases, not the unexpected failure. An intentionally quarantined child is not
reported as acknowledged retirement.

## A08 completed evidence

The result records 18 native tests passed, zero failed and zero ignored. Managed
JIT and Native AOT recorded 489 and 490 assertions respectively. Each mode
reported all 47 jobs, 47 engines and 47 close owners released, zero live jobs,
zero bad releases, and successful actual worker joins. Each sample returned the
native result 12, observed two workers joined and zero outstanding bytes; its
canceled close waiter retained ownership until cleanup completed.

All 34 recorded commands exited zero, including the actual JIT/AOT executions,
Core-only consumers, sample executions and compiled API/XML reference check.
The verifier records a clean source at entry and unchanged source at completion.
Its finite configured bounds are 64 native close/permit races, 32 managed
close/start races and eight repeated canceled-close waits. These are bounded
checks, not an exhaustive concurrency proof.

## A20 preserved failures and completed subsets

Both attempts completed the managed property/race suites: JIT and Native AOT
each reported 8,925 assertions and 72 finite orders. In each execution mode,
the minimum and advanced samples reported two and 886 checks. These completed
subsets remain useful evidence without replacing the failed enclosing gate.
Both attempts report clean source at entry. Neither failed result records the
final source-unchanged check; the public field remains null rather than inferred.

Attempt 1 failed to link the fuzz executable because three required sanitizer
runtime libraries were unavailable: the fuzzer, ASan static and ASan runtimes.
Its fuzz-build exit was 1. There is no fuzz execution command in that attempt's
completed command record. Its failed result and outer receipt are preserved.

Attempt 2 successfully linked the fuzz, negative-oracle and fatal-driver
executables. The normal fuzz process reported 20,000 executed units, 145 new
units, a final corpus of 57 units / 1,459 bytes and peak RSS of 38 in the fuzzer's
reported MB unit. It subsequently emitted a LeakSanitizer fatal diagnostic,
including the runtime's unsupported-ptrace explanation, and exited 1. This is
an environmental failure classification based on the actual diagnostic, not an
independent determination of the tracing component. The run does not establish
either a leak-free result or a product leak. The reported unit count and coarse
fuzzer timing do not supply a performance result or a passed sanitizer gate.

ASan, UBSan and leak detection were enabled in the A20 configuration. Their
instrumented scope is the C serialized-input decoder, independent C oracles and
C fatal driver; stable Rust libraries, CLR and Native AOT runtime are outside
that instrumentation. No full-FFI sanitizer claim is made. Subsequent gate
completion, including the negative/fatal checks, cannot be inferred from an
executable having built or from a future CI result not yet inspected.

## Bound evidence and credit

| Actual receipt | SHA-256 |
| --- | --- |
| A08 result | `ef7f809148c182c35b2bb14c03637c6c955cf787d100c3f681cfdf019c2ec667` |
| A20 attempt 1 result | `88c2e554bd5127483c24546dcddd444034969d8297bb729ea724129dc34794c4` |
| First outer execution, containing A08 and A20 attempt 1 | `ce70ca749199ca7f52f39fbaaac6c73ec6b8001d3d74bcc67c82a9af18b7d7ce` |
| A20 attempt 2 result | `7f4a80d87daebf0be634ed08225a498036bb77f5ff14c61ee58645aba437bb67` |
| Second outer execution | `2f05edb26502df762c67ecff0ef6dfbbffac6b7f2607dc10090fdbd212f3164b` |

The public input-hash inventory also binds the consumed test/sample summaries
and the second fuzz diagnostic. Original detailed receipts and logs remain
preserved separately by the integration owner. This projection grants zero
formal-comparison credit and zero long-duration credit; it does not alter any
original gate outcome or authorize retrying a failed gate until it passes.
