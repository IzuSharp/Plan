# Perf-01 recovery-002 selected-native Server regressions

**Source only; unrun.** This directory adds a finite caller for the existing
B17, B15, B19 and B20 fixtures against the final selected Server native asset.
It has no performance workloads, calibration, acceptance-duration credit,
publication action or automatic continuation. Python AST/JSON checks do not
establish a fixture pass. B18 remains the separate assembled TLS verifier.

## Commands and scope

`recipes.py` is the executable command recipe. It emits 29 serial outer
commands, all using the selected product checkout and the admitted toolchain.
No product or original verifier source is changed.

| Group | Outer commands | Included scope | Required current output |
| --- | ---: | --- | --- |
| B17 | 6 | Locked Release JIT restore/build/fixture; locked Linux x64 AOT restore/publish/fixture | 105 checks and 43 dispatches per mode; four transport markers; request-admission/final-lease retirement over HTTP/1.1 and HTTP/2 TLS; dynamic code true/false |
| B15 | 1 | The unchanged `tests/Server.Application/verify.py --native` caller, including managed JSON/component checks, real Host, exact API and independent NuGet consumers | 85 real Host assertions per mode; 278 exact public symbols; selected native hash; ordinary DTO edit reuses the native asset |
| B19 | 10 | Existing managed JIT/AOT fixture, exact API/static consumer checks and unchanged package probe | JIT/AOT assertion counts equal and at least 230; actual managed-retirement count retained separately for each mode; all three cancellation/retirement markers; 65 exact symbols and five static consumers |
| B20 | 12 | Existing Debug defaults, Release JIT/AOT fixture, internal-only API/XML check, Debug sample modes and unchanged package probe | Debug 5 assertions; Release JIT/AOT 110 each; correct configuration/dynamic modes; ownership join and throwing-listener retirement; ten exact context declarations |

B17 is the six-command managed subset documented in
`../../checks/server-retirement-managed-001/README.md`. The unpublished original
command receipt is not represented as recovered. The command recipe here is
derived from the current committed fixtures and the preserved command bounds.
Its fixture invocations each have a 90-second outer bound; restore/build/publish
each retain 900 seconds.

B15 uses its existing 5,400-second outer bound and unchanged internal command
bounds. B19 uses the ten managed/API/package commands from its original
`verify.py`, each bounded at 600 seconds. B20 uses the twelve managed/API/sample/
package commands and their original bounds (120 seconds for Debug defaults,
180 seconds for real Release fixtures, 900 seconds for builds/API/samples,
1,800 seconds for its package probe).

The B19 native producer, native unit/preparse tests and generator-specific
suites are outside this subset. The B20 native producer/unit tests and all
`--cost` modes are outside this subset. No full B17, B19 or B20 native-verifier
pass is inferred. Package probes remain unchanged, including their no-Rust
consumer checks, normal build/publish behavior, SDK asset checks and B19
external private-layout edit proof. This caller does not rebuild the selected
Rust library.

## Identity and ownership

The caller takes an explicit task root, immutable epoch-002 build-input file
and hash, original build-caller source-index file and hash, this directory's
source-index hash, both completed build-receipt hashes, final product commit,
and a fresh task-root-relative output path. It uses the existing timing lock
named by the build inputs, acquired nonblocking **before** expensive admission.
An active controller or measurement keeps ownership; this caller refuses to
start and does not replace the lock.

The unchanged `recovery-build-001` control index is pinned to
`c7526f08d3c50c6d58f7336adae6ebab5fb82b606cce140108a48f6b54b3d0ab`.
Its `build.completed` reads and rehashes both original eight-producer build
receipts, their finite-owner receipts/logs and bound artifacts. The final
Server asset is selected only from the **after** binding; no arbitrary native
path is accepted. The baseline remains
`ea5fa528035d025bd7a28698ee7c71194432236c`, common driver remains
`2e3995df8d86583ee9443348276ca8d918056bfc`, and Design remains
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.

