# B23 domain workload observations

Phase: **functional**. Execution state: **completed**.

Functional comparison only; timing outputs do not constitute performance evidence.

**Acceptance:** B22 correctness/fault/soak acceptance remains separately required.

## Scope and reproducibility

The product is the accepted C# reference application over the unchanged Rust Database and Server engines. The direct Rust and managed Native AOT applications are comparison executables. Their exact source, lock, executable, native and configuration hashes accompany the raw phase records.

Execution isolation: Functional validation; no performance conclusion.

A21 schedules independent arrivals and retains generator lag, all outcomes, raw events and histograms. The HTTP adapter validates actual protocol/TLS and the application AOT witness; its separate SQL/blob oracle checks durable effects after each process cohort. Adapter admission is HTTP-client dispatch, not an internal Server or database-pool admission timestamp.

## Workload results

| Workload / route | Valid processes | Samples / outcomes | Offered / admitted / completed per second | p50 / p95 / p99 / p99.9 (ms) | Max (ms) |
| --- | ---: | --- | --- | --- | ---: |
| advanced-di-list-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 17.616 / 17.616 | 10.041 / unavailable / unavailable / unavailable | 13.535 |
| cold-create-small-sqlite-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.786 / 18.786 | 6.286 / unavailable / unavailable / unavailable | 6.460 |
| cold-create-small-sqlite-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 18.777 / 18.777 | 6.514 / unavailable / unavailable / unavailable | 7.266 |
| cold-create-small-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 17.978 / 17.978 | 8.854 / unavailable / unavailable / unavailable | 11.249 |
| diagnostics-debug-default-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.822 / 18.822 | 6.257 / unavailable / unavailable / unavailable | 10.215 |
| diagnostics-debug-local-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.993 / 18.993 | 5.300 / unavailable / unavailable / unavailable | 5.903 |
| diagnostics-exporter-failure-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.529 / 18.529 | 7.941 / unavailable / unavailable / unavailable | 8.812 |
| diagnostics-exporter-saturation-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.238 / 18.238 | 9.418 / unavailable / unavailable / unavailable | 9.663 |
| diagnostics-full-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.364 / 18.364 | 8.654 / unavailable / unavailable / unavailable | 8.908 |
| diagnostics-log-only-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.230 / 18.230 | 5.063 / unavailable / unavailable / unavailable | 9.710 |
| diagnostics-meter-only-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 17.240 / 17.240 | 14.806 / unavailable / unavailable / unavailable | 16.012 |
| diagnostics-release-disabled-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.003 / 18.003 | 5.430 / unavailable / unavailable / unavailable | 11.093 |
| diagnostics-sampled-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.740 / 18.740 | 5.210 / unavailable / unavailable / unavailable | 6.724 |
| minimal-list-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 17.921 / 17.921 | 11.602 / unavailable / unavailable / unavailable | 15.773 |
| stream-eight-mib-sqlite-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 12.495 / 12.495 | 60.060 / unavailable / unavailable / unavailable | 87.028 |
| stream-eight-mib-sqlite-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 11.915 / 11.915 | 67.851 / unavailable / unavailable / unavailable | 79.618 |
| stream-eight-mib-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 8.588 / 8.588 | 132.881 / unavailable / unavailable / unavailable | 154.156 |
| stream-one-mib-postgresql-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 15.198 / 15.198 | 26.822 / unavailable / unavailable / unavailable | 31.600 |
| stream-one-mib-postgresql-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 14.869 / 14.869 | 24.810 / unavailable / unavailable / unavailable | 34.507 |
| stream-one-mib-postgresql-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 13.633 / 13.633 | 46.705 / unavailable / unavailable / unavailable | 57.715 |
| stream-one-mib-postgresql-http1-tls / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 15.787 / 15.787 | 19.375 / unavailable / unavailable / unavailable | 26.685 |
| stream-one-mib-postgresql-http1-tls / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 14.462 / 14.462 | 29.541 / unavailable / unavailable / unavailable | 38.296 |
| stream-one-mib-postgresql-http1-tls / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 11.485 / 11.485 | 61.273 / unavailable / unavailable / unavailable | 74.139 |
| stream-one-mib-postgresql-http2-tls / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 11.715 / 11.715 | 66.012 / unavailable / unavailable / unavailable | 70.719 |
| stream-one-mib-postgresql-http2-tls / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 13.195 / 13.195 | 41.849 / unavailable / unavailable / unavailable | 51.572 |
| stream-one-mib-postgresql-http2-tls / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 13.045 / 13.045 | 48.917 / unavailable / unavailable / unavailable | 53.316 |
| stream-one-mib-sqlite-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 16.403 / 16.403 | 19.635 / unavailable / unavailable / unavailable | 21.932 |
| stream-one-mib-sqlite-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 16.734 / 16.734 | 19.520 / unavailable / unavailable / unavailable | 19.735 |
| stream-one-mib-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 13.365 / 13.365 | 49.644 / unavailable / unavailable / unavailable | 61.853 |
| stream-one-mib-sqlite-http1-tls / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 15.999 / 15.999 | 25.004 / unavailable / unavailable / unavailable | 27.462 |
| stream-one-mib-sqlite-http1-tls / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 15.853 / 15.853 | 25.048 / unavailable / unavailable / unavailable | 26.159 |
| stream-one-mib-sqlite-http1-tls / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 14.102 / 14.102 | 41.819 / unavailable / unavailable / unavailable | 53.148 |
| stream-one-mib-sqlite-http2-tls / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 11.971 / 11.971 | 66.093 / unavailable / unavailable / unavailable | 67.064 |
| stream-one-mib-sqlite-http2-tls / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 14.588 / 14.588 | 37.095 / unavailable / unavailable / unavailable | 37.171 |
| stream-one-mib-sqlite-http2-tls / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 12.383 / 12.383 | 60.743 / unavailable / unavailable / unavailable | 61.506 |
| upload-overload-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 1, "rejected": 1} | 10.000 / 2.876 / 2.876 | 38.234 / unavailable / unavailable / unavailable | 695.421 |
| warm-create-large-sqlite-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.901 / 18.901 | 5.815 / unavailable / unavailable / unavailable | 7.449 |
| warm-create-large-sqlite-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 18.985 / 18.985 | 5.345 / unavailable / unavailable / unavailable | 13.244 |
| warm-create-large-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.251 / 18.251 | 9.584 / unavailable / unavailable / unavailable | 10.784 |
| warm-cycle-high-postgresql-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 17.099 / 17.099 | 13.107 / unavailable / unavailable / unavailable | 16.966 |
| warm-cycle-high-postgresql-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 17.941 / 17.941 | 10.551 / unavailable / unavailable / unavailable | 11.475 |
| warm-cycle-high-postgresql-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 13.181 / 13.181 | 32.374 / unavailable / unavailable / unavailable | 51.734 |
| warm-cycle-high-postgresql-http1-tls / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.081 / 18.081 | 10.612 / unavailable / unavailable / unavailable | 12.543 |
| warm-cycle-high-postgresql-http1-tls / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 17.803 / 17.803 | 11.331 / unavailable / unavailable / unavailable | 12.342 |
| warm-cycle-high-postgresql-http1-tls / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 15.963 / 15.963 | 25.287 / unavailable / unavailable / unavailable | 40.192 |
| warm-cycle-high-postgresql-http2-tls / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 17.826 / 17.826 | 9.519 / unavailable / unavailable / unavailable | 12.195 |
| warm-cycle-high-postgresql-http2-tls / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 18.050 / 18.050 | 10.802 / unavailable / unavailable / unavailable | 11.446 |
| warm-cycle-high-postgresql-http2-tls / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 14.534 / 14.534 | 37.613 / unavailable / unavailable / unavailable | 47.553 |
| warm-cycle-high-sqlite-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.482 / 18.482 | 8.212 / unavailable / unavailable / unavailable | 8.336 |
| warm-cycle-high-sqlite-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 18.410 / 18.410 | 8.635 / unavailable / unavailable / unavailable | 9.150 |
| warm-cycle-high-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 16.434 / 16.434 | 21.697 / unavailable / unavailable / unavailable | 60.905 |
| warm-cycle-high-sqlite-http1-tls / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.415 / 18.415 | 8.607 / unavailable / unavailable / unavailable | 10.128 |
| warm-cycle-high-sqlite-http1-tls / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 18.245 / 18.245 | 9.592 / unavailable / unavailable / unavailable | 9.619 |
| warm-cycle-high-sqlite-http1-tls / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 14.305 / 14.305 | 39.812 / unavailable / unavailable / unavailable | 42.796 |
| warm-cycle-high-sqlite-http2-tls / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 16.899 / 16.899 | 15.391 / unavailable / unavailable / unavailable | 18.347 |
| warm-cycle-high-sqlite-http2-tls / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 18.227 / 18.227 | 9.722 / unavailable / unavailable / unavailable | 9.729 |
| warm-cycle-high-sqlite-http2-tls / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 16.294 / 16.294 | 22.744 / unavailable / unavailable / unavailable | 51.738 |
| warm-cycle-low-sqlite-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 16.077 / 16.077 | 8.478 / unavailable / unavailable / unavailable | 24.405 |
| warm-cycle-low-sqlite-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 18.443 / 18.443 | 8.440 / unavailable / unavailable / unavailable | 9.157 |
| warm-cycle-low-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 15.762 / 15.762 | 19.488 / unavailable / unavailable / unavailable | 26.887 |
| warm-keyset-page-postgresql-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.760 / 18.760 | 4.549 / unavailable / unavailable / unavailable | 6.611 |
| warm-keyset-page-postgresql-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 19.045 / 19.045 | 5.015 / unavailable / unavailable / unavailable | 5.531 |
| warm-keyset-page-postgresql-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 16.881 / 16.881 | 9.391 / unavailable / unavailable / unavailable | 18.474 |
| warm-keyset-page-sqlite-http1 / direct-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.247 / 18.247 | 5.052 / unavailable / unavailable / unavailable | 9.609 |
| warm-keyset-page-sqlite-http1 / managed-aot | 1/1 | 2 / {"ok": 2} | 10.000 / 19.120 / 19.120 | 4.605 / unavailable / unavailable / unavailable | 4.767 |
| warm-keyset-page-sqlite-http1 / nativeweave-aot-rust | 1/1 | 2 / {"ok": 2} | 10.000 / 18.702 / 18.702 | 6.702 / unavailable / unavailable / unavailable | 6.939 |

