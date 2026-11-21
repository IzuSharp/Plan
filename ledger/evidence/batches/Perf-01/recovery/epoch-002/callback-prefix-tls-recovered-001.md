# Perf-01: recovered occupied-prefix gRPC TLS diagnostic

The occupied-prefix candidate reduced observed server CPU and post-recovery idle-bracket CPU in these completed short diagnostics. It did not improve every RPC tail: client-stream and duplex p99 were higher in all three corresponding repetitions. This evidence does not select a final candidate or grant formal, capacity, or long-run credit.

## Tested scope and identity

- Actual current source: `a5748ad4e03825e3da7706d074887952da6c2d43`.
- Actual candidate source: `092e5e2c74d7419772f2455a2922ae4238f389de`.
- Shared original driver: `2e3995df8d86583ee9443348276ca8d918056bfc`; native source: `2f40348c3db80a4fbee7a99e721b374a597b16df`.
- Actual loaded Server native SHA-256 for all twelve cells: `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0`.
- Independent original before002 client SHA-256: `ae59038f6d83b0cdc60677f5d65f50f06298b53a168bee65f73a6599d7832f8e`; both cohorts reuse this client.
- Published source snapshots are not substituted for the actual tested commits. The current cohort is an experimental predecessor, not the fixed original-main baseline.
- Outer execution: 2026-11-21T11:13:35.890088+00:00 to 2026-11-21T11:20:53.711270+00:00; 37/37 commands exited zero and retired with no live owned children or cleanup signals.
- Twelve independent processes: unary and mixed streams, each current/candidate in AB/BA/AB order. Every process used concurrency 4, 16 planned calls/s and 20 requested seconds; generator CPUs 0–1 and service CPUs 2–3.
- Unary covers 64 B and 65,536 B messages. The stream mix covers server, client and duplex RPCs, each configured for 32 messages of 4,096 B. Real HTTP/2 + TLS, Native AOT, original content/status checks and identity-only compression apply.
- Every cell completed 323/323 business calls, zero unexpected outcomes or correctness failures, and 32/32 recovery calls. Total measured business calls: 3,876. Intentional deadline/cancellation probes: zero in these profiles; the distinct candidate B18 prerequisite passed.
- The original requested-duration schedule contains 323 arrivals spanning 20.125 scheduled seconds. Actual elapsed and dispatch spans are retained per process. None meets a 30-minute duration gate.

## Whole-profile resources

CPU, allocation and RSS below cover the entire mixed profile. CPU seconds and allocation are means of three processes; RSS is the maximum of their measured-window peaks. The JSON also retains each process, all observed process roles, and the mean of the process RSS peaks. GC/allocation cover the original measurement-phase observations.

| Profile | Server CPU s, current → candidate | CPU change | Peak RSS MiB, current → candidate | Allocation MiB, current → candidate | Idle-bracket one-core CPU %, current → candidate |
|---|---:|---:|---:|---:|---:|
| unary | 1.110000 → 0.940000 | -15.315% | 71.347656 → 71.605469 | 188.157074 → 188.156865 | 4.063422 → 3.331294 |
| streams | 1.706667 → 1.606667 | -5.859% | 68.824219 → 69.183594 | 187.827484 → 186.812584 | 4.064428 → 3.464197 |

Idle CPU is derived from the existing post-recovery and after-idle process snapshots, using their actual elapsed time and CPU ticks. Those snapshots bracket approximately five seconds and include transition/diagnostic work; final server stop/disposal occurs later. Counters have 100 ticks/s resolution. This is not an isolated timer-cost measurement or a statistical claim. Candidate peak RSS was slightly higher in both profiles.

## Per-mode latency and success throughput

Percentiles are arithmetic means of the three original process percentiles, not pooled percentiles. Exact mean latency is **N/A** because it is absent from these completed result metadata; no estimate is reconstructed from histogram bins. All changes are `(candidate − current) / current`, without a new noise decision. Per-mode successful calls/s are contributions to the shared mix window, not standalone capacity.

| Mode | p50 ms, current → candidate | p95 ms, current → candidate | p99 ms, current → candidate | p99 change | Successful calls/s, current → candidate |
|---|---:|---:|---:|---:|---:|
| grpc-unary/http2-tls/64 | 2.684486 → 2.565355 | 13.904458 → 14.627622 | 31.540640 → 28.718731 | -8.947% | 8.048455 → 8.046594 |
| grpc-unary/http2-tls/65536 | 3.693274 → 3.501192 | 15.283158 → 15.736007 | 35.742059 → 29.716292 | -16.859% | 7.998773 → 7.996924 |
| grpc-client/http2-tls | 7.603394 → 8.559400 | 34.156835 → 48.673386 | 64.938533 → 86.357006 | +32.983% | 5.315510 → 5.306590 |
| grpc-duplex/http2-tls | 16.145431 → 19.569771 | 69.955151 → 82.331151 | 113.041587 → 140.614188 | +24.392% | 5.365188 → 5.356184 |
| grpc-server/http2-tls | 9.800835 → 11.876864 | 87.088978 → 70.194240 | 168.513936 → 163.345377 | -3.067% | 5.365188 → 5.356184 |

The stream-mode adverse observations remain explicit:

