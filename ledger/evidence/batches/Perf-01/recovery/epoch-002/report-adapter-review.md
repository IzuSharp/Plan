# Epoch-002 report adapter: independent source review

**Accepted as presentation-only source; no blocking defect found.** This review
binds `diagnostics/recovery-report-002/sources.json` SHA-256
`00757dd85400382b4213bbb7c45a69026f0d4dc42f6223a6f100fa764219aa0e`.
It establishes no actual report result, functional acceptance or measurement
credit.

The reviewer read the complete adapter, example manifest and documentation,
then compared their field accesses with the original database/protocol/codec
extractors, domain drivers, three capacity controllers, measurement caller and
streaming long verifier. All three indexed presentation files and eight indexed
schema sources match their declared hashes. The adapter parses as Python AST;
the source index and example parse as JSON. The example contains 16 comparison,
15 capacity and ten long slots. These checks used CPU 8 and imported no target
module; no adapter, extractor, fixture, service, build or load was executed.

## Numeric meaning

| Area | Checked behavior |
| --- | --- |
| Before/after deltas | `after - before`, divided by before for percentage change. Absolute integer count differences remain integers. A zero or unavailable denominator gives N/A. |
| Direct Rust gaps | `before - direct` and `after - direct`, each divided by direct. Lower latency therefore has a negative latency gap; lower successful throughput has a negative throughput gap. |
| Database | Uses the existing equal-weight process means of throughput and p50/p95/p99. Errors, successes and offered counts are integer sums of the original count vectors. Conditional cycle/page rates retain the whole mixed-load denominator. |
| Protocol | Uses the existing means of three independent process percentiles and throughput. Original integer unexpected-error and business-success totals are preserved; expected cancellation/deadline probes remain separate. |
| Codec | Copies pooled exact-success-sample percentiles and total-success/summed-observation throughput from the original extractor. Isolated call means, wall MiB/s, summed-call MiB/s, ratio and derived counters remain distinct. The extractor's required zero-error result supports the displayed zero; no missing error observation is substituted. |
| Resources | One separate resource row describes the complete mixed process/profile. DB/protocol CPU uses process means; codec CPU uses the original duration-weighted bracket metric. RSS uses the maximum recorded sampled process peak. The adapter assigns no resource shares to conditional scenarios or codec partitions. |

Database one-process strata keep the original statistically ineligible decision.
Protocol eligibility and A21 decisions are copied from their original report.
Codec call/arrival noise decisions are copied independently; completing its
extractor does not turn a descriptive p99/throughput delta into statistical
acceptance. Managed codec observations retain their restricted original scope.
The adapter calculates no percentile, noise band, bootstrap or capacity search.

## Capacity and long-ledger schemas

Capacity projection matches the three actual controller schemas. It requires
the original final three passing 60-second confirmations at the selected
offered rate, preserves higher failed points and the controller's capacity
scope, and labels arithmetic confirmation means as descriptive. Protocol
business throughput excludes successful expected probes; the whole-cell
confirmation p99 includes them. Generator-invalid higher points remain distinct
from a server-capacity upper bound.

The long ledger constructs all five groups × before/after independently of
which entries the operator supplies. Actual UTC fields match each domain's
recorded measurement-window schema. Error totals use original integer outcome
counts; codec compression/decompression counts sum the original `c`/`d`
partitions. CPU, sampled RSS, recovery, idle, drain and durable-state fields keep
their original observation scopes.

An accepted long row requires the bound original verifier's accepted flag,
recorded duration proof and at least 1,800 credited seconds, with credit equal
to the outer execution receipt. The adapter copies those existing seconds. It
neither derives credit from UTC endpoints nor invokes the verifier. Its only
later runtime import of that hash-pinned module supplies `JsonStream` for
bounded protocol metadata/percentile selection; large histogram populations
are skipped.

## Identity, failures and execution limits

Executions must match the same actual epoch-002 admission and measurement
source index. Comparison/after records must match the separate final binding.
Producing receipt and binding identities remain explicit. Comparison process
populations and summary/result hashes must exactly match their outer execution;
historical workloads are reused only as frozen configuration, not as measured
data. Child command completion and retirement receipts are checked.

The existing exclusive lock prevents presentation from competing with a running
controller. Omitted/null slots stay missing. Failed/incomplete executions retain
their status and failure details without partial comparison credit. A schema or
binding error gives an issue and N/A; partially projected comparison rows and
their resource/identity additions are discarded together. The expected ten
long slots remain present, and zero exit status alone is not task completion.

This remains receipt presentation: it does not replay payload/persistence
oracles, rehash every runtime binary, or authenticate an arbitrary rewritten
receipt independently of the supplied evidence chain. Actual first execution
must still produce readable artifacts from current receipts. No source change
is required by this review.

## Publication scope

The refreshed index changes only the README's publication-boundary paragraph
and its recorded hash; `report.py` and the example manifest remain byte-identical
to this review's original `b489a31c` source. The reviewer verified that removing
that added section exactly reproduces the previous README hash. No broad audit
or execution was repeated.

`report.json`, identity-rich flattened CSV and Markdown failure paths are local
intermediate evidence, not automatically publication-safe outputs. Only a
curated numeric/public projection may be published under the existing freeze:
retain actual numeric observations, permitted resource time series and
filename-plus-hash provenance while excluding operational maps and TLS
material. This source acceptance does not endorse committing or uploading the
raw report outputs.
