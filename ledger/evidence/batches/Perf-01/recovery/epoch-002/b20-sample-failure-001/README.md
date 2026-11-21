# Perf-01 epoch-002: B20 explicit-local sample failure

The selected-native regression sequence stopped at its **26th of 29 outer
commands**. The first **25 outer commands completed with exit 0 and retired**;
the Debug diagnostics sample with `--local` failed with **exit -6 and retired**.
The remaining three commands were not run. This is incomplete functional
validation, with **0/10 accepted current-epoch 30-minute before/after runs** and
no performance credit.

## Executed facts

| Observation | Result |
|---|---|
| Selected product | `ccff42c0df4141984ef9de497af7cd768753704a` |
| Selected native asset SHA-256 | `1f023b7506bde3f8c4a13b12de92e3e9503004ca3afc2d41a53bec17e44f1d97` |
| Sequence start / end, UTC | `2026-11-21T03:10:51.975911+00:00` / `2026-11-21T03:20:20.938829+00:00` |
| Failed command start / end, UTC | `2026-11-21T03:20:20.627964+00:00` / `2026-11-21T03:20:20.936688+00:00` |
| Failed command | `dotnet samples/api/server-diagnostics/bin/Debug/net11.0/server-diagnostics.dll --local` |
| Process outcome | `failed`, exit `-6`, `retired=true`; no remaining owned processes or owner children recorded |
| Failure reported on stderr | `InvalidOperationException: Explicit diagnostic listener did not run.` at `samples/api/server-diagnostics/Program.cs`, line 42 |
| Failed sample stdout | Four `application_failure` events for `/failure`, HTTP/1.1, `5xx`; one additional event for `/hello/{name}`, HTTP/1.1, `2xx` |
| Earlier B20 fixture markers | Debug defaults: **5 assertions**, `dynamic=True`; Release JIT: **110 assertions**, `dynamic=True` |
| Earlier sample without `--local` | Exit 0; printed `activities=0; measurements=0` |
| Not run | `b20-publish-aot`, `b20-actual-aot`, `b20-package-consumer` |

The 25 successful outer commands include builds, restores and checks; this
number is not a test-assertion count or a claim that the full regression
sequence passed. The failed sample did not print its final counters.
Its actual `activities`, `measurements` and `warnings.Count` values are
**unavailable**. The four-plus-one figures above count observed log events,
not printed internal counters.

## Source-based inference

At the selected commit, the sample checks each of 16 response status codes,
then requires completed close, zero pending requests and zero retained native
and managed bytes. It awaits disposal before the diagnostic assertion at line
42. Reaching that assertion therefore implies that those earlier operations
returned and their guards did not throw. These are **control-flow inferences**;
the failed sample did not separately print close results, owner snapshots,
response contents or a numeric business-operation tally.

## Unconfirmed cause

Source inspection found a plausible runtime-lifetime race. A fixed-length
response can reach the client before its managed completion continuation
submits native Finish. Immediate close can drain Hyper connections and
acceptors, allowing the Rust runtime to exit first. A later native operation
can then receive `NW_INVALID_STATE`, which the managed adapter maps to
`InvalidOperationException` and diagnostics categorizes as
`application_failure`, even with already committed 2xx headers.

The essential runtime-lifetime, acceptor-drain, operation-scheduling and Finish
function bodies are also present unchanged in the frozen EA5 baseline
`ea5fa528035d025bd7a28698ee7c71194432236c`. The sample, diagnostic implementation
and existing B20 fixture are unchanged too. This establishes a source-side
candidate; **it does not prove the exception behind the observed 2xx event,
baseline reproducibility, or whether the candidate changes its frequency**.
The captured stack belongs to the final sample assertion, not to the earlier
server-side exception. A controlled close-before-Finish probe and capture of
that exception remain necessary. The original failure remains a failure.

## Evidence and scope

[checklist.json](checklist.json) contains numerical results, all 29 outer-command
outcomes, receipt/stdout/stderr SHA-256 values, exact source identities and
source-file hashes. Evidence filenames are relative to the preserved
`server-regressions-002` output bundle; source filenames are relative to their
named repository. Original receipts and logs are hash references, not copied
here. Their environment and machine-path fields are intentionally absent from
this public summary. The selected asset hash is an input/inventory binding,
not a new claim from a loaded-module process trace.

This directory records existing execution and a read-only source review.
Creating it ran no build, test or load and does not add acceptance credit.
