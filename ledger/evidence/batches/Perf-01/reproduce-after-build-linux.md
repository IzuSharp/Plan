# Perf-01 final after build and validation recipe

Status: source-inspected execution recipe, not an executed after build or an
acceptance receipt. All preparation below runs only after the integration owner
ends the exclusive calibration/measurement window. Builders sharing one product
checkout run sequentially. Final product SHA and fresh attempt names are filled
from the accepted candidate; no future SHA or outcome is implied here.

## Source and package decisions

The producer source inspected is the Task-07 implementation at
`ea5fa528035d025bd7a28698ee7c71194432236c`: `eng/task07_native.py`,
`src/Packaging.Domain/{prepare,model,inventory}.py`, and
`eng/verify-task07-linux.sh`. The Perf-01 codec driver source is the unchanged
`tests/Perf01.Codec` inventory bound by the existing before-002 manifest, whose
driver commit is `d14be5432c7fcce7d2aeaaf5d4218b3f6bd40fd3`.

Run the B24 producer again in a fresh after checkout/output. Its first
`build_managed(..., candidate=False)` builds all fourteen managed projects;
`compose(..., previous=None)` packs these and all three native leaves. Use this
new `previous/feed` with one version for measurement, as the before build does.
The script also emits a candidate closure, copying eight common archives only
from its newly produced previous closure. This is safe within the new after
pair; importing common archives from the before pair would omit shared changes.

| Package group | Exact IDs, with `NativeWeave.` prefix |
| --- | --- |
| Eight common packages, rebuilt for after | `Interop.Abi`, `Core`, `Data`, `Database.Transactions`, `Data.Streaming`, `Query.Binding`, `Query.Generator`, `Server.Generator` |
| Six domain facades | `Database`, `Database.Sqlite`, `Database.PostgreSql`, `Server`, `Server.Grpc`, `Server.Mcp` |
| Three native leaves | `Database.Sqlite.Native`, `Database.PostgreSql.Native`, `Server.Native` |

A17 codec is a separate two-package closure: `NativeWeave.Core` and
`NativeWeave.Engines.SyncProof`, both at the existing experimental
`0.1.0-proof.1` identity. It embeds the ABI assembly in its Core envelope. Keep
its before/after feeds and consumer caches separate from each other and from
B24; do not merge the two Core envelopes into a feed.

The protocol agent independently read the B24/protocol commands and source,
producer override rejection, shared client/direct identities and B15 gate wiring
and found no source blocker. This bounded review did not execute the recipe or
review every unrelated repository gate.

## Build inputs and exact commands

The following shell variables describe one new attempt. Set `PERF_AFTER_SHA` to
the final committed forty-character product SHA before running this block.
Do not add host-native ISA, allocator, GC or Rust compiler overrides: the before
manifests bind the original settings. `env.sh` selects SDK 11.0.100, Rust 1.100.0,
the installed linker prerequisites and three Cargo build jobs. The B24 native
producer explicitly rejects unrecorded Rust profile overrides.

```sh
PERF_ROOT=/workspace/scratch/01c249676f47
PERF_DRIVER="$PERF_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF_PLAN="$PERF_ROOT/.worktree/Perf-01-linux/Plan"
PERF_DESIGN="$PERF_ROOT/repos/NativeWeave-Design"
PERF_PRODUCT="$PERF_ROOT/.worktree/Perf-01-after-linux/NativeWeave"
PERF_OUT="$PERF_ROOT/perf01-build/after-001"
PERF_PG_BIN="$PERF_ROOT/perf01-toolchain/postgres18/bin"
PERF_VERSION=0.1.0-perf01.after.1
source "$PERF_ROOT/perf01-toolchain/env.sh"

git -C "$PERF_ROOT/repos/NativeWeave" worktree add --detach "$PERF_PRODUCT" "$PERF_AFTER_SHA"
cd "$PERF_PRODUCT"
CARGO_TARGET_DIR="$PERF_OUT/cargo-stable-target" python3 eng/task07_native.py \
  --output "$PERF_OUT/native-stable"
python3 src/Packaging.Domain/prepare.py \
  --output "$PERF_OUT/packages" \
  --previous-version "$PERF_VERSION" \
  --candidate-version 0.1.0-perf01.after.2 \
  --native-manifest "$PERF_OUT/native-stable/manifest.json"
git diff --exit-code
```