The original build receipts are checked against the **build caller's** source
index, never this regression source index. Their original package/consumer
bindings are retained as prerequisites; this caller makes no new paired
performance claim. Toolchain files, dependency locks, Python dependency bytes,
source commits/trees, recipe-source hashes and the kernel boot must match.
All commands run under the unchanged c752 finite pidfd/subreaper owner on
CPU 8. Interrupted/failed receipts and logs remain in the fresh output.

The SDK argument is the directory containing `dotnet` and `packs/`, not the
`sdk/<version>` subdirectory. The child environment reuses the admitted
toolchain/build environment, with fresh NuGet cache, temporary and CLI-home
directories. The bound Python directory is prepended to `PATH` because the
unchanged nested verifiers invoke `python3` by name. No system home is changed.

## Invocation recipe

Coordinate with the existing controller after the final role build is bound.
All paths below are operator-supplied placeholders. Keep the concrete local
operations map outside the committed Plan record.

```bash
taskset -c 8 "$PERF01_PYTHON" "$PERF01_PLAN/ledger/evidence/batches/Perf-01/diagnostics/recovery-regressions-002/run.py" \
  --root "$PERF01_ROOT" \
  --build-inputs "$PERF01_BUILD_INPUTS" \
  --build-inputs-sha256 "$PERF01_BUILD_INPUTS_SHA256" \
  --build-source-index "$PERF01_BUILD_CALLER_SOURCES" \
  --build-source-index-sha256 "$PERF01_BUILD_CALLER_SOURCES_SHA256" \
  --source-index-sha256 "$PERF01_REGRESSION_SOURCES_SHA256" \
  --before-receipt-sha256 "$PERF01_BEFORE_RECEIPT_SHA256" \
  --after-receipt-sha256 "$PERF01_AFTER_RECEIPT_SHA256" \
  --selected-final-sha "$PERF01_SELECTED_COMMIT" \
  --output "$PERF01_FRESH_OUTPUT_RELATIVE"
```

`PERF01_BUILD_CALLER_SOURCES` is the source index recorded by the actual before
and after build receipts (the epoch-002 caller), not the c752 helper index.
`PERF01_REGRESSION_SOURCES_SHA256` is the SHA-256 of this directory's
`sources.json`. The selected commit is a full 40-character SHA. An existing
output is rejected; an interrupted attempt needs a new output path.

## Evidence produced only on an actual run

- `control/execution.json`: exact argv/environment overrides, prerequisites,
  source/tree/native identities, status, start/end and individual receipt hashes.
- `control/<label>/{receipt.json,stdout.log,stderr.log}`: unchanged finite-owner
  command status, bounds, process retirement and log hashes; failed commands
  remain attributed to their original attempt.
- `inventories/<label>.json`: direct managed fixture/API/sample executable
  inputs immediately before execution, rechecked immediately after. Runtime
  Server SDK records and actual native bytes must match the selected asset.
- `B15/result.json` and original `B15/commands.json`, plus the unchanged
  `B15/package`, `B19-managed/package` and `B20-managed/package` receipts/logs,
  package hashes and actual JIT/AOT output inventories. B15's existing outer
  verifier owns its nested commands; its tested binary inventory is collected
  after that unchanged verifier completes.
- `admission.json` and `result.json`: admitted source hashes and the explicit
  subset results. B19 preserves observed retirement totals and lifecycle marker
  counts; no historical count is substituted. Every reported file is rehashed.

Synthetic B17 TLS fixture material lives in its separate fixture directories.
Output, absolute local operations maps, temporary files, binary/package bytes
and fixture material remain local working evidence until a separate reviewed
projection/archive is prepared. This source directory itself contains no run
result, no selected runtime hash and no functional/performance acceptance credit.

Source validation is `ast.parse` of the three Python files plus JSON parsing
and source-index hash checks. It does not import this caller or its helpers.
