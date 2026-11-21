# Perf-01 final selected-native Server regressions

**Source only; unrun.** This additive caller executes the same 29 serial outer
commands as `recovery-regressions-002`, against the Server asset in the actual
final after binding. It produces no performance, duration or global acceptance
credit. It does not run a Rust producer, native unit suite, benchmark or cost
mode. Native regressions and B18 assembled TLS remain separate evidence.

## Reused command and result scope

`../recovery-regressions-002/recipes.py` is imported unchanged, pinned by its
SHA-256 and the original `20ebc834...` source index. Command arguments, flags,
timeouts, ordering and the executable inventory recipe are unchanged.

| Group | Outer commands | Required output retained |
| --- | ---: | --- |
| B17 | 6 | JIT/AOT 105 checks and 43 dispatches; all four transport markers; request-admission/final-lease regression; matching dynamic-code modes |
| B15 | 1 | Original selected-native verifier: JSON/component, 85 real Host assertions per mode, 278 exact public symbols, independent packages and ordinary DTO/native reuse |
| B19 | 10 | JIT/AOT assertion equality and at least 230 assertions; observed managed-retirement totals; all original lifecycle markers; 65 symbols, five static consumers, and unchanged independent package proofs |
| B20 | 12 | Debug defaults: observed 5 assertions; Release JIT/AOT: observed 122 assertions each; original configuration, ownership, listener, ten-context API/XML, sample and package checks; actual H1/H2 close-before-Finish output |

`results.py` preserves the original result collector byte-for-byte outside its
B20 assertion loop. That loop previously required 110 Release assertions. The
bound product `2f40348c3db80a4fbee7a99e721b374a597b16df` calls the new H1 and H2
close-before-Finish tests from `Program.Main`; each adds six checks. The caller
parses and records the actual fixture summary, requires exactly one summary
with the source-bound count and configuration, and checks only output strings
already emitted by that Program.cs. It records the observed per-protocol and
lifecycle marker counts. It neither modifies the product nor substitutes a
historical assertion count. The original collector and its exact hash remain
separately pinned for an auditable one-block adaptation.

All B17/B15/B19 checks, B20 ownership/listener/API/sample/package checks,
finite-owner receipt validation, SDK/native inventories and package provenance
checks are retained. All 29 commands must run successfully for this new result;
partial passes against the former `ccff42c0...` asset are not transferred.

## Actual before and final-after admission

The caller imports the existing `recovery-measure-002/admission.py::Context`
under measurement index
`6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c`.
It requires the immutable baseline measurement admission and its separate,
real final-binding descriptor. The final binding must contain the actual
`after_build_inputs` and `after_build_source_index`, with the after caller index
`66cc5531f6cacc557b8adf5a29ff7853d74a16f22c94279e441703cec2332692`.

Context validates before/common using their original input and source index,
and validates the new after producer using its own actual input and source
index. It retains the original before prerequisite and checks that the final
build and B18 functional-after receipts bind that same baseline. Completed
functional-before and functional-after evidence is required. This caller never
asks the old `build.completed` reader to invent a before receipt under the new
after destination. The real per-role input, source-index and receipt descriptors
are copied into the new local execution/admission/result records.

The unchanged c752 finite pidfd/subreaper owner is reused. An explicit CPU8
invocation is required. The existing timing lock is opened and acquired
nonblocking before Context imports, producer admission hashing or fixture work;
this caller cannot replace or create that lock. Source commits must be clean,
and the reviewed selected fixture commit, dependency locks, toolchain bytes,
boot identity, actual build artifacts and selected Server native hash must
match. The command population still comes exclusively from the pinned original
recipe. No measurement driver, comparison reader or workload algorithm is
copied or invoked by this caller.

Fixture outputs use a fresh separate destination, fresh writable NuGet cache,
temporary directory and CLI home. Original package probes keep their existing
behavior and no-Rust consumer checks. The pinned Python executable directory is
prepended to PATH for nested `python3` calls. Existing toolchain and preparation
proxy settings are inherited; no system home is changed.

## Invocation

Run only after the actual final after producer and assembled B18 functional
receipts are complete and bound. All variables below are operator-supplied
placeholders, not a published local operations map.

```bash
taskset -c 8 "$PERF01_PYTHON" "$PERF01_PLAN/ledger/evidence/batches/Perf-01/diagnostics/recovery-regressions-003/run.py" \
  --root "$PERF01_ROOT" \
  --admission "$PERF01_BASELINE_MEASUREMENT_ADMISSION" \
  --admission-sha256 "$PERF01_BASELINE_MEASUREMENT_ADMISSION_SHA256" \
  --measurement-source-index-sha256 "6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c" \
  --final-binding "$PERF01_ACTUAL_FINAL_BINDING" \
  --final-binding-sha256 "$PERF01_ACTUAL_FINAL_BINDING_SHA256" \
  --source-index-sha256 "$PERF01_REGRESSION003_SOURCE_INDEX_SHA256" \
  --output "$PERF01_FRESH_REGRESSION_OUTPUT_RELATIVE"
```

The output must be task-root-relative, new, and separate from admitted source,
build and measurement directories. An interrupted or failed run remains in its
original output; a new attempt needs a fresh output path. Admission refusal
before the output is created starts no fixture and grants no pass.

## Evidence and publication boundary

Actual execution writes the same finite command receipts/stdout/stderr,
before-and-after executable/native inventories, and original B15/B19/B20
package evidence as the previous caller. `control/execution.json`,
`admission.json` and `result.json` additionally record the actual per-role
producer descriptors and final binding. A failed command retains its finite
owner receipt and logs; no later failure or retry rewrites an earlier attempt.

These records contain absolute local identities and operations maps. They are
local intermediate evidence, not automatically safe public artifacts. Public
Plan evidence must use a reviewed curated projection with synthetic outcomes,
counts, filename/hash provenance and permitted resource observations, excluding
operational maps, TLS material and other private fixture data. This source
directory contains no runtime hash, measured outcome or acceptance result.

Preparation validation is limited to Python AST parsing, JSON parsing,
source-index/hash checks, and a textual check that the result adaptation changes
only the B20 loop. It imports no caller/fixture modules and runs no workload,
build or product test.
