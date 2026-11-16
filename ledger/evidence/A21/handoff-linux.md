# A21 Linux x64 handoff

## Status and scope

Completed and independently accepted for the Task-01 Linux component scope. Final implementation commit: `1918c9a10929bf64e4066463d32fcac9eabf2499` on `task/Task-01-A21-linux`. The controller and runtime fixtures were accepted at `c64a62c9cba651478b69472f7be333f971431e38`; the final delta only separates ordinary/AOT dependency locks and updates build documentation/verification. The exact mapping is in `final-source-binding.json` and `review-linux/A21-split-lock-review.json`.

Owner: Task-01 root. Worktree: `ROOT/.worktree/Task-01-A21-linux/NativeWeave`. Independent runtime review: A01 agent; supplemental lock review: A19 agent. Start/acceptance dependencies are empty in the pinned Plan graph.

## Delivered

- External open-loop controller with observer-clock scheduled, dispatched, admitted and completed timestamps; explicit generator saturation; finite histograms and tail-support checks; single correction policy; complete error/rejection/timeout/cancellation accounting and lossless raw events.
- Versioned counter inventory with units, availability and observation methods. Unknown is null, never zero. Linux procfs observations retain their actual scope; queue/credit limits are not whole-process memory bounds.
- Independent-process repetitions and a noise-floor-aware comparison helper, with comparison disabled for the scalar smoke fixture because no reviewed domain baseline exists.
- Executable direct Rust, C# NativeAOT plus Rust, and C# NativeAOT scalar comparator fixtures; compiled internal-only API inventory and XML output. Documentation covers minimal/advanced use, expected-value oracle datasets, cancellation/cleanup and evidence interpretation.

## Actual verification

`attempt-003/result.json` is the immutable successful full run: 24 successful commands, 19 focused regressions, actual JIT and NativeAOT execution, two repetitions of each of three routes, 600 requests, 1200 exact raw events. Both managed native executables report dynamic code unavailable. The independent reviewer checked 14 original source files, 50 artifacts, 34 pinned Design inputs and all raw counter/event rows. Compiler-driver and actual BFD linker identities, hashes and emitted Rust/AOT link arguments are recorded separately.

`lock-hygiene/result.json` records six ordinary -> AOT -> ordinary locked restores with stable four-lock hashes. The final 16-file source binding and exact tested AOT-lock byte relocation are explicit. No additional runtime execution is claimed for this build-only delta.

## Findings and failed attempts

All four original independent findings are resolved: malformed event preservation, lossless per-operation counters, a throughput denominator consistent with late completion timestamps, and exact linker provenance. The same independent reproductions pass; their raw cells and prior findings remain in `review-linux/`. Development attempts and the initial split-lock condition failure remain recorded. `archive-policy.json` lists copied text evidence and omitted artifacts; no failed run has been relabeled successful.

## Boundaries and integration

This validates the benchmark controller and three-route scalar adapter, not Database/ORM/Server superiority or a production memory benefit. Final domain workloads and baseline claims remain B23/B22 work. No public application API or product package dependency is introduced by this tooling. Final pristine package/release obligations remain with A16/B24. Windows and other platforms were not executed.

Pinned tools: .NET SDK 11.0.100, Rust 1.100.0, Linux x64, x86-64-v2 fixture profile. Offline local Microsoft SDK packages were used; vulnerability-data refresh was unavailable locally, not reported as passed. Existing repository CI policy is unchanged.

All implementation and supplemental commits are integrated in the Task-01 batch. See `../batches/Task-01/handoff-linux.md` for shared verification, publication mappings and both PRs. No A21 implementation step remains.