p99.9 is unavailable below 1000 samples; aggregate percentiles describe pooled raw requests, confidence intervals compare independent process means.

Expected HTTP500 diagnostic probes form separate workloads. Logical oracle success means the declared result matched; it never relabels those HTTP errors as business success. Individual process receipts preserve actual HTTP status counts, including setup/warmup, separately from measured logical outcomes.

## Latency stages and startup

| Workload / route | Startup to READY (ms) | Dispatch delay p95 (ms) | Client queue/admission p95 (ms) | Successful service observed p95 (ms) |
| --- | ---: | ---: | ---: | ---: |
| advanced-di-list-sqlite-http1 / nativeweave-aot-rust | 52.507 | unavailable | unavailable | unavailable |
| cold-create-small-sqlite-http1 / direct-rust | 12.429 | unavailable | unavailable | unavailable |
| cold-create-small-sqlite-http1 / managed-aot | 38.495 | unavailable | unavailable | unavailable |
| cold-create-small-sqlite-http1 / nativeweave-aot-rust | 39.872 | unavailable | unavailable | unavailable |
| diagnostics-debug-default-sqlite-http1 / nativeweave-aot-rust | 67.423 | unavailable | unavailable | unavailable |
| diagnostics-debug-local-sqlite-http1 / nativeweave-aot-rust | 52.386 | unavailable | unavailable | unavailable |
| diagnostics-exporter-failure-sqlite-http1 / nativeweave-aot-rust | 58.905 | unavailable | unavailable | unavailable |
| diagnostics-exporter-saturation-sqlite-http1 / nativeweave-aot-rust | 40.916 | unavailable | unavailable | unavailable |
| diagnostics-full-sqlite-http1 / nativeweave-aot-rust | 39.085 | unavailable | unavailable | unavailable |
| diagnostics-log-only-sqlite-http1 / nativeweave-aot-rust | 39.025 | unavailable | unavailable | unavailable |
| diagnostics-meter-only-sqlite-http1 / nativeweave-aot-rust | 38.086 | unavailable | unavailable | unavailable |
| diagnostics-release-disabled-sqlite-http1 / nativeweave-aot-rust | 45.323 | unavailable | unavailable | unavailable |
| diagnostics-sampled-sqlite-http1 / nativeweave-aot-rust | 45.012 | unavailable | unavailable | unavailable |
| minimal-list-sqlite-http1 / nativeweave-aot-rust | 41.284 | unavailable | unavailable | unavailable |
| stream-eight-mib-sqlite-http1 / direct-rust | 12.882 | unavailable | unavailable | unavailable |
| stream-eight-mib-sqlite-http1 / managed-aot | 49.808 | unavailable | unavailable | unavailable |
| stream-eight-mib-sqlite-http1 / nativeweave-aot-rust | 48.625 | unavailable | unavailable | unavailable |
| stream-one-mib-postgresql-http1 / direct-rust | 36.100 | unavailable | unavailable | unavailable |
| stream-one-mib-postgresql-http1 / managed-aot | 60.436 | unavailable | unavailable | unavailable |
| stream-one-mib-postgresql-http1 / nativeweave-aot-rust | 68.991 | unavailable | unavailable | unavailable |
| stream-one-mib-postgresql-http1-tls / direct-rust | 22.278 | unavailable | unavailable | unavailable |
| stream-one-mib-postgresql-http1-tls / managed-aot | 107.339 | unavailable | unavailable | unavailable |
| stream-one-mib-postgresql-http1-tls / nativeweave-aot-rust | 74.617 | unavailable | unavailable | unavailable |
| stream-one-mib-postgresql-http2-tls / direct-rust | 19.237 | unavailable | unavailable | unavailable |
| stream-one-mib-postgresql-http2-tls / managed-aot | 163.287 | unavailable | unavailable | unavailable |
| stream-one-mib-postgresql-http2-tls / nativeweave-aot-rust | 61.033 | unavailable | unavailable | unavailable |
| stream-one-mib-sqlite-http1 / direct-rust | 12.464 | unavailable | unavailable | unavailable |
| stream-one-mib-sqlite-http1 / managed-aot | 39.351 | unavailable | unavailable | unavailable |
| stream-one-mib-sqlite-http1 / nativeweave-aot-rust | 54.799 | unavailable | unavailable | unavailable |
| stream-one-mib-sqlite-http1-tls / direct-rust | 16.319 | unavailable | unavailable | unavailable |
| stream-one-mib-sqlite-http1-tls / managed-aot | 166.670 | unavailable | unavailable | unavailable |
| stream-one-mib-sqlite-http1-tls / nativeweave-aot-rust | 40.481 | unavailable | unavailable | unavailable |
| stream-one-mib-sqlite-http2-tls / direct-rust | 14.400 | unavailable | unavailable | unavailable |
| stream-one-mib-sqlite-http2-tls / managed-aot | 74.351 | unavailable | unavailable | unavailable |
| stream-one-mib-sqlite-http2-tls / nativeweave-aot-rust | 44.859 | unavailable | unavailable | unavailable |
| upload-overload-sqlite-http1 / nativeweave-aot-rust | 44.900 | unavailable | unavailable | unavailable |
| warm-create-large-sqlite-http1 / direct-rust | 14.234 | unavailable | unavailable | unavailable |
| warm-create-large-sqlite-http1 / managed-aot | 39.169 | unavailable | unavailable | unavailable |
| warm-create-large-sqlite-http1 / nativeweave-aot-rust | 41.207 | unavailable | unavailable | unavailable |
| warm-cycle-high-postgresql-http1 / direct-rust | 19.208 | unavailable | unavailable | unavailable |
| warm-cycle-high-postgresql-http1 / managed-aot | 50.606 | unavailable | unavailable | unavailable |
| warm-cycle-high-postgresql-http1 / nativeweave-aot-rust | 64.266 | unavailable | unavailable | unavailable |
| warm-cycle-high-postgresql-http1-tls / direct-rust | 32.699 | unavailable | unavailable | unavailable |
| warm-cycle-high-postgresql-http1-tls / managed-aot | 90.131 | unavailable | unavailable | unavailable |
| warm-cycle-high-postgresql-http1-tls / nativeweave-aot-rust | 68.577 | unavailable | unavailable | unavailable |
| warm-cycle-high-postgresql-http2-tls / direct-rust | 32.298 | unavailable | unavailable | unavailable |
| warm-cycle-high-postgresql-http2-tls / managed-aot | 93.414 | unavailable | unavailable | unavailable |
| warm-cycle-high-postgresql-http2-tls / nativeweave-aot-rust | 64.960 | unavailable | unavailable | unavailable |
| warm-cycle-high-sqlite-http1 / direct-rust | 13.998 | unavailable | unavailable | unavailable |
| warm-cycle-high-sqlite-http1 / managed-aot | 51.359 | unavailable | unavailable | unavailable |
| warm-cycle-high-sqlite-http1 / nativeweave-aot-rust | 60.613 | unavailable | unavailable | unavailable |
| warm-cycle-high-sqlite-http1-tls / direct-rust | 12.649 | unavailable | unavailable | unavailable |
| warm-cycle-high-sqlite-http1-tls / managed-aot | 75.410 | unavailable | unavailable | unavailable |
| warm-cycle-high-sqlite-http1-tls / nativeweave-aot-rust | 46.825 | unavailable | unavailable | unavailable |
| warm-cycle-high-sqlite-http2-tls / direct-rust | 20.726 | unavailable | unavailable | unavailable |
| warm-cycle-high-sqlite-http2-tls / managed-aot | 73.159 | unavailable | unavailable | unavailable |
| warm-cycle-high-sqlite-http2-tls / nativeweave-aot-rust | 43.077 | unavailable | unavailable | unavailable |
| warm-cycle-low-sqlite-http1 / direct-rust | 11.505 | unavailable | unavailable | unavailable |
| warm-cycle-low-sqlite-http1 / managed-aot | 47.811 | unavailable | unavailable | unavailable |
| warm-cycle-low-sqlite-http1 / nativeweave-aot-rust | 47.706 | unavailable | unavailable | unavailable |
| warm-keyset-page-postgresql-http1 / direct-rust | 22.804 | unavailable | unavailable | unavailable |
| warm-keyset-page-postgresql-http1 / managed-aot | 112.391 | unavailable | unavailable | unavailable |
| warm-keyset-page-postgresql-http1 / nativeweave-aot-rust | 78.550 | unavailable | unavailable | unavailable |
| warm-keyset-page-sqlite-http1 / direct-rust | 22.374 | unavailable | unavailable | unavailable |
| warm-keyset-page-sqlite-http1 / managed-aot | 40.285 | unavailable | unavailable | unavailable |
| warm-keyset-page-sqlite-http1 / nativeweave-aot-rust | 42.074 | unavailable | unavailable | unavailable |