The first producer creates `PERF_OUT` parents. Both producers reject dirty source
and existing result directories. The selected Rust release profile remains
generic x86-64, thin LTO, one codegen unit and unwind panic behavior; the separate
SQLite/server and PostgreSQL feature profiles are preserved. A native hash may
remain equal when an optimization changes only managed code. A new package hash
alone does not prove that the changed implementation was executed.

### Package application and protocol consumers

Run consumers from the frozen driver checkout, using the new feed. Keep the B21
application source and runner equal to the before measurement; ordinary
application changes are not part of this performance comparison.

```sh
cd "$PERF_DRIVER"
python3 tests/Reference.TaskService/package_probe.py \
  --source "$PERF_DRIVER" --runner "$PERF_DRIVER/tests/Reference.TaskService/run.py" \
  --feed "$PERF_OUT/packages/previous/feed" --version "$PERF_VERSION" \
  --postgres-bin "$PERF_PG_BIN" --output "$PERF_OUT/reference" \
  --variants baseline --providers sqlite --modes jit aot --protocols http1 --build-only
python3 tests/Perf01.Database/prepare_observer.py \
  --package-probe "$PERF_OUT/reference" --output "$PERF_OUT/db-observer" \
  --dotnet "$DOTNET_ROOT/dotnet"
python3 tests/Perf01.Protocols/build.py \
  --feed "$PERF_OUT/packages/previous/feed" --version "$PERF_VERSION" \
  --sdk "$DOTNET_ROOT/dotnet" --output "$PERF_OUT/protocols" \
  --package-manifest "$PERF_OUT/packages/manifest.json" \
  --native-manifest "$PERF_OUT/native-stable/manifest.json"
```

The protocol command's omitted `--packages` selects a fresh private cache inside
the new output. Do not use `--compile-only`: those results are ineligible for
measurement. Protocol C# remains explicit `x86-64-v2`; B21/codec retain their
recorded compiler defaults. These are per-driver before/after matches, not an
assertion that every driver has identical ISA settings.

Final HTTP/gRPC plans must keep the shared independent client:
`--client-build ROOT/perf01-build/before/protocols-v2/build.json`, whose client
SHA-256 is `acb1c163cd51e291f58dbe51ae12c04f82c2b51538aa36e446a05890e06aadd0`.
The protocol integration owner confirmed that the generic direct-Rust v3 server
is retained. Compare the `.cs`, `.csproj`, shared source and protobuf hashes to
this client build when preparing after plans. A newly built client is not an
automatic substitution for the frozen generator. Plan construction also pins
the final Python/profile sources, including any separately accepted layered
protocol selector.

### Codec and profiling-only consumers

```sh
cd "$PERF_DRIVER"
python3 tests/Perf01.Codec/driver.py prepare \
  --product-root "$PERF_PRODUCT" --output "$PERF_OUT/codec"
python3 tests/Perf01.Shared/prepare.py \
  --feed "$PERF_OUT/packages/previous/feed" --version "$PERF_VERSION" \
  --output "$PERF_OUT/shared-retirement"
python3 tests/Perf01.Shared/prepare.py --probe page \
  --feed "$PERF_OUT/packages/previous/feed" --version "$PERF_VERSION" \
  --output "$PERF_OUT/shared-page"
```

Codec `prepare` includes A17's actual package JIT/AOT, ownership, bounded-decode,
negative compilation and ordinary-managed-edit checks; it is not merely a
compile command. It builds its product native module under `PERF_PRODUCT/target`
and the direct reference under the new codec output. The measurement consumer is
then published with the exact same driver and flags as before-002. Reuse
`ROOT/perf01-codec-checks/corpus` unchanged; its manifest SHA-256 is
`92932f7ecba2b3a7104b19344d22a42c3c40605f23eb158a0941d48bfff0465d`.
Do not run `corpus` again or edit a prepared manifest to change its binding.

