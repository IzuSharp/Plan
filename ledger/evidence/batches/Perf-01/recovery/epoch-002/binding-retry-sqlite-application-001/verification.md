# Independent review of the completed SQLite application evidence

The review found **no blocking discrepancy in the completed metadata** for the six C16 cells and their seven finite control commands. This reviewer is separate from the workload executor and prepared the adjacent curated projection. This is not a second independent review of the projection itself.

## Scope and checks

The review ran only bounded completed-file reads, source inspection, hashing and arithmetic on CPU 8. It did not build or run an application, replay any request, rescan the large request/resource streams, or execute a new statistical classifier.

The read set included the original `original-cell-checks.json`, six cell summaries/freezes/plans/progress records, seven finite receipts, both package consumers/observer manifests, the actual package inventories, the common driver sources, and the original reader/adapter sources. [The verification record](verification.json) lists the exact read-and-hashed paths and checks.

- 702 literal comparisons, including identical frozen configurations, original p50/p95/p99/count/outcome fields, successful original predicates, complete resource-summary preservation, and exact durable/recovery/drain results.
- 55 SHA-256 binding comparisons; 60 distinct source/metadata files were read and hashed. Some supplemental hashes are recorded without a second external expected-hash assertion; these are not counted as independently matched bindings.
- 162 checks of original means, success rates, and CPU interval arithmetic. CPU calculations use matching process start identity and clock frequency and preserve unavailable single-sample shutdown phases.
- Six actual Native AOT executable receipts agree with their expected hashes; both tested native library identities agree with their consumer/observer records. Physical libraries were not rehashed by this review after the process ended; their runtime `/proc` load receipts are the original evidence.
- Seventeen actual `.1` package hashes per cohort match the producer’s `previous` member. The separate `.2` `candidate` member is not the tested consumer set.

The original reader had already verified the finite request order, schedule, raw counts/latencies, and input hashes. This review preserves that completed result and checks its projected metadata against independent small cell summaries. It does **not** claim a second raw-stream replay, a fresh persistence query after completion, or a new statistical proof. The raw observation/dataset/application-receipt hashes are retained as original-reader provenance where not reread here.

## Numerical and scope conclusions

All 18 successful-scope metric sets (whole/cycle/page for each cell) agree with the original summary percentile and outcome fields. Original means agree with sum/count, and the whole latency sum is the cycle sum plus page sum. Page p50 and arithmetic median are deliberately kept separate.

All nine descriptive scope pairs show lower mean and p99. Whole-workload p99 changes are −74.265987%, −68.850188%, and −73.517053%. Application CPU is higher in every pair, and original sampled idle CPU is also higher. The idle CPU is available in the original metadata; no zero or unavailable value is substituted. Explicit idle endpoint brackets are an additional calculation with their own duration and scope, not a replacement for the original sampled phase.

All 18,006 measured business operations succeeded. Each cell has 1,501 durable measured commits and 1,500 page operations, zero observed provider exceptions/BUSY/LOCKED, zero explicit benchmark retries, the expected independently observed 1,637 then 1,653 persistent rows per table, successful original content/cardinality oracles, and successful release/dispose results. All seven controls retired without remaining owned processes/children.

## Required limitations

Managed GC/allocation counters are unavailable for the actual uninstrumented application route; Python scheduler GC is not .NET GC. Internal SQLite busy retries and lock/pool wait time are unobserved. Application CPU cannot be apportioned to conditional cycles/pages or solely to the DB retry change. The candidate changes both DB and Server retry periods, while the common native library hashes remain unchanged. Source-level hypotheses about shorter retirement waits or timer-scan CPU are not measurements of causality.

All original per-cell predicates pass, but the adapter explicitly does not perform formal admission or noise classification. The current2f cohort is not the EA5 round-original baseline. This evidence earns **zero formal short, capacity, or 30-minute credit** and leaves the historical 567.131236 ms C16 failure intact.

Projection SHA-256: `2115a4080ca67c8e0e5f76427b4814464b329907dee1120af2fd12c42277e40b`.