Queue/admission is observed over the controller/adapter IPC and includes the bounded HTTP-client queue. Service duration includes HTTP, application, database and client work after adapter admission; it is not an internal database execution timer. Raw A21 records also retain attempts and protocol-event bytes. Those JSONL byte counts are not HTTP/TLS wire-byte measurements.

## Application memory and CPU

| Workload / route | CPU per offered operation (ms) | RSS after (MiB) | Private working set after (MiB) | Threads after | Managed allocated bytes per offered operation |
| --- | ---: | ---: | ---: | ---: | ---: |
| advanced-di-list-sqlite-http1 / nativeweave-aot-rust | 5.000 | 27.684 | 22.504 | 22.0 | 1819480 |
| cold-create-small-sqlite-http1 / direct-rust | 0.000 | 7.477 | 6.605 | 7.0 | unavailable |
| cold-create-small-sqlite-http1 / managed-aot | 0.000 | 35.453 | 32.641 | 13.0 | unavailable |
| cold-create-small-sqlite-http1 / nativeweave-aot-rust | 5.000 | 23.582 | 20.762 | 16.0 | unavailable |
| diagnostics-debug-default-sqlite-http1 / nativeweave-aot-rust | 10.000 | 32.383 | 29.523 | 21.0 | 635020 |
| diagnostics-debug-local-sqlite-http1 / nativeweave-aot-rust | 10.000 | 32.781 | 29.918 | 23.0 | 633828 |
| diagnostics-exporter-failure-sqlite-http1 / nativeweave-aot-rust | 5.000 | 27.344 | 24.488 | 20.0 | 645972 |
| diagnostics-exporter-saturation-sqlite-http1 / nativeweave-aot-rust | 5.000 | 27.266 | 24.410 | 20.0 | 634892 |
| diagnostics-full-sqlite-http1 / nativeweave-aot-rust | 5.000 | 27.262 | 24.406 | 19.0 | 637768 |
| diagnostics-log-only-sqlite-http1 / nativeweave-aot-rust | 5.000 | 31.164 | 28.309 | 20.0 | 626440 |
| diagnostics-meter-only-sqlite-http1 / nativeweave-aot-rust | 10.000 | 27.391 | 24.535 | 20.0 | 634108 |
| diagnostics-release-disabled-sqlite-http1 / nativeweave-aot-rust | 0.000 | 27.512 | 22.355 | 22.0 | 629612 |
| diagnostics-sampled-sqlite-http1 / nativeweave-aot-rust | 5.000 | 26.980 | 24.125 | 20.0 | 644132 |
| minimal-list-sqlite-http1 / nativeweave-aot-rust | 10.000 | 27.316 | 24.461 | 21.0 | 1818868 |
| stream-eight-mib-sqlite-http1 / direct-rust | 60.000 | 7.820 | 6.949 | 9.0 | unavailable |
| stream-eight-mib-sqlite-http1 / managed-aot | 70.000 | 37.582 | 34.770 | 13.0 | unavailable |
| stream-eight-mib-sqlite-http1 / nativeweave-aot-rust | 125.000 | 27.727 | 22.605 | 17.0 | unavailable |
| stream-one-mib-postgresql-http1 / direct-rust | 10.000 | 7.559 | 6.688 | 7.0 | unavailable |
| stream-one-mib-postgresql-http1 / managed-aot | 15.000 | 38.043 | 32.930 | 13.0 | unavailable |
| stream-one-mib-postgresql-http1 / nativeweave-aot-rust | 30.000 | 29.078 | 26.258 | 15.0 | unavailable |
| stream-one-mib-postgresql-http1-tls / direct-rust | 5.000 | 8.453 | 7.582 | 7.0 | unavailable |
| stream-one-mib-postgresql-http1-tls / managed-aot | 20.000 | 43.750 | 40.758 | 13.0 | unavailable |
| stream-one-mib-postgresql-http1-tls / nativeweave-aot-rust | 50.000 | 30.004 | 24.883 | 15.0 | unavailable |
| stream-one-mib-postgresql-http2-tls / direct-rust | 10.000 | 8.766 | 7.895 | 7.0 | unavailable |
| stream-one-mib-postgresql-http2-tls / managed-aot | 30.000 | 42.949 | 37.602 | 13.0 | unavailable |
| stream-one-mib-postgresql-http2-tls / nativeweave-aot-rust | 25.000 | 30.188 | 9.066 | 15.0 | unavailable |
| stream-one-mib-sqlite-http1 / direct-rust | 5.000 | 7.891 | 7.020 | 9.0 | unavailable |
| stream-one-mib-sqlite-http1 / managed-aot | 5.000 | 36.281 | 31.168 | 13.0 | unavailable |
| stream-one-mib-sqlite-http1 / nativeweave-aot-rust | 30.000 | 25.531 | 9.441 | 16.0 | unavailable |
| stream-one-mib-sqlite-http1-tls / direct-rust | 15.000 | 8.770 | 7.898 | 9.0 | unavailable |
| stream-one-mib-sqlite-http1-tls / managed-aot | 15.000 | 43.109 | 40.117 | 13.0 | unavailable |
| stream-one-mib-sqlite-http1-tls / nativeweave-aot-rust | 30.000 | 26.781 | 23.961 | 16.0 | unavailable |
| stream-one-mib-sqlite-http2-tls / direct-rust | 10.000 | 9.211 | 8.332 | 10.0 | unavailable |
| stream-one-mib-sqlite-http2-tls / managed-aot | 15.000 | 42.180 | 36.887 | 13.0 | unavailable |
| stream-one-mib-sqlite-http2-tls / nativeweave-aot-rust | 35.000 | 26.770 | 23.949 | 16.0 | unavailable |
| upload-overload-sqlite-http1 / nativeweave-aot-rust | 100.000 | 27.625 | 10.625 | 17.0 | unavailable |
| warm-create-large-sqlite-http1 / direct-rust | 5.000 | 7.461 | 6.590 | 7.0 | unavailable |
| warm-create-large-sqlite-http1 / managed-aot | 5.000 | 35.305 | 32.492 | 13.0 | unavailable |
| warm-create-large-sqlite-http1 / nativeweave-aot-rust | 5.000 | 23.465 | 20.645 | 16.0 | unavailable |
| warm-cycle-high-postgresql-http1 / direct-rust | 0.000 | 7.102 | 6.230 | 5.0 | unavailable |
| warm-cycle-high-postgresql-http1 / managed-aot | 0.000 | 37.074 | 34.262 | 13.0 | unavailable |
| warm-cycle-high-postgresql-http1 / nativeweave-aot-rust | 20.000 | 29.281 | 26.461 | 15.0 | unavailable |
| warm-cycle-high-postgresql-http1-tls / direct-rust | 0.000 | 8.008 | 7.137 | 5.0 | unavailable |
| warm-cycle-high-postgresql-http1-tls / managed-aot | 5.000 | 42.711 | 39.719 | 13.0 | unavailable |
| warm-cycle-high-postgresql-http1-tls / nativeweave-aot-rust | 15.000 | 29.953 | 27.133 | 15.0 | unavailable |
| warm-cycle-high-postgresql-http2-tls / direct-rust | 0.000 | 8.320 | 7.449 | 5.0 | unavailable |
| warm-cycle-high-postgresql-http2-tls / managed-aot | 5.000 | 42.887 | 39.895 | 13.0 | unavailable |
| warm-cycle-high-postgresql-http2-tls / nativeweave-aot-rust | 15.000 | 30.297 | 27.477 | 15.0 | unavailable |
| warm-cycle-high-sqlite-http1 / direct-rust | 0.000 | 7.672 | 6.801 | 7.0 | unavailable |
| warm-cycle-high-sqlite-http1 / managed-aot | 0.000 | 35.477 | 30.312 | 13.0 | unavailable |
| warm-cycle-high-sqlite-http1 / nativeweave-aot-rust | 15.000 | 25.785 | 22.965 | 16.0 | unavailable |
| warm-cycle-high-sqlite-http1-tls / direct-rust | 0.000 | 8.520 | 7.648 | 7.0 | unavailable |
| warm-cycle-high-sqlite-http1-tls / managed-aot | 5.000 | 41.977 | 38.984 | 13.0 | unavailable |
| warm-cycle-high-sqlite-http1-tls / nativeweave-aot-rust | 20.000 | 26.648 | 23.828 | 16.0 | unavailable |
| warm-cycle-high-sqlite-http2-tls / direct-rust | 0.000 | 8.777 | 7.906 | 7.0 | unavailable |
| warm-cycle-high-sqlite-http2-tls / managed-aot | 0.000 | 41.902 | 38.910 | 13.0 | unavailable |
| warm-cycle-high-sqlite-http2-tls / nativeweave-aot-rust | 15.000 | 26.785 | 23.965 | 16.0 | unavailable |
| warm-cycle-low-sqlite-http1 / direct-rust | 5.000 | 7.699 | 6.828 | 7.0 | unavailable |
| warm-cycle-low-sqlite-http1 / managed-aot | 10.000 | 35.363 | 32.551 | 13.0 | unavailable |
| warm-cycle-low-sqlite-http1 / nativeweave-aot-rust | 15.000 | 25.871 | 23.051 | 16.0 | unavailable |
| warm-keyset-page-postgresql-http1 / direct-rust | 0.000 | 7.777 | 6.906 | 5.0 | unavailable |
| warm-keyset-page-postgresql-http1 / managed-aot | 0.000 | 37.543 | 34.727 | 13.0 | unavailable |
| warm-keyset-page-postgresql-http1 / nativeweave-aot-rust | 5.000 | 30.230 | 27.406 | 17.0 | unavailable |
| warm-keyset-page-sqlite-http1 / direct-rust | 5.000 | 8.457 | 7.555 | 9.0 | unavailable |
| warm-keyset-page-sqlite-http1 / managed-aot | 0.000 | 37.500 | 34.645 | 13.0 | unavailable |
| warm-keyset-page-sqlite-http1 / nativeweave-aot-rust | 5.000 | 26.906 | 24.051 | 21.0 | unavailable |

