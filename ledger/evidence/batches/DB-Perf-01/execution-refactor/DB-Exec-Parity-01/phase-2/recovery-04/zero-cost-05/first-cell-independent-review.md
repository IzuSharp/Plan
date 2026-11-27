# First zero-cost cell: independent lightweight review

The existing SQLite candidate 30-second, 500 offered operations/s cell passes this independent result/validation reconciliation. This review did not rerun the workload, hash large artifacts or add performance credit.

## Observed coverage and costs

- All 35 original case IDs occur exactly once in the per-case ledger and each succeeded 428 or 429 times. Totals are 15,000 successes, 366,067 consumed rows, zero business failures, rejections, retries or oracle failures, and no outstanding requests. Expected-result and mode-contract sets cover the same 35 cases. The existing validator additionally checks each case against the locked row/digest oracle.
- Client process CPU is 2.9482345 ms per success. Managed allocation is 20,738.3125 B per success. Both include producer/harness, driver/framework and business DTO/string/JSON work; framework-only allocation remains unknown.
- GC counts are 98/16/2 for generations 0/1/2. Process pause delta is `(1,138,390 - 54,960) / 10,000,000 = 0.108343 seconds`, matching validation.
- Peak RSS through the post-measurement snapshot is 44,220,416 B. After tracked-owner drain and 4.9995 seconds idle without forced GC, RSS is 42,295,296 B. All tracked owner counters are zero. This is a process-memory observation, not a native-allocation measurement.
- Native allocation profile and framework-only managed bytes are explicitly null/unknown. Latency p50/p95/p99 values are histogram-bin upper bounds, with service, scheduled-to-completion and start-delay boundaries separately retained.

## Advice for the remaining cells

Keep the remaining interleaved cells at the same rate, queue, worker, warmup, row/batch and fixture conditions. Throughput near 500/s reflects the offered rate; use CPU/operation and service/queue distributions for this cost lane. Do not label this single 30-second cell as capacity or parity, and do not count it among the four 30-minute acceptance cells. Its null freeze is appropriate only for this screening identity.

For PostgreSQL, keep client process CPU separate from server visible-proc inner/outer sampled intervals and the server wait4 lifetime total. The lifetime includes startup, seeding, warmup, idle and shutdown; it must not be added to sampled interval CPU. The sampled endpoints are non-atomic observations, not exact steady bounds, and missed exited children or non-atomic transfer losses remain unknown.

## Exact input identity

- `experiments/recovery/zero-cost-05/round-01/sqlite-candidate/measurement/result.json`: SHA256 `948906dd5e87b9b134df17d935fc13b659f0286d37e519ee6c873aa15549ecfd`; 115785 bytes.
- `experiments/recovery/zero-cost-05/round-01/sqlite-candidate/validation.json`: SHA256 `9cbc4576deeeaa60ff425cd44fa8e05781f124a782f350ce81830b5ea4222f48`; 7724 bytes.
