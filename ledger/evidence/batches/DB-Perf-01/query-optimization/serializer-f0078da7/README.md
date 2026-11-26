# Private-root serializer and recovery checkpoint

Continue [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). The
[selected status/counter/identity record](checkpoint.json) and
[original receipt hashes](evidence-index.json) bind this checkpoint. Original
receipts remain local; this directory contains no source, generated outputs,
restore/environment archive, connection arguments or full logs.

## What is established

The selected private-root serializer is implemented in product head
`f0078da720e07031bc56464995af6791c41aaae8`, tree
`1e56f5466fa02640dcb68389f283e5c03c2c09ec`. The local four-file change is
`9002fe3d93609457a66a566d6939e89db723a3b7`. It uses bounded stack storage only for
one dependency-free root, all origins privately referenced and uncaptured, with
an empty publication-gate set at sealing. The entire command must fit 4096 bytes;
larger, shared, captured, imported and CTE commands keep the generic encoder.
Native code, NWQC framing/sidecar/origin contracts and the callback timer are
unchanged by this slice. **Its effect on the earlier allocation regression is
still pending measurement.**

Local correctness passed 165 Binding assertions across 13 cases, including 81
command-only assertions, plus 1321 Fluent assertions across both real providers
(14 cases each). New cases exercise 4096/4097 bytes, private/shared command-byte
parity, captured origins after reference reduction/public owner disposal, and
quota recovery. Public API checks retain 221 Fluent symbols/13 typed cases,
zero Binding public types and 42 frozen Cdecl signatures.

[Ordinary CI 45624813071](https://github.com/IzuSharp/Korda/actions/runs/45624813071)
passes all required jobs for actual producer
`46ef09477b75dd5ce05e1941a739652bc685a9e2`. The plan retains shared `linux`,
`interop` and independent `postgresql`/`sqlite` package scopes, including Fluent
and aggregate API checks. Modules and publish are skipped under the existing PR
rules; there are zero benchmark jobs. Six external Native AOT applications were
built from the exact two provider artifacts. Four 35-case correctness mixes
passed 280/280 scheduled operations; six cancellation/concurrent-conflict checks
passed, with owners drained. This is correctness evidence, not long-load credit.

## Failures remain separate observations

The preceding CI run `45622268417` failed SQLite's existing B03 AOT execution with
exit -6. Its actual exception stderr was not uploaded. Eleven fresh local
invocations of the existing gate passed, but their local native binary differs
from the CI binary. The original cause remains unknown. The follow-up changes
only exact provider diagnostic upload paths; all 45 existing Tooling tests
executed successfully, including the initially skipped CMake case on the pinned
toolchain. Planner selection, checks, thresholds and job structure are unchanged.
The new CI pass does not explain or erase the old failure.

The earlier PostgreSQL `r1-recovered` prepared-query failure is also unresolved.
Three bounded diagnostic processes did not reproduce it. A separate intentional
missing-table run validated the handler's Provider/42P01 output and unchanged
consumer -6/runner 1 failure. That run is neither reproduction of the original
failure nor a successful comparison cell. Its actual ELF and later stderr-guard
commit remain distinct.

## Resume measurement without changing its inputs

The prior `f493d3d…` freeze is closed: all 16 apps and 867 files were checked
unchanged afterward. Six before-resource processes, three per provider, qualified
for their diagnostic boundaries, with zero long-run credit. They do not establish
whole-framework zero allocation or complete per-window PostgreSQL server CPU.

The new freeze is
`f83df84a57af07a927f4955b91e8a64561bccafa8f92d2bd7181bc3a83efa269`:
16 apps and 926 files. It binds `measurements-v4`, exact `final-local-v5` candidate
apps and `phase-v3` baseline/recovered apps. The same-query phase sequence has
started; its current results and the serializer's benefit are not concluded here.
The four final 1800-second Korda/Dapper.AOT mixed cells still have zero accepted
seconds. Previously unrun `plans-3e2bda3-not-run` are retained.

The summary helper additionally binds nine declared workload fields and requires
the unique stdout result to equal the result file under its observer-recorded
SHA. Four positive receipts and 48 negative mutations passed before the new
freeze; these checks ran no consumers. The numeric extraction helpers are also
frozen. Changes require a new version and explicit record, never replacement of
an in-use measurement tool. See the [handoff](../../handoff-linux.md) for local
paths and remaining work. Actual versions are selected into the JSON record;
no hosted-image build-number requirement or benchmark CI is introduced.

## Documentation verification

This continuation reuses the previously completed 20 Plan and two Design gates
at their preceding commits. They were not rerun for this small checkpoint.
[Validation](validation.json) records fresh link/JSON/diff checks and byte
preservation of historical bodies, tools and acceptance. These document checks
provide no product or performance acceptance.
