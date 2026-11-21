# Epoch-002 build and B18 control

This is new, **unexecuted** source. It does not reconstruct the unavailable
private epoch-001 wrappers or claim their hashes. No performance workload is
implemented here; current before/final long-test credit remains **0/10**.

`run.py` reuses the public `../recovery-build-001` control implementation:

| Original source | Reused behavior |
|---|---|
| `build.py::plan` | The same eight original producers per product role and three common producers, original arguments and finite command deadlines |
| `build.py::completed` | Original planned/actual command, child retirement, log, input, freeze, toolchain and artifact binding checks |
| `build.py::source`, `freshness` | Exact clean commit and fresh tracked-project build directories |
| `bindings.py::role`, `common` | Actual native assets, full 17-package B24 closure, resolved package bytes/content identities, common 2e application consumers, independent comparators and corpus |
| `owner.py::command`, `enable_subreaper`, `public_tree` | Unchanged finite process-tree ownership, cancellation and retirement, using the original B23 supervisor |

The original `bindings.paired` external-package equality body is preserved in
`run.py::paired`; its after-source comparison now uses the explicit selected
commit. No global `ON` constant is changed: that constant also identifies the
required common application harness and comparators. Original role/common
readers return the old schema's epoch label. The new receipt records it as
`reader_schema_epoch`, with the actual new execution epoch separately set to
`recovery-002`.

## Inputs and sequence

Populate a **local copy** of `inputs.example.json` once. Required unresolved
inputs are the root-relative locked Design checkout, the complete restored
toolchain manifest/hash and the restored Python HTTP/2 dependency manifest/hash.
The latter retains the published ten distribution versions and actual installed
file hashes. The complete toolchain must report `ready: true`, including
PostgreSQL. A native-only restoration checkpoint is insufficient.

Keep this input, source index and referenced freeze immutable after the first
build. `products.after.commit` deliberately remains `null`: the before build can
proceed while the final repair is still being selected. The eventual after,
bind-pair and functional-after invocations require the full
`--selected-final-sha`. Each verifies the clean selected checkout; role binding
propagates that commit through actual native, B24, protocol, codec and shared
artifacts. Prerequisite after receipts must identify exactly the same commit.

Run the following stages serially from CPU8 with the exact bound Python. Shell
variables below denote actual local values; no command has been executed by
this source-preparation change.

```sh
taskset -c 8 "$PYTHON" "$CALLER/run.py" --root "$ROOT" \
  --inputs "$INPUTS" --inputs-sha256 "$INPUTS_SHA" \
  --source-index-sha256 "$SOURCE_INDEX_SHA" --stage before
```

Use the same prefix for subsequent stages, with these additional arguments:

| Stage | Additional arguments |
|---|---|
| `common` | `--before-receipt-sha256 "$BEFORE_RECEIPT_SHA"` |
| `functional-before` | `--before-receipt-sha256 "$BEFORE_RECEIPT_SHA"` |
| `after` | `--before-receipt-sha256 "$BEFORE_RECEIPT_SHA" --selected-final-sha "$FINAL_SHA"` |
| `functional-after` | `--before-receipt-sha256 "$BEFORE_RECEIPT_SHA" --after-receipt-sha256 "$AFTER_RECEIPT_SHA" --selected-final-sha "$FINAL_SHA"` |
| `bind-pair` | `--before-receipt-sha256 "$BEFORE_RECEIPT_SHA" --after-receipt-sha256 "$AFTER_RECEIPT_SHA" --common-receipt-sha256 "$COMMON_RECEIPT_SHA" --selected-final-sha "$FINAL_SHA"` |

Each stage needs fresh output/control directories. Failures preserve receipts
and partial output; the caller never silently resumes or overwrites them. Role
builds require fresh product checkouts without tracked-project `bin`/`obj` or
`target`. Use the reserved fresh after checkout, not a diagnostic checkout that
already ran tests. All commands share the epoch's exclusive timing lock.

## Functional proof

The two original product-local B18 entry points run inside the same finite owner:

1. `native/protocols/grpc/verify-native.py --output …/native-component`.
2. `tests/Protocols.Grpc/verify.py --output …/assembled --design … --sdk …
   --native ACTUAL_ROLE_SERVER --expected-native-sha256 ACTUAL_ROLE_HASH
   --native-source-commit SELECTED_SHA
   --native-component-receipt …/native-component/result.json`.

The first verifier's Cargo commands use the product's `target` directory; the
caller removes an inherited `CARGO_TARGET_DIR` for these two commands. The
second verifier checks the actual role asset independently of the native
component test binary. Its original JIT/AOT, API/XML, HTTP/2+TLS cardinality,
deadline/trailer and ordinary edited package-consumer assertions remain intact.
No old assertion count is substituted for the selected source's actual result.

The caller retains and hashes the original results, command logs, JIT/AOT
inventories, package proof and actual role asset. `functional_scope` is **B18
only**. Other original module regressions required by the selected shared fix
remain separate obligations. A successful build or B18 receipt is not a noise,
capacity, profiling or 30-minute acceptance receipt.

Full local operational maps remain local. Any later public projection must be
separately curated; this source does not publish evidence or private key bytes.