App child procfs and standard GC/Meter observations are separate from Python adapter resources. Unknown counters are not zero..

CPU comes from child-process procfs ticks around measured requests. RSS/private working set are endpoint observations, and lifetime high-water RSS additionally remains in the JSON. Native allocator live/retained bytes, per-operation FFI/copy counts, whole-thread stacks and kernel-buffer memory remain unavailable where no supported observer exists. A21 raw files separately retain the adapter process observations; those are never presented as application memory.

Instrumented application variants use standard GC totals and Activity/Meter/ILogger listeners. GC deltas include the observation boundary overhead and any concurrent application allocations; they are not isolated DTO allocations. Native payload gauges describe retained charged payload owners, not all native allocations or a process RSS bound. Meter callback snapshots have the accepted one-second cache interval. Instrumented cells allow a declared 1.1-second observation settling interval after measurement boundaries. Module mappings preserve virtual image/code bytes separately from resident memory. Process exit alone is not a retirement or leak proof.

## Actual diagnostic observations

| Workload / process | Activities (delta) | Log calls / exports / failures (delta) | Callback max (us) | Dropped metadata (delta) | Queue entries / bytes sampled peak | Managed / native payload sampled peak (bytes) |
| --- | ---: | --- | ---: | ---: | --- | --- |
| diagnostics-release-disabled-sqlite-http1 / 0 | 0 | 0 / 0 / 0 | unavailable | unavailable | unavailable / unavailable | unavailable / unavailable |
| advanced-di-list-sqlite-http1 / 0 | 0 | 0 / 0 / 0 | unavailable | unavailable | unavailable / unavailable | unavailable / unavailable |
| diagnostics-exporter-saturation-sqlite-http1 / 0 | 3 | 0 / 0 / 0 | 27.761 | 0 | 3 / 456 | 0 / 0 |
| diagnostics-debug-local-sqlite-http1 / 0 | 0 | 2 / 2 / 0 | 56.293 | 0 | 0 / 0 | 0 / 0 |
| diagnostics-meter-only-sqlite-http1 / 0 | 0 | 0 / 0 / 0 | 955.982 | 0 | 0 / 0 | 0 / 0 |
| diagnostics-debug-default-sqlite-http1 / 0 | 0 | 0 / 0 / 0 | unavailable | unavailable | unavailable / unavailable | unavailable / unavailable |
| diagnostics-log-only-sqlite-http1 / 0 | 0 | 2 / 2 / 0 | unavailable | unavailable | unavailable / unavailable | unavailable / unavailable |
| diagnostics-exporter-failure-sqlite-http1 / 0 | 4 | 3 / 0 / 3 | 201.768 | 3 | 0 / 0 | 0 / 0 |
| diagnostics-sampled-sqlite-http1 / 0 | 0 | 2 / 2 / 0 | 86.798 | 0 | 0 / 0 | 0 / 0 |
| diagnostics-full-sqlite-http1 / 0 | 3 | 2 / 2 / 0 | 1363.478 | 0 | 0 / 0 | 0 / 0 |
| minimal-list-sqlite-http1 / 0 | 0 | 0 / 0 / 0 | unavailable | unavailable | unavailable / unavailable | unavailable / unavailable |