Before any new codec cell, require identical `driver_sha256`, `a21_sha256`,
product lock hashes, and relevant build environment fields across before/after.
The driver already rechecks current source, artifacts and copied consumer inputs
at execution. Different package/executable hashes are expected; actual mapped
native bytes must match each respective manifest. The existing before manifest
is `ROOT/perf01-codec-checks/package-before-002/manifest.json` (SHA-256
`4a448f9f9a9e3b9dd1887fced2aae2da33280aa6b6ca7e3c9ef416fe50fc9c87`).

## Focused regression gates

Execute the new focused tests against the unchanged implementation and the final
candidate with the same test source. Keep these component receipts separate from
the immutable main-based before performance packages. The relevant candidate
commands are below; outputs are fresh and all execution stays outside timing.

```sh
cd "$PERF_PRODUCT"
python3 tests/Interop.Negotiation/verify.py \
  --plan-root "$PERF_PLAN" --design-root "$PERF_DESIGN" --output "$PERF_OUT/gates/A02"
env -u CARGO_TARGET_DIR python3 tests/Data.Streaming/verify.py \
  --postgres-bin "$PERF_PG_BIN" --design-root "$PERF_DESIGN" --output "$PERF_OUT/gates/B06"
python3 tests/Server.Application/verify.py \
  --native "$PERF_OUT/native-stable/libnativeweave_server.so" \
  --design "$PERF_DESIGN" --sdk "$DOTNET_ROOT" --output "$PERF_OUT/gates/B15"
env -u CARGO_TARGET_DIR python3 tests/Engines.SyncProof/verify.py \
  --packaging-root "$PERF_PRODUCT" --output "$PERF_OUT/gates/A17"
```

A02 exercises repaired premapping failures, default single bootstrap, explicit
option revalidation and conflicting descriptors in real JIT/AOT processes. B06
executes both real providers, including the blocked synchronous materializer and
concurrent-dispose retirement tests. B15 executes the component suite in JIT
and AOT (including fragmented JSON, exact caps, held writes, faults and quota
release), real server cases and package/API checks. Its `--sdk` takes the SDK
root, whereas protocol `build.py --sdk` takes the `dotnet` executable. A17's full
gate adds native tests, direct valid/invalid codec behavior, generator identity,
C layout, compiled API/XML and source/package consumers beyond codec preparation.

If the retained change affects common owner/buffer/async behavior, select the
corresponding existing regression gate rather than assuming a codec pass covers
all adopters:

```sh
env -u CARGO_TARGET_DIR python3 tests/Interop.Lifetime/verify.py --output "$PERF_OUT/gates/A03"
env -u CARGO_TARGET_DIR python3 tests/Interop.Memory/verify.py --output "$PERF_OUT/gates/A04"
env -u CARGO_TARGET_DIR python3 tests/Interop.Async/verify.py --output "$PERF_OUT/gates/A07"
env -u CARGO_TARGET_DIR python3 tests/Engines.AsyncProof/verify.py \
  --packaging-root "$PERF_PRODUCT" --a17-result "$PERF_OUT/gates/A17/result.json" \
  --output "$PERF_OUT/gates/A18"
```

Use only gates applicable to the final diff, plus mandatory repository gates.
The fixture verifiers resolve known paths under `target`; the scoped environment
removal prevents an inherited global `CARGO_TARGET_DIR` from relocating those
fixtures. No `--prepare` mode qualifies as a completed component acceptance.

## Expected receipts and retained artifacts

| Build | Preserve and inspect |
| --- | --- |
| Native producer | `native-stable/manifest.json`, three `.so` files, exact Cargo build/metadata logs and tool/input hashes |
| B24 | `packages/manifest.json`, `commands.json`, `source-inventory.json`, `native-build-input.json`, both `closure.json`/`release.json` pairs, 17 selected package archives, dependency/license evidence and `evidence-index.json` |
| B21 application | `reference/progress.json`, build-record locks/resolved archive hashes, copied source inventory, AOT/JIT outputs and actual native identities; build-only summary remains `partial` |
| Database observer | `db-observer/manifest.json`, instrumented source identity, logs and actual executable/native hashes; same hook on both versions |
| Protocol | `protocols/build.json`, commands/logs, source/lock/cache identities and package server bytes; retain the separate frozen client/direct manifests |
| Codec | `codec/{manifest,commands,package-consumption,package-closure}.json`, independent consumer snapshots/locks, both `.nupkg` archives, actual AOT/native/direct artifacts and logs |
| Shared probes | Each `manifest.json`, selected consumer source/project/locks, AOT artifact hashes; runtime profiling receipts remain separate |
| Component tests | A02/A17/B15 `result.json`, B06 `summary.json`, command/source/tool/artifact records and actual JIT/AOT outputs; a process exit alone is not acceptance |

