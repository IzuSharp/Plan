# B18 managed integration independent review

Reviewer: `server_track`. Platform: Linux x64.
Managed review/fix baseline: `f8153b57b868ae7664bee47899359c9addcfb815`.
Native component bound into that integration: `12bfa6054990fc8ab2c26ee7b7ec3c2b485a9970`.
Pinned Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.

## Scope and conclusion

The reviewer independently inspected the coordinator-authored C# gRPC facade, terminal/cancellation/disposal behavior, exact static API and focused actual-Host edge fixtures. **No remaining blocking finding was identified in that managed review after f8153b5.** This note binds the accepted managed corrections and their native dependency; it does not claim that the native implementation author independently reviewed their own Rust code. The coordinator's native source review and assembled immutable verification remain separate records.

The same reviewer authored the B18 native implementation and its component receipt. That author evidence is `artifacts/task06/B18/native-final/result.json` in the B18-native worktree, at12bfa60, passed with strict Clippy, Debug/Release leaf and Host/Core tests, unchanged48-symbol Server ABI and pinned upstream allocation-source hashes. Its native SHA is `0ed39dcd2922547bfe72cc642a31ea5811d66ee2f7b9a0f234ab09e5807dc0c7`. It is a native component receipt, not the assembled product/package receipt. The coordinator's later composed asset legitimately has a different shared tree/hash.

## Findings and their disposition

1. **B18-INBOUND-DISPOSE-JOIN — resolved at f8153b5.** Early inbound disposal previously stopped native input but could finish while a captured MoveNext continuation still ran, allowing late publication of Current. The correction caches one disposal task, joins both the deterministic Created-cancel StopInput operation and the captured MoveNext continuation, preserves the first failure and suppresses publication after disposal. The real-Host forced-continuation regression checks that Dispose remains pending until that continuation is released, that repeated Dispose joins the same work, and that Current is not republished.
2. **B18-HEADERS-FAILED-ADMISSION — resolved at f8153b5.** A synchronous header-create rejection previously consumed the managed one-header state even though native admission transferred no owner. The correction restores the state only for that synchronous unadmitted failure. It does not permit retry after an admitted operation. The actual native rejection-then-valid-header fixture verifies the caller can recover with the same call context.
3. **Retained codec Bytes capacity — bound into12bfa60 and independently examined by the coordinator.** The native codec grants cover full retained backing capacity, framing/conversion overlap and Tonic's retained chunks rather than just visible message length. Upstream Bytes/Tonic source identities and raw-operation retained-owner tests are in the native receipt. A zero-length valid message remains distinct from EOF; late normal A07 cleanup cancellation of a successful read does not stop future input. The explicit stop helper cancels a dedicated Created read before Begin and joins retirement, so no scheduler-latency assumption is required.
4. **Pre-response HTTP/2 drop guard — resolved in the native dependency.** Hyper can drop the response future before ownership reaches GrpcBody. PendingResponse retains the request until that transfer and aborts/retires/reaps it if the future is dropped. The actual independent-client pending-read cancellation case exposed this path; native and composed tests require eventual RequestAborted and completed zero-counter Close. An already-won successful EOF is not overwritten merely because cancellation becomes visible afterward.
5. **Metadata live peak and owner transfer — bound into12bfa60/shared integration.** Request, response headers and trailers include decoder/raw-byte overlap and retained backing rather than merely encoded length. Reply-create validation failures retain the caller's token; admitted work owns the token through its actual response lifetime. The coordinator reviewed the narrow completed-body metadata-anchor exception and the fixed HTTP metadata allocation contract. The focused native tests cover retained metadata/request owners before final retirement.

## Public allocation boundary and API

The managed review also required precise GrpcMarshaller documentation. Framework byte buffers and codec overlap remain budgeted. A user-supplied static marshaller's arbitrary private constructor/DTO allocations are application code; encoded protobuf size cannot honestly bound every such CLR object graph. The final documentation distinguishes that SPI boundary from MaxDecodedMessageBytes (decompressed protobuf payload) and preserves the exact pinned public surface, with no reflection-based generic marshaller or added public API.

The C# facade still reuses A07 create/start/take/retire/release, the actual native Host and its single runtime. No C# protocol/network substitute or second callback bridge was introduced. Cancellation signals intent and retirement is observed separately. The four cardinalities preserve native framing, strict unary cardinality, half-close and total-call deadline behavior.

## Evidence limits

This review did not rerun unrelated historical acceptance. The coordinator's final immutable assembled receipt, actual JIT/Native AOT independent grpc-dotnet consumers, Linux package/no-Rust consumption, exact API/XML gate and existing CI are authoritative for delivery acceptance. The native component receipt and this independent managed review are complementary evidence; neither alone claims all-platform acceptance.