Sampled peaks include setup and observation endpoints and can miss shorter peaks between observations. No-listener profiles leave callback/drop/native-payload observations unavailable instead of enabling a Meter implicitly. Exporter saturation and failure are actual controlled sink behavior; the saturation row must exceed the 2048-entry queue and observe a positive drop count. Reduced functional runs only check blocking configuration and do not claim the queue filled.

## Measured-noise comparisons

No confirmatory route comparison was requested in this phase.

Bands are derived from independent calibration-process variability before confirmation data is collected. A21 supplies the seeded process-bootstrap intervals. This initial baseline has no historical-release performance target; a route-cost decision does not select or replace the product engine. Small process counts limit interval precision.

## Deployment and developer cost

| Route | Runtime deployment (MiB) | Executable (MiB) | Native modules (MiB) | Debug symbols (MiB) |
| --- | ---: | ---: | ---: | ---: |
| direct-rust | 8.977 | 8.977 | 0.000 | 0.000 |
| managed-aot | 20.723 | 18.847 | 1.875 | 0.000 |
| nativeweave-aot-rust | 27.937 | 5.754 | 22.183 | 13.855 |

- direct-rust: application source physical lines by role {"rust-comparator": 2162, "sql-schema": 62}.
- managed-aot: application source physical lines by role {"managed-application": 1183, "sql-schema": 62}.
- nativeweave-aot-rust: application source physical lines by role {"managed-application": 1435, "sql-schema": 62}; compressed NativeWeave package closure 9.018 MiB.

