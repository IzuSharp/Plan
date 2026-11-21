# Epoch-002 report presentation

Status: **source prepared, not executed**. Preparation used source inspection,
JSON inspection and Python AST parsing only. No caller/control module or report
module was imported, and no fixture, build, service or load was run. This source
does not establish acceptance or provide any measured seconds.

`report.py` presents the existing epoch-002 measurements. It does not run a
domain reader, regenerate noise, calculate a percentile, bootstrap a sample,
search for capacity, or invoke the long verifier. Its only derived numeric
operations are unit conversion, integer totals, explicit arithmetic means of
the three capacity confirmations, maximum recorded process peaks, and
absolute/percentage differences.

## Explicit inputs

Copy `manifest.example.json` to a local operational file and replace the
`REPLACE_...` descriptors with actual root-relative paths and SHA-256 hashes.
The example is intentionally not executable. Every supplied execution must
belong to `recovery-002` and the same actual immutable measurement admission
and measurement source index. Comparison and after executions must match the
separate exact final binding. No historical sample can fill a missing slot.

The top-level references are:

- `admission`: the actual populated measurement admission, not the example.
- `measurement_sources`: the exact `measurement-sources.json` used by those
  executions. It also pins the original streaming JSON reader.
- `final_binding`: the actual final binding, or null for a partial before-only
  presentation. A missing binding cannot present comparisons or after data.
- `comparisons`: group/scene plus the actual outer compare `execution.json`.
- `capacities`: group/role plus the actual outer capacity `execution.json`.
- `long_runs`: group/role plus the actual outer long `execution.json`.
- `failed_attempts`: additional actual outer execution receipts, with their
  `stage`, group, role and comparison scene where applicable. Their recorded
  failures remain visible; their partial values receive no comparison credit.

References have `{ "path": "ROOT_RELATIVE_PATH", "sha256": "64_HEX_DIGITS" }`.
Actual receipts may contain absolute paths; they must resolve beneath `--root`.
The adapter follows each outer receipt's existing comparison, capacity or long
verification references. It checks their content hashes, epoch, source/admission
identity and command completion/retirement receipts. Report cell populations
and result hashes must match the outer comparison execution exactly.

Actual producer execution and binding documents are also hash-bound. Their
source commits, package closure/file hashes and native assets are retained in
`report.json`, together with the loaded identities recorded for measured cells.
This is receipt presentation, not a fresh check of all binaries or payloads.
Producer logs and raw correctness ledgers are not replayed. The adapter never
opens a TLS private key or publishes an operational admission in full.

Omitted slots or `execution: null` remain missing. Expected comparison slots are
read from the pinned workload bundle; capacity has five groups × three roles;
the long ledger always has five groups × before/after. Non-completed executions
retain their recorded status. A binding/schema failure produces an explicit
issue and N/A for that slot; a partially projected comparison is discarded as a
unit. Bad top-level inputs fail before output is created.

## Run outside measurement

Use CPU8 and a fresh output directory. The adapter takes the **existing** build
input's exclusive lock before reading result files or producer bindings. A held
lock fails immediately; it never interrupts the current owner or waits for it.
No process owner, workload scheduler or new reservation is introduced.

```sh
taskset -c 8 "$PYTHON" "$REPORT_SOURCE/report.py" \
  --root "$ROOT" \
  --manifest "$REPORT_MANIFEST" \
  --manifest-sha256 "$REPORT_MANIFEST_SHA256" \
  --source-index-sha256 "$REPORT_SOURCE_INDEX_SHA256" \
  --output "$NEW_REPORT_OUTPUT"
```

`sources.json` binds this source directory. The original long verifier module is
loaded only for its hash-pinned `JsonStream` reader. Long protocol projection
selects small metadata and the already recorded p50/p95/p99 fields, skipping
both whole-result and per-scenario histogram populations. The adapter does not
invoke `verify()` and creates no additional acceptance receipt.

Output contains `report.md`, `report.json`, `comparison.csv`, `resources.csv`,
`capacity.csv`, `long-ledger.csv`, `comparison-slots.csv` and `attempts.csv`.
JSON null/Markdown N/A/empty numeric CSV cells indicate unavailable values,
never zero. CSV names use dotted paths for nested fields; arrays are JSON cells.
The process exits nonzero for recorded binding/schema issues, after preserving
the report. Missing or failed supplied slots are presented without turning
their coverage into completion. Check `coverage` and per-slot statuses; a zero
exit code alone is not task acceptance.

## Publication boundary

`report.json` and the identity-rich flattened CSV files contain local operational
paths and maps. They are intermediate evidence, **not automatically safe for
publication under the freeze**. The Markdown failure section can also contain
local paths. Do not automatically commit or upload these raw outputs as the
public Plan deliverable. Curate the actual numeric observations and resource
time series, with filename-plus-hash provenance, under the existing freeze's
publication rules; exclude operational maps and TLS material. Root will prepare
that public report separately. This adapter adds no publication projection or
approval framework.

## Statistical and resource meanings

- Database and protocol p50/p95/p99 are equal-weight means of independent
  process percentiles. Codec percentiles pool exact successful samples. These
  conventions remain explicit in every comparison row.
- DB/protocol throughput is an equal-weight process mean. Codec throughput is
  total successes divided by summed observation seconds. Conditional rows use
  the complete mixed-load observation window; their rates are contributions,
  not standalone capacities.
- CPU/RSS live in a separate whole-profile resource table, referenced by each
  scenario. CPU is percent of one core: DB/protocol use process means; codec
  uses its existing duration-weighted bracket metric. RSS is the maximum of
  recorded sampled process peaks, not the mean of peaks or a continuous bound.
- Error/count totals remain integers. Expected cancellation/deadline probes
  are retained separately from ordinary protocol business success. SQLite
  BUSY/LOCKED counts cover the complete application lifetime; durable
  measurement commits have their original narrower phase scope.
- A21 decisions are copied unchanged and concern independent-process means.
  p99 and throughput deltas are descriptive. C1/C4/C8 database strata retain
  their one-process, statistically ineligible status.
- Codec call time, arrival time, wall MiB/s, summed-call MiB/s, ratio and
  source-derived allocation/copy/FFI counters remain distinct. Managed codec
  observations retain the original restricted valid-corpus isolated-call scope.
- Capacity copies the original selected offered rate and all three final
  confirmations. Their means are explicitly descriptive; protocol business
  throughput excludes probes, while whole-cell confirmation p99 includes them.
  Higher failed points remain recorded; generator failure does not bound the
  server's sustainable capacity.
- Long UTC endpoints describe actual recorded load windows. Effective seconds
  come solely from the original accepted ordinary-operation duration proof.
  Warmup, recovery, idle and outer command/verifier time remain separate. Long
  protocol p99 includes successful expected probes. Codec action counts are
  integer sums of the original compression/decompression partition counts.

The JSON retains original resource-phase summaries, drain/recovery observations,
independent durable results, codec partitions, identity maps and raw evidence
hashes for drilldown. It does not invent GC, native allocation, queue, connection,
SQL/pool/lock wait, per-partition resource or HTTP/2 stream observations. Large
protocol per-scenario histograms and new resource time buckets are deliberately
not regenerated by this presentation adapter.
