# B21 independent controller review

**Verdict:** no remaining concrete blocker in the requested scope after C1 and C2 were closed. This was a read-only review; no product change, root worktree edit or matrix rerun was performed. The reviewer authored the reference application but did not author these controllers.

## Findings and closure

- **C1 — TLS transport inference, closed at `fd04f951262438d1d5f7d85e62c3a72992a76711`.** The original HTTP/1 TLS row could accept a plaintext READY URI because its summary reflected the certificate argument. The revised Service rejects scheme mismatch before any request, retains normal certificate/hostname verification, and derives TLS from the observed scheme. The parent-produced readback records actual HTTPS for all 12 original TLS rows.
- **C2 — next-statement observation window, closed at `517d1e42cfa04f0d6a81ddf2d520a9268a26e7b9`.** The original check began after INSERT completion, omitting any intervening Execute sent while INSERT was blocked. The revised check begins after INSERT dispatch. Only at most one exact SQLx catalog command may precede the separate operations SELECT. The parent readback records both original PG JIT/AOT traces passing the stricter window.

## Key checks

The conflict oracle requires an actual upstream COMMIT hold, independent PostgreSQL lock-wait evidence, an `INSERT 0 0` completion, the next business SELECT returning one row, identical HTTP responses and independent durable operation/item/outbox identities. Unknown requires actual COMMIT plus idle ReadyForQuery to be withheld, an HTTP outcome_unknown response, matching committed recovery identity and unchanged durable replay. These checks do not substitute elapsed time or application logs for the database witnesses.

The catalog exception is a full-match, catalog-only SQLx 0.9.0 ColumnResolver shape with bounded numeric pairs. Its exact source was inspected; it is not a general exemption for arbitrary SELECT statements.

The package controller snapshots and hashes source, controller, package archives, restored graphs, executables, output inventories and native modules. Resume rejects changed inputs or retained artifacts. JIT/AOT is observed in the running executable through the injected RuntimeFeature marker. The edited model accessor compiles in the projection; the added DTO property and handler header provide distinct HTTP witnesses. Native module hashes stay tied to the frozen package inputs.

TLS verification remains enabled, and the HTTP2 frame path requires ALPN h2. The cargo/rustc/rustup PATH traps provide ordinary consumer invocation evidence; they are not a universal detector for absolute executable paths or proof of a pristine machine. The controller explicitly leaves pristine B24 and B22 soak acceptance false, which preserves that boundary.

## Exact reviewed identities

| Input | Commit | SHA-256 |
| --- | --- | --- |
| Original postgres_oracles.py | 11b7d27ba01f4b6e66d04d89d5a77984c393452b | 6b35ba40809f232d4a5427c441e03f32ae404ce6c7a466ffb486b664df4b7703 |
| package_probe.py, unchanged through final dispatch fix | 11b7d27ba01f4b6e66d04d89d5a77984c393452b / 517d1e42cfa04f0d6a81ddf2d520a9268a26e7b9 | e2da4b3d6828f82193d9b01488c7030515808b31fa7f53b3c6a99a4dff157fc2 |
| run.py TLS/changed assertions | fd04f951262438d1d5f7d85e62c3a72992a76711 | e805319b5129e1a84963720c4366c17b26b96e97e838e2cb96d74adc5f951dd2 |
| Final postgres_oracles.py | 517d1e42cfa04f0d6a81ddf2d520a9268a26e7b9 | 422889b5be450e61e4a2404c34ab86f3d1e22a99a866dc9eccd78365d48a4f8b |

`review.json` records the exact review inputs, closure records, boundaries and hashes of the parent-produced TLS/dispatch readbacks. Those readback records were read; this review does not claim to have rerun their product scenarios or independently reopened every raw trace.