The shipped NativeWeave Server module contains HTTP/TLS/Tonic/rmcp native code. Unconfigured managed protocol facades do not remove that code. Both provider assets are present in the full reference consumer; loaded mappings are observed separately.

Source line counts include comments/blanks and retain individual hashes. They cover the named app/comparator sources only; dependencies, precompiled Rust modules and unpersisted source-generator output are disclosed separately. Code moved into a package or generated layer is not treated as eliminated complexity.

| Recorded application build | Command | Elapsed (s) | Observation method |
| --- | --- | ---: | --- |
| direct-rust | recorded producer build | 126.000 | compiler-reported duration |
| direct-rust | Actual incremental build after the Linux platform boundary guard, not a cold build-cost comparison | 35.452 | external monotonic command duration |
| managed-aot | recorded producer build | unavailable | not recorded |
| nativeweave-aot-rust | baseline-jit-restore | unavailable | not recorded |
| nativeweave-aot-rust | baseline-jit-build | 4.280 | MSBuild-reported Time Elapsed |
| nativeweave-aot-rust | baseline-aot-restore | unavailable | not recorded |
| nativeweave-aot-rust | baseline-aot-publish | unavailable | not recorded |
| ordinary-edit-evidence | baseline-jit-restore | unavailable | not recorded |
| ordinary-edit-evidence | baseline-jit-build | 4.760 | MSBuild-reported Time Elapsed |
| ordinary-edit-evidence | baseline-aot-restore | unavailable | not recorded |
| ordinary-edit-evidence | baseline-aot-publish | unavailable | not recorded |
| ordinary-edit-evidence | edited-jit-restore | unavailable | not recorded |
| ordinary-edit-evidence | edited-jit-build | 3.960 | MSBuild-reported Time Elapsed |
| ordinary-edit-evidence | edited-aot-restore | unavailable | not recorded |
| ordinary-edit-evidence | edited-aot-publish | unavailable | not recorded |
| instrumented-copy | restore | 1.272 | external monotonic command duration |
| instrumented-copy | release-publish | 16.566 | external monotonic command duration |
| instrumented-copy | debug-publish | 18.283 | external monotonic command duration |