Before timing, bind the exact product source, all selected package archives,
compiled application, controller/profile/corpus and actual loaded native hashes.
Run the frozen short correctness/drain cells, then only the root-owned serial
cohort. This recipe assigns no long-stage duration credit and does not select new
rates or resource limits after observing the after result.

## Repository and review gates

`NativeWeave/AGENTS.md` requires `python3 eng/build.py verify`. The existing
`.github/workflows/build.yml` additionally runs the pristine no-Rust HelloWorld
consumer, `bash eng/verify-task04-linux.sh`, `bash eng/verify-task07-linux.sh` and
source-drift checks. The latter two need their existing pinned SDK/runtime Docker
images; Task-07 consumes the full domain graphs in JIT/AOT, exercises ordinary
managed edits, negative packaging, local release/rollback and runtime transfer.
The required PostgreSQL CI service is the pinned PostgreSQL 18.0 image. Local
package builds do not replace these pristine/runtime checks.

The local source gate command is:

```sh
cd "$PERF_PRODUCT"
env -u CARGO_TARGET_DIR python3 eng/build.py verify --version 0.1.0-perf01.verify.1
git diff --exit-code
```

CI `Verify` requires the build and security workflows to succeed. Security covers
dependency review on PRs, the pinned full-history redacted secret scanner, and
CodeQL C#/Python. Read live repository protection and checks on the final PR head
before merging; workflow text alone does not establish current server-side
approval requirements. Actual independent technical review is distinct from
author self-review and from a second GitHub account approval.

Plan ledger changes trigger `.github/workflows/native-slices-final-check.yml`.
It runs public API history/plan checks, `prepare_acceptance.py verify-contracts`
and `verify-tasks`, binding/completion/research/source-lifecycle verification,
graph validation, mutation/host-selection/Rust-1.100 checks and all three graph
schemas. Run the exact workflow gate list with the locked Design checkout beside
Plan: these tools resolve `Plan.parent/NativeWeave-Design`, not an environment
override. The current Design pin remains
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. This evidence-only note changes no
graph, contract or prior acceptance binding.

Existing NativeWeave CI build/evidence archives expire after 14 days; publication
verification archives and Plan integrity artifacts use 30 days. Current upload
paths do not automatically include Perf-01 raw measurement directories. Root
must retain the authorized synthetic evidence separately, record its actual
location/retention, and read it back before claiming recoverability.

After the accepted PR merge, observe main CI and the ordinary Release workflow.
The existing preview publisher remains HelloWorld-only and requires the exact
merged-PR identity and release/security gates. Domain package publication stays
the separate task; do not manually publish these private performance feeds.

## PageProbe/default-retirement compatibility review

PageProbe source commit `9fda0a09f35d63bebf145873217a7dca4cba563e` received an
independent source-only review from the database agent. Public API/type binding,
100-row cap/EOF order, both-provider parameters, transaction/session retirement,
full DTO checks and owned-table cleanup passed that review. Comment/README
follow-up `0cb82dcd8e641e19e816b908f1c752d0f796a156` clarifies that a new logical
session may reuse the sole pooled physical connection: this profile is not the
formal database driver's external durable oracle. Neither review ran a build,
test or load.

Omitting `--probe` still selects the exact `RetirementProbe` folder/project.
The selected C# source, assembly identity, copied SDK pin, package version/feed
mapping, isolated cache, Rust traps, Release/AOT/x86-64-v2 flags, restore and
publish commands are unchanged. The new `probe` and `consumerInputs` fields add
receipt metadata after the same build; `driverSources` now also inventories the
new page files. Consequently whole manifest bytes differ, while selected
retirement consumer behavior and build arguments remain unchanged. Preserve old
receipts as written; compare selected source/flags rather than rewriting their
manifest to the expanded format. Actual PageProbe compilation/execution remains
a separate pending gate.
