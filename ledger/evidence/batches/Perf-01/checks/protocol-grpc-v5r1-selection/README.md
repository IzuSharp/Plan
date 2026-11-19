# Perf-01 final before gRPC calibration: v5r1

These are byte-identical copies of the completed, small metadata files from
`ROOT/perf01-evidence/calibration/before-grpc-v5r1`, copied on CPU 8 after root
ended session 98397. No new workload was started for this copy.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `selection.json` | 1,880 | `8af8ed599c3378a7009635a681e787da5d44fae4b783f60e82ee7b12c02f09ba` |
| `controller.json` | 36,466 | `dd1901f0762146cafcd6c59cfd71880421668bbc3a8e5bd04e3a2f0c9e712319` |

Selection completed at **2026-11-19T13:40:11.064866+00:00**. The largest
consistently passing sampled offered rate was **160 calls/s** with 64 client
workers; the paired long rate is **128 calls/s**. The unchanged policy chooses
80% of the before rate, capped at 500/s. After/direct capacity measurements may
not retune these paired long rates. This selection grants no 30-minute credit.

| Fresh confirmation | Offered / successful logical checks | p99 arrival latency | Server RSS maximum |
| --- | ---: | ---: | ---: |
| `09-confirmation-0-160` | 9,617 / 9,617 | 154.982480 ms | 107,732,992 bytes |
| `10-confirmation-1-160` | 9,617 / 9,617 | 153.711915 ms | 90,501,120 bytes |
| `11-confirmation-2-160` | 9,617 / 9,617 | 155.846419 ms | 84,533,248 bytes |

Each row is a separate 60-second scheduled process with `exit_code=0`,
`valid=true`, and `qualifies=true`. Each has 9,136 ordinary successful business
calls, with expected cancellation/deadline probes counted separately in the raw
result. The table repeats recorded controller metadata; the independent bounded
memory/failure extraction is linked below.

The first failing bracket rate is 176/s, with two unary `ResourceExhausted`
responses. The 192/s cell has five explicit status-8 rejections. Both remain
valid overload evidence that fails the zero-error service standard. At 256/s,
the original invalid result includes three missing required initial-header
assertions, 61 explicit status-8 rejections and 14 unexpected cancellations.
The exact status/assertion distinctions and hashes are retained in
[`../../protocol-grpc-failure-inspection.md`](../../protocol-grpc-failure-inspection.md).

The before producer is clean main
`ea5fa528035d025bd7a28698ee7c71194432236c`; both producer/common-client build
manifests have SHA-256
`818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3`.
The short gRPC profile SHA-256 is
`42fb00a0571a5721b2b63144544471c103639530dbf8e5664bd7906d1866315b`;
the unchanged long mixed profile SHA-256 is
`fcd529ae210b57a6c3030f7521127204f665f33978ec50d848d13259a7b697af`.
The policy SHA-256 is
`0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc`.
All full command arrays, cell timestamps, plan/result hashes and source pins
remain in `controller.json`. TLS paths/hashes are retained as metadata only;
no key or certificate contents were copied.

The sampled controller/generator memory scope and actual extraction are in
[`../../protocol-controller-memory-review.md`](../../protocol-controller-memory-review.md).