Accepted ordinary Entity/DTO/Handler edit evidence: [{"builds": ["edited-aot", "edited-jit"], "changed_files": ["DatabaseService.cs", "Models.cs", "Program.cs", "Protocol.cs"], "native_modules_unchanged": true, "no_consumer_rust_invocation": true, "variant": "edited"}].

Build durations reuse actual recorded commands with warm/available caches. Missing durations remain unavailable; these observations are not a clean-machine build-time comparison. The full exact command/source/native/package inventory is in the JSON.

## Unsupported and non-equivalent cells

- upload-overload-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- upload-overload-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-release-disabled-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-release-disabled-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-debug-default-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-debug-default-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-debug-local-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-debug-local-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-sampled-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-sampled-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-full-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-full-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-meter-only-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-meter-only-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-log-only-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-log-only-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-exporter-saturation-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-exporter-saturation-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-exporter-failure-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- diagnostics-exporter-failure-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- minimal-list-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- minimal-list-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- advanced-di-list-sqlite-http1 / managed-aot: No equivalent implementation of this product resource/diagnostic profile.
- advanced-di-list-sqlite-http1 / direct-rust: No equivalent implementation of this product resource/diagnostic profile.
- direct-rust: Ordinary workload cells only. No B22 fault/soak or maintenance acceptance..
- direct-rust: No equivalent NativeWeave global byte-credit/overload ledger; corresponding cells not implemented/not run..
- direct-rust: No DI or enabled-diagnostics variants..
- direct-rust: Seven-day retention maintenance is not implemented; fresh bounded-duration datasets only..
- direct-rust: Comparator migration ledger and runtime/pool architecture differ from NativeWeave; cold/startup and whole-service ratios must disclose this..
- direct-rust: Exact idle/overload/cancellation equivalence is not established by these ordinary rows..
- managed-aot: Ordinary workload cells only. No B22 fault/soak or maintenance acceptance..
- managed-aot: No equivalent NativeWeave global byte-credit/overload ledger; corresponding cells not implemented/not run..
- managed-aot: No DI or enabled-diagnostics variants..
- managed-aot: Seven-day retention maintenance is not implemented; fresh bounded-duration datasets only..
- managed-aot: Comparator migration ledger and runtime/pool architecture differ from NativeWeave; cold/startup and whole-service ratios must disclose this..
- managed-aot: Exact idle/overload/cancellation equivalence is not established by these ordinary rows..
- nativeweave-aot-rust: No public per-operation FFI/copy/native-allocation counter is present in the accepted application.

## Interpretation and remaining gates

The measured reference service includes typed query construction, Rust database execution, DTO serialization, authenticated HTTP, transactional result/outbox writes, keyset queries and attachment staging/streaming in the declared cells. Foreground timing disables the periodic outbox consumer equally; external publication throughput is not established by these rows. Content-addressed stream fixtures reuse identical bytes after their first upload, explicitly distinguishing that cache profile from unique-content storage growth.

Cold means a fresh application process/database and its first request. Host page caches are not flushed. The fixed native Server closure still includes its accepted optional protocol code even when only REST is configured; no absent-code or zero-cost claim follows from an unconfigured facade.

Unsupported query families or optional protocol facades absent from the reference app are not silently represented by an empty handler. No unmeasured optimization or universal percentage benefit is asserted. B22 supplies independent fault/long-duration correctness, and B24 supplies final package/pristine-consumer/release acceptance. Linux evidence does not certify other platforms.
