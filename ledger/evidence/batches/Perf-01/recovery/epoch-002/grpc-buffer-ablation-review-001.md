# Perf-01: independent review of the completed gRPC buffer ablation report

Status: **accepted as a diagnostic public projection after the histogram-field correction**. No remaining blocking discrepancy was found. The experiment remains isolated and unselected; this review grants no formal comparison, capacity, long-duration, or product-retention acceptance.

| Reviewed file or completed source | SHA-256 |
| --- | --- |
| `grpc-buffer-ablation-001/README.md` | `c0076aa08209dc35c3e4bfe044d7ff42bb3fd5f080bb3ee39b6311999b5b9fd5` |
| `grpc-buffer-ablation-001/projection.json` | `968a25c72a2a9d0568a443b682b1161c9660ae2f6b47bba98ef9f987f3b1bc18` |
| Actual ablation execution | `37a61ab9c3c5d7625a4003d4c4d352523aad3b30a44c6873240d03328293520a` |
| Actual finite plan | `68457d9223dd5106a572768928a234e41df3f56580635dfea126aa43ef7bd10b` |

The initial public `arrival_success_maximum_ns` label was ambiguous: it copied the configured A21 histogram ceiling, not an observed maximum latency. Source inspection of `Benchmarks.Harness/nativeweave_bench.py::histogram` confirmed the distinction. The author renamed all thirty fields to `arrival_success_histogram_maximum_ns` and added explicit JSON/Markdown clarification. The unchanged 60-second bound is no longer presented as an observed maximum; no maximum or mean was inferred from histogram bins.

The review used bounded source and completed metadata reads on CPU 8. Fifty-six metadata files were checked: the execution and actual plan, thirty-seven original command receipts, twelve results, three build manifests, and B18 result/execution metadata. There were 2,072 literal comparisons and 45 arithmetic comparisons without a discrepancy. All twelve resource-table rows also match the original values after display rounding. No raw request/resource JSONL, corpus payload, package, executable or native binary was read or hashed, and no target module or workload was run.

The current managed source `2f40348c…`, candidate `ea006711…`, unchanged common driver `2e3995df…`, shared independent client, package identities, and actually loaded Server SHA `8b726c39…` match their completed receipts. The candidate's managed/native provenance remains explicitly different. B18 JIT/AOT assertion and retirement counts match the actual passed fixture metadata; the separate accepted component-test binary is not confused with the experiment's loaded Server.

All thirty scenario observations, twelve process resources/GC/gauge observations, exact percentiles, null means, counts, statuses, recovery and retirement values match their original results. All thirty-seven commands exited zero and retired with no recorded live owned or adopted children. The total is 3,876 measured successful calls. The report correctly separates ordinary calls from warmup/recovery and does not claim the short mixes exercised deadline/cancel probes.

All three server-stream p99 increases remain visible: +63.6611%, +35.3720%, and +3.2299%. The three client-stream increases are +4.9966%, +2.6215%, and +11.3219%. Every candidate after-idle RSS is higher across the six paired processes. Streaming allocation and sampled CPU reductions are also retained, without a claim that these establish a tail-latency or memory-footprint win. Comparisons are paired descriptive arithmetic, not an A21 noise decision or a direct-Rust/baseline gap update. The report does not causally attribute the adverse tails to the extra credit/reap path.

A public key/value check found no absolute operational paths, PIDs, environment maps, endpoint addresses or TLS material. Evidence-relative names, source repository references and recorded hashes remain. The report is suitable for the intended public diagnostic checkpoint; actual measured-load acceptance remains with the original task gates.
