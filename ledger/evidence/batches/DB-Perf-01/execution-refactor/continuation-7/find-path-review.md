# Complete-key Find review — retained decision

The reviewed candidate was
[`dc235553309e1f5c282fd530fabd225204070d05`](https://github.com/IzuSharp/Korda/commit/dc235553309e1f5c282fd530fabd225204070d05),
parent `47fe650dfed5d7bba1c4d74c4a127c5d08b66082`. The review recommended retaining
it after correctness review, without assigning performance credit from source
inspection. The final selected path incorporates this decision.

| Layer | Decision | Reason and boundary |
|---|---|---|
| Public `DataSession.FindAsync` | Replace its repeated Fluent construction with the private shape route; delete the former production body. | Keep complete-key validation, open-state checks and precancellation before shape acquisition. The removed body remains only in the test oracle, with an actual test caller. |
| Cold native construction | Compile one immutable complete-key plan through the additive Find factory. | Ordered key equalities, full declaration-order projection, terminal 3 and the existing typed Int64 `LIMIT 2` remain identical to the old query. Construction does not call the provider. |
| Parameter schema | Reuse `PreparedParameterLayout.CreateWireLayout`. | Private ordinal definitions use the same canonical JSON/hash/descriptors as public prepared parameters, including configured codecs. They never allocate public parameter identities. |
| Key admission | Keep small scalar counters and the original per-key error order. | No Fluent tape or temporary per-key value frame is emitted. The native factory returns the actual fixed logical byte fee; changing payload bytes are charged synchronously and rechecked natively. |
| Projection ownership | Share the source-registered projection in both the native arena and plan. | The initially retained parsed duplicate was removed before sealing. Mapper identity remains the exact managed Table object. |
| Repeated execution | Copy the owned key snapshot directly into one execution values frame. | Each execution owns independent values and uses the existing cursor pull, TypedStream terminal and exact Table.Row mapper. |
| General native ShapeCache | Bypass only for private Find. | The Find LRU already owns this plan and its immutable compilation. Repeated ABI/identity buffer construction, hashing, mutex/LRU lookup and second cache retention add no reuse here. Ordinary Fluent and public Prepare still enter their existing cache. |
| Provider I/O, cancellation and retirement | Reuse the existing execution and completion paths. | No physical connection, prepared statement, row description, Session, cancellation token or transaction is retained by the Find cache. |


## Lifetime and compatibility constraints

The source LRU keys by exact managed Table identity, so equal metadata cannot
substitute another mapper. Acquisition returns a retained lease before releasing
the registration lock. Eviction/source close release the cache reference while
active executions keep their own lease. Count and retained-byte limits remain;
oversized shapes may execute uncached. The budget is not a whole-process RSS bound.

Each execution owns mutable key/parameter values independently. The cache owns
no Session, cancellation state, result batch, transaction or physical statement.
Ordinary terminal-3 plans remain one-shot; only the private Find flag permits its
reuse. Private parameter identities cannot be imported into normal queries.

The additive capability is `db.find.shape.v1` (bit 29); source admission checks
capability and export before use. Existing provider behavior, DDL mismatch ordering,
cancellation and retirement remain. Tests cover mapper identity, binary-key
mutation, cache eviction, source closure and ordinary consumer compilation.