| Mode | Repetition 0 p99 ms, current → candidate | Repetition 1 | Repetition 2 |
|---|---:|---:|---:|
| grpc-client/http2-tls | 64.041184 → 86.587154 | 47.592577 → 87.824761 | 83.181837 → 84.659102 |
| grpc-duplex/http2-tls | 114.478637 → 142.269590 | 133.112574 → 166.946931 | 91.533549 → 112.626044 |
| grpc-server/http2-tls | 94.642196 → 203.732176 | 199.892369 → 146.651109 | 211.007242 → 139.652845 |

Client-stream and duplex p99 increased in all three pairs. Server-stream mean-of-process p99 decreased slightly, but the first pair increased substantially; all three candidate server-stream medians were higher. Mixed-profile p99 fell, which does not remove these conditional regressions. Three short repetitions provide descriptive observations, not a new significance test or evidence of a unique cause.

## Per-process resource and drain observations

| Cell | Server CPU s | Server peak RSS MiB | Allocated MiB | Mixed p99 ms | Idle CPU % of one core | Successes | Recovery | Close |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| unary-0-current | 1.15 | 70.875000 | 188.111504 | 40.490402 | 4.193674 | 323/323 | 32/32 | Completed / Disposed |
| unary-0-candidate | 0.88 | 71.410156 | 188.166519 | 18.164117 | 3.797838 | 323/323 | 32/32 | Completed / Disposed |
| unary-1-candidate | 1.03 | 71.320312 | 188.139107 | 34.770467 | 3.198048 | 323/323 | 32/32 | Completed / Disposed |
| unary-1-current | 1.04 | 70.808594 | 188.193924 | 18.118904 | 3.998464 | 323/323 | 32/32 | Completed / Disposed |
| unary-2-current | 1.14 | 71.347656 | 188.165794 | 36.976681 | 3.998129 | 323/323 | 32/32 | Completed / Disposed |
| unary-2-candidate | 0.91 | 71.605469 | 188.164970 | 29.808355 | 2.997997 | 323/323 | 32/32 | Completed / Disposed |
| streams-0-current | 1.68 | 68.398438 | 186.683372 | 97.603529 | 4.198002 | 323/323 | 32/32 | Completed / Disposed |
| streams-0-candidate | 1.63 | 68.398438 | 187.296349 | 142.269590 | 3.194925 | 323/323 | 32/32 | Completed / Disposed |
| streams-1-candidate | 1.59 | 68.828125 | 186.381569 | 146.920676 | 3.798713 | 323/323 | 32/32 | Completed / Disposed |
| streams-1-current | 1.70 | 68.664062 | 188.243141 | 192.833334 | 3.997535 | 323/323 | 32/32 | Completed / Disposed |
| streams-2-current | 1.74 | 68.824219 | 188.555939 | 173.549848 | 3.997746 | 323/323 | 32/32 | Completed / Disposed |
| streams-2-candidate | 1.60 | 69.183594 | 186.759834 | 116.682584 | 3.398955 | 323/323 | 32/32 | Completed / Disposed |

All original cell validity, service-standard and recovery predicates passed. Each close receipt reports zero pending requests and zero retained managed/native payload bytes; the observed idle owner/request gauges receded to zero. The JSON preserves all observed maxima and idle gauges, per-process integer counts, protobuf payload/encoded-byte totals and wire statuses. Encoded byte counts exclude gRPC envelopes, HTTP/2 framing and TLS overhead. Socket descriptor counts are not active-stream counts; absent per-operation native allocation, copy, FFI, scheduler and owner costs remain unavailable.

## Bounded source review

The actual a5748-to-092e diff changes only `src/Interop.Callbacks/CallbackCoordinator.cs` and its existing test program. The coordinator records the occupied slot prefix under its existing gate: reservation extends it, release trims trailing empty slots, and retry snapshots that limit before invoking contexts outside the gate. Holes within the prefix remain visible. The added sparse/reuse and reservation-during-retry tests exercise the boundary; this report does not claim to have executed them.

No blocking ownership or lock defect was found in this bounded source read. A reservation beyond a scan snapshot still relies on its existing signal or a later timer scan; the configured interval is not a hard latency bound. Overlapping timer callbacks remain possible, and a dense or high-index prefix can still require a large scan. The shared coordinator has other consumers, whose applicable original regressions remain part of the final selection gate.

## Provenance and limits

- Completed outer execution SHA-256: `b66210f8c27ed70c44dad68d90d1bf58544713c0e5529d749adbb40e1ec7e08e`.
- Actual finite plan SHA-256: `d57bf508fa4a0f7567086722cdaab639ea1b923725458c64e4853e35b77814c5`.
- Candidate B18 result SHA-256: `be0c9ccabaa0b675b5d2ede4ab2fecf3ef231adb21390e5773a7359b5e01d9c1`.
- Full public numeric projection: `callback-prefix-tls-recovered-001.json`; filename/hash provenance index: `callback-prefix-tls-recovered-001.sources.json`.
- Metadata hashes were matched to the completed execution; all 37 original outer receipts were matched to their actual argv, cwd, deadlines and terminal retirement. Package/executable/native identities are the actual producer and loaded-library pins; this review did not reopen or hash their bytes.
- Only explicit public fields are retained. Operational absolute paths, PIDs, environment maps, addresses, TLS material/certificate fingerprints, histogram sample bins and raw observations are excluded. Private source records are not rewritten.
- This is recovery of an already completed diagnostic, with zero formal, capacity or long-run credit. There is no original-main or direct-Rust cohort here and no replacement of any earlier failed or adverse sample. The historical high-load drain failure and the mandatory before/after 30-minute groups remain separate acceptance obligations.
