# B14 Linux handoff

Status: implementation and Linux x64 component validation passed. Parent integration review, package-level checks and PR/merge handling remain with the main executor. No other platform is accepted by this receipt.

## Fixed source and assets

The executable source is `fa4badc8195e69f0e606970a4bc8a8671842bf51` on `task/Task-05-B14-linux`. The immutable Design pin is `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. Source, native profiles/lock inputs, ordinary executable assets and Native AOT assets were hashed before execution in `jit-inputs.json` and `aot-inputs.json`; every recorded hash was checked unchanged after both runs. Frozen executables are under `jit-frozen/` and `aot-frozen/`, with independent SQLite/PostgreSQL provider assets under `assets/`. The actual upstream profiles are recorded in `features-sqlite.log` and `features-postgres.log`.

The latest owned checkpoints after the earlier implementation are `bcdb722`, `30ab4ba`, `a1874fc` and `fa4badc`; the parent already integrated the former source checkpoints and owns the shared bounded-codec/compound-admission patches. The branch is clean. Shared dependency fixes were reused, including the B08 independent PostgreSQL connect deadline/manifest preflight and final B13 query/Fluent behavior.

## Actual validation

- Frozen JIT: **1673 assertions**, **570** independently observed A07 retirements; all six native counters returned to zero on both providers.
- Frozen Linux x64 Native AOT: **1678 assertions**, **572** separate retirements; both runtime dynamic-code flags false and all six native counters zero.
- Native leaf tests: **2 passed**, zero ignored; combined Host/relations strict Clippy and format checks passed. Actual execution uses SQLite and a dedicated real PostgreSQL18 TCP cluster, with no provider skip.
- API/XML/reference: **81 required B14 symbols**, all present; exact compiled inventories contain432 Database and149 Data symbols, all matching the pin. Six actual-product compile-negative consumers reject with the expected compiler diagnostics.
- Minimal and advanced sample builds have zero warnings/errors and run on both providers, including caller savepoint rollback and acknowledged partial PerBatch commits.
- Ordinary and explicit `linux-x64` AOT restores passed locked mode with the original NuGet configuration and audit enabled. The managed build and AOT publish contain no Rust build step.

`evidence-linux.json` records the complete checked coverage, contract decisions, input/binary/log hashes and toolchain identities. Final logs are `jit-verified/consumer.log`, `aot-verified/consumer.log`, `native-tests-verified.log`, `clippy-verified.log`, `api-final.log`, `compile-negative-final.log`, `sample-sqlite.log` and `sample-postgres/consumer.log`.

## Review points

Native SeaQuery owns CRUD SQL and relation predicates. Insert and upsert update values remain independent, tenant/composite keys are never dropped, and caller-supplied versions are never incremented or replayed automatically. The pinned database API §5 declares key writes0/1 and treats multiple matches as schema/constraint errors: reason16 is reserved for expected1/actual0; separate actual tests cover both cases.

Bulk owns an explicit compound session/transaction lease while input enumeration awaits between native commands. Caller `All` owns a tracked savepoint; `PerBatch` records only acknowledged preceding commits. Actual cancellation/input/converter/disposal/native failures retain original exceptions and progress; PostgreSQL backend termination covers unknown commit and failed rollback without inventing rollback or retry. Existing self-sized kind7 followed by exactly one kind15 is the minimal bulk error composition; ordinary errors remain kind7 and malformed combinations reject.

Snapshot preflight charges exact wire/control overhead and remaining row bytes before encoding. Static JSON preserves the supplied type metadata and options. The finite output cap6R+4096 is **not** a complete live-memory peak: growth retains old+new backing arrays, final copies and SDK escape scratch can overlap, and buffered rows remain live. Allocation regressions use preallocated application inputs and make no throughput/process-peak claim. SQLite's existing physical SQL+input-copy grant remains separate from logical parameter limits; the final matrix covers both physical rejection before SQL and successful values within that grant.

No dynamic SeaORM eager loader, managed SQL engine, implicit tracking or new package/resolver is introduced. B14 composes into the existing Database/provider distribution. Final pristine package/release gates and whole-batch acceptance belong to the main executor. Earlier failed diagnostic logs are retained honestly and are not acceptance evidence.

## Next step

The main executor should ingest this receipt and handoff into `Plan/ledger/evidence/B14/`, finish independent integration review, update the Task-05 Linux batch handoff and complete the authorized PR/check/merge workflow. This child can move to the separately assigned Task-06 B18 documentation/sample/package-consumer work after that handoff; it does not start a different task package automatically.
