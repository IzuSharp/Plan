# Perf-01: actual B17 managed request-retirement regression

The shared request-retirement correction passed the **complete existing B17
managed fixture and its new ownership regressions in Release JIT and actual
Native AOT**. Each mode reported 105 checks and 43 original fixture dispatches.
All four original HTTP transport markers and the new HTTP/1.1 + HTTP/2 TLS
retirement marker were present. All six owned commands exited zero and their
process groups and adopted descendants retired without cleanup signals.

This is finite managed functional evidence. No native verifier was replayed,
no B18 pass is granted, and performance, capacity and 30-minute measurement
credit are **zero**. The earlier spontaneous B18 AOT failure and deliberate
ticket-tail reproduction retain their separate outcomes.

## Exact source and selected binary

| Identity | Actual value |
| --- | --- |
| Local managed producer | `9de3f74444246e356a2b12ab664ef99286309aaf` |
| [Public source](https://github.com/IzuSharp/NativeWeave/tree/12c477f0cdbc01fb026e98ac0e26eb45617424ed) | `12c477f0cdbc01fb026e98ac0e26eb45617424ed` |
| Exact shared tree | `0c763ba3b908dcc289528369231daf1788f87571` |
| Selected native producer | `da48ccf9d263155ebcbc2a6eea986f6b05972f51` |
| Selected native Server SHA-256 | `28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2` |
| Native producer manifest SHA-256 | `0192798bb7fbd90b419eee669c244f6c52b22164ef608e45622e6a301845a44f` |
| Actual JIT test DLL SHA-256 | `1ab5b26b299e8517f9c65ff6947952c104b860fc51293b67ac71ed93b1064416` |
| Actual AOT executable SHA-256 | `28b028260c3f78026cbc423305d5135954238a8c35f692b1f1b1a93043062ce3` |
| Executor SHA-256 | `06a6a673b462a6312fb8183f5ffccd67a2330d59c2d0eb4a7101264282f3028b` |
| Execution receipt SHA-256 | `9ba7c4dd2d2d95f0fe911468815dfe980fb4304bbc26244ab673721957c8ddad` |
| Actual collection interval | 2026-11-20 12:07:20.425721–12:08:16.445972 UTC |

An independent publication read fetched all five changed files and verified
their bytes, SHA-256 and Git blob identities against the reviewed local source.
The local and public commits have the exact same tree. The numerical evidence
binds that readback receipt. The native producer is recorded separately: native
source/build inputs did not change, and the selected precompiled library was
verified in both actual runtime output inventories before and after execution.

## Actual managed coverage

| Runtime | Exit | Checks | Original dispatch count | Original transport markers | New retirement marker |
| --- | --- | --- | --- | --- | --- |
| Release JIT | 0 | 105 | 43 | 4 | Passed |
| Native AOT | 0 | 105 | 43 | 4 | Passed |

The four original transport combinations remain HTTP/1.1 cleartext, HTTP/2
cleartext, HTTP/2 with TLS and HTTP/1.1 with TLS. The original retained-body,
quota, cancellation, native listener, TLS reload and composed Application
assertions remain in the executed fixture.

The new [retirement cases](https://github.com/IzuSharp/NativeWeave/blob/12c477f0cdbc01fb026e98ac0e26eb45617424ed/tests/Server.Native/RetirementFixtures.cs)
run over both HTTP/1.1 and HTTP/2 TLS. They establish two distinct ownership
boundaries:

- After native dispatch quiescence, a deliberately held managed dispatcher
  tail still retains its native admission owner. A second independent client
  stays in the native queue, then succeeds when the first full managed tail
  returns and final owner release removes its managed ticket.
- A real admitted physical lease delays final SafeHandle destruction after
  logical disposal. A throwing cancellation registration remains an observable
  host fault, while its completed cancellation task still permits safe release.
  After independently establishing native completion and zero payload, a
  100 ms close still reports one managed pending request and waits at least
  80 ms. Releasing the last physical lease completes the original subsequent
  finite close wait with no pending requests or retained bytes.

The phase and release bounds are unchanged from the reviewed source. No
private client-side wait for ticket removal was added to the original gRPC
fixture. The new tests exercise the shared Server boundary directly.

## Native evidence remains separately attributed

The retained native-component receipt
`0f52a6e20a55a16dd876766c319728aa613b6447fab41e5e8ea537ad1dc5cffa`
reports passed at source `1207b8d3b0c273752a28dabdf3e7a2b54c933571`.
Its retained whole-Server binary has SHA-256
`0542a7766a79091c6ea2d51daad74c257fcc7e9f902619bf4eebcc129b6a2e5b`.
Those bytes differ from the selected `28d793d6…` library above. The component
receipt and retained binary were rehashed and remain attributed to their
original producer and gRPC leaf/Host component scope. They are not presented
as this run's selected native asset or as a newly executed complete B17 native
verifier.

The six commands were locked JIT restore/build/execute followed by locked AOT
restore/publish/execute. Restore and build/publish commands retained 900-second
outer bounds; each actual fixture invocation retained its 90-second outer
bound. The original process/adopted-child owner and exclusive global lock were
used. Fresh retained output directories and separate synthetic TLS fixture
directories kept generated fixture material out of executable inventories.

## Independent result audit and retention

The offline audit verified all 12 stdout/stderr hashes, 31 source-inventory
hashes, 20 actual JIT artifacts and ten actual AOT artifacts. It checked both
complete stdout marker sequences, empty execution stderr, original native
producer/component identities, exact public source readback, source cleanliness
and finite process/adopted-child retirement. It ran once on CPU 8, exited zero
in 0.093333131 seconds, and executed no product test or workload.

`completion-markers.json` preserves the complete small stdout marker sequences.
`evidence.json` preserves numerical outcomes, source and relative artifact
identities, and actual hashes. Absolute host paths, raw operational commands,
process identifiers and control records are excluded. The original binaries,
receipts and operational logs remain owner-controlled working evidence; no
durable external binary archive is asserted here. The public projection remains
retrievable while the corresponding Plan repository history is retained.

The manifest binds the published bytes, inspector and its actual audit receipt.
Full B18 and the other affected module/package gates remain separate
obligations before the scratch retention decision or fresh performance timing.
